"""Secure storage and validation of gateway API keys using bcrypt hashing."""

import bcrypt
import logging
from typing import List, Set

logger = logging.getLogger(__name__)


class SecureKeyManager:
    """Secure storage and validation of gateway API keys using bcrypt hashing."""
    
    def __init__(self, hashed_keys: List[str]):
        """Initialize with list of bcrypt-hashed keys.
        
        Args:
            hashed_keys: List of bcrypt-hashed API keys
        """
        self.hashed_keys: Set[bytes] = set()
        
        for key in hashed_keys:
            if key:  # Skip empty/None keys
                try:
                    self.hashed_keys.add(key.encode('utf-8'))
                except Exception as e:
                    logger.warning(f"Invalid hash format, skipping: {e}")
    
    @staticmethod
    def hash_key(api_key: str) -> str:
        """Hash an API key using bcrypt with random salt.
        
        Args:
            api_key: Plain text API key to hash
            
        Returns:
            Bcrypt hash string
        """
        if not api_key:
            raise ValueError("API key cannot be empty")
            
        # Use 12 rounds for good security/performance balance
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(api_key.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def validate_key(self, api_key: str) -> bool:
        """Validate an API key against stored hashes.
        
        Args:
            api_key: Plain text API key to validate
            
        Returns:
            True if key is valid, False otherwise
        """
        if not api_key:
            return False
            
        # Input validation for security
        if len(api_key) < 8 or len(api_key) > 256:
            return False
            
        key_bytes = api_key.encode('utf-8')
        
        for hashed_key in self.hashed_keys:
            try:
                if bcrypt.checkpw(key_bytes, hashed_key):
                    return True
            except (ValueError, TypeError):
                # Invalid hash format, skip
                continue
        
        return False
    
    def add_key(self, api_key: str) -> str:
        """Add a new API key and return its hash.
        
        Args:
            api_key: Plain text API key to add
            
        Returns:
            Bcrypt hash of the added key
        """
        hashed = self.hash_key(api_key)
        self.hashed_keys.add(hashed.encode('utf-8'))
        return hashed
    
    def remove_key_by_hash(self, key_hash: str) -> bool:
        """Remove a key by its hash.
        
        Args:
            key_hash: Bcrypt hash to remove
            
        Returns:
            True if key was removed, False if not found
        """
        try:
            hash_bytes = key_hash.encode('utf-8')
            if hash_bytes in self.hashed_keys:
                self.hashed_keys.remove(hash_bytes)
                return True
        except Exception:
            pass
        return False
    
    def get_hash_count(self) -> int:
        """Get number of stored key hashes.
        
        Returns:
            Number of stored hashes
        """
        return len(self.hashed_keys)
    
    def clear_all_keys(self) -> None:
        """Remove all stored key hashes."""
        self.hashed_keys.clear()