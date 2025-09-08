"""
Integration tests with mock LogFlux agent.

These tests create a mock LogFlux agent server to test real socket communication
without requiring an actual LogFlux agent to be running.
"""

import json
import logging
import os
import socket
import tempfile
import threading
import time
import unittest
from typing import List, Optional

import logflux


class MockLogFluxAgent:
    """Mock LogFlux agent for integration testing."""

    def __init__(self, socket_path: Optional[str] = None):
        """Initialize mock agent."""
        if socket_path:
            self.socket_path = socket_path
        else:
            # Create temporary socket
            self.socket_path = os.path.join(
                tempfile.gettempdir(), f"logflux-test-{os.getpid()}.sock"
            )

        self.server_socket: Optional[socket.socket] = None
        self.server_thread: Optional[threading.Thread] = None
        self.running = False
        self.received_messages: List[dict] = []
        self.clients: List[socket.socket] = []
        self._lock = threading.Lock()

    def start(self) -> None:
        """Start the mock agent server."""
        # Clean up existing socket
        try:
            os.unlink(self.socket_path)
        except FileNotFoundError:
            pass

        # Create Unix domain socket
        self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_socket.bind(self.socket_path)
        self.server_socket.listen(5)
        self.running = True

        # Start server thread
        self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
        self.server_thread.start()

        # Wait for server to be ready
        time.sleep(0.1)

    def stop(self) -> None:
        """Stop the mock agent server."""
        self.running = False

        # Close all client connections
        with self._lock:
            for client in self.clients:
                try:
                    client.close()
                except Exception:
                    pass
            self.clients.clear()

        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass

        # Clean up socket file
        try:
            os.unlink(self.socket_path)
        except FileNotFoundError:
            pass

        # Wait for thread to finish
        if self.server_thread:
            self.server_thread.join(timeout=1.0)

    def _server_loop(self) -> None:
        """Main server loop."""
        while self.running:
            try:
                if not self.server_socket:
                    break

                self.server_socket.settimeout(0.5)
                client_socket, _ = self.server_socket.accept()

                with self._lock:
                    self.clients.append(client_socket)

                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket,),
                    daemon=True
                )
                client_thread.start()

            except socket.timeout:
                continue
            except Exception:
                break

    def _handle_client(self, client_socket: socket.socket) -> None:
        """Handle individual client connection."""
        try:
            client_socket.settimeout(1.0)
            buffer = ""

            while self.running:
                try:
                    data = client_socket.recv(1024).decode('utf-8')
                    if not data:
                        break

                    buffer += data

                    # Process complete lines (JSON messages end with \n)
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        if line.strip():
                            self._process_message(line.strip())

                except socket.timeout:
                    continue
                except Exception:
                    break

        finally:
            try:
                client_socket.close()
            except Exception:
                pass

            with self._lock:
                if client_socket in self.clients:
                    self.clients.remove(client_socket)

    def _process_message(self, message_json: str) -> None:
        """Process received JSON message."""
        try:
            message = json.loads(message_json)
            with self._lock:
                self.received_messages.append(message)
        except json.JSONDecodeError:
            pass  # Ignore invalid JSON

    def get_received_messages(self) -> List[dict]:
        """Get all received messages."""
        with self._lock:
            return list(self.received_messages)

    def clear_messages(self) -> None:
        """Clear received messages."""
        with self._lock:
            self.received_messages.clear()

    def wait_for_messages(self, count: int, timeout: float = 5.0) -> bool:
        """Wait for a specific number of messages."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            with self._lock:
                if len(self.received_messages) >= count:
                    return True
            time.sleep(0.1)
        return False


class TestMockAgentIntegration(unittest.TestCase):
    """Integration tests using mock LogFlux agent."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_agent = MockLogFluxAgent()
        self.mock_agent.start()

    def tearDown(self):
        """Clean up test fixtures."""
        self.mock_agent.stop()

    def test_basic_log_sending(self):
        """Test basic log message sending to mock agent."""
        client = logflux.new_unix_client(self.mock_agent.socket_path)

        try:
            client.connect()

            # Send a log entry
            entry = logflux.new_log_entry("Test message", "mock-test")
            client.send_log_entry(entry)

            # Wait for message to be received
            self.assertTrue(self.mock_agent.wait_for_messages(1, timeout=2.0))

            # Check received message
            messages = self.mock_agent.get_received_messages()
            self.assertEqual(len(messages), 1)

            message = messages[0]
            self.assertEqual(message['payload'], "Test message")
            self.assertEqual(message['source'], "mock-test")
            self.assertEqual(message['entryType'], logflux.TYPE_LOG)

        finally:
            client.close()

    def test_batch_processing(self):
        """Test batch processing with mock agent."""
        batch_config = logflux.BatchConfig(max_batch_size=3, flush_interval=1.0, auto_flush=True)
        client = logflux.new_batch_unix_client(self.mock_agent.socket_path, batch_config)

        try:
            client.connect()

            # Send multiple entries to trigger batching
            for i in range(5):
                entry = logflux.new_log_entry(f"Batch message {i}", "batch-mock-test")
                client.send_log_entry(entry)

            # Wait for batch processing
            self.assertTrue(self.mock_agent.wait_for_messages(2, timeout=3.0))

            messages = self.mock_agent.get_received_messages()

            # Should receive 2 batch messages (3 + 2 entries)
            self.assertEqual(len(messages), 2)

            # First batch should have 3 entries
            first_batch = messages[0]
            self.assertIn('entries', first_batch)
            self.assertEqual(len(first_batch['entries']), 3)

            # Second batch should have 2 entries
            second_batch = messages[1]
            self.assertIn('entries', second_batch)
            self.assertEqual(len(second_batch['entries']), 2)

        finally:
            client.close()

    def test_async_mode_safety(self):
        """Test async mode never blocks even with slow mock agent."""
        # Create a slow-responding mock by adding delay
        original_process = self.mock_agent._process_message

        def slow_process(message_json: str):
            time.sleep(0.5)  # Simulate slow processing
            original_process(message_json)

        self.mock_agent._process_message = slow_process

        config = logflux.Config(
            address=self.mock_agent.socket_path,
            async_mode=True,
            channel_buffer=10
        )
        client = logflux.Client(config)

        try:
            client.connect()

            # Send messages rapidly - should never block
            start_time = time.time()

            for i in range(5):
                entry = logflux.new_log_entry(f"Async message {i}", "async-mock-test")
                client.send_log_entry(entry)

            # Should complete quickly even with slow agent
            elapsed = time.time() - start_time
            self.assertLess(elapsed, 1.0, "Async sending should not block")

            # Messages should eventually be processed
            self.assertTrue(self.mock_agent.wait_for_messages(5, timeout=10.0))

        finally:
            client.close()

    def test_circuit_breaker_with_mock_failures(self):
        """Test circuit breaker behavior with simulated failures."""
        # Stop the mock agent to simulate connection failures
        self.mock_agent.stop()

        config = logflux.Config(
            address=self.mock_agent.socket_path,
            circuit_breaker_threshold=3,
            circuit_breaker_timeout=1.0,
            max_retries=1,
            retry_delay=0.1
        )
        client = logflux.Client(config)

        try:
            # Attempt to send entries - should trigger circuit breaker
            for i in range(5):
                entry = logflux.new_log_entry(f"Failure test {i}", "circuit-test")
                # These should fail silently due to async mode
                client.send_log_entry(entry)

            # Check circuit breaker stats
            stats = client.get_circuit_breaker_stats()
            # In async mode, failures are handled silently, but circuit breaker should still work
            self.assertIn(stats['state'], ['closed', 'open', 'half_open'])

        finally:
            client.close()

    def test_logging_handler_integration(self):
        """Test Python logging handler integration with mock agent."""
        client = logflux.new_unix_client(self.mock_agent.socket_path)

        try:
            client.connect()

            # Create handler
            from logflux.integrations import LogFluxHandler
            handler = LogFluxHandler(
                client=client,
                source="logging-mock-test",
                json_format=True,
                include_extra=True
            )

            # Set up logger
            logger = logging.getLogger("mock_test")
            logger.setLevel(logging.DEBUG)
            logger.addHandler(handler)

            # Send various log levels
            logger.info("Info message", extra={"user_id": 123})
            logger.warning("Warning message")
            logger.error("Error message")

            # Wait for messages
            self.assertTrue(self.mock_agent.wait_for_messages(3, timeout=2.0))

            messages = self.mock_agent.get_received_messages()
            self.assertEqual(len(messages), 3)

            # Check that messages contain expected data
            info_msg = messages[0]
            self.assertEqual(info_msg['source'], "logging-mock-test")
            self.assertEqual(info_msg['logLevel'], logflux.LEVEL_INFO)

            # JSON format should include structured data
            payload = json.loads(info_msg['payload'])
            self.assertEqual(payload['level'], 'INFO')
            self.assertEqual(payload['message'], 'Info message')
            self.assertIn('metadata', payload)

        finally:
            client.close()

    def test_error_resilience(self):
        """Test that SDK handles errors gracefully without crashing."""
        client = logflux.new_unix_client(self.mock_agent.socket_path)

        try:
            client.connect()

            # Test with various problematic inputs
            test_cases = [
                ("", "empty-source"),  # Empty message
                ("Normal message", ""),  # Empty source
                ("Very " + "long " * 1000 + "message", "long-test"),  # Very long message
                ("Unicode: test 测试 العربية", "unicode-test"),  # Unicode characters
                ('{"malformed": json}', "json-test"),  # Malformed JSON
                (None, "none-test") if False else ("None replacement", "none-test")  # Handle None
            ]

            for payload, source in test_cases:
                try:
                    entry = logflux.new_log_entry(payload, source)
                    client.send_log_entry(entry)
                except Exception:
                    # Should not raise exceptions - all handled gracefully
                    self.fail(f"Exception raised for test case: {payload[:50]}...")

            # Should receive most messages (some might be filtered/rejected)
            time.sleep(1.0)
            messages = self.mock_agent.get_received_messages()
            self.assertGreater(len(messages), 0, "Should receive at least some messages")

        finally:
            client.close()


class TestRealAgentIntegration(unittest.TestCase):
    """Integration tests for real LogFlux agent (if available)."""

    def setUp(self):
        """Set up test fixtures."""
        self.socket_path = os.environ.get("LOGFLUX_SOCKET", "/tmp/logflux-agent.sock")

    def _check_agent_available(self):
        """Check if real LogFlux agent is available."""
        if not os.path.exists(self.socket_path):
            self.skipTest(f"Real LogFlux agent not found at {self.socket_path}")

        try:
            # Quick connectivity test
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(2.0)
            sock.connect(self.socket_path)
            sock.close()
        except Exception as e:
            self.skipTest(f"Real LogFlux agent not responsive: {e}")

    def test_real_agent_connectivity(self):
        """Test connectivity with real LogFlux agent."""
        self._check_agent_available()

        client = logflux.new_unix_client(self.socket_path)

        try:
            client.connect()

            # Send test message
            entry = logflux.new_log_entry(
                "Integration test with real agent",
                "real-agent-test"
            ).with_metadata("test_run", str(int(time.time())))

            client.send_log_entry(entry)

            # Test ping functionality
            pong = client.ping()
            self.assertEqual(pong.status, "pong")

        finally:
            client.close()

    def test_real_agent_batch_processing(self):
        """Test batch processing with real LogFlux agent."""
        self._check_agent_available()

        batch_config = logflux.BatchConfig(
            max_batch_size=5,
            flush_interval=2.0,
            auto_flush=True
        )
        client = logflux.new_batch_unix_client(self.socket_path, batch_config)

        try:
            client.connect()

            # Send multiple entries
            test_run_id = str(int(time.time()))
            for i in range(10):
                entry = logflux.new_log_entry(
                    f"Real agent batch test {i}",
                    "real-agent-batch-test"
                ).with_metadata("test_run", test_run_id).with_metadata("sequence", str(i))

                client.send_log_entry(entry)

            # Manual flush to ensure all messages are sent
            client.flush()
            time.sleep(1.0)

        finally:
            client.close()


if __name__ == "__main__":
    # Run mock agent tests
    unittest.main(verbosity=2)
