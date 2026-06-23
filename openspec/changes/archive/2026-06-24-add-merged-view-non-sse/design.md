## Context

The JSON viewer dialog currently provides three view modes (Raw, Chunks, Merged) for SSE streaming responses, but only a single JSON tree view for non-SSE responses. The SSE "Merged" view concatenates `choices[].delta.content` fragments into readable text. Non-SSE OpenAI responses contain the same information in `choices[].message.content` and `choices[].message.reasoning_content`, but there is no way to quickly see just the readable text without navigating the JSON tree.

## Goals / Non-Goals

**Goals:**
- Add a JSON / Merged toggle for non-SSE content in the JSON viewer dialog
- Extract and display `choices[].message.content` and `choices[].message.reasoning_content` from parsed JSON in the Merged view
- Reuse the same visual layout (labeled Reasoning/Content sections, divider) as the SSE Merged view
- Support copy in non-SSE merged mode with the same format as SSE merged copy
- Default to JSON mode (preserving current behavior)

**Non-Goals:**
- Adding a "Raw" or "Chunks" tab for non-SSE (those are SSE-specific concepts)
- Supporting non-OpenAI response formats (e.g., Anthropic) in the initial implementation — the extraction logic can be extended later
- Changing the SSE viewer behavior in any way

## Decisions

### 1. Reuse existing SSE merged styles for non-SSE merged view

**Decision**: Use the same CSS classes (`sse-merged-section`, `sse-merged-label`, `sse-merged-divider`) for non-SSE merged rendering.

**Rationale**: The visual output is identical — labeled Reasoning/Content sections with a divider. Reusing classes avoids CSS duplication and ensures visual consistency.

**Alternative considered**: Separate `non-sse-merged-*` classes — rejected because it adds unnecessary CSS with no visual difference.

### 2. New extraction function `_mergeNonSSEContent(parsed)` instead of extending `_mergeSSEContent`

**Decision**: Create a standalone function `_mergeNonSSEContent(parsed)` that operates on the already-parsed JSON object, extracting from `choices[].message` instead of `choices[].delta`.

**Rationale**: The data shapes are different (message vs delta, single object vs array of chunks). A separate function keeps each path clean and testable. The output format `{ reasoning, content }` is shared.

**Alternative considered**: A single generic extractor with format detection — rejected because it adds complexity for no reuse benefit (the two paths are always called from different code locations).

### 3. Tab bar for non-SSE shows only JSON / Merged (two options)

**Decision**: Show a two-button toggle (JSON / Merged) for non-SSE content, rather than three buttons like SSE.

**Rationale**: Raw and Chunks are SSE-specific concepts. A two-button toggle keeps the UI clean and focused. The toggle is conditionally rendered with a new `x-if` block separate from the SSE toggle.

### 4. Only show Merged tab when the parsed JSON contains extractable content

**Decision**: Always show the JSON / Merged toggle for non-SSE content (when the parsed value is an object), and display an informational message in Merged view when no `choices[].message.content` fields are found.

**Rationale**: Hiding the Merged tab based on content analysis adds complexity. A consistent UI with a helpful empty state is simpler and more predictable. This matches the SSE Merged behavior which shows a message when no content is found.

## Risks / Trade-offs

- **[Non-OpenAI responses]**: Non-SSE responses from non-OpenAI providers (e.g., Anthropic) won't have extractable content in Merged view. → Mitigation: The "no extractable content" message guides users; the JSON tree remains available. The extraction function can be extended to support additional formats later.
- **[String-only responses]**: When `jsonViewerParsed` is a string (JSON parse failed), the toggle won't be shown because there's no structured data to extract from. This is acceptable since a raw string is already the "merged" view of plain text content.
