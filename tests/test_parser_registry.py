from sparrow.tracing.parsers import get_parser
from sparrow.tracing.parsers.anthropic_messages import AnthropicMessagesParser
from sparrow.tracing.parsers.openai_chat import OpenAIChatParser
from sparrow.tracing.parsers.openai_responses import OpenAIResponsesParser


class TestParserRegistry:
    def test_chat_completions_path(self):
        parser = get_parser("/v1/chat/completions")
        assert isinstance(parser, OpenAIChatParser)

    def test_messages_path(self):
        parser = get_parser("/v1/messages")
        assert isinstance(parser, AnthropicMessagesParser)

    def test_responses_path(self):
        parser = get_parser("/v1/responses")
        assert isinstance(parser, OpenAIResponsesParser)

    def test_unknown_path_falls_back_to_chat(self):
        parser = get_parser("/v1/embeddings")
        assert isinstance(parser, OpenAIChatParser)

    def test_path_with_query_params(self):
        parser = get_parser("/v1/messages?version=2023-06-01")
        assert isinstance(parser, AnthropicMessagesParser)

    def test_subpath_match(self):
        parser = get_parser("/v1/chat/completions/extra")
        assert isinstance(parser, OpenAIChatParser)
