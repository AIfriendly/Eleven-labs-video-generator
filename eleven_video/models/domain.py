"""Domain models for the eleven-video application."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Script:
    """Generated video script from Gemini API.
    
    Attributes:
        content: The raw text content of the generated script.
    """
    content: str


@dataclass
class Audio:
    """Generated audio from TTS API (Story 2.2 - AC6).
    
    Attributes:
        data: Raw audio bytes in mp3 format.
        duration_seconds: Audio duration for downstream processing (optional).
        file_size_bytes: File size in bytes for downstream processing (optional).
    """
    data: bytes
    duration_seconds: Optional[float] = None
    file_size_bytes: Optional[int] = None

