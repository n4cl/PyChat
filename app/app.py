import os
from pydantic import BaseModel
from fastapi import FastAPI, status, Response
from chat import chat_request
from db import insert_message, insert_message_details, select_message_details, MessageRole
from custom_exception import RequiredParameterError
from log import ContextIncludedRoute


OPENAI_API_KEY = "OPENAI_API_KEY"
if OPENAI_API_KEY not in os.environ and not os.environ[OPENAI_API_KEY]:
    raise RequiredParameterError("OPENAI_API_KEY is required")


class TestBody(BaseModel):
    message: str = None

class ChatRequestBody(BaseModel):
    message_id: int = None
    query: str
    model: str

app = FastAPI()
app.router.route_class = ContextIncludedRoute


@app.get("/")
def hello() -> dict[str, str]:
    return {"message": "Hello World"}

@app.post("/chat")
def chat(chat_request_body: ChatRequestBody, response: Response) -> dict[str, str]:
    mid = chat_request_body.message_id
    query = chat_request_body.query
    model = chat_request_body.model
    if not query:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "query is required"}
    if not model:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "model is required"}
    if not mid:
        mid = insert_message()

    insert_message_details(mid, MessageRole.USER, None, query)
    messages = select_message_details(mid)
    msg, http_status = chat_request(messages, model)

    response.status_code = http_status
    if http_status != status.HTTP_200_OK:
        return {"message": msg}

    insert_message_details(mid, MessageRole.ASSISTANT, model, msg)

    return {"message": msg, "message_id": mid}
