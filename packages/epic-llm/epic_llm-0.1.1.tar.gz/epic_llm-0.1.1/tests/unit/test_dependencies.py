"""Tests for the dependencies system."""

from unittest.mock import patch

import pytest
from rich.console import Console

from epic_llm.utils.dependencies import (
    Dependency,
    DependencyChecker,
    DependencyType,
)


class TestDependencyClass:
    """Test Dependency dataclass."""

    def test_dependency_creation(self):
        """Test basic dependency creation."""
        dep = Dependency(
            name="git",
            type=DependencyType.CLI_COMMAND,
            description="Git version control",
            check_command=["git", "--version"],
        )

        assert dep.name == "git"
        assert dep.type == DependencyType.CLI_COMMAND
        assert dep.description == "Git version control"
        assert dep.required is True  # Default value
        assert dep.check_command == ["git", "--version"]

    def test_dependency_with_install_command(self):
        """Test dependency with install command."""
        dep = Dependency(
            name="node",
            type=DependencyType.EXECUTABLE,
            description="Node.js runtime",
            executable="node",
            install_command="apt install nodejs",
            auto_install=True,
        )

        assert dep.install_command == "apt install nodejs"
        assert dep.auto_install is True

    def test_dependency_with_install_instructions(self):
        """Test dependency with install instructions."""
        dep = Dependency(
            name="copilot-api",
            type=DependencyType.NPX_PACKAGE,
            description="Copilot API service",
            npx_url="copilot-api@latest",
            npx_check_args=["--help"],
            install_instructions="Run: npm install -g copilot-api",
            required=False,
        )

        assert dep.install_instructions == "Run: npm install -g copilot-api"
        assert dep.required is False

    def test_dependency_defaults(self):
        """Test dependency default values."""
        dep = Dependency(
            name="test", type=DependencyType.CLI_COMMAND, description="Test dependency"
        )

        assert dep.required is True
        assert dep.check_command is None
        assert dep.executable is None
        assert dep.npm_package is None
        assert dep.npx_url is None
        assert dep.npx_check_args is None
        assert dep.min_python_version is None
        assert dep.install_command is None
        assert dep.install_instructions is None
        assert dep.auto_install is False


class TestDependencyChecker:
    """Test DependencyChecker class."""

    def test_dependency_checker_initialization(self):
        """Test DependencyChecker initialization."""
        checker = DependencyChecker()

        assert isinstance(checker.console, Console)
        assert isinstance(checker._dependency_cache, dict)
        assert len(checker._dependency_cache) == 0


class TestCheckDependency:
    """Test individual dependency checking."""

    @pytest.mark.asyncio
    async def test_check_cli_command_dependency(self):
        """Test checking CLI command dependency."""
        dep = Dependency(
            name="git",
            type=DependencyType.CLI_COMMAND,
            description="Git VCS",
            check_command=["git", "--version"],
        )

        checker = DependencyChecker()

        with patch("epic_llm.utils.dependencies.check_cli_command") as mock_check:
            mock_check.return_value = True

            result = await checker.check_dependency(dep)

            assert result is True
            mock_check.assert_called_once_with(["git", "--version"])

    @pytest.mark.asyncio
    async def test_check_executable_dependency(self):
        """Test checking executable dependency."""
        dep = Dependency(
            name="python",
            type=DependencyType.EXECUTABLE,
            description="Python interpreter",
            executable="python3",
        )

        checker = DependencyChecker()

        with patch(
            "epic_llm.utils.dependencies.check_executable_in_path"
        ) as mock_check:
            mock_check.return_value = True

            result = await checker.check_dependency(dep)

            assert result is True
            mock_check.assert_called_once_with("python3")

    @pytest.mark.asyncio
    async def test_check_npm_global_dependency(self):
        """Test checking NPM global dependency."""
        dep = Dependency(
            name="lodash",
            type=DependencyType.NPM_GLOBAL,
            description="Utility library",
            npm_package="lodash",
        )

        checker = DependencyChecker()

        with patch(
            "epic_llm.utils.dependencies.check_npm_package_global"
        ) as mock_check:
            mock_check.return_value = True

            result = await checker.check_dependency(dep)

            assert result is True
            mock_check.assert_called_once_with("lodash")

    @pytest.mark.asyncio
    async def test_check_npx_package_dependency(self):
        """Test checking NPX package dependency."""
        dep = Dependency(
            name="create-react-app",
            type=DependencyType.NPX_PACKAGE,
            description="React app generator",
            npx_url="create-react-app@latest",
            npx_check_args=["--version"],
        )

        checker = DependencyChecker()

        with patch("epic_llm.utils.dependencies.check_npx_package") as mock_check:
            mock_check.return_value = True

            result = await checker.check_dependency(dep)

            assert result is True
            mock_check.assert_called_once_with("create-react-app@latest", ["--version"])

    @pytest.mark.asyncio
    async def test_check_python_version_dependency(self):
        """Test checking Python version dependency."""
        dep = Dependency(
            name="python3.8+",
            type=DependencyType.PYTHON_VERSION,
            description="Python 3.8 or higher",
            min_python_version=(3, 8),
        )

        checker = DependencyChecker()

        with patch("epic_llm.utils.dependencies.check_python_version") as mock_check:
            mock_check.return_value = True

            result = await checker.check_dependency(dep)

            assert result is True
            mock_check.assert_called_once_with((3, 8))

    @pytest.mark.asyncio
    async def test_check_python_version_dependency_default(self):
        """Test checking Python version dependency with default version."""
        dep = Dependency(
            name="python",
            type=DependencyType.PYTHON_VERSION,
            description="Python interpreter",
        )

        checker = DependencyChecker()

        with patch("epic_llm.utils.dependencies.check_python_version") as mock_check:
            mock_check.return_value = True

            result = await checker.check_dependency(dep)

            assert result is True
            mock_check.assert_called_once_with((3, 8))  # Default version

    @pytest.mark.asyncio
    async def test_check_dependency_caching(self):
        """Test dependency check result caching."""
        dep = Dependency(
            name="git",
            type=DependencyType.CLI_COMMAND,
            description="Git VCS",
            check_command=["git", "--version"],
        )

        checker = DependencyChecker()

        with patch("epic_llm.utils.dependencies.check_cli_command") as mock_check:
            mock_check.return_value = True

            # First call should invoke the check
            result1 = await checker.check_dependency(dep)
            assert result1 is True
            assert mock_check.call_count == 1

            # Second call should use cache
            result2 = await checker.check_dependency(dep)
            assert result2 is True
            assert mock_check.call_count == 1  # Should not be called again

    @pytest.mark.asyncio
    async def test_check_dependency_missing_config(self):
        """Test checking dependency with missing configuration."""
        # CLI command without check_command
        dep = Dependency(
            name="test", type=DependencyType.CLI_COMMAND, description="Test tool"
        )

        checker = DependencyChecker()
        result = await checker.check_dependency(dep)

        assert result is False

    @pytest.mark.asyncio
    async def test_check_dependencies_multiple(self):
        """Test checking multiple dependencies."""
        deps = [
            Dependency(
                "git",
                DependencyType.CLI_COMMAND,
                "Git VCS",
                check_command=["git", "--version"],
            ),
            Dependency(
                "python", DependencyType.EXECUTABLE, "Python", executable="python3"
            ),
        ]

        checker = DependencyChecker()

        with patch("epic_llm.utils.dependencies.check_cli_command") as mock_cli:
            with patch(
                "epic_llm.utils.dependencies.check_executable_in_path"
            ) as mock_exec:
                mock_cli.return_value = True
                mock_exec.return_value = False

                results = await checker.check_dependencies(deps)

                assert results == {"git": True, "python": False}
                mock_cli.assert_called_once_with(["git", "--version"])
                mock_exec.assert_called_once_with("python3")


class TestInstallDependency:
    """Test dependency installation."""

    @pytest.mark.asyncio
    async def test_install_npm_dependency_success(self):
        """Test successful NPM dependency installation."""
        dep = Dependency(
            name="lodash",
            type=DependencyType.NPM_GLOBAL,
            description="Utility library",
            npm_package="lodash",
            auto_install=True,
        )

        checker = DependencyChecker()

        with patch(
            "epic_llm.utils.dependencies.install_npm_package_global"
        ) as mock_install:
            mock_install.return_value = True

            result = await checker.install_dependency(dep)

            assert result is True
            mock_install.assert_called_once_with("lodash")

    @pytest.mark.asyncio
    async def test_install_npm_dependency_failure(self):
        """Test failed NPM dependency installation."""
        dep = Dependency(
            name="invalid-package",
            type=DependencyType.NPM_GLOBAL,
            description="Invalid package",
            npm_package="invalid-package",
            auto_install=True,
        )

        checker = DependencyChecker()

        with patch(
            "epic_llm.utils.dependencies.install_npm_package_global"
        ) as mock_install:
            mock_install.return_value = False

            result = await checker.install_dependency(dep)

            assert result is False

    @pytest.mark.asyncio
    async def test_install_dependency_auto_install_disabled(self):
        """Test installation attempt when auto_install is disabled."""
        dep = Dependency(
            name="some-package",
            type=DependencyType.NPM_GLOBAL,
            description="Some package",
            npm_package="some-package",
            auto_install=False,
        )

        checker = DependencyChecker()
        result = await checker.install_dependency(dep)

        assert result is False

    @pytest.mark.asyncio
    async def test_install_dependency_unsupported_type(self):
        """Test installation attempt for unsupported dependency type."""
        dep = Dependency(
            name="python",
            type=DependencyType.EXECUTABLE,
            description="Python interpreter",
            auto_install=True,
        )

        checker = DependencyChecker()
        result = await checker.install_dependency(dep)

        assert result is False

    @pytest.mark.asyncio
    async def test_install_dependency_clears_cache(self):
        """Test that successful installation clears the cache."""
        dep = Dependency(
            name="test-package",
            type=DependencyType.NPM_GLOBAL,
            description="Test package",
            npm_package="test-package",
            auto_install=True,
        )

        checker = DependencyChecker()

        # Pre-populate cache
        cache_key = f"{dep.type.value}:{dep.name}"
        checker._dependency_cache[cache_key] = False

        with patch(
            "epic_llm.utils.dependencies.install_npm_package_global"
        ) as mock_install:
            mock_install.return_value = True

            result = await checker.install_dependency(dep)

            assert result is True
            assert cache_key not in checker._dependency_cache


class TestDisplayMethods:
    """Test display and reporting methods."""

    def test_show_dependency_status_all_success(self):
        """Test displaying status when all dependencies are satisfied."""
        deps = [
            Dependency("git", DependencyType.CLI_COMMAND, "Git VCS"),
            Dependency("python", DependencyType.EXECUTABLE, "Python interpreter"),
        ]
        results = {"git": True, "python": True}

        checker = DependencyChecker()

        with patch.object(checker.console, "print") as mock_print:
            checker.show_dependency_status(deps, results)

            # Should print the table
            mock_print.assert_called()

    def test_show_dependency_status_mixed_results(self):
        """Test displaying status with mixed results."""
        deps = [
            Dependency("git", DependencyType.CLI_COMMAND, "Git VCS", required=True),
            Dependency(
                "optional-tool",
                DependencyType.EXECUTABLE,
                "Optional tool",
                required=False,
            ),
        ]
        results = {"git": True, "optional-tool": False}

        checker = DependencyChecker()

        with patch.object(checker.console, "print") as mock_print:
            checker.show_dependency_status(deps, results)

            mock_print.assert_called()

    def test_show_dependency_status_hide_optional(self):
        """Test displaying status with optional dependencies hidden."""
        deps = [
            Dependency("git", DependencyType.CLI_COMMAND, "Git VCS", required=True),
            Dependency(
                "optional-tool",
                DependencyType.EXECUTABLE,
                "Optional tool",
                required=False,
            ),
        ]
        results = {"git": True, "optional-tool": False}

        checker = DependencyChecker()

        with patch.object(checker.console, "print") as mock_print:
            checker.show_dependency_status(deps, results, show_optional=False)

            mock_print.assert_called()

    def test_show_installation_instructions_no_missing(self):
        """Test installation instructions when no dependencies are missing."""
        deps = [
            Dependency("git", DependencyType.CLI_COMMAND, "Git VCS"),
        ]
        results = {"git": True}

        checker = DependencyChecker()

        with patch.object(checker.console, "print") as mock_print:
            checker.show_installation_instructions(deps, results)

            # Should not print anything when no missing deps
            mock_print.assert_not_called()

    def test_show_installation_instructions_with_command(self):
        """Test installation instructions with install command."""
        deps = [
            Dependency(
                "git",
                DependencyType.CLI_COMMAND,
                "Git VCS",
                install_command="apt install git",
            ),
        ]
        results = {"git": False}

        checker = DependencyChecker()

        with patch.object(checker.console, "print") as mock_print:
            checker.show_installation_instructions(deps, results)

            mock_print.assert_called()
            # Check that install command is mentioned
            call_args = [call[0][0] for call in mock_print.call_args_list]
            install_mentioned = any("apt install git" in str(arg) for arg in call_args)
            assert install_mentioned

    def test_show_installation_instructions_with_instructions(self):
        """Test installation instructions with custom instructions."""
        deps = [
            Dependency(
                "special-tool",
                DependencyType.EXECUTABLE,
                "Special tool",
                install_instructions="Visit example.com to download",
            ),
        ]
        results = {"special-tool": False}

        checker = DependencyChecker()

        with patch.object(checker.console, "print") as mock_print:
            checker.show_installation_instructions(deps, results)

            mock_print.assert_called()
            call_args = [call[0][0] for call in mock_print.call_args_list]
            instructions_mentioned = any(
                "Visit example.com to download" in str(arg) for arg in call_args
            )
            assert instructions_mentioned


class TestCheckAndInstall:
    """Test the comprehensive check_and_install workflow."""

    @pytest.mark.asyncio
    async def test_check_and_install_all_satisfied(self):
        """Test check_and_install when all dependencies are satisfied."""
        deps = [
            Dependency(
                "git",
                DependencyType.CLI_COMMAND,
                "Git VCS",
                check_command=["git", "--version"],
            ),
        ]

        checker = DependencyChecker()

        with patch.object(checker, "check_dependencies") as mock_check:
            with patch.object(checker, "show_dependency_status") as mock_show:
                mock_check.return_value = {"git": True}

                result = await checker.check_and_install(deps)

                assert result is True
                mock_check.assert_called_once_with(deps)
                mock_show.assert_called_once_with(deps, {"git": True})

    @pytest.mark.asyncio
    async def test_check_and_install_with_missing_deps(self):
        """Test check_and_install with missing dependencies."""
        deps = [
            Dependency(
                "missing-tool",
                DependencyType.NPM_GLOBAL,
                "Missing tool",
                npm_package="missing-tool",
                auto_install=True,
            ),
        ]

        checker = DependencyChecker()

        with patch.object(checker, "check_dependencies") as mock_check:
            with patch.object(checker, "install_dependency") as mock_install:
                with patch.object(checker, "show_dependency_status"):
                    with patch.object(checker, "show_installation_instructions"):
                        mock_check.return_value = {"missing-tool": False}
                        mock_install.return_value = True

                        result = await checker.check_and_install(
                            deps, auto_install=True
                        )

                        assert result is True
                        mock_install.assert_called_once_with(deps[0])

    @pytest.mark.asyncio
    async def test_check_and_install_no_auto_install(self):
        """Test check_and_install without auto-installation."""
        deps = [
            Dependency("missing-tool", DependencyType.CLI_COMMAND, "Missing tool"),
        ]

        checker = DependencyChecker()

        with patch.object(checker, "check_dependencies") as mock_check:
            with patch.object(
                checker, "show_installation_instructions"
            ) as mock_instructions:
                mock_check.return_value = {"missing-tool": False}

                result = await checker.check_and_install(deps, auto_install=False)

                assert result is False
                mock_instructions.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_and_install_installation_failure(self):
        """Test check_and_install when installation fails."""
        deps = [
            Dependency(
                "failing-tool",
                DependencyType.NPM_GLOBAL,
                "Tool that fails to install",
                npm_package="failing-tool",
                auto_install=True,
            ),
        ]

        checker = DependencyChecker()

        with patch.object(checker, "check_dependencies") as mock_check:
            with patch.object(checker, "install_dependency") as mock_install:
                with patch.object(
                    checker, "show_installation_instructions"
                ) as mock_instructions:
                    mock_check.return_value = {"failing-tool": False}
                    mock_install.return_value = False

                    result = await checker.check_and_install(deps, auto_install=True)

                    assert result is False
                    mock_install.assert_called_once_with(deps[0])
                    mock_instructions.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_and_install_no_status_display(self):
        """Test check_and_install with status display disabled."""
        deps = [
            Dependency("git", DependencyType.CLI_COMMAND, "Git VCS"),
        ]

        checker = DependencyChecker()

        with patch.object(checker, "check_dependencies") as mock_check:
            with patch.object(checker, "show_dependency_status") as mock_show:
                mock_check.return_value = {"git": True}

                result = await checker.check_and_install(deps, show_status=False)

                assert result is True
                mock_show.assert_not_called()


class TestIntegrationScenarios:
    """Test complex integration scenarios."""

    @pytest.mark.asyncio
    async def test_complete_dependency_workflow(self):
        """Test a complete dependency checking and installation workflow."""
        deps = [
            Dependency(
                "git",
                DependencyType.CLI_COMMAND,
                "Git VCS",
                check_command=["git", "--version"],
                required=True,
            ),
            Dependency(
                "auto-package",
                DependencyType.NPM_GLOBAL,
                "Auto-installable package",
                npm_package="auto-package",
                auto_install=True,
                required=True,
            ),
            Dependency(
                "manual-tool",
                DependencyType.EXECUTABLE,
                "Manual installation tool",
                executable="manual-tool",
                install_instructions="Please install manually",
                required=True,
            ),
        ]

        checker = DependencyChecker()

        with patch("epic_llm.utils.dependencies.check_cli_command") as mock_cli:
            with patch(
                "epic_llm.utils.dependencies.install_npm_package_global"
            ) as mock_npm:
                with patch(
                    "epic_llm.utils.dependencies.check_npm_package_global"
                ) as mock_npm_check:
                    with patch(
                        "epic_llm.utils.dependencies.check_executable_in_path"
                    ) as mock_exec:
                        # Git available, auto-package missing but installable, manual-tool missing
                        mock_cli.return_value = True
                        mock_npm_check.side_effect = [
                            False,
                            True,
                        ]  # First false, then true after install
                        mock_npm.return_value = True
                        mock_exec.return_value = False

                        result = await checker.check_and_install(
                            deps, auto_install=True, show_status=False
                        )

                        # Should fail because manual-tool can't be auto-installed
                        assert result is False
                        mock_npm.assert_called_once_with("auto-package")

    @pytest.mark.asyncio
    async def test_dependency_status_reporting(self):
        """Test dependency status reporting with various scenarios."""
        deps = [
            Dependency(
                "available-req",
                DependencyType.EXECUTABLE,
                "Available required",
                executable="python",
                required=True,
            ),
            Dependency(
                "missing-req",
                DependencyType.EXECUTABLE,
                "Missing required",
                executable="missing",
                required=True,
            ),
            Dependency(
                "available-opt",
                DependencyType.EXECUTABLE,
                "Available optional",
                executable="ls",
                required=False,
            ),
            Dependency(
                "missing-opt",
                DependencyType.EXECUTABLE,
                "Missing optional",
                executable="missing-opt",
                required=False,
            ),
        ]

        checker = DependencyChecker()

        with patch(
            "epic_llm.utils.dependencies.check_executable_in_path"
        ) as mock_check:
            mock_check.side_effect = lambda exe: exe in ["python", "ls"]

            results = await checker.check_dependencies(deps)

            expected = {
                "available-req": True,
                "missing-req": False,
                "available-opt": True,
                "missing-opt": False,
            }
            assert results == expected

    def test_dependency_type_enum_values(self):
        """Test that DependencyType enum has expected values."""
        assert DependencyType.CLI_COMMAND.value == "cli_command"
        assert DependencyType.EXECUTABLE.value == "executable"
        assert DependencyType.NPM_GLOBAL.value == "npm_global"
        assert DependencyType.NPX_PACKAGE.value == "npx_package"
        assert DependencyType.PYTHON_VERSION.value == "python_version"
