# Copyright Hewlett Packard Enterprise Development LP

import logging
import os
from logging import Logger
from logging.handlers import RotatingFileHandler


def logger_exists(logger_name: str) -> bool:
    """
    Check if a logger with the given name already exists.

    Args:
        logger_name (str): Name of the logger to check.

    Returns:
        bool: True if the logger exists, False otherwise.
    """
    return logger_name in logging.Logger.manager.loggerDict


def get_logger(
    log_name: str = "di_sdk",
    log_path: str = ".",
    handler: str = "rotating_file_handler",
) -> Logger:
    """
    Get the logger for the given probe name

    Args:
        log_name (_type_): Name of the logger file
        level (str, optional): _description_. Defaults to "info".
        handler (str, optional): _description_. Defaults to "rotating_file_handler".
        log_path (_type_, optional): _description_. Artifact path for log file.

    Raises:
        Exception: _description_

    Returns:
        _type_: _description_
    """

    level = os.getenv("LOG_LEVEL", "INFO").upper()

    if logger_exists(log_name):
        logger = logging.getLogger(log_name)
        return logger

    logger = logging.getLogger(log_name)

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    # Logfile name
    file = log_path + "/" + log_name + ".log"

    format_string = "%(asctime)-15s %(process)d %(name)s %(levelname)s %(module)s %(funcName)s %(message)s"
    log_format = logging.Formatter(format_string)

    if handler == "file_handler":
        hdlr = logging.FileHandler(file)
        hdlr.setFormatter(log_format)
        logger.setLevel(level.upper())
        logger.addHandler(hdlr)

    # Current logic logs to both file and stream
    elif handler == "stream_handler":
        hdlr = logging.StreamHandler()  # type: ignore
        hdlr.setFormatter(log_format)
        logger.setLevel(level.upper())
        logger.addHandler(hdlr)

        file_hdlr = logging.FileHandler(file)
        logger.addHandler(file_hdlr)

    elif handler == "rotating_file_handler":
        hdlr = RotatingFileHandler(file, maxBytes=200000, backupCount=10)
        hdlr.setFormatter(log_format)
        logger.setLevel(level.upper())
        logger.addHandler(hdlr)

    else:
        raise Exception(
            "Incorrect 'handler' provided: correct options - 'file_handler' or 'stream_handler' or 'rotating_file_handler'"
        )

    return logger
