"""GitHub Copilot API provider implementation."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

import httpx

from ..managers.state import AuthStatus
from ..utils.auth_middleware import AuthMiddleware
from ..utils.copilot_auth_validator import CopilotAuthValidator
from ..utils.dependencies import Dependency, DependencyType
from ..utils.gateway import GatewayKeySupport
from ..utils.paths import get_provider_pkg_dir
from .base import BaseProvider


class CopilotProvider(BaseProvider):
    """GitHub Copilot API provider."""

    def __init__(self, install_dir: Optional[Path] = None):
        if install_dir is None:
            install_dir = get_provider_pkg_dir("copilot")
        # NOTE: Port 8081 instead of 8080 due to hardcoded Gemini OAuth callback conflict
        # geminicli2api hardcodes redirect_uri="http://localhost:8080" with no config option
        super().__init__(
            "copilot", 8081, install_dir
        )  # Changed from 8080 to avoid conflict with Gemini OAuth
        self.repo_url = "https://github.com/ericc-ch/copilot-api.git"  # Updated to use correct repository
        self._auth_validator = CopilotAuthValidator()
        self._monitoring_task = None
        self._middleware: Optional[AuthMiddleware] = None
        self._upstream_process = None

        # Gateway authentication capabilities - Copilot uses middleware for gateway auth
        self.gw_key_num_support = GatewayKeySupport.MW_MULTIPLE
        self._gateway_manager.support_level = self.gw_key_num_support

        # Initialize with cached status, will be updated by validation
        current_status = self.get_authentication_status()
        if (
            current_status == AuthStatus.NOT_REQUIRED
        ):  # Only set if completely uninitialized
            self.set_authentication_status(AuthStatus.REQUIRED)

    def get_dependencies(self) -> list[Dependency]:
        """Get dependencies for Copilot provider."""
        return [
            Dependency(
                name="node",
                type=DependencyType.EXECUTABLE,
                description="Node.js runtime for npx commands",
                executable="node",
                install_instructions="Install Node.js from https://nodejs.org/",
                required=True,
            ),
            Dependency(
                name="npm",
                type=DependencyType.EXECUTABLE,
                description="npm package manager with npx",
                executable="npm",
                install_instructions="npm comes with Node.js installation",
                required=True,
            ),
        ]

    def is_authentication_required(self) -> bool:
        """Copilot provider requires GitHub authentication."""
        return True

    async def validate_authentication(self) -> AuthStatus:
        """Validate GitHub Copilot authentication."""
        status = await self._auth_validator.validate_authentication()
        self.set_authentication_status(status)
        return status

    async def get_credential_info(self) -> dict:
        """Get information about GitHub Copilot credentials."""
        info = self._auth_validator.get_credential_info()
        if info is None:
            return {"status": "no_credentials"}

        # Add additional info
        info["github_username"] = await self._auth_validator.get_github_username()
        info[
            "copilot_subscription"
        ] = await self._auth_validator.check_copilot_subscription()
        return info

    async def handle_authentication_prompt(self) -> None:
        """Guide user through GitHub Copilot authentication setup."""
        print("\n" + "=" * 80)
        print("GITHUB COPILOT AUTHENTICATION REQUIRED")
        print("=" * 80)
        print("GitHub Copilot is not authenticated or not available.")
        print("")
        print("To authenticate GitHub Copilot:")
        print("  npx copilot-api@latest auth")
        print("")
        print("To check if you have a Copilot subscription:")
        print("  Visit: https://github.com/settings/copilot")
        print("")
        print("After authentication, restart the provider.")
        print("=" * 80)

    async def process_output_line(self, line: str) -> None:
        """Process output line to detect authentication issues."""
        line_lower = line.lower()

        # Check for authentication-related errors
        auth_keywords = [
            "authentication failed",
            "authentication error",
            "invalid token",
            "unauthorized",
            "auth error",
            "login required",
            "copilot subscription",
            "github token",
            "device code",
        ]

        if any(keyword in line_lower for keyword in auth_keywords):
            self.set_authentication_status(AuthStatus.FAILED)
            print(f"AUTH DEBUG: {line}")
            await self.handle_authentication_prompt()

    async def install(self) -> bool:
        """Install Copilot API."""
        # Check dependencies first
        if not await self.check_dependencies(auto_install=False):
            return False

        try:
            # For ericc-ch/copilot-api, we don't need to clone and install
            # It's available via npx, but we can test if it's accessible
            result = await asyncio.create_subprocess_exec(
                "npx",
                "copilot-api@latest",
                "--help",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await result.wait()

            if result.returncode == 0:
                # Create install directory to mark as "installed"
                self.install_dir.mkdir(parents=True, exist_ok=True)
                # Create a marker file
                (self.install_dir / ".copilot-api-ready").write_text(
                    "installed via npx"
                )
                return True
            else:
                return False

        except Exception:
            return False

    async def start(self, port: int) -> bool:
        """Start Copilot API server with middleware if gateway keys are configured."""
        try:
            # Validate GitHub authentication before starting
            auth_status = await self.validate_authentication()

            if auth_status == AuthStatus.REQUIRED:
                await self.handle_authentication_prompt()
                print(
                    "\n❌ Cannot start Copilot provider: GitHub authentication required."
                )
                print("   Run 'npx copilot-api@latest auth' and restart the provider.")
                return False
            elif auth_status == AuthStatus.FAILED:
                await self.handle_authentication_prompt()
                print(
                    "\n❌ Cannot start Copilot provider: GitHub authentication failed."
                )
                print("   Please re-authenticate and restart the provider.")
                return False

            print("✅ GitHub Copilot authentication validated successfully")

            # Get credential info for debugging
            cred_info = await self.get_credential_info()
            if cred_info.get("github_username"):
                print(f"   Authenticated as: {cred_info['github_username']}")

            # Check if gateway keys are configured to determine middleware mode
            gateway_keys = self.get_gateway_keys()
            use_middleware = len(gateway_keys) > 0

            if use_middleware:
                return await self._start_with_middleware(port, gateway_keys)
            else:
                return await self._start_direct(port)

        except Exception as e:
            print(f"Start exception: {e}")
            return False

    async def _start_direct(self, port: int) -> bool:
        """Start Copilot API directly without middleware."""
        import os

        env = os.environ.copy()
        env["PORT"] = str(port)

        # Use asyncio.create_subprocess_exec for proper log capture
        print(f"Starting Copilot API server on port {port}...")
        
        self.process = await asyncio.create_subprocess_exec(
            "npx", "copilot-api@latest", "start", "--port", str(port),
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        # Setup and start log capture
        self._setup_log_capture()
        self._log_event(f"Starting Copilot provider on port {port} (direct mode)")
        
        # Start capturing logs in background
        if self._log_capture:
            asyncio.create_task(self._start_log_capture())
        
        # Store process ID
        process_id = self.process.pid

        # Update state with process info
        self._update_process_state(process_id, port)

        # Wait for startup and check if process is still running
        await asyncio.sleep(5)
        
        try:
            import psutil
            process = psutil.Process(process_id)
            if not (process.is_running() and process.status() != psutil.STATUS_ZOMBIE):
                print(f"Process {process_id} failed to start or exited early")
                self._clear_process_state()
                return False
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            print(f"Process {process_id} not found after startup")
            self._clear_process_state()
            return False

        print(f"Debug: Copilot provider running successfully on port {port}")
        return True

    async def _start_with_middleware(self, public_port: int, gateway_keys: list[str]) -> bool:
        """Start Copilot API with authentication middleware."""
        from ..managers.port import PortManager
        
        # Allocate a random port for the upstream provider
        port_manager = PortManager()
        try:
            upstream_port = port_manager.get_available_port("copilot-upstream")
        except RuntimeError as e:
            print(f"❌ Failed to allocate upstream port for Copilot provider: {e}")
            return False

        try:
            # Start upstream Copilot API with proper detachment
            import os
            import subprocess

            env = os.environ.copy()
            env["PORT"] = str(upstream_port)

            # Use subprocess.Popen for proper process detachment  
            log_file = self.install_dir / "copilot_upstream.log"
            
            with open(log_file, "w") as f:
                upstream_proc = subprocess.Popen(
                    ["npx", "copilot-api@latest", "start", "--port", str(upstream_port)],
                    env=env,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
            
            # Store process ID
            upstream_process_id = upstream_proc.pid
            self._upstream_process = None  # Don't keep subprocess reference

            # Wait for upstream to start
            await asyncio.sleep(3)
            
            # Check if upstream process is still running
            try:
                import psutil
                process = psutil.Process(upstream_process_id)
                if not (process.is_running() and process.status() != psutil.STATUS_ZOMBIE):
                    print(f"Upstream process {upstream_process_id} failed to start or exited early")
                    return False
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                print(f"Upstream process {upstream_process_id} not found after startup")
                return False

            # Create and start authentication middleware as a detached process
            import json
            import tempfile
            import subprocess
            import sys
            from pathlib import Path
            
            # Create temporary config file for middleware daemon
            middleware_config = {
                "upstream_host": "127.0.0.1",
                "upstream_port": upstream_port,
                "public_port": public_port,
                "gateway_keys": gateway_keys
            }
            
            config_file = self.install_dir / "middleware_config.json"
            with open(config_file, "w") as f:
                json.dump(middleware_config, f, indent=2)
            
            # Start middleware daemon as detached process
            middleware_script = Path(__file__).parent.parent / "utils" / "middleware_daemon.py"
            log_file = self.install_dir / "middleware_daemon.log"
            
            with open(log_file, "w") as f:
                middleware_proc = subprocess.Popen(
                    [sys.executable, "-u", str(middleware_script), str(config_file)],  # -u for unbuffered output
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                    cwd=str(self.install_dir),
                    env=dict(os.environ, PYTHONUNBUFFERED="1")  # Ensure unbuffered output
                )
            
            # Store middleware process ID
            middleware_process_id = middleware_proc.pid
            self._middleware = None  # Don't keep subprocess reference
            
            # Wait for middleware to start
            await asyncio.sleep(2)

            # Update state with both process information
            self._update_middleware_process_state(
                middleware_process_id=middleware_process_id,
                middleware_port=public_port,
                upstream_process_id=upstream_process_id,
                upstream_port=upstream_port,
                gateway_keys=gateway_keys
            )

            # Don't start monitoring task since we don't have stdout pipes
            # self._monitoring_task = asyncio.create_task(self.monitor_upstream_output())

            print(f"✅ Copilot provider with middleware running on port {public_port}")
            print(f"   Upstream service: 127.0.0.1:{upstream_port}")
            print(f"   Gateway keys: {len(gateway_keys)} configured")
            return True

        except Exception as e:
            print(f"Failed to start middleware: {e}")
            # Clean up on failure
            try:
                import psutil
                process = psutil.Process(upstream_process_id)
                process.terminate()
                process.wait(timeout=5)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                pass
            return False

    async def monitor_upstream_output(self) -> None:
        """Monitor upstream process output for authentication issues."""
        # Since we no longer capture stdout, this method is disabled
        # Output is redirected to log files instead
        pass

    async def stop(self) -> bool:
        """Stop Copilot API server and middleware if running."""
        self._log_event("Stopping Copilot provider")
        
        # Stop log capture
        self._stop_log_capture()
        
        # Cancel monitoring task if running
        if self._monitoring_task and not self._monitoring_task.done():
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

        # Stop middleware if running (legacy in-process middleware)
        if self._middleware:
            try:
                await self._middleware.stop()
                self._middleware = None
            except Exception as e:
                print(f"Error stopping middleware: {e}")

        success = True
        
        # For middleware providers, stop both middleware and upstream processes
        if self.is_middleware_provider:
            # Stop middleware process
            middleware_pid = self.process_id
            if middleware_pid:
                try:
                    import psutil
                    process = psutil.Process(middleware_pid)
                    process.terminate()
                    process.wait(timeout=5)
                    print(f"Stopped middleware process {middleware_pid}")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired) as e:
                    print(f"Warning: Could not stop middleware process {middleware_pid}: {e}")
                    success = False
            
            # Stop upstream process
            upstream_pid = self.upstream_port  # This should be upstream_process_id
            state = self._state_manager.get_provider_state(self.name)
            upstream_pid = state.upstream_process_id
            if upstream_pid:
                try:
                    import psutil
                    process = psutil.Process(upstream_pid)
                    process.terminate()
                    process.wait(timeout=5)
                    print(f"Stopped upstream process {upstream_pid}")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired) as e:
                    print(f"Warning: Could not stop upstream process {upstream_pid}: {e}")
                    success = False
        else:
            # For direct mode, stop the single process
            if hasattr(self, "process") and self.process:
                try:
                    self.process.terminate()
                    await self.process.wait()
                    self.process = None
                except Exception:
                    pass

            # Try to stop process from state
            process_id = self.process_id
            if process_id:
                try:
                    import psutil
                    process = psutil.Process(process_id)
                    process.terminate()
                    process.wait(timeout=5)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    success = False
        
        # Clean up state regardless of success
        self._clear_process_state()
        
        # Clean up temporary files
        try:
            config_file = self.install_dir / "middleware_config.json"
            if config_file.exists():
                config_file.unlink()
        except Exception:
            pass
            
        return success

    async def health_check(self) -> bool:
        """Check if Copilot API is healthy."""
        port = self.current_port
        if not port:
            print("Health check failed: No port configured")
            return False

        try:
            import httpx
            # For direct providers, check the direct port
            # For middleware providers, check the public port
            async with httpx.AsyncClient(timeout=10.0) as client:
                if self.is_middleware_provider:
                    # For middleware, test the health endpoint which should be publicly accessible
                    print(f"Health check: Testing middleware on port {port} (public endpoint)")
                    try:
                        response = await client.get(f"http://localhost:{port}/")
                        print(f"Health check response: {response.status_code}")
                        # Healthy if middleware responds successfully to public endpoint
                        return response.status_code == 200
                    except Exception as e:
                        print(f"Health check failed: {e}")
                        return False
                else:
                    # Direct mode
                    print(f"Health check: Testing direct mode on port {port}")
                    try:
                        response = await client.get(f"http://localhost:{port}/")
                        print(f"Health check response: {response.status_code}")
                        return response.status_code == 200
                    except Exception as e:
                        print(f"Health check for direct mode failed: {e}")
                        return False
        except Exception as e:
            print(f"Health check failed with exception: {e}")
            return False

    def set_gateway_key(self, key: Optional[str]) -> None:
        """Set gateway API key and update middleware if running."""
        super().set_gateway_key(key)
        # Update state manager
        self._state_manager.update_provider_gateway_keys(self.name, self.get_gateway_keys())
        # Update middleware if running
        if self._middleware:
            self._middleware.update_gateway_keys(self.get_gateway_keys())

    def add_gateway_key(self, key: str) -> None:
        """Add a gateway API key and update middleware if running."""
        super().add_gateway_key(key)
        # Update state manager
        self._state_manager.update_provider_gateway_keys(self.name, self.get_gateway_keys())
        # Update middleware if running
        if self._middleware:
            self._middleware.update_gateway_keys(self.get_gateway_keys())

    def remove_gateway_key(self, key: str) -> bool:
        """Remove a gateway API key and update middleware if running."""
        result = super().remove_gateway_key(key)
        if result:
            # Update state manager
            self._state_manager.update_provider_gateway_keys(self.name, self.get_gateway_keys())
            # Update middleware if running
            if self._middleware:
                self._middleware.update_gateway_keys(self.get_gateway_keys())
        return result

    def get_gateway_key(self) -> Optional[str]:
        """Get primary gateway API key from state manager."""
        keys = self.get_gateway_keys()
        return keys[0] if keys else None

    def get_gateway_keys(self) -> list[str]:
        """Get gateway keys from state manager to ensure persistence."""
        stored_keys = self._state_manager.get_provider_gateway_keys(self.name)
        if stored_keys is not None:
            # Update local manager to match stored state
            self._gateway_manager._keys = stored_keys.copy()
            return stored_keys
        return super().get_gateway_keys()
