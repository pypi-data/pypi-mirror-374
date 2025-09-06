"""Tests for validators utilities."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from epic_llm.utils.validators import (
    check_cli_command,
    check_executable_in_path,
    check_npm_package_global,
    check_npx_package,
    check_python_version,
    install_npm_package_global,
)


class TestCheckCliCommand:
    """Test check_cli_command function."""

    @pytest.mark.asyncio
    async def test_check_cli_command_success(self):
        """Test successful CLI command check."""
        with patch("asyncio.create_subprocess_exec") as mock_create_subprocess:
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.wait.return_value = None
            mock_create_subprocess.return_value = mock_process

            result = await check_cli_command(["echo", "test"])

            assert result is True
            mock_create_subprocess.assert_called_once_with(
                "echo",
                "test",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            mock_process.wait.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_cli_command_failure(self):
        """Test failed CLI command check."""
        with patch("asyncio.create_subprocess_exec") as mock_create_subprocess:
            mock_process = AsyncMock()
            mock_process.returncode = 1
            mock_process.wait.return_value = None
            mock_create_subprocess.return_value = mock_process

            result = await check_cli_command(["false"])

            assert result is False

    @pytest.mark.asyncio
    async def test_check_cli_command_file_not_found(self):
        """Test CLI command check with file not found."""
        with patch("asyncio.create_subprocess_exec") as mock_create_subprocess:
            mock_create_subprocess.side_effect = FileNotFoundError()

            result = await check_cli_command(["nonexistent-command"])

            assert result is False

    @pytest.mark.asyncio
    async def test_check_cli_command_os_error(self):
        """Test CLI command check with OS error."""
        with patch("asyncio.create_subprocess_exec") as mock_create_subprocess:
            mock_create_subprocess.side_effect = OSError()

            result = await check_cli_command(["some-command"])

            assert result is False

    @pytest.mark.asyncio
    async def test_check_cli_command_empty_command(self):
        """Test CLI command check with empty command."""
        # The function should handle empty command gracefully
        # This will actually cause a TypeError when unpacking empty list
        try:
            result = await check_cli_command([])
            # If it somehow succeeds, it should return False
            assert result is False
        except (TypeError, IndexError):
            # This is expected behavior - empty command list should fail
            pass


class TestCheckExecutableInPath:
    """Test check_executable_in_path function."""

    def test_check_executable_in_path_exists(self):
        """Test checking for executable that exists in PATH."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = "/usr/bin/python3"

            result = check_executable_in_path("python3")

            assert result is True
            mock_which.assert_called_once_with("python3")

    def test_check_executable_in_path_not_exists(self):
        """Test checking for executable that doesn't exist in PATH."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = None

            result = check_executable_in_path("nonexistent-exe")

            assert result is False
            mock_which.assert_called_once_with("nonexistent-exe")

    def test_check_executable_none_name(self):
        """Test checking for executable with None name."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = None

            result = check_executable_in_path(None)

            assert result is False


class TestNpmPackageOperations:
    """Test npm package operations."""

    @pytest.mark.asyncio
    async def test_check_npm_package_global_exists(self):
        """Test checking for globally installed npm package."""
        with patch("asyncio.create_subprocess_exec") as mock_create_subprocess:
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.wait.return_value = None
            mock_create_subprocess.return_value = mock_process

            result = await check_npm_package_global("lodash")

            assert result is True
            mock_create_subprocess.assert_called_once_with(
                "npm",
                "list",
                "-g",
                "lodash",
                "--depth=0",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

    @pytest.mark.asyncio
    async def test_check_npm_package_global_not_exists(self):
        """Test checking for npm package that's not installed globally."""
        with patch("asyncio.create_subprocess_exec") as mock_create_subprocess:
            mock_process = AsyncMock()
            mock_process.returncode = 1
            mock_process.wait.return_value = None
            mock_create_subprocess.return_value = mock_process

            result = await check_npm_package_global("nonexistent-package")

            assert result is False

    @pytest.mark.asyncio
    async def test_check_npm_package_global_npm_not_available(self):
        """Test checking npm package when npm is not available."""
        with patch("asyncio.create_subprocess_exec") as mock_create_subprocess:
            mock_create_subprocess.side_effect = FileNotFoundError()

            result = await check_npm_package_global("some-package")

            assert result is False

    @pytest.mark.asyncio
    async def test_install_npm_package_global_success(self):
        """Test successful global npm package installation."""
        with patch("asyncio.create_subprocess_exec") as mock_create_subprocess:
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.wait.return_value = None
            mock_create_subprocess.return_value = mock_process

            result = await install_npm_package_global("lodash")

            assert result is True
            mock_create_subprocess.assert_called_once_with(
                "npm",
                "install",
                "-g",
                "lodash",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

    @pytest.mark.asyncio
    async def test_install_npm_package_global_failure(self):
        """Test failed global npm package installation."""
        with patch("asyncio.create_subprocess_exec") as mock_create_subprocess:
            mock_process = AsyncMock()
            mock_process.returncode = 1
            mock_process.wait.return_value = None
            mock_create_subprocess.return_value = mock_process

            result = await install_npm_package_global("nonexistent-package")

            assert result is False

    @pytest.mark.asyncio
    async def test_install_npm_package_global_npm_not_available(self):
        """Test npm package installation when npm is not available."""
        with patch("asyncio.create_subprocess_exec") as mock_create_subprocess:
            mock_create_subprocess.side_effect = FileNotFoundError()

            result = await install_npm_package_global("some-package")

            assert result is False


class TestNpxPackageOperations:
    """Test npx package operations."""

    @pytest.mark.asyncio
    async def test_check_npx_package_exists(self):
        """Test checking for npx package that exists."""
        with patch("asyncio.create_subprocess_exec") as mock_create_subprocess:
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.wait.return_value = None
            mock_create_subprocess.return_value = mock_process

            result = await check_npx_package("create-react-app@latest", ["--version"])

            assert result is True
            mock_create_subprocess.assert_called_once_with(
                "npx",
                "create-react-app@latest",
                "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

    @pytest.mark.asyncio
    async def test_check_npx_package_not_exists(self):
        """Test checking for npx package that doesn't exist."""
        with patch("asyncio.create_subprocess_exec") as mock_create_subprocess:
            mock_process = AsyncMock()
            mock_process.returncode = 1
            mock_process.wait.return_value = None
            mock_create_subprocess.return_value = mock_process

            result = await check_npx_package("nonexistent-package", ["--help"])

            assert result is False

    @pytest.mark.asyncio
    async def test_check_npx_package_timeout(self):
        """Test npx package check with timeout."""
        with patch("asyncio.create_subprocess_exec") as mock_create_subprocess:
            mock_process = AsyncMock()
            mock_process.wait.side_effect = asyncio.TimeoutError()
            mock_process.terminate.return_value = None
            mock_create_subprocess.return_value = mock_process

            with patch("asyncio.wait_for") as mock_wait_for:
                mock_wait_for.side_effect = asyncio.TimeoutError()

                result = await check_npx_package("slow-package", ["--version"])

                assert result is False
                mock_process.terminate.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_npx_package_npx_not_available(self):
        """Test npx package check when npx is not available."""
        with patch("asyncio.create_subprocess_exec") as mock_create_subprocess:
            mock_create_subprocess.side_effect = FileNotFoundError()

            result = await check_npx_package("some-package", ["--help"])

            assert result is False

    @pytest.mark.asyncio
    async def test_check_npx_package_with_custom_command(self):
        """Test npx package check with custom check arguments."""
        with patch("asyncio.create_subprocess_exec") as mock_create_subprocess:
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.wait.return_value = None
            mock_create_subprocess.return_value = mock_process

            result = await check_npx_package(
                "some-package@latest", ["--help", "--verbose"]
            )

            assert result is True
            mock_create_subprocess.assert_called_once_with(
                "npx",
                "some-package@latest",
                "--help",
                "--verbose",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )


class TestPythonVersionChecking:
    """Test Python version checking."""

    def test_check_python_version_success(self):
        """Test Python version check when version meets requirements."""
        with patch("sys.version_info", (3, 9, 0)):
            result = check_python_version((3, 8))
            assert result is True

    def test_check_python_version_failure(self):
        """Test Python version check when version doesn't meet requirements."""
        with patch("sys.version_info", (3, 7, 0)):
            result = check_python_version((3, 8))
            assert result is False

    def test_check_python_version_exact_match(self):
        """Test Python version check with exact version match."""
        with patch("sys.version_info", (3, 8, 0)):
            result = check_python_version((3, 8))
            assert result is True

    def test_check_python_version_with_custom_executable(self):
        """Test Python version check with default parameters."""
        # Test the default behavior
        result = check_python_version()
        # Should return True since we're running with Python 3.8+
        assert result is True

    def test_check_python_version_higher_requirement(self):
        """Test Python version check with higher version requirement."""
        with patch("sys.version_info", (3, 8, 5)):
            result = check_python_version((3, 10))
            assert result is False


class TestValidatorsEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_npm_package_operations_empty_package_name(self):
        """Test npm operations with empty package name."""
        with patch("asyncio.create_subprocess_exec") as mock_create_subprocess:
            mock_process = AsyncMock()
            mock_process.returncode = 1
            mock_process.wait.return_value = None
            mock_create_subprocess.return_value = mock_process

            result = await check_npm_package_global("")
            assert result is False

            result = await install_npm_package_global("")
            assert result is False

    def test_python_version_check_empty_version(self):
        """Test Python version check with invalid version tuple."""
        with patch("sys.version_info", (3, 8, 0)):
            # Test with empty tuple - should handle gracefully
            result = check_python_version(())
            assert result is True  # Empty tuple should be less than any version

    @pytest.mark.asyncio
    async def test_command_with_timeout(self):
        """Test CLI command execution behavior under timeout conditions."""
        with patch("asyncio.create_subprocess_exec") as mock_create_subprocess:
            mock_process = AsyncMock()
            mock_process.returncode = 0
            # Simulate a quick command that finishes normally
            mock_process.wait.return_value = None
            mock_create_subprocess.return_value = mock_process

            result = await check_cli_command(["echo", "quick"])
            assert result is True

    @pytest.mark.asyncio
    async def test_command_with_timeout_exception(self):
        """Test handling of timeout in npx package check."""
        with patch("asyncio.create_subprocess_exec") as mock_create_subprocess:
            mock_process = AsyncMock()
            mock_process.terminate.return_value = None
            mock_process.wait.return_value = None
            mock_create_subprocess.return_value = mock_process

            # Mock wait_for to simulate timeout
            with patch("asyncio.wait_for") as mock_wait_for:
                mock_wait_for.side_effect = asyncio.TimeoutError()

                result = await check_npx_package("timeout-package", ["--version"])

                assert result is False
                mock_process.terminate.assert_called_once()


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""

    @pytest.mark.asyncio
    async def test_dependency_chain_checking(self):
        """Test checking a chain of dependencies."""
        # Test a realistic scenario of checking multiple tools
        commands_to_check = [
            ["git", "--version"],
            ["node", "--version"],
            ["npm", "--version"],
        ]

        with patch("asyncio.create_subprocess_exec") as mock_create_subprocess:
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.wait.return_value = None
            mock_create_subprocess.return_value = mock_process

            results = []
            for cmd in commands_to_check:
                result = await check_cli_command(cmd)
                results.append(result)

            assert all(results)  # All should succeed
            assert mock_create_subprocess.call_count == len(commands_to_check)

    @pytest.mark.asyncio
    async def test_npm_install_workflow(self):
        """Test complete npm package install workflow."""
        package_name = "test-package"

        with patch("asyncio.create_subprocess_exec") as mock_create_subprocess:
            # First check returns False (not installed)
            # Then install returns True (successful install)
            # Then check returns True (now installed)
            mock_process = AsyncMock()
            mock_process.wait.return_value = None
            mock_create_subprocess.return_value = mock_process

            # Setup return codes: not installed, install success, now installed
            mock_process.returncode = 1  # First check - not installed
            initially_installed = await check_npm_package_global(package_name)
            assert initially_installed is False

            mock_process.returncode = 0  # Install success
            install_result = await install_npm_package_global(package_name)
            assert install_result is True

            mock_process.returncode = 0  # Now installed
            finally_installed = await check_npm_package_global(package_name)
            assert finally_installed is True

    def test_python_environment_validation(self):
        """Test Python environment validation scenarios."""
        # Test various Python version scenarios
        test_cases = [
            ((3, 8), (3, 8), True),  # Exact match
            ((3, 9), (3, 8), True),  # Higher version
            ((3, 7), (3, 8), False),  # Lower version
            ((3, 8, 5), (3, 8), True),  # Patch version higher
        ]

        for current_version, min_version, expected in test_cases:
            with patch("sys.version_info", current_version):
                result = check_python_version(min_version)
                assert result == expected, (
                    f"Failed for {current_version} >= {min_version}"
                )
