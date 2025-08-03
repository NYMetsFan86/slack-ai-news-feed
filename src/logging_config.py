"""Secure logging configuration"""
import logging

from .security import sanitize_for_logging


class SanitizingFormatter(logging.Formatter):
    """Custom formatter that sanitizes sensitive data from logs"""

    def format(self, record: logging.LogRecord) -> str:
        # Format the message normally first
        formatted = super().format(record)

        # Sanitize the formatted message
        sanitized = sanitize_for_logging(formatted)

        # Also sanitize any args that might contain sensitive data
        if hasattr(record, 'args') and record.args:
            record.args = tuple(
                sanitize_for_logging(str(arg)) if isinstance(arg, str) else arg
                for arg in record.args
            )

        return sanitized


def configure_logging(level: str = "INFO") -> None:
    """Configure logging with security sanitization"""

    # Create sanitizing formatter
    formatter = SanitizingFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add new handler with sanitizing formatter
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Reduce noise from external libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('boto3').setLevel(logging.WARNING)
