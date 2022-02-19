import logging
import os
from config import config


def initialize_logging():
    params = config("logging")

    log_formatter = logging.Formatter(
        "%(asctime)s [%(threadName)-10.10s] [%(filename)-10.10s] [%(funcName)-15.15s]"
        "[l %(lineno)-4.4s] [%(levelname)-7.7s]\t%(message)s"
    )
    root_logger = logging.getLogger()

    try:
        file_handler = logging.FileHandler(f"{params['log_path']}/{params['log_filename']}.log")
    except FileNotFoundError:
        os.makedirs(f"{params['log_path']}")
        file_handler = logging.FileHandler(f"{params['log_path']}/{params['log_filename']}.log")

    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)

    root_logger.setLevel(getattr(logging, params["level"]))
