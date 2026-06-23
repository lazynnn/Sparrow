## ADDED Requirements

### Requirement: Non-SSE merged content extraction
The system SHALL extract readable text content from parsed non-SSE JSON objects that follow the OpenAI response format, by reading `choices[].message.content` and `choices[].message.reasoning_content` (or `choices[].message.reasoning`) fields.

#### Scenario: Extract content from OpenAI chat completion response
- **WHEN** the merged view renders a non-SSE parsed JSON object containing `choices` array with `message.content` fields
- **THEN** the system SHALL concatenate all non-null, non-empty `message.content` values into a single content string

#### Scenario: Extract reasoning from OpenAI response with thinking
- **WHEN** the merged view renders a non-SSE parsed JSON object containing `choices` array with `message.reasoning_content` or `message.reasoning` fields
- **THEN** the system SHALL concatenate all non-null, non-empty reasoning values into a single reasoning string, preferring `reasoning_content` over `reasoning`

#### Scenario: No extractable content in non-SSE response
- **WHEN** the merged view renders a non-SSE parsed JSON object that does not contain `choices[].message.content` or `choices[].message.reasoning_content` fields
- **THEN** the system SHALL display an informational message indicating no extractable text content was found, referencing `choices[].message.content`

#### Scenario: Non-object parsed content
- **WHEN** the parsed JSON content is not an object (e.g., a string or null)
- **THEN** the merged view SHALL NOT be available and only the JSON tree view SHALL be shown

### Requirement: Non-SSE merged view rendering
The system SHALL render extracted non-SSE content in the same visual format as the SSE merged view, with labeled Reasoning and Content sections separated by a divider.

#### Scenario: Render content with reasoning
- **WHEN** the merged view has both reasoning and content extracted from a non-SSE response
- **THEN** the viewer SHALL display a "Reasoning" section with a label badge and the reasoning text, a dashed divider, and a "Content" section with a label badge and the content text

#### Scenario: Render content only
- **WHEN** the merged view has content but no reasoning extracted from a non-SSE response
- **THEN** the viewer SHALL display only a "Content" section with a label badge and the content text

#### Scenario: Render reasoning only
- **WHEN** the merged view has reasoning but no content extracted from a non-SSE response
- **THEN** the viewer SHALL display only a "Reasoning" section with a label badge and the reasoning text

### Requirement: Copy non-SSE merged content
The system SHALL support copying the merged content to the clipboard when the viewer is in non-SSE merged mode.

#### Scenario: Copy merged content with reasoning
- **WHEN** a user clicks the copy button while in non-SSE merged mode and both reasoning and content exist
- **THEN** the clipboard SHALL contain the reasoning text, a separator line, and the content text (matching the SSE merged copy format)

#### Scenario: Copy merged content only
- **WHEN** a user clicks the copy button while in non-SSE merged mode and only content or only reasoning exists
- **THEN** the clipboard SHALL contain whichever text is available
