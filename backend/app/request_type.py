from typing import Annotated

from pydantic import BaseModel, StringConstraints


class RequestPostMessagesBody(BaseModel):
    title: str

class RequestPutMessagesBody(BaseModel):
    title: str

class RequestPostChatBody(BaseModel):
    query: Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
    llm_model_id: int  # プレフィックスに model を利用すると問題が発生する
    file: str = None

class RequestGenerateTitleBody(BaseModel):
    query: str
