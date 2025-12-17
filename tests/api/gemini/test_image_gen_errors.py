"""
Tests for API error handling in image generation (Story 2.3).

Test IDs: 2.3-UNIT-011 to 2.3-UNIT-014
Tests verify user-friendly error messages for various API errors (AC5).
"""
import pytest
from unittest.mock import MagicMock, patch


class TestImageGenApiErrorHandling:
    """Tests for API error handling in image generation (AC5)."""

    def test_auth_error_shows_user_friendly_message(self, mock_genai_new_sdk_error):
        """
        [2.3-UNIT-011] AC5: 401 error shows authentication message.
        
        GIVEN a 401 Unauthorized error from API
        WHEN the error is caught
        THEN a user-friendly message about authentication is shown.
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import Script
        from eleven_video.exceptions.custom_errors import GeminiAPIError
        
        mock_client_cls, mock_client, set_error = mock_genai_new_sdk_error
        set_error(Exception("401 Unauthorized"))
        
        adapter = GeminiAdapter(api_key="test-key")
        script = Script(content="Test content")
        
        with pytest.raises(GeminiAPIError) as exc_info:
            adapter.generate_images(script)
        
        error_msg = str(exc_info.value).lower()
        assert "authentication" in error_msg or "api key" in error_msg or "unauthorized" in error_msg

    def test_rate_limit_error_shows_retry_message(self, mock_genai_new_sdk_error):
        """
        [2.3-UNIT-012] AC5: 429 error suggests retry.
        
        GIVEN a 429 Rate Limit error from API
        WHEN the error is caught
        THEN a message suggesting retry is shown.
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import Script
        from eleven_video.exceptions.custom_errors import GeminiAPIError
        
        mock_client_cls, mock_client, set_error = mock_genai_new_sdk_error
        set_error(Exception("429 Resource exhausted"))
        
        adapter = GeminiAdapter(api_key="test-key")
        script = Script(content="Test content")
        
        with pytest.raises(GeminiAPIError) as exc_info:
            adapter.generate_images(script)
        
        error_msg = str(exc_info.value).lower()
        assert "rate limit" in error_msg or "retry" in error_msg or "quota" in error_msg

    def test_server_error_shows_retry_message(self, mock_genai_new_sdk_error):
        """
        [2.3-UNIT-013] AC5: 500 error shows server issue message.
        
        GIVEN a 500 Server Error from API
        WHEN the error is caught
        THEN a message about server issues is shown.
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import Script
        from eleven_video.exceptions.custom_errors import GeminiAPIError
        
        mock_client_cls, mock_client, set_error = mock_genai_new_sdk_error
        set_error(Exception("500 Internal Server Error"))
        
        adapter = GeminiAdapter(api_key="test-key")
        script = Script(content="Test content")
        
        with pytest.raises(GeminiAPIError) as exc_info:
            adapter.generate_images(script)
        
        error_msg = str(exc_info.value).lower()
        assert "server" in error_msg or "try again" in error_msg or "internal" in error_msg

    def test_timeout_error_shows_timeout_message(self, mock_genai_new_sdk_error):
        """
        [2.3-UNIT-014] AC5: Timeout shows timeout message.
        
        GIVEN a timeout error from API
        WHEN the error is caught
        THEN a message about timeout is shown.
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import Script
        from eleven_video.exceptions.custom_errors import GeminiAPIError
        
        mock_client_cls, mock_client, set_error = mock_genai_new_sdk_error
        set_error(TimeoutError("Request timed out"))
        
        adapter = GeminiAdapter(api_key="test-key")
        script = Script(content="Test content")
        
        with pytest.raises(GeminiAPIError) as exc_info:
            adapter.generate_images(script)
        
        error_msg = str(exc_info.value).lower()
        assert "timeout" in error_msg or "timed out" in error_msg
