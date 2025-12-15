"""
Test Fixtures for API Adapters - Epic 2

Mock responses for ElevenLabs TTS and Gemini APIs to enable offline testing.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json


# =============================================================================
# ElevenLabs TTS Mock Responses
# =============================================================================

ELEVENLABS_VOICES_RESPONSE = {
    "voices": [
        {
            "voice_id": "21m00Tcm4TlvDq8ikWAM",
            "name": "Rachel",
            "category": "premade",
            "labels": {"accent": "american", "gender": "female"}
        },
        {
            "voice_id": "AZnzlk1XvdvUeBnXmlld",
            "name": "Domi",
            "category": "premade",
            "labels": {"accent": "american", "gender": "female"}
        },
        {
            "voice_id": "EXAVITQu4vr4xnSDxMaL",
            "name": "Bella",
            "category": "premade",
            "labels": {"accent": "american", "gender": "female"}
        }
    ]
}

ELEVENLABS_USER_RESPONSE = {
    "subscription": {
        "tier": "free",
        "character_count": 1234,
        "character_limit": 10000,
        "next_character_count_reset_unix": 1735689600
    }
}

# Sample MP3 audio bytes (minimal valid MP3 header)
ELEVENLABS_AUDIO_BYTES = bytes([
    0xFF, 0xFB, 0x90, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
])


@pytest.fixture
def mock_elevenlabs_tts():
    """Mock ElevenLabs TTS API responses."""
    with patch("httpx.Client") as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = ELEVENLABS_AUDIO_BYTES
        mock_response.headers = {"content-type": "audio/mpeg"}
        mock_client.return_value.post.return_value = mock_response
        yield mock_client


@pytest.fixture
def mock_elevenlabs_voices():
    """Mock ElevenLabs voices list API."""
    with patch("httpx.Client") as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = ELEVENLABS_VOICES_RESPONSE
        mock_client.return_value.get.return_value = mock_response
        yield mock_client


@pytest.fixture
def mock_elevenlabs_user():
    """Mock ElevenLabs user/subscription API."""
    with patch("httpx.Client") as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = ELEVENLABS_USER_RESPONSE
        mock_client.return_value.get.return_value = mock_response
        yield mock_client


# =============================================================================
# Google Gemini Mock Responses
# =============================================================================

GEMINI_TEXT_RESPONSE = {
    "candidates": [
        {
            "content": {
                "parts": [
                    {"text": "This is a sample generated script for your video."}
                ],
                "role": "model"
            },
            "finishReason": "STOP"
        }
    ],
    "usageMetadata": {
        "promptTokenCount": 10,
        "candidatesTokenCount": 50,
        "totalTokenCount": 60
    }
}

GEMINI_MODELS_RESPONSE = {
    "models": [
        {
            "name": "models/gemini-2.5-flash",
            "displayName": "Gemini 2.5 Flash",
            "supportedGenerationMethods": ["generateContent", "streamGenerateContent"]
        },
        {
            "name": "models/gemini-1.5-pro",
            "displayName": "Gemini 1.5 Pro",
            "supportedGenerationMethods": ["generateContent", "streamGenerateContent"]
        }
    ]
}

GEMINI_ERROR_RESPONSE = {
    "error": {
        "code": 400,
        "message": "Invalid API key",
        "status": "INVALID_ARGUMENT"
    }
}


@pytest.fixture
def mock_gemini_text():
    """Mock Gemini text generation API."""
    with patch("httpx.Client") as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = GEMINI_TEXT_RESPONSE
        mock_client.return_value.post.return_value = mock_response
        yield mock_client


@pytest.fixture
def mock_gemini_models():
    """Mock Gemini models list API."""
    with patch("httpx.Client") as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = GEMINI_MODELS_RESPONSE
        mock_client.return_value.get.return_value = mock_response
        yield mock_client


@pytest.fixture
def mock_gemini_error():
    """Mock Gemini API error response."""
    with patch("httpx.Client") as mock_client:
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = GEMINI_ERROR_RESPONSE
        mock_response.raise_for_status.side_effect = Exception("400 Bad Request")
        mock_client.return_value.post.return_value = mock_response
        yield mock_client


# =============================================================================
# Combined API Fixtures
# =============================================================================

@pytest.fixture
def mock_all_apis():
    """
    Mock all external API calls for fully offline testing.
    
    Usage:
        def test_video_pipeline(mock_all_apis):
            # All API calls are mocked
            pass
    """
    with patch("httpx.Client") as mock_client:
        instance = mock_client.return_value
        
        def mock_request(method, url, **kwargs):
            mock_resp = Mock()
            mock_resp.status_code = 200
            
            if "elevenlabs.io" in url:
                if "text-to-speech" in url:
                    mock_resp.content = ELEVENLABS_AUDIO_BYTES
                    mock_resp.headers = {"content-type": "audio/mpeg"}
                elif "voices" in url:
                    mock_resp.json.return_value = ELEVENLABS_VOICES_RESPONSE
                elif "user" in url:
                    mock_resp.json.return_value = ELEVENLABS_USER_RESPONSE
            elif "generativelanguage.googleapis.com" in url:
                if "generateContent" in url:
                    mock_resp.json.return_value = GEMINI_TEXT_RESPONSE
                elif "models" in url:
                    mock_resp.json.return_value = GEMINI_MODELS_RESPONSE
            
            return mock_resp
        
        instance.request = mock_request
        instance.get = lambda url, **kw: mock_request("GET", url, **kw)
        instance.post = lambda url, **kw: mock_request("POST", url, **kw)
        
        yield mock_client


# =============================================================================
# Rate Limit / Error Simulation Fixtures
# =============================================================================

@pytest.fixture
def mock_rate_limited():
    """Simulate rate limiting (429) response."""
    with patch("httpx.Client") as mock_client:
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_response.json.return_value = {"error": "Rate limit exceeded"}
        mock_client.return_value.post.return_value = mock_response
        mock_client.return_value.get.return_value = mock_response
        yield mock_client


@pytest.fixture
def mock_server_error():
    """Simulate server error (500) response."""
    with patch("httpx.Client") as mock_client:
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal server error"}
        mock_client.return_value.post.return_value = mock_response
        mock_client.return_value.get.return_value = mock_response
        yield mock_client
