"""Tests for main CLI application."""

from unittest.mock import AsyncMock, Mock, patch

from typer.testing import CliRunner

from epic_llm.main import app


class TestCLICommands:
    """Test CLI command functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("epic_llm.main.ProviderManager")
    def test_install_command_all_providers(self, mock_provider_manager):
        """Test install command with all providers."""
        mock_manager = Mock()
        mock_manager.initialize_providers = Mock()
        mock_manager.install_providers = AsyncMock()
        mock_provider_manager.return_value = mock_manager

        result = self.runner.invoke(app, ["install"])

        assert result.exit_code == 0
        mock_manager.initialize_providers.assert_called_once_with(None)

    @patch("epic_llm.main.ProviderManager")
    def test_install_command_specific_providers(self, mock_provider_manager):
        """Test install command with specific providers."""
        mock_manager = Mock()
        mock_manager.initialize_providers = Mock()
        mock_manager.install_providers = AsyncMock()
        mock_provider_manager.return_value = mock_manager

        result = self.runner.invoke(app, ["install", "claude", "copilot"])

        assert result.exit_code == 0
        mock_manager.initialize_providers.assert_called_once_with(["claude", "copilot"])

    @patch("epic_llm.main.ProviderManager")
    def test_start_command_basic(self, mock_provider_manager):
        """Test start command without port specifications."""
        mock_manager = Mock()
        mock_manager.initialize_providers = Mock()
        mock_manager.start_providers = AsyncMock()
        mock_provider_manager.return_value = mock_manager

        result = self.runner.invoke(app, ["start"])

        assert result.exit_code == 0
        mock_manager.initialize_providers.assert_called_once_with(None)
        mock_manager.start_providers.assert_called_once_with(None, {})

    @patch("epic_llm.main.ProviderManager")
    def test_start_command_with_ports(self, mock_provider_manager):
        """Test start command with port specifications."""
        mock_manager = Mock()
        mock_manager.initialize_providers = Mock()
        mock_manager.start_providers = AsyncMock()
        mock_provider_manager.return_value = mock_manager

        result = self.runner.invoke(
            app, ["start", "--port", "claude:8001", "--port", "copilot:8002"]
        )

        assert result.exit_code == 0
        expected_port_map = {"claude": 8001, "copilot": 8002}
        mock_manager.start_providers.assert_called_once_with(None, expected_port_map)

    @patch("epic_llm.main.ProviderManager")
    @patch("epic_llm.main.console")
    def test_start_command_invalid_port(self, mock_console, mock_provider_manager):
        """Test start command with invalid port number."""
        mock_manager = Mock()
        mock_manager.initialize_providers = Mock()
        mock_provider_manager.return_value = mock_manager

        result = self.runner.invoke(app, ["start", "--port", "claude:invalid"])

        assert result.exit_code == 0
        mock_console.print.assert_called_with("[red]Invalid port number: invalid[/red]")

    @patch("epic_llm.main.ProviderManager")
    def test_stop_command(self, mock_provider_manager):
        """Test stop command."""
        mock_manager = Mock()
        mock_manager.initialize_providers = Mock()
        mock_manager.stop_providers = AsyncMock()
        mock_provider_manager.return_value = mock_manager

        result = self.runner.invoke(app, ["stop"])

        assert result.exit_code == 0
        mock_manager.initialize_providers.assert_called_once_with()
        mock_manager.stop_providers.assert_called_once_with(None)

    @patch("epic_llm.main.ProviderManager")
    def test_stop_command_specific_providers(self, mock_provider_manager):
        """Test stop command with specific providers."""
        mock_manager = Mock()
        mock_manager.initialize_providers = Mock()
        mock_manager.stop_providers = AsyncMock()
        mock_provider_manager.return_value = mock_manager

        result = self.runner.invoke(app, ["stop", "claude"])

        assert result.exit_code == 0
        mock_manager.stop_providers.assert_called_once_with(["claude"])

    @patch("epic_llm.main.ProviderManager")
    def test_status_command(self, mock_provider_manager):
        """Test status command."""
        mock_manager = Mock()
        mock_manager.initialize_providers = Mock()
        mock_manager.show_status = AsyncMock()
        mock_provider_manager.return_value = mock_manager

        result = self.runner.invoke(app, ["status"])

        assert result.exit_code == 0
        mock_manager.initialize_providers.assert_called_once_with()
        mock_manager.show_status.assert_called_once()

    @patch("epic_llm.main.ProviderManager")
    @patch("epic_llm.main.console")
    def test_check_command_success(self, mock_console, mock_provider_manager):
        """Test check command with successful dependency check."""
        mock_provider = Mock()
        mock_provider.check_dependencies = AsyncMock(return_value=True)

        mock_manager = Mock()
        mock_manager.initialize_providers = Mock()
        mock_manager.providers = {"claude": mock_provider, "copilot": mock_provider}
        mock_provider_manager.return_value = mock_manager

        result = self.runner.invoke(app, ["check"])

        assert result.exit_code == 0
        mock_console.print.assert_any_call(
            "\n[green]All dependencies satisfied![/green]"
        )

    @patch("epic_llm.main.ProviderManager")
    @patch("epic_llm.main.console")
    def test_check_command_failure(self, mock_console, mock_provider_manager):
        """Test check command with failed dependency check."""
        mock_provider = Mock()
        mock_provider.check_dependencies = AsyncMock(return_value=False)

        mock_manager = Mock()
        mock_manager.initialize_providers = Mock()
        mock_manager.providers = {"claude": mock_provider}
        mock_provider_manager.return_value = mock_manager

        result = self.runner.invoke(app, ["check"])

        assert result.exit_code == 0
        mock_console.print.assert_any_call(
            "\n[red]Some dependencies are missing.[/red]"
        )

    @patch("epic_llm.main.ProviderManager")
    @patch("epic_llm.main.console")
    def test_check_command_with_auto_install(self, mock_console, mock_provider_manager):
        """Test check command with auto-install flag."""
        mock_provider = Mock()
        mock_provider.check_dependencies = AsyncMock(return_value=True)

        mock_manager = Mock()
        mock_manager.initialize_providers = Mock()
        mock_manager.providers = {"claude": mock_provider}
        mock_provider_manager.return_value = mock_manager

        result = self.runner.invoke(app, ["check", "--install"])

        assert result.exit_code == 0
        mock_provider.check_dependencies.assert_called_with(auto_install=True)

    def test_list_command(self):
        """Test list command."""
        with patch(
            "epic_llm.providers.PROVIDERS", {"claude": Mock(), "copilot": Mock()}
        ):
            with patch("epic_llm.main.console") as mock_console:
                result = self.runner.invoke(app, ["list"])

                assert result.exit_code == 0
                mock_console.print.assert_any_call("[bold]Available providers:[/bold]")


class TestAuthStatusCommand:
    """Test auth-status CLI command functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("epic_llm.main.ProviderManager")
    @patch("epic_llm.main.console")
    def test_auth_status_no_auth_required(self, mock_console, mock_provider_manager):
        """Test auth-status for provider that doesn't require auth."""
        mock_provider = Mock()
        mock_provider.is_authentication_required.return_value = False

        mock_manager = Mock()
        mock_manager.initialize_providers = Mock()
        mock_manager.providers = {"test_provider": mock_provider}
        mock_provider_manager.return_value = mock_manager

        result = self.runner.invoke(app, ["auth-status"])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("  ➖ Authentication not required")

    @patch("epic_llm.main.ProviderManager")
    @patch("epic_llm.main.console")
    def test_auth_status_authenticated(self, mock_console, mock_provider_manager):
        """Test auth-status for authenticated provider."""
        from epic_llm.managers.state import AuthStatus

        mock_provider = Mock()
        mock_provider.is_authentication_required.return_value = True
        mock_provider.get_authentication_status.return_value = AuthStatus.AUTHENTICATED
        mock_provider.validate_authentication = AsyncMock(
            return_value=AuthStatus.AUTHENTICATED
        )
        mock_provider.get_credential_info = AsyncMock(
            return_value={"status": "authenticated"}
        )

        mock_manager = Mock()
        mock_manager.initialize_providers = Mock()
        mock_manager.providers = {"claude": mock_provider}
        mock_provider_manager.return_value = mock_manager

        result = self.runner.invoke(app, ["auth-status"])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("  Status: ✅ Authenticated")

    @patch("epic_llm.main.ProviderManager")
    @patch("epic_llm.main.console")
    def test_auth_status_claude_specific_info(
        self, mock_console, mock_provider_manager
    ):
        """Test auth-status with Claude-specific credential info."""
        from epic_llm.managers.state import AuthStatus

        mock_provider = Mock()
        mock_provider.is_authentication_required.return_value = True
        mock_provider.get_authentication_status.return_value = AuthStatus.AUTHENTICATED
        mock_provider.validate_authentication = AsyncMock(
            return_value=AuthStatus.AUTHENTICATED
        )
        mock_provider.get_credential_info = AsyncMock(
            return_value={
                "status": "authenticated",
                "claude_username": "test_user",
                "claude_version": "1.0.0",
                "credentials_file_exists": True,
                "is_secure": True,
            }
        )

        mock_manager = Mock()
        mock_manager.initialize_providers = Mock()
        mock_manager.providers = {"claude": mock_provider}
        mock_provider_manager.return_value = mock_manager

        result = self.runner.invoke(app, ["auth-status"])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("  Claude Username: test_user")
        mock_console.print.assert_any_call("  Claude CLI Version: 1.0.0")
        mock_console.print.assert_any_call("  File Security: ✅ Secure")

    @patch("epic_llm.main.ProviderManager")
    @patch("epic_llm.main.console")
    def test_auth_status_copilot_specific_info(
        self, mock_console, mock_provider_manager
    ):
        """Test auth-status with Copilot-specific credential info."""
        from epic_llm.managers.state import AuthStatus

        mock_provider = Mock()
        mock_provider.is_authentication_required.return_value = True
        mock_provider.get_authentication_status.return_value = AuthStatus.AUTHENTICATED
        mock_provider.validate_authentication = AsyncMock(
            return_value=AuthStatus.AUTHENTICATED
        )
        mock_provider.get_credential_info = AsyncMock(
            return_value={
                "status": "authenticated",
                "github_username": "test_user",
                "github_token_file_exists": True,
                "is_secure": True,
                "copilot_subscription": {"active": True},
            }
        )

        mock_manager = Mock()
        mock_manager.initialize_providers = Mock()
        mock_manager.providers = {"copilot": mock_provider}
        mock_provider_manager.return_value = mock_manager

        result = self.runner.invoke(app, ["auth-status"])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("  GitHub Username: test_user")
        mock_console.print.assert_any_call("  Copilot Subscription: ✅ Active")

    @patch("epic_llm.main.ProviderManager")
    @patch("epic_llm.main.console")
    def test_auth_status_no_credentials(self, mock_console, mock_provider_manager):
        """Test auth-status with no credential file found."""
        from epic_llm.managers.state import AuthStatus

        mock_provider = Mock()
        mock_provider.is_authentication_required.return_value = True
        mock_provider.get_authentication_status.return_value = AuthStatus.REQUIRED
        mock_provider.validate_authentication = AsyncMock(
            return_value=AuthStatus.REQUIRED
        )
        mock_provider.get_credential_info = AsyncMock(
            return_value={"status": "no_credentials"}
        )
        mock_provider.handle_authentication_prompt = AsyncMock()

        mock_manager = Mock()
        mock_manager.initialize_providers = Mock()
        mock_manager.providers = {"test_provider": mock_provider}
        mock_provider_manager.return_value = mock_manager

        result = self.runner.invoke(app, ["auth-status"])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("  No credential file found")
        mock_provider.handle_authentication_prompt.assert_called_once()

    @patch("epic_llm.main.ProviderManager")
    @patch("epic_llm.main.console")
    def test_auth_status_error_handling(self, mock_console, mock_provider_manager):
        """Test auth-status with error during credential check."""
        from epic_llm.managers.state import AuthStatus

        mock_provider = Mock()
        mock_provider.is_authentication_required.return_value = True
        mock_provider.get_authentication_status.return_value = AuthStatus.FAILED
        mock_provider.validate_authentication = AsyncMock(
            side_effect=Exception("Test error")
        )

        mock_manager = Mock()
        mock_manager.initialize_providers = Mock()
        mock_manager.providers = {"test_provider": mock_provider}
        mock_provider_manager.return_value = mock_manager

        result = self.runner.invoke(app, ["auth-status"])

        assert result.exit_code == 0
        mock_console.print.assert_any_call(
            "  [red]Error checking credentials: Test error[/red]"
        )


class TestCLIErrorHandling:
    """Test CLI error handling scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("epic_llm.main.ProviderManager")
    def test_async_exception_handling(self, mock_provider_manager):
        """Test handling of async exceptions in CLI commands."""
        mock_manager = Mock()
        mock_manager.initialize_providers = Mock()
        mock_manager.start_providers = AsyncMock(
            side_effect=Exception("Test exception")
        )
        mock_provider_manager.return_value = mock_manager

        # Should not crash but handle the exception
        result = self.runner.invoke(app, ["start"])

        # The exception should be handled by asyncio.run()
        assert isinstance(result.exception, Exception)

    @patch("epic_llm.main.ProviderManager")
    def test_initialization_failure(self, mock_provider_manager):
        """Test handling when provider manager initialization fails."""
        mock_provider_manager.side_effect = Exception("Initialization failed")

        result = self.runner.invoke(app, ["status"])

        assert isinstance(result.exception, Exception)
