## 1. Parser Infrastructure

- [x] 1.1 Create `sparrow/tracing/parsers/` package with `__init__.py`
- [x] 1.2 Create `sparrow/tracing/parsers/base.py` — define `TokenUsage` TypedDict and `ResponseParser` protocol with `extract_model_name`, `extract_token_usage`, and `extract_token_usage_from_sse` methods
- [x] 1.3 Create `sparrow/tracing/parsers/registry.py` — implement path-to-parser mapping with `get_parser(request_path: str) -> ResponseParser` that returns the correct parser based on the path, falling back to OpenAI Chat

## 2. OpenAI Chat Completions Parser (Refactor)

- [x] 2.1 Create `sparrow/tracing/parsers/openai_chat.py` — extract existing `extract_model_name`, `extract_token_usage`, and `extract_token_usage_from_sse` logic from `tracer.py` into a `OpenAIChatParser` class
- [x] 2.2 Register `/v1/chat/completions` and default fallback in the registry to use `OpenAIChatParser`
- [x] 2.3 Update `tracer.py` to delegate to the registry instead of calling extraction functions directly

## 3. Anthropic Messages Parser

- [x] 3.1 Create `sparrow/tracing/parsers/anthropic_messages.py` — implement `AnthropicMessagesParser` with `extract_model_name` (reads `model` from request body), `extract_token_usage` (maps `input_tokens`/`output_tokens` to `prompt_tokens`/`completion_tokens`), and `extract_token_usage_from_sse` (parses `message_start` and `message_delta` events)
- [x] 3.2 Register `/v1/messages` path in the registry to use `AnthropicMessagesParser`

## 4. OpenAI Responses Parser

- [x] 4.1 Create `sparrow/tracing/parsers/openai_responses.py` — implement `OpenAIResponsesParser` with `extract_model_name` (reads `model` from request body), `extract_token_usage` (maps `input_tokens`/`output_tokens`, computes `total_tokens` if missing), and `extract_token_usage_from_sse` (parses `response.completed` event)
- [x] 4.2 Register `/v1/responses` path in the registry to use `OpenAIResponsesParser`

## 5. Proxy Router Integration

- [x] 5.1 Update `sparrow/proxy/router.py` to pass the `request_path` to `save_trace` so the tracer can select the correct parser
- [x] 5.2 Update `sparrow/tracing/tracer.py` `save_trace` signature to accept `request_path` and use the parser registry to select the appropriate parser before calling extraction methods

## 6. Tests

- [x] 6.1 Add unit tests for `OpenAIChatParser` — verify existing Chat Completions extraction behavior is preserved (non-streaming token extraction, SSE token extraction, model name extraction)
- [x] 6.2 Add unit tests for `AnthropicMessagesParser` — non-streaming token extraction with `input_tokens`/`output_tokens`, SSE parsing with `message_start` and `message_delta` events, model name extraction
- [x] 6.3 Add unit tests for `OpenAIResponsesParser` — non-streaming token extraction with `input_tokens`/`output_tokens`, SSE parsing with `response.completed` event, `total_tokens` computation
- [x] 6.4 Add unit tests for parser registry — path-based dispatch for `/v1/chat/completions`, `/v1/messages`, `/v1/responses`, and fallback for unknown paths
