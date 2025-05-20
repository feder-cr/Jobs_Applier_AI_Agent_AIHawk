import logging.handlers
import os
import sys
import logging
from loguru import logger
from selenium.webdriver.remote.remote_connection import LOGGER as selenium_logger

from config import LOG_LEVEL, LOG_SELENIUM_LEVEL, LOG_TO_CONSOLE, LOG_TO_FILE


def remove_default_loggers():
    """Remove default loggers from root logger."""
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    if os.path.exists("log/app.log"):
        os.remove("log/app.log")

def init_loguru_logger() -> None:
    """Initialize and configure loguru logger."""

    def get_log_filename():
        return f"log/app.log"

    log_file = get_log_filename()
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    except OSError as e:
        print(f"Failed to create log directory {os.path.dirname(log_file)}: {e}")
        raise

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


def init_selenium_logger():
    """Initialize and configure selenium logger to write to selenium.log."""
    log_file = "log/selenium.log"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    selenium_logger.handlers.clear()
    selenium_logger.setLevel(LOG_SELENIUM_LEVEL)

    # Create file handler for selenium logger
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_file, when="D", interval=1, backupCount=5
    )
    file_handler.setLevel(LOG_SELENIUM_LEVEL)

    # Define a simplified format for selenium logger entries
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    # Add the file handler to selenium_logger
    selenium_logger.addHandler(file_handler)


remove_default_loggers()
init_loguru_logger()
init_selenium_logger()
