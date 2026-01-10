"""Unit tests for model-specific usage metrics (Story 5.2).

Tests cover the `by_model` aggregation in UsageMonitor.get_summary(),
ensuring usage metrics are broken down by individual model IDs.

Test ID Convention: [5.2-UNIT-XXX]
Risk Link: R-001 (Cost Accuracy)
"""
import pytest

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
    # Setup: Reset to clean state
    PricingStrategy.reset()
    monitor = UsageMonitor.get_instance()
    monitor.reset()
    
    yield monitor
    
    # Teardown: Always reset after test (runs even if test fails)
    PricingStrategy.reset()
    monitor.reset()


# =============================================================================
# P0 Tests - Model Separation (Critical)
# =============================================================================

def test_model_specific_aggregation(clean_monitor_state):
    """[5.2-UNIT-001][P0] Verify get_summary() separates usage by model ID.
    
    GIVEN: Multiple usage events from different Gemini models
    WHEN: get_summary() is called
    THEN: The 'by_model' dict contains separate entries for each model ID
          with correct token counts and costs
    
    Risk: R-001 (Cost Accuracy)
    """
    # GIVEN: Clean monitor from fixture
    monitor = clean_monitor_state
    
    # Track usage for two different Gemini models
    monitor.track_usage(
        service="gemini",
        model_id="gemini-2.5-flash",
        metric_type="input_tokens",
        value=500_000  # 500K input tokens
    )
    monitor.track_usage(
        service="gemini",
        model_id="gemini-2.5-flash",
        metric_type="output_tokens",
        value=100_000  # 100K output tokens
    )
    monitor.track_usage(
        service="gemini",
        model_id="gemini-2.5-pro",
        metric_type="input_tokens",
        value=200_000  # 200K input tokens from Pro model
    )
    
    # WHEN: Get summary
    summary = monitor.get_summary()
    
    # THEN: 'by_model' exists and contains both models
    assert "by_model" in summary, "get_summary() must include 'by_model' key"
    
    by_model = summary["by_model"]
    assert "gemini-2.5-flash" in by_model, "Flash model should be in by_model"
    assert "gemini-2.5-pro" in by_model, "Pro model should be in by_model"
    
    # Verify Flash model metrics
    flash_data = by_model["gemini-2.5-flash"]
    assert flash_data["metrics"]["input_tokens"] == 500_000
    assert flash_data["metrics"]["output_tokens"] == 100_000
    
    # Verify Pro model metrics  
    pro_data = by_model["gemini-2.5-pro"]
    assert pro_data["metrics"]["input_tokens"] == 200_000


def test_same_model_aggregation(clean_monitor_state):
    """[5.2-UNIT-002][P0] Verify same model_id aggregates multiple calls.
    
    GIVEN: Multiple usage events from the same model ID
    WHEN: get_summary() is called
    THEN: All usage is aggregated under one model entry
    
    Risk: R-001 (Cost Accuracy)
    """
    # GIVEN: Clean monitor from fixture
    monitor = clean_monitor_state
    
    # Track multiple usages for the same model
    monitor.track_usage(
        service="gemini",
        model_id="gemini-2.5-flash",
        metric_type="input_tokens",
        value=100_000
    )
    monitor.track_usage(
        service="gemini",
        model_id="gemini-2.5-flash",
        metric_type="input_tokens",
        value=150_000
    )
    monitor.track_usage(
        service="gemini",
        model_id="gemini-2.5-flash",
        metric_type="input_tokens",
        value=50_000
    )
    
    # WHEN: Get summary
    summary = monitor.get_summary()
    
    # THEN: Total should be aggregated
    assert "by_model" in summary
    flash_data = summary["by_model"]["gemini-2.5-flash"]
    assert flash_data["metrics"]["input_tokens"] == 300_000  # 100K + 150K + 50K


def test_model_cost_calculation(clean_monitor_state):
    """[5.2-UNIT-003][P0] Verify per-model cost calculation is accurate.
    
    GIVEN: Usage events from multiple models with known token counts
    WHEN: get_summary() is called
    THEN: Each model in 'by_model' has accurate cost subtotal
    
    Risk: R-001 (Cost Accuracy - $0.0001 precision required)
    """
    # GIVEN: Clean monitor from fixture
    monitor = clean_monitor_state
    
    # Track exactly 1M input tokens for Flash (cost = $0.50 at default rate)
    monitor.track_usage(
        service="gemini",
        model_id="gemini-2.5-flash",
        metric_type="input_tokens",
        value=1_000_000
    )
    
    # Track exactly 1M input tokens for Pro (also $0.50 at default rate)
    monitor.track_usage(
        service="gemini",
        model_id="gemini-2.5-pro",
        metric_type="input_tokens",
        value=1_000_000
    )
    
    # WHEN: Get summary
    summary = monitor.get_summary()
    
    # THEN: Each model should have $0.50 cost
    by_model = summary["by_model"]
    
    assert abs(by_model["gemini-2.5-flash"]["cost"] - 0.50) < 0.0001, \
        "Flash model cost should be $0.50 for 1M input tokens"
    assert abs(by_model["gemini-2.5-pro"]["cost"] - 0.50) < 0.0001, \
        "Pro model cost should be $0.50 for 1M input tokens"


# =============================================================================
# P1 Tests - Mixed Services Model Breakdown
# =============================================================================

def test_mixed_service_model_breakdown(clean_monitor_state):
    """[5.2-UNIT-004][P1] Verify ElevenLabs voice model appears in by_model.
    
    GIVEN: Usage events from both Gemini (text model) and ElevenLabs (voice model)
    WHEN: get_summary() is called
    THEN: Both model IDs appear in 'by_model' with correct metrics
    
    AC: #4 - ElevenLabs voice model ID is also broken down
    """
    # GIVEN: Clean monitor from fixture
    monitor = clean_monitor_state
    
    # Track Gemini text model usage
    monitor.track_usage(
        service="gemini",
        model_id="gemini-2.5-flash",
        metric_type="input_tokens",
        value=500_000
    )
    
    # Track ElevenLabs voice model usage (voice ID)
    monitor.track_usage(
        service="elevenlabs",
        model_id="21m00Tcm4TlvDq8ikWAM",  # Adam voice ID
        metric_type="characters",
        value=5000
    )
    
    # WHEN: Get summary
    summary = monitor.get_summary()
    
    # THEN: Both models appear in by_model
    assert "by_model" in summary
    by_model = summary["by_model"]
    
    assert "gemini-2.5-flash" in by_model, "Gemini model should appear"
    assert "21m00Tcm4TlvDq8ikWAM" in by_model, "ElevenLabs voice ID should appear"
    
    # Verify ElevenLabs metrics
    el_data = by_model["21m00Tcm4TlvDq8ikWAM"]
    assert el_data["metrics"]["characters"] == 5000


def test_image_model_in_by_model(clean_monitor_state):
    """[5.2-UNIT-005][P1] Verify image generation model appears in by_model.
    
    GIVEN: Usage events from text, image, and TTS models
    WHEN: get_summary() is called
    THEN: Image model ID appears with image count metric
    """
    # GIVEN: Clean monitor from fixture
    monitor = clean_monitor_state
    
    # Track text model usage
    monitor.track_usage(
        service="gemini",
        model_id="gemini-2.5-flash",
        metric_type="input_tokens",
        value=100_000
    )
    
    # Track image model usage
    monitor.track_usage(
        service="gemini",
        model_id="gemini-2.5-flash-image",
        metric_type="images",
        value=5  # 5 images generated
    )
    
    # WHEN: Get summary
    summary = monitor.get_summary()
    
    # THEN: Both models appear in by_model
    assert "by_model" in summary
    by_model = summary["by_model"]
    
    assert "gemini-2.5-flash" in by_model, "Text model should appear"
    assert "gemini-2.5-flash-image" in by_model, "Image model should appear"
    
    # Verify image metrics
    image_data = by_model["gemini-2.5-flash-image"]
    assert image_data["metrics"]["images"] == 5


# =============================================================================
# P2 Tests - Edge Cases
# =============================================================================

def test_empty_usage_has_empty_by_model(clean_monitor_state):
    """[5.2-UNIT-006][P2] Verify empty usage returns empty by_model dict.
    
    GIVEN: No usage events tracked
    WHEN: get_summary() is called
    THEN: 'by_model' is an empty dict
    """
    # GIVEN: Clean monitor from fixture (no events)
    monitor = clean_monitor_state
    
    # WHEN: Get summary without tracking anything
    summary = monitor.get_summary()
    
    # THEN: by_model should be empty dict
    assert "by_model" in summary
    assert summary["by_model"] == {}


def test_by_model_matches_by_service_total(clean_monitor_state):
    """[5.2-UNIT-007][P2] Verify by_model costs sum to by_service costs.
    
    GIVEN: Multiple models from the same service
    WHEN: get_summary() is called
    THEN: Sum of by_model costs for a service equals by_service cost
    """
    # GIVEN: Clean monitor from fixture
    monitor = clean_monitor_state
    
    # Track multiple Gemini models
    monitor.track_usage(
        service="gemini",
        model_id="gemini-2.5-flash",
        metric_type="input_tokens",
        value=1_000_000  # $0.50
    )
    monitor.track_usage(
        service="gemini",
        model_id="gemini-2.5-pro",
        metric_type="input_tokens",
        value=1_000_000  # $0.50
    )
    
    # WHEN: Get summary
    summary = monitor.get_summary()
    
    # THEN: by_model costs sum to by_service cost
    by_model = summary["by_model"]
    by_service = summary["by_service"]
    
    flash_cost = by_model["gemini-2.5-flash"]["cost"]
    pro_cost = by_model["gemini-2.5-pro"]["cost"]
    gemini_total_cost = by_service["gemini"]["cost"]
    
    assert abs((flash_cost + pro_cost) - gemini_total_cost) < 0.0001, \
        "Sum of model costs should equal service cost"
