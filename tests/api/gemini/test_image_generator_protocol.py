"""
Tests for ImageGenerator protocol (Story 2.3).

Test IDs: 2.3-UNIT-016a, 2.3-UNIT-016b
Tests verify the ImageGenerator protocol exists and GeminiAdapter implements it.
"""
import pytest
from unittest.mock import patch


class TestImageGeneratorProtocol:
    """Tests for ImageGenerator protocol compliance."""

    def test_image_generator_protocol_exists(self):
        """
        [2.3-UNIT-016a] ImageGenerator protocol exists.
        
        GIVEN the interfaces module
        WHEN importing ImageGenerator
        THEN the protocol should exist.
        """
        from eleven_video.api.interfaces import ImageGenerator
        
        assert ImageGenerator is not None

    def test_gemini_adapter_has_generate_images_method(self):
        """
        [2.3-UNIT-016b] GeminiAdapter has generate_images method.
        
        GIVEN the GeminiAdapter class
        WHEN checking for generate_images method
        THEN the method should exist.
        """
        with patch("eleven_video.api.gemini.genai.Client"):
            from eleven_video.api.gemini import GeminiAdapter
            
            adapter = GeminiAdapter(api_key="test-key")
            
            assert hasattr(adapter, 'generate_images')
            assert callable(getattr(adapter, 'generate_images'))
