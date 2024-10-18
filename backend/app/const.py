from enum import Enum


class LLMProvider(Enum):
    OpenAI = 1
    Anthropic = 2


class LLMRequestParameter(Enum):
    ROLE = "role"
    CONTENT = "content"
