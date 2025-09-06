"""Claude Code API provider implementation."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

import httpx

from ..managers.state import AuthStatus
from ..utils.claude_auth_validator import ClaudeAuthValidator
from ..utils.dependencies import Dependency, DependencyType
from ..utils.gateway import GatewayKeySupport
from ..utils.paths import get_provider_pkg_dir
from .base import BaseProvider


class ClaudeProvider(BaseProvider):
    """Claude Code API provider."""

    def __init__(self, install_dir: Optional[Path] = None):
        if install_dir is None:
            install_dir = get_provider_pkg_dir("claude")
        super().__init__("claude", 8000, install_dir)
        self.repo_url = "https://github.com/codingworkflow/claude-code-api.git"
        self._auth_validator = ClaudeAuthValidator()
        self._monitoring_task = None
        self._gateway_config_file = self.install_dir / "gateway_config.json"

        # Gateway authentication capabilities - Claude supports multiple keys
        self.gw_key_num_support = GatewayKeySupport.MULTIPLE
        self._gateway_manager.support_level = self.gw_key_num_support

        # Load gateway configuration on initialization
        self._load_gateway_config()

        # Initialize with cached status, will be updated by validation
        current_status = self.get_authentication_status()
        if (
            current_status == AuthStatus.NOT_REQUIRED
        ):  # Only set if completely uninitialized
            self.set_authentication_status(AuthStatus.REQUIRED)

    def get_dependencies(self) -> list[Dependency]:
        """Get dependencies for Claude provider."""
        return [
            Dependency(
                name="node",
                type=DependencyType.EXECUTABLE,
                description="Node.js runtime for claude-code package",
                executable="node",
                install_instructions="Install Node.js from https://nodejs.org/",
                required=True,
            ),
            Dependency(
                name="npm",
                type=DependencyType.EXECUTABLE,
                description="npm package manager",
                executable="npm",
                install_instructions="npm comes with Node.js installation",
                required=True,
            ),
            Dependency(
                name="claude",
                type=DependencyType.CLI_COMMAND,
                description="Anthropic Claude CLI tool",
                check_command=["claude", "--version"],
                install_instructions="Install Claude CLI from Anthropic",
                required=True,
            ),
            Dependency(
                name="claude_code",
                type=DependencyType.NPM_GLOBAL,
                description="Anthropic Claude Code CLI tool",
                npm_package="@anthropic-ai/claude-code",
                install_command="npm install -g @anthropic-ai/claude-code",
                install_instructions="Install globally with npm",
                auto_install=True,
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

        # Use plaintext keys for local storage (NOT hashes)
        keys = self._gateway_manager.get_plaintext_keys()
        config = {"gateway_api_keys": keys, "auth_enabled": len(keys) > 0}

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

                # Handle both old format (single key) and new format (multiple keys)
                if "gateway_api_key" in config:
                    # Old format - migrate to new format
                    old_key = config.get("gateway_api_key")
                    if old_key:
                        self.set_gateway_key(old_key)
                elif "gateway_api_keys" in config:
                    # New format - keys are stored as plaintext in local config
                    keys = config.get("gateway_api_keys", [])
                    for key in keys:
                        if key:  # Skip empty keys
                            self.add_gateway_key(key)
        except Exception:
            # If config file is corrupted or missing, start with no gateway keys
            pass

    def is_authentication_required(self) -> bool:
        """Claude provider requires CLI authentication."""
        return True

    async def validate_authentication(self) -> AuthStatus:
        """Validate Claude CLI authentication."""
        status = await self._auth_validator.validate_authentication()
        self.set_authentication_status(status)
        return status

    async def get_credential_info(self) -> dict:
        """Get information about Claude CLI credentials."""
        info = self._auth_validator.get_credential_info()
        if info is None:
            return {"status": "no_credentials"}

        # Add additional info
        info["claude_version"] = await self._auth_validator.get_claude_version()
        info["claude_username"] = await self._auth_validator.get_claude_username()
        return info

    async def handle_authentication_prompt(self) -> None:
        """Guide user through Claude CLI authentication setup."""
        print("\n" + "=" * 80)
        print("CLAUDE CLI AUTHENTICATION REQUIRED")
        print("=" * 80)
        print("Claude CLI is not authenticated or not installed.")
        print("")
        print("To install Claude CLI:")
        print("  npm install -g @anthropic-ai/claude-code")
        print("")
        print("To authenticate Claude CLI:")
        print("  claude auth login")
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
            "invalid credentials",
            "permission denied",
            "unauthorized",
            "auth error",
            "login required",
        ]

        # Check for port binding errors
        port_keywords = [
            "address already in use",
            "bind on address",
            "errno 98",
        ]

        if any(keyword in line_lower for keyword in auth_keywords):
            self.set_authentication_status(AuthStatus.FAILED)
            print(f"AUTH DEBUG: {line}")
            await self.handle_authentication_prompt()
        elif any(keyword in line_lower for keyword in port_keywords):
            print(f"PORT ERROR: {line}")

    async def install(self) -> bool:
        """Install Claude Code API using the proper setup process."""
        # Check dependencies first
        if not await self.check_dependencies(auto_install=True):
            return False

        try:
            # Create parent directory
            self.install_dir.parent.mkdir(parents=True, exist_ok=True)

            # Clone repository if not already exists
            if not self.install_dir.exists():
                print("Cloning claude-code-api repository...")
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

            # Create virtual environment in the repo directory
            venv_dir = self.install_dir / ".venv"
            if not venv_dir.exists():
                print("Creating virtual environment...")
                result = await asyncio.create_subprocess_exec(
                    "python",
                    "-m",
                    "venv",
                    ".venv",
                    cwd=self.install_dir,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await result.wait()

                if result.returncode != 0:
                    stderr = await result.stderr.read()
                    print(f"Virtual env creation failed: {stderr.decode()}")
                    return False

            # Install dependencies using make install with activated virtual environment
            print("Installing dependencies with make install...")

            # Set up environment with activated virtual environment
            import os

            env = os.environ.copy()
            env["VIRTUAL_ENV"] = str(venv_dir)
            env["PATH"] = f"{venv_dir / 'bin'}:{env.get('PATH', '')}"

            result = await asyncio.create_subprocess_exec(
                "make",
                "install",
                cwd=self.install_dir,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await result.wait()

            if result.returncode != 0:
                stderr = await result.stderr.read()
                stdout = await result.stdout.read()
                print("Make install failed:")
                print(f"STDOUT: {stdout.decode()}")
                print(f"STDERR: {stderr.decode()}")
                return False

            print("✅ Claude Code API installed successfully")
            return True

        except Exception as e:
            print(f"Install exception: {e}")
            return False

    async def start(self, port: int) -> bool:
        """Start Claude Code API server."""
        try:
            # Validate Claude CLI authentication before starting
            auth_status = await self.validate_authentication()

            if auth_status == AuthStatus.REQUIRED:
                await self.handle_authentication_prompt()
                print(
                    "\n❌ Cannot start Claude provider: "
                    "Claude CLI authentication required."
                )
                print("   Run 'claude auth login' and restart the provider.")
                return False
            elif auth_status == AuthStatus.FAILED:
                await self.handle_authentication_prompt()
                print(
                    "\n❌ Cannot start Claude provider: "
                    "Claude CLI authentication failed."
                )
                print("   Please re-authenticate and restart the provider.")
                return False

            print("✅ Claude CLI authentication validated successfully")

            # Get credential info for debugging
            cred_info = await self.get_credential_info()
            if cred_info.get("claude_username"):
                print(f"   Authenticated as: {cred_info['claude_username']}")
            if cred_info.get("claude_version"):
                print(f"   Claude CLI version: {cred_info['claude_version']}")

            # Set up environment with activated virtual environment and Claude CLI path
            import os
            import shutil

            env = os.environ.copy()

            # Set up virtual environment
            venv_dir = self.install_dir / ".venv"
            env["VIRTUAL_ENV"] = str(venv_dir)
            env["PATH"] = f"{venv_dir / 'bin'}:{env.get('PATH', '')}"

            # Find claude binary and add its directory to PATH
            claude_path = shutil.which("claude")
            if claude_path:
                claude_dir = str(Path(claude_path).parent)
                current_path = env.get("PATH", "")
                if claude_dir not in current_path:
                    env["PATH"] = f"{claude_dir}:{current_path}"
            else:
                print(
                    "Warning: Claude CLI not found in PATH - "
                    "the server might fail to start"
                )

            # Use the exact same command as "make start" but with configurable port
            print(f"Starting Claude Code API server on port {port}...")

            # Configure gateway authentication if API keys are set
            if self.has_gateway_keys():
                env["REQUIRE_AUTH"] = "true"
                # Use plaintext keys for the Claude server (not hashes)
                plaintext_keys = self._gateway_manager.get_plaintext_keys()
                env["API_KEYS"] = ",".join(plaintext_keys)
                print(
                    f"🔐 Gateway authentication enabled with "
                    f"{len(plaintext_keys)} key(s)"
                )
            else:
                env["REQUIRE_AUTH"] = "false"
                print("🔓 Gateway authentication disabled")

            # Copy the exact uvicorn command from Makefile but with dynamic port
            # This ensures we use the same working configuration as "make start"
            self.process = await asyncio.create_subprocess_exec(
                "uvicorn",
                "claude_code_api.main:app",
                "--host",
                "0.0.0.0",
                "--port",
                str(port),
                "--reload",
                "--reload-exclude=*.db*",
                "--reload-exclude=*.log",
                cwd=self.install_dir,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # Setup and start log capture
            self._setup_log_capture()
            self._log_event(f"Starting Claude provider on port {port}")
            
            # Start capturing logs in background
            if self._log_capture:
                asyncio.create_task(self._start_log_capture())

            # Update state with process info
            self._update_process_state(self.process.pid, port)

            # Start monitoring output in background for auth issues
            self._monitoring_task = asyncio.create_task(self.monitor_process_output())

            # Wait for the API to start and become healthy
            print("Waiting for Claude Code API to become ready...")
            max_attempts = 12  # 12 attempts with 2.5 second intervals = 30 seconds max
            attempt = 1

            # Give the process a moment to start and potentially fail immediately
            await asyncio.sleep(1.0)

            while attempt <= max_attempts:
                # Check if the main process has exited
                if self.process.returncode is not None:
                    stdout_data, stderr_data = await self.process.communicate()
                    stdout_output = stdout_data.decode() if stdout_data else "No stdout"
                    stderr_output = stderr_data.decode() if stderr_data else "No stderr"

                    print(
                        f"❌ Process exited with return code: {self.process.returncode}"
                    )
                    if stdout_output.strip():
                        print(f"STDOUT: {stdout_output}")
                    if stderr_output.strip():
                        print(f"STDERR: {stderr_output}")

                    # Check for specific error patterns
                    if (
                        "address already in use" in stderr_output.lower()
                        or "address already in use" in stdout_output.lower()
                    ):
                        print(f"❌ Port {port} is already in use by another process")

                    self._clear_process_state()
                    return False

                # Try health check
                try:
                    if await self.health_check():
                        print(f"✅ Claude Code API is healthy and ready on port {port}")
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
                "❌ Health check timeout - "
                "Claude Code API failed to start within 30 seconds"
            )

            # Check if process exited during our attempts
            if self.process.returncode is not None:
                stdout_data, stderr_data = await self.process.communicate()
                stdout_output = stdout_data.decode() if stdout_data else "No stdout"
                stderr_output = stderr_data.decode() if stderr_data else "No stderr"

                print(
                    "Process exited during health checks with return code: "
                    f"{self.process.returncode}"
                )
                if stdout_output.strip():
                    print(f"STDOUT: {stdout_output}")
                if stderr_output.strip():
                    print(f"STDERR: {stderr_output}")
            else:
                print("Process is still running but not responding to health checks")

            await self.stop()
            return False

        except Exception as e:
            print(f"Start exception: {e}")
            return False

    async def stop(self) -> bool:
        """Stop Claude Code API server."""
        self._log_event("Stopping Claude provider")
        
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
                self._log_event("Claude provider stopped successfully")
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
            self._log_event("Claude provider stopped via PID")
            return True
        except Exception as e:
            # Process might already be dead, clear state anyway
            self._clear_process_state()
            self._log_event(f"Process cleanup completed: {e}", "WARNING")
            return False

    async def health_check(self) -> bool:
        """Check if Claude API is healthy by querying available models."""
        port = self.current_port
        if not port:
            return False

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try multiple approaches to health checking
                primary_key = self._gateway_manager.get_primary_plaintext_key()
                
                # Approach 1: If no gateway key is set, try without auth
                if not primary_key:
                    response = await client.get(
                        f"http://localhost:{port}/v1/models"
                    )
                    if response.status_code == 200:
                        # Parse and validate response
                        data = response.json()
                        if data.get("data") and isinstance(data["data"], list):
                            models = [model.get("id", "") for model in data["data"]]
                            claude_models = [m for m in models if "claude" in m.lower()]
                            if claude_models:
                                print(
                                    f"Health check passed: Found {len(claude_models)} "
                                    f"Claude model(s): {claude_models}"
                                )
                                return True
                    return False
                
                # Approach 2: If gateway key is set, try with auth
                headers = {"Authorization": f"Bearer {primary_key}"}
                response = await client.get(
                    f"http://localhost:{port}/v1/models", headers=headers
                )
                
                if response.status_code == 200:
                    # Parse and validate response
                    data = response.json()
                    if data.get("data") and isinstance(data["data"], list):
                        models = [model.get("id", "") for model in data["data"]]
                        claude_models = [m for m in models if "claude" in m.lower()]
                        if claude_models:
                            print(
                                f"Health check passed: Found {len(claude_models)} "
                                f"Claude model(s): {claude_models}"
                            )
                            return True
                    return False
                
                # Approach 3: If auth failed, try without auth as fallback
                if response.status_code == 401:
                    print("Health check: Auth failed, trying without auth...")
                    try:
                        response_no_auth = await client.get(
                            f"http://localhost:{port}/v1/models"
                        )
                        if response_no_auth.status_code == 200:
                            print("Warning: Server running but auth may be misconfigured")
                            # For now, consider this a success to avoid startup failure
                            data = response_no_auth.json()
                            if data.get("data") and isinstance(data["data"], list):
                                models = [model.get("id", "") for model in data["data"]]
                                claude_models = [m for m in models if "claude" in m.lower()]
                                if claude_models:
                                    print("Server is healthy but gateway auth needs verification")
                                    return True
                    except Exception:
                        pass
                
                print(f"Health check failed: HTTP {response.status_code}")
                if response.status_code == 401:
                    print("Authentication error - check gateway key configuration")
                return False

                # Parse the response to verify it contains models
                data = response.json()
                if not data.get("data") or not isinstance(data["data"], list):
                    print("Health check failed: No models data in response")
                    return False

                # Check if we have Claude models available
                models = [model.get("id", "") for model in data["data"]]
                claude_models = [m for m in models if "claude" in m.lower()]

                if not claude_models:
                    print(
                        "Health check failed: No Claude models found. "
                        f"Available: {models}"
                    )
                    return False

                print(
                    f"Health check passed: Found {len(claude_models)} Claude model(s): "
                    f"{claude_models}"
                )
                return True

        except Exception as e:
            print(f"Health check failed with exception: {e}")
            return False
