"""
Tests for progress indicator during image generation (Story 2.3).

Test IDs: 2.3-UNIT-007, 2.3-UNIT-008
Tests verify progress callbacks are invoked correctly (AC3, FR23).
"""
import pytest
from unittest.mock import MagicMock, patch


class TestProgressIndicatorForImageGen:
    """Tests for progress indicator during image generation (AC3, FR23)."""

    def test_progress_callback_invoked_per_image(self, mock_genai_new_sdk_image):
        """
        [2.3-UNIT-007] AC3/FR23: Progress callback invoked per image.
        
        GIVEN a progress callback is provided
        WHEN generating multiple images
        THEN the callback is invoked for each image.
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import Script
        
        mock_client_cls, mock_client, mock_response = mock_genai_new_sdk_image
        
        progress_updates = []
        def progress_callback(status: str):
            progress_updates.append(status)
        
        adapter = GeminiAdapter(api_key="test-key")
        script = Script(content="""First paragraph.

Second paragraph.

Third paragraph.""")
        
        adapter.generate_images(script, progress_callback=progress_callback)
        
        # Should have at least one update per image
        assert len(progress_updates) >= 3

    def test_progress_format_generating_image_x_of_y(self, mock_genai_new_sdk_image):
        """
        [2.3-UNIT-008] AC3: Progress format "Generating image X of Y".
        
        GIVEN a progress callback is provided
        WHEN images are being generated
        THEN progress uses format "Generating image X of Y".
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import Script
        
        mock_client_cls, mock_client, mock_response = mock_genai_new_sdk_image
        
        progress_updates = []
        def progress_callback(status: str):
            progress_updates.append(status)
        
        adapter = GeminiAdapter(api_key="test-key")
        script = Script(content="Single paragraph.")
        
        adapter.generate_images(script, progress_callback=progress_callback)
        
        # Check format matches expected pattern
        assert any("Generating image" in msg and "of" in msg for msg in progress_updates)
