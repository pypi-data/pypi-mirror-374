"""Gateway authentication utilities."""

from enum import Enum
from typing import List, Optional

from .secure_keys import SecureKeyManager


class GatewayKeySupport(Enum):
    """Enum for gateway key support levels."""

    NONE = "none"  # No gateway authentication support
    SINGLE = "single"  # Supports one API key
    MULTIPLE = "multiple"  # Supports multiple API keys
    MW_MULTIPLE = "mw_multiple"  # Middleware-provided multiple key support


class GatewayKeyManager:
    """Base class for managing gateway keys using secure hash storage."""

    def __init__(self, support_level: GatewayKeySupport):
        self.support_level = support_level
        self._key_hashes: List[str] = []  # Store hashes instead of plaintext
        self._plaintext_keys: List[str] = []  # Store plaintext for providers that need local storage

    def set_key(self, key: Optional[str]) -> None:
        """Set a single gateway key. None to disable."""
        if self.support_level == GatewayKeySupport.NONE:
            raise ValueError("Gateway keys are not supported by this provider")

        if key is None:
            self._key_hashes = []
            self._plaintext_keys = []
        else:
            # Hash the key before storing
            hashed_key = SecureKeyManager.hash_key(key)
            self._key_hashes = [hashed_key]
            self._plaintext_keys = [key]  # Keep plaintext for local storage

    def add_key(self, key: str) -> None:
        """Add a gateway key (for multiple key support)."""
        if self.support_level == GatewayKeySupport.NONE:
            raise ValueError("Gateway keys are not supported by this provider")

        if self.support_level == GatewayKeySupport.SINGLE and self._key_hashes:
            raise ValueError("Provider only supports a single gateway key")

        # Hash the key before storing
        hashed_key = SecureKeyManager.hash_key(key)
        if hashed_key not in self._key_hashes:
            self._key_hashes.append(hashed_key)
            self._plaintext_keys.append(key)  # Keep plaintext for local storage

    def remove_key(self, key: str) -> bool:
        """Remove a specific gateway key. Returns True if key was found and removed."""
        # Find and remove both hash and plaintext
        if key in self._plaintext_keys:
            index = self._plaintext_keys.index(key)
            self._plaintext_keys.remove(key)
            if index < len(self._key_hashes):
                self._key_hashes.pop(index)
            return True
        return False

    def get_keys(self) -> List[str]:
        """Get all configured gateway key hashes (for internal use)."""
        return self._key_hashes.copy()

    def get_plaintext_keys(self) -> List[str]:
        """Get all configured gateway keys in plaintext (for local storage)."""
        return self._plaintext_keys.copy()

    def get_primary_key(self) -> Optional[str]:
        """Get the primary (first) gateway key hash."""
        return self._key_hashes[0] if self._key_hashes else None

    def get_primary_plaintext_key(self) -> Optional[str]:
        """Get the primary (first) gateway key in plaintext."""
        return self._plaintext_keys[0] if self._plaintext_keys else None

    def has_keys(self) -> bool:
        """Check if any gateway keys are configured."""
        return len(self._key_hashes) > 0

    def validate_key(self, key: str) -> bool:
        """Validate if a key is authorized using secure hash comparison."""
        if not self._key_hashes:
            return False
        key_manager = SecureKeyManager(self._key_hashes)
        return key_manager.validate_key(key)
