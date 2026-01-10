"""Factory functions for API mock responses (Story 5.1).

Provides standardized mock response factories for Gemini and ElevenLabs APIs
with override support for flexible test data generation.
"""
from typing import Dict, Any, Optional, List
from unittest.mock import MagicMock
from datetime import datetime
import uuid


def create_gemini_response(overrides: Dict[str, Any] = None) -> MagicMock:
    """Factory for Gemini API mock responses.
    
    Creates a properly structured MagicMock that mimics the Google GenAI 
    response format with usage_metadata for token tracking.
    
    Args:
        overrides: Optional dict to override default values. Supports:
            - text: Response text content (default: "Generated content")
            - finish_reason: Finish reason enum (default: None)
            - input_tokens: Prompt token count (default: 100)
            - output_tokens: Candidates token count (default: 200)
            - model: Model ID (default: "gemini-1.5-flash")
    
    Returns:
        MagicMock configured as a Gemini API response
    
    Example:
        >>> response = create_gemini_response({"input_tokens": 50, "output_tokens": 100})
        >>> response.usage_metadata.prompt_token_count
        50
    """
    overrides = overrides or {}
    
    mock_response = MagicMock()
    mock_response.candidates = [
        MagicMock(
            content=MagicMock(
                parts=[MagicMock(text=overrides.get("text", "Generated content"))]
            ),
            finish_reason=overrides.get("finish_reason", None)
        )
    ]
    mock_response.usage_metadata = MagicMock()
    mock_response.usage_metadata.prompt_token_count = overrides.get("input_tokens", 100)
    mock_response.usage_metadata.candidates_token_count = overrides.get("output_tokens", 200)
    
    return mock_response


def create_gemini_image_response(overrides: Dict[str, Any] = None) -> MagicMock:
    """Factory for Gemini image generation mock responses.
    
    Creates a MagicMock that mimics the Gemini image generation response
    with inline_data containing base64 image data.
    
    Args:
        overrides: Optional dict to override default values. Supports:
            - image_data: Base64 image data (default: test bytes)
            - mime_type: MIME type (default: "image/png")
            - input_tokens: Prompt token count (default: 50)
            - output_tokens: Output token count (default: 0)
    
    Returns:
        MagicMock configured as a Gemini image API response
    """
    overrides = overrides or {}
    
    mock_response = MagicMock()
    mock_part = MagicMock()
    mock_part.inline_data = MagicMock()
    mock_part.inline_data.data = overrides.get("image_data", b"fake_image_data_base64")
    mock_part.inline_data.mime_type = overrides.get("mime_type", "image/png")
    mock_part.text = None  # Image responses don't have text
    
    mock_response.candidates = [
        MagicMock(
            content=MagicMock(parts=[mock_part]),
            finish_reason=overrides.get("finish_reason", None)
        )
    ]
    mock_response.usage_metadata = MagicMock()
    mock_response.usage_metadata.prompt_token_count = overrides.get("input_tokens", 50)
    mock_response.usage_metadata.candidates_token_count = overrides.get("output_tokens", 0)
    
    return mock_response


def create_elevenlabs_response(overrides: Dict[str, Any] = None) -> List[bytes]:
    """Factory for ElevenLabs TTS mock responses.
    
    Creates a list of byte chunks that mimics the ElevenLabs streaming
    audio response format.
    
    Args:
        overrides: Optional dict to override default values. Supports:
            - audio_chunks: List of byte chunks (default: [b"audio", b"data"])
            - chunk_count: Number of chunks to generate (default: 2)
    
    Returns:
        List of bytes representing audio chunks
    
    Example:
        >>> response = create_elevenlabs_response({"chunk_count": 3})
        >>> len(response)
        3
    """
    overrides = overrides or {}
    
    if "audio_chunks" in overrides:
        return overrides["audio_chunks"]
    
    chunk_count = overrides.get("chunk_count", 2)
    return [f"audio_chunk_{i}".encode() for i in range(chunk_count)]


def create_elevenlabs_voice_response(overrides: Dict[str, Any] = None) -> MagicMock:
    """Factory for ElevenLabs voice info mock responses.
    
    Creates a MagicMock that mimics the ElevenLabs voice metadata response.
    
    Args:
        overrides: Optional dict to override default values. Supports:
            - voice_id: Voice ID (default: UUID)
            - name: Voice name (default: "Test Voice")
            - category: Voice category (default: "premade")
    
    Returns:
        MagicMock configured as an ElevenLabs voice response
    """
    overrides = overrides or {}
    
    mock_voice = MagicMock()
    mock_voice.voice_id = overrides.get("voice_id", str(uuid.uuid4()))
    mock_voice.name = overrides.get("name", "Test Voice")
    mock_voice.category = overrides.get("category", "premade")
    mock_voice.labels = overrides.get("labels", {"accent": "american", "gender": "male"})
    
    return mock_voice


def create_usage_metadata(overrides: Dict[str, Any] = None) -> MagicMock:
    """Factory for usage metadata mock objects.
    
    Creates a standalone usage_metadata mock for partial response testing.
    
    Args:
        overrides: Optional dict to override default values. Supports:
            - prompt_token_count: Input tokens (default: 100)
            - candidates_token_count: Output tokens (default: 200)
            - total_token_count: Total tokens (default: sum of above)
    
    Returns:
        MagicMock configured as usage metadata
    """
    overrides = overrides or {}
    
    input_tokens = overrides.get("prompt_token_count", 100)
    output_tokens = overrides.get("candidates_token_count", 200)
    
    mock_metadata = MagicMock()
    mock_metadata.prompt_token_count = input_tokens
    mock_metadata.candidates_token_count = output_tokens
    mock_metadata.total_token_count = overrides.get("total_token_count", input_tokens + output_tokens)
    
    return mock_metadata
