# Epic LLM - Development Guide

## Build & Test Commands
```bash
# Development setup
uv sync --dev                   # Install dependencies
uv run python -m epic_llm --help  # Test CLI

# Testing
uv run pytest                     # Run all tests
uv run pytest tests/unit/         # Run unit tests only
uv run pytest tests/integration/  # Run integration tests only
uv run pytest -v                  # Verbose output
uv run pytest --cov=epic_llm   # Coverage report
uv run pytest -k "auth"          # Run authentication tests
uv run pytest -k "provider"      # Run provider tests
uv run pytest -m "not slow"      # Skip slow tests
make test                         # Run via Makefile
make test-unit                    # Unit tests via Makefile
make test-coverage                # Coverage via Makefile

# End-to-End Testing
./scripts/quick-test.sh           # Quick E2E validation (recommended)
python scripts/test-e2e.py        # Comprehensive E2E tests
make test-quick                   # Quick E2E via Makefile
make test-e2e                     # Comprehensive E2E via Makefile

# Core Working Tests (51% coverage)
uv run pytest tests/integration/ tests/unit/test_main_cli.py tests/unit/test_providers_init.py tests/unit/test_provider_manager.py tests/unit/test_managers.py tests/unit/test_base_provider.py tests/unit/test_validators.py tests/unit/test_dependencies.py tests/unit/test_gemini_auth_validator.py tests/unit/test_paths.py --cov=epic_llm
make test-core                    # Core tests via Makefile

# Linting & Formatting  
uv run ruff check .            # Linting
uv run ruff format .           # Formatting
uv run mypy src/               # Type checking

# Build & Install
uv build                       # Build wheel
uv pip install -e .            # Editable install

# uvx Distribution Testing
uvx --from ./dist/epic_llm-*.whl epic-llm --help  # Test uvx distribution
make test-uvx                   # Test uvx build process
make release                    # Full release build

# Dependency Checking
uv run epic-llm check         # Check all provider dependencies
uv run epic-llm check claude  # Check specific provider
uv run epic-llm check --install  # Auto-install missing dependencies

# Gateway Authentication Commands
epic-llm set-gateway-key claude --key "your-api-key"   # Enable gateway auth
epic-llm set-gateway-key claude                        # Disable gateway auth  
epic-llm show-gateway-key claude                       # Show current status
```

## Code Style Guidelines
- **Imports**: Use absolute imports, group stdlib/third-party/local
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Types**: Use type hints everywhere, prefer Union over | for Python <3.10 compat
- **Error Handling**: Use custom exceptions, log errors with context
- **Async**: Use async/await for I/O operations, subprocess calls
- **Docker**: Prefer official images, use multi-stage builds
- **Config**: Use Pydantic for settings validation
- **CLI**: Use typer for consistent CLI interface
- **Logging**: Use structlog for structured logging

## Provider Integration Notes
- **Claude**: Requires `claude auth login` and validates via `claude whoami` (Port: 8000)
- **Copilot**: Uses ericc-ch/copilot-api with GitHub device auth (Port: 8081)
- **Gemini**: Requires OAuth flow with Google (Port: 8888)
- **Port Management**: Auto-allocate ports 8000-8999, detect conflicts
- **Port Conflicts**: Copilot moved from 8080→8081 to avoid conflict with Gemini OAuth callback
- **Health Checks**: All providers must expose health endpoints
- **Dependencies**: Use `epic-llm check` to verify all required tools

## Authentication & OAuth
- **Gemini OAuth**: Uses port 8080 for OAuth callback (localhost:8080/callback)
- **Claude CLI Auth**: Requires `claude auth login` and validates via `claude whoami`
- **Copilot Auth**: Handled via GitHub CLI (no OAuth callback needed)
- **Port 8080 Reserved**: Keep port 8080 free for Gemini OAuth authentication flow

## Port 8080 Hardcoded Issue
⚠️ **CRITICAL**: Port 8080 is hardcoded in geminicli2api's OAuth flow and cannot be changed:
- `redirect_uri="http://localhost:8080"` is hardcoded in `src/auth.py`
- OAuth callback server binds to port 8080 during authentication
- **No configuration option** exists to change this port
- **Solution**: All other providers must avoid port 8080
- **Copilot moved**: 8080→8081 to resolve this conflict
- **Future providers**: Must not use port 8080

## Authentication Testing Support
- **Claude CLI Validation**: Checks `~/.claude/.credentials.json` and tests `claude whoami`
- **Copilot GitHub Auth**: Validates GitHub token via GitHub API `/user` endpoint
- **Gemini OAuth Validation**: Tests refresh token with Google OAuth API
- **Dynamic Status Updates**: Real-time authentication status detection
- **Secure Credential Handling**: Never exposes sensitive authentication data
- **User Guidance**: Clear setup instructions for each authentication type

## Directory Structure

### Application Directory: `~/.local/share/epic-llm/`
```
~/.local/share/epic-llm/
├── state.json                     # Application state (running processes, ports, etc.)
├── config.json                    # epic-llm configuration (optional)
└── pkg/                           # Downloaded packages/repos
    ├── claude-code-api/          # Git repo: https://github.com/codingworkflow/claude-code-api.git
    ├── copilot-api/              # NPM package cache for ericc-ch/copilot-api
    └── geminicli2api/            # Git repo: https://github.com/gzzhongqi/geminicli2api.git
        └── oauth_creds.json      # Gemini OAuth credentials
```

### External Configuration (not managed by epic-llm):
- **Claude**: `~/.claude/.credentials.json` (managed by Claude CLI)
- **Copilot**: `~/.config/gh/hosts.yml` (managed by GitHub CLI)

### Migration Notes:
- New installations use the `pkg/` subdirectory structure
- Existing installations in root directory will continue to work
- Manual migration: `mv ~/.local/share/epic-llm/claude-code-api ~/.local/share/epic-llm/pkg/`
- **Copilot Provider**: Updated to use `ericc-ch/copilot-api` instead of `aaamoon/copilot-gpt4-service`
- **NPX Integration**: Copilot now uses `npx copilot-api@latest` for installation and execution
- **Authentication Flow**: All providers now support comprehensive authentication validation