## ADDED Requirements

### Requirement: JSON viewer handles SSE content
The JSON viewer dialog SHALL detect SSE-formatted content and present view mode controls when applicable, in addition to its existing JSON viewing capabilities.

#### Scenario: Open viewer with SSE content
- **WHEN** a user opens the JSON viewer with SSE-formatted content (e.g., a streaming response body)
- **THEN** the viewer SHALL detect the SSE format and display a view mode toggle (Raw, Chunks, Merged) in the dialog header

#### Scenario: Open viewer with non-SSE content
- **WHEN** a user opens the JSON viewer with valid JSON or other non-SSE content
- **THEN** the viewer SHALL function exactly as before without displaying SSE view mode controls
