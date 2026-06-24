# Unified Logging

## Purpose

Provide a single, consistent log format across all application loggers, including third-party loggers like uvicorn and httpx.

## Requirements

### Requirement: Unified log format with timestamps
All log output from the application SHALL use a single consistent format: `YYYY-MM-DD HH:MM:SS,mmm LEVEL:     message`, where `LEVEL` is right-padded to 8 characters (e.g., `INFO:    `, `WARNING: `, `ERROR:   `).

#### Scenario: Application log message
- **WHEN** the sparrow logger emits an INFO message "Database initialized"
- **THEN** the output SHALL match the pattern `YYYY-MM-DD HH:MM:SS,mmm INFO:     Database initialized`

#### Scenario: Warning-level message
- **WHEN** the sparrow logger emits a WARNING message
- **THEN** the output SHALL use `WARNING:` with consistent padding, e.g., `YYYY-MM-DD HH:MM:SS,mmm WARNING:  message`

### Requirement: Logger name included for non-sparrow loggers
When a log record originates from a logger other than `sparrow`, the output SHALL include the logger name in brackets: `YYYY-MM-DD HH:MM:SS,mmm LEVEL:     [name] message`.

#### Scenario: httpx log message
- **WHEN** httpx emits a log message about an HTTP request
- **THEN** the output SHALL include `[httpx]`, e.g., `YYYY-MM-DD HH:MM:SS,mmm INFO:     [httpx] HTTP Request: POST https://example.com "HTTP/1.1 200 OK"`

#### Scenario: Uvicorn server log message
- **WHEN** uvicorn emits a startup message
- **THEN** the output SHALL include `[uvicorn]`, e.g., `YYYY-MM-DD HH:MM:SS,mmm INFO:     [uvicorn] Started server process [13926]`

#### Scenario: Sparrow application log
- **WHEN** the sparrow logger emits a message
- **THEN** the output SHALL NOT include `[sparrow]`, e.g., `YYYY-MM-DD HH:MM:SS,mmm INFO:     Shutdown signal received`

### Requirement: Uvicorn loggers use unified format
Uvicorn's loggers (`uvicorn`, `uvicorn.error`, `uvicorn.access`) SHALL use the same unified formatter as all other loggers, replacing uvicorn's default log format.

#### Scenario: Uvicorn access log
- **WHEN** an HTTP request is logged by uvicorn.access
- **THEN** the output SHALL follow the unified format, e.g., `YYYY-MM-DD HH:MM:SS,mmm INFO:     [uvicorn.access] 127.0.0.1:45920 - "GET /api/traces/stream HTTP/1.1" 200 OK`

#### Scenario: Uvicorn startup log
- **WHEN** uvicorn emits "Uvicorn running on http://0.0.0.0:8080"
- **THEN** the output SHALL follow the unified format with timestamp, e.g., `YYYY-MM-DD HH:MM:SS,mmm INFO:     [uvicorn] Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)`

### Requirement: Logging configured via dictConfig
The application SHALL use `logging.config.dictConfig` instead of `logging.basicConfig` to ensure all loggers (root, uvicorn, and application) share the same formatter.

#### Scenario: Logging initialization
- **WHEN** the application starts
- **THEN** logging SHALL be configured via `dictConfig` with a shared formatter applied to the root handler and uvicorn loggers

#### Scenario: Existing filter behavior preserved
- **WHEN** the ShutdownLogFilter is active and a shutdown is in progress
- **THEN** WARNING+ messages from uvicorn, httpcore, etc. SHALL still be suppressed, preserving existing shutdown filter behavior
