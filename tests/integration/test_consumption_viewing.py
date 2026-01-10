"""Integration tests for live consumption data viewing (Story 5.3).

Tests verify that consumption data updates in real-time during video generation
and that the final summary is displayed at session end.

Test IDs: [5.3-INT-001] through [5.3-INT-003]
"""
import pytest
from unittest.mock import MagicMock, patch, call
from io import StringIO

from rich.console import Console
from eleven_video.ui.usage_panel import UsageDisplay
from eleven_video.monitoring.usage import (
    UsageMonitor,
    SERVICE_GEMINI,
    SERVICE_ELEVENLABS,
    METRIC_INPUT_TOKENS,
    METRIC_OUTPUT_TOKENS,
    METRIC_CHARACTERS,
    MODEL_GEMINI_FLASH,
    MODEL_GEMINI_PRO
)


# =============================================================================
# P1 Tests: Live Consumption Viewing
# =============================================================================

class TestLiveConsumptionViewing:
    """P1 integration tests for live consumption data updates."""

    def test_consumption_data_updates_during_generation(self, clean_monitor_state):
        """[5.3-INT-001][P1] Verify consumption data updates in real-time.
        
        GIVEN: A video generation session is in progress
        WHEN: API calls complete and usage is tracked
        THEN: The consumption data display updates to show new usage
        
        AC: AC4 (Real-time updates)
        """
        # GIVEN: Clean monitor and display
        monitor = clean_monitor_state
        display = UsageDisplay()
        
        # WHEN: Track initial usage
        monitor.track_usage(
            service=SERVICE_GEMINI,
            model_id=MODEL_GEMINI_FLASH,
            metric_type=METRIC_INPUT_TOKENS,
            value=1_000_000
        )
        
        # Get initial summary
        initial_summary = monitor.get_summary()
        initial_cost = initial_summary["total_cost"]
        
        # THEN: Initial cost should be $0.50
        # This test will FAIL until Story 5.3 implementation
        assert initial_cost == 0.50, f"Expected $0.50, got ${initial_cost}"
        
        # WHEN: Track additional usage (simulating more API calls)
        monitor.track_usage(
            service=SERVICE_ELEVENLABS,
            model_id="21m00Tcm4TlvDq8ikWAM",
            metric_type=METRIC_CHARACTERS,
            value=5_000
        )
        
        # Get updated summary
        updated_summary = monitor.get_summary()
        updated_cost = updated_summary["total_cost"]
        
        # THEN: Cost should remain the same (ElevenLabs is $0.00 per Story 5.5)
        # But we should see ElevenLabs character tracking
        assert updated_cost == initial_cost, \
            f"Cost should remain ${initial_cost} (ElevenLabs is subscription-based with $0 cost)"
        assert SERVICE_GEMINI in updated_summary["by_service"], "Should show Gemini service"
        assert SERVICE_ELEVENLABS in updated_summary["by_service"], "Should show ElevenLabs service"
        assert len(updated_summary["by_model"]) == 2, "Should show 2 models"
        
        # Verify ElevenLabs tracks characters even though cost is $0
        elevenlabs_data = updated_summary["by_service"][SERVICE_ELEVENLABS]
        assert elevenlabs_data["metrics"]["characters"] == 5_000, \
            "Should track 5000 characters for ElevenLabs"
        assert elevenlabs_data["cost"] == 0.0, \
            "ElevenLabs cost should be $0.00 (subscription model)"

    def test_consumption_display_reflects_latest_data(self, clean_monitor_state):
        """[5.3-INT-002][P1] Verify UsageDisplay shows latest consumption data.
        
        GIVEN: Usage is being tracked in real-time
        WHEN: UsageDisplay is rendered multiple times
        THEN: Each render reflects the current state of tracked usage
        
        AC: AC4 (Real-time updates)
        """
        # GIVEN: Clean monitor and display
        monitor = clean_monitor_state
        
        # Fixture already handles singleton reset, so getInstance returns the clean monitor
        display = UsageDisplay()
            
        # WHEN: Track first batch of usage
        monitor.track_usage(
            service=SERVICE_GEMINI,
            model_id=MODEL_GEMINI_FLASH,
            metric_type=METRIC_INPUT_TOKENS,
            value=500_000
        )
            
        # Render first time
        panel_1 = display.__rich__()
        
        # Render panel to string using Rich Console
        string_io = StringIO()
        console = Console(file=string_io, force_terminal=False, width=120)
        console.print(panel_1)
        panel_1_str = string_io.getvalue()
            
        # THEN: Should show first batch cost
        assert "$0.25" in panel_1_str, "Should show $0.25 for 500K tokens"
            
        # WHEN: Track second batch of usage
        monitor.track_usage(
            service=SERVICE_GEMINI,
            model_id=MODEL_GEMINI_FLASH,
            metric_type=METRIC_INPUT_TOKENS,
            value=500_000  # Another 500K tokens
        )
            
        # Render second time
        panel_2 = display.__rich__()
            
        # Render panel to string using Rich Console
        string_io_2 = StringIO()
        console_2 = Console(file=string_io_2, force_terminal=False, width=120)
        console_2.print(panel_2)
        panel_2_str = string_io_2.getvalue()
            
        # THEN: Should show updated cost
        assert "$0.50" in panel_2_str or "$0.5" in panel_2_str, "Should show $0.50 for 1M tokens total"


# =============================================================================
# P1 Tests: Session-End Summary
# =============================================================================

class TestSessionEndSummary:
    """P1 integration tests for session-end summary display."""

    def test_final_summary_displays_complete_breakdown(self, clean_monitor_state):
        """[5.3-INT-003][P1] Verify final summary shows complete consumption breakdown.
        
        GIVEN: A video generation session has completed
        WHEN: The final usage summary is displayed
        THEN: It shows total cost and complete breakdown of all API usage
        
        AC: AC5 (Session-end summary)
        """
        # GIVEN: Completed session with multiple API calls
        monitor = clean_monitor_state
        
        # Track various usage events
        monitor.track_usage(SERVICE_GEMINI, MODEL_GEMINI_FLASH, METRIC_INPUT_TOKENS, 1_500_000)
        monitor.track_usage(SERVICE_GEMINI, MODEL_GEMINI_FLASH, METRIC_OUTPUT_TOKENS, 400_000)
        monitor.track_usage(SERVICE_GEMINI, MODEL_GEMINI_PRO, METRIC_INPUT_TOKENS, 500_000)
        monitor.track_usage(SERVICE_GEMINI, MODEL_GEMINI_PRO, METRIC_OUTPUT_TOKENS, 100_000)
        monitor.track_usage(SERVICE_ELEVENLABS, "21m00Tcm4TlvDq8ikWAM", METRIC_CHARACTERS, 5_000)
        
        # WHEN: Get final summary
        final_summary = monitor.get_summary()
        
        # THEN: Summary should be complete
        # This test will FAIL until Story 5.3 implementation
        assert final_summary["total_cost"] > 0, "Should have non-zero total cost"
        assert len(final_summary["by_service"]) == 2, "Should show 2 services"
        assert len(final_summary["by_model"]) == 3, "Should show 3 models"
        assert final_summary["events_count"] == 5, "Should show 5 events"
        
        # Verify service breakdown
        assert SERVICE_GEMINI in final_summary["by_service"], "Should include Gemini service"
        assert SERVICE_ELEVENLABS in final_summary["by_service"], "Should include ElevenLabs service"
        
        # Verify model breakdown
        assert MODEL_GEMINI_FLASH in final_summary["by_model"], "Should include Flash model"
        assert MODEL_GEMINI_PRO in final_summary["by_model"], "Should include Pro model"
        assert "21m00Tcm4TlvDq8ikWAM" in final_summary["by_model"], "Should include voice ID"
        
        # Verify cost consistency: by_model costs should sum to by_service costs
        gemini_service_cost = final_summary["by_service"][SERVICE_GEMINI]["cost"]
        flash_cost = final_summary["by_model"][MODEL_GEMINI_FLASH]["cost"]
        pro_cost = final_summary["by_model"][MODEL_GEMINI_PRO]["cost"]
        
        # Allow small floating point tolerance
        model_sum = flash_cost + pro_cost
        assert abs(gemini_service_cost - model_sum) < 0.0001, \
            f"Model costs ({model_sum}) should sum to service cost ({gemini_service_cost})"


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def clean_monitor_state():
    """Reset UsageMonitor state before and after each test.
    
    Ensures test isolation by clearing all tracked usage events.
    """
    # Setup: Reset to clean state
    monitor = UsageMonitor.get_instance()
    monitor.reset()
    
    yield monitor
    
    # Teardown: Always reset after test
    monitor.reset()
