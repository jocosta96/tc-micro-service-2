import logging
import json
from datetime import datetime
from enum import Enum
from typing import Optional

from src.config.app_config import app_config


class LogLevels(str, Enum):
    info = "INFO"
    warn = "WARN"
    error = "ERROR"
    debug = "DEBUG"


class StructuredLogger:
    """
    Structured logger for the application.

    In Clean Architecture:
    - This is part of the Frameworks & Drivers layer
    - It provides structured logging capabilities
    - It formats logs in JSON for better parsing
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.name = name

    def _format_log(self, level: str, message: str, **kwargs) -> str:
        """Format log message as structured JSON"""
        # Convert non-serializable objects to strings
        serializable_kwargs = {}
        for key, value in kwargs.items():
            if hasattr(value, '__str__'):
                serializable_kwargs[key] = str(value)
            else:
                serializable_kwargs[key] = repr(value)
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "logger": self.name,
            "message": message,
            **serializable_kwargs,
        }
        return json.dumps(log_entry)

    def info(self, message: str, **kwargs):
        """Log info message with structured data"""
        self.logger.info(self._format_log("INFO", message, **kwargs))

    def warning(self, message: str, **kwargs):
        """Log warning message with structured data"""
        self.logger.warning(self._format_log("WARNING", message, **kwargs))

    def error(self, message: str, **kwargs):
        """Log error message with structured data"""
        self.logger.error(self._format_log("ERROR", message, **kwargs))

    def debug(self, message: str, **kwargs):
        """Log debug message with structured data"""
        self.logger.debug(self._format_log("DEBUG", message, **kwargs))

    def exception(self, message: str, exc_info: Optional[Exception] = None, **kwargs):
        """Log exception with structured data"""
        if exc_info:
            kwargs["exception_type"] = type(exc_info).__name__
            kwargs["exception_message"] = str(exc_info)
        self.logger.error(self._format_log("ERROR", message, **kwargs))


def configure_logging(log_level: str = None):
    """Configure logging for the application"""
    if log_level is None:
        log_level = app_config.log_level

    # Convert enum to string if needed
    if isinstance(log_level, LogLevels):
        log_level = log_level.value

    log_level = str(log_level).upper()
    log_levels = [level.value for level in LogLevels]

    if log_level not in log_levels:
        logging.basicConfig(level=LogLevels.error.value)
        return

    if log_level == LogLevels.debug.value:
        logging.basicConfig(level=log_level, format=app_config.log_format)
        return

    logging.basicConfig(level=log_level)


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance"""
    return StructuredLogger(name)
