"""Dependency validation functions."""

import asyncio
import shutil
from typing import List, Tuple


async def check_cli_command(command: List[str]) -> bool:
    """Check if a CLI command is available and working."""
    try:
        process = await asyncio.create_subprocess_exec(
            *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await process.wait()
        return process.returncode == 0
    except (FileNotFoundError, OSError):
        return False


def check_executable_in_path(executable: str) -> bool:
    """Check if an executable is available in PATH."""
    return shutil.which(executable) is not None


async def check_npm_package_global(package_name: str) -> bool:
    """Check if an npm package is installed globally."""
    try:
        process = await asyncio.create_subprocess_exec(
            "npm",
            "list",
            "-g",
            package_name,
            "--depth=0",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.wait()
        return process.returncode == 0
    except (FileNotFoundError, OSError):
        return False


async def check_npx_package(package_url: str, check_args: List[str]) -> bool:
    """Check if an npx package can be executed."""
    try:
        cmd = ["npx", package_url] + check_args
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        # Give it a short timeout since npx might try to install
        try:
            await asyncio.wait_for(process.wait(), timeout=10.0)
            return process.returncode == 0
        except asyncio.TimeoutError:
            process.terminate()
            await process.wait()
            return False
    except (FileNotFoundError, OSError):
        return False


def check_python_version(min_version: Tuple[int, int] = (3, 8)) -> bool:
    """Check if Python version meets minimum requirements."""
    import sys

    return sys.version_info >= min_version


async def install_npm_package_global(package_name: str) -> bool:
    """Install an npm package globally."""
    try:
        process = await asyncio.create_subprocess_exec(
            "npm",
            "install",
            "-g",
            package_name,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.wait()
        return process.returncode == 0
    except (FileNotFoundError, OSError):
        return False
