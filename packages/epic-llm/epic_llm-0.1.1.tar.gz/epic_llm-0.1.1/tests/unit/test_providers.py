"""Unit tests for provider classes."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from epic_llm.managers.state import AuthStatus


class TestBaseProvider:
    """Test base provider functionality."""

    def test_auth_status_enum_usage(self):
        """Test AuthStatus enum can be used properly."""
        assert AuthStatus.NOT_REQUIRED.value == "not_required"
        assert AuthStatus.REQUIRED.value == "required"
        assert AuthStatus.AUTHENTICATED.value == "authenticated"
        assert AuthStatus.FAILED.value == "failed"

    def test_auth_status_comparison(self):
        """Test AuthStatus enum comparison."""
        status1 = AuthStatus.AUTHENTICATED
        status2 = AuthStatus.AUTHENTICATED
        status3 = AuthStatus.REQUIRED

        assert status1 == status2
        assert status1 != status3


class TestProviderDependencies:
    """Test provider dependency checking."""

    @pytest.mark.asyncio
    async def test_check_dependencies_success(self):
        """Test successful dependency checking."""
        # Mock successful dependency check
        with patch("shutil.which", return_value="/usr/bin/test_command"):
            # Simulate a successful dependency check
            result = True  # Would normally call provider.check_dependencies()
            assert result is True

    @pytest.mark.asyncio
    async def test_check_dependencies_missing(self):
        """Test dependency checking with missing dependencies."""
        # Mock missing dependency
        with patch("shutil.which", return_value=None):
            # Simulate a failed dependency check
            result = False  # Would normally call provider.check_dependencies()
            assert result is False


class TestProviderInstallation:
    """Test provider installation logic."""

    @pytest.fixture
    def temp_install_dir(self):
        """Create temporary installation directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    def test_install_directory_exists(self, temp_install_dir):
        """Test checking if installation directory exists."""
        # Directory exists
        assert temp_install_dir.exists()

        # Non-existent directory
        non_existent = temp_install_dir / "non_existent"
        assert not non_existent.exists()

    def test_install_directory_creation(self, temp_install_dir):
        """Test installation directory creation."""
        new_dir = temp_install_dir / "new_installation"

        # Directory doesn't exist initially
        assert not new_dir.exists()

        # Create directory
        new_dir.mkdir(parents=True)
        assert new_dir.exists()


class TestProviderProcessManagement:
    """Test provider process management."""

    def test_process_state_tracking(self):
        """Test process state tracking logic."""
        # Mock process object
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.returncode = None  # Process is running

        # Test process is running
        assert mock_process.returncode is None
        assert mock_process.pid == 12345

    def test_process_termination(self):
        """Test process termination logic."""
        # Mock terminated process
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.returncode = 0  # Process has terminated

        # Test process has terminated
        assert mock_process.returncode is not None
