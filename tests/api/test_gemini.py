"""
Tests for Gemini API adapter.

Test IDs: 1.5-UNIT-021 to 1.5-UNIT-028
Tests cover ServiceHealth protocol implementation, health checks, and usage retrieval.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx


class TestGeminiAdapter:
    """Tests for GeminiAdapter class."""

    def test_adapter_can_be_imported(self):
        """[1.5-UNIT-021] Adapter should be importable from gemini module."""
        # Given: The gemini module exists
        # When: GeminiAdapter is imported
        from eleven_video.api.gemini import GeminiAdapter
        # Then: It should not be None
        assert GeminiAdapter is not None

    def test_adapter_implements_service_health(self):
        """[1.5-UNIT-022] AC1: Adapter must implement ServiceHealth protocol."""
        # Given: The ServiceHealth protocol is defined
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.api.interfaces import ServiceHealth
        
        # When: Creating an adapter instance
        adapter = GeminiAdapter(api_key="test-key")
        
        # Then: It should have all required protocol methods
        assert hasattr(adapter, 'check_health')
        assert hasattr(adapter, 'get_usage')
        assert hasattr(adapter, 'service_name')

    def test_adapter_has_correct_service_name(self):
        """[1.5-UNIT-023] Adapter service_name should be 'Google Gemini'."""
        # Given: A Gemini adapter
        from eleven_video.api.gemini import GeminiAdapter
        adapter = GeminiAdapter(api_key="test-key")
        
        # When: Accessing service_name
        # Then: It should be 'Google Gemini'
        assert adapter.service_name == "Google Gemini"

    def test_adapter_requires_api_key(self):
        """[1.5-UNIT-024] Adapter should require API key."""
        # Given: No API key provided
        from eleven_video.api.gemini import GeminiAdapter
        
        # When: Creating adapter with None key
        # Then: Should raise TypeError or ValueError
        with pytest.raises((TypeError, ValueError)):
            GeminiAdapter(api_key=None)


class TestGeminiCheckHealth:
    """Tests for check_health method."""

    @pytest.mark.asyncio
    async def test_check_health_success(self):
        """[1.5-UNIT-025] AC1: check_health returns ok status on success."""
        # Given: A valid API key and successful API response
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.api.interfaces import HealthResult

        adapter = GeminiAdapter(api_key="valid-key")
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": [{"name": "gemini-pro"}]}
        
        # When: check_health is called with mocked successful response
        with patch.object(adapter, '_fetch_models', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_response
            result = await adapter.check_health()
        
        # Then: Status should be ok with latency
        assert isinstance(result, HealthResult)
        assert result.status == "ok"
        assert result.latency_ms is not None

    @pytest.mark.asyncio
    async def test_check_health_auth_failure(self):
        """[1.5-UNIT-026] AC3: check_health returns error on auth failure."""
        # Given: An invalid API key
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.api.interfaces import HealthResult

        adapter = GeminiAdapter(api_key="invalid-key")
        
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        # When: check_health encounters 401 response
        with patch.object(adapter, '_fetch_models', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_response
            result = await adapter.check_health()
        
        # Then: Status should be error
        assert isinstance(result, HealthResult)
        assert result.status == "error"

    @pytest.mark.asyncio
    async def test_check_health_connection_failure(self):
        """[1.5-UNIT-027] AC3: check_health returns error on connection failure."""
        # Given: A network failure scenario
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.api.interfaces import HealthResult

        adapter = GeminiAdapter(api_key="valid-key")
        
        # When: Connection error occurs
        with patch.object(adapter, '_fetch_models', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = httpx.ConnectError("Connection refused")
            result = await adapter.check_health()
        
        # Then: Status should be error
        assert isinstance(result, HealthResult)
        assert result.status == "error"


class TestGeminiGetUsage:
    """Tests for get_usage method."""

    @pytest.mark.asyncio
    async def test_get_usage_not_available(self):
        """[1.5-UNIT-028] AC2: Gemini API does not expose quota."""
        # Given: Gemini API doesn't expose usage via API
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.api.interfaces import UsageResult

        adapter = GeminiAdapter(api_key="valid-key")
        
        # When: get_usage is called
        result = await adapter.get_usage()
        
        # Then: Usage should be unavailable
        assert isinstance(result, UsageResult)
        assert result.available is False
        assert result.used is None
        assert result.limit is None


# =============================================================================
# Story 2.1 ATDD Tests: Default Script Generation from Prompt
# =============================================================================
# RED PHASE: All tests below are expected to FAIL until implementation.
# Test IDs: 2.1-UNIT-001 to 2.1-UNIT-017
# =============================================================================


class TestScriptGenerationSuccess:
    """Tests for successful script generation (AC1)."""

    def test_generate_script_returns_coherent_content(self):
        """
        [2.1-UNIT-001] AC1: Coherent script generation from valid prompt.
        
        GIVEN a valid text prompt
        WHEN the script generation is initiated
        THEN a coherent script is returned containing structured content.
        
        Status: RED - generate_script method not implemented
        """
        from eleven_video.api.gemini import GeminiAdapter
        from unittest.mock import MagicMock, patch
        
        # Mock the genai SDK
        with patch("google.generativeai.configure"), \
             patch("google.generativeai.GenerativeModel") as mock_model_cls:
            
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "[Scene 1] Mountain landscape\n[Narration] Welcome..."
            mock_model.generate_content.return_value = mock_response
            mock_model_cls.return_value = mock_model
            
            adapter = GeminiAdapter(api_key="test-key")
            script = adapter.generate_script("Create a video about mountains")
            
            assert script is not None
            assert hasattr(script, 'content')
            assert len(script.content) > 0

    def test_generate_script_uses_default_model(self):
        """
        [2.1-UNIT-002] AC1: Default model gemini-2.5-flash is used.
        
        GIVEN no model specified
        WHEN generating a script
        THEN gemini-2.5-flash is used as default.
        
        Status: RED - generate_script method not implemented
        """
        from eleven_video.api.gemini import GeminiAdapter
        from unittest.mock import MagicMock, patch
        
        with patch("google.generativeai.configure"), \
             patch("google.generativeai.GenerativeModel") as mock_model_cls:
            
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "Generated script content"
            mock_model.generate_content.return_value = mock_response
            mock_model_cls.return_value = mock_model
            
            adapter = GeminiAdapter(api_key="test-key")
            adapter.generate_script("Test prompt")
            
            mock_model_cls.assert_called_with("gemini-2.5-flash")

    def test_generate_script_returns_script_model(self):
        """
        [2.1-UNIT-003] AC1: Returns Script domain model.
        
        GIVEN a valid prompt
        WHEN script generation completes
        THEN a Script domain model is returned.
        
        Status: RED - Script model not implemented
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import Script
        from unittest.mock import MagicMock, patch
        
        with patch("google.generativeai.configure"), \
             patch("google.generativeai.GenerativeModel") as mock_model_cls:
            
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "Script content"
            mock_model.generate_content.return_value = mock_response
            mock_model_cls.return_value = mock_model
            
            adapter = GeminiAdapter(api_key="test-key")
            result = adapter.generate_script("Test prompt")
            
            assert isinstance(result, Script)


class TestApiKeySecurityForScriptGen:
    """Tests for API key security in script generation (AC2)."""

    def test_api_key_never_in_logs(self, caplog):
        """
        [2.1-UNIT-004] AC2: API key never exposed in logs.
        
        GIVEN script generation is running
        WHEN logs are produced
        THEN the API key is never exposed in log output.
        
        Status: RED - generate_script method not implemented
        """
        import logging
        from eleven_video.api.gemini import GeminiAdapter
        from unittest.mock import MagicMock, patch
        
        with caplog.at_level(logging.DEBUG):
            with patch("google.generativeai.configure"), \
                 patch("google.generativeai.GenerativeModel") as mock_model_cls:
                
                mock_model = MagicMock()
                mock_response = MagicMock()
                mock_response.text = "Script"
                mock_model.generate_content.return_value = mock_response
                mock_model_cls.return_value = mock_model
                
                adapter = GeminiAdapter(api_key="super-secret-key-12345")
                adapter.generate_script("Test prompt")
        
        for record in caplog.records:
            assert "super-secret-key-12345" not in record.message

    def test_api_key_never_in_error_messages(self):
        """
        [2.1-UNIT-005] AC2: API key never in error messages.
        
        GIVEN an API error occurs
        WHEN the error is raised
        THEN the API key is not exposed in the error message.
        
        Status: RED - generate_script method not implemented
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.exceptions.custom_errors import GeminiAPIError
        from unittest.mock import MagicMock, patch
        
        with patch("google.generativeai.configure"), \
             patch("google.generativeai.GenerativeModel") as mock_model_cls:
            
            mock_model = MagicMock()
            mock_model.generate_content.side_effect = Exception("API Error")
            mock_model_cls.return_value = mock_model
            
            adapter = GeminiAdapter(api_key="secret-key-xyz")
            
            with pytest.raises(GeminiAPIError) as exc_info:
                adapter.generate_script("Test prompt")
            
            assert "secret-key-xyz" not in str(exc_info.value)


class TestProgressIndicatorForScriptGen:
    """Tests for progress indicator during generation (AC3, FR23)."""

    def test_progress_callback_called_during_generation(self):
        """
        [2.1-UNIT-006] AC3/FR23: Progress callback invoked during generation.
        
        GIVEN a progress callback is provided
        WHEN script generation runs
        THEN the callback is invoked with status updates.
        
        Status: RED - Progress callback not implemented
        """
        from eleven_video.api.gemini import GeminiAdapter
        from unittest.mock import MagicMock, patch
        
        progress_updates = []
        def progress_callback(status: str):
            progress_updates.append(status)
        
        with patch("google.generativeai.configure"), \
             patch("google.generativeai.GenerativeModel") as mock_model_cls:
            
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "Script"
            mock_model.generate_content.return_value = mock_response
            mock_model_cls.return_value = mock_model
            
            adapter = GeminiAdapter(api_key="test-key")
            adapter.generate_script("Test prompt", progress_callback=progress_callback)
        
        assert len(progress_updates) > 0


class TestInvalidPromptHandling:
    """Tests for empty/invalid prompt handling (AC4)."""

    def test_empty_prompt_raises_validation_error(self):
        """
        [2.1-UNIT-007] AC4: Empty prompt raises validation error.
        
        GIVEN an empty prompt
        WHEN generation is attempted
        THEN a clear validation error is raised before API call.
        
        Status: RED - Prompt validation not implemented
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.exceptions.custom_errors import ValidationError
        from unittest.mock import patch
        
        with patch("google.generativeai.configure"):
            adapter = GeminiAdapter(api_key="test-key")
            
            with pytest.raises(ValidationError):
                adapter.generate_script("")

    def test_whitespace_only_prompt_raises_error(self):
        """
        [2.1-UNIT-008] AC4: Whitespace-only prompt raises error.
        
        GIVEN a whitespace-only prompt
        WHEN generation is attempted
        THEN a validation error is raised.
        
        Status: RED - Prompt validation not implemented
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.exceptions.custom_errors import ValidationError
        from unittest.mock import patch
        
        with patch("google.generativeai.configure"):
            adapter = GeminiAdapter(api_key="test-key")
            
            with pytest.raises(ValidationError):
                adapter.generate_script("   \n\t   ")

    def test_none_prompt_raises_error(self):
        """
        [2.1-UNIT-009] AC4: None prompt raises error.
        
        GIVEN a None prompt
        WHEN generation is attempted
        THEN a validation error is raised.
        
        Status: RED - Prompt validation not implemented
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.exceptions.custom_errors import ValidationError
        from unittest.mock import patch
        
        with patch("google.generativeai.configure"):
            adapter = GeminiAdapter(api_key="test-key")
            
            with pytest.raises((ValidationError, TypeError)):
                adapter.generate_script(None)


class TestScriptGenApiErrorHandling:
    """Tests for API error handling in script generation (AC5)."""

    def test_auth_error_shows_user_friendly_message(self):
        """
        [2.1-UNIT-010] AC5: 401 error shows authentication message.
        
        GIVEN a 401 Unauthorized error from API
        WHEN the error is caught
        THEN a user-friendly message about authentication is shown.
        
        Status: RED - Error handling not implemented
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.exceptions.custom_errors import GeminiAPIError
        from unittest.mock import MagicMock, patch
        
        with patch("google.generativeai.configure"), \
             patch("google.generativeai.GenerativeModel") as mock_model_cls:
            
            mock_model = MagicMock()
            # Simulate auth error
            mock_model.generate_content.side_effect = Exception("401 Unauthorized")
            mock_model_cls.return_value = mock_model
            
            adapter = GeminiAdapter(api_key="test-key")
            
            with pytest.raises(GeminiAPIError) as exc_info:
                adapter.generate_script("Test prompt")
            
            error_msg = str(exc_info.value).lower()
            assert "authentication" in error_msg or "api key" in error_msg or "unauthorized" in error_msg

    def test_rate_limit_error_suggests_retry(self):
        """
        [2.1-UNIT-011] AC5: 429 error suggests retry.
        
        GIVEN a 429 Rate Limit error from API
        WHEN the error is caught
        THEN a message suggesting retry is shown.
        
        Status: RED - Error handling not implemented
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.exceptions.custom_errors import GeminiAPIError
        from unittest.mock import MagicMock, patch
        
        with patch("google.generativeai.configure"), \
             patch("google.generativeai.GenerativeModel") as mock_model_cls:
            
            mock_model = MagicMock()
            mock_model.generate_content.side_effect = Exception("429 Rate limit exceeded")
            mock_model_cls.return_value = mock_model
            
            adapter = GeminiAdapter(api_key="test-key")
            
            with pytest.raises(GeminiAPIError) as exc_info:
                adapter.generate_script("Test prompt")
            
            error_msg = str(exc_info.value).lower()
            assert "rate limit" in error_msg or "retry" in error_msg or "quota" in error_msg

    def test_server_error_shows_retry_message(self):
        """
        [2.1-UNIT-012] AC5: 500 error shows server issue message.
        
        GIVEN a 500 Server Error from API
        WHEN the error is caught
        THEN a message about server issues is shown.
        
        Status: RED - Error handling not implemented
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.exceptions.custom_errors import GeminiAPIError
        from unittest.mock import MagicMock, patch
        
        with patch("google.generativeai.configure"), \
             patch("google.generativeai.GenerativeModel") as mock_model_cls:
            
            mock_model = MagicMock()
            mock_model.generate_content.side_effect = Exception("500 Internal Server Error")
            mock_model_cls.return_value = mock_model
            
            adapter = GeminiAdapter(api_key="test-key")
            
            with pytest.raises(GeminiAPIError) as exc_info:
                adapter.generate_script("Test prompt")
            
            error_msg = str(exc_info.value).lower()
            assert "server" in error_msg or "try again" in error_msg or "internal" in error_msg

    def test_timeout_error_shows_timeout_message(self):
        """
        [2.1-UNIT-013] AC5: Timeout shows timeout message.
        
        GIVEN a timeout error from API
        WHEN the error is caught
        THEN a message about timeout is shown.
        
        Status: RED - Error handling not implemented
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.exceptions.custom_errors import GeminiAPIError
        from unittest.mock import MagicMock, patch
        
        with patch("google.generativeai.configure"), \
             patch("google.generativeai.GenerativeModel") as mock_model_cls:
            
            mock_model = MagicMock()
            mock_model.generate_content.side_effect = TimeoutError("Request timed out")
            mock_model_cls.return_value = mock_model
            
            adapter = GeminiAdapter(api_key="test-key")
            
            with pytest.raises(GeminiAPIError) as exc_info:
                adapter.generate_script("Test prompt")
            
            error_msg = str(exc_info.value).lower()
            assert "timeout" in error_msg or "timed out" in error_msg


class TestScriptGeneratorProtocol:
    """Tests for ScriptGenerator protocol compliance."""

    def test_gemini_adapter_has_generate_script_method(self):
        """
        [2.1-UNIT-014] Adapter has generate_script method.
        
        GIVEN the GeminiAdapter class
        WHEN checking for generate_script method
        THEN the method exists with correct signature.
        
        Status: RED - generate_script method not implemented
        """
        from eleven_video.api.gemini import GeminiAdapter
        from unittest.mock import patch
        
        with patch("google.generativeai.configure"):
            adapter = GeminiAdapter(api_key="test-key")
            
            assert hasattr(adapter, 'generate_script')
            assert callable(getattr(adapter, 'generate_script'))


class TestScriptDomainModel:
    """Tests for Script domain model existence."""

    def test_script_model_exists(self):
        """
        [2.1-UNIT-015] Script domain model exists.
        
        GIVEN the models.domain module
        WHEN importing Script
        THEN the class should exist.
        
        Status: RED - Script model not implemented
        """
        from eleven_video.models.domain import Script
        
        assert Script is not None

    def test_script_model_has_content_attribute(self):
        """
        [2.1-UNIT-016] Script model has content attribute.
        
        GIVEN a Script instance
        WHEN accessing content
        THEN a string attribute exists.
        
        Status: RED - Script model not implemented
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
        
        Status: RED - GeminiAPIError not implemented
        """
        from eleven_video.exceptions.custom_errors import GeminiAPIError
        
        assert GeminiAPIError is not None
        assert issubclass(GeminiAPIError, Exception)


# =============================================================================
# Story 2.1 Integration Tests (Skip in CI)
# =============================================================================
# These tests validate real API connectivity. Skip in CI environments.
# Run manually with: uv run pytest tests/api/test_gemini.py -k "integration" -v
# =============================================================================


class TestScriptGenerationIntegration:
    """Integration tests for real Gemini API - skip in CI."""

    @pytest.mark.skip(reason="Integration test - requires real GEMINI_API_KEY")
    def test_real_api_generates_script(self):
        """
        [2.1-INT-001] Integration: Real API generates coherent script.
        
        GIVEN a valid GEMINI_API_KEY in environment
        WHEN generate_script is called with a real prompt
        THEN a coherent script is returned from the actual API.
        
        Note: Uncomment @pytest.mark.skip to run with real credentials.
        """
        import os
        from eleven_video.api.gemini import GeminiAdapter
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            pytest.skip("GEMINI_API_KEY not set")
        
        adapter = GeminiAdapter(api_key=api_key)
        script = adapter.generate_script("Create a 30-second video script about the ocean.")
        
        assert script is not None
        assert len(script.content) > 50  # Should have substantial content
        assert isinstance(script.content, str)

    @pytest.mark.skip(reason="Integration test - requires real GEMINI_API_KEY")
    def test_real_api_with_settings_class(self):
        """
        [2.1-INT-002] Integration: Real API with Settings class.
        
        GIVEN a valid GEMINI_API_KEY via Settings class
        WHEN GeminiAdapter is created with Settings
        THEN script generation works correctly.
        
        Note: Uncomment @pytest.mark.skip to run with real credentials.
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

