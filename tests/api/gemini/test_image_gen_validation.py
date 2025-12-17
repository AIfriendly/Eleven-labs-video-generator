"""
Tests for invalid script handling in image generation (Story 2.3).

Test IDs: 2.3-UNIT-009, 2.3-UNIT-010
Tests verify empty/whitespace scripts raise ValidationError (AC4).
"""
import pytest
from unittest.mock import patch


class TestInvalidScriptHandling:
    """Tests for empty/invalid script handling (AC4)."""

    def test_empty_script_raises_validation_error(self):
        """
        [2.3-UNIT-009] AC4: Empty script raises validation error.
        
        GIVEN an empty script content
        WHEN generate_images is called
        THEN a ValidationError is raised.
        """
        from eleven_video.exceptions.custom_errors import ValidationError
        from eleven_video.models.domain import Script
        
        with patch("eleven_video.api.gemini.genai.Client"):
            from eleven_video.api.gemini import GeminiAdapter
            
            adapter = GeminiAdapter(api_key="test-key")
            script = Script(content="")
            
            with pytest.raises(ValidationError):
                adapter.generate_images(script)

    def test_whitespace_script_raises_validation_error(self):
        """
        [2.3-UNIT-010] AC4: Whitespace-only script raises error.
        
        GIVEN a whitespace-only script content
        WHEN generate_images is called
        THEN a ValidationError is raised.
        """
        from eleven_video.exceptions.custom_errors import ValidationError
        from eleven_video.models.domain import Script
        
        with patch("eleven_video.api.gemini.genai.Client"):
            from eleven_video.api.gemini import GeminiAdapter
            
            adapter = GeminiAdapter(api_key="test-key")
            script = Script(content="   \n\t   ")
            
            with pytest.raises(ValidationError):
                adapter.generate_images(script)
