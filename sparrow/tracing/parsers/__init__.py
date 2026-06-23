from sparrow.tracing.parsers.base import ResponseParser, TokenUsage
from sparrow.tracing.parsers.registry import get_parser
from sparrow.tracing.parsers.openai_chat import OpenAIChatParser
from sparrow.tracing.parsers.anthropic_messages import AnthropicMessagesParser
from sparrow.tracing.parsers.openai_responses import OpenAIResponsesParser
from sparrow.tracing.parsers.registry import register, set_default

_chat_parser = OpenAIChatParser()
_anthropic_parser = AnthropicMessagesParser()
_responses_parser = OpenAIResponsesParser()

register("/v1/chat/completions", _chat_parser)
register("/v1/messages", _anthropic_parser)
register("/v1/responses", _responses_parser)
set_default(_chat_parser)

__all__ = ["ResponseParser", "TokenUsage", "get_parser"]
