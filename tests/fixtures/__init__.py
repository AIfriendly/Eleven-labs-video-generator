"""
Fixtures package for Epic 2 API testing.

Provides mock responses for ElevenLabs and Gemini APIs to enable offline testing.
"""

from tests.fixtures.api_fixtures import (
    mock_elevenlabs_tts,
    mock_elevenlabs_voices,
    mock_elevenlabs_user,
    mock_gemini_text,
    mock_gemini_models,
    mock_gemini_error,
    mock_all_apis,
    mock_rate_limited,
    mock_server_error,
    ELEVENLABS_VOICES_RESPONSE,
    ELEVENLABS_USER_RESPONSE,
    ELEVENLABS_AUDIO_BYTES,
    GEMINI_TEXT_RESPONSE,
    GEMINI_MODELS_RESPONSE,
    GEMINI_ERROR_RESPONSE,
)

__all__ = [
    # Fixtures
    "mock_elevenlabs_tts",
    "mock_elevenlabs_voices",
    "mock_elevenlabs_user",
    "mock_gemini_text",
    "mock_gemini_models",
    "mock_gemini_error",
    "mock_all_apis",
    "mock_rate_limited",
    "mock_server_error",
    # Response data
    "ELEVENLABS_VOICES_RESPONSE",
    "ELEVENLABS_USER_RESPONSE",
    "ELEVENLABS_AUDIO_BYTES",
    "GEMINI_TEXT_RESPONSE",
    "GEMINI_MODELS_RESPONSE",
    "GEMINI_ERROR_RESPONSE",
]
