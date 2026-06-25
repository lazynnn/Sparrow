## 1. Backend Parser Updates

- [x] 1.1 Update `OpenAIChatParser.extract_token_usage_from_sse()` in `sparrow/tracing/parsers/openai_chat.py`: replace `line.startswith("data: ")` with `re.match(r"^data:\s*(.*)", line)` and use capture group instead of `line[6:]`
- [x] 1.2 Update `AnthropicMessagesParser.extract_token_usage_from_sse()` in `sparrow/tracing/parsers/anthropic_messages.py`: replace `line.startswith("data: ")` and `line.startswith("event: ")` with regex matching, use capture groups instead of `line[6:]` and `line[7:]`
- [x] 1.3 Update `OpenAIResponsesParser.extract_token_usage_from_sse()` in `sparrow/tracing/parsers/openai_responses.py`: replace `line.startswith("data: ")` with `re.match(r"^data:\s*(.*)", line)` and use capture group instead of `line[6:]`

## 2. Test Updates

- [x] 2.1 Add non-standard SSE format test to `TestOpenAIChatTokenExtraction` in `tests/test_tracing.py`: verify token extraction from `data:{"usage":...}` (no space)
- [x] 2.2 Add mixed-prefix SSE test to `TestOpenAIChatTokenExtraction` in `tests/test_tracing.py`: verify token extraction when some lines have space and some don't
- [x] 2.3 Add non-standard SSE format test to `TestAnthropicSSEExtraction` in `tests/test_anthropic_parser.py`: verify token extraction from `data:{"type":"message_start",...}` (no space) with and without `event:` lines
- [x] 2.4 Add non-standard SSE format test to `TestOpenAIResponsesSSEExtraction` in `tests/test_openai_responses_parser.py`: verify token extraction from `data:{"type":"response.completed",...}` (no space)
- [x] 2.5 Run all tests to verify no regressions
