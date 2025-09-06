"""Test fixtures for mock data and responses."""

from typing import Any, Dict


class MockResponses:
    """Mock HTTP responses for external APIs."""

    @staticmethod
    def github_user_success() -> Dict[str, Any]:
        """Mock successful GitHub user API response."""
        return {
            "login": "test_user",
            "id": 12345,
            "name": "Test User",
            "email": "test@example.com",
            "avatar_url": "https://github.com/images/test.jpg",
            "type": "User",
        }

    @staticmethod
    def github_user_unauthorized() -> Dict[str, Any]:
        """Mock unauthorized GitHub API response."""
        return {
            "message": "Bad credentials",
            "documentation_url": "https://docs.github.com/rest",
        }

    @staticmethod
    def google_oauth_success() -> Dict[str, Any]:
        """Mock successful Google OAuth token info response."""
        return {
            "scope": "openid email profile",
            "email": "test@gmail.com",
            "email_verified": True,
            "expires_in": 3599,
            "access_type": "online",
        }

    @staticmethod
    def google_oauth_invalid() -> Dict[str, Any]:
        """Mock invalid Google OAuth token response."""
        return {"error": "invalid_token", "error_description": "Invalid Value"}

    @staticmethod
    def claude_api_health() -> Dict[str, Any]:
        """Mock Claude API health check response."""
        return {"status": "healthy", "version": "1.0.0", "uptime": 12345}

    @staticmethod
    def copilot_api_health() -> Dict[str, Any]:
        """Mock Copilot API health check response."""
        return {"status": "ok", "message": "Copilot API is running"}

    @staticmethod
    def copilot_models_list() -> Dict[str, Any]:
        """Mock Copilot API models list response."""
        return {
            "object": "list",
            "data": [
                {
                    "id": "gpt-4",
                    "object": "model",
                    "created": 1677610602,
                    "owned_by": "openai",
                },
                {
                    "id": "gpt-3.5-turbo",
                    "object": "model",
                    "created": 1677610602,
                    "owned_by": "openai",
                },
            ],
        }

    @staticmethod
    def gemini_api_health() -> Dict[str, Any]:
        """Mock Gemini API health check response."""
        return {
            "status": "running",
            "port": 8082,
            "models": ["gemini-pro", "gemini-pro-vision"],
        }


class TestConfigs:
    """Test configuration data."""

    @staticmethod
    def claude_credentials() -> Dict[str, Any]:
        """Mock Claude credentials data."""
        return {
            "username": "test_user",
            "session_key": "test_session_key_12345",
            "expires_at": "2024-12-31T23:59:59Z",
        }

    @staticmethod
    def provider_states() -> Dict[str, Dict[str, Any]]:
        """Mock provider state configurations."""
        return {
            "claude": {
                "name": "claude",
                "status": "stopped",
                "auth_status": "unknown",
                "port": None,
                "pid": None,
                "health_url": None,
                "start_command": ["claude", "api", "--port", "8080"],
                "dependencies": ["claude"],
            },
            "copilot": {
                "name": "copilot",
                "status": "stopped",
                "auth_status": "unknown",
                "port": None,
                "pid": None,
                "health_url": None,
                "start_command": ["npx", "ericc-ch/copilot-api", "--port", "8081"],
                "dependencies": ["node", "npx"],
            },
            "gemini": {
                "name": "gemini",
                "status": "stopped",
                "auth_status": "unknown",
                "port": None,
                "pid": None,
                "health_url": None,
                "start_command": ["npx", "geminicli2api", "--port", "8082"],
                "dependencies": ["node", "npx"],
            },
        }

    @staticmethod
    def port_allocation_config() -> Dict[str, Any]:
        """Mock port allocation configuration."""
        return {
            "start_port": 8000,
            "end_port": 8999,
            "preferred_ports": {"claude": 8080, "copilot": 8081, "gemini": 8082},
        }


class CommandOutputs:
    """Mock command line outputs."""

    @staticmethod
    def claude_whoami_success() -> str:
        """Mock successful claude whoami output."""
        return "Authenticated as: test_user"

    @staticmethod
    def claude_whoami_failure() -> str:
        """Mock failed claude whoami output."""
        return "Error: Authentication required. Please run 'claude auth' to log in."

    @staticmethod
    def node_version_success() -> str:
        """Mock successful node --version output."""
        return "v18.17.0"

    @staticmethod
    def npm_version_success() -> str:
        """Mock successful npm --version output."""
        return "9.6.7"

    @staticmethod
    def which_command_success(command: str) -> str:
        """Mock successful which command output."""
        return f"/usr/bin/{command}"

    @staticmethod
    def which_command_failure() -> str:
        """Mock failed which command output."""
        return ""

    @staticmethod
    def ps_aux_output() -> str:
        """Mock ps aux output for process checking."""
        return (
            "USER  PID %CPU %MEM  VSZ  RSS TTY STAT START TIME COMMAND\n"
            "root    1  0.0  0.0 169300 13808 ?  Ss  08:00 0:02 /sbin/init\n"
            "test 12345 0.1  1.2 987654 98765 ?  Sl  08:30 0:05 node copilot-api\n"
            "test 54321 0.0  0.5 123456 12345 ?   S  08:31 0:01 claude api"
        )


class EnvironmentSetup:
    """Environment setup helpers for tests."""

    @staticmethod
    def mock_home_directory() -> str:
        """Mock user home directory path."""
        return "/home/test_user"

    @staticmethod
    def mock_claude_config_dir() -> str:
        """Mock Claude configuration directory."""
        return "/home/test_user/.claude"

    @staticmethod
    def mock_copilot_config_dir() -> str:
        """Mock Copilot configuration directory."""
        return "/home/test_user/.local/share/copilot-api"

    @staticmethod
    def mock_environment_variables() -> Dict[str, str]:
        """Mock environment variables."""
        return {
            "HOME": "/home/test_user",
            "PATH": "/usr/bin:/bin:/usr/local/bin",
            "NODE_PATH": "/usr/local/lib/node_modules",
        }
