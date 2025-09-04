import logging
import os
from pathlib import Path
from typing import Union, Dict, Optional


class ErrorLogger:
    """Special class for logging error codes in image processing"""

    def __init__(self, error_codes: Dict[int, str], output_dir: Union[str, Path] = None, logger: logging.Logger = None):
        self.logger = logger
        self.output_dir = output_dir
        self.error_codes = error_codes

        self.error_file_name = "error.txt"
        self.recorded_errors = []

    def log_error_with_code(self, code: int, info: Optional[str] = None):
        """Log an error with a given error code"""
        if self.output_dir is None:
            raise Exception("output_dir is None.")

        log_msg = f"recording error with code: {code} ({self.error_codes[code]})"
        if info:
            log_msg += f" - info: {info}"

        if self.logger:
            if str(code).startswith("2"):
                self.logger.warning(log_msg)
            else:
                self.logger.error(log_msg)

        self.recorded_errors.append(code)

        error_path = os.path.join(self.output_dir, self.error_file_name)
        error_message = self.error_codes[code]
        if info:
            error_message += f" - info: {info}"

        with open(error_path, "a") as f:
            f.write(str(code) + "\n")
            f.write(error_message + "\n")

    def log_unknown_error_with_message(self, error_message: str, info: Optional[str] = None):
        """Log an error with a given error code"""
        if self.output_dir is None:
            raise Exception("output_dir is None.")

        self.logger.error(error_message)

        self.recorded_errors.append(3)

        error_path = os.path.join(self.output_dir, self.error_file_name)
        if info:
            error_message += f" - info: {info}"

        with open(error_path, "a") as f:
            f.write('error without code logged' + "\n")
            f.write(error_message + "\n")

    def last_recorded_error(self):
        """Returns last recorded error code. Returns 0 if no codes have been previously recorded."""
        if len(self.recorded_errors):
            return self.recorded_errors[-1]

        return 0
