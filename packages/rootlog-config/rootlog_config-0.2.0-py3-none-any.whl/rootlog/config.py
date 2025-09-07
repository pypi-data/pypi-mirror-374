import datetime
import logging
import os
import queue
import re
from logging.handlers import (
    QueueHandler,
    QueueListener,
    RotatingFileHandler,
    TimedRotatingFileHandler,
)
from pathlib import Path
from typing import Optional, Union

import colorlog


# todo: replace os.path.join with pathlib.Path
def remove_all_loggers():
    """Remove all handlers and set INFO level for all existing loggers.
    This is CRUCIAL for ensuring consistent logging behavior across the application.
    """
    # Clean root logger handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.root.setLevel(logging.INFO)
    # Clean all other loggers
    for name, logger in logging.root.manager.loggerDict.items():
        if hasattr(logger, "handlers"):
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
            logger.setLevel(logging.INFO)


def _parse_rotation(rotation: Union[str, int]) -> dict:
    """Parse rotation parameter and return handler configuration."""
    if isinstance(rotation, int):
        # Size-based rotation in bytes
        return {"type": "size", "maxBytes": rotation, "backupCount": 5}

    if isinstance(rotation, str):
        # Time-based rotation patterns like "12:00", "1 week", "500 MB"
        rotation = rotation.strip().lower()

        # Size patterns: "500 MB", "1 GB", etc. (must have explicit unit for size)
        size_match = re.match(r"(\d+(?:\.\d+)?)\s*(mb|gb|kb|b)$", rotation)
        if size_match:
            size, unit = size_match.groups()
            size = float(size)

            multipliers = {"b": 1, "kb": 1024, "mb": 1024**2, "gb": 1024**3}
            bytes_size = int(size * multipliers[unit])
            return {"type": "size", "maxBytes": bytes_size, "backupCount": 5}

        # Time patterns: "12:00", "00:00", "1 week", "1 day", etc.
        time_patterns = {
            r"(\d{1,2}):(\d{2})": "time",  # "12:00"
            r"(\d+)\s*day(s)?": "D",  # "1 day", "7 days"
            r"(\d+)\s*week(s)?": "W0",  # "1 week", "2 weeks"
            r"(\d+)\s*hour(s)?": "H",  # "1 hour", "24 hours"
        }

        for pattern, when in time_patterns.items():
            match = re.match(pattern, rotation)
            if match:
                if when == "time":
                    # Daily rotation at specific time
                    return {
                        "type": "time",
                        "when": "midnight",
                        "interval": 1,
                        "backupCount": 7,
                    }
                elif when in ["D", "W0", "H"]:
                    interval = int(match.group(1))
                    return {
                        "type": "time",
                        "when": when,
                        "interval": interval,
                        "backupCount": 7,
                    }

        # Default daily rotation for unrecognized patterns
        return {"type": "time", "when": "midnight", "interval": 1, "backupCount": 7}

    # Default to size-based rotation
    return {"type": "size", "maxBytes": 1_000_000, "backupCount": 5}


def _create_file_handler(
    log_dir: Path,
    is_testing: bool,
    rotation: Optional[Union[str, int]],
    level_f: int,
    format_f: str,
):
    """Create appropriate file handler based on rotation configuration."""
    base_name = "testing" if is_testing else datetime.datetime.now().strftime("%Y%m%d-%H")

    if rotation is None:
        # Default hourly rotation (existing behavior)
        log_file_name = f"{base_name}.log"
        file_handler = RotatingFileHandler(
            log_dir / log_file_name,
            maxBytes=1_000_000,
            backupCount=5,
        )
    else:
        config = _parse_rotation(rotation)

        if config["type"] == "size":
            log_file_name = f"{base_name}.log"
            file_handler = RotatingFileHandler(
                log_dir / log_file_name,
                maxBytes=config["maxBytes"],
                backupCount=config["backupCount"],
            )
        elif config["type"] == "time":
            log_file_name = f"{base_name}.log"
            file_handler = TimedRotatingFileHandler(
                log_dir / log_file_name,
                when=config["when"],
                interval=config["interval"],
                backupCount=config["backupCount"],
            )
        else:
            # Fallback to default
            log_file_name = f"{base_name}.log"
            file_handler = RotatingFileHandler(
                log_dir / log_file_name,
                maxBytes=1_000_000,
                backupCount=5,
            )

    file_handler.setLevel(level_f)
    file_handler.setFormatter(logging.Formatter(format_f))
    return file_handler


def check_registered_loggers():
    # Check all registered loggers and their levels
    logging.info("Root logger level: %s", logging.getLogger().getEffectiveLevel())
    logging.info("Checking all registered loggers:")
    for name in logging.root.manager.loggerDict:
        logging.info(f"{name}: {logging.getLogger(name).getEffectiveLevel()}")


def rootlog_config(
    script: str = None,
    app: str = None,
    logger_name: str = None,
    level_c: int = logging.INFO,
    level_f: int = logging.DEBUG,
    format_c: str = "%(levelname)s %(filename)s:%(lineno)d:%(funcName)s %(message)s",
    format_f: str = "%(levelname)s %(filename)s:%(lineno)d:%(funcName)s %(message)s",
    log_c: bool = True,
    log_f: bool = True,
    rotation: Optional[Union[str, int]] = None,
    use_queue: bool = False,
) -> Optional[logging.Logger]:
    # The env is set to "true" in the pytest fixture for testing purposes
    #
    # @pytest.fixture(autouse=True, scope="session")
    # def setup_testing_env():
    #     os.environ["TESTING"] = "true"
    #     yield
    #     os.environ.pop("TESTING", None)
    is_testing = (os.getenv("TESTING", "false").lower() == "true",)
    remove_all_loggers()  # Remove any existing handlers from ALL loggers
    if logger_name:
        logger = logging.getLogger(logger_name)  # Get specific logger only if logger name is provided (don't use module name __name__ or other names)
    else:
        logger = logging.getLogger()  # Get root logger if no logger name is provided
    logger.setLevel(min(level_c, level_f))
    if logger.hasHandlers():
        logger.handlers.clear()  # Prevent duplicate logs
    # Set up handlers list for potential queue listener
    handlers = []

    if log_c:
        console_handler = colorlog.StreamHandler()
        console_formatter = colorlog.ColoredFormatter(
            f"%(log_color)s{format_c}",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(level_c)
        handlers.append(console_handler)

        if not use_queue:
            logger.addHandler(console_handler)

    if log_f:
        try:
            # Create log directory if it doesn't exist
            log_base = Path(script).stem if script else app or "default"
            py_log_path = Path(os.getenv("PY_LOG_PATH", Path.home() / "python-log"))
            log_dir = py_log_path / log_base
            log_dir.mkdir(parents=True, exist_ok=True)

            # Determine file handler type based on rotation parameter
            file_handler = _create_file_handler(log_dir, is_testing, rotation, level_f, format_f)
            handlers.append(file_handler)

            if not use_queue:
                logger.addHandler(file_handler)

        except (OSError, PermissionError) as e:
            # Graceful fallback: continue with console logging only
            if log_c:
                logging.warning(f"Failed to set up file logging: {e}. Continuing with console logging only.")
            else:
                # If both file and console logging fail, set up basic console as fallback
                basic_handler = logging.StreamHandler()
                basic_handler.setFormatter(logging.Formatter(format_c))
                basic_handler.setLevel(level_c)
                logger.addHandler(basic_handler)
                logging.warning(f"Failed to set up file logging: {e}. Falling back to basic console logging.")

    # Set up queue-based logging if requested
    if use_queue and handlers:
        log_queue = queue.Queue()
        queue_handler = QueueHandler(log_queue)
        logger.addHandler(queue_handler)

        # Start queue listener in a separate thread
        listener = QueueListener(log_queue, *handlers, respect_handler_level=True)
        listener.start()

        # Store listener reference to prevent garbage collection
        if not hasattr(logger, "_queue_listeners"):
            logger._queue_listeners = []
        logger._queue_listeners.append(listener)
    if logger_name:
        return logger
    else:
        return None
