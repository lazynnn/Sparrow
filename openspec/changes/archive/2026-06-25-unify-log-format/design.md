## Context

Sparrow uses Python's `logging` module with `logging.basicConfig` configured in `sparrow/__main__.py`. The current format is `%(asctime)s [%(levelname)s] %(name)s: %(message)s`, which produces lines like `2026-06-25 02:39:05,867 [INFO] sparrow: message`. However, uvicorn manages its own loggers (`uvicorn`, `uvicorn.error`, `uvicorn.access`) with a different default format: `INFO:     message`. Third-party libraries like httpx inherit the basicConfig format. This results in visually inconsistent terminal output.

## Goals / Non-Goals

**Goals:**
- Unify all log output to a single, consistent format with timestamps
- Format: `YYYY-MM-DD HH:MM:SS,mmm LEVEL:     message` (timestamp + right-aligned level label + message)
- Include logger name for disambiguation when it's not `sparrow`: `YYYY-MM-DD HH:MM:SS,mmm LEVEL:     [name] message`
- Apply to all loggers: sparrow application, uvicorn (server, error, access), httpx, and any other libraries

**Non-Goals:**
- Structured/JSON logging (separate concern)
- Log file output (currently only console/stderr)
- Changing log levels or filtering behavior (ShutdownLogFilter stays as-is)

## Decisions

### 1. Use `dictConfig` instead of `logging.basicConfig`

Replace `logging.basicConfig()` with `logging.config.dictConfig()` for full control over formatters and handlers. basicConfig only sets the root logger and cannot configure uvicorn's named loggers.

**Alternative**: Pass `log_config` dict to `uvicorn.Config`. Rejected because it only configures uvicorn's loggers, not the root logger or other libraries.

### 2. Custom Formatter class for conditional logger name display

Create a `SparrowLogFormatter(logging.Formatter)` that includes `[name]` only when the logger name is not `sparrow`. This keeps the common case (application logs) clean while still showing origin for library logs.

**Alternative**: Always include name. Rejected because `sparrow:` prefix on every app log is redundant when most output is from sparrow.

**Alternative**: Never include name. Rejected because httpx/uvicorn logs would be indistinguishable from app logs.

### 3. Apply formatter via dictConfig to root and uvicorn loggers

Configure the same formatter for the root handler AND explicitly for uvicorn's loggers (`uvicorn`, `uvicorn.error`, `uvicorn.access`). This overrides uvicorn's default `DefaultFormatter` which uses a different format.

### 4. Uvicorn access log format

Disable uvicorn's custom access log formatter and let it use the shared formatter. The access log message already contains request details (method, path, status), so the shared format with logger name `[uvicorn.access]` provides sufficient context.

## Risks / Trade-offs

- **Uvicorn log format change is cosmetic** → No behavioral impact, but users accustomed to the current uvicorn format may notice. Mitigated by keeping the visual style close to uvicorn's default (right-aligned level label with padding).
- **Third-party loggers may have their own formatters** → httpx, httpcore, etc. use the root logger's handler by default, so they will inherit the unified format. If a library configures its own handler, it will remain unaffected (acceptable).
- **Conditional logger name adds minor complexity** → The custom formatter is simple (5 lines) and well-tested.
