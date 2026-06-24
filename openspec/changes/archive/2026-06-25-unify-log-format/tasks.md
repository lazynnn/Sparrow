## 1. Logging Infrastructure

- [x] 1.1 Create `SparrowLogFormatter` class in `sparrow/__main__.py` that formats as `%(asctime)s %(levelname)-8s %(message)s` with conditional `[name]` prefix (omit when logger name is `sparrow`)
- [x] 1.2 Replace `logging.basicConfig()` call with `logging.config.dictConfig()` that applies the shared formatter to the root handler and uvicorn loggers (`uvicorn`, `uvicorn.error`, `uvicorn.access`)

## 2. Integration

- [x] 2.1 Verify `ShutdownLogFilter` still works correctly with the new `dictConfig` setup — add filter to uvicorn loggers in the dictConfig
- [x] 2.2 Remove `logging.getLogger(logger_name).addFilter(shutdown_filter)` loop since filter will be configured via dictConfig

## 3. Verification

- [x] 3.1 Run the application and confirm all log lines (sparrow, uvicorn, httpx) use the unified `YYYY-MM-DD HH:MM:SS,mmm LEVEL:     message` format
- [x] 3.2 Confirm sparrow logs omit `[sparrow]` and library logs include their logger name in brackets
