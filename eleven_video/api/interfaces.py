"""
API interfaces and protocols for service health checking.

This module defines the ServiceHealth protocol and related dataclasses
for consistent API status checking across different service adapters.
"""
from dataclasses import dataclass
from typing import Protocol, runtime_checkable, Optional, Any, Callable, TYPE_CHECKING, List
from pathlib import Path

if TYPE_CHECKING:
    from eleven_video.models.domain import Script, Audio, Image, Video


@dataclass
class HealthResult:
    """Result of a service health check.
    
    Attributes:
        status: "ok" for healthy, "error" for failure
        message: Human-readable status description
        latency_ms: Response time in milliseconds, None if failed
    """
    status: str  # "ok" | "error"
    message: str
    latency_ms: Optional[float]


@dataclass
class UsageResult:
    """Result of a usage/quota query.
    
    Attributes:
        available: Whether usage data is available from this API
        used: Amount of quota used (None if unavailable)
        limit: Total quota limit (None if unavailable)
        unit: Unit of measurement (e.g., "characters", "tokens")
        raw_data: Raw response data for additional details
    """
    available: bool
    used: Optional[int]
    limit: Optional[int]
    unit: Optional[str]
    raw_data: Optional[dict[str, Any]]


@runtime_checkable
class ServiceHealth(Protocol):
    """Protocol for API service health checking.
    
    All API adapters must implement this protocol to provide
    consistent health checking and usage monitoring.
    """
    
    @property
    def service_name(self) -> str:
        """Human-readable service name for display."""
        ...
    
    async def check_health(self) -> HealthResult:
        """Check service connectivity and authentication.
        
        Returns:
            HealthResult with status, message, and latency.
        """
        ...
    
    async def get_usage(self) -> UsageResult:
        """Get current usage/quota information.
        
        Returns:
            UsageResult with quota details or unavailable status.
        """
        ...


@runtime_checkable
class ScriptGenerator(Protocol):
    """Protocol for script generation from prompts.
    
    Implementations must generate coherent scripts from text prompts
    using an AI service (e.g., Google Gemini).
    """
    
    def generate_script(
        self, 
        prompt: str, 
        progress_callback: "Optional[Callable[[str], None]]" = None
    ) -> "Script":
        """Generate a video script from a text prompt.
        
        Args:
            prompt: The text prompt describing the desired video.
            progress_callback: Optional callback for progress updates.
            
        Returns:
            Script domain model with generated content.
            
        Raises:
            ValidationError: If prompt is empty or invalid.
            GeminiAPIError: If API call fails.
        """
        ...


@runtime_checkable
class SpeechGenerator(Protocol):
    """Protocol for text-to-speech generation (Story 2.2).
    
    Implementations must convert text to audio using a TTS service
    (e.g., ElevenLabs).
    """
    
    def generate_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        progress_callback: "Optional[Callable[[str], None]]" = None
    ) -> "Audio":
        """Generate audio from text using TTS API.
        
        Args:
            text: The script text to convert to speech.
            voice_id: Optional voice ID (uses default if not provided).
            progress_callback: Optional callback for progress updates.
            
        Returns:
            Audio domain model with generated audio bytes.
            
        Raises:
            ValidationError: If text is empty or invalid.
            ElevenLabsAPIError: If API call fails.
        """
        ...


@runtime_checkable
class ImageGenerator(Protocol):
    """Protocol for image generation from script (Story 2.3).
    
    Implementations must generate images from script content using
    an AI image generation service (e.g., Google Gemini Nano Banana).
    """
    
    def generate_images(
        self,
        script: "Script",
        progress_callback: "Optional[Callable[[str], None]]" = None
    ) -> "List[Image]":
        """Generate images from script content.
        
        Args:
            script: The Script domain model to generate images for.
            progress_callback: Optional callback with format "Generating image X of Y".
            
        Returns:
            List of Image domain models with bytes and metadata.
            
        Raises:
            ValidationError: If script is empty or invalid.
            GeminiAPIError: If API call fails.
        """
        ...


@runtime_checkable
class VideoCompiler(Protocol):
    """Protocol for video compilation from assets (Story 2.4).
    
    Implementations must compile images and audio into a synchronized
    video file using FFmpeg or similar technology.
    """
    
    def compile_video(
        self,
        images: "List[Image]",
        audio: "Audio",
        output_path: Path,
        progress_callback: "Optional[Callable[[str], None]]" = None
    ) -> "Video":
        """Compile images and audio into synchronized video.
        
        Args:
            images: List of Image domain models to include in video.
            audio: Audio domain model for the video soundtrack.
            output_path: Path where the MP4 video will be saved.
            progress_callback: Optional callback with format "Processing image X of Y".
            
        Returns:
            Video domain model with file path, duration, and size.
            
        Raises:
            ValidationError: If images or audio are empty/invalid.
            VideoProcessingError: If FFmpeg fails or disk errors occur.
        """
        ...


