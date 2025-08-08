import logging
import sys
from typing import Dict

# Central registry to cache loggers per category
_logger_cache: Dict[str, logging.Logger] = {}

def get_logger(category: str) -> logging.Logger:
    """
    Returns a logger for the given category, creating it if necessary.
    """
    if category in _logger_cache:
        return _logger_cache[category]

    logger = logging.getLogger(category)
    logger.setLevel(logging.DEBUG)  # Allow all messages through this logger

    if not logger.handlers:
        # Only add handler if not already attached
        handler = logging.StreamHandler(sys.stdout)
        # %(asctime)s
        formatter = logging.Formatter(
            '%(levelname)s %(name)s:  %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    _logger_cache[category] = logger
    return logger

# Default/base logger used when no specific category is passed
logger = get_logger("[CONTAINER_CRAFT] ")
core_logger = get_logger("[Core] ")
mcpkg_logger = get_logger("[MCPKG] ")
