"""
Integration tests for ElevenLabs TTS API (Story 2.2).

Test IDs: 2.2-INT-001 to 2.2-INT-002
Tests real API connectivity - SKIP in CI (requires ELEVENLABS_API_KEY).

Split from test_elevenlabs_speech.py per TEA review (P1: file length recommendation).
Run manually with: uv run pytest tests/api/test_elevenlabs_integration.py -m integration -v
"""
import os
import pytest


# =============================================================================
# Story 2.2 Integration Tests (Skip in CI)
# =============================================================================

@pytest.mark.integration
class TestTTSGenerationIntegration:
    """Integration tests for real ElevenLabs API - skip in CI."""

    @pytest.mark.skipif(
        not os.environ.get("ELEVENLABS_API_KEY"),
        reason="ELEVENLABS_API_KEY not set"
    )
    def test_real_api_generates_audio(self):
        """
        [2.2-INT-001] Integration: Real API generates audio.
        
        GIVEN a valid ELEVENLABS_API_KEY in environment
        WHEN generate_speech is called with a real script
        THEN audio bytes are returned from the actual API.
        """
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        
        api_key = os.environ.get("ELEVENLABS_API_KEY")
        adapter = ElevenLabsAdapter(api_key=api_key)
        audio = adapter.generate_speech("Hello, this is a test of the ElevenLabs API.")
        
        assert audio is not None
        assert len(audio.data) > 100  # Should have substantial audio data
        assert audio.file_size_bytes > 0

    @pytest.mark.skipif(
        not os.environ.get("ELEVENLABS_API_KEY"),
        reason="ELEVENLABS_API_KEY not set"
    )
    def test_real_api_with_settings_class(self):
        """
        [2.2-INT-002] Integration: Real API with Settings class.
        
        GIVEN a valid ELEVENLABS_API_KEY via Settings class
        WHEN ElevenLabsAdapter is created with Settings
        THEN audio generation works correctly.
        """
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        from eleven_video.config.settings import Settings
        
        try:
            settings = Settings()
        except Exception:
            pytest.skip("Settings not configured with API keys")
        
        adapter = ElevenLabsAdapter(settings=settings)
        audio = adapter.generate_speech("Testing with Settings class.")
        
        assert audio is not None
        assert len(audio.data) > 50
