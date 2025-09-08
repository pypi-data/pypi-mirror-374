#!/usr/bin/env python3
"""
Basic LogFlux Python SDK example.

This example demonstrates basic usage of the LogFlux Python SDK
for sending log entries to the LogFlux agent.
"""

import logflux


def main():
    """Main function demonstrating basic SDK usage."""
    # Create a simple client (connects to /tmp/logflux-agent.sock by default)
    client = logflux.new_unix_client("/tmp/logflux-agent.sock")

    try:
        # Connect to the agent
        client.connect()
        print("Connected to LogFlux agent")

        # Send a log entry using the fluent API
        entry = (
            logflux.new_log_entry("Hello, LogFlux!", "example-app")
            .with_log_level(logflux.LEVEL_INFO)
            .with_source("basic-example")
            .with_metadata("environment", "development")
            .with_metadata("version", "1.0.0")
        )

        client.send_log_entry(entry)
        print("Log entry sent successfully!")

        # Send a simple log message
        client.send_log("This is a simple log message", "basic-example")
        print("Simple log message sent successfully!")

        # Send a JSON log
        json_log = '{"event": "user_login", "user_id": 12345, "timestamp": "2024-01-01T12:00:00Z"}'
        json_entry = logflux.new_log_entry(json_log, "auth-service").with_log_level(
            logflux.LEVEL_INFO
        )
        client.send_log_entry(json_entry)
        print("JSON log entry sent successfully!")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Always close the client
        client.close()
        print("Connection closed")


if __name__ == "__main__":
    main()
