"""Claude CLI authentication validation utilities."""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, Optional

from ..managers.state import AuthStatus


class ClaudeAuthValidator:
    """Validates Claude CLI authentication status."""

    def __init__(self):
        self.credentials_file = Path.home() / ".claude" / ".credentials.json"
        self.claude_dir = Path.home() / ".claude"

    async def validate_authentication(self) -> AuthStatus:
        """Validate Claude CLI authentication and return status."""
        # Level 1: Check if Claude CLI is installed
        if not await self._check_claude_cli_installed():
            return AuthStatus.REQUIRED

        # Level 2: Check if credentials file exists
        if not self.credentials_file.exists():
            return AuthStatus.REQUIRED

        # Level 3: Test authentication with claude whoami
        if not await self._test_claude_whoami():
            return AuthStatus.FAILED

        return AuthStatus.AUTHENTICATED

    async def _check_claude_cli_installed(self) -> bool:
        """Check if Claude CLI is installed and accessible."""
        try:
            result = await asyncio.create_subprocess_exec(
                "claude",
                "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await result.wait()
            return result.returncode == 0
        except FileNotFoundError:
            return False
        except Exception:
            return False

    async def _test_claude_whoami(self) -> bool:
        """Test Claude CLI authentication with whoami command."""
        try:
            result = await asyncio.create_subprocess_exec(
                "claude",
                "whoami",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()

            if result.returncode == 0:
                # Check if we got a meaningful response (username)
                username = stdout.decode().strip()
                return bool(username and len(username) > 0)
            else:
                return False

        except Exception:
            return False

    async def get_claude_username(self) -> Optional[str]:
        """Get the authenticated Claude username."""
        try:
            result = await asyncio.create_subprocess_exec(
                "claude",
                "whoami",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()

            if result.returncode == 0:
                return stdout.decode().strip()
            return None

        except Exception:
            return None

    async def get_claude_version(self) -> Optional[str]:
        """Get Claude CLI version."""
        try:
            result = await asyncio.create_subprocess_exec(
                "claude",
                "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()

            if result.returncode == 0:
                return stdout.decode().strip()
            return None

        except Exception:
            return None

    def get_credential_info(self) -> Optional[Dict[str, Any]]:
        """Get basic information about stored Claude credentials."""
        if not self.credentials_file.exists():
            return None

        try:
            stat = self.credentials_file.stat()

            info = {
                "credentials_file_exists": True,
                "file_size": stat.st_size,
                "last_modified": stat.st_mtime,
                "file_permissions": oct(stat.st_mode)[-3:],  # Last 3 digits
                "is_secure": stat.st_mode & 0o077
                == 0,  # Check if only owner can read/write
            }

            # Try to get basic info without exposing sensitive data
            try:
                with open(self.credentials_file, "r") as f:
                    creds_data = json.load(f)
                    info["has_session_token"] = bool(creds_data.get("sessionToken"))
                    info["has_user_uuid"] = bool(creds_data.get("userUuid"))
                    # Don't expose actual tokens/UUIDs
            except (json.JSONDecodeError, PermissionError, KeyError):
                info["credentials_readable"] = False

            return info

        except Exception:
            return None

    async def test_simple_command(self) -> bool:
        """Test a simple Claude command to verify full functionality."""
        try:
            result = await asyncio.create_subprocess_exec(
                "claude",
                "-p",
                "Respond with just: OK",
                "--output-format",
                "text",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # Give it a reasonable timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    result.communicate(), timeout=30.0
                )

                if result.returncode == 0:
                    response = stdout.decode().strip()
                    # Check if we got a reasonable response
                    return bool(response and len(response) > 0)
                return False

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
