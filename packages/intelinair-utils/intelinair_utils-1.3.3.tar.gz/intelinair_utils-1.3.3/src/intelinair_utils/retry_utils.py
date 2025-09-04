import logging

logger = logging.getLogger(__name__)

def log_after_first_attempt(retry_state):
    """Logs a generic retry message after the first attempt fails."""
    if retry_state.attempt_number > 1:
        func_name = retry_state.fn.__name__  # Get the function name being retried
        logger.info(f"Attempt {retry_state.attempt_number}: Failed to execute '{func_name}'. Retrying...")
