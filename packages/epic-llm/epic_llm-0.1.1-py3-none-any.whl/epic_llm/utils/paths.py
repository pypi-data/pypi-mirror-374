"""Path management utilities for epic-llm."""

from pathlib import Path


def get_base_dir() -> Path:
    """Get the base epic-llm directory."""
    return Path.home() / ".local/share/epic-llm"


def get_pkg_dir() -> Path:
    """Get the packages directory for downloaded code."""
    return get_base_dir() / "pkg"


def get_state_file() -> Path:
    """Get the state file path."""
    return get_base_dir() / "state.json"


def get_config_file() -> Path:
    """Get the epic-llm configuration file path."""
    return get_base_dir() / "config.json"


def get_provider_pkg_dir(provider_name: str) -> Path:
    """Get the package directory for a specific provider."""
    pkg_dir = get_pkg_dir()

    # Map provider names to their package directory names
    package_names = {
        "claude": "claude-code-api",
        "copilot": "copilot-api",
        "gemini": "geminicli2api",
    }

    package_name = package_names.get(provider_name, provider_name)
    return pkg_dir / package_name


def ensure_directories() -> None:
    """Ensure all required directories exist."""
    get_base_dir().mkdir(parents=True, exist_ok=True)
    get_pkg_dir().mkdir(parents=True, exist_ok=True)
