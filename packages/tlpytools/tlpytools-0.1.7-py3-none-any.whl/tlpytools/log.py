import os
import logging
import platform
import datetime
import time
import contextlib
import numpy as np
import pandas as pd
import sqlalchemy as sql
import pyodbc


def setup_logger(name, log_file=None, level=logging.INFO, console_output=True):
    """
    Set up a logger with file and optionally console output.

    Args:
        name (str): Logger name
        log_file (str, optional): Path to log file
        level (int): Logging level (default: INFO)
        console_output (bool): Whether to output to console

    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    logger.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # File handler
    if log_file:
        # Create directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Log initial information
    logger.info("=== Logging initialized ===")
    logger.info(f"Time: {datetime.datetime.now()}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Platform: {platform.platform()}")

    # Log version information
    try:
        logger.info(f"numpy: {np.__version__}")
        logger.info(f"pandas: {pd.__version__}")
        logger.info(f"sqlalchemy: {sql.__version__}")
        logger.info(f"pyodbc: {pyodbc.version}")
    except Exception as e:
        logger.warning(f"Could not log version information: {e}")

    return logger


def log_with_context(logger, level, message, extra_data=None):
    """
    Log a message with additional context data.

    Args:
        logger (logging.Logger): Logger instance
        level (int): Logging level
        message (str): Log message
        extra_data (dict, optional): Additional context data
    """
    if extra_data:
        context_str = " | ".join([f"{k}={v}" for k, v in extra_data.items()])
        full_message = f"{message} | {context_str}"
    else:
        full_message = message

    logger.log(level, full_message)


@contextlib.contextmanager
def performance_timer(logger, operation_name):
    """
    Context manager for timing operations and logging performance.

    Args:
        logger (logging.Logger): Logger instance
        operation_name (str): Name of the operation being timed

    Usage:
        with performance_timer(logger, 'data_processing'):
            # ... your code here
    """
    start_time = time.time()
    logger.info(f"Starting {operation_name}")

    try:
        yield
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Completed {operation_name} in {duration:.2f} seconds")
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        logger.error(f"Failed {operation_name} after {duration:.2f} seconds: {e}")
        raise


def configure_pandas_logging():
    """
    Configure pandas to reduce noisy logging.
    """
    # Suppress pandas PerformanceWarning
    import warnings

    warnings.simplefilter(action="ignore", category=pd.errors.PerformanceWarning)

    # Set pandas options for better logging
    pd.set_option("mode.chained_assignment", None)


class logger:
    """Legacy logger class for backwards compatibility."""

    def __init__(self) -> None:
        self.log = None

    def init_logger(self, logFile=None, computer="run"):
        # if log file name is None, use source class name
        if logFile == None:
            filename = "{}.log".format(type(self).__name__)
            logFile = filename

        # get computer name
        name = "{}_{}".format(computer, platform.node())

        # try get log handler if it exists
        self.log = logging.getLogger(name)

        # if not, add log handler
        if len(self.log.handlers) == 0:
            # create logger
            self.log = logging.getLogger(name)
            self.log.setLevel(logging.DEBUG)
            # create formatter and add it to the handlers
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            # create file handler
            fh = logging.FileHandler(logFile)
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            self.log.addHandler(fh)
            # create console handler
            ch = logging.StreamHandler()
            # ch.setLevel(logging.ERROR)
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            self.log.addHandler(ch)

        # log message
        self.log.info("===Logging enabled===")
        self.log.info("Time - {}".format(datetime.datetime.now()))
        self.log.info("CWD - {d}".format(d=os.getcwd()))
        # print versions
        self.log.info("numpy " + np.__version__)
        self.log.info("pandas " + pd.__version__)
        self.log.info("sqlalchemy " + sql.__version__)
        self.log.info("pyodbc " + pyodbc.version)
        self.log.info("ipfn " + "1.4.0")


class analyzer:
    """not implemented: analyze performance of log by analyzing time points"""

    def __init__(self) -> None:
        self.log = None
