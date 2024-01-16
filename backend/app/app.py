import os

from chat import chat_request, generate_title
from custom_exception import RequiredParameterError
from db import (
    DataType,
    MessageRole,
    delete_message,
    get_message,
    insert_message,
    insert_message_details,
    select_message_details,
)
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi_custom_route import ContextIncludedRoute
from pydantic import BaseModel
from response_type import (
    ErrorResponse,
    ResponseDeleteChat,
    ResponseGetChat,
    ResponseGetHistory,
    ResponseHello,
    ResponsePostChat,
)

OPENAI_API_KEY = "OPENAI_API_KEY"
if OPENAI_API_KEY not in os.environ and not os.environ[OPENAI_API_KEY]:
    raise RequiredParameterError("OPENAI_API_KEY is required")


class ChatRequestBody(BaseModel):
    message_id: int = None # Memo: message_id is not required
    query: str
    model: str
    file: str = None

app = FastAPI()
app.router.route_class = ContextIncludedRoute


@app.get("/", response_model=ResponseHello)
def hello() -> dict[str, str]:
    return {"message": "Hello World"}

@app.get("/history", response_model=ResponseGetHistory)
def history() -> dict[str, list]:
    res = get_message()
    return {"history": res}

@app.get("/chat/{message_id}", response_model=ResponseGetChat)
def get_chat(message_id: int) -> dict[str, list]:
    messages = select_message_details(message_id, required_column={"role", "message", "model"})
    return {"messages": messages}

@app.delete("/chat/{message_id}",
            response_model=ResponseDeleteChat,
            responses={status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}})
def delete_chat(message_id: int) -> dict[str, str]:

    if len(get_message(message_id)) == 0:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "No message_id"})

    delete_message(message_id)
    return {"message": "Succeeed to delete"}

@app.post("/chat", response_model=ResponsePostChat,
          responses={status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse}})
def chat(chat_request_body: ChatRequestBody) -> dict[str, str]:
    mid = chat_request_body.message_id
    query = chat_request_body.query
    model = chat_request_body.model
    file = chat_request_body.file
    contents = {DataType.TEXT: query}
    if not query:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "query is required"})
    if not model:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "model is required"})
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
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Failed to chat"})

    contentes = {DataType.TEXT: msg}
    insert_message_details(mid, MessageRole.ASSISTANT, model, contentes)

    return {"message": msg, "message_id": mid}
