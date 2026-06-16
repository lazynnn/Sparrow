## ADDED Requirements

### Requirement: SSE detection in JSON viewer
The JSON viewer SHALL detect SSE-formatted content by checking if the content contains at least one line starting with `data: `.

#### Scenario: Detect SSE content
- **WHEN** the JSON viewer opens content that contains at least one line starting with `data: `
- **THEN** the viewer SHALL identify the content as SSE format and enable SSE view mode controls

#### Scenario: Non-SSE content
- **WHEN** the JSON viewer opens content that does not contain any line starting with `data: `
- **THEN** the viewer SHALL operate in standard JSON mode without showing SSE view mode controls

### Requirement: SSE view mode toggle
When SSE content is detected, the JSON viewer SHALL display a toggle control allowing the user to switch between Raw, Chunks, and Merged view modes.

#### Scenario: Toggle visibility
- **WHEN** the JSON viewer detects SSE-formatted content
- **THEN** a view mode toggle SHALL appear in the dialog header offering Raw, Chunks, and Merged options

#### Scenario: Default mode
- **WHEN** the JSON viewer detects SSE-formatted content
- **THEN** the view mode SHALL default to Chunks

#### Scenario: Toggle not shown for non-SSE
- **WHEN** the JSON viewer opens non-SSE content (valid JSON or other text)
- **THEN** the view mode toggle SHALL NOT be displayed

#### Scenario: Switch view mode
- **WHEN** a user clicks a different view mode option on the toggle
- **THEN** the viewer SHALL immediately render the content in the selected mode without closing the dialog

### Requirement: Raw view mode
The Raw view mode SHALL display the original SSE content as plain text with syntax highlighting for `data:` line prefixes.

#### Scenario: Display raw SSE
- **WHEN** the user selects Raw view mode for SSE content
- **THEN** the viewer SHALL display the complete original SSE text with `data:` prefixes highlighted distinctly

### Requirement: Chunks view mode
The Chunks view mode SHALL parse each `data:` line into a separate collapsible JSON tree, with a header for each chunk.

#### Scenario: Parse SSE chunks
- **WHEN** the user selects Chunks view mode for SSE content
- **THEN** each line starting with `data: ` SHALL be parsed as a separate JSON object and rendered as a collapsible JSON tree

#### Scenario: Chunk headers
- **WHEN** the Chunks view renders parsed SSE data
- **THEN** each chunk SHALL have a header showing its index (e.g., "Chunk 1", "Chunk 2")

#### Scenario: DONE marker
- **WHEN** a `data: [DONE]` line is encountered in Chunks view
- **THEN** it SHALL be displayed as a plain text marker labeled "[DONE]" rather than parsed as JSON

#### Scenario: Invalid JSON in data line
- **WHEN** a `data:` line contains content that is not valid JSON (other than [DONE])
- **THEN** the viewer SHALL display that line as raw text within its chunk section

### Requirement: Merged view mode
The Merged view mode SHALL extract and concatenate text content from all SSE chunks into a single readable string.

#### Scenario: Merge delta content
- **WHEN** the user selects Merged view mode for SSE content containing OpenAI-compatible chunks with `choices[].delta.content`
- **THEN** the viewer SHALL concatenate all non-null, non-empty `delta.content` values into a single string and display it in a formatted text block

#### Scenario: No extractable content
- **WHEN** the user selects Merged view mode for SSE content that does not contain `choices[].delta.content` fields
- **THEN** the viewer SHALL display an informational message indicating no extractable text content was found

#### Scenario: Copy merged content
- **WHEN** a user clicks the copy button while in Merged view
- **THEN** the merged text content SHALL be copied to the clipboard
