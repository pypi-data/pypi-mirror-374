#!/usr/bin/env python3
"""
Batch LogFlux Python SDK example.

This example demonstrates batch processing with the LogFlux Python SDK
for high-throughput log collection and sending.
"""

import time

import logflux


def main():
    """Main function demonstrating batch processing."""
    # Create a batch configuration
    batch_config = logflux.BatchConfig(
        max_batch_size=5, flush_interval=2.0, auto_flush=True  # 2 seconds
    )

    # Create a batch client
    client = logflux.new_batch_unix_client("/tmp/logflux-agent.sock", batch_config)

    try:
        # Connect to the agent
        client.connect()
        print("Connected to LogFlux agent with batch processing")

        # Send multiple log entries - they will be batched automatically
        for i in range(12):
            entry = (
                logflux.new_log_entry(f"Batch log entry #{i+1}", "batch-example")
                .with_log_level(logflux.LEVEL_INFO)
                .with_metadata("batch_id", "001")
                .with_metadata("sequence", str(i + 1))
            )

            client.send_log_entry(entry)
            print(f"Queued log entry #{i+1}")

            # Show stats every few entries
            if (i + 1) % 3 == 0:
                stats = client.get_stats()
                print(
                    f"  Batch stats: {stats.pending_entries} pending, "
                    f"max size: {stats.max_batch_size}"
                )

            time.sleep(0.1)  # Small delay to show batching

        print("\nAll entries queued, waiting for auto-flush...")
        time.sleep(3)  # Wait for auto-flush

        # Manual flush of remaining entries
        client.flush()
        print("Manual flush completed")

        # Show final stats
        stats = client.get_stats()
        print(f"Final stats: {stats.pending_entries} pending entries")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Always close the client (flushes remaining entries)
        client.close()
        print("Batch client closed")


if __name__ == "__main__":
    main()
