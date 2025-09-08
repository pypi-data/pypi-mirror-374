"""
Unit tests for LogFlux logging handler integration.
"""

import json
import logging
import unittest
from unittest.mock import MagicMock, patch

from logflux.batch import BatchClient
from logflux.client import Client
from logflux.integrations.logging_handler import (
    LogFluxHandler,
    create_logflux_handler,
    setup_logging_with_logflux,
)
from logflux.types import (
    LEVEL_CRITICAL,
    LEVEL_DEBUG,
    LEVEL_ERROR,
    LEVEL_INFO,
    LEVEL_WARNING,
    LogEntry,
)


class TestLogFluxHandler(unittest.TestCase):
    """Test cases for LogFluxHandler class."""

    def setUp(self):
        self.mock_client = MagicMock(spec=Client)
        self.handler = LogFluxHandler(client=self.mock_client, source="test-source")

    def test_creation_with_client(self):
        """Test LogFluxHandler creation with client."""
        handler = LogFluxHandler(self.mock_client)

        self.assertEqual(handler.client, self.mock_client)
        self.assertEqual(handler.source, "python-logging")
        self.assertTrue(handler.include_extra)
        self.assertTrue(handler.include_stack_info)
        self.assertFalse(handler.json_format)

    def test_creation_with_batch_client(self):
        """Test LogFluxHandler creation with batch client."""
        mock_batch_client = MagicMock(spec=BatchClient)
        handler = LogFluxHandler(mock_batch_client)

        self.assertEqual(handler.client, mock_batch_client)

    def test_creation_with_custom_options(self):
        """Test LogFluxHandler creation with custom options."""
        handler = LogFluxHandler(
            client=self.mock_client,
            source="custom-source",
            include_extra=False,
            include_stack_info=False,
            json_format=True,
        )

        self.assertEqual(handler.source, "custom-source")
        self.assertFalse(handler.include_extra)
        self.assertFalse(handler.include_stack_info)
        self.assertTrue(handler.json_format)

    def test_level_mapping(self):
        """Test Python logging level to LogFlux level mapping."""
        expected_mapping = {
            logging.DEBUG: LEVEL_DEBUG,
            logging.INFO: LEVEL_INFO,
            logging.WARNING: LEVEL_WARNING,
            logging.ERROR: LEVEL_ERROR,
            logging.CRITICAL: LEVEL_CRITICAL,
        }

        self.assertEqual(LogFluxHandler.LEVEL_MAPPING, expected_mapping)

    def test_emit_basic_log_record(self):
        """Test emitting a basic log record."""
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        self.handler.emit(record)

        self.mock_client.send_log_entry.assert_called_once()

        # Verify the LogEntry was created correctly
        sent_entry = self.mock_client.send_log_entry.call_args[0][0]
        self.assertIsInstance(sent_entry, LogEntry)
        self.assertEqual(sent_entry.source, "test-source")
        self.assertEqual(sent_entry.log_level, LEVEL_INFO)

    def test_emit_with_different_log_levels(self):
        """Test emitting records with different log levels."""
        test_cases = [
            (logging.DEBUG, LEVEL_DEBUG),
            (logging.INFO, LEVEL_INFO),
            (logging.WARNING, LEVEL_WARNING),
            (logging.ERROR, LEVEL_ERROR),
            (logging.CRITICAL, LEVEL_CRITICAL),
        ]

        for python_level, expected_logflux_level in test_cases:
            with self.subTest(level=python_level):
                record = logging.LogRecord(
                    name="test.logger",
                    level=python_level,
                    pathname="/path/to/file.py",
                    lineno=42,
                    msg="Test message",
                    args=(),
                    exc_info=None,
                )

                self.handler.emit(record)

                sent_entry = self.mock_client.send_log_entry.call_args[0][0]
                self.assertEqual(sent_entry.log_level, expected_logflux_level)

        self.assertEqual(self.mock_client.send_log_entry.call_count, len(test_cases))

    def test_emit_with_unknown_level_defaults_to_info(self):
        """Test emitting record with unknown level defaults to INFO."""
        record = logging.LogRecord(
            name="test.logger",
            level=999,  # Unknown level
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        self.handler.emit(record)

        sent_entry = self.mock_client.send_log_entry.call_args[0][0]
        self.assertEqual(sent_entry.log_level, LEVEL_INFO)

    def test_convert_record_includes_metadata(self):
        """Test convert_record includes proper metadata."""
        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="/path/to/test_file.py",
            lineno=123,
            msg="Error message",
            args=(),
            exc_info=None,
            func="test_function",
        )
        record.module = "test_file"
        record.thread = 12345
        record.threadName = "MainThread"
        record.process = 9876

        entry = self.handler._convert_record(record)

        expected_metadata = {
            "logger_name": "test.logger",
            "level_name": "ERROR",
            "module": "test_file",
            "function": "test_function",
            "line": "123",
            "thread": "12345",
            "thread_name": "MainThread",
            "process": "9876",
            "pathname": "/path/to/test_file.py",
        }

        for key, expected_value in expected_metadata.items():
            self.assertEqual(entry.metadata[key], expected_value)

    def test_convert_record_with_extra_fields(self):
        """Test convert_record includes extra fields when enabled."""
        handler = LogFluxHandler(self.mock_client, include_extra=True)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Add extra fields
        record.user_id = "12345"
        record.request_id = "req-abc-123"

        entry = handler._convert_record(record)

        self.assertEqual(entry.metadata["extra_user_id"], "12345")
        self.assertEqual(entry.metadata["extra_request_id"], "req-abc-123")

    def test_convert_record_exclude_extra_fields(self):
        """Test convert_record excludes extra fields when disabled."""
        handler = LogFluxHandler(self.mock_client, include_extra=False)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Add extra fields
        record.user_id = "12345"

        entry = handler._convert_record(record)

        self.assertNotIn("extra_user_id", entry.metadata)

    def test_convert_record_with_exception_info(self):
        """Test convert_record includes exception information."""
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            exc_info = (type(e), e, e.__traceback__)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Error occurred",
            args=(),
            exc_info=exc_info,
        )

        entry = self.handler._convert_record(record)

        self.assertIn("exception", entry.metadata)
        self.assertIn("ValueError", entry.metadata["exception"])
        self.assertIn("Test exception", entry.metadata["exception"])

    def test_convert_record_exclude_stack_info(self):
        """Test convert_record excludes stack info when disabled."""
        handler = LogFluxHandler(self.mock_client, include_stack_info=False)

        try:
            raise ValueError("Test exception")
        except ValueError as e:
            exc_info = (type(e), e, e.__traceback__)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Error occurred",
            args=(),
            exc_info=exc_info,
        )

        entry = handler._convert_record(record)

        self.assertNotIn("exception", entry.metadata)

    def test_convert_record_with_stack_info(self):
        """Test convert_record includes stack info."""
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.stack_info = "Stack trace info here"

        entry = self.handler._convert_record(record)

        self.assertEqual(entry.metadata["stack_info"], "Stack trace info here")

    def test_json_format_payload(self):
        """Test JSON format payload creation."""
        handler = LogFluxHandler(self.mock_client, json_format=True)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.created = 1640995200.0  # Fixed timestamp for testing

        entry = handler._convert_record(record)

        # Parse the JSON payload
        payload_data = json.loads(entry.payload)

        self.assertEqual(payload_data["message"], "Test message")
        self.assertEqual(payload_data["level"], "INFO")
        self.assertEqual(payload_data["logger"], "test.logger")
        self.assertEqual(payload_data["timestamp"], 1640995200.0)
        self.assertIn("metadata", payload_data)

    def test_json_format_with_exception(self):
        """Test JSON format includes structured exception data."""
        handler = LogFluxHandler(self.mock_client, json_format=True)

        try:
            raise ValueError("Test exception")
        except ValueError as e:
            exc_info = (type(e), e, e.__traceback__)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Error occurred",
            args=(),
            exc_info=exc_info,
        )

        entry = handler._convert_record(record)
        payload_data = json.loads(entry.payload)

        self.assertIn("exception", payload_data)
        self.assertEqual(payload_data["exception"]["type"], "ValueError")
        self.assertEqual(payload_data["exception"]["message"], "Test exception")
        self.assertIn("traceback", payload_data["exception"])

    def test_emit_handles_errors_gracefully(self):
        """Test emit handles errors without breaking the application."""
        # Make client raise an exception
        self.mock_client.send_log_entry.side_effect = Exception("Client error")

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        with patch.object(self.handler, "handleError") as mock_handle_error:
            self.handler.emit(record)

            # Should call handleError instead of raising
            mock_handle_error.assert_called_once_with(record)

    def test_close_closes_client_if_available(self):
        """Test close calls client.close() if available."""
        self.handler.close()

        self.mock_client.close.assert_called_once()

    def test_close_ignores_client_close_errors(self):
        """Test close ignores errors from client.close()."""
        self.mock_client.close.side_effect = Exception("Close error")

        # Should not raise exception
        self.handler.close()

    def test_close_with_client_without_close_method(self):
        """Test close with client that doesn't have close method."""
        mock_client = MagicMock()
        del mock_client.close  # Remove close method

        handler = LogFluxHandler(mock_client)

        # Should not raise exception
        handler.close()

    @patch("logging.Handler.close")
    def test_close_calls_super_close(self, mock_super_close):
        """Test close calls super().close()."""
        self.handler.close()

        mock_super_close.assert_called_once()


class TestFactoryFunctions(unittest.TestCase):
    """Test cases for factory functions."""

    def setUp(self):
        self.mock_client = MagicMock(spec=Client)

    def test_create_logflux_handler_basic(self):
        """Test create_logflux_handler with basic parameters."""
        handler = create_logflux_handler(self.mock_client)

        self.assertIsInstance(handler, LogFluxHandler)
        self.assertEqual(handler.client, self.mock_client)
        self.assertEqual(handler.source, "python-logging")
        self.assertEqual(handler.level, logging.INFO)

    def test_create_logflux_handler_with_level(self):
        """Test create_logflux_handler with custom level."""
        handler = create_logflux_handler(self.mock_client, level=logging.DEBUG)

        self.assertEqual(handler.level, logging.DEBUG)

    def test_create_logflux_handler_with_format_string(self):
        """Test create_logflux_handler with custom format string."""
        format_string = "%(name)s - %(levelname)s - %(message)s"
        handler = create_logflux_handler(self.mock_client, format_string=format_string)

        self.assertIsNotNone(handler.formatter)
        self.assertEqual(handler.formatter._fmt, format_string)

    def test_create_logflux_handler_with_custom_source(self):
        """Test create_logflux_handler with custom source."""
        handler = create_logflux_handler(self.mock_client, source="custom-app")

        self.assertEqual(handler.source, "custom-app")

    def test_create_logflux_handler_with_kwargs(self):
        """Test create_logflux_handler passes kwargs to LogFluxHandler."""
        handler = create_logflux_handler(self.mock_client, json_format=True, include_extra=False)

        self.assertTrue(handler.json_format)
        self.assertFalse(handler.include_extra)

    def test_setup_logging_with_logflux_basic(self):
        """Test setup_logging_with_logflux with basic parameters."""
        logger = setup_logging_with_logflux(self.mock_client, logger_name="test.unique.logger")

        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.level, logging.INFO)
        # Check that our handler was added (there might be others from other tests)
        logflux_handlers = [h for h in logger.handlers if isinstance(h, LogFluxHandler)]
        self.assertGreaterEqual(len(logflux_handlers), 1)
        self.assertIsInstance(logflux_handlers[0], LogFluxHandler)

    def test_setup_logging_with_logflux_custom_logger_name(self):
        """Test setup_logging_with_logflux with custom logger name."""
        logger = setup_logging_with_logflux(self.mock_client, logger_name="myapp.module")

        self.assertEqual(logger.name, "myapp.module")

    def test_setup_logging_with_logflux_root_logger(self):
        """Test setup_logging_with_logflux with root logger."""
        logger = setup_logging_with_logflux(self.mock_client, logger_name="")

        self.assertEqual(logger.name, "root")

    def test_setup_logging_with_logflux_custom_parameters(self):
        """Test setup_logging_with_logflux with custom parameters."""
        format_string = "CUSTOM: %(message)s"
        logger = setup_logging_with_logflux(
            self.mock_client,
            logger_name="test.app",
            level=logging.WARNING,
            format_string=format_string,
            source="test-app",
            json_format=True,
        )

        self.assertEqual(logger.level, logging.WARNING)
        handler = logger.handlers[0]
        self.assertEqual(handler.source, "test-app")
        self.assertTrue(handler.json_format)
        self.assertEqual(handler.formatter._fmt, format_string)


class TestIntegrationWithRealLogging(unittest.TestCase):
    """Integration tests with real Python logging."""

    def setUp(self):
        self.mock_client = MagicMock(spec=Client)
        # Create a unique logger name to avoid interference
        import time

        unique_name = f"test.integration.{int(time.time() * 1000000)}"
        self.logger = setup_logging_with_logflux(
            self.mock_client,
            logger_name=unique_name,
            format_string="%(message)s",  # Simple format for predictable testing
        )

    def test_real_log_message_processing(self):
        """Test processing real log messages."""
        self.logger.info("This is a test message")

        self.mock_client.send_log_entry.assert_called_once()

        sent_entry = self.mock_client.send_log_entry.call_args[0][0]
        self.assertEqual(sent_entry.payload, "This is a test message")
        self.assertEqual(sent_entry.log_level, LEVEL_INFO)

    def test_real_log_message_with_formatting(self):
        """Test processing log messages with formatting."""
        self.logger.warning("User %s failed login attempt %d", "john_doe", 3)

        sent_entry = self.mock_client.send_log_entry.call_args[0][0]
        self.assertEqual(sent_entry.payload, "User john_doe failed login attempt 3")
        self.assertEqual(sent_entry.log_level, LEVEL_WARNING)

    def test_real_exception_logging(self):
        """Test logging real exceptions."""
        try:
            raise ValueError("Test exception for logging")
        except ValueError:
            self.logger.exception("An error occurred")

        sent_entry = self.mock_client.send_log_entry.call_args[0][0]
        self.assertIn("exception", sent_entry.metadata)
        self.assertIn("Test exception for logging", sent_entry.metadata["exception"])

    def test_real_log_with_extra_data(self):
        """Test logging with extra data."""
        self.logger.info(
            "Operation completed",
            extra={"user_id": "12345", "operation": "data_export", "duration_ms": 1250},
        )

        sent_entry = self.mock_client.send_log_entry.call_args[0][0]
        self.assertEqual(sent_entry.metadata["extra_user_id"], "12345")
        self.assertEqual(sent_entry.metadata["extra_operation"], "data_export")
        self.assertEqual(sent_entry.metadata["extra_duration_ms"], "1250")


if __name__ == "__main__":
    unittest.main()
