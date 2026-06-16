## Why

When a trace has `stream: true`, the response body is stored as raw SSE text (`data: {...}\n\ndata: {...}\n\n...`). This cannot be parsed as a single JSON object, so both the inline preview and the JSON viewer fall back to displaying unformatted raw text. Users cannot easily inspect individual SSE chunks, see the aggregated content, or navigate the structured data within each chunk.

## What Changes

- Add a view mode toggle to the JSON viewer dialog when it detects SSE-formatted data (streaming responses)
- Support three view modes: **Raw** (original SSE text as-is), **Chunks** (each `data:` line parsed and rendered as a separate collapsible JSON tree), and **Merged** (all chunk `delta.content` fields concatenated into a single readable string)
- Auto-detect SSE format by checking for `data: ` prefix patterns in the content
- When SSE is detected, default to Chunks view for the best inspection experience
- When SSE is not detected, the viewer works exactly as before (no toggle shown)

## Capabilities

### New Capabilities
- `sse-viewer`: Toggle-based viewing modes for SSE streaming response data in the JSON viewer, supporting raw, chunk-parsed, and content-merged views

### Modified Capabilities
- `json-viewer-dialog`: Extends the existing JSON viewer to detect SSE data and present view mode toggle when applicable

## Impact

- Frontend only: `sparrow/web/static/js/app.js` (SSE detection, parsing, view mode toggle, merged content rendering), `sparrow/web/templates/index.html` (toggle UI in dialog header), `sparrow/web/static/css/input.css` (toggle button styles)
- No backend/API changes — all data is already available from the existing trace detail endpoint
