import logging.handlers
import os
import sys
import logging
from loguru import logger

from config import LOG_LEVEL, LOG_TO_CONSOLE, LOG_TO_FILE


def remove_default_loggers():
    """Remove default loggers from root logger."""
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    if os.path.exists("log/app.log"):
        os.remove("log/app.log")

def init_loguru_logger():
    """Initialize and configure loguru logger."""

    def get_log_filename():
        return f"log/app.log"

    log_file = get_log_filename()

    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger.remove()

    # Add file logger if LOG_TO_FILE is True
    if LOG_TO_FILE:
        logger.add(
            log_file,
            level=LOG_LEVEL,
            rotation="10 MB",
            retention="1 week",
            compression="zip",
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            backtrace=True,
            diagnose=True,
        )

    # Add console logger if LOG_TO_CONSOLE is True
    if LOG_TO_CONSOLE:
        logger.add(
            sys.stderr,
            level=LOG_LEVEL,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            backtrace=True,
            diagnose=True,
        )


remove_default_loggers()
init_loguru_logger()
