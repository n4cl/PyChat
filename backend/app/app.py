import datetime
import os

from chat import chat_anthropic, chat_openai, generate_title
from const import LLMProvider
from custom_exception import RequiredParameterError
from db import (
    DataType,
    MessageRole,
    delete_message,
    get_message,
    get_model,
    insert_message,
    insert_message_details,
    select_message_details,
    update_message,
)
from db import (
    get_messages as get_messages_from_db,
)
from db import (
    get_models as get_models_from_db,
)
from fastapi import FastAPI, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_custom_route import ContextIncludedRoute
from request_type import RequestGenerateTitleBody, RequestPostChatBody, RequestPostMessagesBody, RequestPutMessagesBody
from response_type import (
    ErrorResponse,
    ResponseDeleteChat,
    ResponseGetChat,
    ResponseGetChatMessage,
    ResponseGetModels,
    ResponseHello,
    ResponsePostChat,
    ResponsePostGenerateTitle,
    ResponsePostMessage,
)

OPENAI_API_KEY = "OPENAI_API_KEY"
if OPENAI_API_KEY not in os.environ and not os.environ[OPENAI_API_KEY]:
    raise RequiredParameterError("OPENAI_API_KEY is required")


app = FastAPI()
app.router.route_class = ContextIncludedRoute


@app.get("/", response_model=ResponseHello)
def healt_check() -> dict[str, str]:
    return ResponseHello(message="Hello, world!")


@app.get("/messages", response_model=ResponseGetChat)
def get_messages(page_no: int = 1, page_size: int = 20) -> dict[str, list]:
    res = get_messages_from_db(page_no, page_size)
    return ResponseGetChat(
        history=res["history"],
        current_page=res["current_page"],
        next_page=res["next_page"],
        total_page=res["total_pages"],
    )


@app.get("/models", response_model=ResponseGetModels)
def get_models() -> dict[str, list]:
    models = get_models_from_db()
    return ResponseGetModels(models=models)


@app.get("/messages/{message_id}",
         response_model=ResponseGetChatMessage,
         responses={status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}})
def get_messages_details(message_id: int) -> dict[str, list]:

    if not get_message(message_id):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content=jsonable_encoder(ErrorResponse(message="No message_id"))
        )
    messages = select_message_details(message_id, required_column={"role", "message", "model", "create_date"})

    return ResponseGetChatMessage(messages=messages)


@app.delete(
    "/messages/{message_id}",
    response_model=ResponseDeleteChat,
    responses={status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}},
)
def delete_messages(message_id: int) -> dict[str, str]:
    if len(get_message(message_id)) == 0:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content=jsonable_encoder(ErrorResponse(message="No message_id"))
        )

    delete_message(message_id)
    return ResponseDeleteChat(message="Succeeed to delete")


@app.post(
    "/messages",
    response_model=ResponsePostMessage,
    responses={status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse}})
def post_messages(request_body: RequestPostMessagesBody) -> dict[str, str]:
    title = request_body.title
    if title.strip() == "":
        draft_title = f"No title {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:')}"
    else:
        draft_title = title.split("\n")[0][:255]
    message_id = insert_message(draft_title)
    return ResponsePostMessage(message_id=message_id)

@app.put("/messages/{message_id}",
         responses={status.HTTP_204_NO_CONTENT: {"model": None},
                    status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse}})
def put_messages(message_id: int, request_body: RequestPutMessagesBody) -> dict[str, str]:
    title = request_body.title
    if title.strip() == "":
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content=jsonable_encoder(ErrorResponse(message="Title is required")))
    update_message(message_id, title)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.post("/messages/{message_id}/chat",
          response_model=ResponsePostChat,
          responses={status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
                     status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse}})
def post_messages_resouce_chat(message_id: int, request_body: RequestPostChatBody) -> dict[str, str]:
    model_id = request_body.llm_model_id
    query = request_body.query
    # TODO: file upload

    # モデルの提供者が存在しない場合はエラー
    model_name, provider_id = get_model(model_id)
    if provider_id is None:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content=jsonable_encoder(ErrorResponse(message="Model not found")))
    else:
        try:
            provider = LLMProvider(provider_id)
        except ValueError:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                content=jsonable_encoder(ErrorResponse(message="Invalid model")))

    messages = select_message_details(message_id, required_column={"role", "message"})
    messages.append({"role": "user", "content": query})

    query = query.strip()
    if provider == LLMProvider.Anthropic:
        msg, http_status = chat_anthropic(messages, model_name)
    elif provider == LLMProvider.OpenAI:
        msg, http_status = chat_openai(messages, model_name)

    if http_status != status.HTTP_200_OK:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content=jsonable_encoder(ErrorResponse(message="Failed to chat")))
    user_query = {DataType.TEXT: query}
    llm_response = {DataType.TEXT: msg}
    insert_message_details(message_id, MessageRole.USER, None, user_query)
    insert_message_details(message_id, MessageRole.ASSISTANT, model_name, llm_response)

    return ResponsePostChat(message=msg)


@app.post("/generate/title",
          response_model=ResponsePostGenerateTitle,
          responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse}})
def generate_title_api(request_body: RequestGenerateTitleBody) -> dict[str, str]:
    body = request_body.query
    body = body.strip()
    if not body:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content=jsonable_encoder(ErrorResponse(message="query is required")))
    title = generate_title(body)
    if not title:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content=jsonable_encoder(ErrorResponse(message="Failed to generate title")))
    return ResponsePostGenerateTitle(title=title)
