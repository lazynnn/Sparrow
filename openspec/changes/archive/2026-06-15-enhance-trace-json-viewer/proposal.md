## Why

When viewing trace details, request and response bodies are displayed in constrained `<pre>` blocks with a max height of 320px. For large JSON payloads (common with LLM API calls), this makes it difficult to read, navigate, and inspect the data. Users cannot effectively search, expand/collapse nested structures, or copy the full content. A dedicated full-screen JSON viewer dialog is needed to provide a better experience for inspecting long trace payloads.

## What Changes

- Add a fullscreen/overlay dialog that opens when clicking on any JSON section (request body, response body, request headers, response headers) in the trace detail panel
- The dialog will display the full JSON content with syntax highlighting, collapsible/expandable nodes, copy-to-clipboard, and search functionality
- Add a clickable "expand" button on each JSON section in the trace detail panel to open the dialog
- The inline preview in the trace detail panel remains as-is (truncated scrollable view) — the dialog is opt-in for deeper inspection

## Capabilities

### New Capabilities
- `json-viewer-dialog`: A fullscreen overlay dialog for viewing and interacting with JSON data, with syntax highlighting, collapsible nodes, copy-to-clipboard, and search

### Modified Capabilities
<!-- No existing capability specs are changing at the requirements level -->

## Impact

- Frontend: `sparrow/web/templates/index.html` (dialog markup, button additions), `sparrow/web/static/js/app.js` (dialog state, JSON viewer logic, copy/search), `sparrow/web/static/css/input.css` (dialog styles)
- No backend/API changes required — all data is already available from the existing trace detail endpoint
- No new external dependencies — will be implemented with Alpine.js and Tailwind CSS, consistent with the existing vendored approach
