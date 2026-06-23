## 1. Update SSE detection

- [x] 1.1 Modify `_isSSE()` in `sparrow/web/static/js/app.js` to detect lines starting with `data:` (with or without trailing space) instead of strict `data: `

## 2. Update SSE chunk parsing

- [x] 2.1 Modify `_parseSSEChunks()` to match `data:` prefix with optional whitespace using regex, extracting payload via capture group instead of hardcoded `slice(6)`
- [x] 2.2 Verify `[DONE]` detection works for both `data: [DONE]` and `data:[DONE]` formats

## 3. Update raw SSE rendering

- [x] 3.1 Modify `getRawSSEHtml()` to highlight `data:` prefix lines (with or without trailing space) using the existing `sse-data-prefix` class

## 4. Verification

- [x] 4.1 Manually verify standard `data: ` SSE responses still render correctly in Raw, Chunks, and Merged views
- [x] 4.2 Manually verify non-standard `data:` SSE responses (no space) render correctly in Raw, Chunks, and Merged views
