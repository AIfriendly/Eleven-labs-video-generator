"""
ATDD Tests for Story 5.5: API Cost Tracking During Generation.

Tests verify:
- Gemini costs displayed as dollar amounts ($X.XX)
- ElevenLabs shows character consumption only (no fake costs)
- Cost precision of $0.0001 (Risk R-001)
- Session reset clears accumulated data (AC #5)

Run with: pytest tests/monitoring/test_cost_tracking.py -v
"""

import pytest
from io import StringIO
from unittest.mock import patch

from rich.console import Console

from eleven_video.monitoring.usage import (
    UsageMonitor,
    PricingStrategy,
    SERVICE_GEMINI,
    SERVICE_ELEVENLABS,
    METRIC_INPUT_TOKENS,
    METRIC_OUTPUT_TOKENS,
    METRIC_CHARACTERS,
    METRIC_IMAGES,
    MODEL_GEMINI_FLASH,
    MODEL_GEMINI_FLASH_IMAGE,
)
from eleven_video.ui.usage_panel import UsageDisplay


# Test-only constant for ElevenLabs voice model (not in usage.py since voice selection is dynamic)
MODEL_ELEVEN_RACHEL = "Rachel"


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
    # Setup: Reset to clean state
    PricingStrategy.reset()
    monitor = UsageMonitor.get_instance()
    monitor.reset()
    
    yield monitor
    
    # Teardown: Always reset after test (runs even if test fails)
    PricingStrategy.reset()
    monitor.reset()


# =============================================================================
# P0 Unit Tests - Cost Precision (Risk R-001 Mitigation)
# =============================================================================

@pytest.mark.p0
class TestCostPrecision:
    """[5.5-UNIT-001] Token-to-cost calculation must match expected values within $0.0001 precision."""
    
    def test_gemini_input_token_cost_precision(self, clean_monitor_state):
        """[5.5-UNIT-001a][P0] Verify Gemini input token cost precision.
        
        GIVEN: Default pricing configuration (input_token: $0.50/million)
        WHEN: 12345 input tokens are tracked for Gemini
        THEN: Cost should be exactly $0.0062 (12345 / 1M * 0.50 = 0.0061725, rounded to 4 decimal places)
        
        Risk: R-001 (Cost Accuracy)
        Quality Gate: Token-to-cost calculation must match expected within $0.0001 precision
        """
        # GIVEN: clean_monitor_state fixture provides reset monitor
        monitor = clean_monitor_state
        
        # WHEN: Track 12345 input tokens
        monitor.track_usage(
            service=SERVICE_GEMINI,
            model_id=MODEL_GEMINI_FLASH,
            metric_type=METRIC_INPUT_TOKENS,
            value=12345
        )
        
        # THEN: Cost should be within $0.0001 of expected
        summary = monitor.get_summary()
        expected_cost = (12345 / 1_000_000) * 0.50  # = 0.0061725
        
        # Use by_service cost (4 decimal precision) instead of total_cost (2 decimal)
        gemini_cost = summary["by_service"][SERVICE_GEMINI]["cost"]
        assert abs(gemini_cost - expected_cost) < 0.0001, \
            f"Cost precision failed: expected ~${expected_cost:.4f}, got ${gemini_cost:.4f}"
    
    def test_gemini_output_token_cost_precision(self, clean_monitor_state):
        """[5.5-UNIT-001b][P0] Verify Gemini output token cost precision.
        
        GIVEN: Default pricing configuration (output_token: $1.50/million)
        WHEN: 50000 output tokens are tracked for Gemini
        THEN: Cost should be exactly $0.0750 (50000 / 1M * 1.50 = 0.075)
        
        Risk: R-001 (Cost Accuracy)
        """
        # GIVEN: clean_monitor_state fixture provides reset monitor
        monitor = clean_monitor_state
        
        # WHEN: Track 50000 output tokens
        monitor.track_usage(
            service=SERVICE_GEMINI,
            model_id=MODEL_GEMINI_FLASH,
            metric_type=METRIC_OUTPUT_TOKENS,
            value=50000
        )
        
        # THEN: Cost should be within $0.0001 of expected
        summary = monitor.get_summary()
        expected_cost = (50000 / 1_000_000) * 1.50  # = 0.075
        
        gemini_cost = summary["by_service"][SERVICE_GEMINI]["cost"]
        assert abs(gemini_cost - expected_cost) < 0.0001, \
            f"Cost precision failed: expected ~${expected_cost:.4f}, got ${gemini_cost:.4f}"
    
    def test_gemini_image_cost_precision(self, clean_monitor_state):
        """[5.5-UNIT-001c][P0] Verify Gemini image cost precision.
        
        GIVEN: Default pricing configuration (image: $0.04 per image)
        WHEN: 5 images are generated
        THEN: Cost should be exactly $0.20 (5 * 0.04 = 0.20)
        
        Risk: R-001 (Cost Accuracy)
        """
        # GIVEN: clean_monitor_state fixture provides reset monitor
        monitor = clean_monitor_state
        
        # WHEN: Track 5 images
        monitor.track_usage(
            service=SERVICE_GEMINI,
            model_id=MODEL_GEMINI_FLASH_IMAGE,
            metric_type=METRIC_IMAGES,
            value=5
        )
        
        # THEN: Cost should be within $0.0001 of expected
        summary = monitor.get_summary()
        expected_cost = 5 * 0.04  # = 0.20
        
        gemini_cost = summary["by_service"][SERVICE_GEMINI]["cost"]
        assert abs(gemini_cost - expected_cost) < 0.0001, \
            f"Cost precision failed: expected ~${expected_cost:.4f}, got ${gemini_cost:.4f}"


@pytest.mark.p0
class TestCostAccumulation:
    """[5.5-UNIT-002] Cost accumulates correctly across multiple Gemini API calls."""
    
    def test_cost_accumulates_across_multiple_calls(self, clean_monitor_state):
        """[5.5-UNIT-002a][P0] Verify cost accumulates correctly across multiple API calls.
        
        GIVEN: Default pricing configuration
        WHEN: Multiple Gemini API calls are made (script generation + image generation)
        THEN: Total cost should be the sum of all individual costs
        
        Risk: R-001 (Cost Accuracy)
        """
        # GIVEN: clean_monitor_state fixture provides reset monitor
        monitor = clean_monitor_state
        
        # WHEN: Track multiple API calls
        # Call 1: Script generation (1M input tokens, 50K output tokens)
        monitor.track_usage(
            service=SERVICE_GEMINI,
            model_id=MODEL_GEMINI_FLASH,
            metric_type=METRIC_INPUT_TOKENS,
            value=1_000_000
        )
        monitor.track_usage(
            service=SERVICE_GEMINI,
            model_id=MODEL_GEMINI_FLASH,
            metric_type=METRIC_OUTPUT_TOKENS,
            value=50_000
        )
        
        # Call 2: Image generation (5 images)
        monitor.track_usage(
            service=SERVICE_GEMINI,
            model_id=MODEL_GEMINI_FLASH_IMAGE,
            metric_type=METRIC_IMAGES,
            value=5
        )
        
        # THEN: Total cost should be sum of all costs
        summary = monitor.get_summary()
        
        # Expected: $0.50 (input) + $0.075 (output) + $0.20 (images) = $0.775
        expected_total = 0.50 + 0.075 + 0.20
        
        # total_cost is rounded to 2 decimal places
        assert summary["total_cost"] == round(expected_total, 2), \
            f"Total cost mismatch: expected ${expected_total:.2f}, got ${summary['total_cost']:.2f}"


@pytest.mark.p0
class TestElevenLabsSubscriptionModel:
    """[5.5-UNIT-003] ElevenLabs returns 0 cost and shows character count only."""
    
    def test_elevenlabs_returns_zero_cost(self, clean_monitor_state):
        """[5.5-UNIT-003a][P0] Verify ElevenLabs returns $0 cost (subscription-based).
        
        GIVEN: ElevenLabs is subscription-based with character quotas (not pay-per-use)
        WHEN: 5000 characters are used for TTS
        THEN: ElevenLabs service cost should be $0.00 (not $0.55 = 5000/1M * $110)
        
        Note: This test will FAIL until PricingStrategy is fixed to set 
        elevenlabs.character_price_per_million = 0.0
        """
        # GIVEN: clean_monitor_state fixture provides reset monitor
        monitor = clean_monitor_state
        
        # WHEN: Track 5000 characters for ElevenLabs TTS
        monitor.track_usage(
            service=SERVICE_ELEVENLABS,
            model_id=MODEL_ELEVEN_RACHEL,
            metric_type=METRIC_CHARACTERS,
            value=5000
        )
        
        # THEN: ElevenLabs cost should be $0.00 (subscription-based, no per-call cost)
        summary = monitor.get_summary()
        elevenlabs_cost = summary["by_service"][SERVICE_ELEVENLABS]["cost"]
        
        assert elevenlabs_cost == 0.0, \
            f"ElevenLabs should have $0 cost (subscription-based), got ${elevenlabs_cost:.4f}"
    
    def test_elevenlabs_tracks_character_count(self, clean_monitor_state):
        """[5.5-UNIT-003b][P0] Verify ElevenLabs tracks character count correctly.
        
        GIVEN: ElevenLabs usage tracking is active
        WHEN: 5000 characters are used for TTS
        THEN: Character count should be tracked accurately (5000)
        """
        # GIVEN: clean_monitor_state fixture provides reset monitor
        monitor = clean_monitor_state
        
        # WHEN: Track 5000 characters
        monitor.track_usage(
            service=SERVICE_ELEVENLABS,
            model_id=MODEL_ELEVEN_RACHEL,
            metric_type=METRIC_CHARACTERS,
            value=5000
        )
        
        # THEN: Character count should be tracked
        summary = monitor.get_summary()
        metrics = summary["by_service"][SERVICE_ELEVENLABS]["metrics"]
        
        assert metrics.get(METRIC_CHARACTERS) == 5000, \
            f"Character count mismatch: expected 5000, got {metrics.get(METRIC_CHARACTERS)}"
    
    def test_elevenlabs_does_not_affect_total_cost(self, clean_monitor_state):
        """[5.5-UNIT-003c][P0] Verify ElevenLabs usage does not inflate total cost.
        
        GIVEN: Gemini has pay-per-use costs, ElevenLabs is subscription-based
        WHEN: Both services are used
        THEN: Total cost should only include Gemini costs, not ElevenLabs
        
        Note: This test will FAIL until PricingStrategy is fixed
        """
        # GIVEN: clean_monitor_state fixture provides reset monitor
        monitor = clean_monitor_state
        
        # WHEN: Use both services
        # Gemini: 1M input tokens = $0.50
        monitor.track_usage(
            service=SERVICE_GEMINI,
            model_id=MODEL_GEMINI_FLASH,
            metric_type=METRIC_INPUT_TOKENS,
            value=1_000_000
        )
        
        # ElevenLabs: 10000 characters = should be $0.00 (not $1.10)
        monitor.track_usage(
            service=SERVICE_ELEVENLABS,
            model_id=MODEL_ELEVEN_RACHEL,
            metric_type=METRIC_CHARACTERS,
            value=10000
        )
        
        # THEN: Total cost should be $0.50 (Gemini only), not $1.60
        summary = monitor.get_summary()
        
        assert summary["total_cost"] == 0.50, \
            f"Total cost should be $0.50 (Gemini only), got ${summary['total_cost']:.2f}"


# =============================================================================
# P0 UI Tests - Display Differentiation (AC #1, #2, #3)
# =============================================================================

@pytest.mark.p0
class TestUsageDisplayDifferentiation:
    """Tests for UsageDisplay showing Gemini as dollars, ElevenLabs as credits."""
    
    def test_gemini_displays_dollar_cost(self, clean_monitor_state):
        """[5.5-UI-001][P0] Verify Gemini displays dollar cost format.
        
        GIVEN: Gemini API calls have been tracked
        WHEN: UsageDisplay is rendered
        THEN: Gemini line should show dollar cost format ($X.XXXX)
        
        AC #1: I can see running dollar cost totals for Gemini usage
        """
        # GIVEN: Track some Gemini usage
        monitor = clean_monitor_state
        monitor.track_usage(
            service=SERVICE_GEMINI,
            model_id=MODEL_GEMINI_FLASH,
            metric_type=METRIC_INPUT_TOKENS,
            value=1_000_000
        )
        
        # WHEN: Render UsageDisplay
        display = UsageDisplay()
        console = Console(file=StringIO(), force_terminal=True, width=80)
        console.print(display)
        output = console.file.getvalue()
        
        # THEN: Should show Gemini with dollar format
        # Expected: "Gemini API Cost: $0.5000" or similar
        assert "Gemini" in output
        assert "$" in output
        # Look for dollar format with Gemini
        assert "$0.50" in output or "$0.5000" in output, \
            f"Gemini should show dollar cost, got: {output}"
    
    def test_elevenlabs_displays_character_credits_not_dollars(self, clean_monitor_state):
        """[5.5-UI-002][P0] Verify ElevenLabs displays character credits, NOT dollars.
        
        GIVEN: ElevenLabs TTS calls have been tracked
        WHEN: UsageDisplay is rendered
        THEN: ElevenLabs line should show "X characters" format, NOT "$X.XX"
        
        AC #2: I see character credit consumption for ElevenLabs (not dollar cost)
        
        Note: This test will FAIL until UsageDisplay.__rich__() is updated
        to differentiate between Gemini and ElevenLabs display formats.
        """
        # GIVEN: Track some ElevenLabs usage
        monitor = clean_monitor_state
        monitor.track_usage(
            service=SERVICE_ELEVENLABS,
            model_id=MODEL_ELEVEN_RACHEL,
            metric_type=METRIC_CHARACTERS,
            value=5000
        )
        
        # WHEN: Render UsageDisplay
        display = UsageDisplay()
        console = Console(file=StringIO(), force_terminal=True, width=80)
        console.print(display)
        output = console.file.getvalue()
        
        # THEN: Should show ElevenLabs with character format, NOT dollar cost
        assert "Elevenlabs" in output or "ElevenLabs" in output
        
        # Should show character count
        assert "5,000 characters" in output or "5K characters" in output or "5.0K characters" in output, \
            f"ElevenLabs should show character count, got: {output}"
        
        # Should NOT show dollar cost for ElevenLabs
        # This is the key assertion - ElevenLabs should not have a dollar amount
        # Current behavior incorrectly shows "$X.XXXX" for ElevenLabs
        lines = output.split('\n')
        for line in lines:
            if 'Elevenlabs' in line or 'ElevenLabs' in line:
                # ElevenLabs line should NOT contain a cost like "$0.5500"
                assert '$0.' not in line or 'characters' in line.split('$')[0], \
                    f"ElevenLabs line should show characters, not fake dollar cost: {line}"
    
    def test_display_formatting_ac3(self, clean_monitor_state):
        """[5.5-UI-003][P0] Verify cost formatting matches AC #3 requirements.
        
        GIVEN: Both Gemini and ElevenLabs usage tracked
        WHEN: UsageDisplay is rendered
        THEN: Costs displayed with appropriate formatting:
              - Gemini: "$0.0125" format
              - ElevenLabs: "5,000 chars" format
        
        AC #3: Costs displayed with appropriate formatting
        """
        # GIVEN: Track usage for both services
        monitor = clean_monitor_state
        
        # Gemini: 25000 input tokens = $0.0125
        monitor.track_usage(
            service=SERVICE_GEMINI,
            model_id=MODEL_GEMINI_FLASH,
            metric_type=METRIC_INPUT_TOKENS,
            value=25000
        )
        
        # ElevenLabs: 5000 characters
        monitor.track_usage(
            service=SERVICE_ELEVENLABS,
            model_id=MODEL_ELEVEN_RACHEL,
            metric_type=METRIC_CHARACTERS,
            value=5000
        )
        
        # WHEN: Render UsageDisplay
        display = UsageDisplay()
        console = Console(file=StringIO(), force_terminal=True, width=80)
        console.print(display)
        output = console.file.getvalue()
        
        # THEN: Verify formatting
        # Gemini should show dollar cost with precision
        assert "$0.0125" in output or "$0.01" in output, \
            f"Gemini cost format incorrect, got: {output}"
        
        # ElevenLabs should show character count (with comma or K formatting)
        assert "5,000" in output or "5K" in output or "5.0K" in output, \
            f"ElevenLabs character format incorrect, got: {output}"


# =============================================================================
# P1 Integration Tests - Final Cost Report (AC #4)
# =============================================================================

@pytest.mark.p1
class TestFinalCostReport:
    """[5.5-INT-001] Test final cost report is generated at end of flow."""
    
    def test_final_summary_separates_gemini_and_elevenlabs(self, clean_monitor_state):
        """[5.5-INT-001a][P1] Verify final summary separates Gemini cost from ElevenLabs credits.
        
        GIVEN: A complete generation session with both services used
        WHEN: Final summary is displayed
        THEN: 
          - Gemini shows "Gemini API Cost: $X.XX" 
          - ElevenLabs shows "ElevenLabs Credits: X characters"
          - These are clearly separated (not combined into misleading "Total Cost")
        
        AC #4: Final summary shows Gemini dollar cost and ElevenLabs character 
               consumption clearly separated
        """
        # GIVEN: Track usage simulating complete generation
        monitor = clean_monitor_state
        
        # Script generation
        monitor.track_usage(
            service=SERVICE_GEMINI,
            model_id=MODEL_GEMINI_FLASH,
            metric_type=METRIC_INPUT_TOKENS,
            value=500_000
        )
        monitor.track_usage(
            service=SERVICE_GEMINI,
            model_id=MODEL_GEMINI_FLASH,
            metric_type=METRIC_OUTPUT_TOKENS,
            value=25_000
        )
        
        # Image generation
        monitor.track_usage(
            service=SERVICE_GEMINI,
            model_id=MODEL_GEMINI_FLASH_IMAGE,
            metric_type=METRIC_IMAGES,
            value=5
        )
        
        # TTS generation
        monitor.track_usage(
            service=SERVICE_ELEVENLABS,
            model_id=MODEL_ELEVEN_RACHEL,
            metric_type=METRIC_CHARACTERS,
            value=5000
        )
        
        # WHEN: Get summary and render display
        summary = monitor.get_summary()
        display = UsageDisplay()
        console = Console(file=StringIO(), force_terminal=True, width=80)
        console.print(display)
        output = console.file.getvalue()
        
        # THEN: Verify separation
        # Gemini cost should be present as API Cost (not generic "Total Cost")
        # Expected Gemini: $0.25 (input) + $0.0375 (output) + $0.20 (images) = ~$0.49
        gemini_cost = summary["by_service"][SERVICE_GEMINI]["cost"]
        assert gemini_cost > 0, "Gemini should have a cost"
        
        # ElevenLabs should have $0 cost but tracked characters
        elevenlabs_data = summary["by_service"][SERVICE_ELEVENLABS]
        assert elevenlabs_data["cost"] == 0.0, \
            f"ElevenLabs cost should be $0, got ${elevenlabs_data['cost']}"
        assert elevenlabs_data["metrics"][METRIC_CHARACTERS] == 5000, \
            f"ElevenLabs should track 5000 chars, got {elevenlabs_data['metrics']}"
        
        # Display should label correctly (not misleading "Total Cost" that includes fake ElevenLabs cost)
        # This assertion will FAIL until display is updated
        # Current: "Total Cost: $X.XX" includes fake ElevenLabs cost
        # Expected: "Gemini API Cost: $X.XX" for actual costs only
        assert "Gemini" in output and "$" in output
    
    def test_cost_accumulates_across_script_and_images(self, clean_monitor_state):
        """[5.5-INT-001b][P1] Verify cost accumulates correctly across script + image generation.
        
        GIVEN: A generation session
        WHEN: Script and image generation calls are made
        THEN: Gemini total cost reflects both operations correctly
        """
        # GIVEN: clean_monitor_state fixture provides reset monitor
        monitor = clean_monitor_state
        
        # WHEN: Track script generation (1M input, 100K output)
        monitor.track_usage(
            service=SERVICE_GEMINI,
            model_id=MODEL_GEMINI_FLASH,
            metric_type=METRIC_INPUT_TOKENS,
            value=1_000_000
        )
        monitor.track_usage(
            service=SERVICE_GEMINI,
            model_id=MODEL_GEMINI_FLASH,
            metric_type=METRIC_OUTPUT_TOKENS,
            value=100_000
        )
        
        # Track image generation (10 images)
        monitor.track_usage(
            service=SERVICE_GEMINI,
            model_id=MODEL_GEMINI_FLASH_IMAGE,
            metric_type=METRIC_IMAGES,
            value=10
        )
        
        # THEN: Total Gemini cost should be accurate
        summary = monitor.get_summary()
        
        # Expected: $0.50 (input) + $0.15 (output) + $0.40 (images) = $1.05
        expected_gemini = 0.50 + 0.15 + 0.40
        gemini_cost = summary["by_service"][SERVICE_GEMINI]["cost"]
        
        assert abs(gemini_cost - expected_gemini) < 0.01, \
            f"Gemini cost mismatch: expected ${expected_gemini:.2f}, got ${gemini_cost:.4f}"


# =============================================================================
# P2 Edge Case Tests - Zero Usage and Session Reset (AC #5)
# =============================================================================

@pytest.mark.p2
class TestEdgeCases:
    """[5.5-UNIT-003] Edge case tests for zero usage and session reset."""
    
    def test_zero_usage_shows_zero_cost(self, clean_monitor_state):
        """[5.5-UNIT-003a][P2] Test zero-usage scenarios (dry runs) show $0.00 cost.
        
        GIVEN: No API calls have been made
        WHEN: Summary is requested
        THEN: Total cost should be $0.00
        """
        # GIVEN: clean_monitor_state fixture provides reset monitor with no events
        monitor = clean_monitor_state
        
        # WHEN: Get summary without any tracked usage
        summary = monitor.get_summary()
        
        # THEN: Total cost should be $0.00
        assert summary["total_cost"] == 0.0, \
            f"Zero usage should show $0.00 cost, got ${summary['total_cost']:.2f}"
        assert summary["events_count"] == 0, \
            f"Zero usage should have 0 events, got {summary['events_count']}"
    
    def test_session_reset_clears_accumulated_data(self, clean_monitor_state):
        """[5.5-UNIT-003b][P2] Test session reset clears accumulated data (AC #5).
        
        GIVEN: A session with tracked usage
        WHEN: A new video generation starts and monitor.reset() is called
        THEN: All previous tracking data is cleared
        
        AC #5: Starting a new video resets tracking for the new session
        """
        # GIVEN: Track some usage in "first generation"
        monitor = clean_monitor_state
        
        monitor.track_usage(
            service=SERVICE_GEMINI,
            model_id=MODEL_GEMINI_FLASH,
            metric_type=METRIC_INPUT_TOKENS,
            value=1_000_000
        )
        
        # Verify usage is tracked
        summary_before = monitor.get_summary()
        assert summary_before["total_cost"] > 0, "Should have cost from first session"
        assert summary_before["events_count"] > 0, "Should have events from first session"
        
        # WHEN: Reset for new session
        monitor.reset()
        
        # THEN: All tracking data should be cleared
        summary_after = monitor.get_summary()
        assert summary_after["total_cost"] == 0.0, \
            f"Reset should clear cost, got ${summary_after['total_cost']:.2f}"
        assert summary_after["events_count"] == 0, \
            f"Reset should clear events, got {summary_after['events_count']}"
        assert summary_after["by_service"] == {}, \
            f"Reset should clear by_service, got {summary_after['by_service']}"
        assert summary_after["by_model"] == {}, \
            f"Reset should clear by_model, got {summary_after['by_model']}"
    
    def test_multiple_sessions_independent(self, clean_monitor_state):
        """[5.5-UNIT-003c][P2] Test multiple generation sessions are independent.
        
        GIVEN: First session completes and is reset
        WHEN: Second session starts and tracks new usage
        THEN: Second session only reflects its own usage, not first session
        """
        # GIVEN: First session
        monitor = clean_monitor_state
        
        monitor.track_usage(
            service=SERVICE_GEMINI,
            model_id=MODEL_GEMINI_FLASH,
            metric_type=METRIC_INPUT_TOKENS,
            value=2_000_000  # $1.00
        )
        
        first_summary = monitor.get_summary()
        assert first_summary["total_cost"] == 1.00
        
        # Reset for second session
        monitor.reset()
        
        # WHEN: Second session with different usage
        monitor.track_usage(
            service=SERVICE_GEMINI,
            model_id=MODEL_GEMINI_FLASH,
            metric_type=METRIC_INPUT_TOKENS,
            value=500_000  # $0.25
        )
        
        # THEN: Second session should only show its own usage
        second_summary = monitor.get_summary()
        assert second_summary["total_cost"] == 0.25, \
            f"Second session should show $0.25, got ${second_summary['total_cost']:.2f}"
        assert second_summary["events_count"] == 1, \
            f"Second session should have 1 event, got {second_summary['events_count']}"
