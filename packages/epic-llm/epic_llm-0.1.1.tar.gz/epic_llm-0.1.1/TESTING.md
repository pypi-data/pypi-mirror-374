# LLM API Gateway - Testing Framework

## 📋 Overview

Comprehensive testing framework for the LLM API Gateway project featuring:
- **Unit Tests**: Fast, isolated component testing
- **Integration Tests**: Cross-component functionality testing  
- **Simulation Tests**: Logic validation without external dependencies
- **CLI Tests**: Command-line interface validation

## 🧪 Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── test_basic.py                  # Basic framework validation
├── unit/                          # Unit tests (fast, isolated)
│   ├── test_auth_validators.py    # Authentication validation logic
│   ├── test_managers.py           # Port/state management
│   └── test_providers.py          # Provider base functionality
├── integration/                   # Integration tests
│   ├── test_cli_commands.py       # CLI command simulation
│   └── test_provider_lifecycle.py # End-to-end workflows
├── fixtures/                      # Test data and mocks
│   └── mock_responses.py          # HTTP response mocks
└── Makefile                       # Testing convenience commands
```

## 🚀 Quick Start

### Run All Tests
```bash
# Via pytest
uv run pytest

# Via Makefile  
make test
```

### Run Specific Test Categories
```bash
# Unit tests only (fast)
make test-unit

# Integration tests only  
make test-integration

# Core working tests (from CRUSH.md)
make test-core

# Authentication tests
make test-auth

# Provider tests
make test-providers

# CLI tests
make test-cli

# End-to-end tests
make test-e2e        # Comprehensive E2E tests
make test-quick      # Quick E2E validation
```

### Development Workflow
```bash
# Run tests with coverage
make test-coverage

# Run tests in watch mode (auto-rerun on changes)
make test-watch

# Fast feedback loop (unit tests only)
make test-fast

# Full quality checks (lint + typecheck + test)
make check-all
```

## 📊 Test Categories

### 1. Unit Tests (24 tests)
- **Fast execution** (< 1 second)
- **Isolated components** with mocked dependencies
- **High test coverage** for individual functions/classes
- **Examples**: Port allocation logic, auth status validation, enum handling

### 2. Integration Tests (17 tests)  
- **Cross-component workflows** 
- **Simulation-based** to avoid external dependencies
- **End-to-end scenarios** like provider lifecycle management
- **Examples**: Port conflict resolution, auth flow caching, CLI error handling

### 3. Simulation Tests (9 tests)
- **Logic validation** without external API calls
- **State management** testing  
- **Process coordination** simulation
- **Examples**: Multiple provider coordination, auth status caching

### 4. End-to-End Tests
- **CLI functionality testing** with real commands
- **User workflow validation** 
- **Package building verification**
- **Examples**: Help commands, provider listing, dependency checking

## 🔧 Test Features

### Async Support
- Full **pytest-asyncio** integration
- Automatic async test detection
- Proper event loop management

### Mocking & Fixtures  
- **Comprehensive mock data** in `fixtures/mock_responses.py`
- **Reusable fixtures** in `conftest.py`
- **HTTP response mocking** for external APIs
- **Process/command mocking** for CLI operations

### Quality Assurance
- **Linting** with ruff (fixed automatically)
- **Type checking** ready (mypy)
- **Coverage reporting** with pytest-cov
- **CI-ready** configuration

## 📈 Coverage Report

Current test coverage focuses on tested components:
- **Port Manager**: 84% coverage
- **State Manager**: 55% coverage  
- **Auth Validators**: 49% coverage
- **Overall**: 10% (expected - simulation tests don't exercise full codebase)

## 🛠 Development Commands

### Testing Commands
```bash
uv run pytest                     # Run all tests
uv run pytest tests/unit/         # Unit tests only
uv run pytest tests/integration/  # Integration tests only
uv run pytest -v                  # Verbose output
uv run pytest --cov=epic_llm   # Coverage report
uv run pytest -k "auth"          # Run authentication tests
uv run pytest -k "provider"      # Run provider tests
uv run pytest -m "not slow"      # Skip slow tests

# End-to-end testing
python scripts/test-e2e.py        # Comprehensive E2E tests
./scripts/quick-test.sh           # Quick E2E validation
```

### Quality Commands
```bash
uv run ruff check .              # Linting
uv run ruff format .             # Formatting
uv run mypy epic_llm/          # Type checking
```

### Makefile Shortcuts
```bash
make test                        # Run all tests
make test-unit                   # Unit tests via Makefile
make test-core                   # Core working tests (51% coverage)
make test-coverage               # Coverage via Makefile
make test-e2e                    # Comprehensive end-to-end tests
make test-quick                  # Quick end-to-end validation
make lint                        # Linting
make format                      # Code formatting
make check-all                   # All quality checks
```

## 🎯 Testing Best Practices

### Test Organization
- **Unit tests**: Test individual functions/classes in isolation
- **Integration tests**: Test workflows between components
- **Simulation tests**: Test logic without external dependencies
- **Use descriptive test names** that explain the scenario

### Mocking Strategy
- **Mock external dependencies** (HTTP APIs, file system, processes)
- **Use fixture factories** for consistent test data
- **Test both success and failure scenarios**
- **Verify behavior, not just return values**

### Async Testing
- **Use pytest.mark.asyncio** for async tests
- **Mock async operations** appropriately
- **Test concurrent scenarios** when relevant

### Coverage Goals
- **Unit tests**: Aim for high coverage (>80%)
- **Integration tests**: Focus on critical workflows
- **Don't chase 100% coverage** - focus on valuable tests

## 🔄 Continuous Integration

The test suite is designed for CI/CD pipelines:
- **Fast unit tests** for quick feedback
- **Comprehensive integration tests** for confidence
- **Quality checks** (linting, type checking)
- **Coverage reporting** for metrics

Example CI workflow:
```yaml
- name: Run tests
  run: |
    uv sync --dev
    make test-unit      # Fast feedback
    make test-coverage  # Full test suite
    make lint          # Code quality
    make typecheck     # Type safety
```

## 📚 Adding New Tests

### For New Features
1. **Start with unit tests** for core logic
2. **Add integration tests** for workflows
3. **Update fixtures** for new mock data
4. **Add Makefile targets** if needed

### Test File Naming
- `test_*.py` - Test files
- `Test*` - Test classes  
- `test_*` - Test functions
- Use descriptive names explaining the scenario

### Example Test Structure
```python
class TestNewFeature:
    \"\"\"Test new feature functionality.\"\"\"
    
    @pytest.fixture
    def setup_data(self):
        \"\"\"Create test data.\"\"\"
        return {"key": "value"}
    
    def test_success_scenario(self, setup_data):
        \"\"\"Test successful operation.\"\"\"
        # Arrange, Act, Assert
        
    @pytest.mark.asyncio
    async def test_async_scenario(self):
        \"\"\"Test async operation.\"\"\"
        # Test async functionality
```

This testing framework provides confidence in code quality while maintaining fast development cycles through comprehensive yet efficient test coverage.