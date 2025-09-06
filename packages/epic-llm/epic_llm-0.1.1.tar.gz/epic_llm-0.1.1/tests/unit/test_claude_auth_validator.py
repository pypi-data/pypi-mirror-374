"""Tests for Claude authentication validator."""

import asyncio
import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from epic_llm.managers.state import AuthStatus
from epic_llm.utils.claude_auth_validator import ClaudeAuthValidator


class TestClaudeAuthValidatorInitialization:
    """Test ClaudeAuthValidator initialization."""

    def test_validator_creation(self):
        """Test creating Claude auth validator instance."""
        validator = ClaudeAuthValidator()
        assert validator is not None

    def test_validator_with_custom_credentials_dir(self, temp_dir):
        """Test validator with custom credentials directory."""
        custom_dir = temp_dir / "custom_claude"
        validator = ClaudeAuthValidator(credentials_dir=custom_dir)
        assert validator.credentials_dir == custom_dir

    def test_validator_default_credentials_dir(self):
        """Test validator with default credentials directory."""
        validator = ClaudeAuthValidator()
        expected_path = Path.home() / ".claude"
        assert validator.credentials_dir == expected_path


class TestClaudeCredentialsValidation:
    """Test Claude credentials validation functionality."""

    @pytest.mark.asyncio
    async def test_validate_authentication_not_installed(self):
        """Test validation when Claude CLI is not installed."""
        validator = ClaudeAuthValidator()

        with patch.object(validator, "_check_claude_cli_installed") as mock_check:
            mock_check.return_value = False

            result = await validator.validate_authentication()

            assert result == AuthStatus.FAILED

    @pytest.mark.asyncio
    async def test_validate_authentication_no_credentials_file(self, temp_dir):
        """Test validation when credentials file doesn't exist."""
        credentials_dir = temp_dir / "claude"
        validator = ClaudeAuthValidator(credentials_dir=credentials_dir)

        with patch.object(validator, "_check_claude_cli_installed") as mock_check:
            mock_check.return_value = True

            result = await validator.validate_authentication()

            assert result == AuthStatus.REQUIRED

    @pytest.mark.asyncio
    async def test_validate_authentication_invalid_credentials_file(self, temp_dir):
        """Test validation with invalid credentials file."""
        credentials_dir = temp_dir / "claude"
        credentials_dir.mkdir()
        credentials_file = credentials_dir / ".credentials.json"
        credentials_file.write_text("invalid json")

        validator = ClaudeAuthValidator(credentials_dir=credentials_dir)

        with patch.object(validator, "_check_claude_cli_installed") as mock_check:
            mock_check.return_value = True

            result = await validator.validate_authentication()

            assert result == AuthStatus.FAILED

    @pytest.mark.asyncio
    async def test_validate_authentication_missing_fields(self, temp_dir):
        """Test validation with credentials file missing required fields."""
        credentials_dir = temp_dir / "claude"
        credentials_dir.mkdir()
        credentials_file = credentials_dir / ".credentials.json"
        credentials_file.write_text(json.dumps({"incomplete": "data"}))

        validator = ClaudeAuthValidator(credentials_dir=credentials_dir)

        with patch.object(validator, "_check_claude_cli_installed") as mock_check:
            mock_check.return_value = True

            result = await validator.validate_authentication()

            assert result == AuthStatus.FAILED

    @pytest.mark.asyncio
    async def test_validate_authentication_success(self, temp_dir):
        """Test successful authentication validation."""
        credentials_dir = temp_dir / "claude"
        credentials_dir.mkdir()
        credentials_file = credentials_dir / ".credentials.json"
        credentials_file.write_text(
            json.dumps({"username": "test_user", "session_key": "test_session_key"})
        )

        validator = ClaudeAuthValidator(credentials_dir=credentials_dir)

        with patch.object(validator, "_check_claude_cli_installed") as mock_check:
            with patch.object(validator, "_test_claude_whoami") as mock_whoami:
                mock_check.return_value = True
                mock_whoami.return_value = True

                result = await validator.validate_authentication()

                assert result == AuthStatus.AUTHENTICATED

    @pytest.mark.asyncio
    async def test_validate_authentication_whoami_fails(self, temp_dir):
        """Test validation when claude whoami command fails."""
        credentials_dir = temp_dir / "claude"
        credentials_dir.mkdir()
        credentials_file = credentials_dir / ".credentials.json"
        credentials_file.write_text(
            json.dumps({"username": "test_user", "session_key": "test_session_key"})
        )

        validator = ClaudeAuthValidator(credentials_dir=credentials_dir)

        with patch.object(validator, "_check_claude_cli_installed") as mock_check:
            with patch.object(validator, "_test_claude_whoami") as mock_whoami:
                mock_check.return_value = True
                mock_whoami.return_value = False

                result = await validator.validate_authentication()

                assert result == AuthStatus.FAILED


class TestClaudeCliChecking:
    """Test Claude CLI checking functionality."""

    @pytest.mark.asyncio
    async def test_check_claude_cli_installed_success(self):
        """Test successful Claude CLI installation check."""
        validator = ClaudeAuthValidator()

        with patch(
            "epic_llm.utils.claude_auth_validator.check_cli_command"
        ) as mock_check:
            mock_check.return_value = True

            result = await validator._check_claude_cli_installed()

            assert result is True
            mock_check.assert_called_once_with(["claude", "--version"])

    @pytest.mark.asyncio
    async def test_check_claude_cli_installed_failure(self):
        """Test failed Claude CLI installation check."""
        validator = ClaudeAuthValidator()

        with patch(
            "epic_llm.utils.claude_auth_validator.check_cli_command"
        ) as mock_check:
            mock_check.return_value = False

            result = await validator._check_claude_cli_installed()

            assert result is False

    @pytest.mark.asyncio
    async def test_test_claude_whoami_success(self):
        """Test successful claude whoami command."""
        validator = ClaudeAuthValidator()

        with patch(
            "epic_llm.utils.claude_auth_validator.check_cli_command"
        ) as mock_check:
            mock_check.return_value = True

            result = await validator._test_claude_whoami()

            assert result is True
            mock_check.assert_called_once_with(["claude", "whoami"])

    @pytest.mark.asyncio
    async def test_test_claude_whoami_failure(self):
        """Test failed claude whoami command."""
        validator = ClaudeAuthValidator()

        with patch(
            "epic_llm.utils.claude_auth_validator.check_cli_command"
        ) as mock_check:
            mock_check.return_value = False

            result = await validator._test_claude_whoami()

            assert result is False


class TestClaudeUserInfo:
    """Test Claude user information retrieval."""

    @pytest.mark.asyncio
    async def test_get_claude_username_from_credentials(self, temp_dir):
        """Test getting Claude username from credentials file."""
        credentials_dir = temp_dir / "claude"
        credentials_dir.mkdir()
        credentials_file = credentials_dir / ".credentials.json"
        credentials_file.write_text(
            json.dumps(
                {"username": "test_user@example.com", "session_key": "test_session_key"}
            )
        )

        validator = ClaudeAuthValidator(credentials_dir=credentials_dir)
        username = await validator.get_claude_username()

        assert username == "test_user@example.com"

    @pytest.mark.asyncio
    async def test_get_claude_username_no_file(self, temp_dir):
        """Test getting Claude username when credentials file doesn't exist."""
        credentials_dir = temp_dir / "claude"
        validator = ClaudeAuthValidator(credentials_dir=credentials_dir)

        username = await validator.get_claude_username()

        assert username is None

    @pytest.mark.asyncio
    async def test_get_claude_username_invalid_json(self, temp_dir):
        """Test getting Claude username with invalid JSON."""
        credentials_dir = temp_dir / "claude"
        credentials_dir.mkdir()
        credentials_file = credentials_dir / ".credentials.json"
        credentials_file.write_text("invalid json")

        validator = ClaudeAuthValidator(credentials_dir=credentials_dir)
        username = await validator.get_claude_username()

        assert username is None

    @pytest.mark.asyncio
    async def test_get_claude_version_success(self):
        """Test getting Claude CLI version successfully."""
        validator = ClaudeAuthValidator()

        with patch("asyncio.create_subprocess_exec") as mock_subprocess:
            mock_process = Mock()
            mock_process.communicate.return_value = (b"claude version 1.2.3\n", b"")
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process

            version = await validator.get_claude_version()

            assert "1.2.3" in version

    @pytest.mark.asyncio
    async def test_get_claude_version_failure(self):
        """Test getting Claude CLI version when command fails."""
        validator = ClaudeAuthValidator()

        with patch("asyncio.create_subprocess_exec") as mock_subprocess:
            mock_process = Mock()
            mock_process.communicate.return_value = (b"", b"command not found")
            mock_process.returncode = 1
            mock_subprocess.return_value = mock_process

            version = await validator.get_claude_version()

            assert version is None


class TestClaudeCredentialInfo:
    """Test Claude credential information retrieval."""

    @pytest.mark.asyncio
    async def test_get_credential_info_complete(self, temp_dir):
        """Test getting complete credential information."""
        credentials_dir = temp_dir / "claude"
        credentials_dir.mkdir(mode=0o700)  # Secure permissions
        credentials_file = credentials_dir / ".credentials.json"
        credentials_file.write_text(
            json.dumps(
                {"username": "test_user@example.com", "session_key": "test_session_key"}
            )
        )
        credentials_file.chmod(0o600)  # Secure file permissions

        validator = ClaudeAuthValidator(credentials_dir=credentials_dir)

        with patch.object(validator, "get_claude_version") as mock_version:
            mock_version.return_value = "1.2.3"

            info = await validator.get_credential_info()

            assert info["status"] == "authenticated"
            assert info["claude_username"] == "test_user@example.com"
            assert info["claude_version"] == "1.2.3"
            assert info["credentials_file_exists"] is True
            assert info["is_secure"] is True

    @pytest.mark.asyncio
    async def test_get_credential_info_no_credentials(self, temp_dir):
        """Test getting credential info when no credentials exist."""
        credentials_dir = temp_dir / "claude"
        validator = ClaudeAuthValidator(credentials_dir=credentials_dir)

        info = await validator.get_credential_info()

        assert info["status"] == "no_credentials"
        assert info["credentials_file_exists"] is False

    @pytest.mark.asyncio
    async def test_get_credential_info_insecure_permissions(self, temp_dir):
        """Test getting credential info with insecure file permissions."""
        credentials_dir = temp_dir / "claude"
        credentials_dir.mkdir(mode=0o755)  # Insecure permissions
        credentials_file = credentials_dir / ".credentials.json"
        credentials_file.write_text(
            json.dumps({"username": "test_user", "session_key": "test_session_key"})
        )
        credentials_file.chmod(0o644)  # Insecure file permissions

        validator = ClaudeAuthValidator(credentials_dir=credentials_dir)

        info = await validator.get_credential_info()

        assert info["is_secure"] is False


class TestClaudeSimpleCommand:
    """Test Claude simple command functionality."""

    @pytest.mark.asyncio
    async def test_simple_command_success(self):
        """Test successful simple Claude command."""
        validator = ClaudeAuthValidator()

        with patch(
            "epic_llm.utils.claude_auth_validator.check_cli_command"
        ) as mock_check:
            mock_check.return_value = True

            result = await validator.test_simple_command()

            assert result is True
            # Should test a simple command like help
            mock_check.assert_called_once_with(["claude", "--help"])

    @pytest.mark.asyncio
    async def test_simple_command_failure(self):
        """Test failed simple Claude command."""
        validator = ClaudeAuthValidator()

        with patch(
            "epic_llm.utils.claude_auth_validator.check_cli_command"
        ) as mock_check:
            mock_check.return_value = False

            result = await validator.test_simple_command()

            assert result is False


class TestClaudeAuthValidatorEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_validate_authentication_with_exception(self, temp_dir):
        """Test validation when an unexpected exception occurs."""
        validator = ClaudeAuthValidator()

        with patch.object(
            validator,
            "_check_claude_cli_installed",
            side_effect=Exception("Unexpected error"),
        ):
            result = await validator.validate_authentication()

            assert result == AuthStatus.FAILED

    @pytest.mark.asyncio
    async def test_credentials_file_permission_check(self, temp_dir):
        """Test checking credentials file permissions."""
        credentials_dir = temp_dir / "claude"
        credentials_dir.mkdir()
        credentials_file = credentials_dir / ".credentials.json"
        credentials_file.write_text(
            json.dumps({"username": "test", "session_key": "test"})
        )

        validator = ClaudeAuthValidator(credentials_dir=credentials_dir)

        # Test with different permission scenarios
        credentials_file.chmod(0o600)  # Secure
        info = await validator.get_credential_info()
        assert info.get("is_secure") is True

        credentials_file.chmod(0o644)  # Insecure
        info = await validator.get_credential_info()
        assert info.get("is_secure") is False

    @pytest.mark.asyncio
    async def test_concurrent_validation_calls(self):
        """Test concurrent validation calls."""
        validator = ClaudeAuthValidator()

        with patch.object(validator, "_check_claude_cli_installed") as mock_check:
            with patch.object(validator, "_test_claude_whoami") as mock_whoami:
                mock_check.return_value = True
                mock_whoami.return_value = True

                # Run multiple validations concurrently
                results = await asyncio.gather(
                    validator.validate_authentication(),
                    validator.validate_authentication(),
                    validator.validate_authentication(),
                )

                assert all(result == AuthStatus.AUTHENTICATED for result in results)
