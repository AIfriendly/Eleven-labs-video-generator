"""
Tests for API key security in image generation (Story 2.3).

Test IDs: 2.3-UNIT-005, 2.3-UNIT-006
Tests verify API key is never exposed in logs or error messages (AC2).
"""
import pytest
from unittest.mock import MagicMock, patch


class TestApiKeySecurityForImageGen:
    """Tests for API key security in image generation (AC2)."""

    def test_api_key_never_in_logs_image_gen(self, mock_genai_new_sdk_image, caplog):
        """
        [2.3-UNIT-005] AC2: API key never exposed in logs.
        
        GIVEN image generation is running
        WHEN logs are produced
        THEN the API key is never exposed in log output.
        """
        import logging
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import Script
        
        mock_client_cls, mock_client, mock_response = mock_genai_new_sdk_image
        
        with caplog.at_level(logging.DEBUG):
            adapter = GeminiAdapter(api_key="super-secret-image-key-12345")
            script = Script(content="Test content")
            adapter.generate_images(script)
        
        for record in caplog.records:
            assert "super-secret-image-key-12345" not in record.message

    def test_api_key_never_in_error_messages_image_gen(self, mock_genai_new_sdk_error):
        """
        [2.3-UNIT-006] AC2: API key never in error messages.
        
        GIVEN an API error occurs during image generation
        WHEN the error is raised
        THEN the API key is not exposed in the error message.
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import Script
        from eleven_video.exceptions.custom_errors import GeminiAPIError
        
        mock_client_cls, mock_client, set_error = mock_genai_new_sdk_error
        set_error(Exception("API Error"))
        
        adapter = GeminiAdapter(api_key="secret-image-key-xyz")
        script = Script(content="Test content")
        
        with pytest.raises(GeminiAPIError) as exc_info:
            adapter.generate_images(script)
        
        assert "secret-image-key-xyz" not in str(exc_info.value)
