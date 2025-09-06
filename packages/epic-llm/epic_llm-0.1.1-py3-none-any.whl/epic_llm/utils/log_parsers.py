"""Provider-specific log parsers for extracting metrics and events."""

import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class TokenUsage:
    """Token usage information."""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    timestamp: Optional[datetime] = None


@dataclass
class ApiRequest:
    """API request information."""
    method: str
    endpoint: str
    status_code: Optional[int] = None
    response_time: Optional[float] = None
    timestamp: Optional[datetime] = None


@dataclass
class LogEvent:
    """Generic log event."""
    event_type: str
    message: str
    level: str = "INFO"
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseLogParser:
    """Base class for provider-specific log parsers."""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
    
    def parse_line(self, line: str) -> Optional[LogEvent]:
        """Parse a single line and extract structured information."""
        # Default implementation for unknown providers
        return LogEvent(
            event_type="general",
            message=line.strip()
        )
    
    def extract_token_usage(self, line: str) -> Optional[TokenUsage]:
        """Extract token usage information from a log line."""
        return None
    
    def extract_api_request(self, line: str) -> Optional[ApiRequest]:
        """Extract API request information from a log line."""
        return None
    
    def extract_error(self, line: str) -> Optional[LogEvent]:
        """Extract error information from a log line."""
        return None
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse timestamp from various formats."""
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S.%f",
            "%m/%d/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        return None


class ClaudeLogParser(BaseLogParser):
    """Parser for Claude provider logs."""
    
    def __init__(self):
        super().__init__("claude")
        
        # Claude-specific patterns
        self.token_pattern = re.compile(
            r'(?i)tokens?[:\s]+(?:input[:\s]+(\d+)[,\s]*)?(?:output[:\s]+(\d+)[,\s]*)?(?:total[:\s]+(\d+))?'
        )
        self.api_request_pattern = re.compile(
            r'(?P<method>GET|POST|PUT|DELETE|PATCH)\s+(?P<endpoint>/[^\s]*)\s+(?P<status>\d{3})?'
        )
        self.error_pattern = re.compile(
            r'(?i)(error|exception|failed|failure)[:\s]*(.*?)$'
        )
        self.auth_pattern = re.compile(
            r'(?i)(auth|login|credential|token)[:\s]*(.*?)$'
        )
    
    def parse_line(self, line: str) -> Optional[LogEvent]:
        """Parse a Claude log line."""
        # Try to extract timestamp
        timestamp_match = re.match(r'^\[([^\]]+)\]', line)
        timestamp = None
        if timestamp_match:
            timestamp = self._parse_timestamp(timestamp_match.group(1))
        
        # Check for different types of events
        
        # Token usage
        token_usage = self.extract_token_usage(line)
        if token_usage:
            return LogEvent(
                event_type="token_usage",
                message=line.strip(),
                timestamp=timestamp,
                metadata={"token_usage": token_usage}
            )
        
        # API requests
        api_request = self.extract_api_request(line)
        if api_request:
            return LogEvent(
                event_type="api_request",
                message=line.strip(),
                timestamp=timestamp,
                metadata={"api_request": api_request}
            )
        
        # Errors
        error_event = self.extract_error(line)
        if error_event:
            return error_event
        
        # Authentication events
        auth_match = self.auth_pattern.search(line)
        if auth_match:
            return LogEvent(
                event_type="authentication",
                message=line.strip(),
                timestamp=timestamp,
                metadata={"auth_type": auth_match.group(1)}
            )
        
        # Default generic event
        return LogEvent(
            event_type="general",
            message=line.strip(),
            timestamp=timestamp
        )
    
    def extract_token_usage(self, line: str) -> Optional[TokenUsage]:
        """Extract token usage from Claude logs."""
        match = self.token_pattern.search(line)
        if match:
            input_tokens = int(match.group(1)) if match.group(1) else 0
            output_tokens = int(match.group(2)) if match.group(2) else 0
            total_tokens = int(match.group(3)) if match.group(3) else input_tokens + output_tokens
            
            return TokenUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens
            )
        return None
    
    def extract_api_request(self, line: str) -> Optional[ApiRequest]:
        """Extract API request information from Claude logs."""
        match = self.api_request_pattern.search(line)
        if match:
            return ApiRequest(
                method=match.group("method"),
                endpoint=match.group("endpoint"),
                status_code=int(match.group("status")) if match.group("status") else None
            )
        return None
    
    def extract_error(self, line: str) -> Optional[LogEvent]:
        """Extract error information from Claude logs."""
        match = self.error_pattern.search(line)
        if match:
            return LogEvent(
                event_type="error",
                message=line.strip(),
                level="ERROR",
                metadata={"error_details": match.group(2)}
            )
        return None


class GeminiLogParser(BaseLogParser):
    """Parser for Gemini provider logs."""
    
    def __init__(self):
        super().__init__("gemini")
        
        # Gemini-specific patterns
        self.oauth_pattern = re.compile(
            r'(?i)(oauth|authorization|refresh|token)[:\s]*(.*?)$'
        )
        self.api_pattern = re.compile(
            r'(?i)(api|request|response)[:\s]*(.*?)$'
        )
        self.error_pattern = re.compile(
            r'(?i)(error|exception|failed|failure)[:\s]*(.*?)$'
        )
    
    def parse_line(self, line: str) -> Optional[LogEvent]:
        """Parse a Gemini log line."""
        # Try to extract timestamp
        timestamp_match = re.match(r'^\[([^\]]+)\]', line)
        timestamp = None
        if timestamp_match:
            timestamp = self._parse_timestamp(timestamp_match.group(1))
        
        # OAuth events
        oauth_match = self.oauth_pattern.search(line)
        if oauth_match:
            return LogEvent(
                event_type="oauth",
                message=line.strip(),
                timestamp=timestamp,
                metadata={"oauth_stage": oauth_match.group(1)}
            )
        
        # API events
        api_match = self.api_pattern.search(line)
        if api_match:
            return LogEvent(
                event_type="api",
                message=line.strip(),
                timestamp=timestamp,
                metadata={"api_details": api_match.group(2)}
            )
        
        # Errors
        error_event = self.extract_error(line)
        if error_event:
            return error_event
        
        # Default generic event
        return LogEvent(
            event_type="general",
            message=line.strip(),
            timestamp=timestamp
        )
    
    def extract_error(self, line: str) -> Optional[LogEvent]:
        """Extract error information from Gemini logs."""
        match = self.error_pattern.search(line)
        if match:
            return LogEvent(
                event_type="error",
                message=line.strip(),
                level="ERROR",
                metadata={"error_details": match.group(2)}
            )
        return None


class CopilotLogParser(BaseLogParser):
    """Parser for Copilot provider logs."""
    
    def __init__(self):
        super().__init__("copilot")
        
        # Copilot-specific patterns
        self.github_api_pattern = re.compile(
            r'(?i)(github|api).*?(?P<method>GET|POST|PUT|DELETE|PATCH).*?(?P<endpoint>/[^\s]*)'
        )
        self.completion_pattern = re.compile(
            r'(?i)(completion|suggestion|code)[:\s]*(.*?)$'
        )
        self.error_pattern = re.compile(
            r'(?i)(error|exception|failed|failure)[:\s]*(.*?)$'
        )
        self.request_pattern = re.compile(
            r'(?P<method>GET|POST|PUT|DELETE|PATCH)\s+(?P<endpoint>/[^\s]*)\s+(?P<status>\d{3})?'
        )
    
    def parse_line(self, line: str) -> Optional[LogEvent]:
        """Parse a Copilot log line."""
        # Try to extract timestamp
        timestamp_match = re.match(r'^\[([^\]]+)\]', line)
        timestamp = None
        if timestamp_match:
            timestamp = self._parse_timestamp(timestamp_match.group(1))
        
        # GitHub API requests
        github_match = self.github_api_pattern.search(line)
        if github_match:
            return LogEvent(
                event_type="github_api",
                message=line.strip(),
                timestamp=timestamp,
                metadata={
                    "method": github_match.group("method") if "method" in github_match.groupdict() else None,
                    "endpoint": github_match.group("endpoint") if "endpoint" in github_match.groupdict() else None
                }
            )
        
        # Code completion events
        completion_match = self.completion_pattern.search(line)
        if completion_match:
            return LogEvent(
                event_type="completion",
                message=line.strip(),
                timestamp=timestamp,
                metadata={"completion_details": completion_match.group(2)}
            )
        
        # API requests
        api_request = self.extract_api_request(line)
        if api_request:
            return LogEvent(
                event_type="api_request",
                message=line.strip(),
                timestamp=timestamp,
                metadata={"api_request": api_request}
            )
        
        # Errors
        error_event = self.extract_error(line)
        if error_event:
            return error_event
        
        # Default generic event
        return LogEvent(
            event_type="general",
            message=line.strip(),
            timestamp=timestamp
        )
    
    def extract_api_request(self, line: str) -> Optional[ApiRequest]:
        """Extract API request information from Copilot logs."""
        match = self.request_pattern.search(line)
        if match:
            return ApiRequest(
                method=match.group("method"),
                endpoint=match.group("endpoint"),
                status_code=int(match.group("status")) if match.group("status") else None
            )
        return None
    
    def extract_error(self, line: str) -> Optional[LogEvent]:
        """Extract error information from Copilot logs."""
        match = self.error_pattern.search(line)
        if match:
            return LogEvent(
                event_type="error",
                message=line.strip(),
                level="ERROR",
                metadata={"error_details": match.group(2)}
            )
        return None


class LogParserFactory:
    """Factory for creating provider-specific log parsers."""
    
    _parsers = {
        "claude": ClaudeLogParser,
        "gemini": GeminiLogParser,
        "copilot": CopilotLogParser,
    }
    
    @classmethod
    def get_parser(cls, provider: str) -> BaseLogParser:
        """Get the appropriate parser for a provider."""
        parser_class = cls._parsers.get(provider.lower())
        if parser_class:
            return parser_class()
        
        # Return a generic parser for unknown providers
        return BaseLogParser(provider)
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of providers with specialized parsers."""
        return list(cls._parsers.keys())