#!/usr/bin/env python3
"""
Configuration example for LogFlux Python SDK.

This example demonstrates various configuration options
for the LogFlux Python SDK client.
"""

import time

import logflux


def main():
    """Main function demonstrating configuration options."""
    # Create a custom configuration
    config = logflux.Config(
        network="unix",
        address="/tmp/logflux-agent.sock",
        timeout=5.0,
        max_retries=2,
        retry_delay=0.5,
        max_retry_delay=2.0,
        retry_multiplier=1.5,
        jitter_percent=0.2,
        async_mode=True,
        channel_buffer=500,
        circuit_breaker_threshold=3,
        circuit_breaker_timeout=10.0,
    )

    # Create client with custom configuration
    client = logflux.Client(config)

    try:
        # Connect to the agent
        client.connect()
        print("Connected with custom configuration")

        # Send some logs to test the configuration
        for i in range(5):
            entry = (
                logflux.new_log_entry(f"Config test log #{i+1}", "config-example")
                .with_log_level(logflux.LEVEL_INFO)
                .with_metadata("test_type", "configuration")
            )

            client.send_log_entry(entry)
            print(f"Sent log entry #{i+1}")

            # Show circuit breaker stats
            cb_stats = client.get_circuit_breaker_stats()
            print(f"  Circuit breaker: {cb_stats['state']}, failures: {cb_stats['failure_count']}")

        print("\nWaiting for async processing...")
        time.sleep(1)

        # Test ping functionality
        try:
            pong = client.ping()
            print(f"Ping successful: {pong.status}")
        except Exception as e:
            print(f"Ping failed: {e}")

    except Exception as e:
        print(f"Error: {e}")
        # Show circuit breaker stats on error
        cb_stats = client.get_circuit_breaker_stats()
        print(f"Circuit breaker stats: {cb_stats}")
    finally:
        # Always close the client
        client.close()
        print("Custom configured client closed")


def tcp_example():
    """Example using TCP configuration with authentication."""
    print("\n--- TCP Configuration Example ---")

    # Create TCP configuration with shared secret
    config = logflux.Config(
        network="tcp",
        address="localhost:8080",
        shared_secret="your-secret-key-here",
        timeout=10.0,
        async_mode=False,  # Use sync mode for TCP example
    )

    client = logflux.Client(config)

    try:
        # Connect to the agent
        client.connect()
        print("Connected via TCP")

        # Authenticate (required for TCP)
        auth_response = client.authenticate()
        print(f"Authentication: {auth_response.status} - {auth_response.message}")

        # Send a log entry
        entry = logflux.new_log_entry("TCP log entry", "tcp-example").with_log_level(
            logflux.LEVEL_INFO
        )

        client.send_log_entry(entry)
        print("TCP log entry sent successfully!")

    except Exception as e:
        print(f"TCP Error: {e}")
    finally:
        client.close()
        print("TCP client closed")


if __name__ == "__main__":
    main()
    tcp_example()
