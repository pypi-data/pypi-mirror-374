"""
LogFlux configuration module.

This module contains configuration classes and defaults for the LogFlux Python SDK.
"""

import random

# Default configuration constants
DEFAULT_NETWORK = "unix"
DEFAULT_SOCKET_PATH = "/tmp/logflux-agent.sock"

# Timeout defaults (in seconds)
DEFAULT_TIMEOUT = 10.0
DEFAULT_RETRY_DELAY = 0.1  # 100ms, reduced for tests
DEFAULT_MAX_RETRY_DELAY = 5.0  # 5s, reduced for tests
DEFAULT_RETRY_MULTIPLIER = 2.0
DEFAULT_JITTER_PERCENT = 0.1

# Batch defaults
DEFAULT_BATCH_SIZE = 10
DEFAULT_MAX_BATCH_SIZE = 10
DEFAULT_FLUSH_INTERVAL = 5.0  # 5 seconds

# Retry defaults
DEFAULT_MAX_RETRIES = 3

# Async defaults
DEFAULT_ASYNC_MODE = True
DEFAULT_CHANNEL_BUFFER = 1000

# Circuit breaker defaults
DEFAULT_CIRCUIT_BREAKER_THRESHOLD = 5  # Failures before opening
DEFAULT_CIRCUIT_BREAKER_TIMEOUT = 30.0  # How long to stay open (seconds)

# Batch size limits (from API spec)
MIN_BATCH_SIZE = 1
MAX_BATCH_SIZE = 100


class Config:
    """Configuration for the SDK client."""

    def __init__(
        self,
        network: str = DEFAULT_NETWORK,
        address: str = DEFAULT_SOCKET_PATH,
        shared_secret: str = "",
        timeout: float = DEFAULT_TIMEOUT,
        flush_interval: float = DEFAULT_FLUSH_INTERVAL,
        batch_size: int = DEFAULT_BATCH_SIZE,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        max_retry_delay: float = DEFAULT_MAX_RETRY_DELAY,
        retry_multiplier: float = DEFAULT_RETRY_MULTIPLIER,
        jitter_percent: float = DEFAULT_JITTER_PERCENT,
        async_mode: bool = DEFAULT_ASYNC_MODE,
        channel_buffer: int = DEFAULT_CHANNEL_BUFFER,
        circuit_breaker_threshold: int = DEFAULT_CIRCUIT_BREAKER_THRESHOLD,
        circuit_breaker_timeout: float = DEFAULT_CIRCUIT_BREAKER_TIMEOUT,
    ):
        """
        Initialize Config.

        Args:
            network: "unix" or "tcp"
            address: Socket path for unix, host:port for tcp
            shared_secret: Optional shared secret for authentication
            timeout: Connection timeout in seconds
            flush_interval: Time to wait before sending partial batch
            batch_size: Number of messages to batch before sending
            max_retries: Maximum retry attempts
            retry_delay: Initial delay between retries in seconds
            max_retry_delay: Maximum delay between retries in seconds
            retry_multiplier: Backoff multiplier (e.g., 2.0 for doubling)
            jitter_percent: Jitter as percentage (0.0-1.0)
            async_mode: Enable async/non-blocking mode
            channel_buffer: Buffer size for async queue
            circuit_breaker_threshold: Consecutive failures before opening circuit
            circuit_breaker_timeout: How long to keep circuit open in seconds
        """
        self.network = network
        self.address = address
        self.shared_secret = shared_secret
        self.timeout = timeout
        self.flush_interval = flush_interval
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.max_retry_delay = max_retry_delay
        self.retry_multiplier = retry_multiplier
        self.jitter_percent = jitter_percent
        self.async_mode = async_mode
        self.channel_buffer = channel_buffer
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout

    def calculate_backoff_delay(self, attempt: int) -> float:
        """
        Calculate the next retry delay using exponential backoff with jitter.

        Args:
            attempt: The current attempt number (0-based)

        Returns:
            Delay in seconds
        """
        if attempt <= 0:
            return self.retry_delay

        # Calculate exponential backoff: delay * multiplier^attempt
        delay = self.retry_delay
        for _ in range(attempt):
            delay *= self.retry_multiplier

        # Cap at maximum delay
        if delay > self.max_retry_delay:
            delay = self.max_retry_delay

        # Add jitter: ±(delay * jitter_percent)
        if self.jitter_percent > 0:
            jitter = delay * self.jitter_percent
            # Random value between -jitter and +jitter
            jitter_amount = (random.random() * 2 - 1) * jitter
            delay += jitter_amount

        # Ensure we don't go below the initial delay
        if delay < self.retry_delay:
            return self.retry_delay

        return delay


class BatchConfig:
    """Configuration for batch processing."""

    def __init__(
        self,
        max_batch_size: int = DEFAULT_MAX_BATCH_SIZE,
        flush_interval: float = DEFAULT_FLUSH_INTERVAL,
        auto_flush: bool = True,
    ):
        """
        Initialize BatchConfig.

        Args:
            max_batch_size: Maximum entries per batch
            flush_interval: Time to wait before sending partial batch in seconds
            auto_flush: Automatically flush batches
        """
        self.max_batch_size = max_batch_size
        self.flush_interval = flush_interval
        self.auto_flush = auto_flush


def default_config() -> Config:
    """Return a default configuration for Unix socket connection."""
    return Config()


def default_batch_config() -> BatchConfig:
    """Return default batch configuration."""
    return BatchConfig()
