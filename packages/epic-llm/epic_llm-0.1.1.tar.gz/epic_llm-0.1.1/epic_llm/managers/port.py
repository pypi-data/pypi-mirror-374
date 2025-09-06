"""Port management utilities."""

import socket
from typing import Dict, Optional

from .state import StateManager


class PortManager:
    """Manages port allocation for providers."""

    def __init__(self, port_range: tuple[int, int] = (8000, 8999)):
        self.port_range = port_range
        self.default_ports = {
            "claude": 8000,
            "copilot": 8081,  # Changed from 8080 to avoid Gemini OAuth conflict
            "gemini": 8888,
        }
        self._state_manager = StateManager()

    def is_port_available(self, port: int) -> bool:
        """Check if a port is available."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(("localhost", port))
                return result != 0
        except Exception:
            return False

    def get_available_port(
        self, provider_name: str, preferred_port: Optional[int] = None
    ) -> int:
        """Get an available port for a provider."""
        # Get currently allocated ports from state
        allocated_ports = self._state_manager.get_all_allocated_ports()

        # Try preferred port first
        if preferred_port:
            if not self.is_port_available(preferred_port):
                # Check if it's allocated by our own system
                allocated_by = None
                for provider, port in allocated_ports.items():
                    if port == preferred_port:
                        allocated_by = provider
                        break

                if allocated_by:
                    raise RuntimeError(
                        f"Port {preferred_port} is already in use by {allocated_by} provider. "
                        f"Stop {allocated_by} first or choose a different port."
                    )
                else:
                    raise RuntimeError(
                        f"Port {preferred_port} is already in use by another process. "
                        f"Please choose a different port for {provider_name}."
                    )
            return preferred_port

        # Try default port for this provider
        default_port = self.default_ports.get(provider_name)
        if default_port:
            if not self.is_port_available(default_port):
                # Check if it's allocated by our own system
                allocated_by = None
                for provider, port in allocated_ports.items():
                    if port == default_port:
                        allocated_by = provider
                        break

                if allocated_by:
                    # Try to find an alternative port in this case
                    pass  # Continue to automatic port assignment
                else:
                    raise RuntimeError(
                        f"Default port {default_port} for {provider_name} is in use by another process. "
                        f"Specify a custom port using --port {provider_name}:PORT"
                    )
            else:
                return default_port

        # Find any available port in range
        for port in range(self.port_range[0], self.port_range[1] + 1):
            if port not in allocated_ports.values() and self.is_port_available(port):
                return port

        raise RuntimeError(
            f"No available ports in range {self.port_range}. "
            f"Please stop some providers or specify a custom port."
        )

    def release_port(self, provider_name: str) -> None:
        """Release a port allocated to a provider."""
        # Port release is now handled by the state manager
        pass

    def validate_port_assignments(self, port_map: dict) -> list[str]:
        """Validate port assignments for conflicts. Returns list of error messages."""
        errors = []
        allocated_ports = self._state_manager.get_all_allocated_ports()

        # Check for conflicts with currently running providers
        for provider, requested_port in port_map.items():
            # Check if port is already allocated by another provider
            for running_provider, running_port in allocated_ports.items():
                if running_port == requested_port and running_provider != provider:
                    errors.append(
                        f"Port {requested_port} is already in use by {running_provider}. "
                        f"Stop {running_provider} first or choose a different port for {provider}."
                    )

            # Check if port is in use by external process
            if not self.is_port_available(requested_port):
                # Only add this error if it's not already covered by the allocation check
                if requested_port not in allocated_ports.values():
                    errors.append(
                        f"Port {requested_port} is in use by another process. "
                        f"Choose a different port for {provider}."
                    )

        # Check for conflicts within the requested assignments
        port_usage = {}
        for provider, port in port_map.items():
            if port in port_usage:
                errors.append(
                    f"Port {port} is assigned to both {port_usage[port]} and {provider}. "
                    f"Each provider needs a unique port."
                )
            else:
                port_usage[port] = provider

        # Check for reserved ports
        reserved_ports = {8080: "Gemini OAuth (hardcoded, cannot be changed)"}
        for provider, port in port_map.items():
            if port in reserved_ports:
                errors.append(
                    f"Port {port} is reserved for {reserved_ports[port]}. "
                    f"Choose a different port for {provider}."
                )

        return errors

    def get_allocated_ports(self) -> Dict[str, int]:
        """Get all currently allocated ports."""
        return self._state_manager.get_all_allocated_ports()
