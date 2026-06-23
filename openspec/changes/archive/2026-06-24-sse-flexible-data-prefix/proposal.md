## Why

Some LLM routers return SSE chunks with `data:{}` (no space after the colon) instead of the standard `data: {}`. The frontend JSON viewer strictly matches `data: ` (with space), causing it to fail to detect and parse these non-standard SSE responses, leaving users unable to use the SSE viewer (Raw/Chunks/Merged) for those traces.

## What Changes

- Make SSE detection in the JSON viewer accept both `data: ` and `data:` line prefixes
- Make SSE chunk parsing handle both `data: ` and `data:` prefixes when extracting JSON payloads
- Make raw SSE rendering highlight both `data:` and `data: ` prefixes correctly
- Do NOT modify any backend parsing code or response data — this is purely a frontend display concern

## Capabilities

### New Capabilities

- `flexible-sse-prefix`: Accept both standard (`data: `) and non-standard (`data:`) SSE data line prefixes in the JSON viewer

### Modified Capabilities

- `sse-viewer`: SSE detection and parsing requirements must accommodate `data:` without trailing space

## Impact

- Frontend JavaScript (`sparrow/web/static/js/app.js`) — `_isSSE`, `_parseSSEChunks`, and raw rendering logic
- The `sse-viewer` spec requirements for SSE detection and chunk parsing
