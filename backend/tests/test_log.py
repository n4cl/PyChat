import sys
from logging import DEBUG, StreamHandler

from log import get_logger


def test_get_logger():
    # ロガーの名前とレベルが正しく設定されていることを確認
    logger_name = "test_logger"
    logger = get_logger(logger_name)
    assert logger.name == logger_name
    assert logger.level == DEBUG

    # ロガーのハンドラが正しく設定されていることを確認
    assert len(logger.handlers) == 1
    handler = logger.handlers[0]
    assert isinstance(handler, StreamHandler)
    assert handler.level == DEBUG
    assert handler.stream == sys.stdout

