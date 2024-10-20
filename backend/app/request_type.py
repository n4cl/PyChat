from pydantic import BaseModel


class RequestPostMessagesBody(BaseModel):
    title: str

class RequestPutMessagesBody(BaseModel):
    title: str

class RequestPostChatBody(BaseModel):
    query: str = None
    llm_model_id: int  # プレフィックスに model を利用すると問題が発生する
    file: str = None
    file_name: str = None

class RequestGenerateTitleBody(BaseModel):
    query: str
