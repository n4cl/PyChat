import os

from chat import chat_anthropic, chat_openai, generate_title
from const import LLMProvider
from custom_exception import RequiredParameterError
from db import (
    DataType,
    MessageRole,
    delete_message,
    get_message,
    get_messages,
    get_model,
    insert_message,
    insert_message_details,
    select_message_details,
)
from db import (
    get_models as db_get_models,
)
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi_custom_route import ContextIncludedRoute
from request_type import ChatRequestBody
from response_type import (
    ErrorResponse,
    ResponseDeleteChat,
    ResponseGetChat,
    ResponseGetChatMessage,
    ResponseGetModels,
    ResponseHello,
    ResponsePostChat,
)

OPENAI_API_KEY = "OPENAI_API_KEY"
if OPENAI_API_KEY not in os.environ and not os.environ[OPENAI_API_KEY]:
    raise RequiredParameterError("OPENAI_API_KEY is required")


app = FastAPI()
app.router.route_class = ContextIncludedRoute


@app.get("/", response_model=ResponseHello)
def hello() -> dict[str, str]:
    return ResponseHello(message="Hello, world!")


@app.get("/chat", response_model=ResponseGetChat)
def get_chat(page_no: int = 1, page_size: int = 20) -> dict[str, list]:
    res = get_messages(page_no, page_size)
    return ResponseGetChat(
        history=res["history"],
        current_page=res["current_page"],
        next_page=res["next_page"],
        total_page=res["total_pages"],
    )


@app.get("/models", response_model=ResponseGetModels)
def get_models() -> dict[str, list]:
    models = db_get_models()
    return ResponseGetModels(models=models)


@app.get("/chat/{message_id}", response_model=ResponseGetChatMessage)
def get_chat_message(message_id: int) -> dict[str, list]:
    messages = select_message_details(message_id, required_column={"role", "message", "model", "create_date"})
    return ResponseGetChatMessage(messages=messages)


@app.delete(
    "/chat/{message_id}",
    response_model=ResponseDeleteChat,
    responses={status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}},
)
def delete_chat(message_id: int) -> dict[str, str]:
    if len(get_message(message_id)) == 0:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content=ErrorResponse(message="No message_id").dict()
        )

    delete_message(message_id)
    return ResponseDeleteChat(message="Succeeed to delete")


@app.post("/chat", response_model=ResponsePostChat, responses={status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse}})
def chat(chat_request_body: ChatRequestBody) -> dict[str, str]:
    mid = chat_request_body.message_id
    query = chat_request_body.query
    model_id = chat_request_body.model
    file = chat_request_body.file
    contents = {DataType.TEXT: query}

    # モデルの提供者が存在しない場合はエラー
    model_name, provider_id = get_model(model_id)
    if provider_id is None:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=ErrorResponse(message="Model not found"))
    else:
        try:
            provider = LLMProvider(provider_id)
        except ValueError:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=ErrorResponse(message="Invalid model"))

    if file:
        # TODO: file upload
        # contents[DataType.FILE] = file_path
        pass

    if not mid:
        title = generate_title(query)
        mid = insert_message(title)

    insert_message_details(mid, MessageRole.USER, None, contents)
    messages = select_message_details(mid, required_column={"role", "message"})

    if provider == LLMProvider.Anthropic:
        msg, http_status = chat_anthropic(messages, model_name)
    elif provider == LLMProvider.OpenAI:
        msg, http_status = chat_openai(messages, model_name)

    if http_status != status.HTTP_200_OK:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=ErrorResponse(message="Failed to chat").dict()
        )

    contentes = {DataType.TEXT: msg}
    insert_message_details(mid, MessageRole.ASSISTANT, model_name, contentes)

    return ResponsePostChat(message_id=mid, message=msg)
