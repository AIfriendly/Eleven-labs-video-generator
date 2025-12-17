"""
Google Gemini API adapter for service health checking and script generation.

Implements ServiceHealth, ScriptGenerator, and ImageGenerator protocols.
Uses GET /v1beta/models?page_size=1 for lightweight auth check.
Uses google-genai SDK for content generation (text + images).
Note: Gemini does not expose quota information via API.
"""
import time
from typing import Optional, Callable, Union, List

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from google import genai

from eleven_video.api.interfaces import HealthResult, UsageResult
from eleven_video.models.domain import Script, Image
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
    DEFAULT_MODEL = "gemini-2.5-flash-lite"
    
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
        
        self._http_client: Optional[httpx.AsyncClient] = None
        
        # Initialize the SDK client (new google-genai SDK pattern)
        self._genai_client = genai.Client(api_key=self._api_key)
    
    @property
    def service_name(self) -> str:
        """Human-readable service name."""
        return "Google Gemini"
    
    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client for health checks."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                timeout=10.0
            )
        return self._http_client
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException, httpx.RemoteProtocolError))
    )
    async def _fetch_models(self) -> httpx.Response:
        """Fetch models list with retry logic (lightweight auth check)."""
        http_client = await self._get_http_client()
        response = await http_client.get(
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
        Uses new google-genai SDK client.models.generate_content pattern.
        """
        response = self._genai_client.models.generate_content(
            model=self.DEFAULT_MODEL,
            contents=prompt
        )
        # Extract text from new SDK response structure
        return Script(content=response.candidates[0].content.parts[0].text)
    
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
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()

    # =========================================================================
    # Image Generation (Story 2.3)
    # =========================================================================
    
    IMAGE_MODEL = "gemini-2.5-flash-image"  # Nano Banana model for image generation
    STYLE_SUFFIX = ", photorealistic, cinematic composition, 16:9 aspect ratio, high quality"
    
    def generate_images(
        self,
        script: Script,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> List[Image]:
        """Generate images from script content using Gemini Nano Banana.
        
        Args:
            script: The Script domain model to generate images for.
            progress_callback: Optional callback with format "Generating image X of Y".
            
        Returns:
            List of Image domain models with bytes and metadata.
            
        Raises:
            ValidationError: If script is empty or invalid.
            GeminiAPIError: If API call fails.
        """
        # AC4: Validate script before API call
        if script is None:
            raise ValidationError("Script cannot be None")
        if not script.content or not script.content.strip():
            raise ValidationError("Script content cannot be empty or whitespace-only")
        
        # Segment script into image prompts
        segments = self._segment_script(script.content)
        
        if not segments:
            raise ValidationError("Could not extract any image-generating content from script")
        
        images: List[Image] = []
        total_images = len(segments)
        
        for i, segment in enumerate(segments, start=1):
            # AC3: Progress callback
            if progress_callback:
                progress_callback(f"Generating image {i} of {total_images}")
            
            try:
                image = self._generate_image_with_retry(segment)
                images.append(image)
            except TimeoutError:
                raise GeminiAPIError("Request timed out. Please check your connection and try again.")
            except Exception as e:
                error_msg = self._format_error(e)
                raise GeminiAPIError(error_msg)
        
        if progress_callback:
            progress_callback(f"Generated {len(images)} images successfully")
        
        return images
    
    def _segment_script(self, content: str) -> List[str]:
        """Split script into segments for image generation (Task 5).
        
        Splits by paragraphs first, then by major sentences if needed.
        Each segment becomes a prompt with style suffix appended.
        
        Args:
            content: Raw script text content.
            
        Returns:
            List of image prompts with style suffix.
        """
        # Split by double newlines (paragraphs)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        if not paragraphs:
            # Fall back to single newlines
            paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        
        if not paragraphs:
            # Last resort: treat entire content as one segment
            paragraphs = [content.strip()]
        
        # Create image prompts with style suffix
        prompts = []
        for paragraph in paragraphs:
            # Take first sentence or full paragraph if short
            if len(paragraph) > 200:
                # Split long paragraphs by sentence
                sentences = paragraph.replace('!', '.').replace('?', '.').split('.')
                for sentence in sentences:
                    if sentence.strip() and len(sentence.strip()) > 10:
                        prompts.append(sentence.strip() + self.STYLE_SUFFIX)
                        break  # Only take first substantial sentence
            else:
                prompts.append(paragraph + self.STYLE_SUFFIX)
        
        return prompts
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True
    )
    def _generate_image_with_retry(self, prompt: str) -> Image:
        """Generate a single image with retry logic (Task 6).
        
        Args:
            prompt: The image generation prompt with style suffix.
            
        Returns:
            Image domain model with bytes and metadata.
        """
        response = self._genai_client.models.generate_content(
            model=self.IMAGE_MODEL,
            contents=prompt
        )
        
        # Parse response to extract image data
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data is not None:
                image_bytes = part.inline_data.data
                mime_type = getattr(part.inline_data, 'mime_type', 'image/png')
                return Image(
                    data=image_bytes,
                    mime_type=mime_type,
                    file_size_bytes=len(image_bytes)
                )
        
        # If no image data found, raise error
        raise GeminiAPIError("No image data returned from Gemini API")
