"""
Pytest fixtures for API adapter tests.

Provides common mocking patterns for google-genai SDK and other API adapters.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock


@pytest.fixture
def mock_genai():
    """
    Fixture providing mocked google-genai SDK (new SDK).
    
    Yields:
        tuple: (mock_client_cls, mock_client, mock_response)
        
    Usage:
        def test_example(mock_genai):
            mock_client_cls, mock_client, mock_response = mock_genai
            # ... test code
    """
    with patch("eleven_video.api.gemini.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_response = MagicMock()
        
        # Setup text generation response (for generate_script)
        mock_text_part = MagicMock()
        mock_text_part.text = "Generated script content"
        
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].content.parts = [mock_text_part]
        mock_response.candidates[0].content.parts[0].text = "Generated script content"
        mock_client.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_client
        
        yield mock_client_cls, mock_client, mock_response


@pytest.fixture
def mock_genai_error():
    """
    Fixture providing mocked google-genai SDK that raises errors.
    
    Yields:
        tuple: (mock_client_cls, mock_client, set_error_func)
        
    Usage:
        def test_error(mock_genai_error):
            mock_client_cls, mock_client, set_error = mock_genai_error
            set_error(Exception("401 Unauthorized"))
            # ... test code
    """
    with patch("eleven_video.api.gemini.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        
        def set_error(error):
            mock_client.models.generate_content.side_effect = error
        
        yield mock_client_cls, mock_client, set_error


@pytest.fixture
def gemini_adapter():
    """
    Fixture providing a GeminiAdapter instance with mocked SDK.
    
    Yields:
        GeminiAdapter: Configured adapter for testing
    """
    with patch("eleven_video.api.gemini.genai.Client"):
        from eleven_video.api.gemini import GeminiAdapter
        adapter = GeminiAdapter(api_key="test-key-fixture")
        yield adapter


# =============================================================================
# Story 2.3 Fixtures - New google-genai SDK
# =============================================================================


@pytest.fixture
def mock_genai_new_sdk():
    """
    Fixture providing mocked google-genai SDK (NEW) for text generation.
    
    Yields:
        tuple: (mock_client_cls, mock_client, mock_response)
        
    Usage:
        def test_example(mock_genai_new_sdk):
            mock_client_cls, mock_client, mock_response = mock_genai_new_sdk
            # ... test code
    """
    with patch("eleven_video.api.gemini.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_response = MagicMock()
        
        # Setup text generation response (for generate_script)
        mock_text_part = MagicMock()
        mock_text_part.text = "Generated script content"
        mock_text_part.inline_data = None
        
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].content.parts = [mock_text_part]
        mock_client.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_client
        
        yield mock_client_cls, mock_client, mock_response


@pytest.fixture
def mock_genai_new_sdk_image():
    """
    Fixture providing mocked google-genai SDK for image generation.
    
    Returns mock responses with inline_data for image bytes.
    
    Yields:
        tuple: (mock_client_cls, mock_client, mock_response)
    """
    with patch("eleven_video.api.gemini.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_response = MagicMock()
        
        # Setup image generation response
        mock_image_part = MagicMock()
        mock_image_part.inline_data = MagicMock()
        mock_image_part.inline_data.data = b"fake_png_bytes"
        mock_image_part.inline_data.mime_type = "image/png"
        
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].content.parts = [mock_image_part]
        mock_client.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_client
        
        yield mock_client_cls, mock_client, mock_response


@pytest.fixture
def mock_genai_new_sdk_error():
    """
    Fixture providing mocked google-genai SDK that raises errors.
    
    Yields:
        tuple: (mock_client_cls, mock_client, set_error_func)
        
    Usage:
        def test_error(mock_genai_new_sdk_error):
            mock_client_cls, mock_client, set_error = mock_genai_new_sdk_error
            set_error(Exception("401 Unauthorized"))
            # ... test code
    """
    with patch("eleven_video.api.gemini.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        
        def set_error(error):
            mock_client.models.generate_content.side_effect = error
        
        yield mock_client_cls, mock_client, set_error
