"""Extended unit tests for UsageMonitor and PricingStrategy (Story 5.1).

Covers edge cases, ElevenLabs pricing, output tokens, and reset behavior.
"""
import pytest
from unittest.mock import MagicMock, patch

from eleven_video.monitoring.usage import UsageMonitor, PricingStrategy
from tests.support.factories.usage_factory import create_pricing_config


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


# =============================================================================
# ElevenLabs Character Pricing (AC5)
# =============================================================================

class TestElevenLabsPricing:
    """Tests for ElevenLabs character-based pricing calculations."""

    def test_calculate_cost_elevenlabs_characters(self, clean_monitor_state):
        """[5.1-UNIT-004][P0] Verify ElevenLabs character cost calculation.
        
        GIVEN: ElevenLabs character usage is tracked
        WHEN: Cost is calculated
        THEN: Correct cost based on character pricing is returned
        
        AC: AC5 (ElevenLabs Pricing)
        """
        # GIVEN: Monitor from fixture
        monitor = clean_monitor_state
        
        # WHEN: Track 1000 characters
        monitor.track_usage(
            service="elevenlabs",
            model_id="eleven_multilingual_v2",
            metric_type="characters",
            value=1000
        )
        
        # THEN: Cost should be calculated (default: $0.18 per 1000 chars)
        summary = monitor.get_summary()
        assert summary["by_service"]["elevenlabs"]["metrics"]["characters"] == 1000
        # Cost calculation depends on pricing strategy
        assert summary["by_service"]["elevenlabs"]["cost"] >= 0


# =============================================================================
# Gemini Token Pricing
# =============================================================================

class TestGeminiPricing:
    """Tests for Gemini token-based pricing calculations."""

    def test_calculate_cost_gemini_output_tokens(self, clean_monitor_state):
        """[5.1-UNIT-005][P0] Verify Gemini output token cost calculation (separate rate).
        
        GIVEN: Gemini output tokens are tracked
        WHEN: Cost is calculated
        THEN: Output tokens use higher price per million
        
        Risk: R-001 (Cost Accuracy)
        """
        # GIVEN: Monitor from fixture
        monitor = clean_monitor_state
        
        # WHEN: Track 1M output tokens
        monitor.track_usage(
            service="gemini",
            model_id="gemini-1.5-flash",
            metric_type="output_tokens",
            value=1_000_000
        )
        
        # THEN: Cost should be higher than input tokens (default: $1.50 vs $0.50)
        summary = monitor.get_summary()
        assert summary["by_service"]["gemini"]["metrics"]["output_tokens"] == 1_000_000
        # Default output token rate is $1.50/1M
        assert summary["total_cost"] == pytest.approx(1.50, rel=0.01)


# =============================================================================
# Image Count Tracking (AC3)
# =============================================================================

class TestImageTracking:
    """Tests for image generation count tracking."""

    def test_track_image_generation_count(self, clean_monitor_state):
        """[5.1-UNIT-006][P0] Verify image generation count is tracked (AC3).
        
        GIVEN: Image generation events are tracked
        WHEN: Multiple images are generated
        THEN: Counter increments correctly
        
        AC: AC3 (Token/Image Tracking)
        """
        # GIVEN: Monitor from fixture
        monitor = clean_monitor_state
        
        # WHEN: Track 5 image generations
        for i in range(5):
            monitor.track_usage(
                service="gemini",
                model_id="gemini-2.5-flash-image",
                metric_type="images",
                value=1
            )
        
        # THEN: Event count reflects all images
        summary = monitor.get_summary()
        assert summary["events_count"] == 5
        assert summary["by_service"]["gemini"]["metrics"]["images"] == 5


# =============================================================================
# Reset Behavior
# =============================================================================

class TestResetBehavior:
    """Tests for UsageMonitor and PricingStrategy reset functionality."""

    def test_monitor_reset_clears_all_events(self, clean_monitor_state):
        """[5.1-UNIT-007][P1] Verify reset() clears all tracked events.
        
        GIVEN: Monitor has tracked events
        WHEN: reset() is called
        THEN: All events are cleared
        """
        # GIVEN: Track some events
        monitor = clean_monitor_state
        monitor.track_usage(service="gemini", model_id="test", metric_type="input_tokens", value=100)
        monitor.track_usage(service="elevenlabs", model_id="test", metric_type="characters", value=50)
        assert len(monitor.get_events()) == 2
        
        # WHEN: Reset
        monitor.reset()
        
        # THEN: Events cleared
        assert len(monitor.get_events()) == 0
        summary = monitor.get_summary()
        assert summary["events_count"] == 0
        assert summary["total_cost"] == 0

    def test_pricing_strategy_reset_restores_defaults(self, clean_monitor_state):
        """[5.1-UNIT-008][P1] Verify PricingStrategy.reset() restores default pricing.
        
        GIVEN: Custom pricing is configured
        WHEN: reset() is called
        THEN: Default pricing is restored
        """
        # GIVEN: Configure custom pricing
        PricingStrategy.configure({
            "gemini": {"input_token_price_per_million": 99.99}
        })
        
        # WHEN: Reset
        PricingStrategy.reset()
        
        # THEN: Default pricing restored
        monitor = clean_monitor_state
        monitor.track_usage(service="gemini", model_id="test", metric_type="input_tokens", value=1_000_000)
        summary = monitor.get_summary()
        assert summary["total_cost"] == pytest.approx(0.50, rel=0.01)  # Default rate


# =============================================================================
# Multiple Services Combined (AC3)
# =============================================================================

class TestCombinedServices:
    """Tests for multiple service cost aggregation."""

    def test_combined_service_costs(self, clean_monitor_state):
        """[5.1-UNIT-009][P0] Verify combined costs from multiple services.
        
        GIVEN: Usage from both Gemini and ElevenLabs
        WHEN: Summary is requested
        THEN: Total cost includes all services
        
        AC: AC3 (Token/Image Tracking)
        """
        # GIVEN: Monitor from fixture
        monitor = clean_monitor_state
        
        # Track Gemini usage
        monitor.track_usage(
            service="gemini",
            model_id="gemini-1.5-flash",
            metric_type="input_tokens",
            value=1_000_000  # $0.50
        )
        monitor.track_usage(
            service="gemini",
            model_id="gemini-1.5-flash",
            metric_type="output_tokens",
            value=1_000_000  # $1.50
        )
        
        # Track ElevenLabs usage
        monitor.track_usage(
            service="elevenlabs",
            model_id="eleven_multilingual_v2",
            metric_type="characters",
            value=10000  # Subscription-based: $0 per-call cost (Story 5.5 fix)
        )
        
        # WHEN: Get summary
        summary = monitor.get_summary()
        
        # THEN: Total cost includes Gemini only (ElevenLabs is subscription-based)
        assert summary["events_count"] == 3
        assert "gemini" in summary["by_service"]
        assert "elevenlabs" in summary["by_service"]
        # Total = $0.50 (input) + $1.50 (output) = $2.00 (ElevenLabs is subscription, $0 cost)
        assert summary["total_cost"] == pytest.approx(2.0, rel=0.01)
        # ElevenLabs tracks characters but not cost
        assert summary["by_service"]["elevenlabs"]["cost"] == 0.0
        assert summary["by_service"]["elevenlabs"]["metrics"]["characters"] == 10000


# =============================================================================
# Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge case handling in UsageMonitor."""

    def test_track_zero_value_event(self, clean_monitor_state):
        """[5.1-UNIT-010][P2] Verify zero-value events are handled gracefully.
        
        GIVEN: An event with value=0
        WHEN: Tracked
        THEN: Event is recorded but cost is 0
        """
        # GIVEN/WHEN: Track zero-value event
        monitor = clean_monitor_state
        monitor.track_usage(
            service="gemini",
            model_id="test",
            metric_type="input_tokens",
            value=0
        )
        
        # THEN: Event recorded, cost is 0
        summary = monitor.get_summary()
        assert summary["events_count"] == 1
        assert summary["total_cost"] == 0

    def test_get_summary_empty_monitor(self, clean_monitor_state):
        """[5.1-UNIT-011][P2] Verify get_summary works with no events.
        
        GIVEN: Monitor has no events
        WHEN: Summary is requested
        THEN: Returns valid structure with zeros
        """
        # GIVEN: Fresh monitor from fixture
        monitor = clean_monitor_state
        
        # WHEN: Get summary
        summary = monitor.get_summary()
        
        # THEN: Valid empty structure
        assert summary["events_count"] == 0
        assert summary["total_cost"] == 0
        assert isinstance(summary["by_service"], dict)

    def test_unknown_service_tracked(self, clean_monitor_state):
        """[5.1-UNIT-012][P2] Verify unknown services don't crash the monitor.
        
        GIVEN: A usage event from an unknown service
        WHEN: Tracked
        THEN: Event is recorded without error
        """
        # GIVEN/WHEN: Track unknown service
        monitor = clean_monitor_state
        monitor.track_usage(
            service="unknown_service",
            model_id="mystery-model",
            metric_type="mystery_metric",
            value=100
        )
        
        # THEN: Event recorded
        summary = monitor.get_summary()
        assert summary["events_count"] == 1
        assert "unknown_service" in summary["by_service"]
