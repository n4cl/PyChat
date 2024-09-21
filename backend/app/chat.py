import os

from anthropic import Anthropic
from anthropic import BadRequestError as AnthropicBadRequestError
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


def generate_title(message: str):
    """
    入力された内容を要約してタイトルを生成する
    """

    content = TITLE_PROMPT.format(message=message)
    default_model = "gpt-4o-mini-2024-07-18"
    title, http_staus = chat_openai([{"role": "user", "content": content}], default_model)
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
        response = client.messages.create(model=model, temperature=0, messages=messages, max_tokens=1024)
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
