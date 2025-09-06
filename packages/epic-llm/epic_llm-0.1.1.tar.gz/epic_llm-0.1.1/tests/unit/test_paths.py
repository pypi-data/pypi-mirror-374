"""Tests for paths utility."""

from pathlib import Path
from unittest.mock import patch

from epic_llm.utils.paths import (
    ensure_directories,
    get_base_dir,
    get_config_file,
    get_pkg_dir,
    get_provider_pkg_dir,
    get_state_file,
)


class TestPathsUtility:
    """Test paths utility functions."""

    def test_get_base_dir(self):
        """Test getting base directory."""
        expected = Path.home() / ".local/share/epic-llm"
        assert get_base_dir() == expected

    def test_get_pkg_dir(self):
        """Test getting packages directory."""
        expected = Path.home() / ".local/share/epic-llm/pkg"
        assert get_pkg_dir() == expected

    def test_get_state_file(self):
        """Test getting state file path."""
        expected = Path.home() / ".local/share/epic-llm/state.json"
        assert get_state_file() == expected

    def test_get_config_file(self):
        """Test getting config file path."""
        expected = Path.home() / ".local/share/epic-llm/config.json"
        assert get_config_file() == expected

    def test_get_provider_pkg_dir_claude(self):
        """Test getting Claude provider package directory."""
        expected = Path.home() / ".local/share/epic-llm/pkg/claude-code-api"
        assert get_provider_pkg_dir("claude") == expected

    def test_get_provider_pkg_dir_copilot(self):
        """Test getting Copilot provider package directory."""
        expected = Path.home() / ".local/share/epic-llm/pkg/copilot-api"
        assert get_provider_pkg_dir("copilot") == expected

    def test_get_provider_pkg_dir_gemini(self):
        """Test getting Gemini provider package directory."""
        expected = Path.home() / ".local/share/epic-llm/pkg/geminicli2api"
        assert get_provider_pkg_dir("gemini") == expected

    def test_get_provider_pkg_dir_unknown(self):
        """Test getting unknown provider package directory."""
        expected = Path.home() / ".local/share/epic-llm/pkg/unknown"
        assert get_provider_pkg_dir("unknown") == expected

    def test_ensure_directories(self):
        """Test ensuring directories are created."""
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            ensure_directories()

            # Should call mkdir twice: once for base dir, once for pkg dir
            assert mock_mkdir.call_count == 2

            # Check the arguments
            calls = mock_mkdir.call_args_list
            assert all(call[1]["parents"] is True for call in calls)
            assert all(call[1]["exist_ok"] is True for call in calls)
