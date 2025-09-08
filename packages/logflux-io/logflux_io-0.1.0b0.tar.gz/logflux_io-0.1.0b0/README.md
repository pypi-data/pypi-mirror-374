# LogFlux Python SDK (BETA)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE-APACHE-2.0)
[![GitHub issues](https://img.shields.io/github/issues/logflux-io/logflux-python-sdk)](https://github.com/logflux-io/logflux-python-sdk/issues)

> **BETA SOFTWARE**: This SDK is feature-complete for basic logging use cases but is marked as BETA while we gather community feedback and add additional features. The API is stable but may evolve based on user needs.

A lightweight Python SDK for communicating with the LogFlux agent.

## Installation

Install from PyPI:

```bash
pip install logflux-io
```

For development:

```bash
git clone https://github.com/logflux-io/logflux-python-sdk.git
cd logflux-python-sdk
pip install -e .[dev]
```

## Current Status

- **Stable API** for core logging functionality
- **Production quality** code and testing  
- **Ready for evaluation** and non-critical use cases
- **Additional features** (metrics, traces, events) coming soon
- **Gathering feedback** for API refinements

## Package Structure

```
logflux/
├── types.py          # Core types (LogEntry, LogBatch, etc.)
├── client.py         # Client implementation (Client class)
├── batch.py          # Batch client for high-throughput logging
├── config.py         # Configuration management
└── integrations/     # Logger integrations
    └── logging_handler.py  # Python logging integration
examples/             # Usage examples
├── basic/            # Basic client usage
├── batch/            # Batch client usage
├── config/           # Configuration examples
└── integrations/     # Integration examples
    └── logging/      # Python logging integration
```

## Quick Start

```python
import logflux

# Create client - async mode enabled by default for non-blocking sends
client = logflux.new_unix_client("/tmp/logflux-agent.sock")
client.connect()

# Send log entry (non-blocking with circuit breaker protection)
entry = (logflux.new_log_entry("Hello, LogFlux!", "my-app")
         .with_log_level(logflux.LEVEL_INFO)
         .with_metadata("environment", "production"))

client.send_log_entry(entry)
client.close()
```

## Installation

```bash
# Install from PyPI (when available)
pip install logflux

# Install from source
pip install -e .
```

## Examples

### Basic Usage

```python
import logflux

client = logflux.new_unix_client("/tmp/logflux-agent.sock")
client.connect()

entry = (logflux.new_log_entry("User authenticated", "auth-service")
         .with_log_level(logflux.LEVEL_INFO)
         .with_metadata("user_id", "12345"))

client.send_log_entry(entry)
client.close()
```

### Batch Processing

```python
import logflux

batch_config = logflux.BatchConfig(max_batch_size=10, auto_flush=True)
client = logflux.new_batch_unix_client("/tmp/logflux-agent.sock", batch_config)
client.connect()

for i in range(25):
    entry = logflux.new_log_entry(f"Log entry {i}", "batch-app")
    client.send_log_entry(entry)

client.close()
```

### Python Logging Integration

```python
import logging
import logflux
from logflux.integrations import LogFluxHandler

client = logflux.new_unix_client("/tmp/logflux-agent.sock")
client.connect()

handler = LogFluxHandler(client=client, source="my-app", json_format=True)
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

logger.info("Application started", extra={"version": "1.0.0"})
handler.close()
```

## Security

The LogFlux Python SDK prioritizes security and undergoes comprehensive automated security scanning:

### Continuous Security Monitoring

- **Static Analysis**: Bandit scans for security vulnerabilities in code
- **Dependency Scanning**: Safety checks for known vulnerabilities in dependencies  
- **Advanced Pattern Analysis**: Semgrep detects security anti-patterns and OWASP issues
- **Secrets Detection**: Automated scanning for hardcoded credentials and sensitive data
- **Supply Chain Security**: Package integrity verification and suspicious dependency detection

### Security Scans Run On:
- Every pull request and code change
- Weekly scheduled comprehensive scans
- All releases and deployments

### Security Features
- Zero production dependencies (eliminates attack surface)
- Defensive programming with comprehensive error handling
- No credential storage or sensitive data processing
- Safe defaults and input validation
- Resource cleanup and timeout protection

For security reports or to report vulnerabilities, see [SECURITY.md](SECURITY.md).

## License

This project is licensed under the Apache License 2.0. See [LICENSE-APACHE-2.0](LICENSE-APACHE-2.0) for details.
