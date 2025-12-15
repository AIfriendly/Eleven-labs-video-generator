"""
Tests for ElevenLabs API protocols, domain models, and exceptions (Story 2.2).

Test IDs: 2.2-UNIT-014 to 2.2-UNIT-019
Tests cover Audio domain model, SpeechGenerator protocol, ElevenLabsAPIError, and Settings support.

Split from test_elevenlabs_speech.py per TEA review (P1: file length recommendation).
"""
import pytest
from unittest.mock import MagicMock, patch


# =============================================================================
# Story 2.2: AC6 - Audio Domain Model Tests
# =============================================================================

class TestAudioDomainModel:
    """Tests for Audio domain model (AC6)."""

    def test_audio_model_exists(self):
        """
        [2.2-UNIT-014] AC6: Audio domain model exists.
        
        GIVEN the models.domain module
        WHEN importing Audio
        THEN the class should exist.
        """
        from eleven_video.models.domain import Audio
        
        assert Audio is not None

    def test_audio_model_has_required_attributes(self):
        """
        [2.2-UNIT-015] AC6: Audio model has required attributes.
        
        GIVEN an Audio instance
        WHEN accessing attributes
        THEN data, duration_seconds, and file_size_bytes exist.
        """
        from eleven_video.models.domain import Audio
        
        audio = Audio(
            data=b'\xff\xfb\x90\x00',
            duration_seconds=5.0,
            file_size_bytes=1024
        )
        
        assert hasattr(audio, 'data')
        assert hasattr(audio, 'duration_seconds')
        assert hasattr(audio, 'file_size_bytes')
        assert audio.data == b'\xff\xfb\x90\x00'
        assert audio.duration_seconds == 5.0
        assert audio.file_size_bytes == 1024


# =============================================================================
# Protocol Tests
# =============================================================================

class TestSpeechGeneratorProtocol:
    """Tests for SpeechGenerator protocol compliance."""

    def test_speech_generator_protocol_exists(self):
        """
        [2.2-UNIT-016] SpeechGenerator protocol exists.
        
        GIVEN the interfaces module
        WHEN importing SpeechGenerator
        THEN the protocol should exist.
        """
        from eleven_video.api.interfaces import SpeechGenerator
        
        assert SpeechGenerator is not None

    def test_elevenlabs_adapter_has_generate_speech_method(self):
        """
        [2.2-UNIT-017] Adapter has generate_speech method.
        
        GIVEN the ElevenLabsAdapter class
        WHEN checking for generate_speech method
        THEN the method exists with correct signature.
        """
        with patch("eleven_video.api.elevenlabs.ElevenLabs"):
            from eleven_video.api.elevenlabs import ElevenLabsAdapter
            
            adapter = ElevenLabsAdapter(api_key="test-key")
            
            assert hasattr(adapter, 'generate_speech')
            assert callable(getattr(adapter, 'generate_speech'))


# =============================================================================
# Exception Tests
# =============================================================================

class TestElevenLabsAPIErrorExists:
    """Tests for ElevenLabsAPIError exception class."""

    def test_elevenlabs_api_error_exists(self):
        """
        [2.2-UNIT-018] ElevenLabsAPIError exception exists.
        
        GIVEN the exceptions module
        WHEN importing ElevenLabsAPIError
        THEN the class should exist.
        """
        from eleven_video.exceptions.custom_errors import ElevenLabsAPIError
        
        assert ElevenLabsAPIError is not None
        assert issubclass(ElevenLabsAPIError, Exception)


# =============================================================================
# Settings Support Tests
# =============================================================================

class TestSettingsSupport:
    """Tests for Settings class support in ElevenLabsAdapter."""

    def test_adapter_accepts_settings_parameter(self):
        """
        [2.2-UNIT-019] Adapter accepts Settings parameter.
        
        GIVEN a Settings instance with elevenlabs_api_key
        WHEN creating ElevenLabsAdapter with settings
        THEN the adapter initializes correctly.
        """
        with patch("eleven_video.api.elevenlabs.ElevenLabs"):
            mock_settings = MagicMock()
            mock_settings.elevenlabs_api_key.get_secret_value.return_value = "settings-api-key"
            
            from eleven_video.api.elevenlabs import ElevenLabsAdapter
            
            adapter = ElevenLabsAdapter(settings=mock_settings)
            
            assert adapter is not None
