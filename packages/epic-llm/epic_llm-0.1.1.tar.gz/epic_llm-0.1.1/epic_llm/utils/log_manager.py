"""Log management system for provider monitoring."""

import asyncio
import os
import time
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator, Dict, List, Optional, TextIO
from enum import Enum

from .paths import get_base_dir


class LogLevel(Enum):
    """Log levels for filtering."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LogEntry:
    """Represents a single log entry."""
    
    def __init__(self, timestamp: datetime, level: LogLevel, message: str, source: str):
        self.timestamp = timestamp
        self.level = level
        self.message = message
        self.source = source
    
    def __str__(self) -> str:
        timestamp_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp_str}] [{self.level.value}] {self.source}: {self.message}"


class LogManager:
    """Manages logging for providers."""
    
    def __init__(self):
        self.data_dir = get_base_dir()
        self.logs_dir = self.data_dir / "logs"
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.max_files = 5
        self._ensure_log_directories()
    
    def _ensure_log_directories(self) -> None:
        """Create log directories if they don't exist."""
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Create provider subdirectories
        for provider in ["claude", "gemini", "copilot"]:
            provider_dir = self.logs_dir / provider
            provider_dir.mkdir(exist_ok=True)
    
    def get_provider_log_dir(self, provider: str) -> Path:
        """Get the log directory for a specific provider."""
        return self.logs_dir / provider
    
    def get_log_file_path(self, provider: str, log_type: str) -> Path:
        """Get the path to a specific log file."""
        return self.get_provider_log_dir(provider) / f"{log_type}.log"
    
    def write_log(self, provider: str, log_type: str, message: str) -> None:
        """Write a log message to the specified log file."""
        log_file = self.get_log_file_path(provider, log_type)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # Check file size and rotate if needed
            if log_file.exists() and log_file.stat().st_size > self.max_file_size:
                self._rotate_log_file(log_file)
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {message}\n")
                f.flush()
        except Exception as e:
            # Fallback to system log
            system_log = self.logs_dir / "system.log"
            with open(system_log, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] ERROR: Failed to write to {log_file}: {e}\n")
    
    def _rotate_log_file(self, log_file: Path) -> None:
        """Rotate log file when it gets too large."""
        base_name = log_file.stem
        extension = log_file.suffix
        parent_dir = log_file.parent
        
        # Remove oldest backup
        oldest_backup = parent_dir / f"{base_name}.{self.max_files}{extension}"
        if oldest_backup.exists():
            oldest_backup.unlink()
        
        # Shift existing backups
        for i in range(self.max_files - 1, 0, -1):
            old_backup = parent_dir / f"{base_name}.{i}{extension}"
            new_backup = parent_dir / f"{base_name}.{i + 1}{extension}"
            if old_backup.exists():
                old_backup.rename(new_backup)
        
        # Move current log to .1 backup
        backup_file = parent_dir / f"{base_name}.1{extension}"
        log_file.rename(backup_file)
    
    async def tail_logs(
        self, 
        provider: str, 
        log_type: str = "stdout", 
        num_lines: int = 50
    ) -> List[str]:
        """Get the last N lines from a log file."""
        log_file = self.get_log_file_path(provider, log_type)
        
        if not log_file.exists():
            return []
        
        try:
            # Read file backwards to get last N lines efficiently
            with open(log_file, "rb") as f:
                f.seek(0, 2)  # Go to end of file
                file_size = f.tell()
                
                if file_size == 0:
                    return []
                
                lines = []
                buffer = b""
                position = file_size
                
                while len(lines) < num_lines and position > 0:
                    # Read in chunks
                    chunk_size = min(4096, position)
                    position -= chunk_size
                    f.seek(position)
                    chunk = f.read(chunk_size)
                    
                    # Prepend to buffer
                    buffer = chunk + buffer
                    
                    # Split into lines
                    while b"\n" in buffer and len(lines) < num_lines:
                        line, buffer = buffer.rsplit(b"\n", 1)
                        if line:  # Skip empty lines
                            try:
                                # Split multiple entries that might be on one line
                                decoded_line = line.decode("utf-8")
                                # Look for timestamp patterns to split entries
                                import re
                                timestamp_pattern = r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]'
                                parts = re.split(f'({timestamp_pattern})', decoded_line)
                                
                                # Reconstruct entries
                                for i in range(1, len(parts), 2):
                                    if i + 1 < len(parts):
                                        entry = parts[i] + parts[i + 1]
                                        if entry.strip():
                                            lines.insert(0, entry.strip())
                                            if len(lines) >= num_lines:
                                                break
                                
                                # If no timestamp patterns found, add as single line
                                if len(parts) <= 1:
                                    lines.insert(0, decoded_line)
                                    
                            except UnicodeDecodeError:
                                lines.insert(0, line.decode("utf-8", errors="replace"))
                
                # Handle remaining buffer
                if buffer and len(lines) < num_lines:
                    try:
                        lines.insert(0, buffer.decode("utf-8"))
                    except UnicodeDecodeError:
                        lines.insert(0, buffer.decode("utf-8", errors="replace"))
                
                return lines[-num_lines:]  # Ensure we don't exceed requested count
        
        except Exception as e:
            self.write_log("system", "error", f"Failed to tail logs for {provider}: {e}")
            return []
    
    async def follow_logs(
        self, 
        provider: str, 
        log_type: str = "stdout"
    ) -> AsyncGenerator[str, None]:
        """Follow logs in real-time like 'tail -f'."""
        log_file = self.get_log_file_path(provider, log_type)
        
        # Create file if it doesn't exist
        if not log_file.exists():
            log_file.touch()
        
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                # Go to end of file
                f.seek(0, 2)
                
                while True:
                    line = f.readline()
                    if line:
                        yield line.rstrip()
                    else:
                        # Wait a bit before checking again
                        await asyncio.sleep(0.1)
        
        except Exception as e:
            self.write_log("system", "error", f"Failed to follow logs for {provider}: {e}")
            return
    
    def clear_logs(self, provider: str, log_type: Optional[str] = None) -> bool:
        """Clear logs for a provider."""
        try:
            provider_dir = self.get_provider_log_dir(provider)
            
            if log_type:
                # Clear specific log type
                log_file = self.get_log_file_path(provider, log_type)
                if log_file.exists():
                    log_file.unlink()
            else:
                # Clear all logs for provider
                for log_file in provider_dir.glob("*.log"):
                    log_file.unlink()
                    
                # Also clear backup files
                for backup_file in provider_dir.glob("*.log.*"):
                    backup_file.unlink()
            
            return True
        except Exception as e:
            self.write_log("system", "error", f"Failed to clear logs for {provider}: {e}")
            return False
    
    def get_log_stats(self, provider: str) -> Dict[str, any]:
        """Get statistics about log files for a provider."""
        provider_dir = self.get_provider_log_dir(provider)
        stats = {
            "stdout_size": 0,
            "stderr_size": 0,
            "epic_llm_size": 0,
            "total_size": 0,
            "last_modified": None,
            "files": []
        }
        
        for log_type in ["stdout", "stderr", "epic-llm"]:
            log_file = self.get_log_file_path(provider, log_type)
            if log_file.exists():
                stat = log_file.stat()
                size = stat.st_size
                stats[f"{log_type.replace('-', '_')}_size"] = size
                stats["total_size"] += size
                
                if stats["last_modified"] is None or stat.st_mtime > stats["last_modified"]:
                    stats["last_modified"] = stat.st_mtime
                
                stats["files"].append({
                    "name": log_file.name,
                    "size": size,
                    "modified": stat.st_mtime
                })
        
        return stats


class LogCapture:
    """Captures process output and writes to log files."""
    
    def __init__(self, provider: str, log_manager: LogManager):
        self.provider = provider
        self.log_manager = log_manager
        self._tasks: List[asyncio.Task] = []
    
    async def capture_output(self, process: asyncio.subprocess.Process) -> None:
        """Capture stdout and stderr from a process."""
        if process.stdout:
            stdout_task = asyncio.create_task(
                self._capture_stream(process.stdout, "stdout")
            )
            self._tasks.append(stdout_task)
        
        if process.stderr:
            stderr_task = asyncio.create_task(
                self._capture_stream(process.stderr, "stderr")
            )
            self._tasks.append(stderr_task)
    
    async def _capture_stream(self, stream: asyncio.StreamReader, log_type: str) -> None:
        """Capture output from a stream and write to log file."""
        try:
            while True:
                line = await stream.readline()
                if not line:
                    break
                
                # Decode and clean the line
                try:
                    text = line.decode("utf-8").rstrip()
                except UnicodeDecodeError:
                    text = line.decode("utf-8", errors="replace").rstrip()
                
                if text:
                    # Filter out sensitive information
                    filtered_text = self._filter_sensitive_content(text)
                    self.log_manager.write_log(self.provider, log_type, filtered_text)
        
        except Exception as e:
            self.log_manager.write_log(
                "system", 
                "error", 
                f"Error capturing {log_type} for {self.provider}: {e}"
            )
    
    def _filter_sensitive_content(self, text: str) -> str:
        """Filter out sensitive information from log content."""
        # Remove potential API keys (long alphanumeric strings)
        import re
        
        # Pattern for potential API keys (20+ characters, alphanumeric with dashes/underscores)
        api_key_pattern = r'\b[A-Za-z0-9_-]{20,}\b'
        filtered = re.sub(api_key_pattern, lambda m: m.group()[:8] + "..." + m.group()[-4:] if len(m.group()) > 12 else "[FILTERED]", text)
        
        # Remove authorization headers - improved pattern
        auth_pattern = r'(?i)(authorization|bearer|token)[\s:=]+([A-Za-z0-9_-]+)'
        filtered = re.sub(auth_pattern, r'\1: [FILTERED]', filtered)
        
        return filtered
    
    def stop_capture(self) -> None:
        """Stop all capture tasks."""
        for task in self._tasks:
            if not task.done():
                task.cancel()
        self._tasks.clear()