from enum import Enum


class LLMProvider(Enum):
    OpenAI = 1
    Anthropic = 2
    Gemini = 3


class LLMRequestParameter(Enum):
    ROLE = "role"
    CONTENT = "content"

class GeminiRequestParameter(Enum):
    ROLE = "role"
    CONTENT = "parts"
