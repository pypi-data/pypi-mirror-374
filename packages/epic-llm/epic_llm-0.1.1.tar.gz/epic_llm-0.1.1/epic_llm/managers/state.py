"""State management for provider processes and ports."""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

import psutil

from ..utils.paths import ensure_directories, get_state_file


class AuthStatus(Enum):
    """Authentication status for providers."""

    NOT_REQUIRED = "not_required"
    REQUIRED = "required"
    AUTHENTICATED = "authenticated"
    FAILED = "failed"


@dataclass
class ProviderState:
    """State information for a provider."""

    name: str
    process_id: Optional[int] = None
    port: Optional[int] = None
    started_at: Optional[str] = None
    is_installed: bool = False
    auth_status: str = AuthStatus.NOT_REQUIRED.value
    # Middleware support fields
    upstream_process_id: Optional[int] = None
    upstream_port: Optional[int] = None
    is_middleware: bool = False
    gateway_keys: Optional[list] = None


class StateManager:
    """Manages persistent state for providers."""

    def __init__(self, state_file: Optional[Path] = None):
        if state_file is None:
            ensure_directories()
            state_file = get_state_file()

        self.state_file = state_file
        self._state: Dict[str, ProviderState] = {}
        self.load_state()

    def load_state(self) -> None:
        """Load state from disk."""
        if not self.state_file.exists():
            return

        try:
            with open(self.state_file, "r") as f:
                data = json.load(f)

            self._state = {}
            for name, state_dict in data.items():
                # Ensure all required fields exist with defaults for backward compatibility
                state_dict.setdefault('upstream_process_id', None)
                state_dict.setdefault('upstream_port', None)
                state_dict.setdefault('is_middleware', False)
                state_dict.setdefault('gateway_keys', None)
                self._state[name] = ProviderState(**state_dict)
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            print(f"Debug: State loading failed with error: {e}")
            # If state file is corrupted, start fresh
            self._state = {}

    def save_state(self) -> None:
        """Save state to disk."""
        try:
            data = {}
            for name, state in self._state.items():
                data[name] = asdict(state)

            print(f"Debug: Saving state to {self.state_file}")
            print(f"Debug: State content: {data}")

            with open(self.state_file, "w") as f:
                json.dump(data, f, indent=2)

            print("Debug: State saved successfully")
        except Exception as e:
            print(f"Debug: Failed to save state: {e}")
            # Don't fail if we can't save state
            pass

    def get_provider_state(self, name: str) -> ProviderState:
        """Get state for a provider."""
        if name not in self._state:
            self._state[name] = ProviderState(name=name)
        return self._state[name]

    def update_provider_state(self, name: str, **kwargs) -> None:
        """Update state for a provider."""
        state = self.get_provider_state(name)
        for key, value in kwargs.items():
            if hasattr(state, key):
                setattr(state, key, value)
        self.save_state()

    def set_provider_started(self, name: str, process_id: int, port: int) -> None:
        """Mark a provider as started."""
        print(
            f"Debug: StateManager.set_provider_started called with "
            f"name={name}, process_id={process_id}, port={port}"
        )
        self.update_provider_state(
            name,
            process_id=process_id,
            port=port,
            started_at=datetime.now().isoformat(),
        )
        print(f"Debug: State updated for {name}")
        print(f"Debug: Current state: {asdict(self._state[name])}")

    def set_middleware_provider_started(
        self, 
        name: str, 
        middleware_process_id: int, 
        middleware_port: int,
        upstream_process_id: int, 
        upstream_port: int,
        gateway_keys: Optional[list] = None
    ) -> None:
        """Mark a middleware provider as started with both middleware and upstream processes."""
        print(
            f"Debug: StateManager.set_middleware_provider_started called with "
            f"name={name}, middleware_pid={middleware_process_id}, middleware_port={middleware_port}, "
            f"upstream_pid={upstream_process_id}, upstream_port={upstream_port}"
        )
        self.update_provider_state(
            name,
            process_id=middleware_process_id,
            port=middleware_port,
            upstream_process_id=upstream_process_id,
            upstream_port=upstream_port,
            is_middleware=True,
            gateway_keys=gateway_keys,
            started_at=datetime.now().isoformat(),
        )
        print(f"Debug: Middleware state updated for {name}")
        print(f"Debug: Current state: {asdict(self._state[name])}")

    def set_provider_stopped(self, name: str) -> None:
        """Mark a provider as stopped."""
        # Preserve gateway_keys when stopping
        current_state = self.get_provider_state(name)
        gateway_keys = current_state.gateway_keys
        
        self.update_provider_state(
            name, 
            process_id=None, 
            port=None, 
            upstream_process_id=None,
            upstream_port=None,
            is_middleware=False,
            gateway_keys=gateway_keys,  # Preserve gateway keys
            started_at=None
        )

    def set_provider_installed(self, name: str, installed: bool) -> None:
        """Update provider installation status."""
        self.update_provider_state(name, is_installed=installed)

    def is_provider_running(self, name: str) -> bool:
        """Check if a provider is actually running by checking both PID and port."""
        state = self.get_provider_state(name)
        if not state.process_id and not state.port:
            return False

        # For middleware providers, check both processes
        if state.is_middleware:
            return self._is_middleware_provider_running(state)
        
        # Standard provider check
        return self._is_standard_provider_running(state, name)

    def _is_middleware_provider_running(self, state: ProviderState) -> bool:
        """Check if both middleware and upstream processes are running."""
        middleware_running = False
        upstream_running = False
        
        # Check middleware process
        if state.process_id:
            try:
                process = psutil.Process(state.process_id)
                middleware_running = (
                    process.is_running() and process.status() != psutil.STATUS_ZOMBIE
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                middleware_running = False
                
        # Check upstream process
        if state.upstream_process_id:
            try:
                process = psutil.Process(state.upstream_process_id)
                upstream_running = (
                    process.is_running() and process.status() != psutil.STATUS_ZOMBIE
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                upstream_running = False
        
        # Both processes must be running for middleware provider
        return middleware_running and upstream_running

    def _is_standard_provider_running(self, state: ProviderState, name: str) -> bool:
        """Check if a standard (non-middleware) provider is running."""
        # First try to check the tracked PID
        pid_running = False
        if state.process_id:
            try:
                process = psutil.Process(state.process_id)
                pid_running = (
                    process.is_running() and process.status() != psutil.STATUS_ZOMBIE
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pid_running = False

        # If PID check fails, try port-based detection as fallback
        port_running = False
        if state.port:
            try:
                import subprocess

                result = subprocess.run(
                    ["ss", "-tlnp"], capture_output=True, text=True, timeout=2
                )
                if result.returncode == 0:
                    # Check if something is listening on our port
                    for line in result.stdout.split("\n"):
                        if f":{state.port}" in line and "LISTEN" in line:
                            # Extract PID if possible and update our tracking
                            import re

                            pid_match = re.search(r"pid=(\d+)", line)
                            if pid_match:
                                actual_pid = int(pid_match.group(1))
                                if actual_pid != state.process_id:
                                    print(
                                        f"Debug: Updating tracked PID for {name} from {state.process_id} to {actual_pid}"
                                    )
                                    self.update_provider_state(
                                        name, process_id=actual_pid
                                    )
                                port_running = True
                                break
            except Exception as e:
                print(f"Debug: Port check failed for {name}: {e}")

        # Provider is running if either PID or port check succeeds
        is_running = pid_running or port_running

        if not is_running and (state.process_id or state.port):
            print(
                f"Debug: Provider {name} not running (PID: {pid_running}, Port: {port_running})"
            )
            # Only clean up state if both checks fail
            self.set_provider_stopped(name)

        return is_running

    def get_provider_port(self, name: str) -> Optional[int]:
        """Get the port a provider is running on."""
        state = self.get_provider_state(name)
        return state.port if self.is_provider_running(name) else None

    def get_all_allocated_ports(self) -> Dict[str, int]:
        """Get all currently allocated ports."""
        allocated = {}
        for name, state in self._state.items():
            if self.is_provider_running(name) and state.port:
                allocated[name] = state.port
        return allocated

    def set_provider_auth_status(self, name: str, auth_status: AuthStatus) -> None:
        """Update provider authentication status."""
        self.update_provider_state(name, auth_status=auth_status.value)

    def get_provider_auth_status(self, name: str) -> AuthStatus:
        """Get provider authentication status."""
        state = self.get_provider_state(name)
        try:
            return AuthStatus(state.auth_status)
        except ValueError:
            return AuthStatus.NOT_REQUIRED

    def is_middleware_provider(self, name: str) -> bool:
        """Check if a provider is using middleware."""
        state = self.get_provider_state(name)
        return state.is_middleware

    def get_provider_upstream_port(self, name: str) -> Optional[int]:
        """Get the upstream port for a middleware provider."""
        state = self.get_provider_state(name)
        return state.upstream_port if state.is_middleware else None

    def get_provider_gateway_keys(self, name: str) -> Optional[list]:
        """Get the gateway keys for a provider."""
        state = self.get_provider_state(name)
        return state.gateway_keys

    def update_provider_gateway_keys(self, name: str, gateway_keys: Optional[list]) -> None:
        """Update gateway keys for a provider."""
        self.update_provider_state(name, gateway_keys=gateway_keys)

    def cleanup_dead_processes(self) -> None:
        """Clean up state for dead processes."""
        for name in list(self._state.keys()):
            if not self.is_provider_running(name):
                state = self._state[name]
                if state.process_id or state.port:
                    self.set_provider_stopped(name)
