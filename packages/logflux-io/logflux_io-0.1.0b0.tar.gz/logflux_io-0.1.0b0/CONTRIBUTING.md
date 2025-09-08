# Contributing to LogFlux Python SDK

Thank you for your interest in contributing to the LogFlux Python SDK! This document provides guidelines and information for contributors.

## Getting Started

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/logflux-io/logflux-python-sdk.git
cd logflux-python-sdk
```

2. Set up a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
make install-dev
# or
pip install -e .[dev]
```

### Development Workflow

1. Create a new branch for your feature/fix:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes following the coding standards (see below)

3. Run tests and linting:
```bash
make test
make lint
make format
```

4. Commit your changes:
```bash
git add .
git commit -m "feat: your descriptive commit message"
```

5. Push and create a pull request

## Coding Standards

### Python Style
- Follow PEP 8 style guidelines
- Use Black for code formatting (line length: 100)
- Use isort for import sorting
- Use type hints for all functions and methods

### Code Quality
- Write comprehensive tests for new functionality
- Maintain high test coverage (>90%)
- Follow existing patterns and architecture
- Document public APIs with docstrings

### Commit Messages
Follow conventional commit format:
- `feat:` new features
- `fix:` bug fixes
- `docs:` documentation changes
- `test:` test-related changes
- `refactor:` code refactoring
- `chore:` maintenance tasks

## Testing

### Running Tests
```bash
# Unit tests only
make test

# With coverage
make test-cov

# Integration tests (requires LogFlux agent)
make test-integration

# All tests
make test-all
```

### Writing Tests
- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Follow existing test patterns
- Use descriptive test names
- Test edge cases and error conditions

## Pull Request Guidelines

### Before Submitting
- Ensure all tests pass
- Run linting and formatting tools
- Update documentation if needed
- Add tests for new functionality

### PR Description
Include:
- Clear description of changes
- Motivation and context
- Testing performed
- Breaking changes (if any)
- Related issues

## Code Review Process

1. All PRs require at least one review
2. Address review feedback promptly
3. Keep PRs focused and reasonably sized
4. Maintain backwards compatibility when possible

## Development Tools

### Available Make Targets
```bash
make help          # Show all available targets
make install       # Install package
make install-dev   # Install with dev dependencies
make test          # Run unit tests
make test-cov      # Run tests with coverage
make lint          # Run linting
make format        # Format code
make clean         # Clean build artifacts
make dist          # Build distribution packages
```

### IDE Configuration
For VS Code users, recommended extensions:
- Python
- Pylance
- Black Formatter
- isort

## Issue Reporting

When reporting issues, include:
- Python version
- LogFlux Python SDK version
- Minimal reproduction code
- Error messages and stack traces
- Expected vs actual behavior

## Security

If you discover a security vulnerability, please email security@logflux.io instead of opening a public issue.

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

## Questions?

- Open a discussion on GitHub
- Check existing issues and documentation
- Email support@logflux.io for general questions

Thank you for contributing!