"""Tests for providers module initialization."""

import pytest

from epic_llm.providers import PROVIDERS
from epic_llm.providers.claude import ClaudeProvider
from epic_llm.providers.copilot import CopilotProvider
from epic_llm.providers.gemini import GeminiProvider


class TestProvidersModule:
    """Test providers module initialization and exports."""

    def test_providers_dict_exists(self):
        """Test that PROVIDERS dictionary exists."""
        assert PROVIDERS is not None
        assert isinstance(PROVIDERS, dict)

    def test_providers_dict_contains_expected_providers(self):
        """Test that PROVIDERS contains expected provider classes."""
        expected_providers = ["claude", "copilot", "gemini"]

        for provider_name in expected_providers:
            assert provider_name in PROVIDERS
            assert PROVIDERS[provider_name] is not None

    def test_claude_provider_in_providers(self):
        """Test that Claude provider is correctly mapped."""
        assert "claude" in PROVIDERS
        assert PROVIDERS["claude"] == ClaudeProvider

    def test_copilot_provider_in_providers(self):
        """Test that Copilot provider is correctly mapped."""
        assert "copilot" in PROVIDERS
        assert PROVIDERS["copilot"] == CopilotProvider

    def test_gemini_provider_in_providers(self):
        """Test that Gemini provider is correctly mapped."""
        assert "gemini" in PROVIDERS
        assert PROVIDERS["gemini"] == GeminiProvider

    def test_providers_are_classes(self):
        """Test that all providers in PROVIDERS are classes."""
        for provider_name, provider_class in PROVIDERS.items():
            assert callable(provider_class)
            # Check if it's a class (has __name__ attribute)
            assert hasattr(provider_class, "__name__")

    def test_providers_dict_is_immutable_reference(self):
        """Test that PROVIDERS dict reference is stable."""
        providers_ref = PROVIDERS
        # Import again to ensure same reference
        from epic_llm.providers import PROVIDERS as providers_ref2

        assert providers_ref is providers_ref2

    def test_provider_classes_can_be_instantiated(self, temp_dir):
        """Test that provider classes can be instantiated."""
        for provider_name, provider_class in PROVIDERS.items():
            # Create instance with test parameters
            install_dir = temp_dir / f"{provider_name}_test"

            # Each provider should accept install_dir parameter
            instance = provider_class(install_dir=install_dir)

            assert instance is not None
            assert instance.name == provider_name
            assert instance.install_dir == install_dir

    def test_provider_classes_inherit_from_base(self):
        """Test that all provider classes inherit from BaseProvider."""
        from epic_llm.providers.base import BaseProvider

        for provider_name, provider_class in PROVIDERS.items():
            # Check inheritance
            assert issubclass(provider_class, BaseProvider)

    def test_providers_dict_contains_only_expected_keys(self):
        """Test that PROVIDERS doesn't contain unexpected providers."""
        expected_providers = {"claude", "copilot", "gemini"}
        actual_providers = set(PROVIDERS.keys())

        assert actual_providers == expected_providers

    def test_providers_dict_size(self):
        """Test that PROVIDERS has the expected number of providers."""
        assert len(PROVIDERS) == 3

    def test_provider_names_are_strings(self):
        """Test that all provider names are strings."""
        for provider_name in PROVIDERS.keys():
            assert isinstance(provider_name, str)
            assert len(provider_name) > 0

    def test_provider_names_are_lowercase(self):
        """Test that all provider names are lowercase."""
        for provider_name in PROVIDERS.keys():
            assert provider_name.islower()

    def test_providers_module_imports(self):
        """Test that provider module imports work correctly."""
        # Test that we can import all providers directly
        try:
            from epic_llm.providers import PROVIDERS
            from epic_llm.providers.claude import ClaudeProvider
            from epic_llm.providers.copilot import CopilotProvider
            from epic_llm.providers.gemini import GeminiProvider
        except ImportError as e:
            pytest.fail(f"Failed to import providers: {e}")

    def test_provider_classes_have_required_methods(self, temp_dir):
        """Test that provider classes implement required abstract methods."""
        required_methods = [
            "get_dependencies",
            "install",
            "start",
            "stop",
            "health_check",
        ]

        for provider_name, provider_class in PROVIDERS.items():
            install_dir = temp_dir / f"{provider_name}_test"
            instance = provider_class(install_dir=install_dir)

            for method_name in required_methods:
                assert hasattr(instance, method_name)
                assert callable(getattr(instance, method_name))
