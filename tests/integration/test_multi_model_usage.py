"""Integration tests for multi-model usage tracking (Story 5.2).

Tests verify that the full monitoring flow correctly tracks and reports
usage across multiple models in a realistic pipeline scenario.

Test ID Convention: [5.2-INT-XXX]
"""
import pytest

from eleven_video.monitoring.usage import UsageMonitor, PricingStrategy


@pytest.fixture(autouse=True)
def clean_monitor_state():
    """Reset UsageMonitor and PricingStrategy for test isolation."""
    PricingStrategy.reset()
    monitor = UsageMonitor.get_instance()
    monitor.reset()
    
    yield monitor
    
    PricingStrategy.reset()
    monitor.reset()


def test_multi_model_pipeline_usage_tracking(clean_monitor_state):
    """[5.2-INT-001][P1] Verify multi-model usage in realistic pipeline flow.
    
    GIVEN: A simulated video generation pipeline using:
           - gemini-2.5-flash for script generation (text)
           - gemini-2.5-flash-image for image generation
           - ElevenLabs voice for TTS
    WHEN: All API calls are completed and summary is requested
    THEN: by_model contains all three model IDs with correct metrics
    
    This simulates the actual usage pattern in VideoPipeline.
    """
    # GIVEN: Clean monitor from fixture
    monitor = clean_monitor_state
    
    # Simulate script generation (Gemini text model)
    # Typical script generation: ~500 input tokens, ~2000 output tokens
    monitor.track_usage(
        service="gemini",
        model_id="gemini-2.5-flash",
        metric_type="input_tokens",
        value=500
    )
    monitor.track_usage(
        service="gemini",
        model_id="gemini-2.5-flash",
        metric_type="output_tokens",
        value=2000
    )
    
    # Simulate image generation (Gemini image model)
    # Generate 5 images for a ~1 minute video
    for _ in range(5):
        # Each image generation uses some input tokens for the prompt
        monitor.track_usage(
            service="gemini",
            model_id="gemini-2.5-flash-image",
            metric_type="input_tokens",
            value=100
        )
        monitor.track_usage(
            service="gemini",
            model_id="gemini-2.5-flash-image",
            metric_type="images",
            value=1
        )
    
    # Simulate TTS (ElevenLabs)
    # 2000 character script
    monitor.track_usage(
        service="elevenlabs",
        model_id="21m00Tcm4TlvDq8ikWAM",  # Adam voice
        metric_type="characters",
        value=2000
    )
    
    # WHEN: Get the summary
    summary = monitor.get_summary()
    
    # THEN: All models appear in by_model
    assert "by_model" in summary, "Summary must include by_model breakdown"
    by_model = summary["by_model"]
    
    # Verify all three models present
    assert "gemini-2.5-flash" in by_model, "Text model should be tracked"
    assert "gemini-2.5-flash-image" in by_model, "Image model should be tracked"
    assert "21m00Tcm4TlvDq8ikWAM" in by_model, "Voice model should be tracked"
    
    # Verify text model metrics
    text_model = by_model["gemini-2.5-flash"]
    assert text_model["metrics"]["input_tokens"] == 500
    assert text_model["metrics"]["output_tokens"] == 2000
    
    # Verify image model metrics (5 images, 500 total input tokens)
    image_model = by_model["gemini-2.5-flash-image"]
    assert image_model["metrics"]["input_tokens"] == 500  # 5 * 100
    assert image_model["metrics"]["images"] == 5
    
    # Verify TTS metrics
    tts_model = by_model["21m00Tcm4TlvDq8ikWAM"]
    assert tts_model["metrics"]["characters"] == 2000
    
    # Verify costs are present for each model
    assert "cost" in text_model
    assert "cost" in image_model
    assert "cost" in tts_model
    
    # Verify all costs are non-negative
    assert text_model["cost"] >= 0
    assert image_model["cost"] >= 0
    assert tts_model["cost"] >= 0


def test_by_model_consistency_with_events(clean_monitor_state):
    """[5.2-INT-002][P2] Verify by_model is consistent with raw events.
    
    GIVEN: Multiple usage events tracked
    WHEN: get_summary() and get_events() are called
    THEN: by_model aggregation matches manual event aggregation
    """
    # GIVEN: Clean monitor from fixture
    monitor = clean_monitor_state
    
    # Track some events
    monitor.track_usage("gemini", "model-a", "input_tokens", 1000)
    monitor.track_usage("gemini", "model-a", "input_tokens", 500)
    monitor.track_usage("gemini", "model-b", "input_tokens", 2000)
    
    # WHEN: Get both summary and raw events
    summary = monitor.get_summary()
    events = monitor.get_events()
    
    # Calculate expected aggregation from events
    model_totals = {}
    for event in events:
        if event.model_id not in model_totals:
            model_totals[event.model_id] = {}
        metric = event.metric_type.value
        if metric not in model_totals[event.model_id]:
            model_totals[event.model_id][metric] = 0
        model_totals[event.model_id][metric] += event.value
    
    # THEN: by_model matches manual aggregation
    assert "by_model" in summary
    by_model = summary["by_model"]
    
    for model_id, expected_metrics in model_totals.items():
        assert model_id in by_model, f"Model {model_id} should be in by_model"
        actual_metrics = by_model[model_id]["metrics"]
        for metric, expected_value in expected_metrics.items():
            assert actual_metrics[metric] == expected_value, \
                f"Model {model_id} {metric} should be {expected_value}"
