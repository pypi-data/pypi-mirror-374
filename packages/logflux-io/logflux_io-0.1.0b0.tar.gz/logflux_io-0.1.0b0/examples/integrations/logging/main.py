#!/usr/bin/env python3
"""
Python logging integration example.

This example demonstrates how to integrate LogFlux with Python's
standard logging framework.
"""

import logging
import time

import logflux
from logflux.integrations import LogFluxHandler


def main():
    """Main function demonstrating logging integration."""
    # Create a LogFlux client
    client = logflux.new_unix_client("/tmp/logflux-agent.sock")

    try:
        # Connect to the agent
        client.connect()
        print("Connected to LogFlux agent")

        # Create a LogFlux handler
        handler = LogFluxHandler(
            client=client,
            source="logging-example",
            include_extra=True,
            include_stack_info=True,
            json_format=False,
        )
        handler.setLevel(logging.DEBUG)

        # Set up formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        # Configure root logger
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        # Also add console handler for local output
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        print("Logging integration set up successfully")

        # Test different log levels
        logging.debug("This is a debug message")
        logging.info("This is an info message")
        logging.warning("This is a warning message")
        logging.error("This is an error message")
        logging.critical("This is a critical message")

        # Test logging with extra context
        logger.info(
            "User logged in",
            extra={"user_id": 12345, "username": "john.doe", "ip_address": "192.168.1.100"},
        )

        # Test exception logging
        try:
            raise ValueError("This is a test exception")
        except Exception:
            logger.exception("Caught an exception")

        # Test different loggers
        auth_logger = logging.getLogger("auth")
        auth_logger.info("Authentication successful")

        api_logger = logging.getLogger("api")
        api_logger.warning("Rate limit approaching")

        db_logger = logging.getLogger("database")
        db_logger.error("Connection timeout")

        print("All log messages sent successfully!")

        # Wait a bit for async processing
        time.sleep(1)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the handler and client
        handler.close()
        print("Logging integration closed")


def batch_logging_example():
    """Example using batch client with logging integration."""
    print("\n--- Batch Logging Example ---")

    # Create a batch client for better performance
    batch_config = logflux.BatchConfig(max_batch_size=5, flush_interval=2.0, auto_flush=True)

    batch_client = logflux.new_batch_unix_client("/tmp/logflux-agent.sock", batch_config)

    try:
        batch_client.connect()
        print("Connected with batch client")

        # Create handler with JSON formatting
        handler = LogFluxHandler(
            client=batch_client,
            source="batch-logging-example",
            json_format=True,
            include_extra=True,
        )

        # Set up a logger for this example
        batch_logger = logging.getLogger("batch_example")
        batch_logger.setLevel(logging.INFO)
        batch_logger.addHandler(handler)

        # Send multiple log messages
        for i in range(8):
            batch_logger.info(
                f"Batch log message #{i+1}", extra={"sequence": i + 1, "batch_id": "example_001"}
            )
            time.sleep(0.1)

        print("Batch logging messages sent")

        # Wait for batch processing
        time.sleep(3)

    except Exception as e:
        print(f"Batch logging error: {e}")
    finally:
        batch_client.close()
        print("Batch client closed")


if __name__ == "__main__":
    main()
    batch_logging_example()
