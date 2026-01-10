"""
Tests for Gemini API adapter - Script Generation (Story 2.1).

Test IDs: 2.1-UNIT-001 to 2.1-UNIT-017, 2.1-INT-001 to 2.1-INT-002
Tests cover ScriptGenerator protocol, prompt validation, error handling, and security.
"""
import os
import pytest
from unittest.mock import MagicMock, patch


class TestScriptGenerationSuccess:
    """Tests for successful script generation (AC1)."""

    def test_generate_script_returns_coherent_content(self, mock_genai):
        """
        [2.1-UNIT-001] AC1: Coherent script generation from valid prompt.
        
        GIVEN a valid text prompt
        WHEN the script generation is initiated
        THEN a coherent script is returned containing structured content.
        """
        from eleven_video.api.gemini import GeminiAdapter
        
        mock_model_cls, mock_model, mock_response = mock_genai
        mock_response.text = "[Scene 1] Mountain landscape\n[Narration] Welcome..."
        
        adapter = GeminiAdapter(api_key="test-key")
        script = adapter.generate_script("Create a video about mountains")
        
        assert script is not None
        assert hasattr(script, 'content')
        assert len(script.content) > 0

    def test_generate_script_uses_default_model(self, mock_genai):
        """
        [2.1-UNIT-002] AC1: Uses gemini-2.5-flash model.
        
        GIVEN a valid prompt
        WHEN generating a script
        THEN the gemini-2.5-flash model is used.
        """
        from eleven_video.api.gemini import GeminiAdapter
        
        mock_client_cls, mock_client, mock_response = mock_genai
        
        adapter = GeminiAdapter(api_key="test-key")
        adapter.generate_script("Test prompt")
        
        # Verify model parameter in new SDK call
        mock_client.models.generate_content.assert_called_once()
        call_kwargs = mock_client.models.generate_content.call_args
        assert call_kwargs.kwargs.get('model') == "gemini-2.5-flash-lite" or \
               (call_kwargs.args and "gemini-2.5-flash-lite" in str(call_kwargs))

    def test_generate_script_returns_script_model(self, mock_genai):
        """
        [2.1-UNIT-003] AC1: Returns Script domain model.
        
        GIVEN a valid prompt
        WHEN script generation completes
        THEN a Script domain model is returned.
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import Script
        
        mock_model_cls, mock_model, mock_response = mock_genai
        
        adapter = GeminiAdapter(api_key="test-key")
        result = adapter.generate_script("Test prompt")
        
        assert isinstance(result, Script)


class TestApiKeySecurityForScriptGen:
    """Tests for API key security in script generation (AC2)."""

    def test_api_key_never_in_logs(self, mock_genai, caplog):
        """
        [2.1-UNIT-004] AC2: API key never exposed in logs.
        
        GIVEN script generation is running
        WHEN logs are produced
        THEN the API key is never exposed in log output.
        """
        import logging
        from eleven_video.api.gemini import GeminiAdapter
        
        mock_model_cls, mock_model, mock_response = mock_genai
        
        with caplog.at_level(logging.DEBUG):
            adapter = GeminiAdapter(api_key="super-secret-key-12345")
            adapter.generate_script("Test prompt")
        
        for record in caplog.records:
            assert "super-secret-key-12345" not in record.message

    def test_api_key_never_in_error_messages(self, mock_genai_error):
        """
        [2.1-UNIT-005] AC2: API key never in error messages.
        
        GIVEN an API error occurs
        WHEN the error is raised
        THEN the API key is not exposed in the error message.
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.exceptions.custom_errors import GeminiAPIError
        
        mock_model_cls, mock_model, set_error = mock_genai_error
        set_error(Exception("API Error"))
        
        adapter = GeminiAdapter(api_key="secret-key-xyz")
        
        with pytest.raises(GeminiAPIError) as exc_info:
            adapter.generate_script("Test prompt")
        
        assert "secret-key-xyz" not in str(exc_info.value)


class TestProgressIndicatorForScriptGen:
    """Tests for progress indicator during generation (AC3, FR23)."""

    def test_progress_callback_called_during_generation(self, mock_genai):
        """
        [2.1-UNIT-006] AC3/FR23: Progress callback invoked during generation.
        
        GIVEN a progress callback is provided
        WHEN script generation runs
        THEN the callback is invoked with status updates.
        """
        from eleven_video.api.gemini import GeminiAdapter
        
        mock_model_cls, mock_model, mock_response = mock_genai
        
        progress_updates = []
        def progress_callback(status: str):
            progress_updates.append(status)
        
        adapter = GeminiAdapter(api_key="test-key")
        adapter.generate_script("Test prompt", progress_callback=progress_callback)
        
        assert len(progress_updates) > 0


class TestInvalidPromptHandling:
    """Tests for empty/invalid prompt handling (AC4)."""

    def test_empty_prompt_raises_validation_error(self, gemini_adapter):
        """
        [2.1-UNIT-007] AC4: Empty prompt raises validation error.
        
        GIVEN an empty prompt
        WHEN generation is attempted
        THEN a clear validation error is raised before API call.
        """
        from eleven_video.exceptions.custom_errors import ValidationError
        
        with pytest.raises(ValidationError):
            gemini_adapter.generate_script("")

    def test_whitespace_only_prompt_raises_error(self, gemini_adapter):
        """
        [2.1-UNIT-008] AC4: Whitespace-only prompt raises error.
        
        GIVEN a whitespace-only prompt
        WHEN generation is attempted
        THEN a validation error is raised.
        """
        from eleven_video.exceptions.custom_errors import ValidationError
        
        with pytest.raises(ValidationError):
            gemini_adapter.generate_script("   \n\t   ")

    def test_none_prompt_raises_error(self, gemini_adapter):
        """
        [2.1-UNIT-009] AC4: None prompt raises error.
        
        GIVEN a None prompt
        WHEN generation is attempted
        THEN a validation error is raised.
        """
        from eleven_video.exceptions.custom_errors import ValidationError
        
        with pytest.raises((ValidationError, TypeError)):
            gemini_adapter.generate_script(None)


class TestScriptGenApiErrorHandling:
    """Tests for API error handling in script generation (AC5)."""

    def test_auth_error_shows_user_friendly_message(self, mock_genai_error):
        """
        [2.1-UNIT-010] AC5: 401 error shows authentication message.
        
        GIVEN a 401 Unauthorized error from API
        WHEN the error is caught
        THEN a user-friendly message about authentication is shown.
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.exceptions.custom_errors import GeminiAPIError
        
        mock_model_cls, mock_model, set_error = mock_genai_error
        set_error(Exception("401 Unauthorized"))
        
        adapter = GeminiAdapter(api_key="test-key")
        
        with pytest.raises(GeminiAPIError) as exc_info:
            adapter.generate_script("Test prompt")
        
        error_msg = str(exc_info.value).lower()
        assert "authentication" in error_msg or "api key" in error_msg or "unauthorized" in error_msg

    def test_rate_limit_error_suggests_retry(self, mock_genai_error):
        """
        [2.1-UNIT-011] AC5: 429 error suggests retry.
        
        GIVEN a 429 Rate Limit error from API
        WHEN the error is caught
        THEN a message suggesting retry is shown.
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.exceptions.custom_errors import GeminiAPIError
        
        mock_model_cls, mock_model, set_error = mock_genai_error
        set_error(Exception("429 Rate limit exceeded"))
        
        adapter = GeminiAdapter(api_key="test-key")
        
        with pytest.raises(GeminiAPIError) as exc_info:
            adapter.generate_script("Test prompt")
        
        error_msg = str(exc_info.value).lower()
        assert "rate limit" in error_msg or "retry" in error_msg or "quota" in error_msg

    def test_server_error_shows_retry_message(self, mock_genai_error):
        """
        [2.1-UNIT-012] AC5: 500 error shows server issue message.
        
        GIVEN a 500 Server Error from API
        WHEN the error is caught
        THEN a message about server issues is shown.
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.exceptions.custom_errors import GeminiAPIError
        
        mock_model_cls, mock_model, set_error = mock_genai_error
        set_error(Exception("500 Internal Server Error"))
        
        adapter = GeminiAdapter(api_key="test-key")
        
        with pytest.raises(GeminiAPIError) as exc_info:
            adapter.generate_script("Test prompt")
        
        error_msg = str(exc_info.value).lower()
        assert "server" in error_msg or "try again" in error_msg or "internal" in error_msg

    def test_timeout_error_shows_timeout_message(self, mock_genai_error):
        """
        [2.1-UNIT-013] AC5: Timeout shows timeout message.
        
        GIVEN a timeout error from API
        WHEN the error is caught
        THEN a message about timeout is shown.
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.exceptions.custom_errors import GeminiAPIError
        
        mock_model_cls, mock_model, set_error = mock_genai_error
        set_error(TimeoutError("Request timed out"))
        
        adapter = GeminiAdapter(api_key="test-key")
        
        with pytest.raises(GeminiAPIError) as exc_info:
            adapter.generate_script("Test prompt")
        
        error_msg = str(exc_info.value).lower()
        assert "timeout" in error_msg or "timed out" in error_msg


class TestScriptGeneratorProtocol:
    """Tests for ScriptGenerator protocol compliance."""

    def test_gemini_adapter_has_generate_script_method(self, gemini_adapter):
        """
        [2.1-UNIT-014] Adapter has generate_script method.
        
        GIVEN the GeminiAdapter class
        WHEN checking for generate_script method
        THEN the method exists with correct signature.
        """
        assert hasattr(gemini_adapter, 'generate_script')
        assert callable(getattr(gemini_adapter, 'generate_script'))


class TestScriptDomainModel:
    """Tests for Script domain model existence."""

    def test_script_model_exists(self):
        """
        [2.1-UNIT-015] Script domain model exists.
        
        GIVEN the models.domain module
        WHEN importing Script
        THEN the class should exist.
        """
        from eleven_video.models.domain import Script
        
        assert Script is not None

    def test_script_model_has_content_attribute(self):
        """
        [2.1-UNIT-016] Script model has content attribute.
        
        GIVEN a Script instance
        WHEN accessing content
        THEN a string attribute exists.
        """
        from eleven_video.models.domain import Script
        
        script = Script(content="Test content")
        assert hasattr(script, 'content')
        assert script.content == "Test content"


class TestGeminiAPIErrorExists:
    """Tests for GeminiAPIError exception class."""

    def test_gemini_api_error_exists(self):
        """
        [2.1-UNIT-017] GeminiAPIError exception exists.
        
        GIVEN the exceptions module
        WHEN importing GeminiAPIError
        THEN the class should exist.
        """
        from eleven_video.exceptions.custom_errors import GeminiAPIError
        
        assert GeminiAPIError is not None
        assert issubclass(GeminiAPIError, Exception)


# =============================================================================
# Story 2.1 Integration Tests (Skip in CI)
# =============================================================================
# Run manually with: uv run pytest tests/api/test_gemini_script.py -m integration -v
# =============================================================================


@pytest.mark.integration
class TestScriptGenerationIntegration:
    """Integration tests for real Gemini API - skip in CI."""

    @pytest.mark.skipif(
        not os.environ.get("GEMINI_API_KEY"),
        reason="GEMINI_API_KEY not set"
    )
    def test_real_api_generates_script(self):
        """
        [2.1-INT-001] Integration: Real API generates coherent script.
        
        GIVEN a valid GEMINI_API_KEY in environment
        WHEN generate_script is called with a real prompt
        THEN a coherent script is returned from the actual API.
        """
        from eleven_video.api.gemini import GeminiAdapter
        
        api_key = os.environ.get("GEMINI_API_KEY")
        adapter = GeminiAdapter(api_key=api_key)
        script = adapter.generate_script("Create a 30-second video script about the ocean.")
        
        assert script is not None
        assert len(script.content) > 50  # Should have substantial content
        assert isinstance(script.content, str)

    @pytest.mark.skipif(
        not os.environ.get("GEMINI_API_KEY"),
        reason="GEMINI_API_KEY not set"
    )
    def test_real_api_with_settings_class(self):
        """
        [2.1-INT-002] Integration: Real API with Settings class.
        
        GIVEN a valid GEMINI_API_KEY via Settings class
        WHEN GeminiAdapter is created with Settings
        THEN script generation works correctly.
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.config.settings import Settings
        
        try:
            settings = Settings()
        except Exception:
            pytest.skip("Settings not configured with API keys")
        
        adapter = GeminiAdapter(settings=settings)
        script = adapter.generate_script("Write a brief intro for a tech tutorial.")
        
        assert script is not None
        assert len(script.content) > 20
