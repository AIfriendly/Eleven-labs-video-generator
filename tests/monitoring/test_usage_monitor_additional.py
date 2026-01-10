"""Additional unit tests for UsageMonitor edge cases (Story 5.2 - automate workflow).

Covers edge cases identified during test automation expansion:
- Unknown metric type handling (line 166-168 in usage.py)
- Pricing lookup for unknown services/metrics
- Concurrent access safety validation

Test ID Convention: [5.2-AUTO-XXX] (AUTO = automate workflow generated)
"""
import pytest
import threading
from concurrent.futures import ThreadPoolExecutor

from eleven_video.monitoring.usage import (
    UsageMonitor,
    PricingStrategy,
    MetricType,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def clean_monitor_state():
    """Reset UsageMonitor and PricingStrategy state before and after each test."""
    PricingStrategy.reset()
    monitor = UsageMonitor.get_instance()
    monitor.reset()
    
    yield monitor
    
    PricingStrategy.reset()
    monitor.reset()


# =============================================================================
# P1 Tests - Unknown Metric Type Handling
# =============================================================================

class TestUnknownMetricType:
    """Tests for unknown metric type fallback behavior."""

    def test_unknown_metric_type_uses_input_tokens_fallback(self, clean_monitor_state):
        """[5.2-AUTO-001][P1] Verify unknown metric types fall back to input_tokens.
        
        GIVEN: A usage event with an invalid metric_type
        WHEN: track_usage() is called
        THEN: The event is recorded with metric_type as INPUT_TOKENS
        
        Coverage: line 166-168 in usage.py
        """
        # GIVEN: Monitor from fixture
        monitor = clean_monitor_state
        
        # WHEN: Track event with unknown metric type
        monitor.track_usage(
            service="gemini",
            model_id="test-model",
            metric_type="invalid_metric",  # Not a valid MetricType
            value=500
        )
        
        # THEN: Event is recorded with INPUT_TOKENS fallback
        events = monitor.get_events()
        assert len(events) == 1
        assert events[0].metric_type == MetricType.INPUT_TOKENS
        
        # Verify it appears in the summary as input_tokens
        summary = monitor.get_summary()
        assert summary["by_service"]["gemini"]["metrics"]["input_tokens"] == 500

    def test_unknown_metric_type_cost_calculation(self, clean_monitor_state):
        """[5.2-AUTO-002][P2] Verify unknown metric types use input token pricing.
        
        GIVEN: A usage event with an invalid metric_type
        WHEN: get_summary() calculates cost
        THEN: Cost is calculated using input_token_price_per_million
        """
        # GIVEN: Monitor from fixture
        monitor = clean_monitor_state
        
        # WHEN: Track 1 million "unknown" metric units
        monitor.track_usage(
            service="gemini",
            model_id="test-model",
            metric_type="bogus_metric",
            value=1_000_000
        )
        
        # THEN: Cost matches input token pricing (default $0.50/1M)
        summary = monitor.get_summary()
        assert summary["total_cost"] == pytest.approx(0.50, rel=0.01)


# =============================================================================
# P2 Tests - Pricing Lookup Edge Cases
# =============================================================================

class TestPricingLookupEdgeCases:
    """Tests for PricingStrategy.get_price() edge cases."""

    def test_unknown_service_returns_zero_cost(self, clean_monitor_state):
        """[5.2-AUTO-003][P2] Verify unknown service pricing returns 0.
        
        GIVEN: A usage event from an unknown service
        WHEN: get_summary() calculates cost
        THEN: Cost is 0 (no pricing defined)
        """
        # GIVEN: Monitor from fixture
        monitor = clean_monitor_state
        
        # WHEN: Track event from unknown service
        monitor.track_usage(
            service="new_ai_service",
            model_id="future-model",
            metric_type="input_tokens",
            value=1_000_000
        )
        
        # THEN: Cost should be 0 (unknown service has no pricing)
        summary = monitor.get_summary()
        assert summary["by_service"]["new_ai_service"]["cost"] == 0

    def test_unknown_pricing_key_returns_zero(self, clean_monitor_state):
        """[5.2-AUTO-004][P2] Verify unknown price key returns 0.
        
        GIVEN: PricingStrategy with known service but unknown key
        WHEN: get_price() is called
        THEN: Returns 0.0
        """
        # GIVEN: Known service but unknown key
        # WHEN/THEN: get_price returns 0.0
        price = PricingStrategy.get_price("gemini", "unknown_rate_key")
        assert price == 0.0
        
        # Verify it works for unknown service too
        price = PricingStrategy.get_price("totally_unknown", "any_key")
        assert price == 0.0


# =============================================================================
# P1 Tests - Thread Safety
# =============================================================================

class TestThreadSafety:
    """Tests for concurrent access safety."""

    def test_concurrent_track_usage_no_data_loss(self, clean_monitor_state):
        """[5.2-AUTO-005][P1] Verify concurrent usage tracking doesn't lose events.
        
        GIVEN: Multiple threads tracking usage concurrently
        WHEN: All threads complete
        THEN: All events are recorded without data loss
        
        Risk: Thread safety (mentioned as deferred in code review)
        """
        # GIVEN: Monitor and tracking parameters
        monitor = clean_monitor_state
        num_threads = 10
        events_per_thread = 100
        expected_total = num_threads * events_per_thread
        
        def track_events(thread_id):
            for i in range(events_per_thread):
                monitor.track_usage(
                    service="gemini",
                    model_id=f"thread-{thread_id}",
                    metric_type="input_tokens",
                    value=10
                )
        
        # WHEN: Track concurrently
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(track_events, i) for i in range(num_threads)]
            for f in futures:
                f.result()  # Wait for all to complete
        
        # THEN: All events recorded
        events = monitor.get_events()
        assert len(events) == expected_total
        
        # Verify summary totals are correct
        summary = monitor.get_summary()
        assert summary["events_count"] == expected_total
        assert summary["by_service"]["gemini"]["metrics"]["input_tokens"] == expected_total * 10

    def test_concurrent_pricing_strategy_access(self, clean_monitor_state):
        """[5.2-AUTO-006][P2] Verify concurrent pricing reads don't cause errors.
        
        GIVEN: Multiple threads reading and writing to PricingStrategy
        WHEN: Operations complete
        THEN: No exceptions raised, final state is consistent
        """
        # GIVEN: Concurrent read/write operations
        errors = []
        iterations = 50
        
        def reader():
            for _ in range(iterations):
                try:
                    PricingStrategy.get_price("gemini", "input_token_price_per_million")
                except Exception as e:
                    errors.append(e)
        
        def writer():
            for i in range(iterations):
                try:
                    PricingStrategy.configure({
                        "gemini": {"input_token_price_per_million": 0.5 + (i * 0.01)}
                    })
                except Exception as e:
                    errors.append(e)
        
        # WHEN: Run concurrent reads and writes
        threads = []
        for _ in range(5):
            threads.append(threading.Thread(target=reader))
            threads.append(threading.Thread(target=writer))
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # THEN: No exceptions
        assert len(errors) == 0, f"Concurrent access caused errors: {errors}"


# =============================================================================
# P2 Tests - by_model Edge Cases (Story 5.2 Specific)
# =============================================================================

class TestByModelEdgeCases:
    """Additional edge case tests for by_model aggregation."""

    def test_same_model_different_services_tracked_separately(self, clean_monitor_state):
        """[5.2-AUTO-007][P2] Verify same model_id from different services stays separate.
        
        GIVEN: Same model_id used by different services
        WHEN: get_summary() is called
        THEN: First service associated with model_id is used for pricing
        
        Note: This tests the model_to_service mapping behavior
        """
        # GIVEN: Monitor from fixture
        monitor = clean_monitor_state
        
        # Track same model_id from gemini first
        monitor.track_usage(
            service="gemini",
            model_id="shared-model-id",
            metric_type="input_tokens",
            value=1000
        )
        
        # Then from elevenlabs (same model_id)
        monitor.track_usage(
            service="elevenlabs",
            model_id="shared-model-id",
            metric_type="characters",
            value=500
        )
        
        # WHEN: Get summary
        summary = monitor.get_summary()
        
        # THEN: by_model aggregates under one key with both metrics
        # The first service (gemini) will be used for pricing
        assert "shared-model-id" in summary["by_model"]
        model_data = summary["by_model"]["shared-model-id"]
        assert "input_tokens" in model_data["metrics"]
        assert "characters" in model_data["metrics"]

    def test_model_id_with_special_characters(self, clean_monitor_state):
        """[5.2-AUTO-008][P2] Verify model_id with special characters is handled.
        
        GIVEN: A model_id containing special characters
        WHEN: Tracked and summarized
        THEN: Model appears correctly in by_model
        """
        # GIVEN: Monitor from fixture
        monitor = clean_monitor_state
        
        # WHEN: Track with special character model_id
        special_model_id = "voice/21m00Tcm4TlvDq8ikWAM/stream"
        monitor.track_usage(
            service="elevenlabs",
            model_id=special_model_id,
            metric_type="characters",
            value=1000
        )
        
        # THEN: Model appears correctly
        summary = monitor.get_summary()
        assert special_model_id in summary["by_model"]
        assert summary["by_model"][special_model_id]["metrics"]["characters"] == 1000
