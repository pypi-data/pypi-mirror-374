"""Base provider interface for LLM API gateways."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..managers.state import AuthStatus
    from ..utils.dependencies import Dependency

from ..utils.gateway import GatewayKeyManager, GatewayKeySupport


class BaseProvider(ABC):
    """Base class for all LLM API providers."""

    def __init__(self, name: str, default_port: int, install_dir: Path):
        from ..managers.state import StateManager

        self.name = name
        self.default_port = default_port
        self.install_dir = install_dir
        self.process = None
        self._state_manager = StateManager()

        # Gateway key support - default to NONE for safety
        self.gw_key_num_support = GatewayKeySupport.NONE
        self._gateway_manager = GatewayKeyManager(self.gw_key_num_support)

        # Log capture
        self._log_capture = None
        self._log_manager = None

        # Update installation status in state
        self._state_manager.set_provider_installed(name, self.install_dir.exists())

    def is_authentication_required(self) -> bool:
        """Check if this provider requires authentication."""
        return False

    def get_authentication_status(self) -> "AuthStatus":
        """Get current authentication status."""

        return self._state_manager.get_provider_auth_status(self.name)

    def set_authentication_status(self, status: "AuthStatus") -> None:
        """Set authentication status."""
        self._state_manager.set_provider_auth_status(self.name, status)

    async def handle_authentication_prompt(self) -> None:
        """Handle authentication prompt when required."""
        pass

    async def monitor_process_output(self) -> None:
        """Monitor process output for authentication requirements."""
        if not self.process or not self.process.stdout:
            return

        try:
            while True:
                line = await self.process.stdout.readline()
                if not line:
                    break

                output = line.decode().strip()
                if output:
                    await self.process_output_line(output)

        except Exception as e:
            print(f"Error monitoring output for {self.name}: {e}")

    async def process_output_line(self, line: str) -> None:
        """Process a line of output from the provider process."""
        # Override in subclasses to handle specific authentication detection
        pass

    def _setup_log_capture(self) -> None:
        """Setup log capture for the provider."""
        if self._log_manager is None:
            from ..utils.log_manager import LogManager, LogCapture
            self._log_manager = LogManager()
            self._log_capture = LogCapture(self.name, self._log_manager)

    async def _start_log_capture(self) -> None:
        """Start capturing logs from the process."""
        if self.process and self._log_capture:
            await self._log_capture.capture_output(self.process)

    def _stop_log_capture(self) -> None:
        """Stop log capture."""
        if self._log_capture:
            self._log_capture.stop_capture()

    def _log_event(self, message: str, level: str = "INFO") -> None:
        """Log an epic-llm specific event."""
        if self._log_manager:
            self._log_manager.write_log(self.name, "epic-llm", f"[{level}] {message}")

    @abstractmethod
    async def install(self) -> bool:
        """Install the provider."""
        pass

    @abstractmethod
    async def start(self, port: int) -> bool:
        """Start the provider on the specified port."""
        pass

    @abstractmethod
    async def stop(self) -> bool:
        """Stop the provider."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is healthy."""
        pass

    @abstractmethod
    def get_dependencies(self) -> list[Dependency]:
        """Get list of dependencies required by this provider."""
        pass

    async def check_dependencies(self, auto_install: bool = False) -> bool:
        """Check if all dependencies are satisfied."""
        from ..utils.dependencies import DependencyChecker

        checker = DependencyChecker()
        dependencies = self.get_dependencies()
        return await checker.check_and_install(
            dependencies, auto_install=auto_install, show_status=True
        )

    @property
    def is_installed(self) -> bool:
        """Check if the provider is installed."""
        return self.install_dir.exists()

    @property
    def is_running(self) -> bool:
        """Check if the provider is running."""
        if hasattr(self, "process") and self.process:
            return self.process.returncode is None

        if not self.process_id:
            return False

        # Check with state manager if process is actually running
        return self._state_manager.is_provider_running(self.name)

    @property
    def current_port(self) -> Optional[int]:
        """Get the current port the provider is running on."""
        return self._state_manager.get_provider_port(self.name)

    @property
    def process_id(self) -> Optional[int]:
        """Get the current process ID."""
        state = self._state_manager.get_provider_state(self.name)
        return state.process_id

    @property
    def is_middleware_provider(self) -> bool:
        """Check if this provider uses middleware."""
        return self._state_manager.is_middleware_provider(self.name)

    @property
    def upstream_port(self) -> Optional[int]:
        """Get the upstream port for middleware providers."""
        return self._state_manager.get_provider_upstream_port(self.name)

    def _update_process_state(self, process_id: int, port: int) -> None:
        """Update the process state after starting."""
        self._state_manager.set_provider_started(self.name, process_id, port)

    def _update_middleware_process_state(
        self, 
        middleware_process_id: int, 
        middleware_port: int,
        upstream_process_id: int, 
        upstream_port: int,
        gateway_keys: Optional[list] = None
    ) -> None:
        """Update the process state for middleware providers."""
        self._state_manager.set_middleware_provider_started(
            self.name, 
            middleware_process_id, 
            middleware_port,
            upstream_process_id, 
            upstream_port,
            gateway_keys
        )

    def _clear_process_state(self) -> None:
        """Clear the process state after stopping."""
        self._state_manager.set_provider_stopped(self.name)

    # Gateway key management methods
    def set_gateway_key(self, key: Optional[str]) -> None:
        """Set gateway API key. Override in subclasses for custom behavior."""
        self._gateway_manager.set_key(key)

    def get_gateway_key(self) -> Optional[str]:
        """Get primary gateway API key. Override in subclasses for custom behavior."""
        return self._gateway_manager.get_primary_key()

    def get_gateway_keys(self) -> list[str]:
        """Get all gateway API keys."""
        return self._gateway_manager.get_keys()

    def add_gateway_key(self, key: str) -> None:
        """Add a gateway API key (for multiple key support)."""
        self._gateway_manager.add_key(key)

    def remove_gateway_key(self, key: str) -> bool:
        """Remove a specific gateway API key."""
        return self._gateway_manager.remove_key(key)

    def has_gateway_keys(self) -> bool:
        """Check if any gateway keys are configured."""
        return self._gateway_manager.has_keys()

    def validate_gateway_key(self, key: str) -> bool:
        """Validate if a key is authorized."""
        return self._gateway_manager.validate_key(key)
