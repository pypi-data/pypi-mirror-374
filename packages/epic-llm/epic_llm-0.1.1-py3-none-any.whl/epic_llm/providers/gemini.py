"""Gemini CLI to API provider implementation."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

import httpx

from ..managers.state import AuthStatus
from ..utils.auth_validator import GeminiAuthValidator
from ..utils.dependencies import Dependency, DependencyType
from ..utils.gateway import GatewayKeySupport
from ..utils.paths import get_provider_pkg_dir
from .base import BaseProvider


class GeminiProvider(BaseProvider):
    """Gemini CLI to API provider."""

    def __init__(self, install_dir: Optional[Path] = None):
        if install_dir is None:
            install_dir = get_provider_pkg_dir("gemini")
        super().__init__("gemini", 8888, install_dir)
        self.repo_url = "https://github.com/gzzhongqi/geminicli2api.git"
        self._monitoring_task = None
        self._auth_validator = GeminiAuthValidator(install_dir)
        self._gateway_config_file = install_dir / "gateway_config.json"

        # Gateway authentication capabilities - Gemini supports single key
        self.gw_key_num_support = GatewayKeySupport.SINGLE
        self._gateway_manager.support_level = self.gw_key_num_support

        # Load gateway configuration
        self._load_gateway_config()

        # Initialize with cached status, but don't override if already authenticated
        current_status = self.get_authentication_status()
        if (
            current_status == AuthStatus.NOT_REQUIRED
        ):  # Only set if completely uninitialized
            self.set_authentication_status(AuthStatus.REQUIRED)

    def get_dependencies(self) -> list[Dependency]:
        """Get dependencies for Gemini provider."""
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
                name="npx",
                type=DependencyType.EXECUTABLE,
                description="npx package runner",
                executable="npx",
                install_instructions="npx comes with Node.js installation",
                required=True,
            ),
            Dependency(
                name="gemini",
                type=DependencyType.CLI_COMMAND,
                description="Google Gemini CLI tool",
                check_command=["gemini", "--help"],
                install_instructions="Install via: npx https://github.com/google-gemini/gemini-cli",
                required=True,
            ),
            Dependency(
                name="python",
                type=DependencyType.PYTHON_VERSION,
                description="Python 3.8+ for API server",
                min_python_version=(3, 8),
                install_instructions="Install Python 3.8+ from https://python.org/",
                required=True,
            ),
        ]

    def set_gateway_key(self, api_key: str = None):
        """Set gateway API key. None to disable authentication."""
        super().set_gateway_key(api_key)
        self._save_gateway_config()

    def get_gateway_key(self) -> str:
        """Get current gateway API key in plaintext."""
        return self._gateway_manager.get_primary_plaintext_key()

    def _save_gateway_config(self):
        """Save gateway configuration to file."""
        import json

        # Ensure the directory exists
        self.install_dir.mkdir(parents=True, exist_ok=True)

        # Use plaintext key for local storage (NOT hash)
        key = self._gateway_manager.get_primary_plaintext_key()
        config = {"gateway_api_key": key, "auth_enabled": key is not None}

        try:
            with open(self._gateway_config_file, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save gateway config: {e}")

    def _load_gateway_config(self):
        """Load gateway configuration from file."""
        import json

        try:
            if self._gateway_config_file.exists():
                with open(self._gateway_config_file, "r") as f:
                    config = json.load(f)
                # Key is stored as plaintext in local config
                key = config.get("gateway_api_key")
                if key:
                    self.set_gateway_key(key)
        except Exception:
            # If config file is corrupted or missing, start with no gateway key
            pass

    async def install(self) -> bool:
        """Install Gemini CLI to API."""
        # Check dependencies first
        if not await self.check_dependencies(auto_install=False):
            return False

        try:
            # Create parent directory
            self.install_dir.parent.mkdir(parents=True, exist_ok=True)

            # Clone repository
            result = await asyncio.create_subprocess_exec(
                "git",
                "clone",
                self.repo_url,
                str(self.install_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await result.wait()

            if result.returncode != 0:
                stderr = await result.stderr.read()
                print(f"Git clone failed: {stderr.decode()}")
                return False

            # Create virtual environment
            venv_dir = self.install_dir / "venv"
            if not venv_dir.exists():
                result = await asyncio.create_subprocess_exec(
                    "python",
                    "-m",
                    "venv",
                    str(venv_dir),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await result.wait()

                if result.returncode != 0:
                    stderr = await result.stderr.read()
                    print(f"Virtual env creation failed: {stderr.decode()}")
                    return False

            # Install Python dependencies in virtual environment
            pip_path = venv_dir / "bin" / "pip"
            result = await asyncio.create_subprocess_exec(
                str(pip_path),
                "install",
                "-r",
                "requirements.txt",
                cwd=self.install_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await result.wait()

            return result.returncode == 0

        except Exception as e:
            print(f"Install exception: {e}")
            return False

    def is_authentication_required(self) -> bool:
        """Gemini provider requires authentication."""
        return True

    async def validate_authentication(self) -> AuthStatus:
        """Validate current OAuth credentials."""
        status = await self._auth_validator.validate_credentials()
        self.set_authentication_status(status)
        return status

    async def get_credential_info(self) -> dict:
        """Get information about current credentials."""
        info = self._auth_validator.get_credential_info()
        if info is None:
            return {"status": "no_credentials"}
        return info

    async def process_output_line(self, line: str) -> None:
        """Process output line to detect authentication requirements."""
        line_lower = line.lower()

        # Check for authentication URL in the output
        if "please open this url in your browser to log in:" in line_lower:
            print("\n🔗 Authentication URL will be shown next...")
            return

        # Check for the actual authentication URL
        if line.startswith("https://accounts.google.com/o/oauth2/auth"):
            print("\n🔗 AUTHENTICATION URL DETECTED:")
            print(f"   {line}")
            print("   Open this URL in your browser to authenticate.\n")
            return

        if (
            "authentication required" in line_lower
            or "authentication needed" in line_lower
        ):
            self.set_authentication_status(AuthStatus.REQUIRED)
            await self.handle_authentication_prompt()
        elif "authenticated" in line_lower and "successfully" in line_lower:
            self.set_authentication_status(AuthStatus.AUTHENTICATED)
        elif "authentication failed" in line_lower or "auth error" in line_lower:
            self.set_authentication_status(AuthStatus.FAILED)

        # Print all output for debugging during auth setup
        if any(
            keyword in line_lower
            for keyword in ["auth", "credential", "oauth", "login", "browser", "url"]
        ):
            print(f"AUTH DEBUG: {line}")

    async def handle_authentication_prompt(self) -> None:
        """Guide user through OAuth setup when authentication is required."""
        print("\n" + "=" * 80)
        print("GEMINI PROVIDER AUTHENTICATION REQUIRED")
        print("=" * 80)
        print("The Gemini provider requires Google OAuth authentication.")
        print("We'll start the authentication process now...")
        print("=" * 80)

        try:
            # Try to start the OAuth flow by importing and calling the auth function
            # We need to run this in the geminicli2api environment
            import subprocess

            # Use python from virtual environment
            venv_dir = self.install_dir / "venv"
            python_path = venv_dir / "bin" / "python"

            if not python_path.exists():
                print(
                    "❌ Virtual environment not found. "
                    "Please install the provider first."
                )
                print("   Run: epic-llm install gemini")
                return

            print("🔐 Starting OAuth authentication flow...")
            print("📝 This will open a browser window for Google authentication.")
            print(
                "🔗 If the browser doesn't open automatically, "
                "you'll see a URL to copy."
            )
            print(
                "\n⚠️  IMPORTANT: Do not close this terminal "
                "until authentication is complete!\n"
            )

            # Create a simple Python script to run the OAuth flow
            auth_script = """
import sys
import os
sys.path.insert(0, '.')
from src.auth import get_credentials

try:
    print("Initiating Google OAuth flow...")
    credentials = get_credentials(allow_oauth_flow=True)
    if credentials:
        print("✅ Authentication successful!")
        print("You can now start the Gemini provider.")
        sys.exit(0)
    else:
        print("❌ Authentication failed.")
        sys.exit(1)
except KeyboardInterrupt:
    print("\\n❌ Authentication cancelled by user.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Authentication error: {e}")
    sys.exit(1)
"""

            # Write the script to a temporary file
            script_file = self.install_dir / "temp_auth.py"
            with open(script_file, "w") as f:
                f.write(auth_script)

            try:
                # Run the authentication script
                result = subprocess.run(
                    [str(python_path), str(script_file)],
                    cwd=self.install_dir,
                    timeout=300,  # 5 minute timeout
                    text=True,
                    capture_output=False,  # Allow real-time output
                )

                if result.returncode == 0:
                    print("\n🎉 Authentication completed successfully!")
                    print("You can now restart the provider.")
                    # Update our authentication status
                    self.set_authentication_status(AuthStatus.AUTHENTICATED)
                else:
                    print("\n❌ Authentication failed.")
                    self.set_authentication_status(AuthStatus.FAILED)

            finally:
                # Clean up the temporary script
                if script_file.exists():
                    script_file.unlink()

        except subprocess.TimeoutExpired:
            print("\n⏰ Authentication timed out after 5 minutes.")
            print("Please try again with: epic-llm start gemini")
        except KeyboardInterrupt:
            print("\n❌ Authentication cancelled by user.")
        except Exception as e:
            print(f"\n❌ Error during authentication setup: {e}")
            print("Please ensure the Gemini provider is properly installed.")
            print("Run: epic-llm install gemini")

    async def start(self, port: int) -> bool:
        try:
            # Validate authentication before starting
            auth_status = await self.validate_authentication()

            if auth_status == AuthStatus.REQUIRED:
                await self.handle_authentication_prompt()

                # Revalidate authentication after the OAuth flow
                print("\n🔄 Validating authentication...")
                auth_status = await self.validate_authentication()

                if auth_status != AuthStatus.AUTHENTICATED:
                    print(
                        "\n❌ Cannot start Gemini provider: "
                        "Authentication validation failed."
                    )
                    print("   Please ensure you completed the OAuth flow successfully.")
                    return False
                else:
                    print("✅ Authentication validated successfully after OAuth flow")

            elif auth_status == AuthStatus.FAILED:
                await self.handle_authentication_prompt()

                # Revalidate authentication after the OAuth flow
                print("\n🔄 Validating authentication...")
                auth_status = await self.validate_authentication()

                if auth_status != AuthStatus.AUTHENTICATED:
                    print(
                        "\n❌ Cannot start Gemini provider: "
                        "Re-authentication validation failed."
                    )
                    print("   Please ensure you completed the OAuth flow successfully.")
                    return False
                else:
                    print(
                        "✅ Authentication validated successfully "
                        "after re-authentication"
                    )

            if auth_status == AuthStatus.AUTHENTICATED:
                print("✅ Authentication validated successfully")

            # Get credential info for debugging
            cred_info = await self.get_credential_info()
            if cred_info.get("is_expired"):
                print("⚠️  Access token is expired but will be refreshed automatically")

            # Use python from virtual environment
            venv_dir = self.install_dir / "venv"
            python_path = venv_dir / "bin" / "python"

            # Set environment variables for the process
            import os

            env = os.environ.copy()
            env["PORT"] = str(port)
            env["HOST"] = "0.0.0.0"
            # DON'T set PYTHONPATH to the install directory - this interferes with venv
            # The venv's site-packages should be used instead

            # Configure gateway authentication
            gateway_key = self.get_gateway_key()
            if gateway_key:
                env["GEMINI_AUTH_PASSWORD"] = gateway_key
                print("🔐 Gateway authentication enabled")
            else:
                # Use default password for backward compatibility
                auth_password = "llm-api-gw-auth"
                env["GEMINI_AUTH_PASSWORD"] = auth_password
                print("🔓 Gateway authentication using default password")

            # Set proper virtual environment variables
            env["VIRTUAL_ENV"] = str(venv_dir)
            env["PATH"] = f"{venv_dir / 'bin'}:{env.get('PATH', '')}"

            # Store the auth password for health checks
            self._auth_password = gateway_key or "llm-api-gw-auth"

            # Set proper virtual environment variables
            venv_dir = self.install_dir / "venv"
            python_path = venv_dir / "bin" / "python"
            env["VIRTUAL_ENV"] = str(venv_dir)
            env["PATH"] = f"{venv_dir / 'bin'}:{env.get('PATH', '')}"
            # Remove any conflicting PYTHONHOME
            env.pop("PYTHONHOME", None)

            # Use asyncio.create_subprocess_exec for proper log capture
            print(f"Starting Gemini API server on port {port}...")
            
            self.process = await asyncio.create_subprocess_exec(
                str(python_path),
                "run.py",
                cwd=self.install_dir,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # Setup and start log capture
            self._setup_log_capture()
            self._log_event(f"Starting Gemini provider on port {port}")
            
            # Start capturing logs in background
            if self._log_capture:
                asyncio.create_task(self._start_log_capture())

            # Store the process ID
            process_id = self.process.pid

            # Update state with process info
            self._update_process_state(process_id, port)

            # Re-enable monitoring task for output processing
            # (now that process is stable)
            # Don't monitor since we don't have stdout/stderr pipes
            # self._monitoring_task = asyncio.create_task(self.monitor_process_output())

            # Wait for the API to start and become healthy
            print("Waiting for Gemini API to become ready...")
            max_attempts = 12  # 12 attempts with 2.5 second intervals = 30 seconds max
            attempt = 1

            # Give the process a moment to start and potentially fail immediately
            await asyncio.sleep(1.0)

            while attempt <= max_attempts:
                # Check if the process is still running via PID
                try:
                    import psutil

                    process = psutil.Process(process_id)
                    if not (
                        process.is_running()
                        and process.status() != psutil.STATUS_ZOMBIE
                    ):
                        print(f"❌ Process {process_id} is no longer running")
                        self._clear_process_state()
                        return False
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    print(f"❌ Process {process_id} not found")
                    self._clear_process_state()
                    return False

                # Try health check
                try:
                    if await self.health_check():
                        print(f"✅ Gemini API is healthy and ready on port {port}")
                        return True
                except Exception:
                    # Health check failed, but that's expected during startup
                    pass

                print(
                    f"Health check {attempt}/{max_attempts} - "
                    "API not ready yet, waiting..."
                )
                await asyncio.sleep(2.5)
                attempt += 1

            # If we get here, all health checks failed
            print(
                "❌ Health check timeout - Gemini API failed to start within 30 seconds"
            )

            # Check final process status
            try:
                import psutil

                process = psutil.Process(process_id)
                if process.is_running():
                    print(
                        "Process is still running but not responding to health checks"
                    )
                else:
                    print(f"Process exited with status: {process.status()}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                print("Process not found")

            await self.stop()
            return False

        except Exception as e:
            print(f"Start exception: {e}")
            return False

    async def monitor_process_output(self) -> None:
        """Monitor process output for authentication requirements and errors."""
        if not self.process:
            return

        try:
            while True:
                # Check if process has exited first
                if self.process.returncode is not None:
                    print(
                        f"[GEMINI] Process exited with code: {self.process.returncode}"
                    )
                    # Read any remaining output
                    if self.process.stdout:
                        remaining_stdout = await self.process.stdout.read()
                        if remaining_stdout:
                            print(f"[GEMINI FINAL STDOUT] {remaining_stdout.decode()}")
                    if self.process.stderr:
                        remaining_stderr = await self.process.stderr.read()
                        if remaining_stderr:
                            print(f"[GEMINI FINAL STDERR] {remaining_stderr.decode()}")
                    self._clear_process_state()
                    break

                # Read from both stdout and stderr with timeout
                try:
                    stdout_line = None
                    stderr_line = None

                    if self.process.stdout:
                        stdout_line = await asyncio.wait_for(
                            self.process.stdout.readline(), timeout=1.0
                        )
                    if self.process.stderr:
                        stderr_line = await asyncio.wait_for(
                            self.process.stderr.readline(), timeout=1.0
                        )

                    if stdout_line:
                        output = stdout_line.decode().strip()
                        if output:
                            print(f"[GEMINI STDOUT] {output}")
                            await self.process_output_line(output)

                    if stderr_line:
                        error = stderr_line.decode().strip()
                        if error:
                            print(f"[GEMINI STDERR] {error}")

                except asyncio.TimeoutError:
                    # No output received, continue monitoring
                    continue

        except Exception as e:
            print(f"Error monitoring output for {self.name}: {e}")

    async def stop(self) -> bool:
        """Stop Gemini API server."""
        self._log_event("Stopping Gemini provider")
        
        # Stop log capture
        self._stop_log_capture()
        
        # Cancel monitoring task if running
        if self._monitoring_task and not self._monitoring_task.done():
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

        # Try to stop local process first
        if hasattr(self, "process") and self.process:
            try:
                self.process.terminate()
                await self.process.wait()
                self.process = None
                self._clear_process_state()
                self._log_event("Gemini provider stopped successfully")
                return True
            except Exception as e:
                self._log_event(f"Error stopping process: {e}", "ERROR")

        # Try to stop process from state
        process_id = self.process_id
        if not process_id:
            return True

        try:
            import psutil

            process = psutil.Process(process_id)
            process.terminate()
            process.wait(timeout=10)
            self._clear_process_state()
            self._log_event("Gemini provider stopped via PID")
            return True
        except Exception as e:
            # Process might already be dead, clear state anyway
            self._clear_process_state()
            self._log_event(f"Process cleanup completed: {e}", "WARNING")
            return False

    async def health_check(self) -> bool:
        """Check if Gemini API is healthy by querying available models."""
        port = self.current_port
        if not port:
            return False

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # First check the basic health endpoint
                try:
                    health_response = await client.get(
                        f"http://localhost:{port}/health"
                    )
                    if health_response.status_code != 200:
                        print(
                            f"Health endpoint failed: HTTP "
                            f"{health_response.status_code}"
                        )
                        return False
                except Exception as e:
                    print(f"Health endpoint failed: {e}")
                    return False

                # Now check the models endpoint to verify Gemini models are available
                auth_password = getattr(self, "_auth_password", "llm-api-gw-auth")
                try:
                    response = await client.get(
                        f"http://localhost:{port}/v1/models",
                        headers={"Authorization": f"Bearer {auth_password}"},
                    )

                    if response.status_code != 200:
                        print(f"Models endpoint failed: HTTP {response.status_code}")
                        return False

                    # Parse the response to verify it contains models
                    data = response.json()
                    if not data.get("data") or not isinstance(data["data"], list):
                        print("Models endpoint returned no model data")
                        return False

                    # Check if we have Gemini models available
                    models = [model.get("id", "") for model in data["data"]]
                    gemini_models = [m for m in models if "gemini" in m.lower()]

                    if not gemini_models:
                        print(f"No Gemini models found. Available models: {models[:5]}")
                        return False

                    print(
                        f"Health check passed: Found {len(gemini_models)} "
                        f"Gemini model(s): {gemini_models[:5]}"
                    )
                    return True

                except Exception as e:
                    print(f"Models endpoint failed: {e}")
                    return False
        except Exception as e:
            print(f"Health check failed with exception: {e}")
            return False
