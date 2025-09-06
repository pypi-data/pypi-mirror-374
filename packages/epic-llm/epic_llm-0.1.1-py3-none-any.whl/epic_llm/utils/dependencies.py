"""Core dependency checking system."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from rich.console import Console
from rich.table import Table

from .validators import (
    check_cli_command,
    check_executable_in_path,
    check_npm_package_global,
    check_npx_package,
    check_python_version,
    install_npm_package_global,
)


class DependencyType(Enum):
    """Types of dependencies that can be checked."""

    CLI_COMMAND = "cli_command"
    EXECUTABLE = "executable"
    NPM_GLOBAL = "npm_global"
    NPX_PACKAGE = "npx_package"
    PYTHON_VERSION = "python_version"


@dataclass
class Dependency:
    """Definition of a single dependency."""

    name: str
    type: DependencyType
    description: str
    required: bool = True

    # CLI command dependency
    check_command: Optional[List[str]] = None

    # Executable dependency
    executable: Optional[str] = None

    # NPM global package dependency
    npm_package: Optional[str] = None

    # NPX package dependency
    npx_url: Optional[str] = None
    npx_check_args: Optional[List[str]] = None

    # Python version dependency
    min_python_version: Optional[tuple] = None

    # Installation info
    install_command: Optional[str] = None
    install_instructions: Optional[str] = None
    auto_install: bool = False


class DependencyChecker:
    """Checks and manages provider dependencies."""

    def __init__(self):
        self.console = Console()
        self._dependency_cache: Dict[str, bool] = {}

    async def check_dependency(self, dep: Dependency) -> bool:
        """Check if a single dependency is satisfied."""
        cache_key = f"{dep.type.value}:{dep.name}"
        if cache_key in self._dependency_cache:
            return self._dependency_cache[cache_key]

        result = False

        if dep.type == DependencyType.CLI_COMMAND and dep.check_command:
            result = await check_cli_command(dep.check_command)

        elif dep.type == DependencyType.EXECUTABLE and dep.executable:
            result = check_executable_in_path(dep.executable)

        elif dep.type == DependencyType.NPM_GLOBAL and dep.npm_package:
            result = await check_npm_package_global(dep.npm_package)

        elif (
            dep.type == DependencyType.NPX_PACKAGE
            and dep.npx_url
            and dep.npx_check_args
        ):
            result = await check_npx_package(dep.npx_url, dep.npx_check_args)

        elif dep.type == DependencyType.PYTHON_VERSION:
            min_version = dep.min_python_version or (3, 8)
            result = check_python_version(min_version)

        self._dependency_cache[cache_key] = result
        return result

    async def check_dependencies(
        self, dependencies: List[Dependency]
    ) -> Dict[str, bool]:
        """Check multiple dependencies and return results."""
        results = {}
        for dep in dependencies:
            results[dep.name] = await self.check_dependency(dep)
        return results

    async def install_dependency(self, dep: Dependency) -> bool:
        """Attempt to automatically install a dependency."""
        if not dep.auto_install:
            return False

        if dep.type == DependencyType.NPM_GLOBAL and dep.npm_package:
            self.console.print(f"[blue]Installing {dep.npm_package}...[/blue]")
            success = await install_npm_package_global(dep.npm_package)
            if success:
                # Clear cache to force recheck
                cache_key = f"{dep.type.value}:{dep.name}"
                self._dependency_cache.pop(cache_key, None)
            return success

        return False

    def show_dependency_status(
        self,
        dependencies: List[Dependency],
        results: Dict[str, bool],
        show_optional: bool = True,
    ) -> None:
        """Display dependency check results in a table."""
        table = Table(title="Dependency Status")
        table.add_column("Dependency", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Type", style="magenta")
        table.add_column("Description", style="white")

        for dep in dependencies:
            if not show_optional and not dep.required:
                continue

            status = results.get(dep.name, False)
            status_text = (
                "[green]✓ Available[/green]" if status else "[red]✗ Missing[/red]"
            )
            required_text = "Required" if dep.required else "Optional"

            table.add_row(
                dep.name,
                status_text,
                f"{dep.type.value} ({required_text})",
                dep.description,
            )

        self.console.print(table)

    def show_installation_instructions(
        self, dependencies: List[Dependency], results: Dict[str, bool]
    ) -> None:
        """Show installation instructions for missing dependencies."""
        missing_deps = [
            dep
            for dep in dependencies
            if not results.get(dep.name, False) and dep.required
        ]

        if not missing_deps:
            return

        self.console.print("\\n[bold red]Missing Required Dependencies:[/bold red]")

        for dep in missing_deps:
            self.console.print(f"\\n[bold]{dep.name}[/bold]:")

            if dep.install_command:
                self.console.print(f"  [green]Install:[/green] {dep.install_command}")

            if dep.install_instructions:
                self.console.print(
                    f"  [yellow]Instructions:[/yellow] {dep.install_instructions}"
                )

    async def check_and_install(
        self,
        dependencies: List[Dependency],
        auto_install: bool = False,
        show_status: bool = True,
    ) -> bool:
        """Check dependencies and optionally auto-install missing ones."""
        results = await self.check_dependencies(dependencies)

        if show_status:
            self.show_dependency_status(dependencies, results)

        # Check if all required dependencies are satisfied
        missing_required = [
            dep
            for dep in dependencies
            if dep.required and not results.get(dep.name, False)
        ]

        if not missing_required:
            return True

        # Try auto-installation if enabled
        if auto_install:
            self.console.print(
                "\\n[blue]Attempting to install missing dependencies...[/blue]"
            )

            for dep in missing_required:
                if dep.auto_install:
                    success = await self.install_dependency(dep)
                    if success:
                        self.console.print(
                            f"[green]✓ Successfully installed {dep.name}[/green]"
                        )
                        results[dep.name] = True
                    else:
                        self.console.print(f"[red]✗ Failed to install {dep.name}[/red]")

            # Recheck missing required dependencies
            missing_required = [
                dep
                for dep in dependencies
                if dep.required and not results.get(dep.name, False)
            ]

        # Show installation instructions for remaining missing dependencies
        if missing_required:
            self.show_installation_instructions(dependencies, results)
            return False

        return True
