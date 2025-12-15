"""
API module - adapters for external service integration.

Provides ServiceHealth protocol and adapters for ElevenLabs and Gemini APIs.
"""
from eleven_video.api.interfaces import ServiceHealth, HealthResult, UsageResult
from eleven_video.api.elevenlabs import ElevenLabsAdapter
from eleven_video.api.gemini import GeminiAdapter

__all__ = [
    "ServiceHealth",
    "HealthResult",
    "UsageResult",
    "ElevenLabsAdapter",
    "GeminiAdapter",
]
