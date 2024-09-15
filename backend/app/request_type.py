from pydantic import BaseModel, constr


class ChatRequestBody(BaseModel):
    message_id: int | None  # Memo: message_id is not required
    query: constr(min_length=1, strip_whitespace=True)  # 空文字を許可しない
    model: int
    file: str = None
