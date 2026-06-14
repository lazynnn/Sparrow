# Trace Storage

## Purpose

Persist LLM request/response traces in SQLite with WAL mode for concurrent access, async writes for performance, and support for archiving and re-import.

## Requirements

### Requirement: Trace data model
The gateway SHALL store a complete trace record for each proxied request. Each trace SHALL include: request method, path, headers, body, response status code, response headers, response body, timestamp, duration, TTFB (for streaming), and trace status (success, error, timeout).

#### Scenario: Store complete non-streaming trace
- **WHEN** a non-streaming request is proxied successfully
- **THEN** the trace record SHALL contain the full request method, path, headers, body, response status, response headers, response body, timestamp, and duration

#### Scenario: Store streaming trace with accumulated body
- **WHEN** a streaming request is proxied
- **THEN** the trace record SHALL contain the accumulated full response body (reassembled from SSE chunks), TTFB, and total stream duration

### Requirement: SQLite storage with WAL mode
The gateway SHALL store traces in a SQLite database with WAL (Write-Ahead Logging) mode enabled for concurrent read/write performance.

#### Scenario: Concurrent read and write
- **WHEN** the web UI is reading traces while new requests are being proxied
- **THEN** reads SHALL NOT block writes and writes SHALL NOT block reads, using SQLite WAL mode

### Requirement: Asynchronous trace recording
The gateway SHALL write trace records to the database asynchronously using background tasks, so that the proxy response is not blocked by the database write.

#### Scenario: Trace written after response sent
- **WHEN** a proxied request completes
- **THEN** the response SHALL be sent to the client before the trace record is written to the database

### Requirement: Trace archiving to tar.gz
The gateway SHALL support archiving traces to compressed `.tar.gz` files. Archiving SHALL export selected traces to a JSONL format within the archive and delete them from the active database.

#### Scenario: Archive traces older than a date
- **WHEN** the user triggers an archive operation for traces older than a specified date
- **THEN** the gateway SHALL create a `.tar.gz` file containing `metadata.json` (archive timestamp, trace count, date range) and `traces.jsonl` (one complete trace per line), then delete those traces from the active database

#### Scenario: Archive preserves all trace data
- **WHEN** traces are archived
- **THEN** each line in `traces.jsonl` SHALL contain the complete trace record including request headers, request body, response headers, response body, timing, and token usage

### Requirement: Archive re-import
The gateway SHALL support re-importing traces from an archive file back into the active database.

#### Scenario: Import from archive file
- **WHEN** the user triggers an import of an archive `.tar.gz` file
- **THEN** the gateway SHALL read the `traces.jsonl` from the archive and insert each trace into the active database using INSERT OR IGNORE to avoid duplicates

### Requirement: Trace indexing
The gateway SHALL create database indexes on trace fields commonly used for filtering: timestamp, request path, response status code, model name, and duration.

#### Scenario: Fast filtering by timestamp range
- **WHEN** the web UI queries traces filtered by a timestamp range
- **THEN** the query SHALL use the timestamp index for efficient retrieval

### Requirement: Max trace body size
The gateway SHALL enforce a configurable maximum trace body size. Request or response bodies exceeding this limit SHALL be truncated with a marker indicating truncation.

#### Scenario: Large response body truncation
- **WHEN** a response body exceeds the configured max trace body size
- **THEN** the stored trace body SHALL be truncated to the limit with a `[TRUNCATED]` suffix appended
