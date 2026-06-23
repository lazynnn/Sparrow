## MODIFIED Requirements

### Requirement: JSON viewer handles SSE content
The JSON viewer dialog SHALL detect SSE-formatted content and present view mode controls when applicable, in addition to its existing JSON viewing capabilities. For non-SSE content that is a parsed object, the viewer SHALL also present a view mode toggle offering JSON and Merged options.

#### Scenario: Open viewer with SSE content
- **WHEN** a user opens the JSON viewer with SSE-formatted content (e.g., a streaming response body)
- **THEN** the viewer SHALL detect the SSE format and display a view mode toggle (Raw, Chunks, Merged) in the dialog header

#### Scenario: Open viewer with non-SSE object content
- **WHEN** a user opens the JSON viewer with valid JSON or other non-SSE content that parses to an object or array
- **THEN** the viewer SHALL display a view mode toggle (JSON, Merged) in the dialog header

#### Scenario: Open viewer with non-SSE string content
- **WHEN** a user opens the JSON viewer with content that cannot be parsed as JSON (stored as a raw string)
- **THEN** the viewer SHALL NOT display any view mode toggle, and SHALL function as before showing the raw text

#### Scenario: Default mode for non-SSE content
- **WHEN** the JSON viewer opens non-SSE content
- **THEN** the view mode SHALL default to JSON

#### Scenario: Switch non-SSE view mode
- **WHEN** a user clicks a different view mode option on the non-SSE toggle
- **THEN** the viewer SHALL immediately render the content in the selected mode without closing the dialog
