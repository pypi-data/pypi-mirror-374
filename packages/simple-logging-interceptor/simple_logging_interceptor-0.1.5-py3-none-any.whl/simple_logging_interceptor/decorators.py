import functools
import logging
import time
from datetime import datetime
from pathlib import Path

# Default log directory
DEFAULT_LOG_DIR = Path("./logs")
DEFAULT_LOG_DIR.mkdir(parents=True, exist_ok=True)

# Generate timestamped log file name
def _timestamped_log_file(log_dir: Path) -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return log_dir / f"interceptor_{timestamp}.log"

# Configure logger
logger = logging.getLogger("simple_logging_interceptor")
logger.setLevel(logging.INFO)

if not logger.handlers:
    log_file = _timestamped_log_file(DEFAULT_LOG_DIR)

    # File handler with timestamp
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        "%Y-%m-%d %H:%M:%S"
    ))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        "%Y-%m-%d %H:%M:%S"
    ))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def set_log_directory(log_dir: str):
    """Allow user to override the default log directory (creates a new timestamped log file)."""
    new_dir = Path(log_dir)
    new_dir.mkdir(parents=True, exist_ok=True)
    new_file = _timestamped_log_file(new_dir)

    # Remove old file handlers
    for handler in list(logger.handlers):
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)

    # Add new file handler with timestamp
    file_handler = logging.FileHandler(new_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        "%Y-%m-%d %H:%M:%S"
    ))
    logger.addHandler(file_handler)

    logger.info(f"Logging directory changed to: {new_dir}, file={new_file.name}")


def simple_logging_interceptor(func):
    """Decorator to log function calls, arguments, return values, and errors."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Calling: {func.__name__} with args={args}, kwargs={kwargs}")
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = (time.time() - start_time) * 1000
            logger.info(
                f"Returned from {func.__name__} -> {result} (took {elapsed:.4f} ms)"
            )
            return result
        except Exception as e:
            logger.exception(f"Exception in {func.__name__}: {e}")
            raise
    return wrapper
