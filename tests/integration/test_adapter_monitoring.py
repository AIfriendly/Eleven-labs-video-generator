"""Integration tests for adapter monitoring (Story 5.1).

Verifies that GeminiAdapter and ElevenLabsAdapter correctly
report usage to UsageMonitor.
"""
import pytest
from unittest.mock import MagicMock, patch

from eleven_video.api.gemini import GeminiAdapter
from eleven_video.api.elevenlabs import ElevenLabsAdapter
from eleven_video.monitoring.usage import UsageMonitor, PricingStrategy
from tests.support.factories.api_response_factory import (
    create_gemini_response,
    create_elevenlabs_response,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def clean_monitor_state():
    """Reset UsageMonitor and PricingStrategy state before and after each test.
    
    Ensures test isolation for all adapter monitoring tests.
    """
    PricingStrategy.reset()
    monitor = UsageMonitor.get_instance()
    monitor.reset()
    
    yield monitor
    
    PricingStrategy.reset()
    monitor.reset()


@pytest.fixture
def gemini_adapter():
    """Create a GeminiAdapter with fake API key for testing."""
    return GeminiAdapter(api_key="fake-api-key")


@pytest.fixture
def elevenlabs_adapter():
    """Create an ElevenLabsAdapter with fake API key for testing."""
    adapter = ElevenLabsAdapter(api_key="fake-api-key")
    # Mock voice validation to avoid API call
    adapter.validate_voice_id = MagicMock(return_value=True)
    return adapter


# =============================================================================
# GeminiAdapter Tests
# =============================================================================

def test_gemini_reports_usage_metadata(clean_monitor_state, gemini_adapter):
    """[5.1-INT-001][P0] Verify GeminiAdapter extracts and reports usage_metadata.
    
    GIVEN: A GeminiAdapter with mocked SDK client
    WHEN: generate_script is called
    THEN: UsageMonitor receives input_tokens and output_tokens events
    
    Risk: R-003 (API schema changes)
    """
    # GIVEN: Mock response using factory
    mock_response = create_gemini_response({
        "text": "Generated script content",
        "input_tokens": 50,
        "output_tokens": 100
    })
    gemini_adapter._genai_client.models.generate_content = MagicMock(return_value=mock_response)
    
    # WHEN: Generate script
    result = gemini_adapter.generate_script("test prompt")
    
    # THEN: Verify script was generated
    assert result.content == "Generated script content"
    
    # AND: Verify monitor received usage events
    events = clean_monitor_state.get_events()
    assert len(events) >= 2, f"Expected at least 2 events, got {len(events)}"
    
    # Check for input_tokens event
    input_events = [e for e in events if e.metric_type.value == "input_tokens"]
    assert len(input_events) == 1
    assert input_events[0].value == 50
    assert input_events[0].service == "gemini"
    
    # Check for output_tokens event
    output_events = [e for e in events if e.metric_type.value == "output_tokens"]
    assert len(output_events) == 1
    assert output_events[0].value == 100


# =============================================================================
# ElevenLabsAdapter Tests
# =============================================================================

def test_elevenlabs_reports_char_count(clean_monitor_state, elevenlabs_adapter):
    """[5.1-INT-002][P0] Verify ElevenLabsAdapter reports character counts.
    
    GIVEN: An ElevenLabsAdapter with mocked SDK client
    WHEN: generate_speech is called with text
    THEN: UsageMonitor receives a characters event with correct count
    
    Risk: R-003 (API schema changes)
    """
    # GIVEN: Mock response using factory
    mock_response = create_elevenlabs_response({"chunk_count": 2})
    
    mock_sdk = MagicMock()
    mock_sdk.text_to_speech.convert = MagicMock(return_value=mock_response)
    elevenlabs_adapter._sdk_client = mock_sdk
    
    # WHEN: Generate speech
    text = "Hello world, this is a test"
    result = elevenlabs_adapter.generate_speech(text, voice_id="test-voice-id")
    
    # THEN: Verify audio was generated
    assert result.data == b"audio_chunk_0audio_chunk_1"
    
    # AND: Verify monitor received character event
    events = clean_monitor_state.get_events()
    char_events = [e for e in events if e.metric_type.value == "characters"]
    assert len(char_events) == 1
    assert char_events[0].value == len(text)
    assert char_events[0].service == "elevenlabs"


# =============================================================================
# Accumulation Tests
# =============================================================================

def test_monitor_accumulates_events(clean_monitor_state, gemini_adapter):
    """[5.1-INT-003][P0] Verify multiple events sum up correctly (AC3).
    
    GIVEN: A GeminiAdapter with mocked responses
    WHEN: generate_script is called multiple times
    THEN: UsageMonitor accumulates all token counts correctly
    """
    # GIVEN: Mock response with consistent token counts
    mock_response = create_gemini_response({
        "text": "Content",
        "input_tokens": 100,
        "output_tokens": 200
    })
    gemini_adapter._genai_client.models.generate_content = MagicMock(return_value=mock_response)
    
    # WHEN: Generate twice
    gemini_adapter.generate_script("prompt 1")
    gemini_adapter.generate_script("prompt 2")
    
    # THEN: Verify accumulation (2 calls × 100/200 tokens each)
    summary = clean_monitor_state.get_summary()
    assert summary["by_service"]["gemini"]["metrics"]["input_tokens"] == 200
    assert summary["by_service"]["gemini"]["metrics"]["output_tokens"] == 400
