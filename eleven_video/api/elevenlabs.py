"""
ElevenLabs API adapter for service health checking and TTS generation.

Implements ServiceHealth and SpeechGenerator protocols.
Uses httpx for health/usage checks, elevenlabs SDK for TTS generation.
"""
import time
from typing import Optional, Callable, Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from elevenlabs import ElevenLabs

from eleven_video.api.interfaces import HealthResult, UsageResult
from eleven_video.models.domain import Audio
from eleven_video.exceptions.custom_errors import ElevenLabsAPIError, ValidationError


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
    
    def generate_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Audio:
        """Generate audio from text using ElevenLabs TTS API.
        
        Args:
            text: The script text to convert to speech.
            voice_id: Optional voice ID (uses Rachel default if not provided).
            progress_callback: Optional callback for progress updates.
            
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
        
        # AC3/FR23: Progress indicator
        if progress_callback:
            progress_callback("Generating audio...")
        
        try:
            # Use internal method with retry for actual API call
            result = self._generate_with_retry(
                text=text,
                voice_id=voice_id or self.DEFAULT_VOICE_ID
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
        
        # AC6: Return Audio with file size for downstream processing
        # NOTE: duration_seconds requires mp3 parsing (e.g., mutagen library).
        # This can be added in a future story if needed for video timing calculations.
        return Audio(
            data=audio_bytes,
            duration_seconds=None,
            file_size_bytes=len(audio_bytes)
        )
    
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
    
    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

