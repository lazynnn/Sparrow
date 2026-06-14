## 1. JSON Tree Renderer

- [x] 1.1 Add `renderJsonTree(data, searchTerm)` function in `app.js` that recursively generates HTML for a collapsible JSON tree using `<details>/<summary>` elements for objects and arrays, with proper indentation
- [x] 1.2 Implement leaf value rendering that reuses the existing `syntaxHighlight()` function for strings, numbers, booleans, and null values
- [x] 1.3 Add summary indicators for collapsed nodes showing object key count or array length (e.g., `{3 keys}`, `[5 items]`)

## 2. Search Functionality

- [x] 2.1 Add `searchJson(data, term)` function in `app.js` that recursively searches keys and values, returning a set of JSON paths that match
- [x] 2.2 Implement highlight rendering that wraps matching text in `<mark>` elements when a search term is active
- [x] 2.3 Implement auto-expand logic that opens all ancestor `<details>` elements of matching nodes when search results are rendered

## 3. Copy to Clipboard

- [x] 3.1 Add `copyJsonToClipboard(jsonStr)` function in `app.js` using `navigator.clipboard.writeText()` with fallback
- [x] 3.2 Implement visual feedback on the copy button (text changes to "Copied!" for 2 seconds, then reverts)

## 4. Fullscreen Dialog Markup

- [x] 4.1 Add the fullscreen overlay dialog HTML in `index.html` with Alpine.js `x-data` component (`jsonViewer`) managing `isOpen`, `title`, `jsonContent`, `searchTerm`, and `copyFeedback` state
- [x] 4.2 Add dialog header with title, search input, copy button, and close button
- [x] 4.3 Add dialog body that renders the JSON tree using the `renderJsonTree` function
- [x] 4.4 Add Escape key handler to close the dialog (`@keydown.escape`)
- [x] 4.5 Add backdrop click handler to close the dialog

## 5. Trace Detail Panel Integration

- [x] 5.1 Add expand buttons (icon button) next to each JSON section header in the trace detail panel (Request Body, Response Body, Request Headers, Response Headers)
- [x] 5.2 Wire expand buttons to open the JSON viewer dialog with the corresponding data and title
- [x] 5.3 Add `openJsonViewer(title, jsonString)` method to the Alpine.js app component that sets the dialog state and opens it

## 6. Styling

- [x] 6.1 Add Tailwind CSS classes and any custom styles in `input.css` for the fullscreen dialog (backdrop, container, header, search input, tree indentation)
- [x] 6.2 Add styles for search highlight (`<mark>` elements) that work in both light and dark modes
- [x] 6.3 Add styles for collapsed node summary indicators
- [x] 6.4 Rebuild CSS with `build_css.sh`

## 7. Verification

- [x] 7.1 Manually verify dialog opens/closes correctly for all four JSON sections
- [x] 7.2 Manually verify collapsible tree rendering with nested objects and arrays
- [x] 7.3 Manually verify copy-to-clipboard functionality
- [x] 7.4 Manually verify search highlights and auto-expand work correctly
- [x] 7.5 Verify dark mode styling is correct
