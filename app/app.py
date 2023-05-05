import os
from pydantic import BaseModel
from fastapi import FastAPI, status, Response
from chat import chat_request

class RequiredParameterError(Exception):
    pass

OPENAI_API_KEY = "OPENAI_API_KEY"
if OPENAI_API_KEY not in os.environ:
    raise RequiredParameterError("{} is required".format(OPENAI_API_KEY))


class ChatRequestBody(BaseModel):
    query: str
    model: str

app = FastAPI()

@app.get("/")
async def hello() -> dict[str, str]:
    return {"message": "Hello World"}


@app.post("/chat")
async def chat(chat_request_body: ChatRequestBody, response: Response) -> dict[str, str]:
    query = chat_request_body.query
    model = chat_request_body.model
    if not query:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "query is required"}
    if not model:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "model is required"}
    msg, http_status = chat_request(query, model)
    response.status_code = http_status
    return {"message": msg}
