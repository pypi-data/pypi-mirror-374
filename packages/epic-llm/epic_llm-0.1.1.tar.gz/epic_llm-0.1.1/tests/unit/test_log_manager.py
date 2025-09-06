"""Simplified tests for log management functionality."""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from epic_llm.utils.log_manager import LogManager, LogCapture
from epic_llm.utils.log_parsers import LogParserFactory, ClaudeLogParser


class TestLogManager:
    """Test the LogManager class."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary data directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def log_manager(self, temp_data_dir):
        """Create a LogManager with temporary directory."""
        with patch("epic_llm.utils.log_manager.get_base_dir", return_value=temp_data_dir):
            return LogManager()

    def test_initialization(self, log_manager):
        """Test that LogManager initializes correctly."""
        assert log_manager.logs_dir.exists()
        
        # Check provider directories are created
        for provider in ["claude", "gemini", "copilot"]:
            provider_dir = log_manager.logs_dir / provider
            assert provider_dir.exists()

    def test_write_and_read_logs(self, log_manager):
        """Test writing and reading log messages."""
        log_manager.write_log("claude", "stdout", "Test message")
        
        log_file = log_manager.get_log_file_path("claude", "stdout")
        assert log_file.exists()
        
        content = log_file.read_text()
        assert "Test message" in content

    @pytest.mark.asyncio
    async def test_tail_logs(self, log_manager):
        """Test tailing log files."""
        # Write some test logs
        for i in range(5):
            log_manager.write_log("claude", "stdout", f"Line {i}")
        
        lines = await log_manager.tail_logs("claude", "stdout", 10)
        all_content = " ".join(lines)
        assert "Line 0" in all_content
        assert "Line 4" in all_content

    def test_clear_logs(self, log_manager):
        """Test clearing logs."""
        log_manager.write_log("claude", "stdout", "Test message")
        
        result = log_manager.clear_logs("claude", "stdout")
        assert result is True
        
        log_file = log_manager.get_log_file_path("claude", "stdout")
        assert not log_file.exists()

    def test_get_log_stats(self, log_manager):
        """Test getting log file statistics."""
        log_manager.write_log("claude", "stdout", "Test message")
        
        stats = log_manager.get_log_stats("claude")
        assert stats["stdout_size"] > 0
        assert stats["total_size"] > 0


class TestLogParsers:
    """Test the log parser classes."""

    def test_claude_parser_token_usage(self):
        """Test Claude parser token usage extraction."""
        parser = ClaudeLogParser()
        
        line = "Request completed. Tokens: input 150, output 75, total 225"
        event = parser.parse_line(line)
        
        assert event.event_type == "token_usage"
        assert event.metadata["token_usage"].input_tokens == 150

    def test_log_parser_factory(self):
        """Test the log parser factory."""
        claude_parser = LogParserFactory.get_parser("claude")
        assert isinstance(claude_parser, ClaudeLogParser)
        
        # Test unknown provider falls back to base parser
        unknown_parser = LogParserFactory.get_parser("unknown")
        assert unknown_parser.provider_name == "unknown"


class TestLogCapture:
    """Test the LogCapture class."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary data directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def log_manager(self, temp_data_dir):
        """Create a LogManager with temporary directory."""
        with patch("epic_llm.utils.log_manager.get_base_dir", return_value=temp_data_dir):
            return LogManager()

    @pytest.fixture
    def log_capture(self, log_manager):
        """Create a LogCapture instance."""
        return LogCapture("test_provider", log_manager)

    def test_sensitive_content_filtering(self, log_capture):
        """Test filtering of sensitive content from logs."""
        text_with_key = "Using API key: sk-1234567890abcdef1234567890abcdef"
        filtered = log_capture._filter_sensitive_content(text_with_key)
        # Should be filtered in some way
        assert filtered != text_with_key
        assert "sk-12345..." in filtered

    def test_capture_initialization(self, log_capture, log_manager):
        """Test that capture can be initialized and stopped."""
        # Test basic functionality without actual process capture
        assert log_capture.provider == "test_provider"
        
        # Test stop capture doesn't crash
        log_capture.stop_capture()


if __name__ == "__main__":
    pytest.main([__file__])