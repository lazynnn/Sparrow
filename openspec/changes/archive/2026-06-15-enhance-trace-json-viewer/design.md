## Context

The Sparrow web UI is a single-page application built with Alpine.js and Tailwind CSS, served by FastAPI. The trace detail view is a slide-over panel that displays request/response bodies and headers in `<pre>` blocks with a `max-h-80` (320px) constraint and basic custom syntax highlighting. For LLM API traces, request and response bodies are often very large (thousands of lines of JSON), making the constrained view impractical for inspection. The existing codebase has no dialog/modal pattern beyond the slide-over panel itself, and all UI dependencies are vendored (no Node.js build chain).

## Goals / Non-Goals

**Goals:**
- Provide a fullscreen overlay dialog for viewing JSON data with enough space to read large payloads comfortably
- Enable collapsible/expandable JSON nodes so users can focus on relevant sections
- Add copy-to-clipboard functionality for the full JSON content
- Add search/filter within the JSON content
- Maintain consistency with the existing Alpine.js + Tailwind CSS architecture (no new external dependencies)

**Non-Goals:**
- Replacing the inline preview in the trace detail panel — it stays as a quick-glance view
- Adding JSON editing capabilities — the viewer is read-only
- Adding JSON diff/comparison between request and response
- Adding server-side changes — all data is already available from the existing API
- Introducing a Node.js dependency or npm package — everything stays vendored

## Decisions

### 1. Custom JSON tree renderer over external library

**Decision**: Build a recursive Alpine.js component that renders JSON as a collapsible tree with `<details>/<summary>` HTML elements, rather than importing a library like `json-viewer` or `monaco-editor`.

**Rationale**: The project has no Node.js build chain and all dependencies are vendored. Adding an npm package would require introducing a bundler. A custom tree renderer using native `<details>/<summary>` elements provides collapsible nodes for free (no JS needed for toggle), is lightweight, and stays consistent with the project's minimal dependency approach. The existing `syntaxHighlight()` function can be reused for leaf values.

**Alternatives considered**:
- **json-viewer npm package**: Would require a build system, breaking the vendored approach
- **Monaco editor**: Overkill for read-only viewing, heavy (~2MB), requires build tooling
- **iframe with formatted JSON**: No interactivity (no collapse/search/copy)

### 2. Fullscreen overlay dialog over centered modal

**Decision**: Use a fullscreen overlay dialog (100vw x 100vh) rather than a centered modal.

**Rationale**: Large JSON payloads need maximum screen real estate. A centered modal with fixed dimensions would still feel cramped. A fullscreen dialog gives the viewer the entire viewport, which is the primary goal — better readability for long data.

### 3. Alpine.js x-data component for dialog state

**Decision**: Manage the dialog state (open/close, content, search query) as an Alpine.js `x-data` component attached to the dialog container, with `jsonViewer` as the component name.

**Rationale**: Keeps dialog state separate from the main app component. Alpine.js `x-data` provides reactive bindings natively. The dialog will receive the JSON string and title as props when opened via `x-show` + state mutation.

### 4. Search via text matching with highlight

**Decision**: Implement search as a simple text-matching filter that highlights matching nodes and auto-expands their parent paths.

**Rationale**: Full JSONPath query is overkill. Users primarily want to find a key or value quickly. Text matching against stringified key/value pairs is simple to implement and covers the common case. Matching nodes will be highlighted with a background color, and all ancestor `<details>` elements will be programmatically opened.

### 5. Copy-to-clipboard using navigator.clipboard API

**Decision**: Use the browser's `navigator.clipboard.writeText()` API with a fallback for older browsers.

**Rationale**: No additional library needed. The clipboard API is widely supported. A brief visual feedback (button text change to "Copied!") will confirm the action.

## Risks / Trade-offs

- **[Performance with very large JSON]** → For extremely large payloads (100k+ lines), the recursive tree renderer could be slow. Mitigation: initially render only the top-level keys with lazy expansion for deeply nested structures, or fall back to the plain `<pre>` view for payloads exceeding a size threshold (e.g., 500KB).
- **[Search performance on large JSON]** → Searching through a large rendered DOM could be slow. Mitigation: search against the raw JSON string first, then only expand/highlight matching paths rather than scanning the full DOM.
- **[No external dependency means more custom code]** → Custom tree renderer adds ~150-200 lines of JS. Mitigation: `<details>/<summary>` keeps the implementation simple; the code is straightforward and testable.
