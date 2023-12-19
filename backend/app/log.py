import sys
from logging import DEBUG, StreamHandler, getLogger


def get_logger(name) -> getLogger:
    logger = getLogger(name)
    handler = StreamHandler(sys.stdout)
    handler.setLevel(DEBUG)
    logger.addHandler(handler)
    logger.setLevel(DEBUG)
    return logger
