import functools
import logging
import time

# Setup default logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def simple_logging_interceptor(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Calling: {func.__name__} with args={args}, kwargs={kwargs}")
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"Returned from {func.__name__} -> {result} (took {elapsed:.4f} ms)")
            return result
        except Exception as e:
            logger.exception(f"Exception in {func.__name__}: {e}")
            raise
    return wrapper