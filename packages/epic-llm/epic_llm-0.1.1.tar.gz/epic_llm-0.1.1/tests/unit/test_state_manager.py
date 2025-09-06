"""Tests for state manager functionality."""

import json
from pathlib import Path
from unittest.mock import patch

from epic_llm.managers.state import AuthStatus, ProviderState, StateManager


class TestAuthStatus:
    """Test AuthStatus enum functionality."""

    def test_auth_status_values(self):
        """Test AuthStatus enum values."""
        assert AuthStatus.NOT_REQUIRED.value == "not_required"
        assert AuthStatus.REQUIRED.value == "required"
        assert AuthStatus.AUTHENTICATED.value == "authenticated"
        assert AuthStatus.FAILED.value == "failed"

    def test_auth_status_comparison(self):
        """Test AuthStatus enum comparison."""
        assert AuthStatus.AUTHENTICATED == AuthStatus.AUTHENTICATED
        assert AuthStatus.AUTHENTICATED != AuthStatus.FAILED
        assert AuthStatus.REQUIRED != AuthStatus.NOT_REQUIRED

    def test_auth_status_string_representation(self):
        """Test AuthStatus string representation."""
        assert str(AuthStatus.AUTHENTICATED) == "AuthStatus.AUTHENTICATED"


class TestProviderState:
    """Test ProviderState dataclass functionality."""

    def test_provider_state_creation(self):
        """Test creating ProviderState instance."""
        state = ProviderState(
            name="test_provider",
            installed=True,
            running=False,
            port=None,
            process_id=None,
            auth_status=AuthStatus.NOT_REQUIRED,
        )

        assert state.name == "test_provider"
        assert state.installed is True
        assert state.running is False
        assert state.port is None
        assert state.process_id is None
        assert state.auth_status == AuthStatus.NOT_REQUIRED

    def test_provider_state_defaults(self):
        """Test ProviderState default values."""
        state = ProviderState(name="test")

        assert state.name == "test"
        assert state.installed is False
        assert state.running is False
        assert state.port is None
        assert state.process_id is None
        assert state.auth_status == AuthStatus.NOT_REQUIRED

    def test_provider_state_with_values(self):
        """Test ProviderState with all values set."""
        state = ProviderState(
            name="claude",
            installed=True,
            running=True,
            port=8000,
            process_id=12345,
            auth_status=AuthStatus.AUTHENTICATED,
        )

        assert state.name == "claude"
        assert state.installed is True
        assert state.running is True
        assert state.port == 8000
        assert state.process_id == 12345
        assert state.auth_status == AuthStatus.AUTHENTICATED


class TestStateManagerInitialization:
    """Test StateManager initialization."""

    def test_state_manager_creation(self, temp_dir):
        """Test creating StateManager instance."""
        state_file = temp_dir / "test_state.json"
        manager = StateManager(state_file=state_file)

        assert manager.state_file == state_file
        assert manager.providers == {}

    def test_state_manager_default_file(self):
        """Test StateManager with default state file."""
        manager = StateManager()
        expected_path = Path.home() / ".local/share/llm-api-gw/state.json"
        assert manager.state_file == expected_path

    def test_state_manager_loads_existing_state(self, temp_dir):
        """Test StateManager loads existing state file."""
        state_file = temp_dir / "existing_state.json"
        test_data = {
            "providers": {
                "claude": {
                    "name": "claude",
                    "installed": True,
                    "running": False,
                    "port": None,
                    "process_id": None,
                    "auth_status": "authenticated",
                }
            }
        }
        state_file.write_text(json.dumps(test_data))

        manager = StateManager(state_file=state_file)

        assert "claude" in manager.providers
        assert manager.providers["claude"].name == "claude"
        assert manager.providers["claude"].installed is True
        assert manager.providers["claude"].auth_status == AuthStatus.AUTHENTICATED

    def test_state_manager_handles_missing_file(self, temp_dir):
        """Test StateManager handles missing state file gracefully."""
        state_file = temp_dir / "nonexistent.json"
        manager = StateManager(state_file=state_file)

        assert manager.providers == {}

    def test_state_manager_handles_invalid_json(self, temp_dir):
        """Test StateManager handles invalid JSON gracefully."""
        state_file = temp_dir / "invalid.json"
        state_file.write_text("invalid json content")

        manager = StateManager(state_file=state_file)

        assert manager.providers == {}


class TestStateManagerProviderOperations:
    """Test StateManager provider operations."""

    def setup_method(self, temp_dir):
        """Set up test fixtures."""
        self.state_file = temp_dir / "test_state.json"
        self.manager = StateManager(state_file=self.state_file)

    def test_get_provider_state_existing(self, temp_dir):
        """Test getting existing provider state."""
        self.setup_method(temp_dir)
        # Add a provider
        self.manager.providers["claude"] = ProviderState(
            name="claude", installed=True, auth_status=AuthStatus.AUTHENTICATED
        )

        state = self.manager.get_provider_state("claude")

        assert state.name == "claude"
        assert state.installed is True
        assert state.auth_status == AuthStatus.AUTHENTICATED

    def test_get_provider_state_new(self, temp_dir):
        """Test getting state for new provider."""
        self.setup_method(temp_dir)

        state = self.manager.get_provider_state("new_provider")

        assert state.name == "new_provider"
        assert state.installed is False
        assert state.running is False
        assert state.auth_status == AuthStatus.NOT_REQUIRED

    def test_update_provider_state(self, temp_dir):
        """Test updating provider state."""
        self.setup_method(temp_dir)

        self.manager.update_provider_state(
            "claude",
            installed=True,
            running=True,
            port=8000,
            process_id=12345,
            auth_status=AuthStatus.AUTHENTICATED,
        )

        state = self.manager.providers["claude"]
        assert state.installed is True
        assert state.running is True
        assert state.port == 8000
        assert state.process_id == 12345
        assert state.auth_status == AuthStatus.AUTHENTICATED

    def test_update_provider_state_partial(self, temp_dir):
        """Test partial update of provider state."""
        self.setup_method(temp_dir)
        # First create a provider with some values
        self.manager.update_provider_state("claude", installed=True, port=8000)

        # Then update only some fields
        self.manager.update_provider_state("claude", running=True, process_id=12345)

        state = self.manager.providers["claude"]
        assert state.installed is True  # Unchanged
        assert state.running is True  # Updated
        assert state.port == 8000  # Unchanged
        assert state.process_id == 12345  # Updated


class TestStateManagerInstallationOperations:
    """Test StateManager installation-related operations."""

    def setup_method(self, temp_dir):
        """Set up test fixtures."""
        self.state_file = temp_dir / "test_state.json"
        self.manager = StateManager(state_file=self.state_file)

    def test_set_provider_installed(self, temp_dir):
        """Test setting provider installation status."""
        self.setup_method(temp_dir)

        self.manager.set_provider_installed("claude", True)

        assert self.manager.is_provider_installed("claude") is True

    def test_set_provider_not_installed(self, temp_dir):
        """Test setting provider as not installed."""
        self.setup_method(temp_dir)

        self.manager.set_provider_installed("claude", False)

        assert self.manager.is_provider_installed("claude") is False

    def test_is_provider_installed_new_provider(self, temp_dir):
        """Test checking installation status of new provider."""
        self.setup_method(temp_dir)

        result = self.manager.is_provider_installed("new_provider")

        assert result is False


class TestStateManagerRunningOperations:
    """Test StateManager running status operations."""

    def setup_method(self, temp_dir):
        """Set up test fixtures."""
        self.state_file = temp_dir / "test_state.json"
        self.manager = StateManager(state_file=self.state_file)

    def test_set_provider_running(self, temp_dir):
        """Test setting provider running status."""
        self.setup_method(temp_dir)

        self.manager.set_provider_running("claude", True)

        assert self.manager.is_provider_running("claude") is True

    def test_set_provider_stopped(self, temp_dir):
        """Test setting provider as stopped."""
        self.setup_method(temp_dir)

        self.manager.set_provider_running("claude", False)

        assert self.manager.is_provider_running("claude") is False

    def test_set_provider_started_with_details(self, temp_dir):
        """Test setting provider as started with process details."""
        self.setup_method(temp_dir)

        with patch("builtins.print"):  # Suppress debug output
            self.manager.set_provider_started("claude", process_id=12345, port=8000)

        state = self.manager.providers["claude"]
        assert state.running is True
        assert state.process_id == 12345
        assert state.port == 8000

    def test_is_provider_running_new_provider(self, temp_dir):
        """Test checking running status of new provider."""
        self.setup_method(temp_dir)

        result = self.manager.is_provider_running("new_provider")

        assert result is False


class TestStateManagerPortOperations:
    """Test StateManager port-related operations."""

    def setup_method(self, temp_dir):
        """Set up test fixtures."""
        self.state_file = temp_dir / "test_state.json"
        self.manager = StateManager(state_file=self.state_file)

    def test_set_provider_port(self, temp_dir):
        """Test setting provider port."""
        self.setup_method(temp_dir)

        self.manager.set_provider_port("claude", 8000)

        assert self.manager.get_provider_port("claude") == 8000

    def test_get_provider_port_new_provider(self, temp_dir):
        """Test getting port for new provider."""
        self.setup_method(temp_dir)

        port = self.manager.get_provider_port("new_provider")

        assert port is None

    def test_set_provider_process_id(self, temp_dir):
        """Test setting provider process ID."""
        self.setup_method(temp_dir)

        self.manager.set_provider_process_id("claude", 12345)

        assert self.manager.get_provider_process_id("claude") == 12345

    def test_get_provider_process_id_new_provider(self, temp_dir):
        """Test getting process ID for new provider."""
        self.setup_method(temp_dir)

        process_id = self.manager.get_provider_process_id("new_provider")

        assert process_id is None


class TestStateManagerAuthOperations:
    """Test StateManager authentication operations."""

    def setup_method(self, temp_dir):
        """Set up test fixtures."""
        self.state_file = temp_dir / "test_state.json"
        self.manager = StateManager(state_file=self.state_file)

    def test_set_provider_auth_status(self, temp_dir):
        """Test setting provider authentication status."""
        self.setup_method(temp_dir)

        self.manager.set_provider_auth_status("claude", AuthStatus.AUTHENTICATED)

        assert (
            self.manager.get_provider_auth_status("claude") == AuthStatus.AUTHENTICATED
        )

    def test_get_provider_auth_status_new_provider(self, temp_dir):
        """Test getting auth status for new provider."""
        self.setup_method(temp_dir)

        status = self.manager.get_provider_auth_status("new_provider")

        assert status == AuthStatus.NOT_REQUIRED


class TestStateManagerPersistence:
    """Test StateManager persistence operations."""

    def setup_method(self, temp_dir):
        """Set up test fixtures."""
        self.state_file = temp_dir / "test_state.json"
        self.manager = StateManager(state_file=self.state_file)

    def test_save_state(self, temp_dir):
        """Test saving state to file."""
        self.setup_method(temp_dir)

        # Add some provider state
        self.manager.update_provider_state(
            "claude",
            installed=True,
            running=True,
            port=8000,
            auth_status=AuthStatus.AUTHENTICATED,
        )

        with patch("builtins.print"):  # Suppress debug output
            self.manager.save_state()

        # Verify file was created and contains correct data
        assert self.state_file.exists()

        with open(self.state_file) as f:
            data = json.load(f)

        assert "providers" in data
        assert "claude" in data["providers"]
        claude_data = data["providers"]["claude"]
        assert claude_data["installed"] is True
        assert claude_data["running"] is True
        assert claude_data["port"] == 8000
        assert claude_data["auth_status"] == "authenticated"

    def test_save_state_creates_directory(self, temp_dir):
        """Test that save_state creates parent directories."""
        nested_dir = temp_dir / "nested" / "path"
        state_file = nested_dir / "state.json"
        manager = StateManager(state_file=state_file)

        # Add some state
        manager.set_provider_installed("test", True)

        with patch("builtins.print"):  # Suppress debug output
            manager.save_state()

        assert state_file.exists()
        assert nested_dir.exists()

    def test_save_state_error_handling(self, temp_dir):
        """Test save_state error handling."""
        self.setup_method(temp_dir)

        # Mock open to raise an exception
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with patch("builtins.print") as mock_print:
                self.manager.save_state()
                # Should print error message
                mock_print.assert_called()

    def test_load_state_from_existing_file(self, temp_dir):
        """Test loading state from existing file."""
        self.setup_method(temp_dir)

        # Create a state file manually
        test_data = {
            "providers": {
                "claude": {
                    "name": "claude",
                    "installed": True,
                    "running": False,
                    "port": 8000,
                    "process_id": None,
                    "auth_status": "failed",
                }
            }
        }

        with open(self.state_file, "w") as f:
            json.dump(test_data, f)

        # Create new manager to load the state
        new_manager = StateManager(state_file=self.state_file)

        assert "claude" in new_manager.providers
        claude_state = new_manager.providers["claude"]
        assert claude_state.installed is True
        assert claude_state.running is False
        assert claude_state.port == 8000
        assert claude_state.auth_status == AuthStatus.FAILED


class TestStateManagerRealWorldScenarios:
    """Test StateManager with realistic scenarios."""

    def setup_method(self, temp_dir):
        """Set up test fixtures."""
        self.state_file = temp_dir / "test_state.json"
        self.manager = StateManager(state_file=self.state_file)

    def test_provider_lifecycle_scenario(self, temp_dir):
        """Test complete provider lifecycle."""
        self.setup_method(temp_dir)
        provider_name = "claude"

        # Initially provider doesn't exist
        assert not self.manager.is_provider_installed(provider_name)
        assert not self.manager.is_provider_running(provider_name)

        # Install provider
        self.manager.set_provider_installed(provider_name, True)
        assert self.manager.is_provider_installed(provider_name)

        # Authenticate provider
        self.manager.set_provider_auth_status(provider_name, AuthStatus.AUTHENTICATED)
        assert (
            self.manager.get_provider_auth_status(provider_name)
            == AuthStatus.AUTHENTICATED
        )

        # Start provider
        with patch("builtins.print"):
            self.manager.set_provider_started(
                provider_name, process_id=12345, port=8000
            )

        assert self.manager.is_provider_running(provider_name)
        assert self.manager.get_provider_port(provider_name) == 8000
        assert self.manager.get_provider_process_id(provider_name) == 12345

        # Stop provider
        self.manager.set_provider_running(provider_name, False)
        self.manager.set_provider_port(provider_name, None)
        self.manager.set_provider_process_id(provider_name, None)

        assert not self.manager.is_provider_running(provider_name)
        assert self.manager.get_provider_port(provider_name) is None
        assert self.manager.get_provider_process_id(provider_name) is None

    def test_multiple_providers_scenario(self, temp_dir):
        """Test managing multiple providers simultaneously."""
        self.setup_method(temp_dir)

        providers = ["claude", "copilot", "gemini"]

        # Install all providers
        for provider in providers:
            self.manager.set_provider_installed(provider, True)

        # Start some providers
        with patch("builtins.print"):
            self.manager.set_provider_started("claude", process_id=100, port=8000)
            self.manager.set_provider_started("copilot", process_id=200, port=8081)

        # Check states
        assert self.manager.is_provider_running("claude")
        assert self.manager.is_provider_running("copilot")
        assert not self.manager.is_provider_running("gemini")

        assert self.manager.get_provider_port("claude") == 8000
        assert self.manager.get_provider_port("copilot") == 8081
        assert self.manager.get_provider_port("gemini") is None

    def test_state_persistence_across_restarts(self, temp_dir):
        """Test that state persists across manager restarts."""
        self.setup_method(temp_dir)

        # Set up initial state
        self.manager.update_provider_state(
            "claude",
            installed=True,
            running=True,
            port=8000,
            process_id=12345,
            auth_status=AuthStatus.AUTHENTICATED,
        )

        with patch("builtins.print"):
            self.manager.save_state()

        # Create new manager instance (simulating restart)
        new_manager = StateManager(state_file=self.state_file)

        # Verify state was preserved
        assert new_manager.is_provider_installed("claude")
        assert new_manager.is_provider_running("claude")
        assert new_manager.get_provider_port("claude") == 8000
        assert new_manager.get_provider_process_id("claude") == 12345
        assert (
            new_manager.get_provider_auth_status("claude") == AuthStatus.AUTHENTICATED
        )
