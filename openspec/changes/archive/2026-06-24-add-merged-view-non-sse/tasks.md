## 1. Content Extraction Logic

- [x] 1.1 Add `_mergeNonSSEContent(parsed)` function in `app.js` that extracts `choices[].message.content` and `choices[].message.reasoning_content` (or `reasoning`) from a parsed JSON object, returning `{ reasoning, content }`
- [x] 1.2 Add `getNonSSEMergedViewHtml()` method to the Alpine component that calls `_mergeNonSSEContent` and renders the result using the same `sse-merged-*` CSS classes as the SSE merged view, with a "no extractable content" message fallback

## 2. Viewer Mode Dispatch

- [x] 2.1 Update `getJsonViewerTree()` to handle `jsonViewerMode === 'merged'` in the non-SSE branch by dispatching to `getNonSSEMergedViewHtml()`
- [x] 2.2 Update `openJsonViewer()` so that for non-SSE object content, `jsonViewerMode` defaults to `'json'` (no change needed, but verify the default is preserved)

## 3. UI Toggle for Non-SSE

- [x] 3.1 Add a new `<template x-if>` block in `index.html` for non-SSE content that shows a JSON / Merged toggle (two buttons), placed after the SSE toggle block
- [x] 3.2 Ensure the non-SSE toggle is only visible when `!jsonViewerIsSSE && typeof jsonViewerParsed === 'object' && jsonViewerParsed !== null`

## 4. Copy Handler Update

- [x] 4.1 Update `copyJsonToClipboard()` to handle the non-SSE merged mode: when `!jsonViewerIsSSE && jsonViewerMode === 'merged'`, use `_mergeNonSSEContent` to get the text and format it the same as SSE merged copy (reasoning + separator + content, or whichever exists)

## 5. Verification

- [x] 5.1 Verify non-SSE merged view works with an OpenAI chat completion response containing `choices[].message.content`
- [x] 5.2 Verify non-SSE merged view shows reasoning section for responses with `choices[].message.reasoning_content`
- [x] 5.3 Verify the "no extractable content" message appears for non-OpenAI JSON objects
- [x] 5.4 Verify no toggle appears for non-SSE string content (failed JSON parse)
- [x] 5.5 Verify copy works correctly in non-SSE merged mode
- [x] 5.6 Verify SSE viewer behavior is unchanged
