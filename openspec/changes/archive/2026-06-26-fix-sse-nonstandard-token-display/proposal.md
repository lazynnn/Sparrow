## Why

Backend SSE token extraction parsers use strict `data: ` (with space) prefix matching. When LLM routers emit non-standard `data:` (no space) format, the parsers skip all data lines, causing token values (prompt_tokens, completion_tokens, total_tokens) to be stored as null — and the web-ui shows no token information. The frontend was already fixed (commit 52bfeeb) to accept both formats, but the backend was not updated, creating a display gap.

## What Changes

- Update `OpenAIChatParser.extract_token_usage_from_sse()` to accept both `data: ` and `data:` prefixes using regex matching instead of `startswith("data: ")`
- Update `AnthropicMessagesParser.extract_token_usage_from_sse()` to accept both `data: ` and `data:` prefixes, and also handle `event:` lines without a required space
- Update `OpenAIResponsesParser.extract_token_usage_from_sse()` to accept both `data: ` and `data:` prefixes
- Replace hardcoded `line[6:]` slicing with regex capture group for dynamic prefix length
- Update existing tests to cover non-standard SSE format token extraction

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `flexible-sse-prefix`: Extend requirement coverage from frontend-only to include backend SSE token extraction parsers

## Impact

- **Code**: Three Python parser files in `sparrow/tracing/parsers/` — `openai_chat.py`, `anthropic_messages.py`, `openai_responses.py`
- **Tests**: Existing test files in `tests/` need new test cases for non-standard format
- **API/Dependencies**: No API changes, no new dependencies
- **Systems**: Token values will display correctly in web-ui for non-standard SSE responses
