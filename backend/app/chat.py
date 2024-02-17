from fastapi import status
from fastapi_custom_route import LOGGER
from openai import BadRequestError, OpenAI


def generate_title(message: str):

    prompt = ("入力された内容を要約してタイトルを生成してください。\n"
              "また生成場合は出力フォーマットにしたがってください。\n\n"
              "## 出力フォーマット\n"
              "文字列\n\n"
              "## 出力例\n"
              "これはタイトル！\n\n"
              "## 入力された内容\n"
              "{message}\n\n"
              "## タイトル\n")
    content = prompt.format(message=message)
    default_model = "gpt-3.5-turbo"
    title, _ = chat_request([{"role": "user", "content": content}], default_model)
    return title


def chat_request(messages: list, model: str):
    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=messages
        )
    except BadRequestError as e:
        LOGGER.error(e)
        return "", e.status_code

    content = response.choices[0].message.content
    return content, status.HTTP_200_OK

def get_model_list() -> list:
    client = OpenAI()

    response = client.models.list()
    return response.data

if __name__ == "__main__":
    print(get_model_list())
