"""
Tests for ElevenLabs API adapter.

Test IDs: 1.5-UNIT-012 to 1.5-UNIT-022
Tests cover ServiceHealth protocol implementation, health checks, and usage retrieval.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx


class TestElevenLabsAdapter:
    """Tests for ElevenLabsAdapter class."""

    def test_adapter_can_be_imported(self):
        """[1.5-UNIT-012] Adapter should be importable from elevenlabs module."""
        # Given: The elevenlabs module exists
        # When: ElevenLabsAdapter is imported
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        # Then: It should not be None
        assert ElevenLabsAdapter is not None

    def test_adapter_implements_service_health(self):
        """[1.5-UNIT-013] AC1: Adapter must implement ServiceHealth protocol."""
        # Given: The ServiceHealth protocol is defined
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        from eleven_video.api.interfaces import ServiceHealth
        
        # When: Creating an adapter instance
        adapter = ElevenLabsAdapter(api_key="test-key")
        
        # Then: It should have all required protocol methods
        assert hasattr(adapter, 'check_health')
        assert hasattr(adapter, 'get_usage')
        assert hasattr(adapter, 'service_name')

    def test_adapter_has_correct_service_name(self):
        """[1.5-UNIT-014] Adapter service_name should be 'ElevenLabs'."""
        # Given: An ElevenLabs adapter
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        adapter = ElevenLabsAdapter(api_key="test-key")
        
        # When: Accessing service_name
        # Then: It should be 'ElevenLabs'
        assert adapter.service_name == "ElevenLabs"

    def test_adapter_requires_api_key(self):
        """[1.5-UNIT-015] Adapter should require API key."""
        # Given: No API key provided
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        
        # When: Creating adapter with None key
        # Then: Should raise TypeError or ValueError
        with pytest.raises((TypeError, ValueError)):
            ElevenLabsAdapter(api_key=None)


class TestElevenLabsCheckHealth:
    """Tests for check_health method."""

    @pytest.mark.asyncio
    async def test_check_health_success(self):
        """[1.5-UNIT-016] AC1: check_health returns ok status on success."""
        # Given: A valid API key and successful API response
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        from eleven_video.api.interfaces import HealthResult

        adapter = ElevenLabsAdapter(api_key="valid-key")
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"character_count": 1000}
        
        # When: check_health is called with mocked successful response
        with patch.object(adapter, '_fetch_subscription', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_response
            result = await adapter.check_health()
        
        # Then: Status should be ok with latency
        assert isinstance(result, HealthResult)
        assert result.status == "ok"
        assert result.latency_ms is not None

    @pytest.mark.asyncio
    async def test_check_health_auth_failure(self):
        """[1.5-UNIT-017] AC3: check_health returns error on auth failure."""
        # Given: An invalid API key
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        from eleven_video.api.interfaces import HealthResult

        adapter = ElevenLabsAdapter(api_key="invalid-key")
        
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        # When: check_health encounters 401 response
        with patch.object(adapter, '_fetch_subscription', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_response
            result = await adapter.check_health()
        
        # Then: Status should be error with 401 in message
        assert isinstance(result, HealthResult)
        assert result.status == "error"
        assert "401" in result.message

    @pytest.mark.asyncio
    async def test_check_health_connection_failure(self):
        """[1.5-UNIT-018] AC3: check_health returns error on connection failure."""
        # Given: A network failure scenario
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        from eleven_video.api.interfaces import HealthResult

        adapter = ElevenLabsAdapter(api_key="valid-key")
        
        # When: Connection error occurs
        with patch.object(adapter, '_fetch_subscription', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = httpx.ConnectError("Connection refused")
            result = await adapter.check_health()
        
        # Then: Status should be error with connection message
        assert isinstance(result, HealthResult)
        assert result.status == "error"
        assert "connect" in result.message.lower()


class TestElevenLabsGetUsage:
    """Tests for get_usage method."""

    @pytest.mark.asyncio
    async def test_get_usage_returns_quota(self):
        """[1.5-UNIT-019] AC2: get_usage returns character quota."""
        # Given: A successful subscription API response
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        from eleven_video.api.interfaces import UsageResult

        adapter = ElevenLabsAdapter(api_key="valid-key")
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "character_count": 2500,
            "character_limit": 10000,
            "tier": "creator"
        }
        
        # When: get_usage is called
        with patch.object(adapter, '_fetch_subscription', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_response
            result = await adapter.get_usage()
        
        # Then: Usage data should be available with correct values
        assert isinstance(result, UsageResult)
        assert result.available is True
        assert result.used == 2500
        assert result.limit == 10000
        assert result.unit == "characters"

    @pytest.mark.asyncio
    async def test_get_usage_on_error(self):
        """[1.5-UNIT-020] AC3: get_usage handles API errors gracefully."""
        # Given: An API error scenario
        from eleven_video.api.elevenlabs import ElevenLabsAdapter
        from eleven_video.api.interfaces import UsageResult

        adapter = ElevenLabsAdapter(api_key="invalid-key")
        
        # When: API returns an error
        with patch.object(adapter, '_fetch_subscription', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = httpx.HTTPStatusError(
                "Error", request=MagicMock(), response=MagicMock(status_code=401)
            )
            result = await adapter.get_usage()
        
        # Then: Usage should be unavailable
        assert isinstance(result, UsageResult)
        assert result.available is False
