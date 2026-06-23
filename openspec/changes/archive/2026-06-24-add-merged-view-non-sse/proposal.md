## Why

The JSON viewer already provides a "Merged" view for SSE streaming responses, which extracts and concatenates readable text (content and reasoning) into a clean, human-friendly format. Non-SSE responses (e.g., standard OpenAI chat completion responses) contain the same information in `choices[].message.content` and `choices[].message.reasoning_content`, but the viewer only offers a raw JSON tree — making it tedious to read the actual response content. Adding a "Merged" view for non-SSE responses would provide the same quick-read experience.

## What Changes

- Add a view mode toggle (JSON / Merged) to the JSON viewer dialog when viewing non-SSE content
- Implement a "Merged" view for non-SSE responses that extracts `choices[].message.content` and `choices[].message.reasoning_content` from the parsed JSON and renders them in labeled sections (mirroring the SSE merged view)
- Default to "JSON" mode for non-SSE content (preserving current behavior)
- Support copy in merged mode for non-SSE content

## Capabilities

### New Capabilities

- `non-sse-merged-view`: Merged view mode for non-SSE responses in the JSON viewer dialog, extracting readable content from OpenAI-format response objects

### Modified Capabilities

- `json-viewer-dialog`: Add view mode toggle visibility for non-SSE content (currently the toggle is only shown for SSE)
- `sse-viewer`: No requirement changes — the non-SSE merged view follows the same UX patterns but operates on a different data shape

## Impact

- `sparrow/web/static/js/app.js`: New merged rendering logic for non-SSE, mode toggle state management, copy handler updates
- `sparrow/web/templates/index.html`: Conditional tab bar for non-SSE mode
- `sparrow/web/static/css/input.css`: Possible minor style additions for non-SSE merged view
