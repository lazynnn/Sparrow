## 1. SSE Detection and Parsing

- [x] 1.1 Add `isSSE(str)` function in `app.js` that checks if content contains at least one line starting with `data: `
- [x] 1.2 Add `parseSSEChunks(str)` function in `app.js` that splits SSE text into an array of objects `{ index, raw, data, parsed }` where `parsed` is the JSON-parsed value or null for `[DONE]`/invalid lines
- [x] 1.3 Add `mergeSSEContent(chunks)` function in `app.js` that extracts `choices[].delta.content` from each parsed chunk and concatenates non-null/non-empty values into a single string

## 2. View Mode State Management

- [x] 2.1 Add `jsonViewerIsSSE`, `jsonViewerMode` (`'chunks'` | `'raw'` | `'merged'`) state properties to the Alpine.js app component
- [x] 2.2 Update `openJsonViewer()` to detect SSE format and set `jsonViewerIsSSE` and `jsonViewerMode` accordingly (default to `'chunks'` if SSE)
- [x] 2.3 Update `closeJsonViewer()` to reset SSE-related state

## 3. Chunks View Rendering

- [x] 3.1 Add `getChunksViewHtml()` method that iterates parsed SSE chunks and renders each as a collapsible JSON tree with a "Chunk N" header, using `_renderJsonTree()` for parsed chunks and plain text for `[DONE]` markers
- [x] 3.2 Update `getJsonViewerTree()` to check `jsonViewerIsSSE` and `jsonViewerMode`, delegating to the appropriate rendering path (existing JSON tree, raw view, chunks view, or merged view)

## 4. Raw View Rendering

- [x] 4.1 Add `getRawSSEHtml()` method that renders the original SSE text with `data:` prefixes highlighted using a distinct CSS class (`sse-data-prefix`)

## 5. Merged View Rendering

- [x] 5.1 Add `getMergedViewHtml()` method that calls `mergeSSEContent()` and renders the concatenated text in a `<pre>` block, or shows an info message if no content was extractable

## 6. Toggle UI

- [x] 6.1 Add view mode toggle buttons (Raw / Chunks / Merged) in the JSON viewer dialog header, conditionally shown only when `jsonViewerIsSSE` is true
- [x] 6.2 Wire toggle buttons to set `jsonViewerMode` on click
- [x] 6.3 Update copy button behavior: in Chunks mode copy the full raw SSE text, in Merged mode copy the merged content, in Raw mode copy the raw text

## 7. Styling

- [x] 7.1 Add CSS styles in `input.css` for the view mode toggle buttons (active/inactive states, light/dark mode)
- [x] 7.2 Add CSS styles for `sse-data-prefix` highlight class
- [x] 7.3 Add styles for chunk headers in Chunks view
- [x] 7.4 Rebuild CSS with `build_css.sh`

## 8. Verification

- [x] 8.1 Verify SSE detection works for streaming response bodies and doesn't trigger for non-SSE content
- [x] 8.2 Verify Chunks view renders each SSE chunk as a collapsible tree
- [x] 8.3 Verify Raw view displays original SSE text with highlighted prefixes
- [x] 8.4 Verify Merged view concatenates delta.content into readable text
- [x] 8.5 Verify toggle is hidden for non-SSE content
- [x] 8.6 Verify copy works correctly in all three modes
