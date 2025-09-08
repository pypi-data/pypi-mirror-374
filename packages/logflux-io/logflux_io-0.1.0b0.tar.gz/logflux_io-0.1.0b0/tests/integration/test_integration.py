"""
Integration tests for LogFlux Python SDK.

These tests require a running LogFlux agent and test real communication
with the agent over Unix sockets and TCP connections.
"""

import os
import socket
import time
import unittest

import logflux


class TestIntegration(unittest.TestCase):
    """Integration tests requiring a live LogFlux agent."""

    def setUp(self):
        """Set up test fixtures."""
        self.socket_path = os.environ.get("LOGFLUX_SOCKET", "/tmp/logflux-agent.sock")

    def _check_agent_available(self):
        """Check if LogFlux agent is available."""
        if not os.path.exists(self.socket_path):
            self.skipTest(f"LogFlux agent socket not found at {self.socket_path}")

        try:
            # Quick socket test to see if agent is responsive
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(1.0)
            sock.connect(self.socket_path)
            sock.close()
        except Exception as e:
            self.skipTest(f"LogFlux agent not responsive: {e}")

    def test_connectivity(self):
        """Test basic connectivity to LogFlux agent."""
        self._check_agent_available()

        client = logflux.new_unix_client(self.socket_path)

        try:
            client.connect()

            # Send a simple log entry
            entry = logflux.new_log_entry("Integration test message", "integration-test")
            client.send_log_entry(entry)

            # Test should complete without errors

        finally:
            client.close()

    def test_ping(self):
        """Test ping functionality."""
        self._check_agent_available()

        client = logflux.new_unix_client(self.socket_path)

        try:
            client.connect()

            # Send ping
            pong = client.ping()
            self.assertEqual(pong.status, "pong")

        finally:
            client.close()

    def test_batch_sending(self):
        """Test batch log sending."""
        self._check_agent_available()

        batch_config = logflux.BatchConfig(max_batch_size=5, flush_interval=1.0, auto_flush=True)

        client = logflux.new_batch_unix_client(self.socket_path, batch_config)

        try:
            client.connect()

            # Send multiple entries
            for i in range(12):
                entry = (
                    logflux.new_log_entry(f"Batch test message {i}", "batch-integration-test")
                    .with_metadata("test_id", "batch_test")
                    .with_metadata("sequence", str(i))
                )
                client.send_log_entry(entry)

            # Wait for batches to flush
            time.sleep(2.0)

            # Manual flush
            client.flush()

        finally:
            client.close()

    def test_async_mode(self):
        """Test async mode functionality."""
        self._check_agent_available()

        config = logflux.Config(address=self.socket_path, async_mode=True, channel_buffer=100)

        client = logflux.Client(config)

        try:
            client.connect()

            # Send entries in async mode
            for i in range(10):
                entry = (
                    logflux.new_log_entry(f"Async test message {i}", "async-integration-test")
                    .with_metadata("test_id", "async_test")
                    .with_metadata("sequence", str(i))
                )
                client.send_log_entry(entry)

            # Wait for async processing
            time.sleep(1.0)

        finally:
            client.close()

    def test_tcp_connection(self):
        """Test TCP connection to LogFlux agent."""
        # Skip if TCP testing is not configured
        tcp_host = os.environ.get("LOGFLUX_TCP_HOST", "")
        tcp_port = int(os.environ.get("LOGFLUX_TCP_PORT", "0"))

        if not tcp_host or not tcp_port:
            self.skipTest("TCP connection details not configured")

        client = logflux.new_tcp_client(tcp_host, tcp_port)

        try:
            client.connect()

            # Test authentication if shared secret is provided
            shared_secret = os.environ.get("LOGFLUX_SHARED_SECRET", "")
            if shared_secret:
                auth_response = client.authenticate()
                self.assertEqual(auth_response.status, "success")

            # Send test message
            entry = logflux.new_log_entry("TCP integration test", "tcp-integration-test")
            client.send_log_entry(entry)

        finally:
            client.close()

    def test_circuit_breaker_recovery(self):
        """Test circuit breaker recovery after connection issues."""
        self._check_agent_available()

        config = logflux.Config(
            address=self.socket_path,
            circuit_breaker_threshold=2,
            circuit_breaker_timeout=1.0,
            max_retries=1,
        )

        client = logflux.Client(config)

        try:
            client.connect()

            # Send a normal message first
            entry = logflux.new_log_entry("Normal message", "circuit-test")
            client.send_log_entry(entry)

            # Check circuit breaker is closed
            stats = client.get_circuit_breaker_stats()
            self.assertEqual(stats["state"], "closed")

            # The circuit breaker functionality is tested in unit tests
            # Here we just verify it's working normally

        finally:
            client.close()

    def test_high_volume_logging(self):
        """Test high volume log sending."""
        self._check_agent_available()

        batch_config = logflux.BatchConfig(
            max_batch_size=50,
            flush_interval=1.0,
            auto_flush=True
        )
        client = logflux.new_batch_unix_client(self.socket_path, batch_config)

        try:
            client.connect()

            # Send high volume of logs
            start_time = time.time()
            for i in range(500):
                entry = logflux.new_log_entry(
                    f"High volume test message {i}",
                    "high-volume-test"
                ).with_metadata("sequence", str(i)).with_metadata("batch", str(i // 50))

                client.send_log_entry(entry)

            # Should complete quickly due to async processing
            elapsed = time.time() - start_time
            self.assertLess(elapsed, 5.0, "High volume sending should be efficient")

            # Manual flush and wait
            client.flush()
            time.sleep(2.0)

        finally:
            client.close()

    def test_connection_resilience(self):
        """Test connection resilience and recovery."""
        self._check_agent_available()

        config = logflux.Config(
            address=self.socket_path,
            max_retries=3,
            retry_delay=0.1,
            circuit_breaker_threshold=5,
            circuit_breaker_timeout=2.0
        )
        client = logflux.Client(config)

        try:
            client.connect()

            # Send initial message
            entry = logflux.new_log_entry("Before disconnection", "resilience-test")
            client.send_log_entry(entry)

            # Simulate brief disconnection by closing and reopening connection
            # The client should handle this gracefully due to retry logic
            old_socket = client.socket
            if old_socket:
                old_socket.close()
                client.socket = None

            # Send another message - should trigger reconnection
            entry = logflux.new_log_entry("After reconnection", "resilience-test")
            client.send_log_entry(entry)

            time.sleep(1.0)

        finally:
            client.close()

    def test_structured_logging(self):
        """Test structured JSON logging."""
        self._check_agent_available()

        client = logflux.new_unix_client(self.socket_path)

        try:
            client.connect()

            # Send JSON structured log
            json_payload = (
                '{"event": "integration_test", "user_id": 12345, '
                '"action": "login", "success": true}'
            )
            entry = (
                logflux.new_log_entry(json_payload, "structured-test")
                .with_log_level(logflux.LEVEL_INFO)
                .with_metadata("format", "json")
                .with_metadata("test_type", "structured")
            )

            client.send_log_entry(entry)

            # Verify payload type was auto-detected as JSON
            self.assertEqual(entry.payload_type, logflux.PAYLOAD_TYPE_GENERIC_JSON)

        finally:
            client.close()


class TestIntegrationWithLogging(unittest.TestCase):
    """Integration tests for Python logging integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.socket_path = os.environ.get("LOGFLUX_SOCKET", "/tmp/logflux-agent.sock")

    def _check_agent_available(self):
        """Check if LogFlux agent is available."""
        if not os.path.exists(self.socket_path):
            self.skipTest(f"LogFlux agent socket not found at {self.socket_path}")

    def test_logging_integration(self):
        """Test Python logging framework integration."""
        self._check_agent_available()

        import logging

        from logflux.integrations import LogFluxHandler

        client = logflux.new_unix_client(self.socket_path)

        try:
            client.connect()

            # Create LogFlux handler
            handler = LogFluxHandler(
                client=client,
                source="logging-integration-test",
                json_format=False,
                include_extra=True,
            )

            # Set up logger
            logger = logging.getLogger("integration_test")
            logger.setLevel(logging.DEBUG)
            logger.addHandler(handler)

            # Send various log levels
            logger.debug("Debug message from integration test")
            logger.info("Info message from integration test", extra={"user_id": "test_user"})
            logger.warning("Warning message from integration test")
            logger.error("Error message from integration test")

            # Test exception logging
            try:
                raise ValueError("Test exception for logging")
            except Exception:
                logger.exception("Exception caught in integration test")

            # Wait for processing
            time.sleep(0.5)

        finally:
            client.close()


if __name__ == "__main__":
    # Only run integration tests if agent is available
    socket_path = os.environ.get("LOGFLUX_SOCKET", "/tmp/logflux-agent.sock")
    if os.path.exists(socket_path):
        unittest.main()
    else:
        print(f"LogFlux agent not found at {socket_path}. Skipping integration tests.")
        print("Start the LogFlux agent first to run integration tests.")
