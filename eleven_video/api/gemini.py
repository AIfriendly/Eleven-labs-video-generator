"""
Google Gemini API adapter for service health checking and script generation.

Implements ServiceHealth and ScriptGenerator protocols.
Uses GET /v1beta/models?page_size=1 for lightweight auth check.
Uses google-generativeai SDK for script generation.
Note: Gemini does not expose quota information via API.
"""
import time
from typing import Optional, Callable, Union

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from eleven_video.api.interfaces import HealthResult, UsageResult
from eleven_video.models.domain import Script
from eleven_video.exceptions.custom_errors import GeminiAPIError, ValidationError


class GeminiAdapter:
    """Adapter for Google Gemini API health checking and script generation.
    
    Uses the models list endpoint for lightweight connectivity
    and authentication verification. Uses the SDK for content generation.
    
    Can be initialized with either:
    - A Settings instance (recommended, provides SecretStr security)
    - A raw API key string (for testing/backward compatibility)
    """
    
    BASE_URL = "https://generativelanguage.googleapis.com"
    MODELS_ENDPOINT = "/v1beta/models"
    DEFAULT_MODEL = "gemini-2.5-flash"
    
    def __init__(self, api_key: Optional[str] = None, settings: Optional["_SettingsBase"] = None):
        """Initialize the adapter with API key.
        
        Args:
            api_key: Google Gemini API key for authentication (for testing).
            settings: Settings instance with gemini_api_key (recommended).
            
        Raises:
            ValueError: If neither api_key nor settings is provided.
        
        Note:
            If both are provided, api_key takes precedence (for testing).
            Production code should use Settings for SecretStr security.
        """
        if api_key:
            self._api_key = api_key
        elif settings:
            self._api_key = settings.gemini_api_key.get_secret_value()
        else:
            raise ValueError("Either api_key or settings is required for GeminiAdapter")
        
        self._client: Optional[httpx.AsyncClient] = None
        
        # Configure the SDK (does not make network calls)
        genai.configure(api_key=self._api_key)
    
    @property
    def service_name(self) -> str:
        """Human-readable service name."""
        return "Google Gemini"
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                timeout=10.0
            )
        return self._client
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException, httpx.RemoteProtocolError))
    )
    async def _fetch_models(self) -> httpx.Response:
        """Fetch models list with retry logic (lightweight auth check)."""
        client = await self._get_client()
        response = await client.get(
            self.MODELS_ENDPOINT,
            params={"key": self._api_key, "pageSize": 1}
        )
        return response
    
    async def check_health(self) -> HealthResult:
        """Check Gemini API connectivity and authentication.
        
        Returns:
            HealthResult with status, message, and latency.
        """
        start_time = time.perf_counter()
        
        try:
            response = await self._fetch_models()
            latency_ms = (time.perf_counter() - start_time) * 1000
            
            if response.status_code == 200:
                return HealthResult(
                    status="ok",
                    message="Connected successfully",
                    latency_ms=round(latency_ms, 2)
                )
            elif response.status_code in (401, 403):
                return HealthResult(
                    status="error",
                    message=f"Authentication failed ({response.status_code}): Invalid API key",
                    latency_ms=round(latency_ms, 2)
                )
            elif response.status_code == 429:
                return HealthResult(
                    status="error",
                    message="Rate limit exceeded (429): Too many requests",
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
        """Get Gemini usage quota - not available via API.
        
        Note: Google Gemini API does not expose quota information
        through its public API. Usage must be monitored via
        Google Cloud Console.
        
        Returns:
            UsageResult with available=False.
        """
        return UsageResult(
            available=False,
            used=None,
            limit=None,
            unit=None,
            raw_data=None
        )
    
    def generate_script(
        self,
        prompt: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Script:
        """Generate a video script from a text prompt using Gemini.
        
        Args:
            prompt: The text prompt describing the desired video.
            progress_callback: Optional callback for progress updates.
            
        Returns:
            Script domain model with generated content.
            
        Raises:
            ValidationError: If prompt is empty or invalid.
            GeminiAPIError: If API call fails.
        """
        # AC4: Validate prompt before API call
        if prompt is None:
            raise ValidationError("Prompt cannot be None")
        if not isinstance(prompt, str):
            raise ValidationError("Prompt must be a string")
        if not prompt.strip():
            raise ValidationError("Prompt cannot be empty or whitespace-only")
        
        # AC3/FR23: Progress indicator
        if progress_callback:
            progress_callback("Generating script...")
        
        try:
            # Use internal method with retry for actual API call
            result = self._generate_with_retry(prompt)
            
            if progress_callback:
                progress_callback("Script generation complete")
            
            return result
            
        except TimeoutError:
            # AC5: Timeout error
            raise GeminiAPIError("Request timed out. Please check your connection and try again.")
        except Exception as e:
            # AC5: Error handling with user-friendly messages
            # AC2: Never expose API key in error messages
            error_msg = self._format_error(e)
            raise GeminiAPIError(error_msg)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True
    )
    def _generate_with_retry(self, prompt: str) -> Script:
        """Internal method with retry logic for API calls.
        
        Retries on transient connection/timeout errors.
        """
        model = genai.GenerativeModel(self.DEFAULT_MODEL)
        response = model.generate_content(prompt)
        return Script(content=response.text)
    
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
            return "Authentication failed. Please check your GEMINI_API_KEY."
        elif "429" in msg or "rate limit" in msg or "resource exhausted" in msg or "quota" in msg:
            return "Rate limit exceeded. Please retry after a few minutes."
        elif "500" in msg or "503" in msg or "internal" in msg or "server" in msg:
            return "Gemini server error. Please try again later."
        elif "timeout" in msg or "timed out" in msg:
            return "Request timed out. Please check your connection and try again."
        else:
            # Generic error - sanitize to prevent key exposure
            sanitized = str(error)
            if self._api_key and self._api_key in sanitized:
                sanitized = sanitized.replace(self._api_key, "[REDACTED]")
            return f"Gemini API error: {sanitized}"
    
    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

