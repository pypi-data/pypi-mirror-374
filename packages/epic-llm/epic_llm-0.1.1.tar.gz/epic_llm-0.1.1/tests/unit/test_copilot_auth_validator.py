"""Tests for Copilot authentication validator."""

import asyncio
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from epic_llm.managers.state import AuthStatus
from epic_llm.utils.copilot_auth_validator import CopilotAuthValidator


class TestCopilotAuthValidatorInitialization:
    """Test CopilotAuthValidator initialization."""

    def test_validator_creation(self):
        """Test creating Copilot auth validator instance."""
        validator = CopilotAuthValidator()
        assert validator is not None

    def test_validator_with_custom_token_dir(self, temp_dir):
        """Test validator with custom token directory."""
        custom_dir = temp_dir / "custom_copilot"
        validator = CopilotAuthValidator(token_dir=custom_dir)
        assert validator.token_dir == custom_dir

    def test_validator_default_token_dir(self):
        """Test validator with default token directory."""
        validator = CopilotAuthValidator()
        expected_path = Path.home() / ".local/share/copilot-api"
        assert validator.token_dir == expected_path


class TestCopilotAuthenticationValidation:
    """Test Copilot authentication validation functionality."""

    @pytest.mark.asyncio
    async def test_validate_authentication_api_not_available(self):
        """Test validation when Copilot API is not available."""
        validator = CopilotAuthValidator()

        with patch.object(validator, "_check_copilot_api_available") as mock_check:
            mock_check.return_value = False

            result = await validator.validate_authentication()

            assert result == AuthStatus.FAILED

    @pytest.mark.asyncio
    async def test_validate_authentication_no_token_file(self, temp_dir):
        """Test validation when GitHub token file doesn't exist."""
        token_dir = temp_dir / "copilot-api"
        validator = CopilotAuthValidator(token_dir=token_dir)

        with patch.object(validator, "_check_copilot_api_available") as mock_check:
            mock_check.return_value = True

            result = await validator.validate_authentication()

            assert result == AuthStatus.REQUIRED

    @pytest.mark.asyncio
    async def test_validate_authentication_invalid_token(self, temp_dir):
        """Test validation with invalid GitHub token."""
        token_dir = temp_dir / "copilot-api"
        token_dir.mkdir()
        token_file = token_dir / "github_token"
        token_file.write_text("invalid_token")

        validator = CopilotAuthValidator(token_dir=token_dir)

        with patch.object(validator, "_check_copilot_api_available") as mock_check:
            with patch.object(validator, "_test_github_token") as mock_test:
                mock_check.return_value = True
                mock_test.return_value = False

                result = await validator.validate_authentication()

                assert result == AuthStatus.FAILED

    @pytest.mark.asyncio
    async def test_validate_authentication_success(self, temp_dir):
        """Test successful authentication validation."""
        token_dir = temp_dir / "copilot-api"
        token_dir.mkdir()
        token_file = token_dir / "github_token"
        token_file.write_text("ghp_valid_token_123456789")

        validator = CopilotAuthValidator(token_dir=token_dir)

        with patch.object(validator, "_check_copilot_api_available") as mock_check:
            with patch.object(validator, "_test_github_token") as mock_test:
                mock_check.return_value = True
                mock_test.return_value = True

                result = await validator.validate_authentication()

                assert result == AuthStatus.AUTHENTICATED

    @pytest.mark.asyncio
    async def test_validate_authentication_read_token_fails(self, temp_dir):
        """Test validation when reading token file fails."""
        token_dir = temp_dir / "copilot-api"
        token_dir.mkdir()
        # Create file with no read permissions
        token_file = token_dir / "github_token"
        token_file.write_text("token")
        token_file.chmod(0o000)

        validator = CopilotAuthValidator(token_dir=token_dir)

        with patch.object(validator, "_check_copilot_api_available") as mock_check:
            mock_check.return_value = True

            result = await validator.validate_authentication()

            assert result == AuthStatus.FAILED


class TestCopilotApiChecking:
    """Test Copilot API checking functionality."""

    @pytest.mark.asyncio
    async def test_check_copilot_api_available_success(self):
        """Test successful Copilot API availability check."""
        validator = CopilotAuthValidator()

        with patch(
            "epic_llm.utils.copilot_auth_validator.check_npx_package"
        ) as mock_check:
            mock_check.return_value = True

            result = await validator._check_copilot_api_available()

            assert result is True
            mock_check.assert_called_once_with("copilot-api")

    @pytest.mark.asyncio
    async def test_check_copilot_api_available_failure(self):
        """Test failed Copilot API availability check."""
        validator = CopilotAuthValidator()

        with patch(
            "epic_llm.utils.copilot_auth_validator.check_npx_package"
        ) as mock_check:
            mock_check.return_value = False

            result = await validator._check_copilot_api_available()

            assert result is False


class TestGitHubTokenOperations:
    """Test GitHub token reading and validation."""

    @pytest.mark.asyncio
    async def test_read_github_token_success(self, temp_dir):
        """Test successfully reading GitHub token."""
        token_dir = temp_dir / "copilot-api"
        token_dir.mkdir()
        token_file = token_dir / "github_token"
        token_file.write_text("ghp_test_token_123456789")

        validator = CopilotAuthValidator(token_dir=token_dir)
        token = await validator._read_github_token()

        assert token == "ghp_test_token_123456789"

    @pytest.mark.asyncio
    async def test_read_github_token_file_not_exists(self, temp_dir):
        """Test reading GitHub token when file doesn't exist."""
        token_dir = temp_dir / "copilot-api"
        validator = CopilotAuthValidator(token_dir=token_dir)

        token = await validator._read_github_token()

        assert token is None

    @pytest.mark.asyncio
    async def test_read_github_token_permission_error(self, temp_dir):
        """Test reading GitHub token with permission error."""
        token_dir = temp_dir / "copilot-api"
        token_dir.mkdir()
        token_file = token_dir / "github_token"
        token_file.write_text("token")
        token_file.chmod(0o000)  # No permissions

        validator = CopilotAuthValidator(token_dir=token_dir)
        token = await validator._read_github_token()

        assert token is None

    @pytest.mark.asyncio
    async def test_test_github_token_success(self):
        """Test successful GitHub token validation."""
        validator = CopilotAuthValidator()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "login": "test_user",
            "id": 12345,
            "name": "Test User",
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = Mock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await validator._test_github_token("valid_token")

            assert result is True

    @pytest.mark.asyncio
    async def test_test_github_token_failure(self):
        """Test failed GitHub token validation."""
        validator = CopilotAuthValidator()

        mock_response = Mock()
        mock_response.status_code = 401

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = Mock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await validator._test_github_token("invalid_token")

            assert result is False

    @pytest.mark.asyncio
    async def test_test_github_token_exception(self):
        """Test GitHub token validation with network exception."""
        validator = CopilotAuthValidator()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = Mock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.side_effect = Exception("Network error")
            mock_client_class.return_value = mock_client

            result = await validator._test_github_token("token")

            assert result is False


class TestGitHubUserInfo:
    """Test GitHub user information retrieval."""

    @pytest.mark.asyncio
    async def test_get_github_username_success(self, temp_dir):
        """Test getting GitHub username successfully."""
        token_dir = temp_dir / "copilot-api"
        token_dir.mkdir()
        token_file = token_dir / "github_token"
        token_file.write_text("valid_token")

        validator = CopilotAuthValidator(token_dir=token_dir)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"login": "test_user"}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = Mock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            username = await validator.get_github_username()

            assert username == "test_user"

    @pytest.mark.asyncio
    async def test_get_github_username_no_token(self, temp_dir):
        """Test getting GitHub username when no token exists."""
        token_dir = temp_dir / "copilot-api"
        validator = CopilotAuthValidator(token_dir=token_dir)

        username = await validator.get_github_username()

        assert username is None

    @pytest.mark.asyncio
    async def test_get_github_username_api_failure(self, temp_dir):
        """Test getting GitHub username when API call fails."""
        token_dir = temp_dir / "copilot-api"
        token_dir.mkdir()
        token_file = token_dir / "github_token"
        token_file.write_text("invalid_token")

        validator = CopilotAuthValidator(token_dir=token_dir)

        mock_response = Mock()
        mock_response.status_code = 401

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = Mock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            username = await validator.get_github_username()

            assert username is None


class TestCopilotSubscriptionChecking:
    """Test Copilot subscription checking functionality."""

    @pytest.mark.asyncio
    async def test_check_copilot_subscription_success(self, temp_dir):
        """Test successful Copilot subscription check."""
        token_dir = temp_dir / "copilot-api"
        token_dir.mkdir()
        token_file = token_dir / "github_token"
        token_file.write_text("valid_token")

        validator = CopilotAuthValidator(token_dir=token_dir)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "active"}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = Mock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            subscription = await validator.check_copilot_subscription()

            assert subscription == {"status": "active"}

    @pytest.mark.asyncio
    async def test_check_copilot_subscription_no_access(self, temp_dir):
        """Test Copilot subscription check with no access."""
        token_dir = temp_dir / "copilot-api"
        token_dir.mkdir()
        token_file = token_dir / "github_token"
        token_file.write_text("limited_token")

        validator = CopilotAuthValidator(token_dir=token_dir)

        mock_response = Mock()
        mock_response.status_code = 403

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = Mock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            subscription = await validator.check_copilot_subscription()

            assert subscription is None

    @pytest.mark.asyncio
    async def test_check_copilot_subscription_no_token(self, temp_dir):
        """Test Copilot subscription check when no token exists."""
        token_dir = temp_dir / "copilot-api"
        validator = CopilotAuthValidator(token_dir=token_dir)

        subscription = await validator.check_copilot_subscription()

        assert subscription is None


class TestCopilotCredentialInfo:
    """Test Copilot credential information retrieval."""

    @pytest.mark.asyncio
    async def test_get_credential_info_complete(self, temp_dir):
        """Test getting complete credential information."""
        token_dir = temp_dir / "copilot-api"
        token_dir.mkdir(mode=0o700)
        token_file = token_dir / "github_token"
        token_file.write_text("ghp_valid_token_123456789")
        token_file.chmod(0o600)

        validator = CopilotAuthValidator(token_dir=token_dir)

        mock_user_response = Mock()
        mock_user_response.status_code = 200
        mock_user_response.json.return_value = {"login": "test_user"}

        mock_subscription_response = Mock()
        mock_subscription_response.status_code = 200
        mock_subscription_response.json.return_value = {"status": "active"}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = Mock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.side_effect = [
                mock_user_response,
                mock_subscription_response,
            ]
            mock_client_class.return_value = mock_client

            info = await validator.get_credential_info()

            assert info["status"] == "authenticated"
            assert info["github_username"] == "test_user"
            assert info["github_token_file_exists"] is True
            assert info["is_secure"] is True
            assert info["copilot_subscription"] == {"status": "active"}

    @pytest.mark.asyncio
    async def test_get_credential_info_no_token(self, temp_dir):
        """Test getting credential info when no token exists."""
        token_dir = temp_dir / "copilot-api"
        validator = CopilotAuthValidator(token_dir=token_dir)

        info = await validator.get_credential_info()

        assert info["status"] == "no_credentials"
        assert info["github_token_file_exists"] is False

    @pytest.mark.asyncio
    async def test_get_credential_info_insecure_permissions(self, temp_dir):
        """Test getting credential info with insecure permissions."""
        token_dir = temp_dir / "copilot-api"
        token_dir.mkdir(mode=0o755)
        token_file = token_dir / "github_token"
        token_file.write_text("token")
        token_file.chmod(0o644)  # Insecure permissions

        validator = CopilotAuthValidator(token_dir=token_dir)

        info = await validator.get_credential_info()

        assert info["is_secure"] is False


class TestCopilotApiAuthCommand:
    """Test Copilot API auth command functionality."""

    @pytest.mark.asyncio
    async def test_copilot_api_auth_command_success(self):
        """Test successful Copilot API auth command."""
        validator = CopilotAuthValidator()

        with patch(
            "epic_llm.utils.copilot_auth_validator.check_cli_command"
        ) as mock_check:
            mock_check.return_value = True

            result = await validator.test_copilot_api_auth_command()

            assert result is True
            mock_check.assert_called_once_with(["npx", "copilot-api", "auth", "--help"])

    @pytest.mark.asyncio
    async def test_copilot_api_auth_command_failure(self):
        """Test failed Copilot API auth command."""
        validator = CopilotAuthValidator()

        with patch(
            "epic_llm.utils.copilot_auth_validator.check_cli_command"
        ) as mock_check:
            mock_check.return_value = False

            result = await validator.test_copilot_api_auth_command()

            assert result is False


class TestCopilotAuthValidatorEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_validate_authentication_with_exception(self):
        """Test validation when an unexpected exception occurs."""
        validator = CopilotAuthValidator()

        with patch.object(
            validator,
            "_check_copilot_api_available",
            side_effect=Exception("Unexpected error"),
        ):
            result = await validator.validate_authentication()

            assert result == AuthStatus.FAILED

    @pytest.mark.asyncio
    async def test_token_file_permission_check(self, temp_dir):
        """Test checking token file permissions."""
        token_dir = temp_dir / "copilot-api"
        token_dir.mkdir()
        token_file = token_dir / "github_token"
        token_file.write_text("token")

        validator = CopilotAuthValidator(token_dir=token_dir)

        # Test with different permission scenarios
        token_file.chmod(0o600)  # Secure
        info = await validator.get_credential_info()
        assert info.get("is_secure") is True

        token_file.chmod(0o644)  # Insecure
        info = await validator.get_credential_info()
        assert info.get("is_secure") is False

    @pytest.mark.asyncio
    async def test_concurrent_validation_calls(self):
        """Test concurrent validation calls."""
        validator = CopilotAuthValidator()

        with patch.object(validator, "_check_copilot_api_available") as mock_check:
            with patch.object(validator, "_test_github_token") as mock_test:
                mock_check.return_value = True
                mock_test.return_value = True

                # Mock token file
                with patch.object(validator, "_read_github_token") as mock_read:
                    mock_read.return_value = "valid_token"

                    # Run multiple validations concurrently
                    results = await asyncio.gather(
                        validator.validate_authentication(),
                        validator.validate_authentication(),
                        validator.validate_authentication(),
                    )

                    assert all(result == AuthStatus.AUTHENTICATED for result in results)
