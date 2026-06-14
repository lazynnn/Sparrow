import argparse
import asyncio
import logging
import signal
import sys

import uvicorn

from sparrow.config import load_config


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

    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger = logging.getLogger("sparrow")

    proxy_port = args.proxy_port or config.proxy_port
    ui_port = args.ui_port or config.ui_port

    from sparrow.database import Database
    from sparrow.proxy.router import create_proxy_app
    from sparrow.web_ui import create_web_app

    db = Database(config.storage.database)

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
            reload=args.reload,
        )
        web_config = uvicorn.Config(
            web_app,
            host="0.0.0.0",
            port=ui_port,
            log_level=config.log_level.lower(),
            reload=args.reload,
        )

        proxy_server = uvicorn.Server(proxy_config)
        web_server = uvicorn.Server(web_config)

        loop = asyncio.get_event_loop()
        stop = asyncio.Event()

        def _signal_handler():
            logger.info("Shutdown signal received")
            stop.set()
            proxy_server.should_exit = True
            web_server.should_exit = True

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, _signal_handler)

        print(f"╔══════════════════════════════════════╗")
        print(f"║     Sparrow LLM Gateway              ║")
        print(f"╠══════════════════════════════════════╣")
        print(f"║  Proxy:   http://0.0.0.0:{proxy_port:<12}║")
        print(f"║  Web UI:  http://0.0.0.0:{ui_port:<12}║")
        print(f"╚══════════════════════════════════════╝")

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
            await asyncio.gather(*tasks, return_exceptions=True)
            logger.info("Sparrow shutdown complete")

    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
