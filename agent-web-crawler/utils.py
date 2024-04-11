import asyncio
import logging
import sys

def exponential_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
    return delay

async def retry_with_exponential_backoff(func, max_attempts: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
    for attempt in range(1, max_attempts + 1):
        try:
            return await func()
        except Exception as e:
            if attempt == max_attempts:
                raise e
            delay = exponential_backoff(attempt, base_delay, max_delay)
            logging.warning(f"Attempt {attempt} failed. Retrying in {delay} seconds...")
            await asyncio.sleep(delay)

def setup_logging(log_level, log_file=None):
    # Get the root logger
    logger = logging.getLogger()
    
    # Remove all existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    try:
        if log_file:
            # Create a FileHandler if a log file is specified
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    except Exception as e:
        print(f"Failed to set up file logging: {e}", file=sys.stderr)
    
    # Create a StreamHandler for logging to standard output
    stream_handler = logging.StreamHandler(stream=sys.stdout)  # Explicitly set to stdout
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    
    # Set the logging level for the root logger
    logger.setLevel(log_level)