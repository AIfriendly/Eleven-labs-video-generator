"""
Tests for the status command.

Test IDs: 1.5-INT-001 to 1.5-INT-007
Tests cover AC1-6 for status command UI.
"""
import pytest
from typer.testing import CliRunner
from unittest.mock import AsyncMock, patch, MagicMock, PropertyMock
import json


runner = CliRunner()


class TestStatusCommandBasic:
    """Basic tests for status command existence and structure."""

    def test_status_command_exists(self):
        """[1.5-INT-001] AC1: status command should be registered."""
        # Given: The main CLI app
        from eleven_video.main import app
        
        # When: Checking registered commands
        command_names = [cmd.name or cmd.callback.__name__ for cmd in app.registered_commands]
        
        # Then: status should be in the list
        assert "status" in command_names

    def test_status_command_has_json_flag(self):
        """[1.5-INT-002] AC5: status command should accept --json flag."""
        # Given: The status command help output
        from eleven_video.main import app
        
        # When: Invoking status --help
        result = runner.invoke(app, ["status", "--help"])
        
        # Then: --json flag should be documented
        assert "--json" in result.output


def _create_mock_settings():
    """Create a mock settings object with API keys."""
    mock_settings = MagicMock()
    mock_settings.elevenlabs_api_key.get_secret_value.return_value = "test-eleven-key"
    mock_settings.gemini_api_key.get_secret_value.return_value = "test-gemini-key"
    return mock_settings


def _create_mock_adapter(service_name, health_result, usage_result):
    """Create a mock adapter with predefined health and usage results."""
    from eleven_video.models.quota import QuotaInfo
    mock_adapter = MagicMock()
    mock_adapter.service_name = service_name
    mock_adapter.check_health = AsyncMock(return_value=health_result)
    mock_adapter.get_usage = AsyncMock(return_value=usage_result)
    # Story 5.4: Add get_quota_info mock
    mock_adapter.get_quota_info = AsyncMock(return_value=QuotaInfo(
        service=service_name,
        used=usage_result.used,
        limit=usage_result.limit,
        unit=usage_result.unit or "chars",
        reset_date=None
    ))
    mock_adapter.close = AsyncMock()
    return mock_adapter


class TestStatusCommandOutput:
    """Tests for status command output formatting."""

    def test_status_shows_service_statuses(self):
        """[1.5-INT-003] AC1: status shows connectivity status of both APIs."""
        # Given: Mock adapters returning healthy status
        from eleven_video.main import app
        from eleven_video.api.interfaces import HealthResult, UsageResult
        
        mock_health_ok = HealthResult(status="ok", message="Connected", latency_ms=50.0)
        mock_usage_eleven = UsageResult(available=True, used=1000, limit=10000, unit="characters", raw_data={})
        mock_usage_gemini = UsageResult(available=False, used=None, limit=None, unit=None, raw_data=None)
        
        mock_eleven = _create_mock_adapter("ElevenLabs", mock_health_ok, mock_usage_eleven)
        mock_gemini = _create_mock_adapter("Google Gemini", mock_health_ok, mock_usage_gemini)
        
        # When: status command is invoked
        with patch("eleven_video.main.Settings", return_value=_create_mock_settings()), \
             patch("eleven_video.main.ElevenLabsAdapter", return_value=mock_eleven), \
             patch("eleven_video.main.GeminiAdapter", return_value=mock_gemini):
            
            result = runner.invoke(app, ["status"])
        
        # Then: Both services should appear in output
        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "ElevenLabs" in result.output
        assert "Google Gemini" in result.output

    def test_status_displays_usage_quota(self):
        """[1.5-INT-004] AC2: status shows usage/quota for ElevenLabs."""
        # Given: ElevenLabs adapter with usage data
        from eleven_video.main import app
        from eleven_video.api.interfaces import HealthResult, UsageResult
        
        mock_health_ok = HealthResult(status="ok", message="Connected", latency_ms=50.0)
        mock_usage = UsageResult(available=True, used=2500, limit=10000, unit="characters", raw_data={})
        mock_usage_gemini = UsageResult(available=False, used=None, limit=None, unit=None, raw_data=None)
        
        mock_eleven = _create_mock_adapter("ElevenLabs", mock_health_ok, mock_usage)
        mock_gemini = _create_mock_adapter("Google Gemini", mock_health_ok, mock_usage_gemini)
        
        # When: status command is invoked
        with patch("eleven_video.main.Settings", return_value=_create_mock_settings()), \
             patch("eleven_video.main.ElevenLabsAdapter", return_value=mock_eleven), \
             patch("eleven_video.main.GeminiAdapter", return_value=mock_gemini):
            
            result = runner.invoke(app, ["status"])
        
        # Then: Character usage should appear in output
        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "2,500" in result.output or "2500" in result.output
        assert "10,000" in result.output or "10000" in result.output


class TestStatusCommandErrors:
    """Tests for error handling in status command."""

    def test_status_shows_error_for_invalid_credentials(self):
        """[1.5-INT-005] AC3: clear error message for invalid credentials."""
        # Given: Adapters returning auth errors
        from eleven_video.main import app
        from eleven_video.api.interfaces import HealthResult, UsageResult
        
        mock_health_error = HealthResult(status="error", message="Authentication failed (401)", latency_ms=50.0)
        mock_usage = UsageResult(available=False, used=None, limit=None, unit=None, raw_data=None)
        
        mock_eleven = _create_mock_adapter("ElevenLabs", mock_health_error, mock_usage)
        mock_gemini = _create_mock_adapter("Google Gemini", mock_health_error, mock_usage)
        
        # When: status command is invoked with bad credentials
        with patch("eleven_video.main.Settings", return_value=_create_mock_settings()), \
             patch("eleven_video.main.ElevenLabsAdapter", return_value=mock_eleven), \
             patch("eleven_video.main.GeminiAdapter", return_value=mock_gemini):
            
            result = runner.invoke(app, ["status"])
        
        # Then: Error status should appear
        assert "Error" in result.output or "❌" in result.output

    def test_status_graceful_degradation(self):
        """[1.5-INT-006] AC6: partial results when one API fails."""
        # Given: ElevenLabs succeeds but Gemini fails
        from eleven_video.main import app
        from eleven_video.api.interfaces import HealthResult, UsageResult
        
        mock_health_ok = HealthResult(status="ok", message="Connected", latency_ms=50.0)
        mock_health_error = HealthResult(status="error", message="Connection failed", latency_ms=None)
        mock_usage_ok = UsageResult(available=True, used=1000, limit=10000, unit="characters", raw_data={})
        mock_usage_err = UsageResult(available=False, used=None, limit=None, unit=None, raw_data=None)
        
        mock_eleven = _create_mock_adapter("ElevenLabs", mock_health_ok, mock_usage_ok)
        mock_gemini = _create_mock_adapter("Google Gemini", mock_health_error, mock_usage_err)
        
        # When: status command is invoked
        with patch("eleven_video.main.Settings", return_value=_create_mock_settings()), \
             patch("eleven_video.main.ElevenLabsAdapter", return_value=mock_eleven), \
             patch("eleven_video.main.GeminiAdapter", return_value=mock_gemini):
            
            result = runner.invoke(app, ["status"])
        
        # Then: Both services should appear with different states
        assert result.exit_code == 0
        assert "ElevenLabs" in result.output
        assert "Google Gemini" in result.output


class TestStatusJsonOutput:
    """Tests for JSON output mode."""

    def test_status_json_output_structure(self):
        """[1.5-INT-007] AC5: --json flag returns valid JSON."""
        # Given: Mock adapters returning healthy status
        from eleven_video.main import app
        from eleven_video.api.interfaces import HealthResult, UsageResult
        
        mock_health_ok = HealthResult(status="ok", message="Connected", latency_ms=50.0)
        mock_usage_eleven = UsageResult(available=True, used=1000, limit=10000, unit="characters", raw_data={})
        mock_usage_gemini = UsageResult(available=False, used=None, limit=None, unit=None, raw_data=None)
        
        mock_eleven = _create_mock_adapter("ElevenLabs", mock_health_ok, mock_usage_eleven)
        mock_gemini = _create_mock_adapter("Google Gemini", mock_health_ok, mock_usage_gemini)
        
        # When: status --json is invoked
        with patch("eleven_video.main.Settings", return_value=_create_mock_settings()), \
             patch("eleven_video.main.ElevenLabsAdapter", return_value=mock_eleven), \
             patch("eleven_video.main.GeminiAdapter", return_value=mock_gemini):
            
            result = runner.invoke(app, ["status", "--json"])
        
        # Then: Output should be valid JSON with services array
        assert result.exit_code == 0, f"Command failed: {result.output}"
        data = json.loads(result.output)
        assert "services" in data
        assert len(data["services"]) == 2
