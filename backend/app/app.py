import os

from chat import chat_request, generate_title
from custom_exception import RequiredParameterError
from db import DataType, MessageRole, get_message, insert_message, insert_message_details, select_message_details
from fastapi import FastAPI, Response, status
from fastapi_custom_route import ContextIncludedRoute
from pydantic import BaseModel

OPENAI_API_KEY = "OPENAI_API_KEY"
if OPENAI_API_KEY not in os.environ and not os.environ[OPENAI_API_KEY]:
    raise RequiredParameterError("OPENAI_API_KEY is required")


class TestBody(BaseModel):
    message: str = None

class ChatRequestBody(BaseModel):
    message_id: int = None # Memo: message_id is not required
    query: str
    model: str
    file: str = None

app = FastAPI()
app.router.route_class = ContextIncludedRoute


@app.get("/")
def hello() -> dict[str, str]:
    return {"message": "Hello World"}

@app.get("/history")
def history() -> dict[str, list]:
    res = get_message()
    return {"history": res}

@app.get("/chat/{message_id}")
def get_chat(message_id: int) -> dict[str, list]:
    messages = select_message_details(message_id, required_column={"role", "message", "model"})
    return {"messages": messages}

@app.post("/chat")
def chat(chat_request_body: ChatRequestBody, response: Response) -> dict[str, str]:
    mid = chat_request_body.message_id
    query = chat_request_body.query
    model = chat_request_body.model
    file = chat_request_body.file
    contents = {DataType.TEXT: query}
    if not query:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "query is required"}
    if not model:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "model is required"}
    if file:
        # TODO: file upload
        # contents[DataType.FILE] = file_path
        pass

    if not mid:
        title = generate_title(query)
        mid = insert_message(title)

    insert_message_details(mid, MessageRole.USER, None, contents)
    messages = select_message_details(mid, required_column={"role", "message"})
    msg, http_status = chat_request(messages, model)

    if http_status != status.HTTP_200_OK:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Failed to chat"}

    contentes = {DataType.TEXT: msg}
    insert_message_details(mid, MessageRole.ASSISTANT, model, contentes)

    return {"message": msg, "message_id": mid}
