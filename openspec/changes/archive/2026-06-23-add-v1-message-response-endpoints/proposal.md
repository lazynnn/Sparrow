## Why

Sparrow currently only understands OpenAI Chat Completions response format (`/v1/chat/completions`). The Anthropic Messages API (`/v1/messages`) and OpenAI Responses API (`/v1/responses`) use different request/response schemas — different token field names (`input_tokens`/`output_tokens` vs `prompt_tokens`/`completion_tokens`), different SSE streaming formats, and different authentication patterns. Without explicit support, requests to these endpoints are proxied but token usage, model names, and costs are not extracted, making tracing and cost tracking useless for non-Chat-Completions APIs.

## What Changes

- Add Anthropic `/v1/messages` response parsing: extract model name, token usage (`input_tokens`/`output_tokens`), and cost from both non-streaming and streaming (event-prefixed SSE) responses
- Add OpenAI `/v1/responses` response parsing: extract model name, token usage, and cost from the newer Responses API format
- Add route-aware response parser selection based on the request path, so each endpoint uses the correct extraction logic
- Support Anthropic SSE streaming format which uses `event:` lines (`message_start`, `content_block_delta`, `message_delta`, `message_stop`) alongside `data:` lines
- Map Anthropic token fields (`input_tokens`/`output_tokens`) to the existing trace model fields (`prompt_tokens`/`completion_tokens`)

## Capabilities

### New Capabilities
- `anthropic-messages-endpoint`: Anthropic Messages API (`/v1/messages`) support — request parsing, response token extraction, SSE streaming format handling, and field mapping for tracing and cost tracking
- `openai-responses-endpoint`: OpenAI Responses API (`/v1/responses`) support — request parsing, response token extraction, and streaming format handling for tracing and cost tracking

### Modified Capabilities
- `transparent-proxy`: Add route-aware response parser dispatch so the proxy selects the correct parser based on the request path
- `cost-tracking`: Extend token extraction to handle `input_tokens`/`output_tokens` field names and the Anthropic SSE event format in addition to the existing OpenAI Chat Completions format

## Impact

- **API**: No changes to existing API routes or proxy behavior — backward compatible
- **Tracing**: `sparrow/tracing/tracer.py` — new extraction functions, route-aware dispatch logic
- **Streaming**: `sparrow/proxy/streaming.py` — may need SSE format detection for Anthropic event-prefixed streams
- **Proxy router**: `sparrow/proxy/router.py` — pass request path context to tracing for parser selection
- **Config**: `sparrow/config.py` — no changes needed; existing route prefix config works for routing
- **Models**: No schema changes; Anthropic fields map to existing `prompt_tokens`/`completion_tokens` columns
