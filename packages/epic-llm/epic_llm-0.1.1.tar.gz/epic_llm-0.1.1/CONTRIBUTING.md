# Contributing to Epic LLM

Thank you for your interest in contributing to Epic LLM! This guide will help you get started with bug fixes, adding new providers, and general development.

## 🚀 Quick Start

```bash
# 1. Fork and clone the repository
git clone https://github.com/your-username/epic-llm.git
cd epic-llm

# 2. Set up development environment
uv sync --dev

# 3. Run tests to ensure everything works
./scripts/quick-test.sh

# 4. Make your changes
# 5. Test your changes
./scripts/quick-test.sh

# 6. Submit a pull request
```

## 📋 Development Setup

### Prerequisites
- **Python 3.8+** (3.11+ recommended)
- **uv** (Python package manager)
- **Git** for version control

### Environment Setup
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/your-username/epic-llm.git
cd epic-llm

# Install dependencies
uv sync --dev

# Verify installation
uv run epic-llm --help
```

## 🧪 Testing

### Quick Testing (Recommended)
```bash
# Fast end-to-end validation
./scripts/quick-test.sh
```

### Comprehensive Testing
```bash
# All tests
uv run pytest

# Specific test categories
uv run pytest tests/unit/           # Unit tests
uv run pytest tests/integration/    # Integration tests
make test-core                      # Core working tests

# Code quality
uv run ruff check .                 # Linting
uv run ruff format .                # Formatting
```

### Testing Your Changes
```bash
# Before submitting PR
./scripts/quick-test.sh             # Must pass
uv run ruff check .                 # Should have no errors
uv run pytest tests/unit/           # Core tests should pass
```

## 🐛 Bug Fixes

### Finding Issues
- Check [GitHub Issues](https://github.com/epic-llm/epic-llm/issues)
- Look for `good first issue` or `bug` labels
- Run tests to find failing scenarios

### Bug Fix Workflow
1. **Reproduce the bug**:
   ```bash
   # Create a test case that demonstrates the bug
   uv run epic-llm [command that fails]
   ```

2. **Write a test** (if missing):
   ```python
   # tests/unit/test_[component].py
   def test_bug_scenario():
       """Test that reproduces the bug."""
       # Arrange: Set up the scenario
       # Act: Execute the buggy code
       # Assert: Verify expected behavior
   ```

3. **Fix the bug**:
   - Locate the relevant code in `epic_llm/`
   - Make minimal changes to fix the issue
   - Ensure existing tests still pass

4. **Verify the fix**:
   ```bash
   ./scripts/quick-test.sh
   uv run pytest tests/unit/test_[affected_component].py
   ```

## 🚀 Adding New Providers

Adding a new LLM provider involves several steps. Here's how to add support for a new service:

### 1. Provider Research
Before starting, research:
- **API Access Method**: CLI tool, API keys, OAuth, etc.
- **Authentication**: How users authenticate
- **Dependencies**: Required tools/packages
- **Port Requirements**: Default port preferences
- **Repository/Package**: Where the implementation lives

### 2. Create Provider Files

#### Core Provider Class
```python
# epic_llm/providers/[provider_name].py
from epic_llm.providers.base import BaseProvider
from epic_llm.utils.paths import get_provider_pkg_dir

class NewProviderProvider(BaseProvider):
    """Provider for New Provider service."""
    
    def __init__(self, install_dir: str = None):
        if install_dir is None:
            install_dir = get_provider_pkg_dir("newprovider")
        
        super().__init__(
            "newprovider",      # Provider name
            8082,               # Default port (avoid conflicts)
            install_dir
        )
        self.repo_url = "https://github.com/example/newprovider-api.git"
        
    def get_dependencies(self) -> dict:
        """Return required dependencies."""
        return {
            "git": {
                "type": "executable",
                "required": True,
                "description": "Git for cloning repository"
            },
            "node": {
                "type": "executable", 
                "required": True,
                "description": "Node.js runtime"
            }
        }
    
    async def install(self) -> bool:
        """Install the provider."""
        # Implementation for installation
        pass
    
    async def start(self) -> bool:
        """Start the provider service."""
        # Implementation for starting
        pass
    
    async def stop(self) -> bool:
        """Stop the provider service."""
        # Implementation for stopping
        pass
    
    async def health_check(self) -> bool:
        """Check if provider is healthy."""
        # Implementation for health checking
        pass
```

#### Authentication Validator (if needed)
```python
# epic_llm/utils/newprovider_auth_validator.py
from epic_llm.utils.auth_validator import BaseAuthValidator
from epic_llm.managers.state import AuthStatus

class NewProviderAuthValidator(BaseAuthValidator):
    """Authentication validator for New Provider."""
    
    async def validate_authentication(self) -> AuthStatus:
        """Validate authentication status."""
        # Check authentication (API keys, tokens, etc.)
        # Return AuthStatus.AUTHENTICATED, REQUIRED, or FAILED
        pass
```

### 3. Register the Provider

#### Update Provider Registry
```python
# epic_llm/providers/__init__.py
from .newprovider import NewProviderProvider

PROVIDERS = {
    "claude": ClaudeProvider,
    "copilot": CopilotProvider, 
    "gemini": GeminiProvider,
    "newprovider": NewProviderProvider,  # Add your provider
}
```

### 4. Add Tests

#### Unit Tests
```python
# tests/unit/test_newprovider_provider.py
import pytest
from epic_llm.providers.newprovider import NewProviderProvider

class TestNewProviderProvider:
    """Test NewProvider provider functionality."""
    
    def test_provider_creation(self):
        """Test provider can be created."""
        provider = NewProviderProvider()
        assert provider.name == "newprovider"
        assert provider.port == 8082
    
    def test_dependencies(self):
        """Test provider dependencies."""
        provider = NewProviderProvider()
        deps = provider.get_dependencies()
        assert "git" in deps
        assert "node" in deps
```

#### Integration Tests
```python
# tests/integration/test_newprovider_integration.py
import pytest
from epic_llm.providers.newprovider import NewProviderProvider

@pytest.mark.asyncio
async def test_provider_lifecycle():
    """Test provider installation and startup."""
    provider = NewProviderProvider()
    
    # Test installation
    result = await provider.install()
    assert result is True
    
    # Test startup
    result = await provider.start()
    assert result is True
```

### 5. Update Documentation

#### Provider Description
Add to `epic_llm/providers/[provider].py`:
```python
# Add description for the list command
def get_description(self) -> str:
    """Get provider description for listing."""
    return "New Provider service via API (Requires: API key setup)"
```

#### README Updates
Add to the providers table in README.md:
```markdown
| newprovider | New Provider API | 8082 | API key | Commercial |
```

### 6. Provider-Specific Considerations

#### Port Selection
- Avoid ports already used: 8000 (Claude), 8081 (Copilot), 8080 (Gemini OAuth)
- Choose ports in 8000-8999 range
- Document any hardcoded port requirements

#### Authentication Patterns
- **API Keys**: Store in user config files
- **OAuth**: Implement web-based flow
- **CLI Tools**: Integrate with existing CLI authentication
- **Tokens**: Secure storage and validation

#### Installation Patterns
- **Git Repositories**: Clone and build
- **NPM Packages**: Use `npx` or `npm install`
- **Python Packages**: Use `pip install`
- **Binary Downloads**: Download and extract

### 7. Testing Your New Provider

```bash
# Test basic functionality
uv run epic-llm list                    # Should show your provider
uv run epic-llm check newprovider       # Should check dependencies
uv run epic-llm install newprovider     # Should install successfully
uv run epic-llm start newprovider       # Should start service
uv run epic-llm status                  # Should show running
uv run epic-llm stop newprovider        # Should stop service

# Run automated tests
./scripts/quick-test.sh
uv run pytest tests/unit/test_newprovider_provider.py
```

## 📝 Code Style Guidelines

### Python Code Style
```python
# Use type hints
async def start(self) -> bool:
    """Start the provider service."""
    pass

# Use descriptive variable names
authentication_status = await self.validate_auth()

# Handle exceptions properly
try:
    result = await process.communicate()
except asyncio.TimeoutError:
    logger.error("Process timed out")
    return False
```

### Import Organization
```python
# Standard library imports
import asyncio
import json
from pathlib import Path

# Third-party imports
import typer
from rich.console import Console

# Local imports
from epic_llm.providers.base import BaseProvider
from epic_llm.utils.auth_validator import BaseAuthValidator
```

### Error Handling
- Use specific exception types, not bare `except:`
- Log errors with context
- Return meaningful error messages
- Handle async operations properly

### Documentation
- Add docstrings to all classes and methods
- Include type hints
- Document complex logic with comments
- Update README.md for user-facing changes

## 🔧 Development Workflow

### Branch Naming
- `feature/add-provider-x` - New provider
- `fix/issue-123` - Bug fixes  
- `docs/update-contributing` - Documentation
- `test/improve-coverage` - Testing improvements

### Commit Messages
```
feat: add support for NewProvider API
fix: resolve authentication timeout in Claude provider
docs: update installation instructions
test: add integration tests for provider lifecycle
```

### Pull Request Process
1. **Create Feature Branch**:
   ```bash
   git checkout -b feature/add-newprovider
   ```

2. **Make Changes**:
   - Follow code style guidelines
   - Add tests for new functionality
   - Update documentation

3. **Test Changes**:
   ```bash
   ./scripts/quick-test.sh
   uv run ruff check .
   uv run pytest tests/unit/
   ```

4. **Submit PR**:
   - Clear title and description
   - Reference related issues
   - Include testing instructions

### Review Criteria
PRs will be reviewed for:
- ✅ **Functionality**: Does it work as expected?
- ✅ **Tests**: Are there adequate tests?
- ✅ **Code Quality**: Follows style guidelines?
- ✅ **Documentation**: Is it properly documented?
- ✅ **Security**: No security vulnerabilities?

## 🛡️ Security Considerations

### Authentication Handling
- **Never log credentials or tokens**
- Store sensitive data securely
- Validate file permissions (600 for credential files)
- Use secure communication (HTTPS, WSS)

### Input Validation
- Validate all user inputs
- Sanitize file paths
- Check command injection vulnerabilities
- Validate URLs and ports

### Dependencies
- Pin dependency versions where possible
- Review third-party packages for security
- Use official repositories when available

## 🆘 Getting Help

### Resources
- **Documentation**: Check existing docs first
- **Issues**: Search GitHub issues for similar problems
- **Tests**: Look at existing tests for examples
- **Code**: Study existing provider implementations

### Communication
- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and ideas
- **Pull Requests**: For code reviews and feedback

### Troubleshooting
```bash
# Clean environment
rm -rf .venv/
uv sync --dev

# Reset tests
rm -rf .pytest_cache/
./scripts/quick-test.sh

# Check dependencies
uv run epic-llm check
```

## 📊 Contributing Statistics

Current areas needing help:
- 🚀 **New Providers**: OpenAI API, Anthropic API, Local models
- 🐛 **Bug Fixes**: See GitHub issues
- 📚 **Documentation**: User guides, examples
- 🧪 **Testing**: Increase test coverage
- 🌍 **Internationalization**: More language support

## 🎉 Recognition

Contributors will be:
- Listed in the project README
- Mentioned in release notes
- Credited in provider documentation

Thank you for contributing to Epic LLM! 🚀