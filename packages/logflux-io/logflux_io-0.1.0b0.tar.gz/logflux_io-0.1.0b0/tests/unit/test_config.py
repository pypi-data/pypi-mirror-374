"""
Unit tests for LogFlux config module.
"""

import unittest

from logflux.config import (
    DEFAULT_NETWORK,
    DEFAULT_SOCKET_PATH,
    DEFAULT_TIMEOUT,
    BatchConfig,
    Config,
    default_batch_config,
    default_config,
)


class TestConfig(unittest.TestCase):
    """Test cases for Config class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = Config()

        self.assertEqual(config.network, DEFAULT_NETWORK)
        self.assertEqual(config.address, DEFAULT_SOCKET_PATH)
        self.assertEqual(config.timeout, DEFAULT_TIMEOUT)
        self.assertTrue(config.async_mode)
        self.assertGreater(config.channel_buffer, 0)
        self.assertGreater(config.max_retries, 0)

    def test_custom_config(self):
        """Test custom configuration values."""
        config = Config(
            network="tcp", address="localhost:8080", timeout=5.0, async_mode=False, max_retries=1
        )

        self.assertEqual(config.network, "tcp")
        self.assertEqual(config.address, "localhost:8080")
        self.assertEqual(config.timeout, 5.0)
        self.assertFalse(config.async_mode)
        self.assertEqual(config.max_retries, 1)

    def test_calculate_backoff_delay(self):
        """Test exponential backoff calculation."""
        config = Config(
            retry_delay=0.1,
            retry_multiplier=2.0,
            max_retry_delay=1.0,
            jitter_percent=0.0,  # No jitter for predictable testing
        )

        # First attempt should return base delay
        delay0 = config.calculate_backoff_delay(0)
        self.assertEqual(delay0, 0.1)

        # Second attempt should be doubled
        delay1 = config.calculate_backoff_delay(1)
        self.assertEqual(delay1, 0.2)

        # Third attempt should be doubled again
        delay2 = config.calculate_backoff_delay(2)
        self.assertEqual(delay2, 0.4)

        # Should cap at max_retry_delay
        delay10 = config.calculate_backoff_delay(10)
        self.assertEqual(delay10, 1.0)

    def test_calculate_backoff_delay_with_jitter(self):
        """Test backoff delay calculation with jitter."""
        config = Config(
            retry_delay=1.0, retry_multiplier=2.0, max_retry_delay=10.0, jitter_percent=0.1
        )

        # With jitter, delays should vary but stay within bounds
        delays = [config.calculate_backoff_delay(1) for _ in range(10)]

        # All delays should be at least the base retry_delay
        for delay in delays:
            self.assertGreaterEqual(delay, config.retry_delay)

        # Should have some variation due to jitter
        self.assertGreater(max(delays) - min(delays), 0)


class TestBatchConfig(unittest.TestCase):
    """Test cases for BatchConfig class."""

    def test_default_batch_config(self):
        """Test default batch configuration."""
        config = BatchConfig()

        self.assertGreater(config.max_batch_size, 0)
        self.assertGreater(config.flush_interval, 0)
        self.assertTrue(config.auto_flush)

    def test_custom_batch_config(self):
        """Test custom batch configuration."""
        config = BatchConfig(max_batch_size=50, flush_interval=1.0, auto_flush=False)

        self.assertEqual(config.max_batch_size, 50)
        self.assertEqual(config.flush_interval, 1.0)
        self.assertFalse(config.auto_flush)


class TestFactoryFunctions(unittest.TestCase):
    """Test cases for factory functions."""

    def test_default_config_factory(self):
        """Test default_config factory function."""
        config = default_config()

        self.assertIsInstance(config, Config)
        self.assertEqual(config.network, DEFAULT_NETWORK)

    def test_default_batch_config_factory(self):
        """Test default_batch_config factory function."""
        config = default_batch_config()

        self.assertIsInstance(config, BatchConfig)
        self.assertTrue(config.auto_flush)


if __name__ == "__main__":
    unittest.main()
