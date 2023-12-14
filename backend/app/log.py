import sys
import json
import time
import datetime
from typing import Callable
from logging import getLogger, StreamHandler, DEBUG
from uuid import uuid4

from fastapi import Request, Response
from fastapi.routing import APIRoute


logger = getLogger(__name__)
handler = StreamHandler(sys.stdout)
handler.setLevel(DEBUG)
logger.addHandler(handler)
logger.setLevel(DEBUG)


class ContextIncludedRoute(APIRoute):
    """カスタムルートクラス"""

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            """
            カスタムルートハンドラ
            """
            begin = time.time()
            input_field = {}
            request_id = str(uuid4())
            input_field["I/O"] = "IN"
            input_field["timestamp"] = datetime.datetime.fromtimestamp(begin).strftime("%Y/%m/%d %H:%M:%S%Z")
            input_field["request_id"] = request_id

            if await request.body():
                try:
                    input_field["body"] = await request.json()
                except json.decoder.JSONDecodeError:
                    input_field["body"] = (await request.body()).decode("utf-8")
            else:
                input_field["body"] = None
            # input_field["headers"] = {k.decode("utf-8"): v.decode("utf-8") for (k, v) in request.headers.raw}
            input_field["addr"] = request.client.host
            input_field["uri"] = request.url.path
            input_field["method"] = request.method
            logger.info(json.dumps(input_field, ensure_ascii=False))

            # レスポンスオブジェクトの取得
            response: Response = await original_route_handler(request)
            output_field = {}
            output_field["I/O"] = "OUT"
            output_field["timestamp"] = datetime.datetime.fromtimestamp(time.time()).strftime("%Y/%m/%d %H:%M:%S%Z")
            output_field["request_id"] = request_id
            output_field["status_code"] = response.status_code
            # output_field["headers"] = {k: v for (k, v) in response.headers.items()}
            output_field["body"] = response.body.decode("utf-8")
            output_field["elapsed_time"] = round(time.time() - begin, 2)
            logger.info(json.dumps(output_field, ensure_ascii=False))

            return response

        # get_route_handlerは定義したカスタムルートハンドラを返却する
        return custom_route_handler
