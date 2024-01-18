from pydantic import BaseModel, Extra


class ResponseHello(BaseModel):
    """
    Get /のレスポンス
    """
    message: str = None
    class Config:
        # レスポンスに含まれるフィールドを制限する
        extra = Extra.forbid

class ResponseGetHistoryContent(BaseModel):
    """
    Get /historyのレスポンスのhistoryの要素のcontentの要素
    """
    message_id: int = None
    title: str = None
    class Config:
        extra = Extra.forbid

class ResponseGetHistory(BaseModel):
    """
    Get /historyのレスポンスのhistoryの要素
    """
    history: list[ResponseGetHistoryContent]
    class Config:
        extra = Extra.forbid

class ResponseGetChatMessage(BaseModel):
    """
    Get /chat/{message_id}のレスポンスのmessagesの要素
    """
    role: str = None
    content: str = None
    model: str = None
    class Config:
        extra = Extra.forbid

class ResponseGetChat(BaseModel):
    """
    Get /chat/{message_id}のレスポンス
    """
    messages: list[ResponseGetChatMessage] = None
    class Config:
        extra = Extra.forbid

class ResponseDeleteChat(BaseModel):
    """
    Delete /chat/{message_id}のレスポンス
    """
    message: str = None
    class Config:
        extra = Extra.forbid

class ResponsePostChat(BaseModel):
    """
    Post /chatのレスポンス
    """
    message_id: int = None
    message: str = None
    class Config:
        extra = Extra.forbid

class ErrorResponse(BaseModel):
    message: str = None
    class Config:
        extra = Extra.forbid