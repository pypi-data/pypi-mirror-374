# Changelog

All notable changes to the LogFlux Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0-beta] - 2024-01-01

### Added
- Initial beta release of LogFlux Python SDK
- Core client functionality for Unix socket and TCP communication
- Async mode with configurable buffering and circuit breaker protection
- Batch processing client for high-throughput logging
- Exponential backoff retry logic with jitter
- Circuit breaker pattern for failure detection and recovery
- Python logging framework integration via LogFluxHandler
- Comprehensive test suite with unit and integration tests
- Complete documentation and examples
- CI/CD pipeline with GitHub Actions
- Support for Python 3.8+

### Features
- **Client Types**:
  - `Client` - Core client with sync/async modes
  - `BatchClient` - Automatic batching for high throughput
  
- **Transport Support**:
  - Unix socket communication (default)
  - TCP communication with shared secret authentication
  
- **Reliability Features**:
  - Circuit breaker pattern
  - Exponential backoff with jitter
  - Automatic retry logic
  - Connection pooling and management
  
- **Integration**:
  - Python standard logging integration
  - Structured JSON logging support
  - Metadata and context support
  
- **Configuration**:
  - Flexible configuration system
  - Environment-based configuration
  - Reasonable defaults for all settings

### API
- `logflux.Client` - Main client class
- `logflux.BatchClient` - Batching client wrapper  
- `logflux.Config` - Configuration management
- `logflux.LogEntry` - Log entry data structure
- `logflux.integrations.LogFluxHandler` - Logging integration
- Factory functions: `new_unix_client()`, `new_tcp_client()`, etc.

### Known Limitations
- Integration tests require manual LogFlux agent setup
- API may evolve based on community feedback
- Additional payload types (metrics, traces, events) not yet supported

[Unreleased]: https://github.com/logflux-io/logflux-python-sdk/compare/v0.1.0-beta...HEAD
[0.1.0-beta]: https://github.com/logflux-io/logflux-python-sdk/releases/tag/v0.1.0-beta