## Context

The JSON viewer in the Sparrow web UI parses SSE response bodies for display in Raw/Chunks/Merged modes. All three parsing paths (`_isSSE`, `_parseSSEChunks`, `getRawSSEHtml`) use strict `startsWith('data: ')` matching — requiring a space after the colon. Some LLM routers emit `data:{}` (no space), causing the viewer to fail to detect and render SSE content. This is a frontend-only concern; the backend SSE parsers (used for token usage extraction) are not in scope.

Current affected code in `sparrow/web/static/js/app.js`:
- **Line 60**: `_isSSE` — `line.startsWith('data: ')`
- **Line 70**: `_parseSSEChunks` — `trimmed.startsWith('data: ')`
- **Line 71**: `_parseSSEChunks` — `trimmed.slice(6)` (hardcoded offset for `"data: "`)
- **Line 386**: `getRawSSEHtml` — `lines[i].startsWith('data: ')`
- **Line 387**: `getRawSSEHtml` — `line.slice(6)` (hardcoded offset)

## Goals / Non-Goals

**Goals:**
- Accept both `data: ` (standard, with space) and `data:` (non-standard, no space) in all frontend SSE parsing paths
- Preserve existing behavior for standard SSE responses — no visual or functional changes
- Keep the implementation simple and localized to the three affected functions

**Non-Goals:**
- Modifying backend SSE parsers (`openai_chat.py`, `anthropic_messages.py`, `openai_responses.py`)
- Modifying the proxied response data or SSE stream content
- Handling other SSE spec deviations (e.g., multi-line data fields, `data:` with extra spaces)
- Changing the SSE server endpoint (`/api/traces/stream`)

## Decisions

### Decision 1: Use a regex-based prefix matcher instead of `startsWith`

Replace `startsWith('data: ')` with a regex like `/^data:\s*/` to match `data:` followed by zero or more whitespace characters. This naturally handles both `data:{}` and `data: {}` (and even `data:  {}` with extra spaces) without special-casing.

**Alternative considered**: Check both `startsWith('data: ')` and `startsWith('data:')` with separate branches. Rejected because it adds branching logic and a second hardcoded offset, making the code harder to maintain.

### Decision 2: Use regex capture group to extract the data payload

Instead of `slice(6)`, use a regex match to capture the payload after the `data:` prefix and optional whitespace. For example: `const match = trimmed.match(/^data:\s*(.*)/)` then use `match[1]`. This correctly handles variable whitespace after the colon.

**Alternative considered**: Dynamically compute the slice offset based on whether there's a space. Rejected as more error-prone and less readable than a regex capture.

### Decision 3: Preserve `data:` prefix rendering in Raw view

In `getRawSSEHtml`, highlight the full `data:` prefix (including any trailing space if present) using the existing `sse-data-prefix` class. The regex match naturally captures the prefix boundary, allowing correct splitting for highlighting.

## Risks / Trade-offs

- **Over-matching**: `/^data:\s*/` could match lines like `data:  ` (whitespace-only payload). → Mitigation: These lines would previously have been ignored (no `data: ` prefix match), but the JSON parse would fail gracefully and they'd be skipped in Chunks view, same as today.
- **Inconsistent prefix display**: Raw view may show `data:{"key"}` vs `data: {"key"}` depending on upstream. → Mitigation: This is the actual data — we should display it as-is, just with the prefix highlighted correctly.
