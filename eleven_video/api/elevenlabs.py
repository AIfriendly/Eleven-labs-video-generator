"""
ElevenLabs API adapter for service health checking.

Implements ServiceHealth protocol for ElevenLabs API connectivity
and usage monitoring via the /v1/user/subscription endpoint.
"""
import time
from typing import Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from eleven_video.api.interfaces import HealthResult, UsageResult


class ElevenLabsAdapter:
    """Adapter for ElevenLabs API health and usage checking.
    
    Fetches subscription info from GET /v1/user/subscription
    to verify authentication and retrieve character quota.
    """
    
    BASE_URL = "https://api.elevenlabs.io"
    SUBSCRIPTION_ENDPOINT = "/v1/user/subscription"
    
    def __init__(self, api_key: str):
        """Initialize the adapter with API key.
        
        Args:
            api_key: ElevenLabs API key for authentication.
            
        Raises:
            ValueError: If api_key is None or empty.
        """
        if not api_key:
            raise ValueError("API key is required for ElevenLabsAdapter")
        
        self._api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def service_name(self) -> str:
        """Human-readable service name."""
        return "ElevenLabs"
    
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
    
    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
