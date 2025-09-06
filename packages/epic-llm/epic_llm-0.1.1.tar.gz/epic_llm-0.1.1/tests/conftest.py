"""Test configuration and shared fixtures."""

import asyncio
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import Mock

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def mock_claude_credentials(temp_dir: Path) -> Path:
    """Create mock Claude credentials file."""
    creds_dir = temp_dir / ".claude"
    creds_dir.mkdir()
    creds_file = creds_dir / ".credentials.json"
    creds_file.write_text('{"username": "test_user", "session_key": "test_key"}')
    return creds_file


@pytest.fixture
def mock_copilot_token(temp_dir: Path) -> Path:
    """Create mock Copilot token file."""
    token_dir = temp_dir / ".local/share/copilot-api"
    token_dir.mkdir(parents=True)
    token_file = token_dir / "github_token"
    token_file.write_text("ghp_test_token_123456789")
    return token_file


@pytest.fixture
def mock_http_client() -> Mock:
    """Mock HTTP client for external API calls."""
    client = Mock()
    return client


@pytest.fixture
def mock_successful_response() -> Mock:
    """Mock successful HTTP response."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"status": "ok"}
    response.text = '{"status": "ok"}'
    return response


@pytest.fixture
def mock_failed_response() -> Mock:
    """Mock failed HTTP response."""
    response = Mock()
    response.status_code = 401
    response.json.return_value = {"error": "unauthorized"}
    response.text = '{"error": "unauthorized"}'
    return response


@pytest.fixture
def mock_process() -> Mock:
    """Mock subprocess for provider services."""
    process = Mock()
    process.pid = 12345
    process.poll.return_value = None  # Process is running
    process.returncode = None
    return process


@pytest.fixture
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


class MockCommand:
    """Mock for subprocess commands."""

    def __init__(self, return_code: int = 0, stdout: str = "", stderr: str = ""):
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr


@pytest.fixture
def mock_claude_whoami_success() -> MockCommand:
    """Mock successful claude whoami command."""
    return MockCommand(return_code=0, stdout="Authenticated as: test_user")


@pytest.fixture
def mock_claude_whoami_failure() -> MockCommand:
    """Mock failed claude whoami command."""
    return MockCommand(return_code=1, stderr="Authentication required")


@pytest.fixture
def mock_github_user_response() -> dict:
    """Mock GitHub user API response."""
    return {
        "login": "test_user",
        "id": 12345,
        "name": "Test User",
        "email": "test@example.com",
    }


@pytest.fixture
def mock_gemini_oauth_response() -> dict:
    """Mock Google OAuth token info response."""
    return {
        "scope": "openid email profile",
        "email": "test@gmail.com",
        "email_verified": True,
        "expires_in": 3599,
    }
