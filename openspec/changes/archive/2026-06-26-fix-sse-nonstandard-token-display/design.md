## Context

The frontend SSE viewer was fixed in commit 52bfeeb to accept non-standard `data:` (no space after colon) SSE prefixes, matching both `data: {}` and `data:{}`. However, the three backend Python parsers (`OpenAIChatParser`, `AnthropicMessagesParser`, `OpenAIResponsesParser`) still use strict `line.startswith("data: ")` matching. When LLM routers emit non-standard SSE format, these parsers skip all data lines, resulting in null token values stored in the database — and the web-ui shows no token counts or cost information.

## Goals / Non-Goals

**Goals:**
- Make all three backend SSE token extraction parsers accept both `data: ` (standard) and `data:` (non-standard) prefixes
- Ensure token values display correctly in the web-ui regardless of SSE prefix format
- Maintain backward compatibility with existing standard-format responses

**Non-Goals:**
- Changing the frontend SSE parsing (already fixed)
- Adding support for new SSE formats beyond prefix flexibility
- Modifying the SSE streaming proxy or forwarding logic
- Changing the parser registry or route mapping

## Decisions

### Decision 1: Use regex-based prefix matching with capture groups

Replace `line.startswith("data: ")` and `line[6:]` slicing with `re.match(r"^data:\s*(.*)", line)` pattern in all three parsers.

**Rationale**: This mirrors the frontend fix approach. Using a regex capture group dynamically handles the prefix length, eliminating the hardcoded `line[6:]` offset that only works for `data: ` (6 chars). The `\s*` matches zero or more whitespace after the colon, covering both `data:{}` and `data:  {}` (extra spaces).

**Alternative considered**: A shared utility function to extract data payload from SSE lines. Rejected because the parsing logic in each parser has different line-by-line flow (reverse iteration, event tracking, etc.), and a utility would add indirection without meaningful reuse beyond three call sites.

### Decision 2: Handle `event:` prefix flexibility in Anthropic parser

Also make `event:` line matching flexible using `re.match(r"^event:\s*(.*)", line)` in the Anthropic parser, consistent with the `data:` change.

**Rationale**: If `data:` can arrive without a space, `event:` could too from the same non-standard routers. Making both consistent prevents a follow-up fix.

### Decision 3: Use `re` module at function level

Compile the regex pattern inline with `re.match()` rather than pre-compiling with `re.compile()` at module level.

**Rationale**: The parsers are not performance-sensitive — they run once per streaming request on an already-accumulated string. `re.match()` is clear and sufficient. Pre-compilation would be premature optimization.

## Risks / Trade-offs

- **Over-matching risk**: The regex `^data:\s*(.*)` could match lines like `data: ` with empty payload, but this is handled by the subsequent `JSON.parse` try/catch which returns null/continues — same as current behavior. → No mitigation needed.
- **Breaking existing behavior**: Replacing `startswith` with regex changes the matching semantics slightly (e.g., `data:\t{}` would now match). This is acceptable — the SSE spec allows whitespace after the colon. → Considered a feature, not a bug.
