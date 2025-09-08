"""
LogFlux integration with Python's standard logging module.

This module provides a LogFlux handler that can be used with Python's
standard logging framework to send logs to LogFlux.
"""

import json
import logging
import traceback
from typing import Any, Dict, Optional, Union

from ..batch import BatchClient
from ..client import Client
from ..types import LEVEL_CRITICAL, LEVEL_DEBUG, LEVEL_ERROR, LEVEL_INFO, LEVEL_WARNING, LogEntry


class LogFluxHandler(logging.Handler):
    """
    A logging handler that sends log records to LogFlux.

    This handler can be used with Python's standard logging module
    to automatically send log records to the LogFlux agent.
    """

    # Mapping from Python logging levels to LogFlux levels
    LEVEL_MAPPING = {
        logging.DEBUG: LEVEL_DEBUG,
        logging.INFO: LEVEL_INFO,
        logging.WARNING: LEVEL_WARNING,
        logging.ERROR: LEVEL_ERROR,
        logging.CRITICAL: LEVEL_CRITICAL,
    }

    def __init__(
        self,
        client: Union[Client, BatchClient],
        source: str = "python-logging",
        include_extra: bool = True,
        include_stack_info: bool = True,
        json_format: bool = False,
    ):
        """
        Initialize the LogFlux handler.

        Args:
            client: LogFlux client (Client or BatchClient)
            source: Source identifier for log entries
            include_extra: Whether to include extra fields from log records
            include_stack_info: Whether to include stack trace information
            json_format: Whether to format log messages as JSON
        """
        super().__init__()
        self.client = client
        self.source = source
        self.include_extra = include_extra
        self.include_stack_info = include_stack_info
        self.json_format = json_format

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record to LogFlux.

        Args:
            record: The logging record to emit
        """
        try:
            # Convert the log record to a LogFlux entry
            log_entry = self._convert_record(record)

            # Send the log entry
            self.client.send_log_entry(log_entry)

        except Exception:
            # Complete protection against crashes - never let exceptions escape
            # This ensures parent application is never affected by LogFlux issues
            try:
                # Try to use standard logging error handler first
                self.handleError(record)
            except Exception:
                # If even handleError fails, silently ignore to protect parent app
                pass

    def _convert_record(self, record: logging.LogRecord) -> LogEntry:
        """
        Convert a Python logging record to a LogFlux LogEntry.

        Args:
            record: The logging record to convert

        Returns:
            A LogFlux LogEntry
        """
        # Format the message
        message = self.format(record)

        # Create metadata from record attributes
        metadata: Dict[str, str] = {
            "logger_name": record.name,
            "level_name": record.levelname,
            "module": record.module,
            "function": record.funcName or "",
            "line": str(record.lineno),
            "thread": str(record.thread),
            "thread_name": record.threadName or "",
            "process": str(record.process),
        }

        # Add pathname if available
        if hasattr(record, "pathname") and record.pathname:
            metadata["pathname"] = record.pathname

        # Add extra fields if enabled
        if self.include_extra and hasattr(record, "__dict__"):
            for key, value in record.__dict__.items():
                if key not in {
                    "name",
                    "msg",
                    "args",
                    "levelname",
                    "levelno",
                    "pathname",
                    "filename",
                    "module",
                    "lineno",
                    "funcName",
                    "created",
                    "msecs",
                    "relativeCreated",
                    "thread",
                    "threadName",
                    "processName",
                    "process",
                    "getMessage",
                    "exc_info",
                    "exc_text",
                    "stack_info",
                    "message",
                }:
                    metadata[f"extra_{key}"] = str(value)

        # Add exception information if available
        if record.exc_info and self.include_stack_info:
            exc_text = "".join(traceback.format_exception(*record.exc_info))
            metadata["exception"] = exc_text

        # Add stack info if available
        if record.stack_info and self.include_stack_info:
            metadata["stack_info"] = record.stack_info

        # Determine LogFlux log level
        logflux_level = self.LEVEL_MAPPING.get(record.levelno, LEVEL_INFO)

        # Create the payload
        if self.json_format:
            payload = self._create_json_payload(record, message, metadata)
        else:
            payload = message

        # Create and return the LogEntry
        return LogEntry(
            payload=payload, source=self.source, log_level=logflux_level, metadata=metadata
        )

    def _create_json_payload(
        self, record: logging.LogRecord, message: str, metadata: Dict[str, str]
    ) -> str:
        """
        Create a JSON payload from the log record.

        Args:
            record: The original logging record
            message: The formatted message
            metadata: Extracted metadata

        Returns:
            JSON formatted payload string
        """
        payload = {
            "timestamp": record.created,
            "level": record.levelname,
            "logger": record.name,
            "message": message,
            "metadata": metadata,
        }

        # Add exception info as structured data if available
        if record.exc_info:
            payload["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": "".join(traceback.format_exception(*record.exc_info)),
            }

        return json.dumps(payload)

    def close(self) -> None:
        """Close the handler and the underlying client."""
        try:
            if hasattr(self.client, "close"):
                self.client.close()
        except Exception:
            pass  # Ignore errors during close

        try:
            super().close()
        except Exception:
            # Complete protection - even super().close() might fail
            pass


def create_logflux_handler(
    client: Union[Client, BatchClient],
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    source: str = "python-logging",
    **kwargs: Any,
) -> LogFluxHandler:
    """
    Create and configure a LogFlux handler.

    Args:
        client: LogFlux client instance
        level: Logging level threshold
        format_string: Log message format string
        source: Source identifier for log entries
        **kwargs: Additional arguments passed to LogFluxHandler

    Returns:
        Configured LogFluxHandler instance
    """
    handler = LogFluxHandler(client, source=source, **kwargs)
    handler.setLevel(level)

    if format_string:
        formatter = logging.Formatter(format_string)
        handler.setFormatter(formatter)

    return handler


def setup_logging_with_logflux(
    client: Union[Client, BatchClient],
    logger_name: str = "",
    level: int = logging.INFO,
    format_string: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    source: str = "python-logging",
    **kwargs: Any,
) -> logging.Logger:
    """
    Set up a logger with LogFlux integration.

    Args:
        client: LogFlux client instance
        logger_name: Name of the logger (uses root logger if empty)
        level: Logging level threshold
        format_string: Log message format string
        source: Source identifier for log entries
        **kwargs: Additional arguments passed to LogFluxHandler

    Returns:
        Configured logger instance
    """
    # Get or create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # Create and add LogFlux handler
    handler = create_logflux_handler(
        client=client, level=level, format_string=format_string, source=source, **kwargs
    )

    logger.addHandler(handler)
    return logger
