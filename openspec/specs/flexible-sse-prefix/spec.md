## Purpose

Support flexible matching of SSE data line prefixes, accepting both `data: ` (standard, with space) and `data:` (non-standard, no space).

## Requirements

### Requirement: Flexible SSE data prefix matching
The frontend SSE parsing logic SHALL accept both `data: ` (standard, with space) and `data:` (non-standard, no space) as valid SSE data line prefixes in all detection, parsing, and rendering contexts.

#### Scenario: Detect SSE content with no-space prefix
- **WHEN** the JSON viewer opens content containing a line like `data:{"choices":[]}`
- **THEN** the viewer SHALL identify the content as SSE format and enable SSE view mode controls

#### Scenario: Detect SSE content with standard prefix
- **WHEN** the JSON viewer opens content containing a line like `data: {"choices":[]}`
- **THEN** the viewer SHALL identify the content as SSE format and enable SSE view mode controls (unchanged behavior)

#### Scenario: Detect SSE content with mixed prefixes
- **WHEN** the JSON viewer opens content containing both `data:{"a":1}` and `data: {"b":2}` lines
- **THEN** the viewer SHALL identify the content as SSE format and parse both lines as SSE data
