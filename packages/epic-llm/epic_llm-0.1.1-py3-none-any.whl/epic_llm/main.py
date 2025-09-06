"""Main CLI application using Typer."""

import asyncio
from typing import List, Optional

import typer
from rich.console import Console

from .managers.provider import ProviderManager

app = typer.Typer(help="Epic LLM - Unified tool to manage LLM API providers")
console = Console()


@app.command()
def install(
    providers: Optional[List[str]] = typer.Argument(
        None, help="Providers to install (default: all)"
    ),
):
    """Install LLM API providers."""

    async def _install():
        manager = ProviderManager()
        manager.initialize_providers(providers)
        await manager.install_providers(providers)

    asyncio.run(_install())


@app.command()
def start(
    providers: Optional[List[str]] = typer.Argument(
        None, help="Providers to start (default: all)"
    ),
    port: Optional[List[str]] = typer.Option(
        None,
        "--port",
        "-p",
        help="Port assignments (format: provider:port)",
    ),
):
    """Start LLM API providers."""

    async def _start():
        manager = ProviderManager()
        manager.initialize_providers(providers)

        # Parse port assignments
        port_map = {}
        if port:
            for p in port:
                if ":" in p:
                    provider_name, port_num = p.split(":", 1)
                    try:
                        port_map[provider_name] = int(port_num)
                    except ValueError:
                        console.print(f"[red]Invalid port number: {port_num}[/red]")
                        return
                else:
                    console.print(
                        f"[red]Invalid port format: {p}. Use provider:port[/red]"
                    )
                    return

        # Validate port assignments before starting
        if port_map:
            from .managers.port import PortManager

            port_manager = PortManager()
            validation_errors = port_manager.validate_port_assignments(port_map)
            if validation_errors:
                console.print("[red]Port conflict detected:[/red]")
                for error in validation_errors:
                    console.print(f"[red]  • {error}[/red]")
                console.print("\n[yellow]Suggestions:[/yellow]")
                console.print(
                    "  • Stop conflicting providers: [cyan]epic-llm stop <provider>[/cyan]"
                )
                console.print(
                    "  • Use different ports: [cyan]epic-llm start --port provider:PORT[/cyan]"
                )
                console.print(
                    "  • Check running processes: [cyan]ss -tlnp | grep :PORT[/cyan]"
                )
                return

        await manager.start_providers(providers, port_map)

    asyncio.run(_start())


@app.command()
def stop(
    providers: Optional[List[str]] = typer.Argument(
        None, help="Providers to stop (default: all)"
    ),
):
    """Stop LLM API providers."""

    async def _stop():
        manager = ProviderManager()
        manager.initialize_providers()  # Initialize all to check what's running
        await manager.stop_providers(providers)

    asyncio.run(_stop())


@app.command()
def status():
    """Show status of all providers."""

    async def _status():
        manager = ProviderManager()
        manager.initialize_providers()
        await manager.show_status()

    asyncio.run(_status())


@app.command()
def check(
    providers: Optional[List[str]] = typer.Argument(
        None, help="Providers to check (default: all)"
    ),
    auto_install: bool = typer.Option(
        False, "--install", "-i", help="Attempt to auto-install missing dependencies"
    ),
) -> None:
    """Check dependencies for providers."""

    async def _check() -> None:
        manager = ProviderManager()
        manager.initialize_providers(providers)

        success = True
        for name, provider in manager.providers.items():
            console.print(f"\n[bold]Checking dependencies for {name}:[/bold]")
            if not await provider.check_dependencies(auto_install=auto_install):
                success = False

        if success:
            console.print("\n[green]All dependencies satisfied![/green]")
        else:
            console.print("\n[red]Some dependencies are missing.[/red]")
            if not auto_install:
                console.print(
                    "[yellow]Run with --install to attempt "
                    "automatic installation.[/yellow]"
                )

    asyncio.run(_check())


@app.command()
def auth_status(
    providers: Optional[List[str]] = typer.Argument(
        None, help="Providers to check auth status (default: all)"
    ),
) -> None:
    """Show detailed authentication status for providers."""

    async def _auth_status() -> None:
        manager = ProviderManager()
        manager.initialize_providers(providers)

        for name, provider in manager.providers.items():
            console.print(f"\n[bold]Authentication Status for {name}:[/bold]")

            if not provider.is_authentication_required():
                console.print("  ➖ Authentication not required")
                continue

            auth_status = provider.get_authentication_status()
            status_display = {
                "not_required": "➖ Not Required",
                "required": "🔑 Authentication Required",
                "authenticated": "✅ Authenticated",
                "failed": "❌ Authentication Failed",
            }.get(auth_status.value, "❓ Unknown")

            console.print(f"  Status: {status_display}")

            # Show detailed info for providers with authentication
            if hasattr(provider, "get_credential_info"):
                try:
                    # Run fresh validation to get current status
                    if hasattr(provider, "validate_authentication"):
                        fresh_status = await provider.validate_authentication()
                        status_display = {
                            "not_required": "➖ Not Required",
                            "required": "🔑 Authentication Required",
                            "authenticated": "✅ Authenticated",
                            "failed": "❌ Authentication Failed",
                        }.get(fresh_status.value, "❓ Unknown")
                        console.print(f"  Fresh Status: {status_display}")

                    cred_info = await provider.get_credential_info()
                    if cred_info and cred_info.get("status") != "no_credentials":
                        # Claude-specific information
                        if name == "claude":
                            if cred_info.get("claude_username"):
                                console.print(
                                    f"  Claude Username: {cred_info['claude_username']}"
                                )
                            if cred_info.get("claude_version"):
                                console.print(
                                    f"  Claude CLI Version: "
                                    f"{cred_info['claude_version']}"
                                )
                            if cred_info.get("credentials_file_exists"):
                                console.print(
                                    f"  Credentials File: "
                                    f"{'Yes' if cred_info['credentials_file_exists'] else 'No'}"
                                )
                                if cred_info.get("is_secure") is not None:
                                    secure_status = (
                                        "✅ Secure"
                                        if cred_info["is_secure"]
                                        else "⚠️  Insecure permissions"
                                    )
                                    console.print(f"  File Security: {secure_status}")

                        # Copilot-specific information
                        elif name == "copilot":
                            if cred_info.get("github_username"):
                                console.print(
                                    f"  GitHub Username: {cred_info['github_username']}"
                                )
                            if cred_info.get("github_token_file_exists"):
                                console.print(
                                    f"  GitHub Token File: "
                                    f"{'Yes' if cred_info['github_token_file_exists'] else 'No'}"
                                )
                                if cred_info.get("is_secure") is not None:
                                    secure_status = (
                                        "✅ Secure"
                                        if cred_info["is_secure"]
                                        else "⚠️  Insecure permissions"
                                    )
                                    console.print(f"  File Security: {secure_status}")
                            if cred_info.get("copilot_subscription"):
                                subscription = cred_info["copilot_subscription"]
                                if isinstance(subscription, dict):
                                    console.print("  Copilot Subscription: ✅ Active")
                                else:
                                    console.print("  Copilot Subscription: ⚠️  Unknown")

                    else:
                        console.print("  No credential file found")
                        await provider.handle_authentication_prompt()
                except Exception as e:
                    console.print(f"  [red]Error checking credentials: {e}[/red]")

    asyncio.run(_auth_status())


@app.command()
def list() -> None:
    """List available providers."""
    from .providers import PROVIDERS

    console.print("[bold]Available providers:[/bold]")
    for name in PROVIDERS.keys():
        console.print(f"  • {name}")


@app.command()
def set_gateway_key(
    provider: str = typer.Argument(..., help="Provider name"),
    api_key: str = typer.Option(
        None, "--key", help="Gateway API key (empty to disable)"
    ),
):
    """Set gateway API key for provider."""
    from .providers import PROVIDERS
    from .utils.gateway import GatewayKeySupport

    try:
        # Create provider instance
        provider_class = PROVIDERS.get(provider.lower())
        if not provider_class:
            console.print(f"[red]❌ Unknown provider: {provider}[/red]")
            return

        provider_instance = provider_class()

        # Check if provider supports gateway keys
        if provider_instance.gw_key_num_support == GatewayKeySupport.NONE:
            console.print(
                f"[red]❌ Provider '{provider}' does not support gateway keys[/red]"
            )
            console.print("[dim]💡 Supported providers: claude, gemini[/dim]")
            return

        if api_key:
            provider_instance.set_gateway_key(api_key)
            support_level = provider_instance.gw_key_num_support.value
            console.print(f"[green]✅ Gateway API key set for {provider}[/green]")
            console.print("[cyan]🔐 Authentication enabled[/cyan]")
            console.print(
                f"[dim]📋 Key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else api_key}[/dim]"
            )
            console.print(f"[dim]🔧 Support level: {support_level}[/dim]")
        else:
            provider_instance.set_gateway_key(None)
            console.print(f"[green]✅ Gateway API key removed for {provider}[/green]")
            console.print("[cyan]🔓 Authentication disabled[/cyan]")

    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Error setting gateway key: {e}[/red]")


@app.command()
def show_gateway_key(
    provider: str = typer.Argument(..., help="Provider name"),
):
    """Show current gateway API key status."""
    from .providers import PROVIDERS
    from .utils.gateway import GatewayKeySupport

    try:
        # Create provider instance
        provider_class = PROVIDERS.get(provider.lower())
        if not provider_class:
            console.print(f"[red]❌ Unknown provider: {provider}[/red]")
            return

        provider_instance = provider_class()

        # Check if provider supports gateway keys
        if provider_instance.gw_key_num_support == GatewayKeySupport.NONE:
            console.print(
                f"[red]❌ Provider '{provider}' does not support gateway keys[/red]"
            )
            console.print("[dim]💡 Supported providers: claude, gemini[/dim]")
            return

        key = provider_instance.get_gateway_key()
        support_level = provider_instance.gw_key_num_support.value

        if key:
            console.print("[cyan]🔐 Gateway authentication: ENABLED[/cyan]")
            console.print(
                f"[dim]📋 API Key: {key[:8]}...{key[-4:] if len(key) > 12 else key}[/dim]"
            )
            console.print(f"[dim]🔧 Support level: {support_level}[/dim]")

            # Show usage example based on provider
            port = provider_instance.default_port
            console.print("\n[yellow]Usage example:[/yellow]")
            console.print(f'[dim]curl -H "Authorization: Bearer {key}" \\[/dim]')
            console.print(f"[dim]     http://localhost:{port}/v1/models[/dim]")
        else:
            console.print("[cyan]🔓 Gateway authentication: DISABLED[/cyan]")
            console.print(f"[dim]🔧 Support level: {support_level}[/dim]")
            console.print(
                f'[yellow]💡 Enable with: epic-llm set-gateway-key {provider} --key "your-api-key"[/yellow]'
            )

    except Exception as e:
        console.print(f"[red]❌ Error getting gateway key: {e}[/red]")


@app.command()
def logs(
    provider: str = typer.Argument(..., help="Provider name (claude, gemini, copilot, or 'all')"),
    log_type: str = typer.Option(
        "stdout", 
        "--type", 
        "-t", 
        help="Log type (stdout, stderr, epic-llm)"
    ),
    tail: int = typer.Option(
        50, 
        "--tail", 
        "-n", 
        help="Number of lines to show"
    ),
    follow: bool = typer.Option(
        False,
        "--follow",
        "-f",
        help="Follow logs in real-time (like tail -f)"
    ),
    filter_term: Optional[str] = typer.Option(
        None,
        "--filter",
        help="Filter lines containing this term"
    ),
    clear: bool = typer.Option(
        False,
        "--clear",
        help="Clear logs for the provider"
    ),
    stats: bool = typer.Option(
        False,
        "--stats",
        help="Show log file statistics"
    ),
):
    """Manage provider logs."""
    
    async def _logs():
        from .utils.log_manager import LogManager
        from .utils.log_parsers import LogParserFactory
        
        log_manager = LogManager()
        
        # Handle stats command
        if stats:
            await _show_log_stats(log_manager, provider)
            return
        
        # Handle clear command
        if clear:
            if provider.lower() == "all":
                if not typer.confirm("Are you sure you want to clear logs for ALL providers?"):
                    console.print("[yellow]Operation cancelled.[/yellow]")
                    return
            else:
                log_desc = f"{log_type} logs" if log_type != "stdout" else "logs"
                if not typer.confirm(f"Are you sure you want to clear {log_desc} for {provider}?"):
                    console.print("[yellow]Operation cancelled.[/yellow]")
                    return
            
            await _clear_logs(log_manager, provider, log_type)
            return
        
        # Handle follow command
        if follow:
            await _follow_logs(log_manager, provider, log_type, filter_term)
            return
        
        # Default: show logs
        await _show_logs(log_manager, provider, log_type, tail, filter_term)
    
    asyncio.run(_logs())


async def _show_logs(log_manager, provider: str, log_type: str, tail: int, filter_term: Optional[str]):
    """Show recent logs for a provider."""
    if provider.lower() == "all":
        # Show logs for all providers
        manager = ProviderManager()
        manager.initialize_providers()
        
        for provider_name in manager.providers.keys():
            await _show_provider_logs(log_manager, provider_name, log_type, tail, filter_term)
    else:
        await _show_provider_logs(log_manager, provider, log_type, tail, filter_term)


async def _show_provider_logs(log_manager, provider: str, log_type: str, tail: int, filter_term: Optional[str]):
    """Show logs for a specific provider."""
    console.print(f"\n[bold cyan]📋 {provider.title()} - {log_type} logs (last {tail} lines):[/bold cyan]")
    
    logs = await log_manager.tail_logs(provider, log_type, tail)
    
    if not logs:
        console.print(f"[dim]No logs found for {provider} ({log_type})[/dim]")
        return
    
    from .utils.log_parsers import LogParserFactory
    parser = LogParserFactory.get_parser(provider)
    
    for line in logs:
        if filter_term and filter_term.lower() not in line.lower():
            continue
        
        # Parse the line for better formatting
        try:
            event = parser.parse_line(line)
            if event:
                formatted_line = _format_log_event(event)
                console.print(formatted_line)
            else:
                console.print(line)
        except Exception:
            # Fallback to raw line if parsing fails
            console.print(line)


async def _follow_logs(log_manager, provider: str, log_type: str, filter_term: Optional[str]):
    """Follow logs in real-time."""
    # Check if provider exists
    manager = ProviderManager()
    manager.initialize_providers()
    
    if provider.lower() not in manager.providers:
        console.print(f"[red]❌ Unknown provider: {provider}[/red]")
        console.print(f"[yellow]Available providers: {', '.join(manager.providers.keys())}[/yellow]")
        return
    
    console.print(f"[cyan]📋 Following {provider} {log_type} logs... (Ctrl+C to stop)[/cyan]")
    console.print(f"[dim]Log file: {log_manager.get_log_file_path(provider, log_type)}[/dim]\n")
    
    try:
        from .utils.log_parsers import LogParserFactory
        parser = LogParserFactory.get_parser(provider)
        
        async for line in log_manager.follow_logs(provider, log_type):
            if filter_term and filter_term.lower() not in line.lower():
                continue
            
            # Parse the line for better formatting
            try:
                event = parser.parse_line(line)
                if event:
                    formatted_line = _format_log_event(event)
                    console.print(formatted_line)
                else:
                    console.print(line)
            except Exception:
                # Fallback to raw line if parsing fails
                console.print(line)
                    
    except KeyboardInterrupt:
        console.print("\n[yellow]📋 Log following stopped.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ Error following logs: {e}[/red]")


async def _clear_logs(log_manager, provider: str, log_type: str):
    """Clear logs for a provider."""
    if provider.lower() == "all":
        # Clear logs for all providers
        manager = ProviderManager()
        manager.initialize_providers()
        
        success_count = 0
        for provider_name in manager.providers.keys():
            if log_manager.clear_logs(provider_name, log_type if log_type != "stdout" else None):
                success_count += 1
                console.print(f"[green]✅ Cleared logs for {provider_name}[/green]")
            else:
                console.print(f"[red]❌ Failed to clear logs for {provider_name}[/red]")
        
        console.print(f"\n[cyan]📋 Cleared logs for {success_count} providers[/cyan]")
    else:
        if log_manager.clear_logs(provider, log_type if log_type != "stdout" else None):
            log_desc = f"{log_type} logs" if log_type != "stdout" else "logs"
            console.print(f"[green]✅ Cleared {log_desc} for {provider}[/green]")
        else:
            console.print(f"[red]❌ Failed to clear logs for {provider}[/red]")


async def _show_log_stats(log_manager, provider: Optional[str]):
    """Show log file statistics."""
    from rich.table import Table
    
    manager = ProviderManager()
    manager.initialize_providers()
    
    if provider and provider.lower() != "all":
        if provider.lower() not in manager.providers:
            console.print(f"[red]❌ Unknown provider: {provider}[/red]")
            return
        providers = [provider]
    else:
        providers = list(manager.providers.keys())
    
    table = Table(title="📊 Log File Statistics")
    table.add_column("Provider", style="cyan")
    table.add_column("Stdout", justify="right")
    table.add_column("Stderr", justify="right")
    table.add_column("Epic-LLM", justify="right")
    table.add_column("Total", justify="right", style="bold")
    table.add_column("Last Modified", style="dim")
    
    for provider_name in providers:
        stats = log_manager.get_log_stats(provider_name)
        
        def format_size(size_bytes):
            if size_bytes == 0:
                return "-"
            elif size_bytes < 1024:
                return f"{size_bytes}B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f}KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f}MB"
        
        last_modified = "-"
        if stats["last_modified"]:
            import datetime
            dt = datetime.datetime.fromtimestamp(stats["last_modified"])
            last_modified = dt.strftime("%Y-%m-%d %H:%M")
        
        table.add_row(
            provider_name,
            format_size(stats["stdout_size"]),
            format_size(stats["stderr_size"]),
            format_size(stats["epic_llm_size"]),
            format_size(stats["total_size"]),
            last_modified
        )
    
    console.print(table)


def _format_log_event(event) -> "Text":
    """Format a log event for rich display."""
    from rich.text import Text
    
    text = Text()
    
    # Add timestamp if available
    if event.timestamp:
        timestamp_str = event.timestamp.strftime("%H:%M:%S")
        text.append(f"[{timestamp_str}] ", style="dim")
    
    # Add event type indicator
    if event.event_type == "error":
        text.append("❌ ", style="red")
    elif event.event_type == "token_usage":
        text.append("🪙 ", style="yellow")
    elif event.event_type == "api_request":
        text.append("🌐 ", style="blue")
    elif event.event_type == "authentication":
        text.append("🔐 ", style="green")
    elif event.event_type == "oauth":
        text.append("🔑 ", style="green")
    else:
        text.append("📝 ", style="white")
    
    # Add the message
    if event.level == "ERROR":
        text.append(event.message, style="red")
    elif event.level == "WARNING":
        text.append(event.message, style="yellow")
    else:
        text.append(event.message)
    
    return text


if __name__ == "__main__":
    app()
