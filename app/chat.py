import openai
from fastapi import status


def chat_request(message: str, model: str):
    try:
      response = openai.ChatCompletion.create(
        model=model,
        temperature=0,
        messages=[
          {"role": "user", "content": message}
        ]
      )
    except openai.error.InvalidRequestError as e:
        return str(e), status.HTTP_400_BAD_REQUEST

    content = response["choices"][0]["message"]["content"]
    return content, status.HTTP_200_OK
