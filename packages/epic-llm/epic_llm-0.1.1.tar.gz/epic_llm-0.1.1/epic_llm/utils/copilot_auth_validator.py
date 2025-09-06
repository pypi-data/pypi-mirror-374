"""GitHub Copilot authentication validation utilities."""

import asyncio
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

from ..managers.state import AuthStatus


class CopilotAuthValidator:
    """Validates GitHub Copilot authentication status."""

    def __init__(self):
        # ericc-ch/copilot-api stores GitHub token here
        self.github_token_file = (
            Path.home() / ".local" / "share" / "copilot-api" / "github_token"
        )
        self.app_dir = Path.home() / ".local" / "share" / "copilot-api"

    async def validate_authentication(self) -> AuthStatus:
        """Validate GitHub Copilot authentication and return status."""
        # Level 1: Check if copilot-api is available (via npx)
        if not await self._check_copilot_api_available():
            return AuthStatus.REQUIRED

        # Level 2: Check if GitHub token file exists
        if not self.github_token_file.exists():
            return AuthStatus.REQUIRED

        # Level 3: Test GitHub token validity
        github_token = await self._read_github_token()
        if not github_token:
            return AuthStatus.REQUIRED

        if not await self._test_github_token(github_token):
            return AuthStatus.FAILED

        return AuthStatus.AUTHENTICATED

    async def _check_copilot_api_available(self) -> bool:
        """Check if copilot-api is available via npx."""
        try:
            result = await asyncio.create_subprocess_exec(
                "npx",
                "copilot-api@latest",
                "--help",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await result.wait()
            return result.returncode == 0
        except FileNotFoundError:
            return False
        except Exception:
            return False

    async def _read_github_token(self) -> Optional[str]:
        """Read GitHub token from copilot-api storage."""
        try:
            if not self.github_token_file.exists():
                return None

            content = self.github_token_file.read_text().strip()
            return content if content else None

        except Exception:
            return None

    async def _test_github_token(self, token: str) -> bool:
        """Test GitHub token by calling GitHub API /user endpoint."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"token {token}",
                        "Accept": "application/vnd.github.v3+json",
                        "User-Agent": "llm-api-gw",
                    },
                )

                if response.status_code == 200:
                    user_data = response.json()
                    # Check if we got a valid response with login
                    return bool(user_data.get("login"))
                else:
                    return False

        except Exception:
            return False

    async def get_github_username(self) -> Optional[str]:
        """Get the authenticated GitHub username."""
        github_token = await self._read_github_token()
        if not github_token:
            return None

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"token {github_token}",
                        "Accept": "application/vnd.github.v3+json",
                        "User-Agent": "llm-api-gw",
                    },
                )

                if response.status_code == 200:
                    user_data = response.json()
                    return user_data.get("login")
                return None

        except Exception:
            return None

    async def check_copilot_subscription(self) -> Optional[Dict[str, Any]]:
        """Check GitHub Copilot subscription status."""
        github_token = await self._read_github_token()
        if not github_token:
            return None

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Check Copilot subscription via GitHub API
                response = await client.get(
                    "https://api.github.com/user/copilot_seats",
                    headers={
                        "Authorization": f"token {github_token}",
                        "Accept": "application/vnd.github.v3+json",
                        "User-Agent": "llm-api-gw",
                    },
                )

                if response.status_code == 200:
                    return response.json()
                return None

        except Exception:
            return None

    def get_credential_info(self) -> Optional[Dict[str, Any]]:
        """Get basic information about stored GitHub credentials."""
        if not self.github_token_file.exists():
            return None

        try:
            stat = self.github_token_file.stat()

            info = {
                "github_token_file_exists": True,
                "file_size": stat.st_size,
                "last_modified": stat.st_mtime,
                "file_permissions": oct(stat.st_mode)[-3:],  # Last 3 digits
                "is_secure": stat.st_mode & 0o077
                == 0,  # Check if only owner can read/write
                "app_dir_exists": self.app_dir.exists(),
            }

            # Check if token file has content without exposing the token
            try:
                content = self.github_token_file.read_text().strip()
                info["has_token_content"] = bool(content)
            except Exception:
                info["has_token_content"] = False

            return info

        except Exception:
            return None

    async def test_copilot_api_auth_command(self) -> bool:
        """Test running copilot-api auth command to verify installation."""
        try:
            result = await asyncio.create_subprocess_exec(
                "npx",
                "copilot-api@latest",
                "auth",
                "--help",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # Give it a reasonable timeout
            try:
                await asyncio.wait_for(result.wait(), timeout=30.0)
                return result.returncode == 0
            except asyncio.TimeoutError:
                # Kill the process if it takes too long
                try:
                    result.terminate()
                    await result.wait()
                except Exception:
                    pass
                return False

        except Exception:
            return False
