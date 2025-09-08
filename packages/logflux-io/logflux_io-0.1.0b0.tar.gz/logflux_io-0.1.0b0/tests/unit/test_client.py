"""
Unit tests for LogFlux client module.
"""

import socket
import threading
import time
import unittest
from unittest.mock import MagicMock, patch

from logflux.client import (
    AsyncRequest,
    CircuitBreaker,
    CircuitBreakerState,
    Client,
    new_tcp_client,
    new_unix_client,
)
from logflux.config import Config
from logflux.types import LogEntry


class TestCircuitBreaker(unittest.TestCase):
    """Test cases for CircuitBreaker class."""

    def setUp(self):
        self.config = Config(circuit_breaker_threshold=3, circuit_breaker_timeout=1.0)
        self.breaker = CircuitBreaker(self.config)

    def test_initial_state_closed(self):
        """Test circuit breaker starts in closed state."""
        self.assertEqual(self.breaker.state, CircuitBreakerState.CLOSED)
        self.assertTrue(self.breaker.can_execute())
        self.assertEqual(self.breaker.failure_count, 0)

    def test_can_execute_closed_state(self):
        """Test can_execute returns True in closed state."""
        self.assertTrue(self.breaker.can_execute())

    def test_on_success_resets_failure_count(self):
        """Test on_success resets failure count in closed state."""
        self.breaker.failure_count = 2
        self.breaker.on_success()
        self.assertEqual(self.breaker.failure_count, 0)
        self.assertEqual(self.breaker.state, CircuitBreakerState.CLOSED)

    def test_on_failure_increments_count(self):
        """Test on_failure increments failure count."""
        self.breaker.on_failure()
        self.assertEqual(self.breaker.failure_count, 1)
        self.assertEqual(self.breaker.state, CircuitBreakerState.CLOSED)

    def test_circuit_opens_after_threshold(self):
        """Test circuit opens after reaching failure threshold."""
        for _ in range(self.config.circuit_breaker_threshold):
            self.breaker.on_failure()

        self.assertEqual(self.breaker.state, CircuitBreakerState.OPEN)
        self.assertFalse(self.breaker.can_execute())

    def test_circuit_transitions_to_half_open(self):
        """Test circuit transitions from open to half-open after timeout."""
        # Force circuit to open
        for _ in range(self.config.circuit_breaker_threshold):
            self.breaker.on_failure()

        # Wait for timeout
        time.sleep(self.config.circuit_breaker_timeout + 0.1)

        # Should transition to half-open
        self.assertTrue(self.breaker.can_execute())
        self.assertEqual(self.breaker.state, CircuitBreakerState.HALF_OPEN)

    def test_half_open_success_closes_circuit(self):
        """Test successful call in half-open state closes circuit."""
        # Set to half-open state
        self.breaker.state = CircuitBreakerState.HALF_OPEN

        self.breaker.on_success()
        self.assertEqual(self.breaker.state, CircuitBreakerState.CLOSED)
        self.assertEqual(self.breaker.failure_count, 0)

    def test_half_open_failure_reopens_circuit(self):
        """Test failure in half-open state reopens circuit."""
        # Set to half-open state
        self.breaker.state = CircuitBreakerState.HALF_OPEN

        self.breaker.on_failure()
        self.assertEqual(self.breaker.state, CircuitBreakerState.OPEN)

    def test_get_stats(self):
        """Test get_stats returns correct information."""
        stats = self.breaker.get_stats()

        self.assertIn("state", stats)
        self.assertIn("failure_count", stats)
        self.assertIn("is_open", stats)
        self.assertEqual(stats["state"], "closed")
        self.assertEqual(stats["failure_count"], 0)
        self.assertFalse(stats["is_open"])


class TestAsyncRequest(unittest.TestCase):
    """Test cases for AsyncRequest class."""

    def test_creation_without_event(self):
        """Test AsyncRequest creation without result event."""
        data = {"test": "data"}
        request = AsyncRequest(data)

        self.assertEqual(request.data, data)
        self.assertIsNone(request.result_event)
        self.assertIsNone(request.error)

    def test_creation_with_event(self):
        """Test AsyncRequest creation with result event."""
        data = {"test": "data"}
        event = threading.Event()
        request = AsyncRequest(data, event)

        self.assertEqual(request.data, data)
        self.assertEqual(request.result_event, event)
        self.assertIsNone(request.error)


class TestClient(unittest.TestCase):
    """Test cases for Client class."""

    def setUp(self):
        self.config = Config(
            network="unix", address="/tmp/test.sock", timeout=1.0, max_retries=2, async_mode=False
        )

    @patch("socket.socket")
    def test_unix_socket_connection(self, mock_socket_class):
        """Test Unix socket connection."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        client = Client(self.config)
        client.connect()

        mock_socket_class.assert_called_with(socket.AF_UNIX, socket.SOCK_STREAM)
        mock_socket.settimeout.assert_called_with(self.config.timeout)
        mock_socket.connect.assert_called_with(self.config.address)

    @patch("socket.socket")
    def test_tcp_connection(self, mock_socket_class):
        """Test TCP connection."""
        config = Config(network="tcp", address="localhost:8080")
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        client = Client(config)
        client.connect()

        mock_socket_class.assert_called_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_socket.connect.assert_called_with(("localhost", 8080))

    def test_invalid_network_raises_error(self):
        """Test invalid network type raises error."""
        config = Config(network="invalid")
        client = Client(config)

        with self.assertRaises(ValueError):
            client.connect()

    @patch("socket.socket")
    def test_connection_only_once(self, mock_socket_class):
        """Test connection is only established once."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        client = Client(self.config)
        client.connect()
        client.connect()  # Second call should not create new connection

        mock_socket_class.assert_called_once()

    @patch("socket.socket")
    def test_close_connection(self, mock_socket_class):
        """Test connection close."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        client = Client(self.config)
        client.connect()
        client.close()

        mock_socket.close.assert_called_once()
        self.assertIsNone(client.socket)

    @patch("socket.socket")
    def test_send_log_entry_async_only(self, mock_socket_class):
        """Test sending log entry - now always async for parent app safety."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        client = Client(self.config)
        entry = LogEntry("test message", "test-source")

        client.send_log_entry(entry)

        # Give async worker time to process
        time.sleep(0.2)

        # Should connect and send data via async worker
        mock_socket.connect.assert_called()
        mock_socket.sendall.assert_called()

        client.close()

    @patch("socket.socket")
    def test_send_log_batch(self, mock_socket_class):
        """Test sending log batch - now always async."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        client = Client(self.config)
        entries = [LogEntry("message1", "source1"), LogEntry("message2", "source2")]

        client.send_log_batch(entries)

        # Give async worker time to process
        time.sleep(0.2)

        # Verify batch was sent via async worker
        mock_socket.sendall.assert_called()

        client.close()

    @patch("socket.socket")
    def test_retry_on_connection_failure(self, mock_socket_class):
        """Test retry logic on connection failure."""
        mock_socket = MagicMock()
        mock_socket.connect.side_effect = [
            socket.error("Connection failed"),
            None,  # Success on second try
        ]
        mock_socket_class.return_value = mock_socket

        client = Client(self.config)
        entry = LogEntry("test", "source")

        # Test the internal retry method directly since async mode hides exceptions
        # Should succeed on second try (no exception expected)
        client._send_with_retry(entry)

        # Should have tried to connect twice (first fails, second succeeds)
        self.assertEqual(mock_socket.connect.call_count, 2)

    @patch("socket.socket")
    def test_circuit_breaker_opens_on_failures(self, mock_socket_class):
        """Test circuit breaker opens after repeated failures."""
        mock_socket = MagicMock()
        mock_socket.connect.side_effect = socket.error("Connection failed")
        mock_socket_class.return_value = mock_socket

        config = Config(max_retries=0, circuit_breaker_threshold=2)
        client = Client(config)
        entry = LogEntry("test", "source")

        # Test circuit breaker directly since async mode hides exceptions
        # First failure
        try:
            client._send_with_retry(entry)
            self.fail("Expected exception on first failure")
        except Exception:
            pass

        # Second failure should open circuit
        try:
            client._send_with_retry(entry)
            self.fail("Expected exception on second failure")
        except Exception:
            pass

        # Third call should be blocked by circuit breaker
        try:
            client._send_with_retry(entry)
            self.fail("Expected circuit breaker exception")
        except Exception as e:
            self.assertIn("Circuit breaker is open", str(e))

        # Circuit should be open now
        stats = client.get_circuit_breaker_stats()
        self.assertTrue(stats["is_open"])

    def test_send_log_convenience_method(self):
        """Test send_log convenience method."""
        client = Client(self.config)

        with patch.object(client, "send_log_entry") as mock_send:
            client.send_log("test message", "test-source")

            mock_send.assert_called_once()
            entry = mock_send.call_args[0][0]
            self.assertEqual(entry.payload, "test message")
            self.assertEqual(entry.source, "test-source")

    @patch("socket.socket")
    def test_ping(self, mock_socket_class):
        """Test ping functionality."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        client = Client(self.config)
        response = client.ping()

        self.assertEqual(response.status, "pong")
        mock_socket.sendall.assert_called_once()

    @patch("socket.socket")
    def test_authenticate_tcp(self, mock_socket_class):
        """Test authentication for TCP connections."""
        config = Config(
            network="tcp", address="localhost:8080", shared_secret="secret123", async_mode=False
        )
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        client = Client(config)
        response = client.authenticate()

        self.assertEqual(response.status, "success")
        mock_socket.sendall.assert_called_once()

    def test_authenticate_unix_raises_error(self):
        """Test authentication raises error for Unix connections."""
        client = Client(self.config)  # Unix socket config

        with self.assertRaises(Exception) as cm:
            client.authenticate()

        self.assertIn("Authentication only required for TCP", str(cm.exception))

    def test_authenticate_without_secret_raises_error(self):
        """Test authentication without shared secret raises error."""
        config = Config(network="tcp", shared_secret="")
        client = Client(config)

        with self.assertRaises(Exception) as cm:
            client.authenticate()

        self.assertIn("Shared secret required", str(cm.exception))

    def test_get_circuit_breaker_stats(self):
        """Test getting circuit breaker statistics."""
        client = Client(self.config)
        stats = client.get_circuit_breaker_stats()

        self.assertIn("state", stats)
        self.assertIn("failure_count", stats)
        self.assertIn("is_open", stats)


class TestClientAsync(unittest.TestCase):
    """Test cases for Client async functionality."""

    def setUp(self):
        self.config = Config(
            network="unix", address="/tmp/test.sock", async_mode=True, channel_buffer=10
        )

    def test_async_mode_initialization(self):
        """Test async mode initializes worker thread and queue."""
        client = Client(self.config)

        self.assertIsNotNone(client.async_queue)
        self.assertIsNotNone(client.async_worker_thread)
        self.assertIsNotNone(client.stop_event)
        self.assertTrue(client.async_worker_thread.is_alive())

        client.close()

    @patch("socket.socket")
    def test_send_async(self, mock_socket_class):
        """Test asynchronous sending."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        client = Client(self.config)
        entry = LogEntry("async test", "source")

        client.send_log_entry(entry)

        # Give async worker time to process
        time.sleep(0.2)

        # Verify that sendall was called and contains our expected data
        mock_socket.sendall.assert_called()
        calls = mock_socket.sendall.call_args_list

        # Check that at least one call contains our log entry data
        expected_payload = b'"async test"'
        found_expected = any(expected_payload in call[0][0] for call in calls)
        self.assertTrue(found_expected, f"Expected log entry not found in calls: {calls}")

        client.close()

    def test_send_async_with_response(self):
        """Test async sending with response event."""
        client = Client(self.config)
        entry = LogEntry("test", "source")

        with patch.object(client, "_send_with_retry") as mock_send:
            event = client.send_async_with_response(entry)

            # Wait for completion
            event.wait(timeout=1.0)

            self.assertTrue(event.is_set())
            mock_send.assert_called_once()

        client.close()

    def test_async_queue_full_handling(self):
        """Test handling when async queue is full - now silent for parent app safety."""
        config = Config(async_mode=True, channel_buffer=1)
        client = Client(config)

        # Fill the queue
        client.async_queue.put(AsyncRequest("dummy"))

        entry = LogEntry("test", "source")

        # Should NOT raise exception - silent failure for parent app safety
        client._send_async(entry)  # This should silently do nothing

        # Verify no exception was raised
        self.assertTrue(True)  # If we get here, no exception was raised
        client.close()

    def test_close_stops_async_worker(self):
        """Test close stops async worker thread."""
        client = Client(self.config)
        worker_thread = client.async_worker_thread

        self.assertTrue(worker_thread.is_alive())

        client.close()

        # Give thread time to stop
        time.sleep(0.2)

        self.assertFalse(worker_thread.is_alive())


class TestFactoryFunctions(unittest.TestCase):
    """Test cases for factory functions."""

    def test_new_unix_client(self):
        """Test new_unix_client factory function."""
        client = new_unix_client("/tmp/custom.sock")

        self.assertEqual(client.config.network, "unix")
        self.assertEqual(client.config.address, "/tmp/custom.sock")

    def test_new_unix_client_default_path(self):
        """Test new_unix_client with default path."""
        client = new_unix_client()

        self.assertEqual(client.config.network, "unix")
        self.assertTrue(client.config.address.endswith(".sock"))

    def test_new_tcp_client(self):
        """Test new_tcp_client factory function."""
        client = new_tcp_client("example.com", 9090)

        self.assertEqual(client.config.network, "tcp")
        self.assertEqual(client.config.address, "example.com:9090")

    def test_new_tcp_client_defaults(self):
        """Test new_tcp_client with default values."""
        client = new_tcp_client()

        self.assertEqual(client.config.network, "tcp")
        self.assertEqual(client.config.address, "localhost:8080")

    def test_new_tcp_client_invalid_port(self):
        """Test new_tcp_client with invalid port uses default."""
        client = new_tcp_client("example.com", 70000)

        self.assertEqual(client.config.address, "example.com:8080")


class TestErrorHandlingPaths(unittest.TestCase):
    """Test cases for error handling paths and edge cases."""

    def setUp(self):
        self.config = Config(
            network="unix", address="/tmp/test.sock", timeout=1.0, max_retries=1, async_mode=False
        )

    @patch("socket.socket")
    def test_send_data_with_none_socket_raises_error(self, mock_socket_class):
        """Test _send_data with None socket raises error."""
        client = Client(self.config)
        entry = LogEntry("test", "source")

        with self.assertRaises(Exception) as cm:
            client._send_data(entry)

        self.assertIn("Not connected", str(cm.exception))

    @patch("socket.socket")
    def test_send_data_handles_dict_data(self, mock_socket_class):
        """Test _send_data can handle dictionary data."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        client = Client(self.config)
        client.connect()

        # Send raw dictionary data
        data = {"test": "data"}
        client._send_data(data)

        mock_socket.sendall.assert_called_once()
        sent_data = mock_socket.sendall.call_args[0][0].decode("utf-8")
        self.assertTrue(sent_data.endswith("\n"))

    @patch("socket.socket")
    def test_tcp_address_parsing_edge_cases(self, mock_socket_class):
        """Test TCP address parsing edge cases."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        # Test with IPv6-style address
        config = Config(network="tcp", address="[::1]:8080")
        client = Client(config)

        client.connect()

        # Should connect to the parsed host and port
        mock_socket.connect.assert_called_once()
        host, port = mock_socket.connect.call_args[0][0]
        self.assertEqual(port, 8080)

    def test_circuit_breaker_timeout_edge_case(self):
        """Test circuit breaker with zero timeout."""
        config = Config(circuit_breaker_timeout=0.0)
        breaker = CircuitBreaker(config)

        # Force circuit to open
        for _ in range(config.circuit_breaker_threshold):
            breaker.on_failure()

        # With zero timeout, should immediately allow execution
        self.assertTrue(breaker.can_execute())
        self.assertEqual(breaker.state, CircuitBreakerState.HALF_OPEN)

    def test_async_worker_thread_exception_handling(self):
        """Test async worker handles unexpected exceptions."""
        config = Config(async_mode=True, channel_buffer=1, max_retries=0)
        client = Client(config)

        try:
            # Create a request with data that will cause a JSON error
            import threading

            result_event = threading.Event()
            bad_request = AsyncRequest(
                {"data": object()}, result_event
            )  # object() is not JSON serializable

            client.async_queue.put(bad_request)

            # Wait for worker to process
            result_event.wait(timeout=1.0)

            # Worker should handle the error gracefully
            self.assertTrue(result_event.is_set())
            self.assertIsNotNone(bad_request.error)

        finally:
            client.close()

    @patch("socket.socket")
    def test_socket_close_on_send_error(self, mock_socket_class):
        """Test socket is closed when send error occurs."""
        mock_socket = MagicMock()
        mock_socket.sendall.side_effect = socket.error("Send failed")
        mock_socket_class.return_value = mock_socket

        client = Client(self.config)
        entry = LogEntry("test", "source")

        # Test internal method since async mode hides exceptions
        with self.assertRaises(Exception):
            client._send_with_retry(entry)

        # Socket should be closed after error
        mock_socket.close.assert_called()
        self.assertIsNone(client.socket)

    def test_async_mode_always_initialized(self):
        """Test that async mode is always initialized for parent app safety."""
        client = Client(Config())

        # Async components should always be initialized
        self.assertIsNotNone(client.async_queue)
        self.assertIsNotNone(client.stop_event)
        self.assertIsNotNone(client.async_worker_thread)

        # Test that sending doesn't raise exceptions (silent failure mode)
        entry = LogEntry("test", "source")

        # Should not raise exception (silent failure for parent app safety)
        client.send_log_entry(entry)

    def test_close_with_none_async_worker(self):
        """Test close when async worker thread is None."""
        client = Client(Config(async_mode=False))
        client.async_worker_thread = None

        # Should not raise exception
        client.close()

    def test_config_calculate_backoff_delay_edge_cases(self):
        """Test edge cases in backoff delay calculation."""
        config = Config(
            retry_delay=1.0,
            retry_multiplier=2.0,
            max_retry_delay=0.5,  # Max less than base
            jitter_percent=0.0,
        )

        # When max_retry_delay is less than calculated delay, should be capped
        delay = config.calculate_backoff_delay(1)
        # Since max_retry_delay (0.5) < retry_delay (1.0), it should return retry_delay
        self.assertEqual(delay, config.retry_delay)

    def test_config_calculate_backoff_delay_negative_attempt(self):
        """Test backoff delay calculation with negative attempt."""
        config = Config(retry_delay=1.0)

        delay = config.calculate_backoff_delay(-1)
        self.assertEqual(delay, config.retry_delay)

    def test_async_request_without_result_event(self):
        """Test AsyncRequest behavior without result event."""
        request = AsyncRequest({"data": "test"})

        self.assertIsNone(request.result_event)
        self.assertIsNone(request.error)
        self.assertEqual(request.data, {"data": "test"})


if __name__ == "__main__":
    unittest.main()
