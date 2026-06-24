## Why

Pressing Ctrl+C to stop Sparrow produces ugly error tracebacks from uvicorn after the clean shutdown messages. This makes the application appear broken when it is actually shutting down correctly, and obscures any real errors in the logs.

## What Changes

- Suppress or catch exceptions that occur during uvicorn server shutdown (e.g., from in-flight SSE/stream connections being forcibly closed)
- Ensure task cancellation during shutdown handles `asyncio.CancelledError` cleanly without traceback output
- Add a short graceful shutdown timeout so servers have time to finish in-flight requests before tasks are cancelled

## Capabilities

### New Capabilities
- `graceful-shutdown`: Clean shutdown handling that suppresses spurious errors during the shutdown sequence, including proper handling of uvicorn server cleanup, SSE connection teardown, and async task cancellation.

### Modified Capabilities

## Impact

- `sparrow/__main__.py`: Signal handler and shutdown logic
- Uvicorn server configuration (shutdown timeout settings)
- SSE streaming endpoints (error handling during connection teardown)
