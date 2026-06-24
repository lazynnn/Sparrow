## MODIFIED Requirements

### Requirement: Trace data model
The gateway SHALL store a complete trace record for each proxied request. Each trace SHALL include: request method, path, headers, body, response status code, response headers, response body, timestamp (serialized as UTC-aware ISO 8601 with `+00:00` offset), duration, TTFB (for streaming), and trace status (success, error, timeout).

#### Scenario: Store complete non-streaming trace
- **WHEN** a non-streaming request is proxied successfully
- **THEN** the trace record SHALL contain the full request method, path, headers, body, response status, response headers, response body, timestamp (serialized as UTC-aware ISO string with `+00:00`), and duration

#### Scenario: Store streaming trace with accumulated body
- **WHEN** a streaming request is proxied
- **THEN** the trace record SHALL contain the accumulated full response body (reassembled from SSE chunks), TTFB, and total stream duration
