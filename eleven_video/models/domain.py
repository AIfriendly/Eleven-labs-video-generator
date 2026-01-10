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


@dataclass
class VoiceInfo:
    """Voice model information from ElevenLabs API (Story 3.1 - AC4).
    
    Attributes:
        voice_id: Unique identifier for the voice model.
        name: Human-readable name of the voice.
        category: Optional category (e.g., "premade", "cloned").
        preview_url: Optional URL to preview audio sample.
    """
    voice_id: str
    name: str
    category: Optional[str] = None
    preview_url: Optional[str] = None


@dataclass
class ImageModelInfo:
    """Image model information from Gemini API (Story 3.2 - AC4).
    
    Attributes:
        model_id: Unique identifier for the image model (e.g., "gemini-2.5-flash-image").
        name: Human-readable display name of the model.
        description: Optional description of the model's capabilities.
        supports_image_generation: Whether the model supports image generation.
    """
    model_id: str
    name: str
    description: Optional[str] = None
    supports_image_generation: bool = True


@dataclass
class GeminiModelInfo:
    """Gemini text model information (Story 3.5 - FR19).
    
    Attributes:
        model_id: Unique identifier for the model (e.g., "gemini-2.5-flash").
        name: Human-readable display name of the model.
        description: Optional description of the model's capabilities.
        supports_text_generation: Whether the model supports text generation.
    """
    model_id: str
    name: str
    description: Optional[str] = None
    supports_text_generation: bool = True


class VideoDuration(Enum):
    """Predefined video duration options."""
    SHORT = 3     # 3 minutes
    STANDARD = 5    # 5 minutes (default)
    EXTENDED = 10    # 10 minutes


@dataclass
class DurationOption:
    """Video duration option for user selection.
    
    Attributes:
        minutes: Duration in minutes.
        label: Human-readable label (e.g., "Short", "Standard").
        description: Optional description for UI display.
    """
    minutes: int
    label: str
    description: str = ""
    
    @property
    def estimated_word_count(self) -> int:
        """Estimate word count for this duration (150 words/minute)."""
        return self.minutes * 150
    
    @property
    def estimated_image_count(self) -> int:
        """Estimate image count for this duration (15-20 images/minute, using 15)."""
        return self.minutes * 15


# Predefined duration options
DURATION_OPTIONS: list[DurationOption] = [
    DurationOption(minutes=3, label="Short", description="~3 minute video"),
    DurationOption(minutes=5, label="Standard", description="~5 minutes (recommended)"),
    DurationOption(minutes=10, label="Extended", description="~10 minutes"),
]

DEFAULT_DURATION_MINUTES = 5


class Resolution(Enum):
    """Video resolution options (Story 3.8)."""
    HD_1080P = {"width": 1920, "height": 1080, "label": "1080p (Landscape)"}
    HD_720P = {"width": 1280, "height": 720, "label": "720p (Landscape)"}
    PORTRAIT = {"width": 1080, "height": 1920, "label": "Portrait (9:16)"}
    SQUARE = {"width": 1080, "height": 1080, "label": "Square (1:1)"}
