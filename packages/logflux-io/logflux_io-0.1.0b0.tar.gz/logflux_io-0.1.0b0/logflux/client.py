"""
LogFlux client module.

This module contains the main client classes for communicating with the LogFlux agent.
"""

import json
import socket
import threading
import time
from enum import Enum
from queue import Empty, Full, Queue
from threading import Event, Lock
from typing import Any, Dict, List, Optional, Union

from .config import Config, default_config
from .types import AuthRequest, AuthResponse, LogBatch, LogEntry, PingRequest, PongResponse


class CircuitBreakerState(Enum):
    """Circuit breaker state enumeration."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker implementation to prevent cascading failures."""

    def __init__(self, config: Config):
        """
        Initialize CircuitBreaker.

        Args:
            config: Configuration containing circuit breaker settings
        """
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0
        self._lock = Lock()

    def can_execute(self) -> bool:
        """Check if the circuit breaker allows execution."""
        with self._lock:
            if self.state == CircuitBreakerState.CLOSED:
                return True
            elif self.state == CircuitBreakerState.OPEN:
                # Check if timeout has elapsed
                if time.time() - self.last_failure_time >= self.config.circuit_breaker_timeout:
                    # Try to transition to half-open
                    self.state = CircuitBreakerState.HALF_OPEN
                    return True
                return False
            else:  # HALF_OPEN
                return True

    def on_success(self) -> None:
        """Record a successful operation."""
        with self._lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                # Successful call in half-open state, close the circuit
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
            elif self.state == CircuitBreakerState.CLOSED:
                # Reset failure count on success
                self.failure_count = 0

    def on_failure(self) -> None:
        """Record a failed operation."""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.state == CircuitBreakerState.HALF_OPEN:
                # Failure in half-open state, go back to open
                self.state = CircuitBreakerState.OPEN
            elif (
                self.state == CircuitBreakerState.CLOSED
                and self.failure_count >= self.config.circuit_breaker_threshold
            ):
                # Too many failures in closed state, open the circuit
                self.state = CircuitBreakerState.OPEN

    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        with self._lock:
            return {
                "state": self.state.value,
                "failure_count": self.failure_count,
                "is_open": self.state == CircuitBreakerState.OPEN,
            }


class AsyncRequest:
    """Represents an async send request."""

    def __init__(self, data: Any, result_event: Optional[Event] = None):
        """
        Initialize AsyncRequest.

        Args:
            data: Data to send
            result_event: Event to signal completion (None for fire-and-forget)
        """
        self.data = data
        self.result_event = result_event
        self.error: Optional[Exception] = None


class Client:
    """
    A lightweight client for communicating with LogFlux agent local server.
    It supports both Unix socket and TCP connections with automatic retry logic.
    Supports both synchronous and asynchronous sending modes with circuit breaker protection.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize Client.

        Args:
            config: Configuration (uses default if None)
        """
        self.config = config if config else default_config()
        self.socket: Optional[socket.socket] = None
        self.circuit_breaker = CircuitBreaker(self.config)
        self._lock = Lock()

        # Always use async mode for parent application safety
        self.async_queue: Optional[Queue] = None
        self.async_worker_thread: Optional[threading.Thread] = None
        self.stop_event: Optional[Event] = None

        # Force async mode regardless of config to prevent blocking parent app
        self._start_async_worker()

    def _start_async_worker(self) -> None:
        """Start the async worker thread."""
        self.async_queue = Queue(maxsize=self.config.channel_buffer)
        self.stop_event = Event()
        self.async_worker_thread = threading.Thread(target=self._async_worker, daemon=True)
        self.async_worker_thread.start()

    def _async_worker(self) -> None:
        """Async worker thread function."""
        if not self.stop_event or not self.async_queue:
            return

        while not self.stop_event.is_set():
            try:
                # Wait for requests with timeout
                request = self.async_queue.get(timeout=0.1)

                try:
                    self._send_with_retry(request.data)
                    request.error = None
                except Exception as e:
                    request.error = e

                if request.result_event:
                    request.result_event.set()

                self.async_queue.task_done()

            except Empty:
                continue
            except Exception as e:
                # Handle unexpected errors in worker thread
                try:
                    if "request" in locals() and request.result_event:
                        request.error = e
                        request.result_event.set()
                except Exception:
                    pass  # Ignore errors in error handling

    def connect(self) -> None:
        """Establish connection to the agent local server."""
        with self._lock:
            if self.socket:
                return  # Already connected

            if self.config.network == "unix":
                self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.socket.settimeout(self.config.timeout)
                self.socket.connect(self.config.address)
            elif self.config.network == "tcp":
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(self.config.timeout)
                host, port_str = self.config.address.rsplit(":", 1)
                port = int(port_str)
                self.socket.connect((host, port))
            else:
                raise ValueError(f"Unsupported network type: {self.config.network}")

    def close(self) -> None:
        """Close the connection and stop async workers."""
        try:
            # Always stop async worker (now always enabled)
            if self.stop_event:
                self.stop_event.set()
            if self.async_worker_thread:
                self.async_worker_thread.join(timeout=1.0)
        except Exception:
            pass  # Ignore errors during worker shutdown

        try:
            with self._lock:
                if self.socket:
                    self.socket.close()
                    self.socket = None
        except Exception:
            pass  # Ignore errors during socket close

    def send_log(self, message: str, source: str) -> None:
        """
        Send a single log message to the agent.
        Creates a LogEntry with the provided message and source.

        Args:
            message: Log message content
            source: Source identifier
        """
        entry = LogEntry(payload=message, source=source)
        self.send_log_entry(entry)

    def send_log_entry(self, entry: LogEntry) -> None:
        """
        Send a log entry to the agent.
        Always uses async mode to prevent blocking parent application.

        Args:
            entry: LogEntry to send
        """
        # Always use async mode to prevent blocking parent application
        self._send_async(entry)

    def send_log_batch(self, entries: List[LogEntry]) -> None:
        """
        Send multiple log entries as a batch.
        Always uses async mode to prevent blocking parent application.

        Args:
            entries: List of LogEntry objects to send
        """
        batch = LogBatch(entries=entries)

        # Always use async mode to prevent blocking parent application
        self._send_async(batch)

    def _send_with_retry(self, data: Union[LogEntry, LogBatch, PingRequest, AuthRequest]) -> None:
        """Send data with exponential backoff retry logic and circuit breaker protection."""
        if not self.circuit_breaker.can_execute():
            raise Exception("Circuit breaker is open")

        last_error = None

        for attempt in range(self.config.max_retries + 1):
            if attempt > 0:
                delay = self.config.calculate_backoff_delay(attempt)
                time.sleep(delay)

            try:
                # Ensure we have a connection
                if not self.socket:
                    self.connect()

                # Send the data
                self._send_data(data)

                # Success - notify circuit breaker
                self.circuit_breaker.on_success()
                return

            except Exception as e:
                last_error = e
                # Close connection on error to force reconnect
                with self._lock:
                    if self.socket:
                        self.socket.close()
                        self.socket = None
                continue

        # All retries failed - notify circuit breaker
        self.circuit_breaker.on_failure()
        raise Exception(
            f"Failed to send after {self.config.max_retries + 1} attempts: {last_error}"
        )

    def _send_data(self, data: Union[LogEntry, LogBatch, PingRequest, AuthRequest, Any]) -> None:
        """Send JSON data over the connection."""
        if isinstance(data, (LogEntry, LogBatch, PingRequest, AuthRequest)):
            json_data = json.dumps(data.to_dict())
        else:
            json_data = json.dumps(data)

        # Add newline for line-based protocol
        message = json_data + "\n"

        with self._lock:
            if not self.socket:
                raise Exception("Not connected")
            self.socket.sendall(message.encode("utf-8"))

    def _send_async(self, data: Union[LogEntry, LogBatch]) -> None:
        """Send data asynchronously via the worker thread."""
        if not self.async_queue or not self.stop_event:
            # Silent failure - don't crash parent application
            return

        request = AsyncRequest(data)

        try:
            self.async_queue.put_nowait(request)
        except Full:
            # Silent failure - log entry dropped but parent app remains safe
            # This is intentional: parent app safety > log delivery guarantee
            return

    def send_async_with_response(self, data: Union[LogEntry, LogBatch]) -> Event:
        """
        Send data asynchronously and return an Event for the response.
        This allows callers to optionally wait for the send result.

        Args:
            data: Data to send

        Returns:
            Event that will be set when the send completes
        """
        result_event = Event()

        if not self.async_queue or not self.stop_event:
            # Silent failure - set event immediately to prevent blocking
            result_event.set()
            return result_event

        request = AsyncRequest(data, result_event)

        try:
            self.async_queue.put_nowait(request)
            return result_event
        except Full:
            # Silent failure - set event immediately, don't set error
            result_event.set()
            return result_event

    def ping(self) -> PongResponse:
        """
        Send a ping request to the agent for health checking.

        Returns:
            PongResponse on success
        """
        ping = PingRequest()
        self._send_with_retry(ping)
        # Ping is fire-and-forget - assumes success if no send error
        return PongResponse(status="pong")

    def authenticate(self) -> AuthResponse:
        """
        Send an authentication request for TCP connections.
        Only required for TCP connections.

        Returns:
            AuthResponse on success
        """
        if self.config.network != "tcp":
            raise Exception("Authentication only required for TCP connections")

        if not self.config.shared_secret:
            raise Exception("Shared secret required for TCP authentication")

        auth_req = AuthRequest(shared_secret=self.config.shared_secret)
        self._send_with_retry(auth_req)

        # Authentication is fire-and-forget - assumes success if no send error
        return AuthResponse(status="success", message="Authentication successful")

    def get_circuit_breaker_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        return self.circuit_breaker.get_stats()


def new_unix_client(socket_path: str = "") -> Client:
    """
    Create a client configured for Unix socket communication.

    Args:
        socket_path: Socket path (uses default if empty)

    Returns:
        Configured Client instance
    """
    config = default_config()
    if socket_path:
        config.address = socket_path
    config.network = "unix"
    return Client(config)


def new_tcp_client(host: str = "", port: int = 0) -> Client:
    """
    Create a client configured for TCP communication.

    Args:
        host: Host address (defaults to "localhost")
        port: Port number (defaults to 8080)

    Returns:
        Configured Client instance
    """
    if not host:
        host = "localhost"
    if port <= 0 or port > 65535:
        port = 8080

    config = default_config()
    config.network = "tcp"
    config.address = f"{host}:{port}"
    return Client(config)
