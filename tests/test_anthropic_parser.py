import pytest

from sparrow.tracing.parsers.anthropic_messages import AnthropicMessagesParser

_parser = AnthropicMessagesParser()


class TestAnthropicModelNameExtraction:
    def test_extract_model(self):
        body = '{"model":"claude-3-opus-20240229","messages":[]}'
        assert _parser.extract_model_name(body) == "claude-3-opus-20240229"

    def test_no_model(self):
        body = '{"messages":[]}'
        assert _parser.extract_model_name(body) is None

    def test_none_body(self):
        assert _parser.extract_model_name(None) is None

    def test_invalid_json(self):
        assert _parser.extract_model_name("not json") is None


class TestAnthropicTokenExtraction:
    def test_non_streaming_with_usage(self):
        body = '{"id":"msg_123","usage":{"input_tokens":25,"output_tokens":50}}'
        tokens = _parser.extract_token_usage(body)
        assert tokens["prompt_tokens"] == 25
        assert tokens["completion_tokens"] == 50
        assert tokens["total_tokens"] == 75

    def test_non_streaming_with_total_tokens(self):
        body = '{"id":"msg_123","usage":{"input_tokens":25,"output_tokens":50,"total_tokens":80}}'
        tokens = _parser.extract_token_usage(body)
        assert tokens["prompt_tokens"] == 25
        assert tokens["completion_tokens"] == 50
        assert tokens["total_tokens"] == 80

    def test_missing_usage(self):
        body = '{"id":"msg_123"}'
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


class TestAnthropicSSEExtraction:
    def test_full_stream(self):
        chunks = (
            "event: message_start\n"
            'data: {"type":"message_start","message":{"id":"msg_1","usage":{"input_tokens":30}}}\n'
            "\n"
            "event: content_block_start\n"
            'data: {"type":"content_block_start","index":0}\n'
            "\n"
            "event: content_block_delta\n"
            'data: {"type":"content_block_delta","index":0,"delta":{"text":"Hello"}}\n'
            "\n"
            "event: message_delta\n"
            'data: {"type":"message_delta","delta":{"stop_reason":"end_turn"},"usage":{"output_tokens":60}}\n'
            "\n"
            "event: message_stop\n"
            'data: {"type":"message_stop"}\n'
            "\n"
        )
        tokens = _parser.extract_token_usage_from_sse(chunks)
        assert tokens["prompt_tokens"] == 30
        assert tokens["completion_tokens"] == 60
        assert tokens["total_tokens"] == 90

    def test_stream_only_input_tokens(self):
        chunks = (
            "event: message_start\n"
            'data: {"type":"message_start","message":{"usage":{"input_tokens":10}}}\n'
            "\n"
        )
        tokens = _parser.extract_token_usage_from_sse(chunks)
        assert tokens["prompt_tokens"] == 10
        assert tokens["completion_tokens"] is None
        assert tokens["total_tokens"] is None

    def test_stream_no_usage(self):
        chunks = (
            "event: content_block_delta\n"
            'data: {"type":"content_block_delta","delta":{"text":"Hi"}}\n'
            "\n"
        )
        tokens = _parser.extract_token_usage_from_sse(chunks)
        assert tokens["prompt_tokens"] is None
        assert tokens["completion_tokens"] is None

    def test_stream_empty(self):
        tokens = _parser.extract_token_usage_from_sse("")
        assert tokens["prompt_tokens"] is None

    def test_data_only_format(self):
        chunks = (
            'data: {"type":"message_start","message":{"usage":{"input_tokens":15}}}\n'
            "\n"
            'data: {"type":"message_delta","usage":{"output_tokens":25}}\n'
            "\n"
        )
        tokens = _parser.extract_token_usage_from_sse(chunks)
        assert tokens["prompt_tokens"] == 15
        assert tokens["completion_tokens"] == 25
        assert tokens["total_tokens"] == 40
