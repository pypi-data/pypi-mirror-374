#!/usr/bin/env python3
"""Standalone middleware daemon for authentication."""

import asyncio
import json
import sys
import traceback
from pathlib import Path
from typing import Dict, Any

# Add epic_llm to path for proper imports
epic_llm_root = Path(__file__).parent.parent
sys.path.insert(0, str(epic_llm_root.parent))

try:
    from epic_llm.utils.auth_middleware import AuthMiddleware
except ImportError as e:
    print(f"Failed to import AuthMiddleware: {e}")
    print(f"Python path: {sys.path}")
    print(f"Current directory: {Path.cwd()}")
    print(f"Script directory: {Path(__file__).parent}")
    print(f"Epic LLM root: {epic_llm_root}")
    sys.exit(1)


def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize configuration data.
    
    Args:
        config: Raw configuration dictionary
        
    Returns:
        Validated and sanitized configuration
        
    Raises:
        ValueError: If configuration is invalid
    """
    required_fields = ['upstream_port', 'public_port', 'gateway_keys']
    
    # Check required fields
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate port numbers
    upstream_port = config['upstream_port']
    public_port = config['public_port']
    
    if not isinstance(upstream_port, int) or not (1024 <= upstream_port <= 65535):
        raise ValueError(f"Invalid upstream_port: {upstream_port} (must be 1024-65535)")
    
    if not isinstance(public_port, int) or not (1024 <= public_port <= 65535):
        raise ValueError(f"Invalid public_port: {public_port} (must be 1024-65535)")
    
    if upstream_port == public_port:
        raise ValueError("upstream_port and public_port cannot be the same")
    
    # Validate gateway keys
    gateway_keys = config['gateway_keys']
    if not isinstance(gateway_keys, list):
        raise ValueError("gateway_keys must be a list")
    
    if len(gateway_keys) == 0:
        raise ValueError("At least one gateway key must be provided")
    
    # Validate each key
    validated_keys = []
    for key in gateway_keys:
        if not isinstance(key, str):
            raise ValueError("Gateway keys must be strings")
        if len(key) < 8:
            raise ValueError("Gateway keys must be at least 8 characters")
        if len(key) > 256:
            raise ValueError("Gateway keys must be at most 256 characters")
        validated_keys.append(key)
    
    # Validate upstream host
    upstream_host = config.get("upstream_host", "127.0.0.1")
    if upstream_host not in ["127.0.0.1", "localhost"]:
        raise ValueError(f"Invalid upstream_host: {upstream_host} (must be 127.0.0.1 or localhost)")
    
    return {
        "upstream_host": upstream_host,
        "upstream_port": upstream_port,
        "public_port": public_port,
        "gateway_keys": validated_keys
    }


async def main():
    """Run the middleware daemon."""
    try:
        if len(sys.argv) != 2:
            print("Usage: middleware_daemon.py <config_file>")
            sys.exit(1)
        
        config_file = Path(sys.argv[1])
        print(f"Loading config from: {config_file}")
        
        if not config_file.exists():
            print(f"Config file not found: {config_file}")
            sys.exit(1)
        
        try:
            with open(config_file) as f:
                raw_config = json.load(f)
            
            # Validate and sanitize configuration
            config = validate_config(raw_config)
            print(f"Config validated successfully")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in config file: {e}")
            sys.exit(1)
        except ValueError as e:
            print(f"Invalid configuration: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Failed to load config: {e}")
            sys.exit(1)
        
        upstream_host = config.get("upstream_host", "127.0.0.1")
        upstream_port = config["upstream_port"]
        public_port = config["public_port"]
        gateway_keys = config["gateway_keys"]
        
        print(f"Starting middleware daemon on port {public_port}")
        print(f"Proxying to {upstream_host}:{upstream_port}")
        print(f"Gateway keys: {len(gateway_keys)} configured")
        
        middleware = AuthMiddleware(upstream_host, upstream_port, gateway_keys)
        print("AuthMiddleware created, starting server...")
        
        await middleware.start(public_port)
        print(f"Middleware server started on port {public_port}")
        
        try:
            # Keep running until interrupted
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down middleware daemon...")
            await middleware.stop()
            print("Middleware daemon stopped")
    
    except Exception as e:
        # Log error without exposing sensitive details
        print(f"Error in middleware daemon: {type(e).__name__}")
        # Only show full traceback in debug situations (could add debug flag later)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())