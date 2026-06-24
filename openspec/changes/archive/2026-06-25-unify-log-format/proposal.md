## Why

Log output is inconsistent across the application. Uvicorn logs use `INFO:     Started server process [13926]` while application and library logs (sparrow, httpx) use `2026-06-25 02:39:05,867 [INFO] sparrow: message`. This makes logs harder to scan and breaks visual consistency in the terminal.

## What Changes

- Unify all log output to a single format: `YYYY-MM-DD HH:MM:SS,mmm INFO:     message` (timestamp + uvicorn-style leveled message)
- Configure uvicorn loggers to use the same formatter as the rest of the application
- Include logger name in the format for disambiguation: `YYYY-MM-DD HH:MM:SS,mmm INFO:     [name] message`
- Remove the `logging.basicConfig` call and replace with explicit handler/formatter configuration

## Capabilities

### New Capabilities
- `unified-logging`: Centralized log formatting configuration that applies a consistent, timestamped, uvicorn-style format to all loggers (application, uvicorn, httpx, etc.)

### Modified Capabilities
<!-- No existing spec-level behavior changes -->

## Impact

- `sparrow/__main__.py`: logging initialization code changes
- All log output in the terminal will change format (cosmetic only, no behavioral change)
- No API or dependency changes
