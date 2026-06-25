## MODIFIED Requirements

### Requirement: Flexible SSE data prefix matching
The SSE parsing logic SHALL accept both `data: ` (standard, with space) and `data:` (non-standard, no space) as valid SSE data line prefixes in all detection, parsing, rendering, and token extraction contexts — including both frontend JavaScript and backend Python parsers.

#### Scenario: Detect SSE content with no-space prefix
- **WHEN** the JSON viewer opens content containing a line like `data:{"choices":[]}`
- **THEN** the viewer SHALL identify the content as SSE format and enable SSE view mode controls

#### Scenario: Detect SSE content with standard prefix
- **WHEN** the JSON viewer opens content containing a line like `data: {"choices":[]}`
- **THEN** the viewer SHALL identify the content as SSE format and enable SSE view mode controls (unchanged behavior)

#### Scenario: Detect SSE content with mixed prefixes
- **WHEN** the JSON viewer opens content containing both `data:{"a":1}` and `data: {"b":2}` lines
- **THEN** the viewer SHALL identify the content as SSE format and parse both lines as SSE data

#### Scenario: Extract OpenAI Chat tokens from non-standard SSE format
- **WHEN** OpenAI Chat SSE chunks contain `data:{"id":"1","usage":{"prompt_tokens":10,"completion_tokens":5,"total_tokens":15}}` (no space after colon)
- **THEN** the parser SHALL extract prompt_tokens=10, completion_tokens=5, total_tokens=15

#### Scenario: Extract OpenAI Chat tokens from standard SSE format
- **WHEN** OpenAI Chat SSE chunks contain `data: {"id":"1","usage":{"prompt_tokens":10,"completion_tokens":5,"total_tokens":15}}` (with space after colon)
- **THEN** the parser SHALL extract prompt_tokens=10, completion_tokens=5, total_tokens=15 (unchanged behavior)

#### Scenario: Extract Anthropic tokens from non-standard SSE format with event lines
- **WHEN** Anthropic SSE chunks contain `event:message_start\ndata:{"type":"message_start","message":{"usage":{"input_tokens":30}}}` (no space after colon in data lines)
- **THEN** the parser SHALL extract prompt_tokens=30

#### Scenario: Extract Anthropic tokens from non-standard SSE format without event lines
- **WHEN** Anthropic SSE chunks contain `data:{"type":"message_start","message":{"usage":{"input_tokens":15}}}` (no event lines, no space after colon)
- **THEN** the parser SHALL extract prompt_tokens=15

#### Scenario: Extract OpenAI Responses tokens from non-standard SSE format
- **WHEN** OpenAI Responses SSE chunks contain `data:{"type":"response.completed","response":{"usage":{"input_tokens":50,"output_tokens":75}}}` (no space after colon)
- **THEN** the parser SHALL extract prompt_tokens=50, completion_tokens=75, total_tokens=125

#### Scenario: Extract tokens from mixed prefix SSE stream
- **WHEN** an SSE stream contains both `data:{"type":"response.output_text.delta","delta":"Hi"}` and `data: {"type":"response.completed","response":{"usage":{"input_tokens":10,"output_tokens":5}}}` lines
- **THEN** the parser SHALL parse both lines and extract tokens from the completed event
