"""Integration tests for status command with quota display (Story 5.4)."""
import pytest
from typer.testing import CliRunner
from unittest.mock import patch, AsyncMock, MagicMock
from eleven_video.main import app
from eleven_video.models.quota import QuotaInfo
from eleven_video.api.interfaces import HealthResult, UsageResult

runner = CliRunner()


def test_status_command_shows_quota():
    """Verifies that 'status' command fetches and displays quota info."""
    
    # Mock quota info objects
    mock_quota_11labs = QuotaInfo(
        service="ElevenLabs", used=500, limit=1000, unit="chars", reset_date=None
    )
    mock_quota_gemini = QuotaInfo(
        service="Gemini", used=None, limit=15, unit="rpm", reset_date=None
    )
    
    # Mock health and usage results
    mock_health = HealthResult(status="ok", message="Connected", latency_ms=100.0)
    mock_usage = UsageResult(available=True, used=500, limit=1000, unit="chars", raw_data=None)
    
    # Mock the Settings to avoid needing real API keys
    with patch('eleven_video.main.Settings') as mock_settings_cls:
        mock_settings = MagicMock()
        mock_settings.elevenlabs_api_key.get_secret_value.return_value = "fake-eleven-key"
        mock_settings.gemini_api_key.get_secret_value.return_value = "fake-gemini-key"
        mock_settings_cls.return_value = mock_settings
        
        # Mock the adapters
        with patch('eleven_video.main.ElevenLabsAdapter') as mock_eleven_cls, \
             patch('eleven_video.main.GeminiAdapter') as mock_gemini_cls:
            
            # ElevenLabs adapter mock
            mock_eleven = AsyncMock()
            mock_eleven.service_name = "ElevenLabs"
            mock_eleven.check_health = AsyncMock(return_value=mock_health)
            mock_eleven.get_usage = AsyncMock(return_value=mock_usage)
            mock_eleven.get_quota_info = AsyncMock(return_value=mock_quota_11labs)
            mock_eleven.close = AsyncMock()
            mock_eleven_cls.return_value = mock_eleven
            
            # Gemini adapter mock
            mock_gemini = AsyncMock()
            mock_gemini.service_name = "Google Gemini"
            mock_gemini.check_health = AsyncMock(return_value=mock_health)
            mock_gemini.get_usage = AsyncMock(return_value=UsageResult(
                available=False, used=None, limit=None, unit=None, raw_data=None
            ))
            mock_gemini.get_quota_info = AsyncMock(return_value=mock_quota_gemini)
            mock_gemini.close = AsyncMock()
            mock_gemini_cls.return_value = mock_gemini
            
            # Invoke command
            result = runner.invoke(app, ["status"])
            
            # Verify exit code
            assert result.exit_code == 0, f"Command failed: {result.stdout}"
            
            # Verify quota info appears in output (AC #1, #2)
            assert "ElevenLabs" in result.stdout
            assert "Gemini" in result.stdout
            assert "API Quota Status" in result.stdout  # Table title
            
            # Verify adapters were called
            mock_eleven.get_quota_info.assert_called_once()
            mock_gemini.get_quota_info.assert_called_once()
