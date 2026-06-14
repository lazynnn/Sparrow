## ADDED Requirements

### Requirement: Trace list view
The web UI SHALL display a paginated list of traces showing: timestamp, request path, model, status code, duration, token count, and cost. The list SHALL be sorted by timestamp in descending order (newest first).

#### Scenario: View recent traces
- **WHEN** the user opens the web UI
- **THEN** the trace list SHALL display the most recent traces with timestamp, path, model, status, duration, tokens, and cost columns

#### Scenario: Paginate through traces
- **WHEN** there are more traces than the page size
- **THEN** the UI SHALL provide pagination controls to navigate between pages

### Requirement: Trace filtering
The web UI SHALL support filtering traces by: model name, status code (success/error), date range, and minimum duration. Multiple filters SHALL be combinable.

#### Scenario: Filter by model
- **WHEN** the user selects a model name from the filter dropdown
- **THEN** the trace list SHALL show only traces that used the selected model

#### Scenario: Filter by date range
- **WHEN** the user selects a start and end date
- **THEN** the trace list SHALL show only traces within that date range

#### Scenario: Combine filters
- **WHEN** the user applies both a model filter and a date range filter
- **THEN** the trace list SHALL show traces matching both filters

### Requirement: Trace detail view
The web UI SHALL display a detailed view of a single trace when selected. The detail view SHALL show: full request headers, request body (JSON formatted), full response headers, response body (JSON formatted), timing breakdown, token usage, and calculated cost.

#### Scenario: View trace details
- **WHEN** the user clicks on a trace in the list
- **THEN** the UI SHALL display the full trace details including formatted request/response JSON, headers, timing, tokens, and cost

#### Scenario: Pretty-print JSON bodies
- **WHEN** the trace detail view displays a request or response body that is valid JSON
- **THEN** the body SHALL be displayed with syntax highlighting and collapsible sections

### Requirement: Token usage dashboard
The web UI SHALL display a dashboard showing aggregated token usage and cost metrics: total tokens, total cost, tokens by model, cost by model, and usage trends over time.

#### Scenario: View usage summary
- **WHEN** the user navigates to the dashboard
- **THEN** the UI SHALL display total tokens used, total cost, and a breakdown by model

#### Scenario: View cost by model
- **WHEN** the dashboard is displayed
- **THEN** the UI SHALL show a table or chart of cost broken down by model name

### Requirement: Dark mode
The web UI SHALL support dark mode. The default theme SHALL be dark mode. Users SHALL be able to toggle between light and dark mode.

#### Scenario: Default dark mode
- **WHEN** the user opens the web UI for the first time
- **THEN** the UI SHALL render in dark mode

#### Scenario: Toggle theme
- **WHEN** the user clicks the theme toggle button
- **THEN** the UI SHALL switch between light and dark mode, and the preference SHALL persist in localStorage

### Requirement: Real-time trace streaming
The web UI SHALL support real-time updates via SSE. When new traces are recorded, the trace list SHALL update automatically without requiring a page refresh.

#### Scenario: New trace appears in real-time
- **WHEN** a new trace is recorded while the user is viewing the trace list
- **THEN** the new trace SHALL appear at the top of the list without a page refresh

### Requirement: Local static assets
The web UI SHALL serve all CSS and JavaScript assets locally. No external CDN resources SHALL be required. Tailwind CSS SHALL be built locally using the standalone CLI. Alpine.js SHALL be served as a local file.

#### Scenario: Offline operation
- **WHEN** the web UI is accessed without internet connectivity
- **THEN** all styles, scripts, and functionality SHALL work correctly using locally served assets
