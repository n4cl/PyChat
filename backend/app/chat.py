import os
from abc import abstractmethod

from anthropic import Anthropic
from anthropic import BadRequestError as AnthropicBadRequestError
from const import LLMProvider, LLMRequestParameter
from db import MessageModel, select_message_details
from fastapi import status
from fastapi_custom_route import LOGGER
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


class BaseAPIRequester:
    def __init__(self, model: str) -> None:
        self.model = model


    @abstractmethod
    def get_message_logs(self, message_id: int):
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

    def get_message_logs(self, message_id: int):
        message_details = select_message_details(message_id)
        result = []
        for message in message_details:
            result.append({
                LLMRequestParameter.ROLE.value: message.role,
                LLMRequestParameter.CONTENT.value: message.message
            })
        return result

    def make_request_format(self, message_id: int, parameter: MessageModel):
        # TODO: ファイルの送信が未実装
        messages = self.get_message_logs(message_id)
        messages.append({LLMRequestParameter.ROLE.value: "user", LLMRequestParameter.CONTENT.value: parameter.message})
        return messages

    def request(self, messages: list):
        return chat_openai(messages, self.model)


class AnthropicAPIRequester(BaseAPIRequester):

    def __init__(self, model: str) -> None:
        super().__init__(model)

    def get_message_logs(self, message_id: int):
        message_details = select_message_details(message_id)
        result = []
        for index, message_model in enumerate(message_details):
            if message_model.file_path:
                result.append({
                    LLMRequestParameter.ROLE.value: message_model.role,
                    LLMRequestParameter.CONTENT.value: [{
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": f"image/{message_model.file_name.split('.')[-1]}",
                            "data": message_model.file_path,
                        }
                    }]
                })
                # メッセージが存在しないケースもある
                if message_model.message:
                    result[index][LLMRequestParameter.CONTENT.value].append(
                        {
                            "type": "text",
                            "text": message_model.message
                        }
                    )
            else:
                result.append({
                    LLMRequestParameter.ROLE.value: message_model.role,
                    LLMRequestParameter.CONTENT.value: message_model.message
                })
        return result

    def make_request_format(self, message_id: int, parameter: MessageModel):

        messages = self.get_message_logs(message_id)
        if not parameter.file:
            messages.append({LLMRequestParameter.ROLE.value: "user",
                             LLMRequestParameter.CONTENT.value: parameter.message})
            return messages

        else:
            base_param = {LLMRequestParameter.ROLE.value: "user", LLMRequestParameter.CONTENT.value: []}
            base_param[LLMRequestParameter.CONTENT.value].append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": f"image/{parameter.file_name.split('.')[-1]}",
                    "data": parameter.file,
                },
            })

            if parameter.message:
                base_param[LLMRequestParameter.CONTENT.value].append({
                    "type": "text",
                    "text": parameter.message
                })
        messages.append(base_param)
        return messages

    def request(self, messages: list):
        return chat_anthropic(messages, self.model)


class APIClient:
    # MEMO: LangChain を導入すると、もっとシンプルに実装できるが、後方互換性を考慮して未導入
    def __init__(self, service_type: LLMProvider, model: str) -> None:
        if service_type == LLMProvider.Anthropic:
            self.service = AnthropicAPIRequester(model=model)
        elif service_type == LLMProvider.OpenAI:
            self.service = OpenAIAPIRequester(model=model)
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


def get_model_list() -> list:
    client = OpenAI()

    response = client.models.list()
    return response.data


if __name__ == "__main__":
    print(get_model_list())
