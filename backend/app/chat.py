import os
from abc import ABCMeta, abstractmethod

from anthropic import Anthropic
from anthropic import BadRequestError as AnthropicBadRequestError
from const import GeminiRequestParameter, LLMProvider, LLMRequestParameter
from db import MessageRole, select_message_details
from fastapi import status
from fastapi_custom_route import LOGGER
from google import generativeai as genai
from models.app_coordinator import AppMessage
from openai import BadRequestError as OpenAIBadRequestError
from openai import OpenAI

TITLE_PROMPT = (
    "入力された内容を要約してタイトルを生成してください。\n"
    "また出力フォーマットにしたがってください。\n\n"
    "## 出力フォーマット\n"
    "文字列\n\n"
    "## 入力例\n"
    "ここにメッセージが入ります。\n\n"
    "## 出力例\n"
    "タイトルA\n\n"
    "## 入力された内容\n"
    "{message}\n\n"
    "## タイトル\n"
)


class BaseAPIRequester(metaclass=ABCMeta):
    def __init__(self, model: str) -> None:
        self.model = model

    @abstractmethod
    def format_messages(self, role, file_path=None, file_name=None, message=None):
        pass

    @abstractmethod
    def make_request_format(self):
        pass

    @abstractmethod
    def request(self):
        pass

class OpenAIAPIRequester(BaseAPIRequester):
    def __init__(self, model: str) -> None:
        super().__init__(model)

    def format_messages(self, role, file_path=None, file_name=None, message=None):
        content = []
        if message:
            content.append({
                "type": "text",
                "text": message
            })
        if file_path:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/{file_name.split('.')[-1]};base64,{file_path}"
                }
            })

        return {
            LLMRequestParameter.ROLE.value: role,
            LLMRequestParameter.CONTENT.value: content if len(content) == 2 else message
        }

    def make_request_format(self, message_id: int, parameter: AppMessage):
        # TODO: ファイルの送信が未実装
        messages = []
        message_details = select_message_details(message_id)
        for message in message_details:
            messages.append(self.format_messages(
                                role=message.role,
                                file_path=message.file_path,
                                file_name=message.file_name,
                                message=message.message))
        messages.append(self.format_messages(
            role="user",
            file_path=parameter.file,
            file_name=parameter.file_name,
            message=parameter.message
        ))
        return messages

    def request(self, messages: list):
        return chat_openai(messages, self.model)


class AnthropicAPIRequester(BaseAPIRequester):

    def __init__(self, model: str) -> None:
        super().__init__(model)

    def format_messages(self, role, file_path=None, file_name=None, message=None):
        content = []
        if file_path and file_name:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": f"image/{file_name.split('.')[-1]}",
                    "data": file_path,
                }
            })
        if message:
            content.append({
                "type": "text",
                "text": message
            })
        return {
            LLMRequestParameter.ROLE.value: role,
            LLMRequestParameter.CONTENT.value: content if len(content) == 2 else message
        }

    def make_request_format(self, message_id: int, parameter: AppMessage):
        messages = []
        message_details = select_message_details(message_id)
        for message_model in message_details:
            messages.append(self.format_messages(
                role=message_model.role,
                file_path=message_model.file_path,
                file_name=message_model.file_name,
                message=message_model.message
            ))
        messages.append(self.format_messages(
            role="user",
            file_path=parameter.file,
            file_name=parameter.file_name,
            message=parameter.message
        ))

        return messages

    def request(self, messages: list):
        return chat_anthropic(messages, self.model)


class GeminiAPIRequester(BaseAPIRequester):
    def __init__(self, model: str) -> None:
        super().__init__(model)

    def format_messages(self, role, file_path=None, file_name=None, message=None):

        return {
            GeminiRequestParameter.ROLE.value: role,
            GeminiRequestParameter.CONTENT.value: message
        }

    def make_request_format(self, message_id: int, parameter: AppMessage):
        messages = []
        message_details = select_message_details(message_id)
        for message in message_details:
            messages.append(self.format_messages(
                                role= "model" if message.role == MessageRole.ASSISTANT else message.role,
                                file_path=message.file_path,
                                file_name=message.file_name,
                                message=message.message))
        messages.append(self.format_messages(
            role=None, # Gemini は role が不要
            file_path=parameter.file,
            file_name=parameter.file_name,
            message=parameter.message
        ))
        return messages

    def request(self, messages: list):
        return chat_gemini(messages, self.model)


class APIClient:
    # MEMO: LangChain を導入すると、もっとシンプルに実装できるが、後方互換性を考慮して未導入
    def __init__(self, service_type: LLMProvider, model: str) -> None:
        if service_type == LLMProvider.Anthropic:
            self.service = AnthropicAPIRequester(model=model)
        elif service_type == LLMProvider.OpenAI:
            self.service = OpenAIAPIRequester(model=model)
        elif service_type == LLMProvider.Gemini:
            self.service = GeminiAPIRequester(model=model)
        else:
            raise ValueError("Invalid service type")


def generate_title(message: str):
    """
    入力された内容を要約してタイトルを生成する
    """

    content = TITLE_PROMPT.format(message=message)
    default_model = "gpt-4o-mini-2024-07-18"
    title, http_staus = chat_openai([{LLMRequestParameter.ROLE.value: "user",
                                      LLMRequestParameter.CONTENT.value: content}], default_model)
    if title == "":
        return ""
    return title.rstrip()


def chat_openai(messages: list, model: str):
    try:
        client = OpenAI()
        response = client.chat.completions.create(model=model, temperature=0, messages=messages)
    except OpenAIBadRequestError as e:
        LOGGER.error(e)
        return "", e.status_code

    content = response.choices[0].message.content
    return content, status.HTTP_200_OK


def chat_anthropic(messages: list, model: str):
    try:
        client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        response = client.messages.create(model=model, temperature=0, messages=messages, max_tokens=2048)
    except AnthropicBadRequestError as e:
        LOGGER.error(e)
        return "", e.status_code

    content = response.content[0].text
    return content, status.HTTP_200_OK


def chat_gemini(messages: list, model: str):
    try:
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        gemini = genai.GenerativeModel(model)
        chat = gemini.start_chat(history=messages[:-1])
        response = chat.send_message(messages[-1][GeminiRequestParameter.CONTENT.value])
    except Exception as e:
        LOGGER.error(e)
        return "", status.HTTP_500_INTERNAL_SERVER_ERROR

    content = response.text
    return content, status.HTTP_200_OK


def get_model_list() -> list:
    client = OpenAI()

    response = client.models.list()
    return response.data


if __name__ == "__main__":
    print(get_model_list())
