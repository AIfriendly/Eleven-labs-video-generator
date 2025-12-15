"""
Tests for ElevenLabs API adapter - TTS Speech Generation (Story 2.2).

Test IDs: 2.2-UNIT-001 to 2.2-UNIT-013, 2.2-UNIT-020
Tests cover success path (AC1), security (AC2), progress (AC3), validation (AC4), and errors (AC5).

Related test files (split per TEA review P1 recommendation):
- test_elevenlabs_protocols.py: Protocol, domain model, exception, settings tests
- test_elevenlabs_integration.py: Real API integration tests (skip in CI)
"""
import pytest
from unittest.mock import MagicMock, patch


# =============================================================================
# Fixtures for ElevenLabs SDK mocking
# =============================================================================

@pytest.fixture
def mock_elevenlabs_sdk():
    """
    Fixture providing mocked elevenlabs SDK.
    
    Yields:
        tuple: (mock_client_cls, mock_client, mock_audio_iterator)
        
    Usage:
        def test_example(mock_elevenlabs_sdk):
            mock_client_cls, mock_client, mock_audio = mock_elevenlabs_sdk
            # ... test code
    """
    with patch("eleven_video.api.elevenlabs.ElevenLabs") as mock_client_cls:
        mock_client = MagicMock()
        # Mock returns an iterator of bytes (SDK behavior)
        mock_audio_iterator = iter([b'\xff\xfb\x90\x00', b'\x00\x00\x00\x00'])
        mock_client.text_to_speech.convert.return_value = mock_audio_iterator
        mock_client_cls.return_value = mock_client
        yield mock_client_cls, mock_client, mock_audio_iterator


@pytest.fixture
def mock_elevenlabs_sdk_error():
    """
    Fixture providing mocked elevenlabs SDK that raises errors.
    
    Yields:
        tuple: (mock_client_cls, mock_client, set_error_func)
        
    Usage:
        def test_error(mock_elevenlabs_sdk_error):
            mock_client_cls, mock_client, set_error = mock_elevenlabs_sdk_error
            set_error(Exception("401 Unauthorized"))
            # ... test code
    """
    with patch("eleven_video.api.elevenlabs.ElevenLabs") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        
        def set_error(error):
            mock_client.text_to_speech.convert.side_effect = error
        
        yield mock_client_cls, mock_client, set_error


# =============================================================================
# Story 2.2: AC1 - Audio Generation Success Tests
# =============================================================================

class TestTTSGenerationSuccess:
    """Tests for successful TTS generation (AC1)."""

    def test_generate_speech_returns_audio_bytes(self, mock_elevenlabs_sdk):
        """
        [2.2-UNIT-001] AC1: TTS generation returns audio bytes.
        
        GIVEN a valid script text
        WHEN the TTS generation process runs
        THEN an audio file is created with voiceover of the script.
        """
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        from eleven_video.models.domain import Audio
        
        mock_client_cls, mock_client, _ = mock_elevenlabs_sdk
        
        adapter = ElevenLabsAdapter(api_key="test-key")
        audio = adapter.generate_speech("Hello, this is a test script.")
        
        assert audio is not None
        assert isinstance(audio, Audio)
        assert len(audio.data) > 0

    def test_generate_speech_uses_mp3_44100_128_format(self, mock_elevenlabs_sdk):
        """
        [2.2-UNIT-002] AC1: Audio format is mp3_44100_128.
        
        GIVEN TTS generation is initiated
        WHEN generating audio
        THEN mp3_44100_128 format is used (44.1kHz, 128kbps).
        """
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        
        mock_client_cls, mock_client, _ = mock_elevenlabs_sdk
        
        adapter = ElevenLabsAdapter(api_key="test-key")
        adapter.generate_speech("Test script")
        
        # Verify SDK called with correct output_format
        mock_client.text_to_speech.convert.assert_called_once()
        call_kwargs = mock_client.text_to_speech.convert.call_args.kwargs
        assert call_kwargs.get("output_format") == ElevenLabsAdapter.DEFAULT_OUTPUT_FORMAT

    def test_generate_speech_uses_default_voice(self, mock_elevenlabs_sdk):
        """
        [2.2-UNIT-003] AC1: Default voice Rachel is used.
        
        GIVEN no voice specified
        WHEN generating speech
        THEN default voice ID 21m00Tcm4TlvDq8ikWAM is used.
        """
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        
        mock_client_cls, mock_client, _ = mock_elevenlabs_sdk
        
        adapter = ElevenLabsAdapter(api_key="test-key")
        adapter.generate_speech("Test script")
        
        call_kwargs = mock_client.text_to_speech.convert.call_args.kwargs
        assert call_kwargs.get("voice_id") == "21m00Tcm4TlvDq8ikWAM"

    def test_generate_speech_uses_custom_voice(self, mock_elevenlabs_sdk):
        """
        [2.2-UNIT-020] AC1: Custom voice ID is used when provided.
        
        GIVEN a custom voice_id is specified
        WHEN generating speech
        THEN the custom voice ID is passed to the SDK.
        """
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        
        mock_client_cls, mock_client, _ = mock_elevenlabs_sdk
        
        adapter = ElevenLabsAdapter(api_key="test-key")
        custom_voice = "custom-voice-id-12345"
        adapter.generate_speech("Test script", voice_id=custom_voice)
        
        call_kwargs = mock_client.text_to_speech.convert.call_args.kwargs
        assert call_kwargs.get("voice_id") == custom_voice


# =============================================================================
# Story 2.2: AC2 - API Key Security Tests
# =============================================================================

class TestApiKeySecurityForTTS:
    """Tests for API key security in TTS generation (AC2)."""

    def test_api_key_never_in_logs(self, mock_elevenlabs_sdk, caplog):
        """
        [2.2-UNIT-004] AC2: API key never exposed in logs.
        
        GIVEN TTS generation is running
        WHEN logs are produced
        THEN the API key is never exposed in log output.
        """
        import logging
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        
        mock_client_cls, mock_client, _ = mock_elevenlabs_sdk
        
        with caplog.at_level(logging.DEBUG):
            adapter = ElevenLabsAdapter(api_key="super-secret-eleven-key")
            adapter.generate_speech("Test script")
        
        for record in caplog.records:
            assert "super-secret-eleven-key" not in record.message

    def test_api_key_never_in_error_messages(self, mock_elevenlabs_sdk_error):
        """
        [2.2-UNIT-005] AC2: API key never in error messages.
        
        GIVEN an API error occurs
        WHEN the error is raised
        THEN the API key is not exposed in the error message.
        """
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        from eleven_video.exceptions.custom_errors import ElevenLabsAPIError
        
        mock_client_cls, mock_client, set_error = mock_elevenlabs_sdk_error
        set_error(Exception("API Error with key xi-key-secret123"))
        
        adapter = ElevenLabsAdapter(api_key="xi-key-secret123")
        
        with pytest.raises(ElevenLabsAPIError) as exc_info:
            adapter.generate_speech("Test script")
        
        assert "xi-key-secret123" not in str(exc_info.value)


# =============================================================================
# Story 2.2: AC3 - Progress Indicator Tests
# =============================================================================

class TestProgressIndicatorForTTS:
    """Tests for progress indicator during TTS generation (AC3, FR23)."""

    def test_progress_callback_called_during_generation(self, mock_elevenlabs_sdk):
        """
        [2.2-UNIT-006] AC3/FR23: Progress callback invoked during generation.
        
        GIVEN a progress callback is provided
        WHEN TTS generation runs
        THEN the callback is invoked with status updates.
        """
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        
        mock_client_cls, mock_client, _ = mock_elevenlabs_sdk
        
        progress_updates = []
        def progress_callback(status: str):
            progress_updates.append(status)
        
        adapter = ElevenLabsAdapter(api_key="test-key")
        adapter.generate_speech("Test script", progress_callback=progress_callback)
        
        assert len(progress_updates) > 0


# =============================================================================
# Story 2.2: AC4 - Invalid Script Validation Tests
# =============================================================================

class TestInvalidScriptHandling:
    """Tests for empty/invalid script handling (AC4)."""

    def test_empty_text_raises_validation_error(self, mock_elevenlabs_sdk):
        """
        [2.2-UNIT-007] AC4: Empty text raises validation error.
        
        GIVEN an empty script text
        WHEN generation is attempted
        THEN a clear validation error is raised before API call.
        """
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        from eleven_video.exceptions.custom_errors import ValidationError
        
        mock_client_cls, mock_client, _ = mock_elevenlabs_sdk
        
        adapter = ElevenLabsAdapter(api_key="test-key")
        
        with pytest.raises(ValidationError):
            adapter.generate_speech("")

    def test_whitespace_only_text_raises_error(self, mock_elevenlabs_sdk):
        """
        [2.2-UNIT-008] AC4: Whitespace-only text raises error.
        
        GIVEN a whitespace-only script
        WHEN generation is attempted
        THEN a validation error is raised.
        """
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        from eleven_video.exceptions.custom_errors import ValidationError
        
        mock_client_cls, mock_client, _ = mock_elevenlabs_sdk
        
        adapter = ElevenLabsAdapter(api_key="test-key")
        
        with pytest.raises(ValidationError):
            adapter.generate_speech("   \n\t   ")

    def test_none_text_raises_error(self, mock_elevenlabs_sdk):
        """
        [2.2-UNIT-009] AC4: None text raises error.
        
        GIVEN a None script text
        WHEN generation is attempted
        THEN a validation error is raised.
        """
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        from eleven_video.exceptions.custom_errors import ValidationError
        
        mock_client_cls, mock_client, _ = mock_elevenlabs_sdk
        
        adapter = ElevenLabsAdapter(api_key="test-key")
        
        with pytest.raises((ValidationError, TypeError)):
            adapter.generate_speech(None)


# =============================================================================
# Story 2.2: AC5 - API Error Handling Tests
# =============================================================================

class TestTTSApiErrorHandling:
    """Tests for API error handling in TTS generation (AC5)."""

    def test_auth_error_shows_user_friendly_message(self, mock_elevenlabs_sdk_error):
        """
        [2.2-UNIT-010] AC5: 401 error shows authentication message.
        
        GIVEN a 401 Unauthorized error from ElevenLabs API
        WHEN the error is caught
        THEN a user-friendly message about authentication is shown.
        """
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        from eleven_video.exceptions.custom_errors import ElevenLabsAPIError
        
        mock_client_cls, mock_client, set_error = mock_elevenlabs_sdk_error
        set_error(Exception("401 Unauthorized"))
        
        adapter = ElevenLabsAdapter(api_key="test-key")
        
        with pytest.raises(ElevenLabsAPIError) as exc_info:
            adapter.generate_speech("Test script")
        
        error_msg = str(exc_info.value).lower()
        assert "authentication" in error_msg or "api key" in error_msg or "unauthorized" in error_msg

    def test_rate_limit_error_suggests_retry(self, mock_elevenlabs_sdk_error):
        """
        [2.2-UNIT-011] AC5: 429 error suggests retry.
        
        GIVEN a 429 Rate Limit error from ElevenLabs API
        WHEN the error is caught
        THEN a message suggesting retry is shown.
        """
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        from eleven_video.exceptions.custom_errors import ElevenLabsAPIError
        
        mock_client_cls, mock_client, set_error = mock_elevenlabs_sdk_error
        set_error(Exception("429 Rate limit exceeded"))
        
        adapter = ElevenLabsAdapter(api_key="test-key")
        
        with pytest.raises(ElevenLabsAPIError) as exc_info:
            adapter.generate_speech("Test script")
        
        error_msg = str(exc_info.value).lower()
        assert "rate limit" in error_msg or "retry" in error_msg or "quota" in error_msg

    def test_server_error_shows_retry_message(self, mock_elevenlabs_sdk_error):
        """
        [2.2-UNIT-012] AC5: 500 error shows server issue message.
        
        GIVEN a 500 Server Error from ElevenLabs API
        WHEN the error is caught
        THEN a message about server issues is shown.
        """
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        from eleven_video.exceptions.custom_errors import ElevenLabsAPIError
        
        mock_client_cls, mock_client, set_error = mock_elevenlabs_sdk_error
        set_error(Exception("500 Internal Server Error"))
        
        adapter = ElevenLabsAdapter(api_key="test-key")
        
        with pytest.raises(ElevenLabsAPIError) as exc_info:
            adapter.generate_speech("Test script")
        
        error_msg = str(exc_info.value).lower()
        assert "server" in error_msg or "try again" in error_msg or "internal" in error_msg

    def test_timeout_error_shows_timeout_message(self, mock_elevenlabs_sdk_error):
        """
        [2.2-UNIT-013] AC5: Timeout shows timeout message.
        
        GIVEN a timeout error from ElevenLabs API
        WHEN the error is caught
        THEN a message about timeout is shown.
        """
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        from eleven_video.exceptions.custom_errors import ElevenLabsAPIError
        
        mock_client_cls, mock_client, set_error = mock_elevenlabs_sdk_error
        set_error(TimeoutError("Request timed out"))
        
        adapter = ElevenLabsAdapter(api_key="test-key")
        
        with pytest.raises(ElevenLabsAPIError) as exc_info:
            adapter.generate_speech("Test script")
        
        error_msg = str(exc_info.value).lower()
        assert "timeout" in error_msg or "timed out" in error_msg
