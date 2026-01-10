"""Unit tests for UsageMonitor core functionality (Story 5.1).

Tests cover singleton pattern, default cost calculation, and custom pricing overrides.
"""
import pytest
from unittest.mock import patch, MagicMock

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
    # Setup: Reset to clean state
    PricingStrategy.reset()
    monitor = UsageMonitor.get_instance()
    monitor.reset()
    
    yield monitor
    
    # Teardown: Always reset after test (runs even if test fails)
    PricingStrategy.reset()
    monitor.reset()


@pytest.fixture
def custom_pricing_config():
    """Configure custom pricing for Gemini and ensure cleanup.
    
    Yields the custom pricing dict for assertion if needed.
    PricingStrategy is automatically reset by clean_monitor_state fixture.
    """
    custom_pricing = create_pricing_config({
        "gemini": {
            "input_token_price_per_million": 2.00  # Higher mock rate for testing
        }
    })
    PricingStrategy.configure(custom_pricing)
    yield custom_pricing


# =============================================================================
# Tests
# =============================================================================

def test_singleton_pattern():
    """[5.1-UNIT-001][P0] Verify UsageMonitor works as a singleton.
    
    GIVEN: No prior UsageMonitor instances
    WHEN: get_instance() is called multiple times
    THEN: The same instance is returned each time
    """
    monitor1 = UsageMonitor.get_instance()
    monitor2 = UsageMonitor.get_instance()
    assert monitor1 is monitor2


def test_calculate_cost_gemini_default(clean_monitor_state):
    """[5.1-UNIT-002][P0] Verify cost calculation using default rates.
    
    GIVEN: Default pricing configuration is active
    WHEN: 1M input tokens are tracked for Gemini
    THEN: Cost should be $0.50 (default rate)
    
    Risk: R-001 (Cost Accuracy)
    """
    # GIVEN: clean_monitor_state fixture provides reset monitor
    monitor = clean_monitor_state
    
    # WHEN: Track 1M input tokens
    monitor.track_usage(
        service="gemini",
        model_id="gemini-1.5-flash",
        metric_type="input_tokens",
        value=1_000_000
    )
    
    # THEN: Cost should be $0.50 at default rate
    summary = monitor.get_summary()
    assert summary["total_cost"] == 0.50


def test_calculate_cost_with_overrides(clean_monitor_state, custom_pricing_config):
    """[5.1-UNIT-003][P0] Verify custom pricing config overrides defaults.
    
    GIVEN: Custom pricing configuration with $2.00/1M tokens
    WHEN: 1M input tokens are tracked for Gemini
    THEN: Cost should be $2.00 (custom rate)
    
    Risk: R-001 (Cost Accuracy)
    """
    # GIVEN: custom_pricing_config fixture configures $2.00/1M
    monitor = clean_monitor_state
    
    # WHEN: Track 1M input tokens
    monitor.track_usage(
        service="gemini",
        model_id="gemini-1.5-flash",
        metric_type="input_tokens",
        value=1_000_000
    )
    
    # THEN: Cost should be $2.00 (custom rate from fixture)
    summary = monitor.get_summary()
    assert summary["total_cost"] == 2.00
