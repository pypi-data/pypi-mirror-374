import os
import sys
import logging

from typing import Literal

cols = {
    "reset": "\033[0m",
    "white": "\033[2;39m",  # time
    "bold_green": "\033[1;32m",  # debug
    "green": "\033[0;32m",  # debug msg
    "bold_blue": "\033[1;34m",  # info
    "blue": "\033[0;34m",  # info msg
    "bold_yellow": "\033[1;33m",  # warning
    "yellow": "\033[0;33m",  # warning msg
    "bold_red": "\033[1;31m",  # error
    "red": "\033[0;31m",  # error msg
    "red_back": "\033[7;31m",  # critical
    "critic_red": "\033[1;91m",  # critical msg
    "error_msg": "\033[0;91m",
}

def colour(text: str, colour: Literal['reset', 'white', 'bold_green', 'green', 
                                      'bold_blue', 'blue', 'bold_yellow', 'yellow', 
                                      'bold_red', 'red', 'red_back', 'critic_red', 'error_msg']) -> str:
    """Applies ANSI escape codes for text colouring in the console.

    Args:
        text (str): The text to be coloured.
        colour (Literal): The desired colour for the text, chosen from a predefined set of colour names.

    Returns:
        str: The input text wrapped with ANSI escape codes for the specified colour and a reset code.
    """

    return f"{cols[colour]}{text}{cols["reset"]}"


class CustomFormatter(logging.Formatter):
    """A custom formatter that adds colors to console output."""
    def __init__(self, datefmt='%Y-%m-%d %H:%M:%S'):
        super().__init__(datefmt=datefmt)
        self.FORMATS = {
            logging.DEBUG: f"{cols['white']}%(asctime)s{cols['reset']} | {cols['bold_green']}%(levelname)s{cols['reset']} | {cols['green']}%(message)s{cols['reset']}",
            logging.INFO: f"{cols['white']}%(asctime)s{cols['reset']} | {cols['bold_blue']}%(levelname)s{cols['reset']} | {cols['blue']}%(message)s{cols['reset']}",
            logging.WARNING: f"{cols['white']}%(asctime)s{cols['reset']} | {cols['bold_yellow']}%(levelname)s{cols['reset']} | {cols['yellow']}%(message)s{cols['reset']}",
            logging.ERROR: f"{cols['white']}%(asctime)s{cols['reset']} | {cols['bold_red']}%(levelname)s{cols['reset']} | {cols['red']}%(message)s{cols['error_msg']}",
            logging.CRITICAL: f"{cols['white']}%(asctime)s{cols['reset']} | {cols['red_back']}%(levelname)s{cols['reset']} | {cols['critic_red']}%(message)s{cols['reset']}",
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt=self.datefmt)
        return formatter.format(record)


class CustomFileFormatter(logging.Formatter):
    """A custom formatter for file logs that handles multiline messages."""
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            style='%'
        )

    def format(self, record):
        if '\n' in record.msg:
            record.msg = record.msg.replace('\n', '\n\t\t| ')
        return super().format(record)


class MaxLevelFilter(logging.Filter):
    """Filters log records allowing only those with level <= max_level."""
    def __init__(self, max_level):
        super().__init__()
        self.max_level = max_level

    def filter(self, record):
        return record.levelno <= self.max_level


def log_exception(exception: Exception) -> str:
    """Generates a concise log message for a caught exception."""
    return f"{str(exception.__traceback__.tb_lineno)} | {colour(type(exception).__name__, "bold_red")} | {colour(str(exception), "yellow")}"    # type: ignore

def setup_logger(log_dir: str) -> logging.Logger:
    """ Configures a custom logger with an outputdir from the user """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger("negogv_log")
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        logger.handlers.clear()

    error_log_path = os.path.join(log_dir, "high_lvl.log")
    file_handler_error = logging.FileHandler(error_log_path)
    file_handler_error.setLevel(logging.WARNING)
    file_handler_error.setFormatter(CustomFileFormatter())

    app_log_path = os.path.join(log_dir, "low_lvl.log")
    file_handler_app = logging.FileHandler(app_log_path)
    file_handler_app.setLevel(logging.DEBUG)
    file_handler_app.addFilter(MaxLevelFilter(logging.INFO))
    file_handler_app.setFormatter(CustomFileFormatter())

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(CustomFormatter())

    logger.addHandler(file_handler_error)
    logger.addHandler(file_handler_app)
    logger.addHandler(stdout_handler)

    return logger