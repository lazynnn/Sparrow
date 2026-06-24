## ADDED Requirements

### Requirement: Timezone-aware timestamp display
The web UI SHALL display all timestamps converted to the viewer's local timezone. Timestamps SHALL be formatted using `Intl.DateTimeFormat` with a consistent, locale-aware format that includes both date and time.

#### Scenario: Trace list shows local time
- **WHEN** a trace has a UTC timestamp of `2026-06-25T10:00:00+00:00`
- **AND** the viewer's browser is in UTC+8 timezone
- **THEN** the trace list SHALL display the timestamp as `2026-06-25 18:00:00` (or locale-equivalent)

#### Scenario: Trace detail shows local time
- **WHEN** the user opens a trace detail view
- **THEN** the timestamp field SHALL display the trace time converted to the viewer's local timezone

#### Scenario: Archive created timestamp shows local time
- **WHEN** the archive list displays the "Created" column
- **THEN** the timestamp SHALL be formatted using the same `formatTime()` function as other timestamps, converted to the viewer's local timezone

### Requirement: Consistent timestamp formatting
All timestamp fields in the web UI SHALL use a single formatting function (`formatTime`). No timestamp SHALL be rendered as a raw ISO string.

#### Scenario: No raw ISO strings displayed
- **WHEN** any timestamp is displayed in the web UI
- **THEN** it SHALL be rendered through `formatTime()` and NOT as a raw ISO 8601 string
