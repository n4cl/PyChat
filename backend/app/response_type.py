from pydantic import BaseModel, ConfigDict


class ResponseHello(BaseModel):
    """
    Get /のレスポンス
    """

    message: str = None
    model_config = ConfigDict(extra="forbid")  # レスポンスに含まれるフィールドを制限する


class ResponseGetChatContent(BaseModel):
    """
    Get /historyのレスポンスのhistoryの要素のcontentの要素
    """

    message_id: int
    title: str
    model_config = ConfigDict(extra="forbid")


class ResponseGetChat(BaseModel):
    """
    Get /historyのレスポンスのhistoryの要素
    """

    history: list[ResponseGetChatContent]
    current_page: int
    next_page: int | None = None
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


class ResponseGetChatMessageDetail(BaseModel):
    """
    Get /message/{message_id}のレスポンスのmessagesの要素
    """

    role: str
    content: str
    model: str | None = None
    create_date: str
    model_config = ConfigDict(extra="forbid")


class ResponseGetChatMessage(BaseModel):
    """
    Get /message/{message_id}のレスポンス
    """

    messages: list[ResponseGetChatMessageDetail]
    model_config = ConfigDict(extra="forbid")


class ResponseDeleteChat(BaseModel):
    """
    Delete /message/{message_id}のレスポンス
    """

    message: str = None
    model_config = ConfigDict(extra="forbid")


class ResponsePostChat(BaseModel):
    """
    Post /message/{message_id}/chatのレスポンス
    """

    message: str = None
    model_config = ConfigDict(extra="forbid")


class ResponsePostMessage(BaseModel):
    """
    Post /messagesのレスポンス
    """

    message_id: int
    model_config = ConfigDict(extra="forbid")


class ErrorResponse(BaseModel):
    message: str = None
    model_config = ConfigDict(extra="forbid")
