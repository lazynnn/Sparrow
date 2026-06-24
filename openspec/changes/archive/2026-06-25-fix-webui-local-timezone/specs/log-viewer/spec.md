## MODIFIED Requirements

### Requirement: Trace list view
The web UI SHALL display a paginated list of traces showing: timestamp (in the viewer's local timezone), request path, model, status code, duration, token count, and cost. The list SHALL be sorted by timestamp in descending order (newest first).

#### Scenario: View recent traces
- **WHEN** the user opens the web UI
- **THEN** the trace list SHALL display the most recent traces with timestamp (converted to local timezone), path, model, status, duration, tokens, and cost columns

#### Scenario: Paginate through traces
- **WHEN** there are more traces than the page size
- **THEN** the UI SHALL provide pagination controls to navigate between pages
