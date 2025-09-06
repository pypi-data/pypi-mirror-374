"""Provider manager for coordinating all LLM API providers."""

from typing import Dict, List, Optional

from rich.console import Console
from rich.table import Table

from ..managers.port import PortManager
from ..managers.state import AuthStatus, StateManager
from ..providers import PROVIDERS
from ..providers.base import BaseProvider


class ProviderManager:
    """Manages all LLM API providers."""

    def __init__(self):
        self.providers: Dict[str, BaseProvider] = {}
        self.port_manager = PortManager()
        self.console = Console()
        self._state_manager = StateManager()

    def initialize_providers(self, provider_names: Optional[List[str]] = None) -> None:
        """Initialize requested providers."""
        if provider_names is None:
            provider_names = list(PROVIDERS.keys())

        for name in provider_names:
            if name in PROVIDERS:
                provider = PROVIDERS[name]()
                self.providers[name] = provider
            else:
                self.console.print(f"[red]Unknown provider: {name}[/red]")

    async def install_providers(
        self, provider_names: Optional[List[str]] = None
    ) -> bool:
        """Install specified providers."""
        if provider_names is None:
            provider_names = list(self.providers.keys())

        success = True
        for name in provider_names:
            if name not in self.providers:
                self.console.print(f"[red]Provider {name} not initialized[/red]")
                success = False
                continue

            provider = self.providers[name]
            self.console.print(f"[blue]Installing {name}...[/blue]")

            if await provider.install():
                self.console.print(f"[green]✓ {name} installed successfully[/green]")
            else:
                self.console.print(f"[red]✗ Failed to install {name}[/red]")
                success = False

        return success

    async def start_providers(
        self,
        provider_names: Optional[List[str]] = None,
        ports: Optional[Dict[str, int]] = None,
    ) -> bool:
        """Start specified providers."""
        if provider_names is None:
            provider_names = list(self.providers.keys())

        if ports is None:
            ports = {}

        success = True
        for name in provider_names:
            if name not in self.providers:
                self.console.print(f"[red]Provider {name} not initialized[/red]")
                success = False
                continue

            provider = self.providers[name]

            # Check if provider is already running
            if provider.is_running:
                current_port = provider.current_port
                self.console.print(
                    f"[yellow]⚠️  {name} is already running on port {current_port}[/yellow]"
                )
                self.console.print(
                    f"[yellow]Only one instance of {name} can run at a time.[/yellow]"
                )

                # Ask user if they want to restart the provider
                try:
                    response = (
                        input(
                            f"Do you want to stop the current {name} instance and start a new one? (y/N): "
                        )
                        .strip()
                        .lower()
                    )

                    if response in ["y", "yes"]:
                        self.console.print(
                            f"[blue]Stopping existing {name} instance...[/blue]"
                        )
                        if not await provider.stop():
                            self.console.print(
                                f"[red]✗ Failed to stop existing {name} instance[/red]"
                            )
                            success = False
                            continue
                        self.console.print(
                            f"[green]✓ Stopped existing {name} instance[/green]"
                        )
                    else:
                        self.console.print(
                            f"[yellow]Skipping {name} - already running[/yellow]"
                        )
                        continue

                except (KeyboardInterrupt, EOFError):
                    self.console.print(
                        f"\n[yellow]Skipping {name} - already running[/yellow]"
                    )
                    continue

            if not provider.is_installed:
                self.console.print(
                    f"[yellow]Provider {name} not installed, "
                    f"installing first...[/yellow]"
                )
                if not await provider.install():
                    self.console.print(f"[red]✗ Failed to install {name}[/red]")
                    success = False
                    continue

            try:
                port = self.port_manager.get_available_port(name, ports.get(name))
                self.console.print(f"[blue]Starting {name} on port {port}...[/blue]")

                if await provider.start(port):
                    self.console.print(
                        f"[green]✓ {name} started on port {port}[/green]"
                    )
                else:
                    self.console.print(f"[red]✗ Failed to start {name}[/red]")
                    success = False
            except Exception as e:
                self.console.print(f"[red]✗ Error starting {name}: {e}[/red]")
                success = False

        return success

    async def stop_providers(self, provider_names: Optional[List[str]] = None) -> bool:
        """Stop specified providers."""
        if provider_names is None:
            provider_names = list(self.providers.keys())

        success = True
        for name in provider_names:
            if name not in self.providers:
                continue

            provider = self.providers[name]

            if provider.is_running:
                self.console.print(f"[blue]Stopping {name}...[/blue]")
                if await provider.stop():
                    self.console.print(f"[green]✓ {name} stopped[/green]")
                else:
                    self.console.print(f"[red]✗ Failed to stop {name}[/red]")
                    success = False

        return success

    async def show_status(self) -> None:
        """Show status of all providers."""
        # Clean up dead processes first
        self._state_manager.cleanup_dead_processes()

        table = Table(title="LLM API Gateway Status")
        table.add_column("Provider", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Port", style="yellow")
        table.add_column("Health", style="magenta")
        table.add_column("Auth", style="blue")
        table.add_column("Installed", style="white")

        for name, provider in self.providers.items():
            status = "Running" if provider.is_running else "Stopped"
            port = str(provider.current_port) if provider.current_port else "-"
            installed = "Yes" if provider.is_installed else "No"

            # Check health if running
            health = "-"
            if provider.is_running:
                try:
                    health = "Healthy" if await provider.health_check() else "Unhealthy"
                except Exception:
                    health = "Unknown"

            # Get authentication status
            auth_status = provider.get_authentication_status()
            auth_display = {
                AuthStatus.NOT_REQUIRED: "➖ Not Required",
                AuthStatus.REQUIRED: "🔑 Auth Required",
                AuthStatus.AUTHENTICATED: "✅ Authenticated",
                AuthStatus.FAILED: "❌ Auth Failed",
            }.get(auth_status, "❓ Unknown")

            table.add_row(name, status, port, health, auth_display, installed)

        self.console.print(table)
