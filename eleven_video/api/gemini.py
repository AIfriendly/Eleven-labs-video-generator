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
from eleven_video.models.domain import Script, Image, ImageModelInfo, GeminiModelInfo
from eleven_video.exceptions.custom_errors import GeminiAPIError, ValidationError
from eleven_video.monitoring.usage import UsageMonitor


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
        
        # Image model cache (Story 3.2 - Task 2.4)
        self._image_model_cache: Optional[tuple[List[ImageModelInfo], float]] = None
        self._image_model_cache_ttl: int = 60  # 60 seconds TTL
        
        # Text model cache (Story 3.5 - Task 2)
        self._text_model_cache: Optional[tuple[List[GeminiModelInfo], float]] = None
        self._text_model_cache_ttl: int = 60  # 60 seconds TTL
    
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
    
    async def get_quota_info(self) -> "QuotaInfo":
        """Get Gemini quota information (Story 5.4 - AC #2).
        
        Note: Gemini API does not expose actual usage quotas.
        Returns static tier limits for display with session-only usage.
        Falls back gracefully to "Unknown/Standard Limit" if unavailable.
        
        For gemini-2.5-flash Free Tier:
        - 15 RPM (requests per minute)
        - 1,000,000 TPM (tokens per minute)
        
        Returns:
            QuotaInfo with tier limits or unavailable state.
        """
        from eleven_video.models.quota import QuotaInfo
        
        # AC #2: Gemini quotas are opaque - return static tier limits
        # These are the Free Tier limits for gemini-2.5-flash
        return QuotaInfo(
            service="Gemini",
            used=None,  # Session tracking via UsageMonitor if available
            limit=15,   # RPM limit for free tier
            unit="rpm",
            reset_date=None
        )
    
    def generate_script(
        self,
        prompt: str,
        progress_callback: Optional[Callable[[str], None]] = None,
        model_id: Optional[str] = None,
        warning_callback: Optional[Callable[[str], None]] = None,
        duration_minutes: Optional[int] = None,
    ) -> Script:
        """Generate a video script from a text prompt using Gemini.
        
        Args:
            prompt: The text prompt describing the desired video.
            progress_callback: Optional callback for progress updates.
            model_id: Optional Gemini model ID (uses default if not provided).
            warning_callback: Optional callback for warnings (e.g., invalid model fallback).
            
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

        # Story 3.6: Build duration-aware prompt
        if duration_minutes:
            word_count = duration_minutes * 150  # 150 words/minute estimate
            duration_instruction = (
                f"\n\nGenerate a script for approximately a {duration_minutes}-minute video. "
                f"Target around {word_count} words. Structure the content with clear sections "
                f"suitable for visual accompaniment."
            )
            prompt = prompt + duration_instruction
        
        # Story 3.5: Validate model_id and fallback if invalid
        effective_model_id = self.DEFAULT_MODEL
        if model_id:
            if self.validate_text_model_id(model_id):
                effective_model_id = model_id
            else:
                # Invalid model ID - fallback to default with warning
                if warning_callback:
                    warning_callback(
                        f"Invalid Gemini model ID '{model_id}'. "
                        f"Falling back to default model '{self.DEFAULT_MODEL}'."
                    )
        
        # AC3/FR23: Progress indicator
        if progress_callback:
            progress_callback("Generating script...")
        
        try:
            # Use internal method with retry for actual API call
            result = self._generate_with_retry(prompt, effective_model_id)
            
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
    def _generate_with_retry(self, prompt: str, model_id: Optional[str] = None) -> Script:
        """Internal method with retry logic for API calls.
        
        Args:
            prompt: The text prompt.
            model_id: Optional model ID (uses DEFAULT_MODEL if not provided).
            
        Retries on transient connection/timeout errors.
        Uses new google-genai SDK client.models.generate_content pattern.
        """
        effective_model = model_id or self.DEFAULT_MODEL
        response = self._genai_client.models.generate_content(
            model=effective_model,
            contents=prompt
        )
        
        # Story 5.1: Extract and report usage metadata (AC4)
        self._report_text_usage(response, effective_model)
        
        # Extract text from new SDK response structure
        # Defensive parsing (Code Review Fix)
        if not response.candidates:
            raise GeminiAPIError("Gemini API (Text) returned no candidates.")
            
        candidate = response.candidates[0]
        if not candidate.content or not candidate.content.parts:
            # Check finish reason to see if it was blocked
            finish_reason = getattr(candidate, 'finish_reason', 'UNKNOWN')
            raise GeminiAPIError(f"Gemini API (Text) returned empty content. FinishReason: {finish_reason}")
            
        return Script(content=candidate.content.parts[0].text)
    
    def _report_text_usage(self, response, model_id: str) -> None:
        """Extract and report usage metadata to UsageMonitor (Story 5.1).
        
        Defensive parsing: handles missing/changed usage_metadata schema.
        
        Args:
            response: The generate_content API response.
            model_id: The model used for generation.
        """
        try:
            usage_metadata = getattr(response, 'usage_metadata', None)
            if usage_metadata is None:
                return
            
            monitor = UsageMonitor.get_instance()
            
            # Extract prompt tokens (input)
            prompt_tokens = getattr(usage_metadata, 'prompt_token_count', None)
            if prompt_tokens is not None and prompt_tokens > 0:
                monitor.track_usage(
                    service="gemini",
                    model_id=model_id,
                    metric_type="input_tokens",
                    value=prompt_tokens
                )
            
            # Extract candidate tokens (output)
            candidate_tokens = getattr(usage_metadata, 'candidates_token_count', None)
            if candidate_tokens is not None and candidate_tokens > 0:
                monitor.track_usage(
                    service="gemini",
                    model_id=model_id,
                    metric_type="output_tokens",
                    value=candidate_tokens
                )
        except Exception as e:
            # Risk R-003: Defensive parsing - never crash on usage extraction
            # But log for debugging (Code Review Fix - Issue #7)
            import logging
            logging.getLogger(__name__).debug(f"Failed to extract usage metadata: {e}")
    
    def _report_image_usage(self, model_id: str) -> None:
        """Report image generation to UsageMonitor (Story 5.2 - Code Review Fix).
        
        Args:
            model_id: The image model used for generation.
        """
        try:
            monitor = UsageMonitor.get_instance()
            monitor.track_usage(
                service="gemini",
                model_id=model_id,
                metric_type="images",
                value=1
            )
        except Exception as e:
            # Defensive: never crash on usage tracking failure
            import logging
            logging.getLogger(__name__).debug(f"Failed to report image usage: {e}")
    
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
    # Image Generation (Story 2.3, updated Story 3.2)
    # =========================================================================
    
    IMAGE_MODEL = "gemini-2.5-flash-image"  # Verified via list_image_models() query
    STYLE_SUFFIX = ", photorealistic, cinematic composition, 16:9 aspect ratio, high quality"
    
    # =========================================================================
    # Image Model Listing (Story 3.2 - Task 2)
    # =========================================================================
    
    def list_image_models(self, use_cache: bool = False) -> List[ImageModelInfo]:
        """List available image generation models from Gemini API.
        
        Args:
            use_cache: If True, return cached models if available and not expired.
            
        Returns:
            List of ImageModelInfo domain models with model metadata.
            
        Raises:
            GeminiAPIError: If API call fails.
        """
        # Check cache if enabled
        if use_cache and self._image_model_cache:
            cached_models, cache_time = self._image_model_cache
            if time.perf_counter() - cache_time < self._image_model_cache_ttl:
                return cached_models
        
        try:
            models = self._list_image_models_with_retry()
            # Cache the results
            self._image_model_cache = (models, time.perf_counter())
            return models
        except Exception as e:
            error_msg = self._format_error(e)
            raise GeminiAPIError(error_msg)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True
    )
    def _list_image_models_with_retry(self) -> List[ImageModelInfo]:
        """Internal method with retry logic for listing image models.
        
        Filters models to only include image-capable models.
        """
        models_response = self._genai_client.models.list()
        
        image_models: List[ImageModelInfo] = []
        for model in models_response:
            # Filter for image-capable models (name contains 'image' or 'imagen')
            model_name = getattr(model, 'name', '') or ''
            display_name = getattr(model, 'display_name', model_name) or model_name
            description = getattr(model, 'description', None)
            
            # Check if model is image-capable
            is_image_capable = (
                'image' in model_name.lower() or
                'imagen' in model_name.lower()
            )
            
            if is_image_capable:
                # Extract model_id from full name (e.g., "models/gemini-2.5-flash-image" -> "gemini-2.5-flash-image")
                model_id = model_name.replace('models/', '') if model_name.startswith('models/') else model_name
                
                image_models.append(ImageModelInfo(
                    model_id=model_id,
                    name=display_name,
                    description=description,
                    supports_image_generation=True
                ))
        
        return image_models
    
    def validate_image_model_id(self, model_id: str) -> bool:
        """Validate if an image model ID exists in available models.
        
        Args:
            model_id: The image model ID to validate.
            
        Returns:
            True if the model ID exists, False otherwise.
        """
        available_models = self.list_image_models(use_cache=True)
        return any(model.model_id == model_id for model in available_models)

    # =========================================================================
    # Text Model Listing (Story 3.5 - Task 2)
    # =========================================================================
    
    def list_text_models(self, use_cache: bool = False) -> List[GeminiModelInfo]:
        """List available text generation models from Gemini API.
        
        Args:
            use_cache: If True, return cached models if available and not expired.
            
        Returns:
            List of GeminiModelInfo domain models with model metadata.
            
        Raises:
            GeminiAPIError: If API call fails.
        """
        # Check cache if enabled
        if use_cache and self._text_model_cache:
            cached_models, cache_time = self._text_model_cache
            if time.perf_counter() - cache_time < self._text_model_cache_ttl:
                return cached_models
        
        try:
            models = self._list_text_models_with_retry()
            # Cache the results
            self._text_model_cache = (models, time.perf_counter())
            return models
        except Exception as e:
            error_msg = self._format_error(e)
            raise GeminiAPIError(error_msg)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True
    )
    def _list_text_models_with_retry(self) -> List[GeminiModelInfo]:
        """Internal method with retry logic for listing text models.
        
        Filters models to only include text-generation capable models.
        Excludes image-specific models.
        """
        models_response = self._genai_client.models.list()
        
        text_models: List[GeminiModelInfo] = []
        for model in models_response:
            model_name = getattr(model, 'name', '') or ''
            display_name = getattr(model, 'display_name', model_name) or model_name
            description = getattr(model, 'description', None)
            
            # Check if model is text-generation capable
            # Include: gemini-* models that are NOT image-specific
            is_text_capable = (
                'gemini' in model_name.lower() and
                'image' not in model_name.lower() and
                'imagen' not in model_name.lower() and
                'embedding' not in model_name.lower()
            )
            
            if is_text_capable:
                # Extract model_id from full name
                model_id = model_name.replace('models/', '') if model_name.startswith('models/') else model_name
                
                text_models.append(GeminiModelInfo(
                    model_id=model_id,
                    name=display_name,
                    description=description,
                    supports_text_generation=True
                ))
        
        return text_models
    
    def validate_text_model_id(self, model_id: str) -> bool:
        """Validate if a text model ID exists in available models.
        
        Args:
            model_id: The text model ID to validate.
            
        Returns:
            True if the model ID exists, False otherwise.
        """
        available_models = self.list_text_models(use_cache=True)
        return any(model.model_id == model_id for model in available_models)
    
    def _resolve_default_image_model(self, model_id: Optional[str]) -> str:
        """Resolve the image model ID to use (Story 2.3.1 - AC2).
        
        Prioritizes:
        1. User-provided model_id (if valid)
        2. Dynamic discovery of available image models (if no ID provided)
        3. Hardcoded default fallback
        
        Args:
            model_id: Optional user-provided model ID.
            
        Returns:
            Resolved model ID.
        """
        # 1. User provided valid model
        if model_id and self.validate_image_model_id(model_id):
            return model_id
            
        # 2. Dynamic discovery (if no user model)
        # Try to find a valid image model if none specified
        if not model_id:
            try:
                available = self.list_image_models(use_cache=True)
                # Prefer models with 'gemini' and 'flash' in name (cost effective)
                for model in available:
                    if 'gemini' in model.model_id and 'flash' in model.model_id:
                        return model.model_id
                # Or just return first available
                if available:
                    return available[0].model_id
            except Exception:
                # If discovery fails, fall through to default
                pass
                
        # 3. Default fallback
        return self.IMAGE_MODEL
    
    def generate_images(
        self,
        script: Script,
        progress_callback: Optional[Callable[[str], None]] = None,
        model_id: Optional[str] = None,
        warning_callback: Optional[Callable[[str], None]] = None,
        target_image_count: Optional[int] = None,
    ) -> List[Image]:
        """Generate images from script content using Gemini image generation.
        
        Args:
            script: The Script domain model to generate images for.
            progress_callback: Optional callback with format "Generating image X of Y".
            model_id: Optional image model ID (uses default if not provided).
            warning_callback: Optional callback for warnings (e.g., invalid model fallback).
            
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
        
        # Story 2.3.1: Use helper for model resolution (AC2)
        effective_model_id = self._resolve_default_image_model(model_id)
        
        # Warning only if user specifically requested an invalid model
        if model_id and model_id != effective_model_id:
             if warning_callback:
                warning_callback(
                    f"Invalid image model ID '{model_id}'. "
                    f"Falling back to '{effective_model_id}'."
                )
        
        # Segment script into image prompts
        segments = self._segment_script(script.content)
        
        # Story 3.6: Adjust segments to match target image count
        if target_image_count is not None:
            segments = self._adjust_segment_count(segments, target_image_count)
        
        if not segments:
            raise ValidationError("Could not extract any image-generating content from script")
        
        images: List[Image] = []
        total_images = len(segments)
        
        for i, segment in enumerate(segments, start=1):
            # AC3: Progress callback
            if progress_callback:
                progress_callback(f"Generating image {i} of {total_images}")
            
            # Story 2.3.1 AC4: Retry logic for safety blocks
            max_retries = 2
            current_prompt = segment
            
            for attempt in range(max_retries + 1):
                try:
                    image = self._generate_image_with_retry(current_prompt, effective_model_id)
                    images.append(image)
                    break # Success
                except GeminiAPIError as e:
                    # Check if it's a safety/block error
                    is_safety_error = "blocked" in str(e).lower() or "safety" in str(e).lower()
                    
                    if is_safety_error and attempt < max_retries:
                        # Modify prompt and retry
                        current_prompt = segment + " (safe for work, educational, abstract representation)"
                        if warning_callback:
                            warning_callback(f"Image {i} flagged by safety filter. Retrying with modified prompt (Attempt {attempt+2}/{max_retries+1})...")
                        continue
                    
                    # If not correctable or retries exhausted, re-raise
                    if attempt == max_retries:
                         raise
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

    def _adjust_segment_count(self, segments: List[str], target: int) -> List[str]:
        """Adjust segment count to match target (Story 3.6).
        
        Args:
            segments: Current list of image prompts.
            target: Target number of images.
            
        Returns:
            Adjusted list with approximately `target` segments.
        """
        current = len(segments)
        
        if current == 0:
            return segments
            
        if current == target:
            return segments
        
        if current > target:
            # Trim: take first N segments (keeps beginning of video)
            return segments[:target]
        
        # Expand: repeat segments to fill target (cycle through)
        expanded = segments.copy()
        while len(expanded) < target:
            # Append from original list cyclically
            expanded.append(segments[len(expanded) % current])
        return expanded
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True
    )
    def _generate_image_with_retry(self, prompt: str, model_id: Optional[str] = None) -> Image:
        """Generate a single image with retry logic.
        
        Args:
            prompt: The image generation prompt.
            model_id: Optional model ID to use.
            
        Returns:
            Image domain model.
            
        Raises:
            GeminiAPIError: On generation failure or blocked content.
        """
        effective_model = model_id or self.IMAGE_MODEL
        
        from google.genai import types
        
        response = self._genai_client.models.generate_content(
            model=effective_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"]
            )
        )
        
        # Story 2.3.1 AC3: Defensive parsing
        if not response.candidates:
            raise GeminiAPIError("Gemini API returned no candidates.")
            
        candidate = response.candidates[0]
        
        # Check finish reason
        finish_reason = getattr(candidate, 'finish_reason', 'UNKNOWN')
        if finish_reason == 'SAFETY':
             raise GeminiAPIError(f"Image generation blocked by safety filters (FinishReason: {finish_reason}).")
        if finish_reason not in ('STOP', None) and finish_reason != 'SAFETY':
             # Some other stop reason, potentially problematic but we check content first
             pass

        # Check content parts
        if not candidate.content or not candidate.content.parts:
             # Even if finish_reason looks ok, empty content is an error
             raise GeminiAPIError(f"No image data returned (FinishReason: {finish_reason}). Content is empty.")

        # Parse response to extract image data
        for part in candidate.content.parts:
            if hasattr(part, 'inline_data') and part.inline_data is not None:
                image_bytes = part.inline_data.data
                mime_type = getattr(part.inline_data, 'mime_type', 'image/png')
                
                # Story 5.2: Report image generation to UsageMonitor (Code Review Fix)
                self._report_image_usage(effective_model)
                
                return Image(
                    data=image_bytes,
                    mime_type=mime_type,
                    file_size_bytes=len(image_bytes)
                )
        
        # If we got here, we have parts but no inline_data
        raise GeminiAPIError("No inline image data found in response candidates.")
