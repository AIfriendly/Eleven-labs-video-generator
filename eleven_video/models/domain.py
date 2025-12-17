"""Domain models for the eleven-video application."""
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class PipelineStage(Enum):
    """Video generation pipeline stages (Story 2.5).
    
    Represents the different stages of the video generation pipeline
    for progress tracking and display purposes.
    """
    INITIALIZING = "initializing"
    PROCESSING_SCRIPT = "processing_script"
    PROCESSING_AUDIO = "processing_audio"
    PROCESSING_IMAGES = "processing_images"
    COMPILING_VIDEO = "compiling_video"
    COMPLETED = "completed"
    FAILED = "failed"


# Stage icons for Rich display (Story 2.5)
STAGE_ICONS: dict[PipelineStage, str] = {
    PipelineStage.INITIALIZING: "⏳",
    PipelineStage.PROCESSING_SCRIPT: "📝",
    PipelineStage.PROCESSING_AUDIO: "🔊",
    PipelineStage.PROCESSING_IMAGES: "🖼️",
    PipelineStage.COMPILING_VIDEO: "🎬",
    PipelineStage.COMPLETED: "✅",
    PipelineStage.FAILED: "❌",
}


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


@dataclass
class Image:
    """Generated image from Gemini API (Story 2.3 - AC6).
    
    Attributes:
        data: Raw image bytes (PNG format).
        mime_type: MIME type (e.g., "image/png").
        file_size_bytes: File size in bytes for downstream processing.
    """
    data: bytes
    mime_type: str = "image/png"
    file_size_bytes: Optional[int] = None


@dataclass
class Video:
    """Compiled video output (Story 2.4 - AC7).
    
    Attributes:
        file_path: Path to the output video file.
        duration_seconds: Video duration in seconds.
        file_size_bytes: File size in bytes.
        codec: Video codec used (default h264).
        resolution: Video resolution as (width, height) tuple.
    """
    file_path: Path
    duration_seconds: float
    file_size_bytes: int
    codec: str = "h264"
    resolution: tuple = (1920, 1080)

