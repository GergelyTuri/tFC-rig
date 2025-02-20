"""This module provides logging setup and utility functions for logging messages at different levels.
Functions:
- setup_logging(log_file_name="app.log", log_dir="logs")
- log_info(message)
- log_error(message)
- log_warning(message)
"""

import logging
import os


def setup_logging(log_file_name="app.log", log_dir="logs"):
    """
    Setup logging configuration.

    Parameters:
    - log_file_name: str
        The name of the log file.
    - log_dir: str
        The directory to store the log file.
    """
    # Create the log directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file_path = os.path.join(log_dir, log_file_name)

    # Set up logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file_path), logging.StreamHandler()],
    )


def log_info(message):
    """
    Log an info level message.

    Parameters:
    - message: str
        The message to log.
    """
    logging.info(message)


def log_error(message):
    """
    Log an error level message.

    Parameters:
    - message: str
        The message to log.
    """
    logging.error(message)


def log_warning(message):
    """
    Log a warning level message.

    Parameters:
    - message: str
        The message to log.
    """
    logging.warning(message)
