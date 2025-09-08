# Integration Testing Guide

This document explains how to run integration tests for the LogFlux Python SDK.

## Overview

The LogFlux Python SDK includes comprehensive integration tests that can run in two modes:

1. **Mock Agent Mode**: Uses a built-in mock LogFlux agent for testing (no external dependencies)
2. **Real Agent Mode**: Tests against a running LogFlux agent instance

## Quick Start

### Running All Tests (Recommended)

```bash
# Run both mock and real agent tests (skips real tests if agent not available)
python tests/integration/run_integration_tests.py --mode=both
```

### Mock Agent Tests Only

```bash
# Run only mock agent tests (no external dependencies)
python tests/integration/run_integration_tests.py --mode=mock
```

### Real Agent Tests Only

```bash
# Run only real agent tests (requires running LogFlux agent)
python tests/integration/run_integration_tests.py --mode=real
```

## Test Modes

### Mock Agent Tests

Mock agent tests create a temporary Unix socket server that simulates the LogFlux agent protocol. These tests:

- Require no external dependencies
- Test real socket communication 
- Validate message formats and protocols
- Test error handling and edge cases
- Run quickly and reliably in CI/CD

**Test Coverage:**
- Basic log sending and receiving
- Batch processing and auto-flush
- Async mode safety and non-blocking behavior
- Circuit breaker functionality
- Python logging handler integration
- Error resilience and graceful degradation
- High volume logging scenarios

### Real Agent Tests

Real agent tests connect to an actual LogFlux agent instance. These tests:

- Require a running LogFlux agent
- Test end-to-end functionality
- Validate real-world scenarios
- Test both Unix socket and TCP connections

## Setup for Real Agent Testing

### Unix Socket Connection (Default)

1. Start the LogFlux agent with Unix socket enabled
2. Ensure the socket is created at `/tmp/logflux-agent.sock` (default path)

```bash
# Check if agent is available
python tests/integration/run_integration_tests.py --check-agent
```

### TCP Connection

For TCP testing, set environment variables:

```bash
export LOGFLUX_TCP_HOST="localhost"
export LOGFLUX_TCP_PORT="8080"
export LOGFLUX_SHARED_SECRET="your-secret-key"  # Optional

python tests/integration/run_integration_tests.py --mode=real
```

Or use command line arguments:

```bash
python tests/integration/run_integration_tests.py \
    --mode=real \
    --tcp-host=localhost \
    --tcp-port=8080 \
    --shared-secret=your-secret-key
```

### Custom Socket Path

```bash
python tests/integration/run_integration_tests.py \
    --mode=real \
    --socket-path=/custom/path/logflux-agent.sock
```

## Running Individual Test Files

### Run Mock Agent Tests Directly

```bash
python -m pytest tests/integration/test_mock_agent.py -v
```

### Run Real Agent Tests Directly

```bash
# Set environment variables if needed
export LOGFLUX_SOCKET="/tmp/logflux-agent.sock"

python -m pytest tests/integration/test_integration.py -v
```

### Run Specific Test Classes

```bash
# Mock agent tests only
python -m pytest tests/integration/test_mock_agent.py::TestMockAgentIntegration -v

# Real agent tests only  
python -m pytest tests/integration/test_integration.py::TestIntegration -v

# Python logging integration tests
python -m pytest tests/integration/test_integration.py::TestIntegrationWithLogging -v
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOGFLUX_SOCKET` | Unix socket path for LogFlux agent | `/tmp/logflux-agent.sock` |
| `LOGFLUX_TCP_HOST` | TCP host for LogFlux agent | Not set (skips TCP tests) |
| `LOGFLUX_TCP_PORT` | TCP port for LogFlux agent | Not set (skips TCP tests) |
| `LOGFLUX_SHARED_SECRET` | Shared secret for TCP authentication | Not set (optional) |

## CI/CD Integration

The GitHub Actions workflow automatically runs:

1. **Lint and Format Check**: Code quality validation
2. **Unit Tests**: Core functionality tests across Python versions
3. **Mock Integration Tests**: Socket communication tests
4. **Security Scan**: Dependency vulnerability checks
5. **Build Validation**: Package build and validation

Real agent tests are skipped in CI/CD since no LogFlux agent is running in the GitHub Actions environment.

## Troubleshooting

### "LogFlux agent not found" Error

```bash
# Check if the socket file exists
ls -la /tmp/logflux-agent.sock

# Check if agent is responsive
python tests/integration/run_integration_tests.py --check-agent
```

### "Connection refused" Error

1. Verify the LogFlux agent is running
2. Check the socket path is correct
3. Ensure proper permissions on the socket file
4. For TCP: verify host, port, and firewall settings

### Permission Issues

```bash
# Check socket permissions
ls -la /tmp/logflux-agent.sock

# The socket should be readable/writable by your user
```

### Mock Tests Failing

Mock tests should never fail due to external dependencies. If they fail:

1. Check for port conflicts (mock agent uses random socket paths)
2. Verify no firewall blocking local socket creation
3. Check available disk space in `/tmp`

## Test Output Examples

### Successful Mock Tests
```
🤖 Running integration tests with mock LogFlux agent...
tests/integration/test_mock_agent.py::TestMockAgentIntegration::test_basic_log_sending PASSED
tests/integration/test_mock_agent.py::TestMockAgentIntegration::test_batch_processing PASSED
...
Mock agent tests passed
```

### Successful Real Agent Tests
```
Running integration tests with real LogFlux agent...
tests/integration/test_integration.py::TestIntegration::test_connectivity PASSED
tests/integration/test_integration.py::TestIntegration::test_ping PASSED
...
Real agent tests passed
```

### Agent Not Available
```
WARNING: LogFlux agent not available at /tmp/logflux-agent.sock
   Skipping real agent tests
```

## Best Practices

1. **Always run mock tests first** - they're faster and catch most issues
2. **Use real agent tests for final validation** before releases
3. **Set up proper LogFlux agent configuration** for comprehensive testing
4. **Monitor test performance** - integration tests should complete quickly
5. **Check CI/CD logs** for any mock test failures that need investigation

For more details on the LogFlux Python SDK, see the main [README](../README.md) and [API documentation](api.md).