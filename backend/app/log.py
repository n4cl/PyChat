import sys
from logging import DEBUG, Logger, StreamHandler, getLogger


def get_logger(name) -> Logger:
    logger = getLogger(name)
    handler = StreamHandler(sys.stdout)
    handler.setLevel(DEBUG)
    logger.addHandler(handler)
    logger.setLevel(DEBUG)
    return logger
