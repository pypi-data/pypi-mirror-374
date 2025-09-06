"""OAuth credential validation utilities for Gemini provider."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

from ..managers.state import AuthStatus


class GeminiAuthValidator:
    """Validates OAuth credentials for Gemini provider."""

    def __init__(self, install_dir: Path):
        self.install_dir = install_dir
        self.oauth_file = install_dir / "oauth_creds.json"

    async def validate_credentials(self) -> AuthStatus:
        """Validate OAuth credentials and return authentication status."""
        # Level 1: File existence and basic structure
        if not self.oauth_file.exists():
            return AuthStatus.REQUIRED

        try:
            with open(self.oauth_file, "r") as f:
                creds_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError, PermissionError):
            return AuthStatus.FAILED

        # Level 2: Required fields validation
        if not self._validate_required_fields(creds_data):
            return AuthStatus.REQUIRED

        # Level 3: Token validity test
        if not await self._test_refresh_token(creds_data):
            return AuthStatus.FAILED

        return AuthStatus.AUTHENTICATED

    def _validate_required_fields(self, creds_data: Dict[str, Any]) -> bool:
        """Validate that required OAuth fields are present."""
        required_fields = ["refresh_token"]

        for field in required_fields:
            if not creds_data.get(field):
                return False

        # Check for either client_id/client_secret or use defaults
        if not creds_data.get("client_id") or not creds_data.get("client_secret"):
            # These might be using default values from geminicli2api
            pass

        return True

    async def _test_refresh_token(self, creds_data: Dict[str, Any]) -> bool:
        """Test if refresh token can be used to get a new access token."""
        try:
            # Use the same validation logic as geminicli2api
            refresh_token = creds_data.get("refresh_token")
            if not refresh_token:
                return False

            # Get client credentials (use defaults if not in file)
            client_id = creds_data.get(
                "client_id",
                "681255809395-oo8ft2oprdrnp9e3aqf6av3hmdib135j.apps.googleusercontent.com",
            )
            client_secret = creds_data.get(
                "client_secret", "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"
            )

            # Test refresh token by making a request to Google OAuth endpoint
            token_data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data=token_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )

                if response.status_code == 200:
                    token_response = response.json()
                    # Check if we got a valid access token
                    return bool(token_response.get("access_token"))
                else:
                    # Token refresh failed - could be expired or revoked
                    return False

        except Exception:
            # Network error or other issue
            return False

    def get_credential_info(self) -> Optional[Dict[str, Any]]:
        """Get basic information about stored credentials."""
        if not self.oauth_file.exists():
            return None

        try:
            with open(self.oauth_file, "r") as f:
                creds_data = json.load(f)

            info = {
                "has_refresh_token": bool(creds_data.get("refresh_token")),
                "has_access_token": bool(
                    creds_data.get("token") or creds_data.get("access_token")
                ),
                "project_id": creds_data.get("project_id"),
                "scopes": creds_data.get("scopes", []),
            }

            # Parse expiry if present
            if creds_data.get("expiry"):
                try:
                    expiry_str = creds_data["expiry"]
                    if expiry_str.endswith("Z"):
                        expiry_str = expiry_str[:-1] + "+00:00"
                    expiry = datetime.fromisoformat(expiry_str)
                    info["expires_at"] = expiry
                    info["is_expired"] = expiry < datetime.now(expiry.tzinfo)
                except Exception:
                    info["expires_at"] = None
                    info["is_expired"] = None
            else:
                info["expires_at"] = None
                info["is_expired"] = None

            return info

        except Exception:
            return None
