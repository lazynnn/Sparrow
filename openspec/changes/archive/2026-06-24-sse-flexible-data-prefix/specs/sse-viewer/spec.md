## MODIFIED Requirements

### Requirement: SSE detection in JSON viewer
The JSON viewer SHALL detect SSE-formatted content by checking if the content contains at least one line starting with `data:` (with or without a trailing space after the colon).

#### Scenario: Detect SSE content
- **WHEN** the JSON viewer opens content that contains at least one line starting with `data:` or `data: `
- **THEN** the viewer SHALL identify the content as SSE format and enable SSE view mode controls

#### Scenario: Non-SSE content
- **WHEN** the JSON viewer opens content that does not contain any line starting with `data:`
- **THEN** the viewer SHALL operate in standard JSON mode without showing SSE view mode controls

### Requirement: Chunks view mode
The Chunks view mode SHALL parse each `data:` line into a separate collapsible JSON tree, with a header for each chunk.

#### Scenario: Parse SSE chunks
- **WHEN** the user selects Chunks view mode for SSE content
- **THEN** each line starting with `data:` (with or without trailing space) SHALL have its payload parsed as a separate JSON object and rendered as a collapsible JSON tree

#### Scenario: Chunk headers
- **WHEN** the Chunks view renders parsed SSE data
- **THEN** each chunk SHALL have a header showing its index (e.g., "Chunk 1", "Chunk 2")

#### Scenario: DONE marker
- **WHEN** a `data: [DONE]` or `data:[DONE]` line is encountered in Chunks view
- **THEN** it SHALL be displayed as a plain text marker labeled "[DONE]" rather than parsed as JSON

#### Scenario: Invalid JSON in data line
- **WHEN** a `data:` line contains content that is not valid JSON (other than [DONE])
- **THEN** the viewer SHALL display that line as raw text within its chunk section

### Requirement: Raw view mode
The Raw view mode SHALL display the original SSE content as plain text with syntax highlighting for `data:` line prefixes.

#### Scenario: Display raw SSE
- **WHEN** the user selects Raw view mode for SSE content
- **THEN** the viewer SHALL display the complete original SSE text with `data:` prefixes highlighted distinctly, regardless of whether a space follows the colon
