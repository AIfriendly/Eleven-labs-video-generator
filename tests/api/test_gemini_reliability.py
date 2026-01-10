"""
Tests for Gemini Image Generation Reliability & API Compliance (Story 2.3.1)

Covers:
- Safety filter handling and retries (AC3, AC4)
- Defensive response parsing (AC3)
- Dynamic model selection and fallback (AC2, AC6, AC5)
"""
import pytest
from unittest.mock import Mock, patch
from eleven_video.api.gemini import GeminiAdapter
from eleven_video.models.domain import Script, ImageModelInfo
from eleven_video.exceptions.custom_errors import GeminiAPIError

# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def adapter():
    """Create a GeminiAdapter instance with a dummy API key."""
    return GeminiAdapter(api_key="dummy_key")

@pytest.fixture
def mock_genai_client(adapter):
    """Mock the internal Google GenAI client."""
    with patch.object(adapter, "_genai_client") as mock_client:
        yield mock_client

@pytest.fixture
def minimal_script():
    """A minimal script for testing image generation."""
    return Script(content="A beautiful sunset.")

# =============================================================================
# Helper Functions for Mocking
# =============================================================================

def create_mock_response(finish_reason="STOP", has_content=True, has_parts=True, mime_type="image/png", data=b"fake_image_data"):
    """Create a mock generation response matching google-genai SDK structure."""
    mock_response = Mock()
    mock_candidate = Mock()
    mock_candidate.finish_reason = finish_reason
    
    if has_content:
        mock_content = Mock()
        if has_parts:
            mock_part = Mock()
            if data:
                mock_inline_data = Mock()
                mock_inline_data.data = data
                mock_inline_data.mime_type = mime_type
                mock_part.inline_data = mock_inline_data
            else:
                 mock_part.inline_data = None
            
            mock_content.parts = [mock_part]
        else:
            mock_content.parts = []
        mock_candidate.content = mock_content
    else:
        mock_candidate.content = None

    mock_response.candidates = [mock_candidate]
    return mock_response

def create_mock_model(name, display_name=None):
    """Create a mock model object."""
    mock_model = Mock()
    mock_model.name = name
    mock_model.display_name = display_name or name
    return mock_model

# =============================================================================
# Tests: Safety Filter Handling & Retries (AC4)
# =============================================================================

def test_generate_image_retry_on_safety_block_success(adapter, mock_genai_client, minimal_script):
    """[P1] Should retry with modified prompt when blocked by safety filter, then succeed."""
    # Setup mocks
    # Call 1: Safety Block
    response_blocked = create_mock_response(finish_reason="SAFETY", has_content=False)
    # Call 2: Success
    response_success = create_mock_response(finish_reason="STOP")
    
    mock_genai_client.models.generate_content.side_effect = [response_blocked, response_success]
    
    # Execute
    images = adapter.generate_images(minimal_script)
    
    # Assert
    assert len(images) == 1
    assert images[0].data == b"fake_image_data"
    
    # Verify retry logic
    assert mock_genai_client.models.generate_content.call_count == 2
    
    # Check arguments of retry call
    call_args_list = mock_genai_client.models.generate_content.call_args_list
    first_call_prompt = call_args_list[0].kwargs['contents']
    second_call_prompt = call_args_list[1].kwargs['contents']
    
    assert "safe for work" not in first_call_prompt # Initial prompt logic appends style suffix, but not safety suffix
    assert "safe for work" in second_call_prompt # Modified prompt should have safety suffix

def test_generate_image_fail_after_max_retries(adapter, mock_genai_client, minimal_script):
    """[P1] Should raise GeminiAPIError after exhausting retries on persistent safety blocks."""
    # Setup mocks: Always return SAFETY block
    response_blocked = create_mock_response(finish_reason="SAFETY", has_content=False)
    # 1 initial + 2 retries = 3 calls
    mock_genai_client.models.generate_content.side_effect = [response_blocked, response_blocked, response_blocked, response_blocked]
    
    # Execute & Assert
    with pytest.raises(GeminiAPIError) as excinfo:
        adapter.generate_images(minimal_script)
    
    assert "blocked by safety filters" in str(excinfo.value)
    assert mock_genai_client.models.generate_content.call_count == 3 

# =============================================================================
# Tests: Defensive Response Parsing (AC3)
# =============================================================================

def test_generate_image_handle_empty_content(adapter, mock_genai_client, minimal_script):
    """[P1] Should raise GeminiAPIError when response has no content parts (even if not strictly blocked)."""
    # Mock response with finish_reason=STOP but empty parts
    response_empty = create_mock_response(finish_reason="STOP", has_parts=False)
    mock_genai_client.models.generate_content.return_value = response_empty
    
    with pytest.raises(GeminiAPIError) as excinfo:
        adapter.generate_images(minimal_script)
    
    assert "No image data returned" in str(excinfo.value)

def test_generate_image_handle_no_candidates(adapter, mock_genai_client, minimal_script):
    """[P2] Should raise GeminiAPIError when response has no candidates."""
    mock_response = Mock()
    mock_response.candidates = []
    mock_genai_client.models.generate_content.return_value = mock_response
    
    with pytest.raises(GeminiAPIError) as excinfo:
        adapter.generate_images(minimal_script)
    
    assert "no candidates" in str(excinfo.value)

# =============================================================================
# Tests: Dynamic Model Selection (AC2, AC6)
# =============================================================================

def test_resolve_default_image_model_dynamic_discovery(adapter, mock_genai_client):
    """[P1] Should dynamically select valid image model when none specified."""
    # Mock list models response
    mock_genai_client.models.list.return_value = [
        create_mock_model("models/gemini-1.5-flash"), # Text only
        create_mock_model("models/gemini-2.5-flash-image"), # Image capable
        create_mock_model("models/imagen-3.0"), # Image capable
    ]
    
    # Execute - Force cache bypass to ensure list is called
    resolved_model = adapter._resolve_default_image_model(model_id=None)
    
    # Assert
    # Should prefer 'gemini' + 'flash' model as per logic
    assert resolved_model == "gemini-2.5-flash-image"

def test_resolve_default_image_model_user_override(adapter, mock_genai_client):
    """[P1] Should use user-specified model if valid."""
    mock_genai_client.models.list.return_value = [
         create_mock_model("models/imagen-3.0")
    ]
    
    resolved_model = adapter._resolve_default_image_model(model_id="imagen-3.0")
    assert resolved_model == "imagen-3.0"

def test_resolve_default_image_model_fallback_on_invalid(adapter, mock_genai_client):
    """[P2] Should fallback to default if user model is invalid/not found."""
    mock_genai_client.models.list.return_value = [
         create_mock_model("models/gemini-2.5-flash-image")
    ]
    
    # Note: Logic in adapter calls list_image_models via validate_image_model_id
    # If invalid, _resolve_default_image_model falls through to default-model
    # But wait, adapter.generate_images LOGIC is:
    # effective_model_id = self._resolve_default_image_model(model_id)
    # And _resolve_default_image_model says:
    # if model_id and self.validate_image_model_id(model_id): return model_id
    # else: Try dynamic discovery or return DEFAULT.
    
    fallback_model = adapter._resolve_default_image_model(model_id="invalid-model-123")
    assert fallback_model == adapter.IMAGE_MODEL # Should match constant default

def test_list_image_models_filtering(adapter, mock_genai_client):
    """[P1] Should filter out non-image models from list."""
    mock_genai_client.models.list.return_value = [
        create_mock_model("models/gemini-pro"), # Text
        create_mock_model("models/gemini-2.5-flash-image"), # Image
        create_mock_model("models/text-embedding-004"), # Embedding
    ]
    
    models = adapter.list_image_models(use_cache=False)
    
    assert len(models) == 1
    assert models[0].model_id == "gemini-2.5-flash-image"
