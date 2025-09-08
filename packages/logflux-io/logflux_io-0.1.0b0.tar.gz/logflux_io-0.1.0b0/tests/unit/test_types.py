"""
Unit tests for LogFlux types module.
"""

import unittest
from datetime import datetime, timezone

from logflux.types import (
    LEVEL_ERROR,
    LEVEL_NOTICE,
    PAYLOAD_TYPE_GENERIC,
    PAYLOAD_TYPE_GENERIC_JSON,
    TYPE_LOG,
    AuthRequest,
    AuthResponse,
    LogBatch,
    LogEntry,
    PingRequest,
    PongResponse,
    new_auth_request,
    new_log_entry,
    new_ping_request,
)


class TestLogEntry(unittest.TestCase):
    """Test cases for LogEntry class."""

    def test_basic_creation(self):
        """Test basic LogEntry creation."""
        entry = LogEntry("test message", "test-source")

        self.assertEqual(entry.payload, "test message")
        self.assertEqual(entry.source, "test-source")
        self.assertEqual(entry.entry_type, TYPE_LOG)
        self.assertEqual(entry.log_level, LEVEL_NOTICE)
        self.assertEqual(entry.payload_type, PAYLOAD_TYPE_GENERIC)
        self.assertIsInstance(entry.metadata, dict)
        self.assertTrue(entry.timestamp)

    def test_json_payload_detection(self):
        """Test automatic JSON payload type detection."""
        json_payload = '{"key": "value", "number": 42}'
        entry = LogEntry(json_payload, "test-source")

        self.assertEqual(entry.payload_type, PAYLOAD_TYPE_GENERIC_JSON)

    def test_with_methods(self):
        """Test fluent API with_* methods."""
        entry = (
            LogEntry("test", "source")
            .with_log_level(LEVEL_ERROR)
            .with_metadata("key", "value")
            .with_source("new-source")
        )

        self.assertEqual(entry.log_level, LEVEL_ERROR)
        self.assertEqual(entry.metadata["key"], "value")
        self.assertEqual(entry.source, "new-source")

    def test_with_all_metadata(self):
        """Test with_all_metadata method."""
        metadata = {"key1": "value1", "key2": "value2"}
        entry = LogEntry("test", "source").with_all_metadata(metadata)

        self.assertEqual(entry.metadata["key1"], "value1")
        self.assertEqual(entry.metadata["key2"], "value2")

    def test_with_timestamp(self):
        """Test with_timestamp method."""
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        entry = LogEntry("test", "source").with_timestamp(dt)

        self.assertEqual(entry.timestamp, "2024-01-01T12:00:00Z")

    def test_to_dict(self):
        """Test to_dict serialization."""
        entry = (
            LogEntry("test message", "test-source")
            .with_log_level(LEVEL_ERROR)
            .with_metadata("key", "value")
        )

        data = entry.to_dict()

        self.assertEqual(data["payload"], "test message")
        self.assertEqual(data["source"], "test-source")
        self.assertEqual(data["logLevel"], LEVEL_ERROR)
        self.assertEqual(data["entryType"], TYPE_LOG)
        self.assertEqual(data["metadata"]["key"], "value")

    def test_log_level_validation(self):
        """Test log level validation."""
        # Invalid levels should default to LEVEL_INFO
        entry = LogEntry("test", "source", log_level=999)
        self.assertEqual(entry.log_level, LEVEL_NOTICE)

        entry = LogEntry("test", "source", log_level=-1)
        self.assertEqual(entry.log_level, LEVEL_NOTICE)

    def test_empty_source_handling(self):
        """Test handling of empty source."""
        entry = LogEntry("test", "")
        self.assertEqual(entry.source, "unknown")


class TestLogBatch(unittest.TestCase):
    """Test cases for LogBatch class."""

    def test_basic_creation(self):
        """Test basic LogBatch creation."""
        entries = [LogEntry("message1", "source1"), LogEntry("message2", "source2")]
        batch = LogBatch(entries)

        self.assertEqual(len(batch.entries), 2)
        self.assertTrue(batch.version)

    def test_to_dict(self):
        """Test LogBatch to_dict serialization."""
        entries = [LogEntry("test", "source")]
        batch = LogBatch(entries)

        data = batch.to_dict()

        self.assertIn("entries", data)
        self.assertIn("version", data)
        self.assertEqual(len(data["entries"]), 1)


class TestPingRequest(unittest.TestCase):
    """Test cases for PingRequest class."""

    def test_creation(self):
        """Test PingRequest creation."""
        ping = PingRequest()

        self.assertEqual(ping.action, "ping")
        self.assertTrue(ping.version)

    def test_to_dict(self):
        """Test PingRequest serialization."""
        ping = PingRequest()
        data = ping.to_dict()

        self.assertEqual(data["action"], "ping")
        self.assertIn("version", data)


class TestPongResponse(unittest.TestCase):
    """Test cases for PongResponse class."""

    def test_creation(self):
        """Test PongResponse creation."""
        pong = PongResponse()
        self.assertEqual(pong.status, "pong")

    def test_from_dict(self):
        """Test PongResponse from_dict creation."""
        data = {"status": "pong"}
        pong = PongResponse.from_dict(data)

        self.assertEqual(pong.status, "pong")


class TestAuthRequest(unittest.TestCase):
    """Test cases for AuthRequest class."""

    def test_creation(self):
        """Test AuthRequest creation."""
        auth = AuthRequest("secret123")

        self.assertEqual(auth.shared_secret, "secret123")
        self.assertEqual(auth.action, "authenticate")
        self.assertTrue(auth.version)

    def test_empty_secret_raises_error(self):
        """Test that empty shared secret raises ValueError."""
        with self.assertRaises(ValueError):
            AuthRequest("")

    def test_to_dict(self):
        """Test AuthRequest serialization."""
        auth = AuthRequest("secret123")
        data = auth.to_dict()

        self.assertEqual(data["action"], "authenticate")
        self.assertEqual(data["shared_secret"], "secret123")
        self.assertIn("version", data)


class TestAuthResponse(unittest.TestCase):
    """Test cases for AuthResponse class."""

    def test_creation(self):
        """Test AuthResponse creation."""
        auth = AuthResponse("success", "OK")

        self.assertEqual(auth.status, "success")
        self.assertEqual(auth.message, "OK")

    def test_from_dict(self):
        """Test AuthResponse from_dict creation."""
        data = {"status": "success", "message": "Authentication successful"}
        auth = AuthResponse.from_dict(data)

        self.assertEqual(auth.status, "success")
        self.assertEqual(auth.message, "Authentication successful")


class TestFactoryFunctions(unittest.TestCase):
    """Test cases for factory functions."""

    def test_new_log_entry(self):
        """Test new_log_entry factory function."""
        entry = new_log_entry("test message", "test-source")

        self.assertIsInstance(entry, LogEntry)
        self.assertEqual(entry.payload, "test message")
        self.assertEqual(entry.source, "test-source")

    def test_new_ping_request(self):
        """Test new_ping_request factory function."""
        ping = new_ping_request()

        self.assertIsInstance(ping, PingRequest)
        self.assertEqual(ping.action, "ping")

    def test_new_auth_request(self):
        """Test new_auth_request factory function."""
        auth = new_auth_request("secret123")

        self.assertIsInstance(auth, AuthRequest)
        self.assertEqual(auth.shared_secret, "secret123")


class TestEdgeCasesAndErrorHandling(unittest.TestCase):
    """Test cases for edge cases and error handling in types."""

    def test_log_entry_with_none_values(self):
        """Test LogEntry handles None values gracefully."""
        entry = LogEntry("test", None)  # None source
        self.assertEqual(entry.source, "unknown")

        entry = LogEntry("test", "")  # Empty source
        self.assertEqual(entry.source, "unknown")

    def test_log_entry_with_invalid_json_detection(self):
        """Test JSON detection with malformed JSON."""
        # Invalid JSON should default to generic payload type
        invalid_json = '{"incomplete": '
        entry = LogEntry(invalid_json, "source")
        self.assertEqual(entry.payload_type, PAYLOAD_TYPE_GENERIC)

    def test_log_entry_with_non_string_json_detection(self):
        """Test JSON detection with non-string input."""
        entry = LogEntry(123, "source")  # Number as payload
        # Should not crash and should handle gracefully
        self.assertEqual(entry.payload_type, PAYLOAD_TYPE_GENERIC)

    def test_log_entry_copy_preserves_all_fields(self):
        """Test that _copy preserves all fields correctly."""
        original = LogEntry(
            payload="test",
            source="source",
            version="2.0",
            timestamp="2024-01-01T00:00:00Z",
            payload_type=PAYLOAD_TYPE_GENERIC_JSON,
            entry_type=TYPE_LOG,
            log_level=LEVEL_ERROR,
            metadata={"key": "value"},
        )

        copy = original._copy()

        # Verify all fields are copied
        self.assertEqual(copy.payload, original.payload)
        self.assertEqual(copy.source, original.source)
        self.assertEqual(copy.version, original.version)
        self.assertEqual(copy.timestamp, original.timestamp)
        self.assertEqual(copy.payload_type, original.payload_type)
        self.assertEqual(copy.entry_type, original.entry_type)
        self.assertEqual(copy.log_level, original.log_level)
        self.assertEqual(copy.metadata, original.metadata)

        # Verify metadata is a separate dict (not shared reference)
        copy.metadata["new_key"] = "new_value"
        self.assertNotIn("new_key", original.metadata)

    def test_log_entry_with_methods_chain_correctly(self):
        """Test that with_* methods can be chained extensively."""
        entry = (
            LogEntry("test", "source")
            .with_log_level(LEVEL_ERROR)
            .with_metadata("key1", "value1")
            .with_metadata("key2", "value2")
            .with_source("new_source")
            .with_timestamp("2024-01-01T12:00:00Z")
            .with_payload_type(PAYLOAD_TYPE_GENERIC_JSON)
            .with_version("2.0")
        )

        self.assertEqual(entry.log_level, LEVEL_ERROR)
        self.assertEqual(entry.metadata["key1"], "value1")
        self.assertEqual(entry.metadata["key2"], "value2")
        self.assertEqual(entry.source, "new_source")
        self.assertEqual(entry.timestamp, "2024-01-01T12:00:00Z")
        self.assertEqual(entry.payload_type, PAYLOAD_TYPE_GENERIC_JSON)
        self.assertEqual(entry.version, "2.0")

    def test_log_entry_with_metadata_empty_key(self):
        """Test with_metadata with empty key returns self."""
        entry = LogEntry("test", "source")
        result = entry.with_metadata("", "value")

        self.assertIs(result, entry)  # Should return same instance
        self.assertNotIn("", entry.metadata)

    def test_log_entry_to_dict_optional_fields(self):
        """Test to_dict only includes optional fields when they have values."""
        entry = LogEntry("test", "source")

        # Clear optional fields
        entry.version = ""
        entry.timestamp = ""
        entry.payload_type = ""
        entry.metadata = {}

        data = entry.to_dict()

        # Should not include empty optional fields
        self.assertNotIn("version", data)
        self.assertNotIn("timestamp", data)
        self.assertNotIn("payloadType", data)
        self.assertNotIn("metadata", data)

        # Should include required fields
        self.assertIn("payload", data)
        self.assertIn("source", data)
        self.assertIn("entryType", data)
        self.assertIn("logLevel", data)

    def test_auth_request_empty_secret_validation(self):
        """Test AuthRequest validates empty shared secret."""
        with self.assertRaises(ValueError) as cm:
            AuthRequest("")

        self.assertIn("shared_secret cannot be empty", str(cm.exception))

        with self.assertRaises(ValueError):
            AuthRequest(None)

    def test_pong_response_from_dict_with_missing_status(self):
        """Test PongResponse.from_dict with missing status field."""
        data = {}  # No status field
        response = PongResponse.from_dict(data)

        self.assertEqual(response.status, "pong")  # Should default to "pong"

    def test_auth_response_from_dict_with_missing_fields(self):
        """Test AuthResponse.from_dict with missing fields."""
        data = {}  # No fields
        response = AuthResponse.from_dict(data)

        self.assertEqual(response.status, "error")  # Should default to "error"
        self.assertEqual(response.message, "")  # Should default to empty string

    def test_log_batch_empty_entries(self):
        """Test LogBatch with empty entries list."""
        batch = LogBatch([])

        self.assertEqual(len(batch.entries), 0)
        self.assertIsNotNone(batch.version)

        data = batch.to_dict()
        self.assertEqual(data["entries"], [])

    def test_factory_functions_with_edge_cases(self):
        """Test factory functions with edge case inputs."""
        # new_log_entry with empty strings
        entry = new_log_entry("", "")
        self.assertEqual(entry.payload, "")
        self.assertEqual(entry.source, "unknown")  # Empty source becomes "unknown"

        # new_auth_request with valid secret
        auth = new_auth_request("valid_secret")
        self.assertEqual(auth.shared_secret, "valid_secret")
        self.assertEqual(auth.action, "authenticate")


if __name__ == "__main__":
    unittest.main()
