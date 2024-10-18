import datetime
import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from uuid import uuid4

from fastapi import Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from log import get_logger
from response_type import ErrorResponse

LOGGER = get_logger(__name__)


@dataclass
class LogField:
    """ログフィールド"""

    IO: str = "I/O"
    TIMESTAMP: str = "timestamp"
    REQUEST_ID: str = "request_id"
    STATUS_CODE: str = "status_code"
    ELAPSED_TIME: str = "elapsed_time"
    BODY: str = "body"
    ADDR: str = "addr"
    URI: str = "uri"
    METHOD: str = "method"
    ERROR: str = "error"


def generate_default_logfield(io: str) -> dict[str, str]:
    """I/Oの両方で利用するログフィールドを生成する"""
    return {
        LogField.IO: io,
        LogField.TIMESTAMP: datetime.datetime.fromtimestamp(time.time()).strftime("%Y/%m/%d %H:%M:%S%Z"),
    }


class ContextIncludedRoute(APIRoute):
    """カスタムルートクラス"""

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            """
            カスタムルートハンドラ
            """
            begin = time.time()
            input_field = generate_default_logfield("IN")
            request_id = str(uuid4())
            input_field[LogField.REQUEST_ID] = request_id

            if await request.body():
                try:
                    body = await request.json()
                    _show_body = body.copy()
                    if "file" in body:
                        file_content = body["file"]
                        if file_content:
                            _show_body["file"] = f"{file_content[:10]}... (truncated, total size: {len(file_content)})"
                    input_field[LogField.BODY] = _show_body

                except json.decoder.JSONDecodeError:
                    input_field[LogField.BODY] = (await request.body()).decode("utf-8")
            else:
                input_field[LogField.BODY] = None
            # input_field["headers"] = {k.decode("utf-8"): v.decode("utf-8") for (k, v) in request.headers.raw}
            input_field[LogField.ADDR] = request.client.host
            input_field[LogField.URI] = request.url.path
            input_field[LogField.METHOD] = request.method
            LOGGER.info(json.dumps(input_field, ensure_ascii=False))

            # レスポンスオブジェクトの取得
            try:
                response: Response = await original_route_handler(request)
            except RequestValidationError as err:
                response = JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST, content=ErrorResponse(message="Invalid parameter").dict()
                )
                error_field = generate_default_logfield("N/A")
                error_field[LogField.REQUEST_ID] = request_id
                error_field[LogField.ERROR] = err.errors()[0]
                LOGGER.error(json.dumps(error_field, ensure_ascii=False))
            output_field = generate_default_logfield("OUT")
            output_field[LogField.REQUEST_ID] = request_id
            output_field[LogField.STATUS_CODE] = response.status_code
            # output_field["headers"] = {k: v for (k, v) in response.headers.items()}
            output_field[LogField.BODY] = response.body.decode("utf-8")
            output_field[LogField.ELAPSED_TIME] = round(time.time() - begin, 2)
            LOGGER.info(json.dumps(output_field, ensure_ascii=False))

            return response

        # get_route_handlerは定義したカスタムルートハンドラを返却する
        return custom_route_handler
