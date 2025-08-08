import sys
import traceback
from typing import Optional
from container_craft_core.logger import get_logger

error_logger = get_logger("container_craft.error")

class ErrorHandler:
    def __init__(self, exit_on_error: bool = True):
        self.exit_on_error = exit_on_error

    def handle_error(
        self,
        message: str,
        exc: Optional[Exception] = None,
        exit_code: int = 1,
        fatal: bool = True,
    ):
        """
        Logs an error and optionally exits the program.

        Args:
            message: Error message to log.
            exc: Optional exception to include (with traceback).
            exit_code: Code to exit with (if fatal).
            fatal: If True, exits the process or raises an exception.
        """
        if exc:
            tb = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            error_logger.critical(f"{message}: {exc}\n{tb}")
        else:
            error_logger.critical(message)

        if fatal:
            if self.exit_on_error:
                sys.exit(exit_code)
            else:
                raise RuntimeError(message) from exc

# Default shared instance
error_handler = ErrorHandler()
