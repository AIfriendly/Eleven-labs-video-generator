"""Integration tests for partial quota fetch failure (Story 5.4 - Test Automation Expansion).

Tests AC #4: Graceful failure when one service fails to fetch quota info.
Priority: P1
"""
import pytest
from typer.testing import CliRunner
from unittest.mock import patch, AsyncMock, MagicMock
from eleven_video.main import app
from eleven_video.models.quota import QuotaInfo
from eleven_video.api.interfaces import HealthResult, UsageResult

runner = CliRunner()


# =============================================================================
# Fixtures - Extracted from test methods per Test Review recommendation
# =============================================================================


@pytest.fixture
def mock_health_ok():
    """Standard healthy connection result."""
    return HealthResult(status="ok", message="Connected", latency_ms=100.0)


@pytest.fixture
def mock_usage_ok():
    """ElevenLabs usage with available data."""
    return UsageResult(
        available=True, used=500, limit=1000, unit="chars", raw_data=None
    )


@pytest.fixture
def mock_usage_unavailable():
    """Usage result when data is unavailable."""
    return UsageResult(
        available=False, used=None, limit=None, unit=None, raw_data=None
    )


@pytest.fixture
def mock_settings():
    """Mock Settings with fake API keys."""
    settings = MagicMock()
    settings.elevenlabs_api_key.get_secret_value.return_value = "fake-key"
    settings.gemini_api_key.get_secret_value.return_value = "fake-key"
    return settings


def create_mock_adapter(
    service_name: str, health: HealthResult, usage: UsageResult, quota: QuotaInfo
) -> AsyncMock:
    """Factory function to create a mock adapter with given responses.
    
    Args:
        service_name: Name of the service (e.g., "ElevenLabs", "Google Gemini")
        health: HealthResult to return from check_health
        usage: UsageResult to return from get_usage
        quota: QuotaInfo to return from get_quota_info
        
    Returns:
        Configured AsyncMock adapter
    """
    mock_adapter = AsyncMock()
    mock_adapter.service_name = service_name
    mock_adapter.check_health = AsyncMock(return_value=health)
    mock_adapter.get_usage = AsyncMock(return_value=usage)
    mock_adapter.get_quota_info = AsyncMock(return_value=quota)
    mock_adapter.close = AsyncMock()
    return mock_adapter


# =============================================================================
# Test Class
# =============================================================================


class TestPartialQuotaFailure:
    """[P1] Tests for partial service quota failure scenarios (AC #4)."""

    def test_status_shows_quota_when_elevenlabs_fails_gemini_succeeds(
        self, mock_health_ok, mock_usage_ok, mock_usage_unavailable, mock_settings
    ):
        """Verifies graceful degradation: ElevenLabs quota fails, Gemini works."""
        # GIVEN: ElevenLabs quota unavailable, Gemini succeeds
        mock_quota_gemini = QuotaInfo(
            service="Gemini", used=None, limit=15, unit="rpm", reset_date=None
        )
        mock_quota_eleven_unavailable = QuotaInfo(
            service="ElevenLabs", used=None, limit=None, unit="chars", reset_date=None
        )

        mock_eleven = create_mock_adapter(
            "ElevenLabs", mock_health_ok, mock_usage_ok, mock_quota_eleven_unavailable
        )
        mock_gemini = create_mock_adapter(
            "Google Gemini", mock_health_ok, mock_usage_unavailable, mock_quota_gemini
        )

        with patch("eleven_video.main.Settings", return_value=mock_settings):
            with (
                patch("eleven_video.main.ElevenLabsAdapter", return_value=mock_eleven),
                patch("eleven_video.main.GeminiAdapter", return_value=mock_gemini),
            ):
                # WHEN: Invoking status command
                result = runner.invoke(app, ["status"])

                # THEN: Command should succeed and show both services
                assert result.exit_code == 0, f"Command failed: {result.stdout}"
                assert "API Quota Status" in result.stdout
                assert "ElevenLabs" in result.stdout
                assert "Gemini" in result.stdout
                assert "Unavailable" in result.stdout
                assert "15" in result.stdout or "rpm" in result.stdout

    def test_status_shows_quota_when_gemini_fails_elevenlabs_succeeds(
        self, mock_health_ok, mock_usage_ok, mock_usage_unavailable, mock_settings
    ):
        """Verifies graceful degradation: Gemini quota fails, ElevenLabs works."""
        # GIVEN: ElevenLabs quota succeeds, Gemini unavailable
        mock_quota_eleven = QuotaInfo(
            service="ElevenLabs", used=500, limit=1000, unit="chars", reset_date=None
        )
        mock_quota_gemini_unavailable = QuotaInfo(
            service="Gemini", used=None, limit=None, unit="rpm", reset_date=None
        )

        mock_eleven = create_mock_adapter(
            "ElevenLabs", mock_health_ok, mock_usage_ok, mock_quota_eleven
        )
        mock_gemini = create_mock_adapter(
            "Google Gemini",
            mock_health_ok,
            mock_usage_unavailable,
            mock_quota_gemini_unavailable,
        )

        with patch("eleven_video.main.Settings", return_value=mock_settings):
            with (
                patch("eleven_video.main.ElevenLabsAdapter", return_value=mock_eleven),
                patch("eleven_video.main.GeminiAdapter", return_value=mock_gemini),
            ):
                # WHEN: Invoking status command
                result = runner.invoke(app, ["status"])

                # THEN: Command should succeed and show both services
                assert result.exit_code == 0, f"Command failed: {result.stdout}"
                assert "API Quota Status" in result.stdout
                assert "ElevenLabs" in result.stdout
                assert "Gemini" in result.stdout
                assert "500" in result.stdout or "chars" in result.stdout

    def test_status_runs_when_both_quota_fetches_fail(
        self, mock_health_ok, mock_usage_unavailable, mock_settings
    ):
        """Verifies command still runs when both services fail quota fetch."""
        # GIVEN: Both adapters return unavailable quota
        mock_quota_eleven_unavailable = QuotaInfo(
            service="ElevenLabs", used=None, limit=None, unit="chars", reset_date=None
        )
        mock_quota_gemini_unavailable = QuotaInfo(
            service="Gemini", used=None, limit=None, unit="rpm", reset_date=None
        )

        mock_eleven = create_mock_adapter(
            "ElevenLabs",
            mock_health_ok,
            mock_usage_unavailable,
            mock_quota_eleven_unavailable,
        )
        mock_gemini = create_mock_adapter(
            "Google Gemini",
            mock_health_ok,
            mock_usage_unavailable,
            mock_quota_gemini_unavailable,
        )

        with patch("eleven_video.main.Settings", return_value=mock_settings):
            with (
                patch("eleven_video.main.ElevenLabsAdapter", return_value=mock_eleven),
                patch("eleven_video.main.GeminiAdapter", return_value=mock_gemini),
            ):
                # WHEN: Invoking status command
                result = runner.invoke(app, ["status"])

                # THEN: Command should still succeed (graceful degradation)
                assert result.exit_code == 0, f"Command failed: {result.stdout}"
                assert "API Quota Status" in result.stdout
                output_lower = result.stdout.lower()
                assert output_lower.count("unavailable") >= 2 or (
                    "unavailable" in output_lower
                )
