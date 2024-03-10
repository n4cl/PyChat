from pydantic import BaseModel, ConfigDict


class ResponseHello(BaseModel):
    """
    Get /のレスポンス
    """
    message: str = None
    model_config = ConfigDict(extra="forbid") # レスポンスに含まれるフィールドを制限する

class ResponseGetHistoryContent(BaseModel):
    """
    Get /historyのレスポンスのhistoryの要素のcontentの要素
    """
    message_id: int
    title: str
    model_config = ConfigDict(extra="forbid")

class ResponseGetHistory(BaseModel):
    """
    Get /historyのレスポンスのhistoryの要素
    """
    history: list[ResponseGetHistoryContent]
    current_page: int
    next_page: int = None
    total_page: int
    model_config = ConfigDict(extra="forbid")

class ResponseGetModel(BaseModel):
    """
    Get /modelsのレスポンスのmodelsの要素
    """
    id: int
    name: str
    is_file_attached: bool
    model_config = ConfigDict(extra="forbid")


class ResponseGetModels(BaseModel):
    """
    Get /modelsのレスポンス
    """
    models: list[ResponseGetModel]
    model_config = ConfigDict(extra="forbid")

class ResponseGetChatMessage(BaseModel):
    """
    Get /chat/{message_id}のレスポンスのmessagesの要素
    """
    role: str
    content: str
    model: str | None = None
    model_config = ConfigDict(extra="forbid")

class ResponseGetChat(BaseModel):
    """
    Get /chat/{message_id}のレスポンス
    """
    messages: list[ResponseGetChatMessage] = None
    model_config = ConfigDict(extra="forbid")

class ResponseDeleteChat(BaseModel):
    """
    Delete /chat/{message_id}のレスポンス
    """
    message: str = None
    model_config = ConfigDict(extra="forbid")

class ResponsePostChat(BaseModel):
    """
    Post /chatのレスポンス
    """
    message_id: int = None
    message: str = None
    model_config = ConfigDict(extra="forbid")

class ErrorResponse(BaseModel):
    message: str = None
    model_config = ConfigDict(extra="forbid")
