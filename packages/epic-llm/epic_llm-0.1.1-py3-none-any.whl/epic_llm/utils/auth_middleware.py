"""Authentication middleware for gateway key validation."""

import asyncio
import json
import logging
import urllib.parse
from typing import List, Optional, Set

import aiohttp
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response

from .secure_keys import SecureKeyManager

logger = logging.getLogger(__name__)


class AuthMiddleware:
    """HTTP authentication middleware that validates Bearer tokens and proxies requests."""

    def __init__(self, upstream_host: str, upstream_port: int, gateway_key_hashes: List[str]):
        """Initialize the authentication middleware.
        
        Args:
            upstream_host: Host of the upstream provider (usually 127.0.0.1)
            upstream_port: Port of the upstream provider
            gateway_key_hashes: List of bcrypt-hashed gateway API keys
        """
        self.upstream_host = upstream_host
        self.upstream_port = upstream_port
        self.key_manager = SecureKeyManager(gateway_key_hashes)
        self.app: Optional[web.Application] = None
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None

    async def validate_request(self, request: Request) -> bool:
        """Validate Authorization: Bearer <token> header.
        
        Returns:
            True if token is valid, False otherwise
        """
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return False
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        
        # Use secure key manager for validation
        return self.key_manager.validate_key(token)

    async def forward_request(self, request: Request) -> Response:
        """Proxy authenticated requests to upstream provider.
        
        Args:
            request: The incoming HTTP request
            
        Returns:
            The response from the upstream provider
        """
        # Validate and sanitize path to prevent path traversal attacks
        path = request.path
        query_string = request.query_string
        
        # Security: Validate path doesn't contain dangerous patterns
        if ".." in path or "//" in path or path.startswith("/."):
            logger.warning(f"Rejected suspicious path: {path}")
            return Response(
                text=json.dumps({"error": "Invalid request path"}),
                status=400,
                content_type="application/json"
            )
        
        # Reconstruct safe URL
        safe_path_qs = path
        if query_string:
            safe_path_qs += "?" + query_string
        
        upstream_url = f"http://{self.upstream_host}:{self.upstream_port}{safe_path_qs}"
        
        # Prepare safe headers (allowlist approach for security)
        safe_headers = {}
        allowed_headers = {
            'accept', 'accept-encoding', 'accept-language', 'cache-control',
            'content-type', 'origin', 'referer', 'user-agent',
            'x-requested-with', 'x-api-version', 'x-client-version'
        }
        
        for name, value in request.headers.items():
            header_lower = name.lower()
            # Allow specific safe headers and API-related headers starting with x-api-
            if header_lower in allowed_headers or header_lower.startswith('x-api-'):
                # Sanitize header value to prevent injection
                safe_value = str(value).replace('\n', '').replace('\r', '')[:1024]
                safe_headers[name] = safe_value
        
        # Add a User-Agent if not present
        if 'user-agent' not in {k.lower() for k in safe_headers.keys()}:
            safe_headers['User-Agent'] = 'epic-llm-middleware/1.0'
        
        try:
            # Read request body with size limit (10MB max)
            max_body_size = 10 * 1024 * 1024  # 10MB
            content_length = request.headers.get('content-length')
            
            if content_length and int(content_length) > max_body_size:
                logger.warning(f"Request body too large: {content_length} bytes")
                return Response(
                    text=json.dumps({"error": "Request body too large"}),
                    status=413,
                    content_type="application/json"
                )
            
            # Read body safely
            try:
                body = await request.read()
                # Check size after reading
                if len(body) > max_body_size:
                    logger.warning(f"Request body exceeded limit: {len(body)} bytes")
                    return Response(
                        text=json.dumps({"error": "Request body too large"}),
                        status=413,
                        content_type="application/json"
                    )
            except Exception:
                # If reading fails, continue with empty body
                body = b''
            
            # Make request to upstream
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=request.method,
                    url=upstream_url,
                    headers=safe_headers,
                    data=body if body else None,
                    timeout=aiohttp.ClientTimeout(total=30, connect=5)
                ) as upstream_response:
                    # Read upstream response
                    response_body = await upstream_response.read()
                    
                    # Create response with safe headers only (allowlist approach)
                    response_headers = {}
                    allowed_response_headers = {
                        'content-type', 'content-encoding', 'cache-control',
                        'expires', 'last-modified', 'etag', 'vary',
                        'access-control-allow-origin', 'access-control-allow-headers',
                        'access-control-allow-methods', 'x-ratelimit-limit',
                        'x-ratelimit-remaining', 'x-ratelimit-reset'
                    }
                    
                    for name, value in upstream_response.headers.items():
                        header_lower = name.lower()
                        if header_lower in allowed_response_headers or header_lower.startswith('x-api-'):
                            # Sanitize header value
                            safe_value = str(value).replace('\n', '').replace('\r', '')[:1024]
                            response_headers[name] = safe_value
                    
                    # Create response
                    response = Response(
                        body=response_body,
                        status=upstream_response.status,
                        headers=response_headers,
                    )
                    
                    return response
                    
        except Exception as e:
            # Log error without exposing sensitive details
            logger.error(f"Error forwarding request to upstream: {type(e).__name__}")
            return Response(
                text=json.dumps({"error": "Upstream service unavailable"}),
                status=502,
                content_type="application/json"
            )

    async def handle_request(self, request: Request) -> Response:
        """Handle incoming HTTP requests with authentication and forwarding.
        
        Args:
            request: The incoming HTTP request
            
        Returns:
            HTTP response (error or forwarded response)
        """
        # Check if this is a public endpoint that doesn't require authentication
        if self.is_public_endpoint(request.path):
            # Forward public endpoints without authentication
            return await self.forward_request(request)
        
        # Validate authentication for protected endpoints
        is_valid = await self.validate_request(request)
        if not is_valid:
            return Response(
                text=json.dumps({
                    "error": "Unauthorized",
                    "message": "Invalid or missing Authorization header. Use: Authorization: Bearer <your-api-key>"
                }),
                status=401,
                content_type="application/json"
            )
        
        # Forward authenticated request
        return await self.forward_request(request)
    
    def is_public_endpoint(self, path: str) -> bool:
        """Check if an endpoint should be publicly accessible without authentication.
        
        Args:
            path: The request path
            
        Returns:
            True if endpoint is public, False if authentication required
        """
        # Define public endpoints that don't require authentication
        public_endpoints = [
            "/",                    # Root/health check
            "/health",             # Health check endpoint
            "/v1/models",          # Model listing
            "/api/v1/models",      # Alternative model listing path
        ]
        
        # Check exact matches first
        if path in public_endpoints:
            return True
            
        # Check for path patterns (e.g., health checks with query params)
        if path.startswith("/health"):
            return True
            
        return False

    def update_gateway_keys(self, gateway_key_hashes: List[str]) -> None:
        """Update the list of valid gateway key hashes.
        
        Args:
            gateway_key_hashes: New list of bcrypt-hashed gateway API keys
        """
        self.key_manager = SecureKeyManager(gateway_key_hashes)
        logger.info(f"Updated gateway keys, now have {self.key_manager.get_hash_count()} keys")

    async def start(self, public_port: int) -> None:
        """Start the authentication middleware server.
        
        Args:
            public_port: Port to bind the middleware server on (public interface)
        """
        # Create aiohttp application
        self.app = web.Application()
        
        # Add catch-all route handler
        self.app.router.add_route("*", "/{path:.*}", self.handle_request)
        
        # Start the server
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        
        self.site = web.TCPSite(self.runner, "0.0.0.0", public_port)
        await self.site.start()
        
        logger.info(f"Auth middleware started on 0.0.0.0:{public_port}")
        logger.info(f"Forwarding to upstream {self.upstream_host}:{self.upstream_port}")
        logger.info(f"Configured with {self.key_manager.get_hash_count()} gateway keys")

    async def stop(self) -> None:
        """Stop the authentication middleware server."""
        if self.site:
            await self.site.stop()
            self.site = None
            
        if self.runner:
            await self.runner.cleanup()
            self.runner = None
            
        self.app = None
        logger.info("Auth middleware stopped")

    async def health_check(self) -> bool:
        """Check if the middleware server is running and responsive.
        
        Returns:
            True if healthy, False otherwise
        """
        if not self.site:
            return False
            
        try:
            # Simple health check - try to connect to our own server
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"http://127.0.0.1:{self.site._port}/health",
                    timeout=aiohttp.ClientTimeout(total=2)
                ) as response:
                    # Health endpoint is public, so we expect either:
                    # - 200/404 if upstream is healthy (forwarded successfully)
                    # - 502 if upstream is down (our error response)
                    # Any response means the middleware is running
                    return response.status in [200, 404, 502]
        except Exception:
            return False


async def create_auth_middleware(
    upstream_host: str,
    upstream_port: int,
    gateway_key_hashes: List[str],
    public_port: int
) -> AuthMiddleware:
    """Create and start an authentication middleware instance.
    
    Args:
        upstream_host: Host of the upstream provider
        upstream_port: Port of the upstream provider
        gateway_key_hashes: List of bcrypt-hashed gateway API keys
        public_port: Port to bind the middleware server on
        
    Returns:
        Running AuthMiddleware instance
    """
    middleware = AuthMiddleware(upstream_host, upstream_port, gateway_key_hashes)
    await middleware.start(public_port)
    return middleware