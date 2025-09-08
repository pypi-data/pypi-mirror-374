# LogFlux Python SDK Makefile
# Central build automation for all tasks

# Variables
PYTHON := python3
PIP := pip3
PYTEST := pytest
BLACK := black
FLAKE8 := flake8
ISORT := isort
MYPY := mypy

# Directories
SRC_DIR := logflux
TEST_DIR := tests
EXAMPLES_DIR := examples
DOCS_DIR := docs
BIN_DIR := bin
TMP_DIR := tmp

# Default target
.PHONY: all
all: install test lint format

# Help target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  all           - Install dependencies, run tests, and lint"
	@echo "  install       - Install package and dependencies"
	@echo "  install-dev   - Install package with development dependencies"
	@echo "  test          - Run unit tests"
	@echo "  test-cov      - Run tests with coverage"
	@echo "  test-integration - Run integration tests"
	@echo "  test-all      - Run unit and integration tests"
	@echo "  lint          - Run linting (flake8, mypy)"
	@echo "  format        - Format code (black, isort)"
	@echo "  format-check  - Check code formatting"
	@echo "  clean         - Clean build artifacts"
	@echo "  dist          - Build distribution packages"
	@echo "  docs          - Generate documentation"
	@echo "  examples      - Run example scripts"

# Installation targets
.PHONY: install
install:
	$(PIP) install -e .

.PHONY: install-dev
install-dev:
	$(PIP) install -e .[dev]

# Test targets
.PHONY: test
test:
	$(PYTEST) $(TEST_DIR)/unit/ -v

.PHONY: test-cov
test-cov:
	$(PYTEST) $(TEST_DIR)/unit/ --cov=$(SRC_DIR) --cov-report=term-missing --cov-report=html

.PHONY: test-integration
test-integration:
	@echo "Running integration tests (requires LogFlux agent)"
	$(PYTEST) $(TEST_DIR)/integration/ -v -s

.PHONY: test-all
test-all:
	$(PYTEST) $(TEST_DIR)/ -v

# Linting targets
.PHONY: lint
lint: lint-flake8 lint-mypy

.PHONY: lint-flake8
lint-flake8:
	$(FLAKE8) $(SRC_DIR) $(TEST_DIR)

.PHONY: lint-mypy
lint-mypy:
	$(MYPY) $(SRC_DIR)

# Formatting targets
.PHONY: format
format:
	$(BLACK) $(SRC_DIR) $(TEST_DIR) $(EXAMPLES_DIR)
	$(ISORT) $(SRC_DIR) $(TEST_DIR) $(EXAMPLES_DIR)

.PHONY: format-check
format-check:
	$(BLACK) --check $(SRC_DIR) $(TEST_DIR) $(EXAMPLES_DIR)
	$(ISORT) --check-only $(SRC_DIR) $(TEST_DIR) $(EXAMPLES_DIR)

# Build targets
.PHONY: dist
dist: clean
	$(PYTHON) setup.py sdist bdist_wheel

# Manual upload targets removed - use GitHub Actions for releases

# Example targets
.PHONY: examples
examples:
	@echo "Running basic example:"
	cd $(EXAMPLES_DIR)/basic && $(PYTHON) main.py
	@echo "\nRunning batch example:"
	cd $(EXAMPLES_DIR)/batch && $(PYTHON) main.py
	@echo "\nRunning config example:"
	cd $(EXAMPLES_DIR)/config && $(PYTHON) main.py

.PHONY: example-basic
example-basic:
	cd $(EXAMPLES_DIR)/basic && $(PYTHON) main.py

.PHONY: example-batch
example-batch:
	cd $(EXAMPLES_DIR)/batch && $(PYTHON) main.py

.PHONY: example-config
example-config:
	cd $(EXAMPLES_DIR)/config && $(PYTHON) main.py

.PHONY: example-logging
example-logging:
	cd $(EXAMPLES_DIR)/integrations/logging && $(PYTHON) main.py

# Documentation targets
.PHONY: docs
docs:
	@echo "Documentation generation not implemented yet"
	@echo "See README.md for current documentation"

# Utility targets
.PHONY: clean
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf $(TMP_DIR)/*
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

.PHONY: clean-all
clean-all: clean
	rm -rf .venv/
	rm -rf venv/

# Directory creation
$(TMP_DIR):
	mkdir -p $(TMP_DIR)

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

# Version information
.PHONY: version
version:
	@$(PYTHON) -c "import logflux; print(f'LogFlux Python SDK v{logflux.__version__}')"

# Development setup
.PHONY: dev-setup
dev-setup:
	$(PIP) install -e .[dev]
	pre-commit install || true

# Check if LogFlux agent is running
.PHONY: check-agent
check-agent:
	@echo "Checking for LogFlux agent..."
	@if [ -S "/tmp/logflux-agent.sock" ]; then \
		echo "LogFlux agent socket found at /tmp/logflux-agent.sock"; \
	else \
		echo "LogFlux agent socket not found. Start the agent first for integration tests."; \
	fi

# Performance testing
.PHONY: perf-test
perf-test:
	@echo "Performance testing not implemented yet"

# Security scanning
.PHONY: security
security:
	@echo "Security scanning not implemented yet"