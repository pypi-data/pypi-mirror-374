"""Tests for the BaseProvider class."""

from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from epic_llm.providers.base import BaseProvider
from epic_llm.utils.dependencies import Dependency, DependencyType


class ConcreteProvider(BaseProvider):
    """Concrete implementation of BaseProvider for testing."""

    def __init__(
        self,
        name: str = "test_provider",
        default_port: int = 8000,
        install_dir: Path = Path("/tmp/test"),
    ):
        super().__init__(name, default_port, install_dir)

    async def install(self) -> bool:
        return True

    async def start(self, port: int) -> bool:
        return True

    async def stop(self) -> bool:
        return True

    async def health_check(self) -> bool:
        return True

    def get_dependencies(self) -> list[Dependency]:
        return []


class TestBaseProviderInitialization:
    """Test BaseProvider initialization."""

    def test_provider_initialization(self):
        """Test basic provider initialization."""
        install_dir = Path("/tmp/test_provider")
        provider = ConcreteProvider("test", 8080, install_dir)

        assert provider.name == "test"
        assert provider.default_port == 8080
        assert provider.install_dir == install_dir
        assert provider.process is None


class TestBaseProviderAuthentication:
    """Test BaseProvider authentication methods."""

    def test_is_authentication_required_default(self):
        """Test that authentication is not required by default."""
        provider = ConcreteProvider()
        assert provider.is_authentication_required() is False

    @pytest.mark.asyncio
    async def test_handle_authentication_prompt(self):
        """Test authentication prompt handling (default implementation)."""
        provider = ConcreteProvider()
        # Should not raise any exceptions
        await provider.handle_authentication_prompt()


class TestBaseProviderProperties:
    """Test BaseProvider properties."""

    def test_is_installed_property(self):
        """Test is_installed property."""
        install_dir = Path("/tmp/test_provider")
        provider = ConcreteProvider("test", 8080, install_dir)

        with patch("pathlib.Path.exists", return_value=True):
            assert provider.is_installed is True

        with patch("pathlib.Path.exists", return_value=False):
            assert provider.is_installed is False

    def test_is_running_property_with_process(self):
        """Test is_running property with process."""
        provider = ConcreteProvider()

        # No process
        provider.process = None
        assert provider.is_running is False

        # Process with returncode None (running)
        mock_process = Mock()
        mock_process.returncode = None
        provider.process = mock_process
        assert provider.is_running is True

        # Process with returncode (finished)
        mock_process.returncode = 0
        assert provider.is_running is False

    def test_is_running_property_without_process(self):
        """Test is_running property without process but with process_id."""
        provider = ConcreteProvider()
        provider.process = None

        # Mock the _state_manager to return None for process_id
        with patch.object(
            provider._state_manager, "get_provider_state"
        ) as mock_get_state:
            mock_state = Mock()
            mock_state.process_id = None
            mock_get_state.return_value = mock_state
            assert provider.is_running is False


class TestBaseProviderProcessMonitoring:
    """Test BaseProvider process monitoring."""

    @pytest.mark.asyncio
    async def test_monitor_process_output_no_process(self):
        """Test process monitoring with no process."""
        provider = ConcreteProvider()
        provider.process = None

        # Should not raise any exceptions
        await provider.monitor_process_output()

    @pytest.mark.asyncio
    async def test_monitor_process_output_no_stdout(self):
        """Test process monitoring with process but no stdout."""
        provider = ConcreteProvider()
        provider.process = Mock()
        provider.process.stdout = None

        # Should not raise any exceptions
        await provider.monitor_process_output()

    @pytest.mark.asyncio
    async def test_monitor_process_output_with_output(self):
        """Test process monitoring with actual output."""
        provider = ConcreteProvider()

        # Create a mock process with stdout
        mock_process = AsyncMock()
        mock_stdout = AsyncMock()

        # Setup readline to return a line then None (EOF)
        mock_stdout.readline.side_effect = [b"test output\n", b""]
        mock_process.stdout = mock_stdout
        provider.process = mock_process

        # Mock the process_output_line method to track calls
        provider.process_output_line = AsyncMock()

        await provider.monitor_process_output()

        # Verify process_output_line was called with the decoded line
        provider.process_output_line.assert_called_once_with("test output")

    @pytest.mark.asyncio
    @patch("builtins.print")
    async def test_monitor_process_output_exception_handling(self, mock_print):
        """Test process monitoring exception handling."""
        provider = ConcreteProvider()

        # Create a mock process that raises an exception
        mock_process = AsyncMock()
        mock_stdout = AsyncMock()
        mock_stdout.readline.side_effect = Exception("Test exception")
        mock_process.stdout = mock_stdout
        provider.process = mock_process

        # Should not raise the exception, just print and continue
        await provider.monitor_process_output()

        # Verify error was printed (check that the expected message was among the calls)
        error_call_found = False
        for call_args in mock_print.call_args_list:
            if "Error monitoring output for test_provider" in str(call_args):
                error_call_found = True
                break
        assert error_call_found, (
            f"Expected error message not found in calls: {mock_print.call_args_list}"
        )

    @pytest.mark.asyncio
    async def test_process_output_line_default(self):
        """Test default process_output_line implementation."""
        provider = ConcreteProvider()

        # Should not raise any exceptions
        await provider.process_output_line("test line")


class TestBaseProviderAbstractMethods:
    """Test that abstract methods are properly defined."""

    def test_abstract_methods_exist(self):
        """Test that all expected abstract methods exist."""
        abstract_methods = BaseProvider.__abstractmethods__
        expected_methods = {
            "install",
            "start",
            "stop",
            "health_check",
            "get_dependencies",
        }

        assert abstract_methods == expected_methods

    def test_cannot_instantiate_base_provider(self):
        """Test that BaseProvider cannot be instantiated directly."""
        with pytest.raises(
            TypeError, match="Can't instantiate abstract class BaseProvider"
        ):
            BaseProvider("test", 8080, Path("/tmp/test"))


class TestBaseProviderDependencyChecking:
    """Test BaseProvider dependency checking."""

    @pytest.mark.asyncio
    async def test_check_dependencies_basic(self):
        """Test basic dependency checking functionality."""
        provider = ConcreteProvider()

        # Mock the DependencyChecker import inside the method
        with patch(
            "epic_llm.utils.dependencies.DependencyChecker"
        ) as mock_checker_class:
            mock_checker_instance = AsyncMock()
            mock_checker_class.return_value = mock_checker_instance
            mock_checker_instance.check_and_install.return_value = True

            result = await provider.check_dependencies()

            assert result is True
            mock_checker_instance.check_and_install.assert_called_once_with(
                [], auto_install=False, show_status=True
            )

    @pytest.mark.asyncio
    async def test_check_dependencies_with_auto_install(self):
        """Test dependency checking with auto_install=True."""
        provider = ConcreteProvider()

        with patch(
            "epic_llm.utils.dependencies.DependencyChecker"
        ) as mock_checker_class:
            mock_checker_instance = AsyncMock()
            mock_checker_class.return_value = mock_checker_instance
            mock_checker_instance.check_and_install.return_value = True

            result = await provider.check_dependencies(auto_install=True)

            assert result is True
            mock_checker_instance.check_and_install.assert_called_once_with(
                [], auto_install=True, show_status=True
            )

    @pytest.mark.asyncio
    async def test_check_dependencies_failure(self):
        """Test dependency checking failure."""
        provider = ConcreteProvider()

        with patch(
            "epic_llm.utils.dependencies.DependencyChecker"
        ) as mock_checker_class:
            mock_checker_instance = AsyncMock()
            mock_checker_class.return_value = mock_checker_instance
            mock_checker_instance.check_and_install.return_value = False

            result = await provider.check_dependencies()

            assert result is False


class TestBaseProviderIntegration:
    """Test BaseProvider integration scenarios."""

    @pytest.mark.asyncio
    async def test_provider_workflow(self):
        """Test a basic provider workflow."""
        install_dir = Path("/tmp/test_workflow")
        provider = ConcreteProvider("workflow_test", 9000, install_dir)

        # Test basic properties
        assert provider.name == "workflow_test"
        assert provider.default_port == 9000
        assert provider.install_dir == install_dir

        # Test abstract method implementations
        assert await provider.install() is True
        assert await provider.start(9000) is True
        assert await provider.health_check() is True
        assert await provider.stop() is True

        # Test dependencies
        assert provider.get_dependencies() == []

    def test_provider_with_dependencies(self):
        """Test provider that has dependencies."""

        class ProviderWithDeps(ConcreteProvider):
            def get_dependencies(self):
                return [
                    Dependency(
                        "git",
                        DependencyType.CLI_COMMAND,
                        "Git version control",
                        check_command=["git", "--version"],
                    ),
                    Dependency(
                        "node",
                        DependencyType.CLI_COMMAND,
                        "Node.js runtime",
                        check_command=["node", "--version"],
                    ),
                ]

        provider = ProviderWithDeps()
        deps = provider.get_dependencies()

        assert len(deps) == 2
        assert deps[0].name == "git"
        assert deps[0].type == DependencyType.CLI_COMMAND
        assert deps[1].name == "node"
        assert deps[1].type == DependencyType.CLI_COMMAND

    @pytest.mark.asyncio
    async def test_provider_authentication_workflow(self):
        """Test provider authentication workflow."""
        provider = ConcreteProvider()

        # Test default authentication behavior
        assert provider.is_authentication_required() is False

        # Test authentication prompt handling
        await provider.handle_authentication_prompt()

        # Test process output line handling
        await provider.process_output_line("Some output line")
