import pytest

from sparrow.tracing.cost import calculate_cost
from sparrow.tracing.parsers.openai_chat import OpenAIChatParser
from sparrow.config import ModelPricing

_chat = OpenAIChatParser()


class TestCostCalculation:
    def test_known_model(self):
        pricing = {"gpt-4o": ModelPricing(input=2.50, output=10.00)}
        cost = calculate_cost(1000, 500, "gpt-4o", pricing)
        assert cost == pytest.approx(0.0075)

    def test_unknown_model(self):
        pricing = {"gpt-4o": ModelPricing(input=2.50, output=10.00)}
        cost = calculate_cost(1000, 500, "unknown-model", pricing)
        assert cost is None

    def test_null_model(self):
        pricing = {"gpt-4o": ModelPricing(input=2.50, output=10.00)}
        cost = calculate_cost(1000, 500, None, pricing)
        assert cost is None

    def test_partial_tokens(self):
        pricing = {"gpt-4o": ModelPricing(input=2.50, output=10.00)}
        cost = calculate_cost(1000, None, "gpt-4o", pricing)
        assert cost == pytest.approx(0.0025)

    def test_zero_tokens(self):
        pricing = {"gpt-4o": ModelPricing(input=2.50, output=10.00)}
        cost = calculate_cost(0, 0, "gpt-4o", pricing)
        assert cost == 0.0

    def test_null_tokens(self):
        pricing = {"gpt-4o": ModelPricing(input=2.50, output=10.00)}
        cost = calculate_cost(None, None, "gpt-4o", pricing)
        assert cost == 0.0


class TestOpenAIChatTokenExtraction:
    def test_non_streaming_response(self):
        body = '{"id":"chatcmpl-123","usage":{"prompt_tokens":10,"completion_tokens":20,"total_tokens":30}}'
        tokens = _chat.extract_token_usage(body)
        assert tokens["prompt_tokens"] == 10
        assert tokens["completion_tokens"] == 20
        assert tokens["total_tokens"] == 30

    def test_missing_usage(self):
        body = '{"id":"chatcmpl-123"}'
        tokens = _chat.extract_token_usage(body)
        assert tokens["prompt_tokens"] is None
        assert tokens["completion_tokens"] is None
        assert tokens["total_tokens"] is None

    def test_none_body(self):
        tokens = _chat.extract_token_usage(None)
        assert tokens["prompt_tokens"] is None

    def test_invalid_json(self):
        tokens = _chat.extract_token_usage("not json")
        assert tokens["prompt_tokens"] is None

    def test_sse_streaming(self):
        chunks = (
            'data: {"id":"chatcmpl-1","choices":[{"delta":{"content":"Hello"}}]}\n'
            'data: {"id":"chatcmpl-1","choices":[{"delta":{"content":" world"}}]}\n'
            'data: {"id":"chatcmpl-1","usage":{"prompt_tokens":5,"completion_tokens":2,"total_tokens":7}}\n'
            "data: [DONE]\n"
        )
        tokens = _chat.extract_token_usage_from_sse(chunks)
        assert tokens["prompt_tokens"] == 5
        assert tokens["completion_tokens"] == 2
        assert tokens["total_tokens"] == 7

    def test_sse_no_usage(self):
        chunks = (
            'data: {"id":"chatcmpl-1","choices":[{"delta":{"content":"Hi"}}]}\n'
            "data: [DONE]\n"
        )
        tokens = _chat.extract_token_usage_from_sse(chunks)
        assert tokens["prompt_tokens"] is None

    def test_sse_empty(self):
        tokens = _chat.extract_token_usage_from_sse("")
        assert tokens["prompt_tokens"] is None

    def test_sse_nonstandard_prefix(self):
        chunks = (
            'data:{"id":"chatcmpl-1","choices":[{"delta":{"content":"Hello"}}]}\n'
            'data:{"id":"chatcmpl-1","usage":{"prompt_tokens":5,"completion_tokens":2,"total_tokens":7}}\n'
            "data:[DONE]\n"
        )
        tokens = _chat.extract_token_usage_from_sse(chunks)
        assert tokens["prompt_tokens"] == 5
        assert tokens["completion_tokens"] == 2
        assert tokens["total_tokens"] == 7

    def test_sse_mixed_prefix(self):
        chunks = (
            'data: {"id":"chatcmpl-1","choices":[{"delta":{"content":"Hello"}}]}\n'
            'data:{"id":"chatcmpl-1","usage":{"prompt_tokens":10,"completion_tokens":5,"total_tokens":15}}\n'
            "data: [DONE]\n"
        )
        tokens = _chat.extract_token_usage_from_sse(chunks)
        assert tokens["prompt_tokens"] == 10
        assert tokens["completion_tokens"] == 5
        assert tokens["total_tokens"] == 15


class TestOpenAIChatModelNameExtraction:
    def test_extract_model(self):
        body = '{"model":"gpt-4o","messages":[]}'
        assert _chat.extract_model_name(body) == "gpt-4o"

    def test_no_model(self):
        body = '{"messages":[]}'
        assert _chat.extract_model_name(body) is None

    def test_none_body(self):
        assert _chat.extract_model_name(None) is None

    def test_invalid_json(self):
        assert _chat.extract_model_name("not json") is None
