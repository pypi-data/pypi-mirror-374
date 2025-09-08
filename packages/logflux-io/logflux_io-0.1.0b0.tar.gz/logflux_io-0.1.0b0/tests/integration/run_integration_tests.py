#!/usr/bin/env python3
"""
Integration test runner script.

This script helps run integration tests with various configurations,
including mock agent tests and real agent tests.
"""

import argparse
import os
import socket as sock
import subprocess
import sys
from pathlib import Path


def run_mock_tests():
    """Run integration tests with mock agent."""
    print("🤖 Running integration tests with mock LogFlux agent...")

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/integration/test_mock_agent.py",
        "-v",
        "--tb=short",
    ]

    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent.parent)
    return result.returncode == 0


def run_real_agent_tests(socket_path=None, tcp_host=None, tcp_port=None, shared_secret=None):
    """Run integration tests with real LogFlux agent."""
    print("Running Running integration tests with real LogFlux agent...")

    # Set environment variables for real agent tests
    env = os.environ.copy()

    if socket_path:
        env["LOGFLUX_SOCKET"] = socket_path
    if tcp_host:
        env["LOGFLUX_TCP_HOST"] = tcp_host
    if tcp_port:
        env["LOGFLUX_TCP_PORT"] = str(tcp_port)
    if shared_secret:
        env["LOGFLUX_SHARED_SECRET"] = shared_secret

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/integration/test_integration.py",
        "-v",
        "--tb=short",
    ]

    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent.parent, env=env)
    return result.returncode == 0


def check_agent_available(socket_path="/tmp/logflux-agent.sock"):
    """Check if LogFlux agent is available."""
    if not os.path.exists(socket_path):
        return False

    try:
        s = sock.socket(sock.AF_UNIX, sock.SOCK_STREAM)
        s.settimeout(1.0)
        s.connect(socket_path)
        s.close()
        return True
    except Exception:
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run LogFlux Python SDK integration tests")

    parser.add_argument(
        "--mode",
        choices=["mock", "real", "both"],
        default="both",
        help="Test mode: mock agent only, real agent only, or both",
    )

    parser.add_argument(
        "--socket-path",
        default="/tmp/logflux-agent.sock",
        help="Unix socket path for LogFlux agent",
    )

    parser.add_argument("--tcp-host", help="TCP host for LogFlux agent")

    parser.add_argument("--tcp-port", type=int, help="TCP port for LogFlux agent")

    parser.add_argument("--shared-secret", help="Shared secret for TCP authentication")

    parser.add_argument(
        "--check-agent", action="store_true", help="Check if LogFlux agent is available and exit"
    )

    args = parser.parse_args()

    # Check agent availability if requested
    if args.check_agent:
        if check_agent_available(args.socket_path):
            print(f"Success: LogFlux agent is available at {args.socket_path}")
            return 0
        else:
            print(f"Error: LogFlux agent is not available at {args.socket_path}")
            return 1

    success = True

    # Run mock tests
    if args.mode in ["mock", "both"]:
        if not run_mock_tests():
            success = False
            print("Error: Mock agent tests failed")
        else:
            print("Success: Mock agent tests passed")

    # Run real agent tests
    if args.mode in ["real", "both"]:
        agent_available = check_agent_available(args.socket_path)

        if agent_available:
            if not run_real_agent_tests(
                socket_path=args.socket_path,
                tcp_host=args.tcp_host,
                tcp_port=args.tcp_port,
                shared_secret=args.shared_secret,
            ):
                success = False
                print("Error: Real agent tests failed")
            else:
                print("Success: Real agent tests passed")
        else:
            if args.mode == "real":
                print(f"Error: LogFlux agent not available at {args.socket_path}")
                print("   Start the LogFlux agent first or use --mode=mock")
                success = False
            else:
                print(f"Warning:  LogFlux agent not available at {args.socket_path}")
                print("   Skipping real agent tests")

    if success:
        print("\nSuccess: All integration tests completed successfully!")
        return 0
    else:
        print("\nError: Some integration tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
