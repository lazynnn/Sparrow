import argparse
import asyncio
import contextlib
import copy
import logging
import logging.config
import signal
import sys

import click
import uvicorn

from sparrow.config import load_config

_SHUTDOWN_LOGGERS = (
    "uvicorn",
    "uvicorn.error",
    "uvicorn.access",
    "anyio",
    "httpcore",
    "httptools",
)


class ColourizedFormatter(logging.Formatter):
    level_name_colors = {
        logging.DEBUG: lambda level_name: click.style(str(level_name), fg="cyan"),
        logging.INFO: lambda level_name: click.style(str(level_name), fg="green"),
        logging.WARNING: lambda level_name: click.style(str(level_name), fg="yellow"),
        logging.ERROR: lambda level_name: click.style(str(level_name), fg="red"),
        logging.CRITICAL: lambda level_name: click.style(
            str(level_name), fg="bright_red"
        ),
    }

    def __init__(self, fmt=None, datefmt=None, style="%", use_colors=None):
        if use_colors in (True, False):
            self.use_colors = use_colors
        else:
            self.use_colors = sys.stderr.isatty()
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def color_level_name(self, level_name: str, level_no: int) -> str:
        func = self.level_name_colors.get(level_no, lambda n: str(n))
        return func(level_name)

    def formatMessage(self, record: logging.LogRecord) -> str:
        recordcopy = copy.copy(record)
        levelname = recordcopy.levelname
        separator = " " * (8 - len(recordcopy.levelname))
        if self.use_colors:
            levelname = self.color_level_name(levelname, recordcopy.levelno)
            if "color_message" in recordcopy.__dict__:
                recordcopy.msg = recordcopy.__dict__["color_message"]
        recordcopy.__dict__["levelprefix"] = levelname + ":" + separator
        return super().formatMessage(recordcopy)


class ShutdownLogFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        self.shutdown_active = False

    def filter(self, record: logging.LogRecord) -> bool:
        if not self.shutdown_active:
            return True
        if record.levelno >= logging.WARNING and record.name.startswith(
            _SHUTDOWN_LOGGERS
        ):
            return False
        return True


def _build_log_config(log_level: int) -> dict:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "sparrow": {
                "()": ColourizedFormatter,
                "format": "%(asctime)s %(levelprefix)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "sparrow",
                "stream": "ext://sys.stderr",
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["default"],
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["default"],
                "level": log_level,
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["default"],
                "level": log_level,
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["default"],
                "level": log_level,
                "propagate": False,
            },
        },
    }


def main():
    parser = argparse.ArgumentParser(prog="sparrow", description="Sparrow LLM Gateway")
    parser.add_argument(
        "-c", "--config", default="config.yaml", help="Path to config file"
    )
    parser.add_argument("--proxy-port", type=int, help="Override proxy port")
    parser.add_argument("--ui-port", type=int, help="Override web UI port")
    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload for development"
    )
    args = parser.parse_args()

    config = load_config(args.config)

    log_level = getattr(logging, config.log_level.upper(), logging.INFO)

    _log_config = _build_log_config(log_level)
    logging.config.dictConfig(_log_config)

    shutdown_filter = ShutdownLogFilter()
    for name in [None, "uvicorn", "uvicorn.error", "uvicorn.access"]:
        logger_obj = logging.getLogger(name) if name else logging.root
        logger_obj.addFilter(shutdown_filter)

    logger = logging.getLogger("sparrow")

    proxy_port = args.proxy_port or config.proxy_port
    ui_port = args.ui_port or config.ui_port

    from sparrow.database import Database
    from sparrow.proxy.router import create_proxy_app
    from sparrow.web_ui import create_web_app

    db = Database(config.storage.database)

    if not config.upstream_proxy.ssl_verify:
        logger.warning(
            "SSL verification is DISABLED for upstream requests. This exposes requests to man-in-the-middle attacks."
        )

    async def start():
        await db.init()
        logger.info("Database initialized at %s", config.storage.database)

        proxy_app = create_proxy_app(config, db)
        web_app = create_web_app(config, db)

        proxy_config = uvicorn.Config(
            proxy_app,
            host="0.0.0.0",
            port=proxy_port,
            log_level=config.log_level.lower(),
            log_config=_log_config,
            reload=args.reload,
            timeout_graceful_shutdown=5,
        )
        web_config = uvicorn.Config(
            web_app,
            host="0.0.0.0",
            port=ui_port,
            log_level=config.log_level.lower(),
            log_config=_log_config,
            reload=args.reload,
            timeout_graceful_shutdown=5,
        )

        proxy_server = uvicorn.Server(proxy_config)
        web_server = uvicorn.Server(web_config)

        loop = asyncio.get_event_loop()
        stop = asyncio.Event()

        def _signal_handler():
            logger.info("Shutdown signal received")
            shutdown_filter.shutdown_active = True
            stop.set()
            proxy_server.should_exit = True
            web_server.should_exit = True

        if sys.platform != "win32":
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, _signal_handler)

        print("╔══════════════════════════════════════╗")
        print("║     Sparrow LLM Gateway              ║")
        print("╠══════════════════════════════════════╣")
        print(f"║  Proxy:   http://127.0.0.1:{proxy_port:<10}║")
        print(f"║  Web UI:  http://127.0.0.1:{ui_port:<10}║")
        print("╚══════════════════════════════════════╝")

        tasks = [
            asyncio.create_task(proxy_server.serve()),
            asyncio.create_task(web_server.serve()),
        ]

        try:
            await stop.wait()
        finally:
            await db.close()
            logger.info("Database closed")

            for task in tasks:
                task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await asyncio.gather(*tasks)
            logger.info("Sparrow shutdown complete")

    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
