import pytest

from sparrow.tracing.parsers.openai_responses import OpenAIResponsesParser

_parser = OpenAIResponsesParser()


class TestOpenAIResponsesModelNameExtraction:
    def test_extract_model(self):
        body = '{"model":"gpt-4o","input":"Hello"}'
        assert _parser.extract_model_name(body) == "gpt-4o"

    def test_no_model(self):
        body = '{"input":"Hello"}'
        assert _parser.extract_model_name(body) is None

    def test_none_body(self):
        assert _parser.extract_model_name(None) is None

    def test_invalid_json(self):
        assert _parser.extract_model_name("not json") is None


class TestOpenAIResponsesTokenExtraction:
    def test_non_streaming_with_total(self):
        body = '{"id":"resp_123","usage":{"input_tokens":100,"output_tokens":200,"total_tokens":300}}'
        tokens = _parser.extract_token_usage(body)
        assert tokens["prompt_tokens"] == 100
        assert tokens["completion_tokens"] == 200
        assert tokens["total_tokens"] == 300

    def test_non_streaming_without_total(self):
        body = '{"id":"resp_123","usage":{"input_tokens":100,"output_tokens":200}}'
        tokens = _parser.extract_token_usage(body)
        assert tokens["prompt_tokens"] == 100
        assert tokens["completion_tokens"] == 200
        assert tokens["total_tokens"] == 300

    def test_missing_usage(self):
        body = '{"id":"resp_123"}'
        tokens = _parser.extract_token_usage(body)
        assert tokens["prompt_tokens"] is None
        assert tokens["completion_tokens"] is None
        assert tokens["total_tokens"] is None

    def test_none_body(self):
        tokens = _parser.extract_token_usage(None)
        assert tokens["prompt_tokens"] is None

    def test_invalid_json(self):
        tokens = _parser.extract_token_usage("not json")
        assert tokens["prompt_tokens"] is None


class TestOpenAIResponsesSSEExtraction:
    def test_stream_with_completed_event(self):
        chunks = (
            'data: {"type":"response.output_item.added","output_index":0}\n'
            "\n"
            'data: {"type":"response.output_text.delta","delta":"Hello"}\n'
            "\n"
            'data: {"type":"response.completed","response":{"id":"resp_1","usage":{"input_tokens":50,"output_tokens":75,"total_tokens":125}}}\n'
            "\n"
        )
        tokens = _parser.extract_token_usage_from_sse(chunks)
        assert tokens["prompt_tokens"] == 50
        assert tokens["completion_tokens"] == 75
        assert tokens["total_tokens"] == 125

    def test_stream_without_completed_event(self):
        chunks = 'data: {"type":"response.output_text.delta","delta":"Hello"}\n\n'
        tokens = _parser.extract_token_usage_from_sse(chunks)
        assert tokens["prompt_tokens"] is None
        assert tokens["completion_tokens"] is None

    def test_stream_empty(self):
        tokens = _parser.extract_token_usage_from_sse("")
        assert tokens["prompt_tokens"] is None

    def test_stream_completed_without_total(self):
        chunks = (
            'data: {"type":"response.completed","response":{"id":"resp_1","usage":{"input_tokens":40,"output_tokens":60}}}\n'
            "\n"
        )
        tokens = _parser.extract_token_usage_from_sse(chunks)
        assert tokens["prompt_tokens"] == 40
        assert tokens["completion_tokens"] == 60
        assert tokens["total_tokens"] == 100

    def test_nonstandard_prefix(self):
        chunks = (
            'data:{"type":"response.output_item.added","output_index":0}\n'
            "\n"
            'data:{"type":"response.output_text.delta","delta":"Hello"}\n'
            "\n"
            'data:{"type":"response.completed","response":{"id":"resp_1","usage":{"input_tokens":50,"output_tokens":75,"total_tokens":125}}}\n'
            "\n"
        )
        tokens = _parser.extract_token_usage_from_sse(chunks)
        assert tokens["prompt_tokens"] == 50
        assert tokens["completion_tokens"] == 75
        assert tokens["total_tokens"] == 125
