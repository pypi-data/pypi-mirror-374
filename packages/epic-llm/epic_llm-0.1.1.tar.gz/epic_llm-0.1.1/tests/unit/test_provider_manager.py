"""Tests for provider manager functionality - working implementation."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from epic_llm.managers.provider import ProviderManager
from epic_llm.managers.state import AuthStatus


class TestProviderManagerInitialization:
    """Test ProviderManager initialization."""

    def test_provider_manager_creation(self):
        """Test creating ProviderManager instance."""
        manager = ProviderManager()

        assert manager is not None
        assert manager.providers == {}
        assert manager.port_manager is not None
        assert manager.console is not None
        assert manager._state_manager is not None

    def test_provider_manager_attributes(self):
        """Test ProviderManager has correct attributes."""
        manager = ProviderManager()

        assert hasattr(manager, "providers")
        assert hasattr(manager, "port_manager")
        assert hasattr(manager, "console")
        assert hasattr(manager, "_state_manager")


class TestProviderInitialization:
    """Test provider initialization functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ProviderManager()

    @patch("epic_llm.managers.provider.PROVIDERS")
    def test_initialize_providers_all(self, mock_providers):
        """Test initializing all providers."""
        # Mock provider classes
        mock_claude = Mock()
        mock_copilot = Mock()
        mock_claude_instance = Mock()
        mock_copilot_instance = Mock()
        mock_claude.return_value = mock_claude_instance
        mock_copilot.return_value = mock_copilot_instance

        mock_providers_dict = {"claude": mock_claude, "copilot": mock_copilot}
        mock_providers.keys.return_value = mock_providers_dict.keys()
        mock_providers.__getitem__.side_effect = lambda key: mock_providers_dict[key]
        mock_providers.__contains__.side_effect = lambda key: key in mock_providers_dict

        self.manager.initialize_providers()

        assert len(self.manager.providers) == 2
        assert "claude" in self.manager.providers
        assert "copilot" in self.manager.providers
        mock_claude.assert_called_once()
        mock_copilot.assert_called_once()

    @patch("epic_llm.managers.provider.PROVIDERS")
    def test_initialize_providers_specific(self, mock_providers):
        """Test initializing specific providers."""
        mock_claude = Mock()
        mock_claude_instance = Mock()
        mock_claude.return_value = mock_claude_instance

        mock_providers_dict = {"claude": mock_claude}
        mock_providers.__getitem__.side_effect = lambda key: mock_providers_dict.get(
            key
        )
        mock_providers.__contains__.side_effect = lambda key: key in mock_providers_dict

        self.manager.initialize_providers(["claude"])

        assert len(self.manager.providers) == 1
        assert "claude" in self.manager.providers
        mock_claude.assert_called_once()

    @patch("epic_llm.managers.provider.PROVIDERS")
    def test_initialize_providers_nonexistent(self, mock_providers):
        """Test initializing non-existent provider."""
        mock_providers.__contains__.return_value = False

        with patch.object(self.manager.console, "print") as mock_print:
            self.manager.initialize_providers(["nonexistent"])

            mock_print.assert_called_once_with(
                "[red]Unknown provider: nonexistent[/red]"
            )
            assert len(self.manager.providers) == 0


class TestProviderInstallation:
    """Test provider installation functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ProviderManager()

    @pytest.mark.asyncio
    async def test_install_providers_all(self):
        """Test installing all providers."""
        # Mock providers
        mock_provider1 = Mock()
        mock_provider1.install = AsyncMock()
        mock_provider2 = Mock()
        mock_provider2.install = AsyncMock()

        self.manager.providers = {
            "provider1": mock_provider1,
            "provider2": mock_provider2,
        }

        with patch.object(self.manager.console, "print"):
            result = await self.manager.install_providers()

        assert result is True
        mock_provider1.install.assert_called_once()
        mock_provider2.install.assert_called_once()

    @pytest.mark.asyncio
    async def test_install_providers_specific(self):
        """Test installing specific providers."""
        mock_provider1 = Mock()
        mock_provider1.install = AsyncMock()
        mock_provider2 = Mock()
        mock_provider2.install = AsyncMock()

        self.manager.providers = {
            "provider1": mock_provider1,
            "provider2": mock_provider2,
        }

        with patch.object(self.manager.console, "print"):
            result = await self.manager.install_providers(["provider1"])

        assert result is True
        mock_provider1.install.assert_called_once()
        mock_provider2.install.assert_not_called()

    @pytest.mark.asyncio
    async def test_install_providers_not_initialized(self):
        """Test installing provider that's not initialized."""
        with patch.object(self.manager.console, "print") as mock_print:
            result = await self.manager.install_providers(["nonexistent"])

        assert result is False
        mock_print.assert_called_with("[red]Provider nonexistent not initialized[/red]")

    @pytest.mark.asyncio
    async def test_install_providers_failure(self):
        """Test installing provider with installation failure."""
        mock_provider = Mock()
        mock_provider.install = AsyncMock(side_effect=Exception("Install failed"))

        self.manager.providers = {"provider1": mock_provider}

        with patch.object(self.manager.console, "print") as mock_print:
            result = await self.manager.install_providers(["provider1"])

        assert result is False
        mock_provider.install.assert_called_once()
        # Should print error message
        mock_print.assert_called()


class TestProviderStarting:
    """Test provider starting functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ProviderManager()

    @pytest.mark.asyncio
    async def test_start_providers_all(self):
        """Test starting all providers."""
        mock_provider1 = Mock()
        mock_provider1.start = AsyncMock()
        mock_provider1.name = "provider1"
        mock_provider2 = Mock()
        mock_provider2.start = AsyncMock()
        mock_provider2.name = "provider2"

        self.manager.providers = {
            "provider1": mock_provider1,
            "provider2": mock_provider2,
        }

        with patch.object(
            self.manager.port_manager, "get_available_port", side_effect=[8000, 8001]
        ):
            with patch.object(self.manager.console, "print"):
                result = await self.manager.start_providers()

        assert result is True
        mock_provider1.start.assert_called_once_with(8000)
        mock_provider2.start.assert_called_once_with(8001)

    @pytest.mark.asyncio
    async def test_start_providers_with_port_map(self):
        """Test starting providers with specific port assignments."""
        mock_provider = Mock()
        mock_provider.start = AsyncMock()
        mock_provider.name = "provider1"

        self.manager.providers = {"provider1": mock_provider}
        port_map = {"provider1": 9000}

        with patch.object(
            self.manager.port_manager, "get_available_port", return_value=9000
        ):
            with patch.object(self.manager.console, "print"):
                result = await self.manager.start_providers(["provider1"], port_map)

        assert result is True
        # Should use the preferred port from port_map
        self.manager.port_manager.get_available_port.assert_called_with(
            "provider1", 9000
        )
        mock_provider.start.assert_called_once_with(9000)

    @pytest.mark.asyncio
    async def test_start_providers_no_available_port(self):
        """Test starting provider when no port is available."""
        mock_provider = Mock()
        mock_provider.start = AsyncMock()
        mock_provider.name = "provider1"

        self.manager.providers = {"provider1": mock_provider}

        with patch.object(
            self.manager.port_manager,
            "get_available_port",
            side_effect=RuntimeError("No ports available"),
        ):
            with patch.object(self.manager.console, "print") as mock_print:
                result = await self.manager.start_providers(["provider1"])

        assert result is False
        mock_provider.start.assert_not_called()
        mock_print.assert_called()

    @pytest.mark.asyncio
    async def test_start_providers_not_initialized(self):
        """Test starting provider that's not initialized."""
        with patch.object(self.manager.console, "print") as mock_print:
            result = await self.manager.start_providers(["nonexistent"])

        assert result is False
        mock_print.assert_called_with("[red]Provider nonexistent not initialized[/red]")

    @pytest.mark.asyncio
    async def test_start_providers_start_failure(self):
        """Test handling provider start failure."""
        mock_provider = Mock()
        mock_provider.start = AsyncMock(side_effect=Exception("Start failed"))
        mock_provider.name = "provider1"

        self.manager.providers = {"provider1": mock_provider}

        with patch.object(
            self.manager.port_manager, "get_available_port", return_value=8000
        ):
            with patch.object(self.manager.console, "print") as mock_print:
                result = await self.manager.start_providers(["provider1"])

        assert result is False
        mock_provider.start.assert_called_once()
        mock_print.assert_called()


class TestProviderStopping:
    """Test provider stopping functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ProviderManager()

    @pytest.mark.asyncio
    async def test_stop_providers_all(self):
        """Test stopping all providers."""
        mock_provider1 = Mock()
        mock_provider1.stop = AsyncMock()
        mock_provider1.current_port = 8000
        mock_provider1.name = "provider1"
        mock_provider2 = Mock()
        mock_provider2.stop = AsyncMock()
        mock_provider2.current_port = 8001
        mock_provider2.name = "provider2"

        self.manager.providers = {
            "provider1": mock_provider1,
            "provider2": mock_provider2,
        }

        with patch.object(self.manager.console, "print"):
            result = await self.manager.stop_providers()

        assert result is True
        mock_provider1.stop.assert_called_once()
        mock_provider2.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_providers_specific(self):
        """Test stopping specific providers."""
        mock_provider1 = Mock()
        mock_provider1.stop = AsyncMock()
        mock_provider1.current_port = 8000
        mock_provider1.name = "provider1"
        mock_provider2 = Mock()
        mock_provider2.stop = AsyncMock()
        mock_provider2.current_port = 8001
        mock_provider2.name = "provider2"

        self.manager.providers = {
            "provider1": mock_provider1,
            "provider2": mock_provider2,
        }

        with patch.object(self.manager.console, "print"):
            result = await self.manager.stop_providers(["provider1"])

        assert result is True
        mock_provider1.stop.assert_called_once()
        mock_provider2.stop.assert_not_called()

    @pytest.mark.asyncio
    async def test_stop_providers_not_initialized(self):
        """Test stopping provider that's not initialized."""
        with patch.object(self.manager.console, "print") as mock_print:
            result = await self.manager.stop_providers(["nonexistent"])

        assert result is False
        mock_print.assert_called_with("[red]Provider nonexistent not initialized[/red]")

    @pytest.mark.asyncio
    async def test_stop_providers_stop_failure(self):
        """Test handling provider stop failure."""
        mock_provider = Mock()
        mock_provider.stop = AsyncMock(side_effect=Exception("Stop failed"))
        mock_provider.current_port = 8000
        mock_provider.name = "provider1"

        self.manager.providers = {"provider1": mock_provider}

        with patch.object(self.manager.console, "print") as mock_print:
            result = await self.manager.stop_providers(["provider1"])

        assert result is False
        mock_provider.stop.assert_called_once()
        mock_print.assert_called()


class TestProviderStatus:
    """Test provider status functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ProviderManager()

    @pytest.mark.asyncio
    async def test_show_status_with_providers(self):
        """Test showing status with providers."""
        mock_provider1 = Mock()
        mock_provider1.name = "claude"
        mock_provider1.is_installed = True
        mock_provider1.is_running = True
        mock_provider1.current_port = 8000
        mock_provider1.process_id = 12345
        mock_provider1.get_authentication_status.return_value = AuthStatus.AUTHENTICATED

        mock_provider2 = Mock()
        mock_provider2.name = "copilot"
        mock_provider2.is_installed = False
        mock_provider2.is_running = False
        mock_provider2.current_port = None
        mock_provider2.process_id = None
        mock_provider2.get_authentication_status.return_value = AuthStatus.REQUIRED

        self.manager.providers = {"claude": mock_provider1, "copilot": mock_provider2}

        with patch.object(self.manager.console, "print") as mock_print:
            await self.manager.show_status()

        # Should have printed status information
        assert mock_print.call_count > 0

    @pytest.mark.asyncio
    async def test_show_status_no_providers(self):
        """Test showing status with no providers."""
        self.manager.providers = {}

        with patch.object(self.manager.console, "print") as mock_print:
            await self.manager.show_status()

        mock_print.assert_called()


class TestProviderManagerIntegration:
    """Test ProviderManager integration scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ProviderManager()

    @pytest.mark.asyncio
    async def test_full_provider_lifecycle(self):
        """Test complete provider lifecycle management."""
        # Mock provider
        mock_provider = Mock()
        mock_provider.name = "claude"
        mock_provider.install = AsyncMock()
        mock_provider.start = AsyncMock()
        mock_provider.stop = AsyncMock()
        mock_provider.current_port = None

        self.manager.providers = {"claude": mock_provider}

        # Install
        with patch.object(self.manager.console, "print"):
            result = await self.manager.install_providers(["claude"])

        assert result is True
        mock_provider.install.assert_called_once()

        # Start
        mock_provider.current_port = 8000

        with patch.object(
            self.manager.port_manager, "get_available_port", return_value=8000
        ):
            with patch.object(self.manager.console, "print"):
                result = await self.manager.start_providers(["claude"])

        assert result is True
        mock_provider.start.assert_called_once_with(8000)

        # Stop
        with patch.object(self.manager.console, "print"):
            result = await self.manager.stop_providers(["claude"])

        assert result is True
        mock_provider.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_concurrent_provider_operations(self):
        """Test managing multiple providers concurrently."""
        # Mock providers
        providers = {}
        for i, name in enumerate(["claude", "copilot", "gemini"]):
            provider = Mock()
            provider.name = name
            provider.install = AsyncMock()
            provider.start = AsyncMock()
            provider.stop = AsyncMock()
            provider.current_port = None
            providers[name] = provider

        self.manager.providers = providers

        # Install all
        with patch.object(self.manager.console, "print"):
            result = await self.manager.install_providers()

        assert result is True
        for provider in providers.values():
            provider.install.assert_called_once()

        # Start all with different ports
        for i, provider in enumerate(providers.values()):
            provider.current_port = 8000 + i

        with patch.object(
            self.manager.port_manager,
            "get_available_port",
            side_effect=[8000, 8001, 8002],
        ):
            with patch.object(self.manager.console, "print"):
                result = await self.manager.start_providers()

        assert result is True
        for i, provider in enumerate(providers.values()):
            provider.start.assert_called_once_with(8000 + i)

    @pytest.mark.asyncio
    async def test_error_resilience(self):
        """Test error resilience in provider operations."""
        # Mock providers with different failure modes
        mock_provider1 = Mock()
        mock_provider1.name = "claude"
        mock_provider1.install = AsyncMock(side_effect=Exception("Install failed"))
        mock_provider1.start = AsyncMock()

        mock_provider2 = Mock()
        mock_provider2.name = "copilot"
        mock_provider2.install = AsyncMock()
        mock_provider2.start = AsyncMock(side_effect=Exception("Start failed"))

        self.manager.providers = {"claude": mock_provider1, "copilot": mock_provider2}

        # Install should handle failures gracefully
        with patch.object(self.manager.console, "print"):
            result = await self.manager.install_providers()

        assert result is False
        mock_provider1.install.assert_called_once()
        mock_provider2.install.assert_called_once()

        # Start should handle failures gracefully
        with patch.object(
            self.manager.port_manager, "get_available_port", side_effect=[8000, 8001]
        ):
            with patch.object(self.manager.console, "print"):
                result = await self.manager.start_providers()

        assert result is False
        mock_provider2.start.assert_called_once()
