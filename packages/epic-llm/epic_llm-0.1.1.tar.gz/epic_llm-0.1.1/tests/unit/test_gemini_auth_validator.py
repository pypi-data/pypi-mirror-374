"""Tests for Gemini authentication validator."""

import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from epic_llm.managers.state import AuthStatus
from epic_llm.utils.auth_validator import GeminiAuthValidator


class TestGeminiAuthValidatorBasic:
    """Test basic GeminiAuthValidator functionality."""

    def test_validator_initialization(self):
        """Test basic validator initialization."""
        install_dir = Path("/tmp/gemini")
        validator = GeminiAuthValidator(install_dir)

        assert validator.install_dir == install_dir
        assert validator.oauth_file == install_dir / "oauth_creds.json"

    @pytest.mark.asyncio
    async def test_validate_credentials_no_file(self):
        """Test validation when OAuth file doesn't exist."""
        install_dir = Path("/tmp/gemini")
        validator = GeminiAuthValidator(install_dir)

        with patch("pathlib.Path.exists", return_value=False):
            status = await validator.validate_credentials()
            assert status == AuthStatus.REQUIRED

    @pytest.mark.asyncio
    async def test_validate_credentials_invalid_json(self):
        """Test validation with invalid JSON file."""
        install_dir = Path("/tmp/gemini")
        validator = GeminiAuthValidator(install_dir)

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="invalid json")):
                status = await validator.validate_credentials()
                assert status == AuthStatus.FAILED

    @pytest.mark.asyncio
    async def test_validate_credentials_missing_fields(self):
        """Test validation with missing required fields."""
        install_dir = Path("/tmp/gemini")
        validator = GeminiAuthValidator(install_dir)

        invalid_creds = {"some_field": "value"}

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=json.dumps(invalid_creds))):
                status = await validator.validate_credentials()
                assert status == AuthStatus.REQUIRED

    @pytest.mark.asyncio
    async def test_validate_credentials_token_test_fails(self):
        """Test validation when token test fails."""
        install_dir = Path("/tmp/gemini")
        validator = GeminiAuthValidator(install_dir)

        valid_creds = {"refresh_token": "invalid_refresh_token"}

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=json.dumps(valid_creds))):
                with patch.object(validator, "_test_refresh_token", return_value=False):
                    status = await validator.validate_credentials()
                    assert status == AuthStatus.FAILED

    @pytest.mark.asyncio
    async def test_validate_credentials_file_permission_error(self):
        """Test validation with file permission error."""
        install_dir = Path("/tmp/gemini")
        validator = GeminiAuthValidator(install_dir)

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", side_effect=PermissionError()):
                status = await validator.validate_credentials()
                assert status == AuthStatus.FAILED

    def test_validate_required_fields_success(self):
        """Test successful field validation."""
        install_dir = Path("/tmp/gemini")
        validator = GeminiAuthValidator(install_dir)

        valid_data = {
            "refresh_token": "valid_token",
            "client_id": "test_client_id",
            "client_secret": "test_secret",
        }

        result = validator._validate_required_fields(valid_data)
        assert result is True

    def test_validate_required_fields_missing(self):
        """Test field validation with missing refresh token."""
        install_dir = Path("/tmp/gemini")
        validator = GeminiAuthValidator(install_dir)

        invalid_data = {"client_id": "test_client_id"}

        result = validator._validate_required_fields(invalid_data)
        assert result is False

    def test_validate_required_fields_empty_values(self):
        """Test field validation with empty values."""
        install_dir = Path("/tmp/gemini")
        validator = GeminiAuthValidator(install_dir)

        invalid_data = {"refresh_token": ""}

        result = validator._validate_required_fields(invalid_data)
        assert result is False

    def test_validate_required_fields_none_values(self):
        """Test field validation with None values."""
        install_dir = Path("/tmp/gemini")
        validator = GeminiAuthValidator(install_dir)

        invalid_data = {"refresh_token": None}

        result = validator._validate_required_fields(invalid_data)
        assert result is False

    def test_validate_required_fields_missing_client_creds(self):
        """Test field validation with missing client credentials (should pass)."""
        install_dir = Path("/tmp/gemini")
        validator = GeminiAuthValidator(install_dir)

        # Missing client_id and client_secret should still pass
        # because defaults will be used
        data = {"refresh_token": "valid_token"}

        result = validator._validate_required_fields(data)
        assert result is True

    @pytest.mark.asyncio
    async def test_test_refresh_token_no_token(self):
        """Test refresh token validation with missing token."""
        install_dir = Path("/tmp/gemini")
        validator = GeminiAuthValidator(install_dir)

        creds_data = {}

        result = await validator._test_refresh_token(creds_data)
        assert result is False

    @pytest.mark.asyncio
    async def test_test_refresh_token_network_error(self):
        """Test refresh token validation with network error."""
        install_dir = Path("/tmp/gemini")
        validator = GeminiAuthValidator(install_dir)

        creds_data = {"refresh_token": "valid_refresh_token"}

        with patch("httpx.AsyncClient", side_effect=Exception("Network error")):
            result = await validator._test_refresh_token(creds_data)
            assert result is False

    def test_get_credential_info_no_file(self):
        """Test credential info when file doesn't exist."""
        install_dir = Path("/tmp/gemini")
        validator = GeminiAuthValidator(install_dir)

        with patch("pathlib.Path.exists", return_value=False):
            info = validator.get_credential_info()
            assert info is None

    def test_get_credential_info_with_file(self):
        """Test credential info with valid file."""
        install_dir = Path("/tmp/gemini")
        validator = GeminiAuthValidator(install_dir)

        creds_data = {
            "refresh_token": "test_refresh_token",
            "access_token": "test_access_token",
            "project_id": "test-project",
            "scopes": ["scope1", "scope2"],
            "expiry": "2024-12-31T23:59:59Z",
        }

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=json.dumps(creds_data))):
                info = validator.get_credential_info()

                assert info is not None
                assert info["has_refresh_token"] is True
                assert info["has_access_token"] is True
                assert info["project_id"] == "test-project"
                assert info["scopes"] == ["scope1", "scope2"]
                assert info["expires_at"] is not None
                assert isinstance(info["is_expired"], bool)

    def test_get_credential_info_invalid_json(self):
        """Test credential info with invalid JSON."""
        install_dir = Path("/tmp/gemini")
        validator = GeminiAuthValidator(install_dir)

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="invalid json")):
                info = validator.get_credential_info()
                assert info is None

    def test_get_credential_info_incomplete_data(self):
        """Test credential info with incomplete data."""
        install_dir = Path("/tmp/gemini")
        validator = GeminiAuthValidator(install_dir)

        creds_data = {"some_field": "value"}

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=json.dumps(creds_data))):
                info = validator.get_credential_info()

                assert info is not None
                assert info["has_refresh_token"] is False
                assert info["has_access_token"] is False
                assert info["project_id"] is None
                assert info["scopes"] == []
                assert info["expires_at"] is None
                assert info["is_expired"] is None

    def test_get_credential_info_with_token_field(self):
        """Test credential info with 'token' field instead of 'access_token'."""
        install_dir = Path("/tmp/gemini")
        validator = GeminiAuthValidator(install_dir)

        creds_data = {"token": "test_token"}

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=json.dumps(creds_data))):
                info = validator.get_credential_info()

                assert info is not None
                assert info["has_access_token"] is True

    def test_get_credential_info_expiry_parsing_error(self):
        """Test credential info with invalid expiry format."""
        install_dir = Path("/tmp/gemini")
        validator = GeminiAuthValidator(install_dir)

        creds_data = {"expiry": "invalid-date-format"}

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=json.dumps(creds_data))):
                info = validator.get_credential_info()

                assert info is not None
                assert info["expires_at"] is None
                assert info["is_expired"] is None

    def test_get_credential_info_expiry_without_z(self):
        """Test credential info with expiry format without Z suffix."""
        install_dir = Path("/tmp/gemini")
        validator = GeminiAuthValidator(install_dir)

        creds_data = {"expiry": "2024-12-31T23:59:59+00:00"}

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=json.dumps(creds_data))):
                info = validator.get_credential_info()

                assert info is not None
                assert info["expires_at"] is not None
                assert isinstance(info["is_expired"], bool)

    def test_credential_info_workflow(self):
        """Test credential info retrieval workflow."""
        install_dir = Path("/tmp/gemini")
        validator = GeminiAuthValidator(install_dir)

        creds_data = {
            "refresh_token": "test_refresh_token",
            "access_token": "test_access_token",
            "project_id": "test-project-123",
            "scopes": ["https://www.googleapis.com/auth/generative-language"],
            "expiry": "2025-12-31T23:59:59Z",
        }

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=json.dumps(creds_data))):
                info = validator.get_credential_info()

                assert info is not None
                assert info["has_refresh_token"] is True
                assert info["has_access_token"] is True
                assert info["project_id"] == "test-project-123"
                assert len(info["scopes"]) == 1

    @pytest.mark.asyncio
    async def test_error_resilience(self):
        """Test error handling in various scenarios."""
        install_dir = Path("/tmp/gemini")
        validator = GeminiAuthValidator(install_dir)

        # Test various error conditions
        error_scenarios = [
            (FileNotFoundError(), AuthStatus.FAILED),
            (PermissionError(), AuthStatus.FAILED),
            (json.JSONDecodeError("Invalid JSON", "", 0), AuthStatus.FAILED),
        ]

        for exception, expected_status in error_scenarios:
            with patch("pathlib.Path.exists", return_value=True):
                with patch("builtins.open", side_effect=exception):
                    status = await validator.validate_credentials()
                    assert status == expected_status
