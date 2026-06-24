## Context

Sparrow runs two uvicorn servers (proxy and web UI) in a single asyncio event loop. On Ctrl+C, a signal handler sets `should_exit` on both servers and signals a stop event. The `finally` block cancels the server tasks and awaits them with `return_exceptions=True`. However, uvicorn's internal shutdown and SSE connection teardown produce uncaught exceptions (e.g., `anyio`/`httpcore` connection errors on in-flight SSE streams), which uvicorn logs as ERROR tracebacks. These appear after the clean "Sparrow shutdown complete" message.

## Goals / Non-Goals

**Goals:**
- Suppress spurious error tracebacks during graceful shutdown
- Ensure Ctrl+C produces only clean shutdown log messages
- Handle `CancelledError` in async generators (SSE streams) without error output
- Give in-flight requests a short grace period before forcing shutdown

**Non-Goals:**
- Changing the uvicorn library itself
- Adding complex dependency injection for shutdown hooks
- Handling double Ctrl+C (force-kill) — that remains OS-default behavior

## Decisions

1. **Install custom uvicorn log filter** — Add a logging filter that suppresses ERROR-level tracebacks from uvicorn/anyio/httpcore during the shutdown phase. This is the simplest approach that doesn't require patching uvicorn internals.
   - Alternative: Override uvicorn's `Server.handle_exit` — too fragile across uvicorn versions.
   - Alternative: Redirect stderr during shutdown — too coarse, could hide real errors.

2. **Add `timeout_graceful_shutdown` to uvicorn Config** — Uvicorn supports `timeout_graceful_shutdown` natively. Setting it to a few seconds gives in-flight requests time to complete before the server forcibly closes connections. This reduces the number of connection-reset errors.

3. **Wrap the shutdown `gather` to suppress `CancelledError` and `anyio` exceptions** — The `asyncio.gather(*tasks, return_exceptions=True)` already captures exceptions, but uvicorn may log them before we can suppress. The log filter handles this at the output level.

4. **Suppress uvicorn's "Shutdown complete" duplicate logging** — During shutdown, uvicorn logs its own messages. Our signal handler already logs clean messages, so we filter redundant uvicorn shutdown noise.

## Risks / Trade-offs

- **[Risk] Log filter could suppress real errors during shutdown** → Mitigation: Only activate the filter after the shutdown signal is received; before that, all errors pass through normally.
- **[Risk] `timeout_graceful_shutdown` could delay Ctrl+C response** → Mitigation: Use a short timeout (3-5 seconds). If the user presses Ctrl+C twice, the OS sends SIGKILL.
