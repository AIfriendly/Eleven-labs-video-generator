"""
Tests for ElevenLabs Voice Model Selection - Story 3.1

RED Phase: All tests are designed to FAIL before implementation.
Follow TDD red-green-refactor cycle to implement Story 3.1 features.

Test IDs: 3.1-UNIT-001 to 3.1-UNIT-015
Tests cover:
- VoiceInfo domain model (AC: #4)
- VoiceLister protocol (AC: #4)
- list_voices() method (AC: #4)
- validate_voice_id() method (AC: #3)
- Fallback behavior with warning callback (AC: #2, #3)
- Pipeline voice_id parameter (AC: #1)
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from typing import Optional, Callable


# =============================================================================
# Test Group 1: VoiceInfo Domain Model (Task 1)
# =============================================================================

class TestVoiceInfoModel:
    """Tests for VoiceInfo dataclass in eleven_video/models/domain.py."""

    def test_voiceinfo_can_be_imported(self):
        """[3.1-UNIT-001] VoiceInfo should be importable from domain models.
        
        RED Phase: This test will fail until VoiceInfo dataclass is created.
        """
        # Given: The domain module exists with existing models
        # When: Importing VoiceInfo from domain module
        from eleven_video.models.domain import VoiceInfo
        
        # Then: VoiceInfo should exist
        assert VoiceInfo is not None

    def test_voiceinfo_has_required_fields(self):
        """[3.1-UNIT-002] VoiceInfo should have voice_id, name, category, preview_url fields.
        
        RED Phase: This test will fail until VoiceInfo is implemented with all fields.
        """
        # Given: VoiceInfo is created with all required fields
        from eleven_video.models.domain import VoiceInfo
        
        # When: Creating a VoiceInfo instance
        voice = VoiceInfo(
            voice_id="test-voice-id",
            name="Test Voice",
            category="premade",
            preview_url="https://example.com/preview.mp3"
        )
        
        # Then: All fields should be accessible
        assert voice.voice_id == "test-voice-id"
        assert voice.name == "Test Voice"
        assert voice.category == "premade"
        assert voice.preview_url == "https://example.com/preview.mp3"

    def test_voiceinfo_category_is_optional(self):
        """[3.1-UNIT-003] VoiceInfo category and preview_url should be optional.
        
        RED Phase: This test will fail until optional fields are implemented.
        """
        # Given: VoiceInfo allows optional fields
        from eleven_video.models.domain import VoiceInfo
        
        # When: Creating VoiceInfo with only required fields
        voice = VoiceInfo(
            voice_id="minimal-voice",
            name="Minimal Voice"
        )
        
        # Then: Optional fields should default to None
        assert voice.voice_id == "minimal-voice"
        assert voice.name == "Minimal Voice"
        assert voice.category is None
        assert voice.preview_url is None

    def test_voiceinfo_is_dataclass(self):
        """[3.1-UNIT-004] VoiceInfo should be a dataclass for easy comparison and repr.
        
        RED Phase: This test will fail until VoiceInfo is decorated with @dataclass.
        """
        # Given: VoiceInfo is imported
        from eleven_video.models.domain import VoiceInfo
        from dataclasses import is_dataclass
        
        # When: Checking if VoiceInfo is a dataclass
        # Then: It should be a dataclass
        assert is_dataclass(VoiceInfo), "VoiceInfo must be a dataclass"


# =============================================================================
# Test Group 2: VoiceLister Protocol (Task 3)
# =============================================================================

class TestVoiceListerProtocol:
    """Tests for VoiceLister protocol in eleven_video/api/interfaces.py."""

    def test_voicelister_protocol_can_be_imported(self):
        """[3.1-UNIT-005] VoiceLister protocol should be importable from interfaces.
        
        RED Phase: This test will fail until VoiceLister protocol is defined.
        """
        # Given: The interfaces module exists
        # When: Importing VoiceLister
        from eleven_video.api.interfaces import VoiceLister
        
        # Then: VoiceLister should exist
        assert VoiceLister is not None

    def test_voicelister_is_runtime_checkable(self):
        """[3.1-UNIT-006] VoiceLister should be a runtime_checkable Protocol.
        
        RED Phase: This test will fail until VoiceLister is decorated correctly.
        """
        # Given: VoiceLister protocol is imported
        from eleven_video.api.interfaces import VoiceLister
        from typing import runtime_checkable, Protocol
        
        # When: Checking if VoiceLister is a Protocol
        # Then: It should be a subclass of Protocol
        assert issubclass(VoiceLister, Protocol)

    def test_elevenlabs_adapter_implements_voicelister(self):
        """[3.1-UNIT-007] ElevenLabsAdapter should implement VoiceLister protocol.
        
        RED Phase: This test will fail until list_voices() is added to adapter.
        """
        # Given: VoiceLister protocol and ElevenLabsAdapter
        from eleven_video.api.interfaces import VoiceLister
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        
        adapter = ElevenLabsAdapter(api_key="test-key")
        
        # When: Checking if adapter implements VoiceLister
        # Then: Adapter should have list_voices method
        assert hasattr(adapter, 'list_voices'), "Adapter must have list_voices method"
        assert isinstance(adapter, VoiceLister), "Adapter must implement VoiceLister protocol"


# =============================================================================
# Test Group 3: list_voices() Method (Task 2)
# =============================================================================

class TestListVoices:
    """Tests for ElevenLabsAdapter.list_voices() method."""

    def test_list_voices_returns_list_of_voiceinfo(self):
        """[3.1-UNIT-008] list_voices() should return list[VoiceInfo].
        
        RED Phase: This test will fail until list_voices() is implemented.
        """
        # Given: A mocked ElevenLabs SDK response
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        from eleven_video.models.domain import VoiceInfo
        
        adapter = ElevenLabsAdapter(api_key="test-key")
        
        # Mock SDK response
        mock_voice = MagicMock()
        mock_voice.voice_id = "21m00Tcm4TlvDq8ikWAM"
        mock_voice.name = "Rachel"
        mock_voice.category = "premade"
        mock_voice.preview_url = "https://example.com/rachel.mp3"
        
        mock_voices_response = MagicMock()
        mock_voices_response.voices = [mock_voice]
        
        with patch.object(adapter, '_get_sdk_client') as mock_client:
            mock_client.return_value.voices.get_all.return_value = mock_voices_response
            
            # When: Calling list_voices()
            result = adapter.list_voices()
        
        # Then: Result should be list of VoiceInfo objects
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], VoiceInfo)
        assert result[0].voice_id == "21m00Tcm4TlvDq8ikWAM"
        assert result[0].name == "Rachel"
        assert result[0].category == "premade"

    def test_list_voices_handles_multiple_voices(self):
        """[3.1-UNIT-009] list_voices() should handle multiple voices correctly.
        
        RED Phase: This test will fail until list_voices() is implemented.
        """
        # Given: SDK returns multiple voices
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        from eleven_video.models.domain import VoiceInfo
        
        adapter = ElevenLabsAdapter(api_key="test-key")
        
        # Create multiple mock voices
        mock_voices = []
        for i, (vid, name) in enumerate([
            ("voice-1", "Alice"),
            ("voice-2", "Bob"),
            ("voice-3", "Charlie")
        ]):
            mock_voice = MagicMock()
            mock_voice.voice_id = vid
            mock_voice.name = name
            mock_voice.category = "premade"
            mock_voice.preview_url = None
            mock_voices.append(mock_voice)
        
        mock_response = MagicMock()
        mock_response.voices = mock_voices
        
        with patch.object(adapter, '_get_sdk_client') as mock_client:
            mock_client.return_value.voices.get_all.return_value = mock_response
            
            # When: Calling list_voices()
            result = adapter.list_voices()
        
        # Then: All voices should be returned
        assert len(result) == 3
        assert result[0].name == "Alice"
        assert result[1].name == "Bob"
        assert result[2].name == "Charlie"

    def test_list_voices_handles_empty_response(self):
        """[3.1-UNIT-010] list_voices() should return empty list when no voices available.
        
        RED Phase: This test will fail until list_voices() is implemented.
        """
        # Given: SDK returns empty voices list
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        
        adapter = ElevenLabsAdapter(api_key="test-key")
        
        mock_response = MagicMock()
        mock_response.voices = []
        
        with patch.object(adapter, '_get_sdk_client') as mock_client:
            mock_client.return_value.voices.get_all.return_value = mock_response
            
            # When: Calling list_voices()
            result = adapter.list_voices()
        
        # Then: Should return empty list (not None or error)
        assert isinstance(result, list)
        assert len(result) == 0


# =============================================================================
# Test Group 4: Voice ID Validation (Task 4)
# =============================================================================

class TestVoiceIdValidation:
    """Tests for voice ID validation and fallback behavior."""

    def test_validate_voice_id_returns_true_for_valid_id(self):
        """[3.1-UNIT-011] validate_voice_id() should return True for existing voice ID.
        
        RED Phase: This test will fail until validate_voice_id() is implemented.
        """
        # Given: A valid voice ID that exists in the voice list
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        
        adapter = ElevenLabsAdapter(api_key="test-key")
        
        # Mock list_voices to return a known voice
        mock_voice = MagicMock()
        mock_voice.voice_id = "valid-voice-id"
        mock_voice.name = "Valid Voice"
        mock_voice.category = "premade"
        mock_voice.preview_url = None
        
        mock_response = MagicMock()
        mock_response.voices = [mock_voice]
        
        with patch.object(adapter, '_get_sdk_client') as mock_client:
            mock_client.return_value.voices.get_all.return_value = mock_response
            
            # When: Validating a known good voice ID
            result = adapter.validate_voice_id("valid-voice-id")
        
        # Then: Should return True
        assert result is True

    def test_validate_voice_id_returns_false_for_invalid_id(self):
        """[3.1-UNIT-012] validate_voice_id() should return False for non-existent voice ID.
        
        RED Phase: This test will fail until validate_voice_id() is implemented.
        """
        # Given: An invalid voice ID that doesn't exist
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        
        adapter = ElevenLabsAdapter(api_key="test-key")
        
        mock_response = MagicMock()
        mock_response.voices = []  # No voices match
        
        with patch.object(adapter, '_get_sdk_client') as mock_client:
            mock_client.return_value.voices.get_all.return_value = mock_response
            
            # When: Validating an invalid voice ID
            result = adapter.validate_voice_id("non-existent-voice-id")
        
        # Then: Should return False
        assert result is False


# =============================================================================
# Test Group 5: Fallback Behavior with Warning (Task 4)
# =============================================================================

class TestFallbackWithWarning:
    """Tests for generate_speech fallback behavior with warning callback (AC: #3)."""

    def test_generate_speech_falls_back_with_warning_on_invalid_voice(self):
        """[3.1-UNIT-013] generate_speech with invalid voice_id should fallback and warn.
        
        RED Phase: This test will fail until fallback + warning_callback is implemented.
        
        AC3: Given I specify an invalid voice ID, When TTS generation runs,
        Then the system falls back to the default voice with a warning message.
        """
        # Given: An invalid voice ID and a warning callback
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        from eleven_video.models.domain import Audio
        
        adapter = ElevenLabsAdapter(api_key="test-key")
        
        warnings_received = []
        def warning_callback(message: str):
            warnings_received.append(message)
        
        # Mock validate_voice_id to return False
        # Mock generate_with_retry to return audio
        with patch.object(adapter, 'validate_voice_id', return_value=False):
            with patch.object(adapter, '_generate_with_retry') as mock_generate:
                mock_generate.return_value = Audio(data=b"fake-audio")
                
                # When: Generating speech with invalid voice ID
                result = adapter.generate_speech(
                    text="Test text",
                    voice_id="invalid-voice-id",
                    warning_callback=warning_callback
                )
        
        # Then: Should produce audio (using default) and emit warning
        assert result is not None
        assert isinstance(result, Audio)
        assert len(warnings_received) >= 1
        # Warning should mention both the invalid ID and fallback
        warning_text = warnings_received[0].lower()
        assert "invalid" in warning_text or "fallback" in warning_text or "default" in warning_text

    def test_generate_speech_no_warning_for_valid_voice(self):
        """[3.1-UNIT-014] generate_speech with valid voice_id should not warn.
        
        RED Phase: This test will fail until warning_callback parameter is added.
        """
        # Given: A valid voice ID and a warning callback
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        from eleven_video.models.domain import Audio
        
        adapter = ElevenLabsAdapter(api_key="test-key")
        
        warnings_received = []
        def warning_callback(message: str):
            warnings_received.append(message)
        
        # Mock validate_voice_id to return True
        with patch.object(adapter, 'validate_voice_id', return_value=True):
            with patch.object(adapter, '_generate_with_retry') as mock_generate:
                mock_generate.return_value = Audio(data=b"fake-audio")
                
                # When: Generating speech with valid voice ID
                result = adapter.generate_speech(
                    text="Test text",
                    voice_id="valid-voice-id",
                    warning_callback=warning_callback
                )
        
        # Then: Should not emit any warning
        assert result is not None
        assert len(warnings_received) == 0


# =============================================================================
# Test Group 6: Default Voice Behavior (AC: #2)
# =============================================================================

class TestDefaultVoiceBehavior:
    """Tests for default voice behavior when no voice specified."""

    def test_generate_speech_uses_default_when_no_voice_specified(self):
        """[3.1-UNIT-015] generate_speech with no voice_id should use default.
        
        This test validates existing behavior is preserved (AC: #2).
        """
        # Given: No voice ID specified
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        from eleven_video.models.domain import Audio
        
        adapter = ElevenLabsAdapter(api_key="test-key")
        
        with patch.object(adapter, '_generate_with_retry') as mock_generate:
            mock_generate.return_value = Audio(data=b"fake-audio")
            
            # When: Generating speech without voice_id
            result = adapter.generate_speech(text="Test text")
        
        # Then: Should use default voice (call was made with DEFAULT_VOICE_ID)
        assert result is not None
        # The internal call should have used the default voice
        mock_generate.assert_called_once()
        call_args = mock_generate.call_args
        # voice_id should be the default (check both positional and keyword args)
        if call_args.kwargs:
            assert call_args.kwargs.get('voice_id') == ElevenLabsAdapter.DEFAULT_VOICE_ID
        else:
            # Positional: text, voice_id
            assert call_args[0][1] == ElevenLabsAdapter.DEFAULT_VOICE_ID


# =============================================================================
# Test Group 7: Retry Logic (Code Review Fix M1)
# =============================================================================

class TestRetryLogic:
    """Tests for _list_voices_with_retry() retry behavior."""

    def test_list_voices_retries_on_connection_error(self):
        """[3.1-UNIT-016] list_voices should retry on connection errors.
        
        Code Review Fix M1: Added retry logic with @retry decorator.
        """
        # Given: SDK raises connection error then succeeds
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        from eleven_video.models.domain import VoiceInfo
        
        adapter = ElevenLabsAdapter(api_key="test-key")
        
        mock_voice = MagicMock()
        mock_voice.voice_id = "voice-1"
        mock_voice.name = "Test Voice"
        mock_voice.category = "premade"
        mock_voice.preview_url = None
        
        mock_response = MagicMock()
        mock_response.voices = [mock_voice]
        
        # First call fails, second succeeds
        call_count = [0]
        def side_effect():
            call_count[0] += 1
            if call_count[0] < 2:
                raise ConnectionError("Network error")
            return mock_response
        
        with patch.object(adapter, '_get_sdk_client') as mock_client:
            mock_client.return_value.voices.get_all.side_effect = side_effect
            
            # When: Calling list_voices()
            result = adapter.list_voices()
        
        # Then: Should succeed after retry
        assert len(result) == 1
        assert result[0].voice_id == "voice-1"
        assert call_count[0] == 2  # Retry happened

    def test_list_voices_has_retry_decorator(self):
        """[3.1-UNIT-017] _list_voices_with_retry should have @retry decorator."""
        # Given: ElevenLabsAdapter class
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        from tenacity import retry
        
        # When: Checking the method
        method = ElevenLabsAdapter._list_voices_with_retry
        
        # Then: Method should have retry metadata from tenacity
        assert hasattr(method, 'retry')


# =============================================================================
# Test Group 8: Voice List Caching (Code Review Fix M2)
# =============================================================================

class TestVoiceCaching:
    """Tests for voice list caching behavior."""

    def test_list_voices_uses_cache_when_enabled(self):
        """[3.1-UNIT-018] list_voices(use_cache=True) should return cached voices.
        
        Code Review Fix M2: Added voice list caching with 60s TTL.
        """
        # Given: Adapter with cached voices
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        from eleven_video.models.domain import VoiceInfo
        import time
        
        adapter = ElevenLabsAdapter(api_key="test-key")
        
        # Manually set cache
        cached_voices = [VoiceInfo(voice_id="cached-1", name="Cached Voice")]
        adapter._voice_cache = (cached_voices, time.perf_counter())
        
        # When: Calling list_voices with use_cache=True
        result = adapter.list_voices(use_cache=True)
        
        # Then: Should return cached voices without API call
        assert len(result) == 1
        assert result[0].voice_id == "cached-1"
        assert result[0].name == "Cached Voice"

    def test_list_voices_ignores_cache_when_disabled(self):
        """[3.1-UNIT-019] list_voices(use_cache=False) should fetch fresh data."""
        # Given: Adapter with cached voices
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        from eleven_video.models.domain import VoiceInfo
        import time
        
        adapter = ElevenLabsAdapter(api_key="test-key")
        
        # Set cache with old data
        cached_voices = [VoiceInfo(voice_id="cached-1", name="Old Voice")]
        adapter._voice_cache = (cached_voices, time.perf_counter())
        
        # Setup mock for fresh API response
        mock_voice = MagicMock()
        mock_voice.voice_id = "fresh-1"
        mock_voice.name = "Fresh Voice"
        mock_voice.category = "premade"
        mock_voice.preview_url = None
        
        mock_response = MagicMock()
        mock_response.voices = [mock_voice]
        
        with patch.object(adapter, '_get_sdk_client') as mock_client:
            mock_client.return_value.voices.get_all.return_value = mock_response
            
            # When: Calling list_voices without use_cache
            result = adapter.list_voices(use_cache=False)
        
        # Then: Should return fresh data
        assert len(result) == 1
        assert result[0].voice_id == "fresh-1"
        assert result[0].name == "Fresh Voice"

    def test_list_voices_refreshes_expired_cache(self):
        """[3.1-UNIT-020] list_voices should refresh expired cache (>60s TTL)."""
        # Given: Adapter with expired cache
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        from eleven_video.models.domain import VoiceInfo
        import time
        
        adapter = ElevenLabsAdapter(api_key="test-key")
        
        # Set cache with very old timestamp (expired)
        cached_voices = [VoiceInfo(voice_id="old-1", name="Old Voice")]
        adapter._voice_cache = (cached_voices, time.perf_counter() - 120)  # 120s ago
        
        # Setup mock for fresh API response
        mock_voice = MagicMock()
        mock_voice.voice_id = "new-1"
        mock_voice.name = "New Voice"
        mock_voice.category = "premade"
        mock_voice.preview_url = None
        
        mock_response = MagicMock()
        mock_response.voices = [mock_voice]
        
        with patch.object(adapter, '_get_sdk_client') as mock_client:
            mock_client.return_value.voices.get_all.return_value = mock_response
            
            # When: Calling list_voices with use_cache=True but cache expired
            result = adapter.list_voices(use_cache=True)
        
        # Then: Should fetch fresh data due to expired cache
        assert len(result) == 1
        assert result[0].voice_id == "new-1"
        assert result[0].name == "New Voice"


# =============================================================================
# Factory Functions for Test Data
# =============================================================================

def create_voice_info(
    voice_id: str = "test-voice-id",
    name: str = "Test Voice",
    category: Optional[str] = "premade",
    preview_url: Optional[str] = None
):
    """Factory function for creating VoiceInfo test data.
    
    Uses pattern from data-factories.md knowledge base.
    """
    from eleven_video.models.domain import VoiceInfo
    return VoiceInfo(
        voice_id=voice_id,
        name=name,
        category=category,
        preview_url=preview_url
    )


def create_mock_elevenlabs_voice(
    voice_id: str = "test-voice-id",
    name: str = "Test Voice",
    category: str = "premade",
    preview_url: Optional[str] = None
) -> MagicMock:
    """Create a mock ElevenLabs SDK Voice object."""
    mock_voice = MagicMock()
    mock_voice.voice_id = voice_id
    mock_voice.name = name
    mock_voice.category = category
    mock_voice.preview_url = preview_url
    return mock_voice
