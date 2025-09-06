"""Unit tests for manager classes."""

from unittest.mock import Mock, patch

import pytest

from epic_llm.managers.port import PortManager
from epic_llm.managers.state import AuthStatus, ProviderState


class TestPortManager:
    """Test port management functionality."""

    @pytest.fixture
    def port_manager(self):
        """Create port manager instance."""
        return PortManager()

    def test_port_manager_initialization(self, port_manager):
        """Test port manager initializes correctly."""
        assert port_manager.port_range == (8000, 8999)
        assert "claude" in port_manager.default_ports
        assert "copilot" in port_manager.default_ports
        assert "gemini" in port_manager.default_ports

    def test_get_available_port_success(self, port_manager):
        """Test successful port allocation."""
        with patch.object(port_manager, "is_port_available", return_value=True):
            port = port_manager.get_available_port("test_provider")

        assert port >= 8000
        assert port <= 8999

    def test_get_available_port_with_preference(self, port_manager):
        """Test port allocation with preferred port."""
        preferred_port = 8123

        with patch.object(port_manager, "is_port_available", return_value=True):
            port = port_manager.get_available_port("test_provider", preferred_port)

        assert port == preferred_port

    def test_release_port(self, port_manager):
        """Test port release functionality."""
        # Port release is handled by state manager
        # This test verifies the method exists and can be called
        port_manager.release_port("test_provider")
        # No assertion needed as release_port is a no-op

    def test_is_port_available_true(self, port_manager):
        """Test port availability check for available port."""
        with patch("socket.socket") as mock_socket:
            mock_sock = Mock()
            mock_socket.return_value.__enter__.return_value = mock_sock
            mock_sock.connect_ex.return_value = 1  # Port available

            available = port_manager.is_port_available(8123)

        assert available is True

    def test_is_port_available_false(self, port_manager):
        """Test port availability check for unavailable port."""
        with patch("socket.socket") as mock_socket:
            mock_sock = Mock()
            mock_socket.return_value.__enter__.return_value = mock_sock
            mock_sock.connect_ex.return_value = 0  # Port in use

            available = port_manager.is_port_available(8123)

        assert available is False


class TestProviderState:
    """Test provider state management."""

    def test_provider_state_creation(self):
        """Test provider state creation."""
        state = ProviderState(
            name="test_provider",
            process_id=None,
            port=None,
            started_at=None,
            is_installed=False,
            auth_status=AuthStatus.NOT_REQUIRED.value,
        )

        assert state.name == "test_provider"
        assert state.process_id is None
        assert state.port is None
        assert state.auth_status == AuthStatus.NOT_REQUIRED.value

    def test_provider_state_update(self):
        """Test provider state updates."""
        state = ProviderState(name="test_provider")

        state.process_id = 12345
        state.port = 8080
        state.is_installed = True

        assert state.process_id == 12345
        assert state.port == 8080
        assert state.is_installed is True

    def test_auth_status_enum(self):
        """Test AuthStatus enum values."""
        assert AuthStatus.NOT_REQUIRED.value == "not_required"
        assert AuthStatus.REQUIRED.value == "required"
        assert AuthStatus.AUTHENTICATED.value == "authenticated"
        assert AuthStatus.FAILED.value == "failed"
