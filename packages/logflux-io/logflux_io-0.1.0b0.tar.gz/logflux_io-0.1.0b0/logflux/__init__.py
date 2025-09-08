"""
LogFlux Python SDK

A lightweight Python SDK for communicating with the LogFlux agent.
Supports both Unix socket and TCP connections with automatic retry logic,
circuit breaker protection, and async/batch processing.
"""

from .batch import BatchClient, new_batch_tcp_client, new_batch_unix_client
from .client import Client, new_tcp_client, new_unix_client
from .config import BatchConfig, Config, default_batch_config, default_config
from .types import (  # Log levels; Entry types; Payload types; Protocol version
    DEFAULT_PROTOCOL_VERSION,
    LEVEL_ALERT,
    LEVEL_CRITICAL,
    LEVEL_DEBUG,
    LEVEL_EMERGENCY,
    LEVEL_ERROR,
    LEVEL_INFO,
    LEVEL_NOTICE,
    LEVEL_WARNING,
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

__version__ = "0.1.0-beta"
__author__ = "LogFlux Team"
__email__ = "support@logflux.io"
__description__ = "A lightweight Python SDK for LogFlux agent communication"

# Convenience exports
__all__ = [
    # Client classes
    "Client",
    "BatchClient",
    # Factory functions
    "new_unix_client",
    "new_tcp_client",
    "new_batch_unix_client",
    "new_batch_tcp_client",
    # Configuration
    "Config",
    "BatchConfig",
    "default_config",
    "default_batch_config",
    # Types
    "LogEntry",
    "LogBatch",
    "PingRequest",
    "PongResponse",
    "AuthRequest",
    "AuthResponse",
    # Factory functions for types
    "new_log_entry",
    "new_ping_request",
    "new_auth_request",
    # Constants - Log levels
    "LEVEL_EMERGENCY",
    "LEVEL_ALERT",
    "LEVEL_CRITICAL",
    "LEVEL_ERROR",
    "LEVEL_WARNING",
    "LEVEL_NOTICE",
    "LEVEL_INFO",
    "LEVEL_DEBUG",
    # Constants - Entry types
    "TYPE_LOG",
    # Constants - Payload types
    "PAYLOAD_TYPE_GENERIC",
    "PAYLOAD_TYPE_GENERIC_JSON",
    # Constants - Protocol
    "DEFAULT_PROTOCOL_VERSION",
]
