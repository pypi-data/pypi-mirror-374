"""
LogFlux types module.

This module contains all the data types used by the LogFlux Python SDK.
It matches the API specification for logflux-agent-api-v1.yaml.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

# Log level constants (syslog severity levels as per API spec)
LEVEL_EMERGENCY = 1  # System is unusable
LEVEL_ALERT = 2  # Action must be taken immediately
LEVEL_CRITICAL = 3  # Critical conditions
LEVEL_ERROR = 4  # Error conditions
LEVEL_WARNING = 5  # Warning conditions
LEVEL_NOTICE = 6  # Normal but significant condition
LEVEL_INFO = 7  # Informational messages
LEVEL_DEBUG = 8  # Debug-level messages

# Entry type constants
TYPE_LOG = 1  # Standard log entry (default for all entries)

# Default protocol version
DEFAULT_PROTOCOL_VERSION = "1.0"

# Payload type constants
PAYLOAD_TYPE_GENERIC = "generic"
PAYLOAD_TYPE_GENERIC_JSON = "generic_json"


class LogEntry:
    """
    Represents a log entry to be sent to the agent.
    Matches the API specification for logflux-agent-api-v1.yaml
    """

    def __init__(
        self,
        payload: str,
        source: str,
        version: Optional[str] = None,
        timestamp: Optional[str] = None,
        payload_type: Optional[str] = None,
        entry_type: int = TYPE_LOG,
        log_level: int = LEVEL_NOTICE,
        metadata: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize a LogEntry.

        Args:
            payload: The log message content
            source: The source identifier
            version: Protocol version (defaults to DEFAULT_PROTOCOL_VERSION)
            timestamp: Timestamp in RFC3339 format (defaults to current UTC time)
            payload_type: Type of payload (auto-detected if not provided)
            entry_type: Entry type (defaults to TYPE_LOG)
            log_level: Log level (defaults to LEVEL_INFO)
            metadata: Additional metadata key-value pairs
        """
        self.payload = payload
        self.source = source if source else "unknown"
        self.version = version if version else DEFAULT_PROTOCOL_VERSION
        self.entry_type = entry_type
        self.log_level = self._validate_log_level(log_level)
        self.timestamp = (
            timestamp
            if timestamp
            else datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        self.payload_type = (
            payload_type if payload_type else self._auto_detect_payload_type(payload)
        )
        self.metadata = metadata if metadata else {}

    def _validate_log_level(self, level: int) -> int:
        """Validate and return a valid log level."""
        if level < LEVEL_EMERGENCY or level > LEVEL_DEBUG:
            return LEVEL_NOTICE
        return level

    def _auto_detect_payload_type(self, message: str) -> str:
        """Auto-detect payload type based on content."""
        if self._is_valid_json(message):
            return PAYLOAD_TYPE_GENERIC_JSON
        return PAYLOAD_TYPE_GENERIC

    def _is_valid_json(self, s: str) -> bool:
        """Check if string is valid JSON."""
        try:
            json.loads(s)
            return True
        except (json.JSONDecodeError, TypeError):
            return False

    def with_log_level(self, log_level: int) -> "LogEntry":
        """Return a new LogEntry with the specified log level."""
        new_entry = self._copy()
        new_entry.log_level = self._validate_log_level(log_level)
        return new_entry

    def with_entry_type(self, entry_type: int) -> "LogEntry":
        """Return a new LogEntry with the specified entry type (only TYPE_LOG supported)."""
        new_entry = self._copy()
        new_entry.entry_type = TYPE_LOG  # Only TYPE_LOG supported in minimal SDK
        return new_entry

    def with_source(self, source: str) -> "LogEntry":
        """Return a new LogEntry with the specified source."""
        new_entry = self._copy()
        new_entry.source = source if source else "unknown"
        return new_entry

    def with_metadata(self, key: str, value: str) -> "LogEntry":
        """Return a new LogEntry with additional metadata."""
        if not key:
            return self
        new_entry = self._copy()
        new_entry.metadata = dict(self.metadata)
        new_entry.metadata[key] = value
        return new_entry

    def with_all_metadata(self, metadata: Dict[str, str]) -> "LogEntry":
        """Return a new LogEntry with multiple metadata fields."""
        new_entry = self._copy()
        new_entry.metadata = dict(self.metadata)
        new_entry.metadata.update(metadata)
        return new_entry

    def with_timestamp(self, timestamp: Union[datetime, str]) -> "LogEntry":
        """Return a new LogEntry with the specified timestamp."""
        new_entry = self._copy()
        if isinstance(timestamp, datetime):
            new_entry.timestamp = (
                timestamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
            )
        else:
            new_entry.timestamp = timestamp
        return new_entry

    def with_payload_type(self, payload_type: str) -> "LogEntry":
        """Return a new LogEntry with the specified payload type."""
        new_entry = self._copy()
        new_entry.payload_type = payload_type
        return new_entry

    def with_version(self, version: str) -> "LogEntry":
        """Return a new LogEntry with the specified protocol version."""
        new_entry = self._copy()
        new_entry.version = version
        return new_entry

    def _copy(self) -> "LogEntry":
        """Create a copy of this LogEntry."""
        return LogEntry(
            payload=self.payload,
            source=self.source,
            version=self.version,
            timestamp=self.timestamp,
            payload_type=self.payload_type,
            entry_type=self.entry_type,
            log_level=self.log_level,
            metadata=dict(self.metadata),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert LogEntry to dictionary for JSON serialization."""
        result = {
            "payload": self.payload,
            "source": self.source,
            "entryType": self.entry_type,
            "logLevel": self.log_level,
        }

        # Add optional fields only if they have values
        if self.version:
            result["version"] = self.version
        if self.timestamp:
            result["timestamp"] = self.timestamp
        if self.payload_type:
            result["payloadType"] = self.payload_type
        if self.metadata:
            result["metadata"] = self.metadata

        return result


class LogBatch:
    """
    Represents a batch of log entries.
    Matches the API specification for logflux-agent-api-v1.yaml
    """

    def __init__(self, entries: List[LogEntry], version: Optional[str] = None):
        """
        Initialize a LogBatch.

        Args:
            entries: Array of log entries (1-100 items)
            version: Protocol version (defaults to DEFAULT_PROTOCOL_VERSION)
        """
        self.entries = entries
        self.version = version if version else DEFAULT_PROTOCOL_VERSION

    def to_dict(self) -> Dict[str, Any]:
        """Convert LogBatch to dictionary for JSON serialization."""
        result: Dict[str, Any] = {"entries": [entry.to_dict() for entry in self.entries]}
        if self.version:
            result["version"] = self.version
        return result


class PingRequest:
    """Represents a ping health check request."""

    def __init__(self, version: Optional[str] = None):
        """
        Initialize a PingRequest.

        Args:
            version: Protocol version (defaults to DEFAULT_PROTOCOL_VERSION)
        """
        self.version = version if version else DEFAULT_PROTOCOL_VERSION
        self.action = "ping"

    def to_dict(self) -> Dict[str, Any]:
        """Convert PingRequest to dictionary for JSON serialization."""
        result = {"action": self.action}
        if self.version:
            result["version"] = self.version
        return result


class PongResponse:
    """Represents a pong health check response."""

    def __init__(self, status: str = "pong"):
        """
        Initialize a PongResponse.

        Args:
            status: Status (must be "pong")
        """
        self.status = status

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PongResponse":
        """Create PongResponse from dictionary."""
        return cls(status=data.get("status", "pong"))


class AuthRequest:
    """Represents an authentication request for TCP connections."""

    def __init__(self, shared_secret: str, version: Optional[str] = None):
        """
        Initialize an AuthRequest.

        Args:
            shared_secret: Shared secret for authentication
            version: Protocol version (defaults to DEFAULT_PROTOCOL_VERSION)
        """
        if not shared_secret:
            raise ValueError("shared_secret cannot be empty for authentication")
        self.shared_secret = shared_secret
        self.version = version if version else DEFAULT_PROTOCOL_VERSION
        self.action = "authenticate"

    def to_dict(self) -> Dict[str, Any]:
        """Convert AuthRequest to dictionary for JSON serialization."""
        result = {"action": self.action, "shared_secret": self.shared_secret}
        if self.version:
            result["version"] = self.version
        return result


class AuthResponse:
    """Represents an authentication response."""

    def __init__(self, status: str, message: str):
        """
        Initialize an AuthResponse.

        Args:
            status: Status ("success" or "error")
            message: Success or error message
        """
        self.status = status
        self.message = message

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuthResponse":
        """Create AuthResponse from dictionary."""
        return cls(status=data.get("status", "error"), message=data.get("message", ""))


def new_log_entry(payload: str, source: str) -> LogEntry:
    """
    Create a new log entry with default values and auto-detection.
    Automatically detects JSON payload type. All entries default to TYPE_LOG.

    Args:
        payload: The log message content
        source: The source identifier

    Returns:
        A new LogEntry instance
    """
    return LogEntry(payload=payload, source=source)


def new_ping_request() -> PingRequest:
    """Create a new ping request."""
    return PingRequest()


def new_auth_request(shared_secret: str) -> AuthRequest:
    """Create a new authentication request."""
    return AuthRequest(shared_secret=shared_secret)
