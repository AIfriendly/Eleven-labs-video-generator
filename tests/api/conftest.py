"""
Pytest fixtures for API adapter tests.

Provides common mocking patterns for Google Generative AI SDK and other API adapters.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock


@pytest.fixture
def mock_genai():
    """
    Fixture providing mocked google.generativeai SDK.
    
    Yields:
        tuple: (mock_model_cls, mock_model, mock_response)
        
    Usage:
        def test_example(mock_genai):
            mock_model_cls, mock_model, mock_response = mock_genai
            mock_response.text = "Custom response"
            # ... test code
    """
    with patch("google.generativeai.configure"), \
         patch("google.generativeai.GenerativeModel") as mock_model_cls:
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Generated script content"
        mock_model.generate_content.return_value = mock_response
        mock_model_cls.return_value = mock_model
        yield mock_model_cls, mock_model, mock_response


@pytest.fixture
def mock_genai_error():
    """
    Fixture providing mocked google.generativeai SDK that raises errors.
    
    Yields:
        tuple: (mock_model_cls, mock_model, set_error_func)
        
    Usage:
        def test_error(mock_genai_error):
            mock_model_cls, mock_model, set_error = mock_genai_error
            set_error(Exception("401 Unauthorized"))
            # ... test code
    """
    with patch("google.generativeai.configure"), \
         patch("google.generativeai.GenerativeModel") as mock_model_cls:
        mock_model = MagicMock()
        mock_model_cls.return_value = mock_model
        
        def set_error(error):
            mock_model.generate_content.side_effect = error
        
        yield mock_model_cls, mock_model, set_error


@pytest.fixture
def gemini_adapter():
    """
    Fixture providing a GeminiAdapter instance with mocked SDK.
    
    Yields:
        GeminiAdapter: Configured adapter for testing
    """
    with patch("google.generativeai.configure"):
        from eleven_video.api.gemini import GeminiAdapter
        adapter = GeminiAdapter(api_key="test-key-fixture")
        yield adapter
