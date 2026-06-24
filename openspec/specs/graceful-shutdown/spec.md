# Capability: graceful-shutdown

## Purpose

Handle graceful shutdown of the Sparrow server, suppressing spurious error logs and allowing in-flight requests to complete within a grace period.

## Requirements

### Requirement: Shutdown log filter
The system SHALL install a logging filter that suppresses ERROR and WARNING level log records from uvicorn, anyio, httpcore, and httptools loggers after a shutdown signal has been received. Before the shutdown signal, all log records SHALL pass through unfiltered.

#### Scenario: Normal operation - errors are logged
- **WHEN** the application is running and an error occurs in uvicorn
- **THEN** the error is logged normally without suppression

#### Scenario: Shutdown - spurious errors are suppressed
- **WHEN** a shutdown signal (SIGINT or SIGTERM) has been received and a uvicorn/anyio/httpcore/httptools error is logged
- **THEN** the error log record is suppressed and not displayed

### Requirement: Graceful shutdown timeout
The system SHALL configure uvicorn servers with a `timeout_graceful_shutdown` of 5 seconds so that in-flight requests have time to complete before connections are forcibly closed.

#### Scenario: In-flight request completes during grace period
- **WHEN** a shutdown signal is received and an in-flight request completes within 5 seconds
- **THEN** the request completes normally and no connection-reset error is produced

#### Scenario: In-flight request exceeds grace period
- **WHEN** a shutdown signal is received and an in-flight request does not complete within 5 seconds
- **THEN** the server forcibly closes the connection and any resulting error is suppressed by the shutdown log filter

### Requirement: Clean Ctrl+C output
The system SHALL produce only clean shutdown log messages when Ctrl+C is pressed. No ERROR-level tracebacks from uvicorn, anyio, httpcore, or httptools SHALL appear in the output after the "Shutdown signal received" message.

#### Scenario: User presses Ctrl+C
- **WHEN** the user presses Ctrl+C while Sparrow is running
- **THEN** the output shows "Shutdown signal received", "Database closed", and "Sparrow shutdown complete" without any ERROR tracebacks
