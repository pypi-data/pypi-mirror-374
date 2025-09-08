"""
LogFlux batch client module.

This module contains the BatchClient class for automatic batching functionality.
"""

from threading import Lock, Timer
from typing import Any, Dict, List, Optional

from .client import Client
from .config import BatchConfig, default_batch_config
from .types import AuthResponse, LogEntry, PongResponse


class BatchStats:
    """Represents batch client statistics."""

    def __init__(
        self, pending_entries: int, max_batch_size: int, flush_interval: float, auto_flush: bool
    ):
        """
        Initialize BatchStats.

        Args:
            pending_entries: Number of entries pending in current batch
            max_batch_size: Maximum batch size
            flush_interval: Flush interval in seconds
            auto_flush: Whether auto-flush is enabled
        """
        self.pending_entries = pending_entries
        self.max_batch_size = max_batch_size
        self.flush_interval = flush_interval
        self.auto_flush = auto_flush

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "pending_entries": self.pending_entries,
            "max_batch_size": self.max_batch_size,
            "flush_interval": self.flush_interval,
            "auto_flush": self.auto_flush,
        }


class BatchClient:
    """
    BatchClient wraps the basic client with automatic batching functionality.
    It collects log entries and sends them in batches to improve performance.
    Supports automatic flushing based on batch size or time intervals.
    """

    def __init__(self, client: Client, batch_config: Optional[BatchConfig] = None):
        """
        Initialize BatchClient.

        Args:
            client: Underlying Client instance
            batch_config: Batch configuration (uses default if None)
        """
        if client is None:
            raise ValueError("client cannot be None")

        self.client = client
        self.config = batch_config if batch_config else default_batch_config()
        self.batch: List[LogEntry] = []
        self.timer: Optional[Timer] = None
        self.stopped = False
        self._lock = Lock()

        # Start auto-flush timer if enabled
        if self.config.auto_flush and self.config.flush_interval > 0:
            self._start_flush_timer()

    def connect(self) -> None:
        """Establish connection to the agent."""
        self.client.connect()

    def close(self) -> None:
        """Close the connection and flush any remaining entries."""
        with self._lock:
            self.stopped = True

            # Stop timer
            if self.timer:
                self.timer.cancel()
                self.timer = None

            # Flush remaining entries
            if self.batch:
                try:
                    self._flush_batch_locked()
                except Exception:
                    pass  # Ignore errors during close

        self.client.close()

    def send_log(self, message: str, source: str) -> None:
        """
        Add a log message to the batch.
        Creates a LogEntry with the provided message and source.

        Args:
            message: Log message content
            source: Source identifier
        """
        entry = LogEntry(payload=message, source=source)
        self.send_log_entry(entry)

    def send_log_entry(self, entry: LogEntry) -> None:
        """
        Add a log entry to the batch.
        If the batch reaches maximum size, automatically flushes it.
        Never blocks parent application.

        Args:
            entry: LogEntry to add to batch
        """
        try:
            with self._lock:
                if self.stopped:
                    # Send directly if stopped (async mode ensures no blocking)
                    self.client.send_log_entry(entry)
                    return

                # Add to batch
                self.batch.append(entry)

                # Check if batch is full
                if len(self.batch) >= self.config.max_batch_size:
                    self._flush_batch_locked()
        except Exception:
            # Silent failure - never crash parent application
            pass

    def flush(self) -> None:
        """Manually flush the current batch."""
        with self._lock:
            self._flush_batch_locked()

    def _flush_batch_locked(self) -> None:
        """Flush the current batch (must be called with lock held)."""
        if not self.batch:
            return

        # Create a copy of the batch to avoid race conditions
        batch_copy = list(self.batch)

        # Clear the batch regardless of error (avoid infinite retry loops)
        self.batch.clear()

        # Restart timer
        if self.config.auto_flush and not self.stopped:
            self._start_flush_timer_locked()

        # Send the batch copy (after clearing state)
        # Using async client ensures this never blocks parent app
        try:
            self.client.send_log_batch(batch_copy)
        except Exception:
            # Silent failure - parent app safety is priority
            pass

    def _start_flush_timer(self) -> None:
        """Start the auto-flush timer."""
        with self._lock:
            self._start_flush_timer_locked()

    def _start_flush_timer_locked(self) -> None:
        """Start the timer (must be called with lock held)."""
        if self.timer:
            self.timer.cancel()

        def timer_callback() -> None:
            with self._lock:
                if not self.stopped and self.batch:
                    try:
                        self._flush_batch_locked()
                    except Exception:
                        pass  # Ignore errors in timer callback

        self.timer = Timer(self.config.flush_interval, timer_callback)
        self.timer.start()

    def get_stats(self) -> BatchStats:
        """Get batch client statistics."""
        with self._lock:
            return BatchStats(
                pending_entries=len(self.batch),
                max_batch_size=self.config.max_batch_size,
                flush_interval=self.config.flush_interval,
                auto_flush=self.config.auto_flush,
            )

    def ping(self) -> PongResponse:
        """
        Send a ping request directly without batching.

        Returns:
            PongResponse from the underlying client
        """
        return self.client.ping()

    def authenticate(self) -> AuthResponse:
        """
        Send authentication request directly without batching.

        Returns:
            AuthResponse from the underlying client
        """
        return self.client.authenticate()


def new_batch_unix_client(
    socket_path: str = "", batch_config: Optional[BatchConfig] = None
) -> BatchClient:
    """
    Create a batch client for Unix socket communication.

    Args:
        socket_path: Socket path (uses default if empty)
        batch_config: Batch configuration (uses default if None)

    Returns:
        Configured BatchClient instance
    """
    from .client import new_unix_client

    client = new_unix_client(socket_path)
    return BatchClient(client, batch_config)


def new_batch_tcp_client(
    host: str = "", port: int = 0, batch_config: Optional[BatchConfig] = None
) -> BatchClient:
    """
    Create a batch client for TCP communication.

    Args:
        host: Host address (defaults to "localhost")
        port: Port number (defaults to 8080)
        batch_config: Batch configuration (uses default if None)

    Returns:
        Configured BatchClient instance
    """
    from .client import new_tcp_client

    client = new_tcp_client(host, port)
    return BatchClient(client, batch_config)
