## 1. Shutdown Log Filter

- [x] 1.1 Create a `ShutdownLogFilter` class in `sparrow/__main__.py` that tracks whether shutdown has been signaled and suppresses ERROR/WARNING records from uvicorn, anyio, httpcore, and httptools loggers when active
- [x] 1.2 Install the filter on the relevant loggers after logging is configured in `main()`
- [x] 1.3 Set the filter's shutdown flag to active inside the `_signal_handler` callback

## 2. Graceful Shutdown Timeout

- [x] 2.1 Add `timeout_graceful_shutdown=5` to both `uvicorn.Config` instances in `start()`

## 3. Verification

- [x] 3.1 Start Sparrow, verify normal operation logs are unaffected
- [x] 3.2 Press Ctrl+C and verify no ERROR tracebacks appear in output — only clean shutdown messages
