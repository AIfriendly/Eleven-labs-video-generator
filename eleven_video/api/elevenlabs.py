"""
ElevenLabs API adapter for service health checking and TTS generation.

Implements ServiceHealth and SpeechGenerator protocols.
Uses httpx for health/usage checks, elevenlabs SDK for TTS generation.
"""
import time
from datetime import datetime
from typing import Optional, Callable, Any, Tuple

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from elevenlabs import ElevenLabs

from eleven_video.api.interfaces import HealthResult, UsageResult
from eleven_video.models.domain import Audio, VoiceInfo
from eleven_video.models.quota import QuotaInfo
from eleven_video.exceptions.custom_errors import ElevenLabsAPIError, ValidationError
from eleven_video.monitoring.usage import UsageMonitor


class ElevenLabsAdapter:
    """Adapter for ElevenLabs API health checking and TTS generation.
    
    Fetches subscription info from GET /v1/user/subscription
    to verify authentication and retrieve character quota.
    Uses ElevenLabs SDK for TTS generation (Story 2.2).
    
    Can be initialized with either:
    - A Settings instance (recommended, provides SecretStr security)
    - A raw API key string (for testing/backward compatibility)
    """
    
    BASE_URL = "https://api.elevenlabs.io"
    SUBSCRIPTION_ENDPOINT = "/v1/user/subscription"
    DEFAULT_VOICE_ID = "NFG5qt843uXKj4pFvR7C"  # Adam Stone - late night radio
    DEFAULT_MODEL_ID = "eleven_multilingual_v2"
    DEFAULT_OUTPUT_FORMAT = "mp3_44100_128"
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        settings: Optional[Any] = None
    ):
        """Initialize the adapter with API key.
        
        Args:
            api_key: ElevenLabs API key for authentication (for testing).
            settings: Settings instance with elevenlabs_api_key (recommended).
            
        Raises:
            ValueError: If neither api_key nor settings is provided.
        
        Note:
            If both are provided, api_key takes precedence (for testing).
            Production code should use Settings for SecretStr security.
        """
        if api_key:
            self._api_key = api_key
        elif settings:
            self._api_key = settings.elevenlabs_api_key.get_secret_value()
        else:
            raise ValueError("Either api_key or settings is required for ElevenLabsAdapter")
        
        self._client: Optional[httpx.AsyncClient] = None
        self._sdk_client: Optional[ElevenLabs] = None
        # Voice cache: (voices_list, cache_timestamp)
        self._voice_cache: Optional[Tuple[list[VoiceInfo], float]] = None
        self._voice_cache_ttl: float = 60.0  # 60 second TTL
    
    @property
    def service_name(self) -> str:
        """Human-readable service name."""
        return "ElevenLabs"
    
    def _get_sdk_client(self) -> ElevenLabs:
        """Get or create the ElevenLabs SDK client."""
        if self._sdk_client is None:
            self._sdk_client = ElevenLabs(api_key=self._api_key)
        return self._sdk_client
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers={"xi-api-key": self._api_key},
                timeout=10.0
            )
        return self._client
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException, httpx.RemoteProtocolError))
    )
    async def _fetch_subscription(self) -> httpx.Response:
        """Fetch subscription data with retry logic."""
        client = await self._get_client()
        response = await client.get(self.SUBSCRIPTION_ENDPOINT)
        return response
    
    async def check_health(self) -> HealthResult:
        """Check ElevenLabs API connectivity and authentication.
        
        Returns:
            HealthResult with status, message, and latency.
        """
        start_time = time.perf_counter()
        
        try:
            response = await self._fetch_subscription()
            latency_ms = (time.perf_counter() - start_time) * 1000
            
            if response.status_code == 200:
                return HealthResult(
                    status="ok",
                    message="Connected successfully",
                    latency_ms=round(latency_ms, 2)
                )
            elif response.status_code == 401:
                return HealthResult(
                    status="error",
                    message="Authentication failed (401): Invalid API key",
                    latency_ms=round(latency_ms, 2)
                )
            else:
                return HealthResult(
                    status="error",
                    message=f"HTTP {response.status_code}: {response.text[:100]}",
                    latency_ms=round(latency_ms, 2)
                )
        except httpx.ConnectError as e:
            return HealthResult(
                status="error",
                message=f"Connection failed: {str(e)}",
                latency_ms=None
            )
        except httpx.TimeoutException:
            return HealthResult(
                status="error",
                message="Connection timed out",
                latency_ms=None
            )
        except Exception as e:
            return HealthResult(
                status="error",
                message=f"Unexpected error: {str(e)}",
                latency_ms=None
            )
    
    async def get_usage(self) -> UsageResult:
        """Get ElevenLabs character usage quota.
        
        Returns:
            UsageResult with character count and limit.
        """
        try:
            response = await self._fetch_subscription()
            
            if response.status_code != 200:
                return UsageResult(
                    available=False,
                    used=None,
                    limit=None,
                    unit=None,
                    raw_data=None
                )
            
            data = response.json()
            return UsageResult(
                available=True,
                used=data.get("character_count", 0),
                limit=data.get("character_limit", 0),
                unit="characters",
                raw_data=data
            )
        except Exception:
            return UsageResult(
                available=False,
                used=None,
                limit=None,
                unit=None,
                raw_data=None
            )
    
    async def get_quota_info(self) -> QuotaInfo:
        """Get ElevenLabs character quota information (Story 5.4 - AC #1, #4).
        
        Uses HTTP client to fetch subscription data (same as get_usage).
        Returns QuotaInfo with unavailable state on any error.
        
        Returns:
            QuotaInfo with service quota details or unavailable state.
        """
        try:
            # Use HTTP client for consistency with get_usage (which works correctly)
            response = await self._fetch_subscription()
            
            if response.status_code != 200:
                import logging
                logging.getLogger(__name__).debug(
                    f"Failed to fetch ElevenLabs quota: HTTP {response.status_code}"
                )
                return QuotaInfo(
                    service="ElevenLabs",
                    used=None,
                    limit=None,
                    unit="chars",
                    reset_date=None
                )
            
            data = response.json()
            
            # Extract reset date if available
            reset_date = None
            reset_unix = data.get('next_character_count_reset_unix')
            if reset_unix:
                reset_date = datetime.fromtimestamp(reset_unix)
            
            return QuotaInfo(
                service="ElevenLabs",
                used=data.get("character_count"),
                limit=data.get("character_limit"),
                unit="chars",
                reset_date=reset_date
            )
        except Exception as e:
            # AC #4: Fail gracefully - return unavailable state
            import logging
            logging.getLogger(__name__).debug(f"Failed to fetch ElevenLabs quota: {e}")
            return QuotaInfo(
                service="ElevenLabs",
                used=None,
                limit=None,
                unit="chars",
                reset_date=None
            )
    
    def generate_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None,
        warning_callback: Optional[Callable[[str], None]] = None
    ) -> Audio:
        """Generate audio from text using ElevenLabs TTS API.
        
        Args:
            text: The script text to convert to speech.
            voice_id: Optional voice ID (uses default if not provided).
            progress_callback: Optional callback for progress updates.
            warning_callback: Optional callback for warnings (e.g., invalid voice fallback).
            
        Returns:
            Audio domain model with generated audio bytes.
            
        Raises:
            ValidationError: If text is empty or invalid.
            ElevenLabsAPIError: If API call fails.
        """
        # AC4: Validate text before API call
        if text is None:
            raise ValidationError("Text cannot be None")
        if not isinstance(text, str):
            raise ValidationError("Text must be a string")
        if not text.strip():
            raise ValidationError("Text cannot be empty or whitespace-only")
        
        # Story 3.1 AC3: Validate voice_id and fallback if invalid
        effective_voice_id = self.DEFAULT_VOICE_ID
        if voice_id:
            if self.validate_voice_id(voice_id):
                effective_voice_id = voice_id
            else:
                # Fallback to default with warning
                if warning_callback:
                    warning_callback(
                        f"Invalid voice ID '{voice_id}' - falling back to default voice"
                    )
                effective_voice_id = self.DEFAULT_VOICE_ID
        
        # AC3/FR23: Progress indicator
        if progress_callback:
            progress_callback("Generating audio...")
        
        try:
            # Use internal method with retry for actual API call
            result = self._generate_with_retry(
                text=text,
                voice_id=effective_voice_id
            )
            
            if progress_callback:
                progress_callback("Audio generation complete")
            
            return result
            
        except TimeoutError:
            # AC5: Timeout error
            raise ElevenLabsAPIError("Request timed out. Please check your connection and try again.")
        except Exception as e:
            # AC5: Error handling with user-friendly messages
            # AC2: Never expose API key in error messages
            error_msg = self._format_error(e)
            raise ElevenLabsAPIError(error_msg)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((
            ConnectionError, 
            TimeoutError,
            httpx.ConnectError,
            httpx.TimeoutException,
            httpx.RemoteProtocolError,
        )),
        reraise=True
    )
    def _generate_with_retry(self, text: str, voice_id: str) -> Audio:
        """Internal method with retry logic for TTS API calls.
        
        Retries on transient connection/timeout errors.
        """
        client = self._get_sdk_client()
        
        # SDK returns an iterator of bytes
        audio_iterator = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id=self.DEFAULT_MODEL_ID,
            output_format=self.DEFAULT_OUTPUT_FORMAT
        )
        
        # Collect all bytes from iterator
        audio_bytes = b"".join(audio_iterator)
        
        # Story 5.1/5.2: Report character usage to monitor (AC5 / Story 5.2 AC4)
        self._report_character_usage(text, voice_id)
        
        # AC6: Return Audio with file size for downstream processing
        # NOTE: duration_seconds requires mp3 parsing (e.g., mutagen library).
        # This can be added in a future story if needed for video timing calculations.
        return Audio(
            data=audio_bytes,
            duration_seconds=None,
            file_size_bytes=len(audio_bytes)
        )
    
    def _report_character_usage(self, text: str, voice_id: str) -> None:
        """Report character usage to UsageMonitor (Story 5.1 AC5, Story 5.2 AC4).
        
        Args:
            text: The text that was converted to speech.
            voice_id: The voice ID used for generation (for by_model breakdown).
        """
        try:
            monitor = UsageMonitor.get_instance()
            # Story 5.2 AC4: Use voice_id as model_id for per-voice breakdown
            monitor.track_usage(
                service="elevenlabs",
                model_id=voice_id,
                metric_type="characters",
                value=len(text)
            )
        except Exception as e:
            # Never crash on usage tracking failure
            # But log for debugging (Code Review Fix - Issue #7)
            import logging
            logging.getLogger(__name__).debug(f"Failed to report character usage: {e}")
    
    def _format_error(self, error: Exception) -> str:
        """Format error message without exposing API key (AC2).
        
        Args:
            error: The original exception.
            
        Returns:
            User-friendly error message.
        """
        msg = str(error).lower()
        
        # Ensure API key is never in error message
        if self._api_key and self._api_key.lower() in msg:
            msg = msg.replace(self._api_key.lower(), "[REDACTED]")
        
        if "401" in msg or "unauthorized" in msg or "unauthenticated" in msg:
            return "Authentication failed. Please check your ELEVENLABS_API_KEY."
        elif "429" in msg or "rate limit" in msg or "quota" in msg:
            return "Rate limit exceeded. Please retry after a few minutes."
        elif "500" in msg or "503" in msg or "internal" in msg or "server" in msg:
            return "ElevenLabs server error. Please try again later."
        elif "timeout" in msg or "timed out" in msg:
            return "Request timed out. Please check your connection and try again."
        else:
            # Generic error - sanitize to prevent key exposure
            sanitized = str(error)
            if self._api_key and self._api_key in sanitized:
                sanitized = sanitized.replace(self._api_key, "[REDACTED]")
            return f"ElevenLabs API error: {sanitized}"
    
    def validate_voice_id(self, voice_id: str) -> bool:
        """Check if a voice ID exists in the available voices (Story 3.1 - AC3).
        
        Uses cached voice list to avoid repeated API calls (60s TTL).
        
        Args:
            voice_id: The voice ID to validate.
            
        Returns:
            True if voice exists, False otherwise.
        """
        try:
            voices = self.list_voices(use_cache=True)
            return any(v.voice_id == voice_id for v in voices)
        except ElevenLabsAPIError:
            # If we can't get the voice list, assume invalid to be safe
            return False
    
    def list_voices(self, use_cache: bool = False) -> list[VoiceInfo]:
        """Get list of available voice models (Story 3.1 - AC4).
        
        Args:
            use_cache: If True, return cached voices if available and not expired.
        
        Returns:
            List of VoiceInfo domain models with voice metadata.
            
        Raises:
            ElevenLabsAPIError: If API call fails.
        """
        # Check cache if requested
        if use_cache and self._voice_cache is not None:
            voices, cache_time = self._voice_cache
            if time.perf_counter() - cache_time < self._voice_cache_ttl:
                return voices
        
        try:
            voices = self._list_voices_with_retry()
            # Update cache
            self._voice_cache = (voices, time.perf_counter())
            return voices
            
        except Exception as e:
            error_msg = self._format_error(e)
            raise ElevenLabsAPIError(error_msg)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((
            ConnectionError,
            TimeoutError,
            httpx.ConnectError,
            httpx.TimeoutException,
            httpx.RemoteProtocolError,
        )),
        reraise=True
    )
    def _list_voices_with_retry(self) -> list[VoiceInfo]:
        """Internal method with retry logic for voice listing API calls."""
        client = self._get_sdk_client()
        response = client.voices.get_all()
        
        voices = []
        for voice in response.voices:
            voices.append(VoiceInfo(
                voice_id=voice.voice_id,
                name=voice.name,
                category=getattr(voice, 'category', None),
                preview_url=getattr(voice, 'preview_url', None)
            ))
        
        return voices
    
    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

