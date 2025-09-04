.PHONY: help install dev-install test test-cov demo lint format typecheck check clean clean-all clean-pyc clean-build clean-test build publish publish-test info

# Default target
help:
	@echo "Available targets:"
	@echo "  clean       - Remove Python bytecode and basic artifacts"
	@echo "  clean-all   - Deep clean everything (pyc, build, test, cache)"
	@echo "  clean-pyc   - Remove Python bytecode files"
	@echo "  clean-build - Remove build artifacts"
	@echo "  clean-test  - Remove test artifacts"
	@echo "  install     - Install package in current environment"
	@echo "  dev-install - Install package in development mode"
	@echo "  test        - Run tests"
	@echo "  test-cov    - Run tests with coverage report"
	@echo "  demo        - Run the interactive demo"
	@echo "  build       - Build the project"
	@echo "  publish     - Build and publish to PyPI"
	@echo "  publish-test- Build and publish to TestPyPI"
	@echo "  lint        - Check code quality"
	@echo "  format      - Fix code formatting"
	@echo "  typecheck   - Run type checking"
	@echo "  check       - Run all checks (lint, typecheck, test)"
	@echo "  info        - Show project information"

# Install package
install:
	@echo "Installing package..."
	pip install .

# Install package in development mode
dev-install:
	@echo "Installing package in development mode..."
	@if command -v uv >/dev/null 2>&1; then \
		uv sync --dev; \
	else \
		pip install -e ".[dev]"; \
	fi

# Run tests
test:
	@echo "Running tests..."
	@if command -v uv >/dev/null 2>&1; then \
		uv run pytest; \
	elif command -v pytest >/dev/null 2>&1; then \
		pytest; \
	else \
		python -m pytest; \
	fi

# Run tests with coverage
test-cov:
	@echo "Running tests with coverage..."
	@if command -v uv >/dev/null 2>&1; then \
		uv run pytest --cov=chuk_term --cov-report=html --cov-report=term; \
	else \
		pytest --cov=chuk_term --cov-report=html --cov-report=term; \
	fi

# Run the demo
demo:
	@echo "Running ChukTerm demo..."
	@if command -v uv >/dev/null 2>&1; then \
		uv run chuk-term demo; \
	else \
		chuk-term demo; \
	fi

# Check code quality
lint:
	@echo "Running linters..."
	@if command -v uv >/dev/null 2>&1; then \
		uv run ruff check src/ tests/; \
		uv run black --check src/ tests/; \
	elif command -v ruff >/dev/null 2>&1; then \
		ruff check src/ tests/; \
		black --check src/ tests/; \
	else \
		echo "Ruff not found. Install with: pip install ruff black"; \
	fi

# Fix code formatting
format:
	@echo "Formatting code..."
	@if command -v uv >/dev/null 2>&1; then \
		uv run black src/ tests/; \
		uv run ruff check --fix src/ tests/; \
	elif command -v ruff >/dev/null 2>&1; then \
		black src/ tests/; \
		ruff check --fix src/ tests/; \
	else \
		echo "Ruff not found. Install with: pip install ruff black"; \
	fi

# Type checking
typecheck:
	@echo "Running type checker..."
	@if command -v uv >/dev/null 2>&1; then \
		uv run mypy src/; \
	elif command -v mypy >/dev/null 2>&1; then \
		mypy src/; \
	else \
		echo "MyPy not found. Install with: pip install mypy"; \
	fi

# Basic clean - Python bytecode and common artifacts
clean: clean-pyc clean-build
	@echo "Basic clean complete."

# Remove Python bytecode files and __pycache__ directories
clean-pyc:
	@echo "Cleaning Python bytecode files..."
	@find . -type f -name '*.pyc' -delete 2>/dev/null || true
	@find . -type f -name '*.pyo' -delete 2>/dev/null || true
	@find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true

# Remove build artifacts
clean-build:
	@echo "Cleaning build artifacts..."
	@rm -rf build/ dist/ *.egg-info 2>/dev/null || true
	@rm -rf .eggs/ 2>/dev/null || true
	@find . -name '*.egg' -exec rm -f {} + 2>/dev/null || true

# Remove test artifacts
clean-test:
	@echo "Cleaning test artifacts..."
	@rm -rf .pytest_cache/ 2>/dev/null || true
	@rm -rf .coverage 2>/dev/null || true
	@rm -rf htmlcov/ 2>/dev/null || true
	@rm -rf .tox/ 2>/dev/null || true
	@rm -rf .cache/ 2>/dev/null || true
	@find . -name '.coverage.*' -delete 2>/dev/null || true

# Deep clean - everything
clean-all: clean-pyc clean-build clean-test
	@echo "Deep cleaning..."
	@rm -rf .mypy_cache/ 2>/dev/null || true
	@rm -rf .ruff_cache/ 2>/dev/null || true
	@rm -rf .uv/ 2>/dev/null || true
	@rm -rf node_modules/ 2>/dev/null || true
	@find . -name '.DS_Store' -delete 2>/dev/null || true
	@find . -name 'Thumbs.db' -delete 2>/dev/null || true
	@find . -name '*.log' -delete 2>/dev/null || true
	@find . -name '*.tmp' -delete 2>/dev/null || true
	@find . -name '*~' -delete 2>/dev/null || true
	@echo "Deep clean complete."

# Build the project using the pyproject.toml configuration
build: clean-build
	@echo "Building project..."
	@if command -v uv >/dev/null 2>&1; then \
		uv build; \
	else \
		python3 -m build; \
	fi
	@echo "Build complete. Distributions are in the 'dist' folder."

# Publish the package to PyPI using twine
publish: build
	@echo "Publishing package to PyPI..."
	@if [ ! -d "dist" ] || [ -z "$$(ls -A dist 2>/dev/null)" ]; then \
		echo "Error: No distribution files found. Run 'make build' first."; \
		exit 1; \
	fi
	@last_build=$$(ls -t dist/*.tar.gz dist/*.whl 2>/dev/null | head -n 2); \
	if [ -z "$$last_build" ]; then \
		echo "Error: No valid distribution files found."; \
		exit 1; \
	fi; \
	echo "Uploading: $$last_build"; \
	twine upload $$last_build
	@echo "Publish complete."
	@echo "Package available at: https://pypi.org/project/chuk-term/"

# Publish to test PyPI
publish-test: build
	@echo "Publishing to TestPyPI..."
	@if [ ! -d "dist" ] || [ -z "$$(ls -A dist 2>/dev/null)" ]; then \
		echo "Error: No distribution files found. Run 'make build' first."; \
		exit 1; \
	fi
	@last_build=$$(ls -t dist/*.tar.gz dist/*.whl 2>/dev/null | head -n 2); \
	if [ -z "$$last_build" ]; then \
		echo "Error: No valid distribution files found."; \
		exit 1; \
	fi; \
	echo "Uploading to TestPyPI: $$last_build"; \
	twine upload --repository testpypi $$last_build
	@echo "Test publish complete."
	@echo "Package available at: https://test.pypi.org/project/chuk-term/"

# Run all checks
check: lint typecheck test
	@echo "All checks completed."

# Show project info
info:
	@echo "Project Information:"
	@echo "==================="
	@echo "Package: chuk-term"
	@echo "Version: 0.1.0"
	@echo "Description: A terminal library with CLI interface"
	@echo ""
	@if [ -f "pyproject.toml" ]; then \
		echo "pyproject.toml found"; \
		if command -v uv >/dev/null 2>&1; then \
			echo "UV version: $$(uv --version)"; \
		fi; \
		if command -v python >/dev/null 2>&1; then \
			echo "Python version: $$(python --version)"; \
		fi; \
	else \
		echo "No pyproject.toml found"; \
	fi
	@echo "Current directory: $$(pwd)"
	@echo ""
	@echo "Git status:"
	@git status --porcelain 2>/dev/null || echo "Not a git repository"
	@echo ""
	@echo "PyPI credentials:"
	@if [ -f "$$HOME/.pypirc" ]; then \
		echo "  ✓ .pypirc file found"; \
	else \
		echo "  ✗ No .pypirc file"; \
	fi
	@if [ -n "$$TWINE_USERNAME" ] || [ -n "$$PYPI_TOKEN" ]; then \
		echo "  ✓ Environment credentials detected"; \
	else \
		echo "  ✗ No environment credentials"; \
	fi