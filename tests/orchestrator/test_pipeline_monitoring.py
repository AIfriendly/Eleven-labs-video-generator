"""Orchestrator monitoring integration tests (Story 5.1).

Tests that VideoPipeline correctly integrates with UsageMonitor
and UsageDisplay for real-time API usage tracking.
"""
import pytest
from unittest.mock import MagicMock, patch, call
import logging
from pathlib import Path

from eleven_video.orchestrator.video_pipeline import VideoPipeline
from eleven_video.monitoring.usage import UsageMonitor, PricingStrategy


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def clean_monitor_state():
    """Reset UsageMonitor and PricingStrategy state before and after each test.
    
    This fixture ensures test isolation by:
    - Resetting pricing to defaults before each test
    - Clearing all tracked usage events before each test
    - Cleaning up after the test completes (even if it fails)
    """
    PricingStrategy.reset()
    monitor = UsageMonitor.get_instance()
    monitor.reset()
    
    yield monitor
    
    PricingStrategy.reset()
    monitor.reset()


@pytest.fixture
def mock_settings():
    """Create mock Settings object for VideoPipeline.
    
    Provides fake API keys and project root for testing pipeline
    instantiation without real configuration.
    """
    settings = MagicMock()
    settings.project_root = str(Path.cwd())
    settings.gemini_api_key = MagicMock()
    settings.gemini_api_key.get_secret_value.return_value = "fake-key"
    settings.elevenlabs_api_key = MagicMock()
    settings.elevenlabs_api_key.get_secret_value.return_value = "fake-key"
    return settings


@pytest.fixture
def pipeline_with_usage(mock_settings):
    """Create a VideoPipeline with show_usage=True."""
    return VideoPipeline(settings=mock_settings, show_usage=True)


@pytest.fixture
def pipeline_without_usage(mock_settings):
    """Create a VideoPipeline with show_usage=False."""
    return VideoPipeline(settings=mock_settings, show_usage=False)


# =============================================================================
# AC1: Live Usage panel display during video generation
# =============================================================================

class TestLiveUsageDisplay:
    """Tests for live usage display initialization (AC1)."""

    def test_pipeline_initializes_usage_display_when_show_usage_true(self, pipeline_with_usage):
        """[5.1-PIPE-001][P0] VideoPipeline should initialize UsageDisplay when show_usage=True.
        
        GIVEN: VideoPipeline is created with show_usage=True
        WHEN: The pipeline is instantiated
        THEN: UsageDisplay is prepared for initialization during generate()
        
        AC: AC1 (Live Usage Display)
        """
        # GIVEN/WHEN: Pipeline with show_usage enabled (from fixture)
        pipeline = pipeline_with_usage
        
        # THEN: Pipeline should have show_usage flag set
        assert pipeline.show_usage is True
    
    def test_pipeline_skips_usage_display_when_disabled(self, pipeline_without_usage):
        """[5.1-PIPE-002][P1] VideoPipeline should skip UsageDisplay when show_usage=False.
        
        GIVEN: VideoPipeline is created with show_usage=False
        WHEN: The pipeline is instantiated
        THEN: UsageDisplay initialization is skipped
        """
        # GIVEN/WHEN: Pipeline with show_usage disabled (from fixture)
        pipeline = pipeline_without_usage
        
        # THEN: Pipeline should have show_usage flag unset
        assert pipeline.show_usage is False
        assert pipeline._usage_display is None


# =============================================================================
# AC6: Final usage summary logged at session end
# =============================================================================

class TestSessionSummaryLogging:
    """Tests for session-end usage summary logging (AC6)."""

    def test_log_usage_summary_logs_session_summary(self, clean_monitor_state, pipeline_without_usage, caplog):
        """[5.1-PIPE-003][P0] _log_usage_summary should log the final usage summary (AC6).
        
        GIVEN: UsageMonitor has tracked some usage events
        WHEN: _log_usage_summary is called
        THEN: A debug log with session summary is produced
        
        AC: AC6 (Session Summary)
        """
        # GIVEN: Track some usage
        monitor = clean_monitor_state
        monitor.track_usage(
            service="gemini",
            model_id="gemini-1.5-flash",
            metric_type="input_tokens",
            value=1000
        )
        monitor.track_usage(
            service="elevenlabs",
            model_id="eleven_multilingual_v2",
            metric_type="characters",
            value=500
        )
        
        # WHEN: Log summary
        with caplog.at_level(logging.DEBUG):
            pipeline_without_usage._log_usage_summary()
        
        # THEN: Debug log should contain summary information
        assert any("Session Usage Summary" in record.message for record in caplog.records)
        assert any("gemini" in record.message for record in caplog.records)
        assert any("elevenlabs" in record.message for record in caplog.records)

    def test_usage_summary_contains_cost_information(self, clean_monitor_state, pipeline_without_usage, caplog):
        """[5.1-PIPE-004][P1] Usage summary should include total cost estimate.
        
        GIVEN: UsageMonitor has events with cost calculations
        WHEN: Summary is logged
        THEN: Log contains total cost information
        
        Risk: R-001 (Cost Accuracy)
        """
        # GIVEN: Track usage with known cost
        monitor = clean_monitor_state
        monitor.track_usage(
            service="gemini",
            model_id="gemini-1.5-flash",
            metric_type="input_tokens",
            value=1_000_000  # Should be $0.50 at default rate
        )
        
        # WHEN: Log summary
        with caplog.at_level(logging.DEBUG):
            pipeline_without_usage._log_usage_summary()
        
        # THEN: Log should contain cost info
        assert any("total_cost" in record.message or "0.5" in record.message 
                   for record in caplog.records)


# =============================================================================
# Integration: UsageMonitor reset on pipeline start
# =============================================================================

class TestMonitorReset:
    """Tests for UsageMonitor reset during pipeline initialization."""

    def test_init_usage_monitoring_resets_monitor(self, clean_monitor_state, pipeline_without_usage):
        """[5.1-PIPE-005][P1] _init_usage_monitoring should reset the UsageMonitor state.
        
        GIVEN: UsageMonitor has existing events from a previous session
        WHEN: _init_usage_monitoring is called
        THEN: The monitor is reset to clean state
        """
        # GIVEN: Monitor has pre-existing events
        monitor = clean_monitor_state
        monitor.track_usage(
            service="gemini",
            model_id="test",
            metric_type="input_tokens",
            value=999
        )
        assert len(monitor.get_events()) > 0
        
        # WHEN: Initialize usage monitoring
        pipeline_without_usage._init_usage_monitoring()
        
        # THEN: Monitor should be reset
        assert len(monitor.get_events()) == 0


# =============================================================================
# UsageDisplay lifecycle
# =============================================================================

class TestUsageDisplayLifecycle:
    """Tests for UsageDisplay start/stop lifecycle management."""

    @patch("eleven_video.orchestrator.video_pipeline.UsageDisplay")
    @patch("eleven_video.ui.console.console")
    def test_start_usage_display_prints_header(self, mock_console, mock_display_class, mock_settings):
        """[5.1-PIPE-006][P1] _start_usage_display should print usage tracking header.
        
        GIVEN: Pipeline has show_usage=True
        WHEN: _start_usage_display is called
        THEN: A header message is printed to console (stage-based approach)
        
        Note: Changed from start_live_update() to console.print() to avoid
        conflicts between Rich.Live and console.print() statements.
        """
        # GIVEN: Pipeline with usage display
        mock_display = MagicMock()
        mock_display_class.return_value = mock_display
        
        pipeline = VideoPipeline(settings=mock_settings, show_usage=True)
        pipeline._init_usage_monitoring()
        
        # WHEN: Start display
        pipeline._start_usage_display()
        
        # THEN: Console should print usage tracking header
        mock_console.print.assert_called()
    
    @patch("eleven_video.orchestrator.video_pipeline.UsageDisplay")
    def test_stop_usage_display_calls_stop_and_logs_summary(self, mock_display_class, clean_monitor_state, mock_settings, caplog):
        """[5.1-PIPE-007][P0] _stop_usage_display should stop display and log summary.
        
        GIVEN: Pipeline has active UsageDisplay and tracked usage events
        WHEN: _stop_usage_display is called
        THEN: UsageDisplay.stop_live_update() is called and summary is logged
        
        AC: AC6 (Session Summary)
        """
        # GIVEN: Pipeline with active usage display
        mock_display = MagicMock()
        mock_display_class.return_value = mock_display
        
        pipeline = VideoPipeline(settings=mock_settings, show_usage=True)
        pipeline._init_usage_monitoring()
        
        # Track events AFTER init (which resets the monitor)
        monitor = clean_monitor_state
        monitor.track_usage(
            service="gemini",
            model_id="test",
            metric_type="input_tokens",
            value=500
        )
        
        pipeline._start_usage_display()
        
        # WHEN: Stop display
        with caplog.at_level(logging.DEBUG):
            pipeline._stop_usage_display()
        
        # THEN: stop_live_update should be called
        mock_display.stop_live_update.assert_called_once()
        # AND: Summary should be logged (since we tracked events)
        assert any("Session Usage Summary" in record.message for record in caplog.records)

    def test_stop_usage_display_handles_no_display_gracefully(self, clean_monitor_state, pipeline_without_usage, caplog):
        """[5.1-PIPE-008][P2] _stop_usage_display should not fail when no display is active.
        
        GIVEN: Pipeline has show_usage=False (no display)
        WHEN: _stop_usage_display is called
        THEN: No exception is raised, summary still logged if events present
        """
        # GIVEN: Pipeline without usage display, but has events to log
        monitor = clean_monitor_state
        monitor.track_usage(
            service="gemini",
            model_id="test",
            metric_type="input_tokens",
            value=100
        )
        
        # WHEN: Stop display (should not crash)
        with caplog.at_level(logging.DEBUG):
            pipeline_without_usage._stop_usage_display()
        
        # THEN: Summary should still be logged
        assert any("Session Usage Summary" in record.message for record in caplog.records)
