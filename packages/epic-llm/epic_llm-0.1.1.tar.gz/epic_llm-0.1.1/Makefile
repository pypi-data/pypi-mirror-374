# Makefile for testing commands and development workflow

.PHONY: test test-unit test-integration test-verbose test-coverage test-watch
.PHONY: lint format typecheck check-all
.PHONY: clean install install-dev build release test-uvx test-e2e test-quick
.PHONY: help

# Test commands
test:
	@echo "🧪 Running all tests..."
	uv run pytest

test-unit:
	@echo "🔬 Running unit tests..."
	uv run pytest tests/unit/ -v

test-integration:
	@echo "🔗 Running integration tests..."
	uv run pytest tests/integration/ -v

test-verbose:
	@echo "📝 Running tests with verbose output..."
	uv run pytest -v -s

test-coverage:
	@echo "📊 Running tests with coverage..."
	uv run pytest --cov=epic_llm --cov-report=term-missing --cov-report=html

test-watch:
	@echo "👀 Running tests in watch mode..."
	uv run pytest-watch -- tests/

test-fast:
	@echo "⚡ Running fast tests only (unit tests)..."
	uv run pytest tests/unit/ -x

test-slow:
	@echo "🐌 Running slow tests (integration tests)..."
	uv run pytest tests/integration/ -v

test-auth:
	@echo "🔐 Running authentication tests..."
	uv run pytest -k "auth" -v

test-providers:
	@echo "🚀 Running provider tests..."
	uv run pytest -k "provider" -v

test-cli:
	@echo "💻 Running CLI tests..."
	uv run pytest tests/integration/test_cli_commands.py -v

# End-to-end testing
test-e2e:
	@echo "🎯 Running comprehensive end-to-end tests..."
	python scripts/test-e2e.py

test-quick:
	@echo "⚡ Running quick end-to-end tests..."
	./scripts/quick-test.sh

# Core working tests (from CRUSH.md)
test-core:
	@echo "🎯 Running core working tests (51% coverage)..."
	uv run pytest tests/integration/ tests/unit/test_main_cli.py tests/unit/test_providers_init.py tests/unit/test_provider_manager.py tests/unit/test_managers.py tests/unit/test_base_provider.py tests/unit/test_validators.py tests/unit/test_dependencies.py tests/unit/test_paths.py --cov=epic_llm

# Quality checks
lint:
	@echo "🧹 Running linter..."
	uv run ruff check .

format:
	@echo "🎨 Formatting code..."
	uv run ruff format .

typecheck:
	@echo "🔍 Type checking..."
	uv run mypy epic_llm/

check-all: lint typecheck test-unit
	@echo "✅ All checks passed!"

# Development setup
install:
	@echo "📦 Installing package..."
	uv sync

install-dev:
	@echo "🛠️ Installing development dependencies..."
	uv sync --dev

clean:
	@echo "🧽 Cleaning up..."
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Package building
build: clean
	@echo "📦 Building Epic LLM package..."
	uv build

# Test uvx distribution
test-uvx: build
	@echo "🧪 Testing uvx distribution..."
	uvx --from ./dist/epic_llm-*.whl epic-llm --help
	uvx --from ./dist/epic_llm-*.whl epic-llm list
	@echo "✅ uvx distribution works!"

# Release preparation
release: clean check-all test-core build test-uvx test-quick
	@echo "🚀 Preparing release..."
	@echo "✅ Release build completed!"
	@echo "📦 Package available in dist/ directory"
	@echo "🚀 Ready for: uv publish or uvx epic-llm"

# Continuous Integration simulation
ci: install-dev lint typecheck test-coverage
	@echo "🎯 CI pipeline completed successfully!"

# Development workflow
dev-setup: install-dev
	@echo "🚀 Development environment ready!"
	@echo "Available commands:"
	@echo "  make test          - Run all tests"
	@echo "  make test-unit     - Run unit tests only"
	@echo "  make test-watch    - Run tests in watch mode"
	@echo "  make lint          - Run linter"
	@echo "  make format        - Format code"
	@echo "  make typecheck     - Run type checker"
	@echo "  make check-all     - Run all quality checks"
	@echo "  make build         - Build package"
	@echo "  make test-uvx      - Test uvx distribution"
	@echo "  make release       - Full release build"

# Help
help:
	@echo "Available targets:"
	@echo "  Test commands:"
	@echo "    test             - Run all tests"
	@echo "    test-unit        - Run unit tests only"
	@echo "    test-integration - Run integration tests only"
	@echo "    test-verbose     - Run tests with verbose output"
	@echo "    test-coverage    - Run tests with coverage report"
	@echo "    test-watch       - Run tests in watch mode"
	@echo "    test-fast        - Run fast tests only (unit)"
	@echo "    test-core        - Run core working tests (51% coverage)"
	@echo "    test-auth        - Run authentication tests"
	@echo "    test-providers   - Run provider tests"
	@echo "    test-cli         - Run CLI tests"
	@echo "    test-e2e         - Run comprehensive end-to-end tests"
	@echo "    test-quick       - Run quick end-to-end tests"
	@echo ""
	@echo "  Quality checks:"
	@echo "    lint            - Run linter"
	@echo "    format          - Format code"
	@echo "    typecheck       - Run type checker"
	@echo "    check-all       - Run all quality checks"
	@echo ""
	@echo "  Build & Release:"
	@echo "    build           - Build package"
	@echo "    test-uvx        - Test uvx distribution"
	@echo "    release         - Full release build (tests + package)"
	@echo "    clean           - Clean build artifacts"
	@echo ""
	@echo "  Development:"
	@echo "    install         - Install package"
	@echo "    install-dev     - Install with dev dependencies"
	@echo "    dev-setup       - Set up development environment"
	@echo "    ci              - Run full CI pipeline"