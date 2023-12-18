import sys
from logging import getLogger, StreamHandler, DEBUG


def get_logger(name) -> getLogger:
    logger = getLogger(name)
    handler = StreamHandler(sys.stdout)
    handler.setLevel(DEBUG)
    logger.addHandler(handler)
    logger.setLevel(DEBUG)
    return logger
