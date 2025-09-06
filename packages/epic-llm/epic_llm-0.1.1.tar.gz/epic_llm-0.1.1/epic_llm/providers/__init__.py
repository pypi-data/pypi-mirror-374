"""Provider registry."""

from .claude import ClaudeProvider
from .copilot import CopilotProvider
from .gemini import GeminiProvider

__all__ = ["ClaudeProvider", "CopilotProvider", "GeminiProvider"]

PROVIDERS = {
    "claude": ClaudeProvider,
    "copilot": CopilotProvider,
    "gemini": GeminiProvider,
}
