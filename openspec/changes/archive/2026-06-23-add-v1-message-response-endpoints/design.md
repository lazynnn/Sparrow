## Context

Sparrow is a transparent LLM gateway proxy built with FastAPI. It currently proxies all requests through a catch-all `/{path:path}` route, using config-based prefix matching to determine the target URL. The tracing layer extracts model names and token usage from request/response bodies, but only understands the OpenAI Chat Completions format (`usage.prompt_tokens`/`completion_tokens`/`total_tokens` and OpenAI-style SSE `data:` lines).

Anthropic's Messages API (`/v1/messages`) and OpenAI's Responses API (`/v1/responses`) use different schemas:
- Anthropic: `input_tokens`/`output_tokens` in `usage`, SSE with `event:` prefix lines, `x-api-key` auth header
- OpenAI Responses: `input_tokens`/`output_tokens`/`total_tokens` in `usage`, different streaming event types

The existing codebase has no concept of endpoint-specific parsing — `extract_token_usage()` and `extract_token_usage_from_sse()` assume a single format.

## Goals / Non-Goals

**Goals:**
- Extract model name, token usage, and cost from Anthropic `/v1/messages` responses (streaming and non-streaming)
- Extract model name, token usage, and cost from OpenAI `/v1/responses` responses (streaming and non-streaming)
- Route-aware parser dispatch: select the correct extraction logic based on the request path
- Map Anthropic/OpenAI Responses token fields to existing trace model columns
- Maintain full backward compatibility with existing `/v1/chat/completions` behavior

**Non-Goals:**
- Modifying the proxy routing or request forwarding logic (transparent proxy stays transparent)
- Adding new database columns or migration
- Implementing request/response transformation (no protocol translation between API formats)
- Adding authentication middleware for Anthropic's `x-api-key` header (passthrough only)

## Decisions

### Decision 1: Endpoint parser registry with path-based dispatch

Create a registry that maps request path patterns to response parser functions. When a request is traced, the path is matched against registered patterns to select the correct parser for token/model extraction.

**Rationale**: Keeps parser selection decoupled from the proxy router. Adding future endpoints (e.g., `/v1/embeddings`) requires only registering a new parser — no changes to core proxy code.

**Alternatives considered**:
- *Hardcoded if/else in tracer*: Simpler but doesn't scale and violates OCP. Rejected.
- *Config-driven parser mapping*: Over-engineered for the current scope. Could be added later if needed.

### Decision 2: Anthropic SSE parser handles `event:` + `data:` line pairs

Anthropic streaming uses a two-line SSE format: an `event:` line followed by a `data:` line. The parser must accumulate both to determine event type before parsing the JSON payload. Token usage appears in `message_start` (input tokens) and `message_delta` (output tokens) events.

**Rationale**: The existing SSE parser only looks for `data:` lines. Anthropic's format requires tracking the current event type to know which data payloads contain usage info.

**Alternatives considered**:
- *Generic SSE parser*: Could parse all SSE formats uniformly, but adds complexity for edge cases. Rejected — endpoint-specific parsers are clearer and easier to test.

### Decision 3: Token field mapping layer

Each endpoint parser returns a normalized dict with `prompt_tokens`, `completion_tokens`, `total_tokens`. Anthropic's `input_tokens` maps to `prompt_tokens`, `output_tokens` maps to `completion_tokens`. OpenAI Responses uses the same mapping. `total_tokens` is computed as the sum if not provided.

**Rationale**: Avoids schema changes to the Trace model and all downstream code (API, UI, cost calculation). The mapping is transparent and lossless for the fields we track.

**Alternatives considered**:
- *Add input_tokens/output_tokens columns*: Requires DB migration and UI changes. Rejected — the semantic mapping is 1:1.

### Decision 4: Parser modules per endpoint family

Create `sparrow/tracing/parsers/` directory with:
- `base.py` — parser protocol/ABC and normalized return type
- `openai_chat.py` — existing Chat Completions logic (extracted from tracer.py)
- `openai_responses.py` — Responses API parser
- `anthropic_messages.py` — Anthropic Messages API parser
- `registry.py` — path-to-parser mapping and dispatch

**Rationale**: Separates concerns, makes each parser independently testable. Existing code is refactored out of the monolithic `tracer.py`.

**Alternatives considered**:
- *Single file with all parsers*: Gets unwieldy as more endpoints are added. Rejected.
- *Class-based with inheritance*: Over-engineered for stateless parsing functions. Functions with a shared protocol are sufficient.

## Risks / Trade-offs

- **[Anthropic SSE format edge cases]** → Anthropic's SSE spec can have multiline `data:` payloads and may include `message_start` with partial usage then `message_delta` with the rest. The parser must accumulate usage across events. Mitigation: Parse both `message_start` and `message_delta`, merge token counts.

- **[Path matching ambiguity]** → A path like `/v1/messages` could match multiple patterns. Mitigation: Use exact prefix matching (e.g., `/v1/messages` exactly, not just `/v1/mess`) and fall back to the default OpenAI Chat parser for unrecognized paths.

- **[Breaking existing extraction logic]** → Refactoring `extract_token_usage` and `extract_token_usage_from_sse` out of `tracer.py` risks regressions. Mitigation: Existing unit tests must continue passing; add new tests before refactoring.

- **[OpenAI Responses API evolution]** → The Responses API is relatively new and may change. Mitigation: Keep the parser simple, handle missing fields gracefully (return None), and update as the API stabilizes.
