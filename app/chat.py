import openai
from openai import OpenAI
from fastapi import status


def chat_request(messages: list, model: str):
    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=messages
        )
    except openai.BadRequestError as e:
        return str(e), status.HTTP_400_BAD_REQUEST

    content = response.choices[0].message.content
    return content, status.HTTP_200_OK

def get_model_list() -> list:
    client = OpenAI()

    response = client.models.list()
    return response.data

if __name__ == "__main__":
    print(get_model_list())
