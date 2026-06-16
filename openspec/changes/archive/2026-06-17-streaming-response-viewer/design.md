## Context

The JSON viewer dialog was added to provide a fullscreen collapsible tree view for inspecting trace data. It works well for valid JSON (non-streaming responses, request bodies, headers). However, streaming responses are stored as raw SSE text — lines of `data: {...}\n\n` — which cannot be parsed as a single JSON object. The current viewer falls back to displaying raw escaped text in a `<pre>` tag, providing no structure or readability.

The existing codebase already has an SSE parser in Python (`extract_token_usage_from_sse()` in `tracer.py`), but nothing equivalent in the frontend.

## Goals / Non-Goals

**Goals:**
- Detect SSE-formatted content in the JSON viewer and offer view modes suited for streaming data
- Provide a Chunks view that parses each `data:` line into a collapsible JSON tree per chunk
- Provide a Merged view that concatenates all `delta.content` fields into a single readable string
- Keep the Raw view for seeing the exact SSE wire format
- Auto-detect SSE and default to Chunks view when detected

**Non-Goals:**
- Modifying backend storage or API — streaming data is already stored as raw SSE text
- Reconstructing a complete non-streaming JSON response from SSE chunks (chunks may differ across API providers)
- Supporting non-OpenAI SSE formats (e.g., custom event types, binary SSE) — focus on `data:` prefix convention
- Editing or modifying SSE data in the viewer

## Decisions

### 1. Three view modes: Raw, Chunks, Merged

**Decision**: Offer three toggle-able views when SSE is detected.

**Rationale**: Each view serves a distinct purpose:
- **Raw**: Exact wire format, essential for debugging SSE protocol issues
- **Chunks**: Parsed JSON per chunk, best for inspecting individual SSE events and their structure
- **Merged**: Concatenated `delta.content` values, best for reading the full assistant response text

Two modes (Raw + Chunks) would miss the readability use case. Two modes (Raw + Merged) would miss the per-chunk inspection use case. Three covers all common needs.

**Alternatives considered**:
- **Two modes (Raw + Parsed)**: Would require choosing between per-chunk vs merged as the single parsed view — both are important
- **Auto-merge into single JSON**: Not possible since SSE chunks are deltas, not complete objects

### 2. Client-side SSE detection and parsing

**Decision**: Detect SSE format and parse chunks entirely in JavaScript within the viewer, no backend changes.

**Rationale**: The raw SSE text is already available in the viewer. Parsing `data:` lines with `JSON.parse()` per line is trivial in JS. No need for a new API endpoint or server-side transformation. Matches the existing pattern of all viewer logic being client-side.

### 3. SSE detection heuristic

**Decision**: Detect SSE by checking if the content contains at least one line starting with `data: `.

**Rationale**: This is the universal SSE convention. False positives are extremely unlikely for trace response data. Simple, fast, and covers all OpenAI-compatible API formats including `data: [DONE]`.

**Alternatives considered**:
- **Use `is_streaming` flag from trace metadata**: Would require passing the flag to the viewer and coupling detection to trace metadata rather than the content itself
- **Try JSON.parse first, then check SSE**: Unnecessary — if it's valid JSON, the existing viewer handles it; if not, checking for SSE lines is the right fallback

### 4. Chunks view rendering

**Decision**: Render each SSE chunk as a separate collapsible JSON tree, with a header showing the chunk index (e.g., "Chunk 1", "Chunk 2").

**Rationale**: Reuses the existing `_renderJsonTree()` function per chunk. Chunk headers provide visual separation and easy navigation. `data: [DONE]` lines are displayed as plain text markers, not parsed as JSON.

### 5. Merged view content extraction

**Decision**: Extract `choices[].delta.content` from each chunk (OpenAI format) and concatenate all non-null/non-empty values into a single string, displayed in a `<pre>` block.

**Rationale**: The `delta.content` field is the standard path for text content in OpenAI-compatible streaming responses. This produces the readable assistant message that users most often want to see. If chunks don't follow this format (e.g., embedding responses), the merged view shows an informational message.

## Risks / Trade-offs

- **[Non-OpenAI SSE formats]** → Different API providers may use different JSON structures for streaming chunks. Mitigation: The Chunks view works for any SSE format since it parses each chunk independently. The Merged view is OpenAI-specific but shows an info message if no `delta.content` is found.
- **[Very large streaming responses]** → Hundreds of chunks could produce a long Chunks view. Mitigation: The existing scrollable dialog and collapsible trees handle this reasonably. Could add chunk count indicator.
- **[SSE detection false positive]** → Extremely unlikely, but if non-SSE text happens to start with `data: `, it would trigger the toggle. Mitigation: The Raw view always shows the original content, so no data is lost.
