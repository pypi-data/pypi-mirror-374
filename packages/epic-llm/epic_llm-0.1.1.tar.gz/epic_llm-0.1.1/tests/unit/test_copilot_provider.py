"""Tests for Copilot provider implementation."""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from epic_llm.managers.state import AuthStatus
from epic_llm.providers.copilot import CopilotProvider


class TestCopilotProviderInitialization:
    """Test CopilotProvider initialization."""

    def test_copilot_provider_creation(self):
        """Test creating Copilot provider instance."""
        with tempfile.TemporaryDirectory() as temp_dir:
            install_dir = Path(temp_dir) / "copilot"
            provider = CopilotProvider(install_dir=install_dir)

            assert provider.name == "copilot"
            assert provider.default_port == 8081  # Port 8081 to avoid conflict
            assert provider.install_dir == install_dir
            assert provider.repo_url == "https://github.com/ericc-ch/copilot-api.git"
            assert provider._auth_validator is not None

    def test_copilot_provider_default_install_dir(self):
        """Test Copilot provider with default install directory."""
        provider = CopilotProvider()

        expected_path = Path.home() / ".local/share/llm-api-gw/copilot-api"
        assert provider.install_dir == expected_path
        assert provider.default_port == 8081  # Changed from 8080

    @patch("epic_llm.providers.copilot.CopilotAuthValidator")
    def test_copilot_provider_auth_validator_initialization(self, mock_validator):
        """Test that Copilot provider initializes auth validator."""
        provider = CopilotProvider()

        mock_validator.assert_called_once()
        assert provider._auth_validator is not None


class TestCopilotProviderAuthentication:
    """Test Copilot provider authentication functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.install_dir = Path(temp_dir) / "copilot"
            self.provider = CopilotProvider(install_dir=self.install_dir)

    def test_is_authentication_required(self):
        """Test that Copilot provider requires authentication."""
        assert self.provider.is_authentication_required() is True

    @pytest.mark.asyncio
    async def test_validate_authentication_success(self):
        """Test successful authentication validation."""
        with patch.object(
            self.provider._auth_validator, "validate_authentication"
        ) as mock_validate:
            mock_validate.return_value = AuthStatus.AUTHENTICATED

            result = await self.provider.validate_authentication()

            assert result == AuthStatus.AUTHENTICATED
            mock_validate.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_authentication_failure(self):
        """Test failed authentication validation."""
        with patch.object(
            self.provider._auth_validator, "validate_authentication"
        ) as mock_validate:
            mock_validate.return_value = AuthStatus.FAILED

            result = await self.provider.validate_authentication()

            assert result == AuthStatus.FAILED

    @pytest.mark.asyncio
    async def test_get_credential_info(self):
        """Test getting credential information."""
        expected_info = {
            "status": "authenticated",
            "github_username": "test_user",
            "github_token_file_exists": True,
        }

        with patch.object(
            self.provider._auth_validator, "get_credential_info"
        ) as mock_get_info:
            mock_get_info.return_value = expected_info

            result = await self.provider.get_credential_info()

            assert result == expected_info
            mock_get_info.assert_called_once()


class TestCopilotProviderDependencies:
    """Test Copilot provider dependency management."""

    def setup_method(self):
        """Set up test fixtures."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.install_dir = Path(temp_dir) / "copilot"
            self.provider = CopilotProvider(install_dir=self.install_dir)

    def test_get_dependencies(self):
        """Test getting Copilot provider dependencies."""
        dependencies = self.provider.get_dependencies()

        assert len(dependencies) > 0
        # Should include Node, npm, and npx
        dep_names = [dep.name for dep in dependencies]
        assert "node" in dep_names
        assert "npm" in dep_names
        assert "copilot_api" in dep_names

    @pytest.mark.asyncio
    async def test_check_dependencies_success(self):
        """Test successful dependency checking."""
        with patch("epic_llm.providers.base.DependencyChecker") as mock_checker_class:
            mock_checker = Mock()
            mock_checker.check_and_install = AsyncMock(return_value=True)
            mock_checker_class.return_value = mock_checker

            result = await self.provider.check_dependencies()

            assert result is True

    @pytest.mark.asyncio
    async def test_check_dependencies_failure(self):
        """Test failed dependency checking."""
        with patch("epic_llm.providers.base.DependencyChecker") as mock_checker_class:
            mock_checker = Mock()
            mock_checker.check_and_install = AsyncMock(return_value=False)
            mock_checker_class.return_value = mock_checker

            result = await self.provider.check_dependencies()

            assert result is False


class TestCopilotProviderInstallation:
    """Test Copilot provider installation functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.install_dir = Path(temp_dir) / "copilot"
            self.provider = CopilotProvider(install_dir=self.install_dir)

    @pytest.mark.asyncio
    async def test_install_success(self):
        """Test successful installation."""
        with patch("epic_llm.utils.validators.check_npx_package") as mock_check:
            mock_check.return_value = True

            with patch.object(self.provider._state_manager, "set_provider_installed"):
                with patch("builtins.print") as mock_print:
                    await self.provider.install()

            mock_check.assert_called_with("copilot-api")
            mock_print.assert_called()

    @pytest.mark.asyncio
    async def test_install_failure(self):
        """Test installation failure."""
        with patch("epic_llm.utils.validators.check_npx_package") as mock_check:
            mock_check.return_value = False

            with pytest.raises(RuntimeError):
                await self.provider.install()

    @pytest.mark.asyncio
    async def test_install_already_exists(self):
        """Test installation when directory already exists."""
        # Create the install directory
        self.install_dir.mkdir(parents=True)

        with patch("builtins.print") as mock_print:
            with patch(
                "epic_llm.utils.validators.check_npx_package", return_value=True
            ):
                await self.provider.install()

        mock_print.assert_called()


class TestCopilotProviderStartStop:
    """Test Copilot provider start/stop functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.install_dir = Path(temp_dir) / "copilot"
            self.install_dir.mkdir(parents=True)
            self.provider = CopilotProvider(install_dir=self.install_dir)

    @pytest.mark.asyncio
    async def test_start_success(self):
        """Test successful provider start."""
        with patch.object(self.provider, "validate_authentication") as mock_validate:
            mock_validate.return_value = AuthStatus.AUTHENTICATED

            with patch("asyncio.create_subprocess_exec") as mock_subprocess:
                mock_process = Mock()
                mock_process.pid = 12345
                mock_subprocess.return_value = mock_process

                with patch.object(self.provider, "_update_process_state"):
                    await self.provider.start(port=8081)

                mock_subprocess.assert_called()

    @pytest.mark.asyncio
    async def test_start_not_installed(self):
        """Test start when provider is not installed."""
        # Remove install directory
        if self.install_dir.exists():
            import shutil

            shutil.rmtree(self.install_dir)

        with patch("builtins.print") as mock_print:
            await self.provider.start(port=8081)

        mock_print.assert_called()

    @pytest.mark.asyncio
    async def test_start_authentication_required(self):
        """Test start when authentication is required."""
        with patch.object(self.provider, "validate_authentication") as mock_validate:
            mock_validate.return_value = AuthStatus.REQUIRED

            with patch.object(
                self.provider, "handle_authentication_prompt"
            ) as mock_prompt:
                with patch("builtins.print") as mock_print:
                    await self.provider.start(port=8081)

                mock_prompt.assert_called()
                mock_print.assert_called()

    @pytest.mark.asyncio
    async def test_start_authentication_failed(self):
        """Test start when authentication fails."""
        with patch.object(self.provider, "validate_authentication") as mock_validate:
            mock_validate.return_value = AuthStatus.FAILED

            with patch.object(
                self.provider, "handle_authentication_prompt"
            ) as mock_prompt:
                with patch("builtins.print") as mock_print:
                    await self.provider.start(port=8081)

                mock_prompt.assert_called()
                mock_print.assert_called()

    @pytest.mark.asyncio
    async def test_stop_success(self):
        """Test successful provider stop."""
        # Mock running process
        mock_process = Mock()
        mock_process.terminate = Mock()
        mock_process.wait = AsyncMock()
        self.provider.process = mock_process

        with patch.object(self.provider, "_clear_process_state"):
            await self.provider.stop()

        mock_process.terminate.assert_called()

    @pytest.mark.asyncio
    async def test_stop_no_process(self):
        """Test stop when no process is running."""
        self.provider.process = None

        with patch("builtins.print") as mock_print:
            await self.provider.stop()

        mock_print.assert_called()


class TestCopilotProviderHealthCheck:
    """Test Copilot provider health check functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.install_dir = Path(temp_dir) / "copilot"
            self.provider = CopilotProvider(install_dir=self.install_dir)

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = Mock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None

            mock_response = Mock()
            mock_response.status_code = 200
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await self.provider.health_check(port=8081)

            assert result is True
            mock_client.get.assert_called_once_with("http://localhost:8081/health")

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """Test failed health check."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = Mock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None

            mock_response = Mock()
            mock_response.status_code = 500
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await self.provider.health_check(port=8081)

            assert result is False

    @pytest.mark.asyncio
    async def test_health_check_exception(self):
        """Test health check with connection exception."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = Mock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.side_effect = Exception("Connection failed")
            mock_client_class.return_value = mock_client

            result = await self.provider.health_check(port=8081)

            assert result is False


class TestCopilotProviderProcessMonitoring:
    """Test Copilot provider process monitoring functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.install_dir = Path(temp_dir) / "copilot"
            self.provider = CopilotProvider(install_dir=self.install_dir)

    @pytest.mark.asyncio
    async def test_handle_authentication_prompt(self):
        """Test handling authentication prompt."""
        with patch("builtins.print") as mock_print:
            await self.provider.handle_authentication_prompt()

        mock_print.assert_called()

    def test_process_output_line_auth_required(self):
        """Test processing output line that indicates auth is required."""
        auth_line = "GitHub authentication required"

        with patch.object(
            self.provider, "set_authentication_status"
        ) as mock_set_status:
            self.provider.process_output_line(auth_line)

        mock_set_status.assert_called_with(AuthStatus.REQUIRED)

    def test_process_output_line_normal(self):
        """Test processing normal output line."""
        normal_line = "Server starting on port 8081"

        # Should not raise an exception
        self.provider.process_output_line(normal_line)

    def test_process_output_line_error(self):
        """Test processing error output line."""
        error_line = "Error: GitHub token not found"

        with patch.object(
            self.provider, "set_authentication_status"
        ) as mock_set_status:
            self.provider.process_output_line(error_line)

        # Should detect auth error and set status
        mock_set_status.assert_called_with(AuthStatus.FAILED)
