"""
Tests for Gemini API adapter - ServiceHealth protocol (Story 1.5).

Test IDs: 1.5-UNIT-021 to 1.5-UNIT-028
Tests cover ServiceHealth protocol implementation, health checks, and usage retrieval.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx


class TestGeminiAdapter:
    """Tests for GeminiAdapter class."""

    def test_adapter_can_be_imported(self):
        """[1.5-UNIT-021] Adapter should be importable from gemini module."""
        # Given: The gemini module exists
        # When: GeminiAdapter is imported
        from eleven_video.api.gemini import GeminiAdapter
        # Then: It should not be None
        assert GeminiAdapter is not None

    def test_adapter_implements_service_health(self):
        """[1.5-UNIT-022] AC1: Adapter must implement ServiceHealth protocol."""
        # Given: The ServiceHealth protocol is defined
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.api.interfaces import ServiceHealth
        
        # When: Creating an adapter instance
        adapter = GeminiAdapter(api_key="test-key")
        
        # Then: It should have all required protocol methods
        assert hasattr(adapter, 'check_health')
        assert hasattr(adapter, 'get_usage')
        assert hasattr(adapter, 'service_name')

    def test_adapter_has_correct_service_name(self):
        """[1.5-UNIT-023] Adapter service_name should be 'Google Gemini'."""
        # Given: A Gemini adapter
        from eleven_video.api.gemini import GeminiAdapter
        adapter = GeminiAdapter(api_key="test-key")
        
        # When: Accessing service_name
        # Then: It should be 'Google Gemini'
        assert adapter.service_name == "Google Gemini"

    def test_adapter_requires_api_key(self):
        """[1.5-UNIT-024] Adapter should require API key."""
        # Given: No API key provided
        from eleven_video.api.gemini import GeminiAdapter
        
        # When: Creating adapter with None key
        # Then: Should raise TypeError or ValueError
        with pytest.raises((TypeError, ValueError)):
            GeminiAdapter(api_key=None)


class TestGeminiCheckHealth:
    """Tests for check_health method."""

    @pytest.mark.asyncio
    async def test_check_health_success(self):
        """[1.5-UNIT-025] AC1: check_health returns ok status on success."""
        # Given: A valid API key and successful API response
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.api.interfaces import HealthResult

        adapter = GeminiAdapter(api_key="valid-key")
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": [{"name": "gemini-pro"}]}
        
        # When: check_health is called with mocked successful response
        with patch.object(adapter, '_fetch_models', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_response
            result = await adapter.check_health()
        
        # Then: Status should be ok with latency
        assert isinstance(result, HealthResult)
        assert result.status == "ok"
        assert result.latency_ms is not None

    @pytest.mark.asyncio
    async def test_check_health_auth_failure(self):
        """[1.5-UNIT-026] AC3: check_health returns error on auth failure."""
        # Given: An invalid API key
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.api.interfaces import HealthResult

        adapter = GeminiAdapter(api_key="invalid-key")
        
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        # When: check_health encounters 401 response
        with patch.object(adapter, '_fetch_models', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_response
            result = await adapter.check_health()
        
        # Then: Status should be error
        assert isinstance(result, HealthResult)
        assert result.status == "error"

    @pytest.mark.asyncio
    async def test_check_health_connection_failure(self):
        """[1.5-UNIT-027] AC3: check_health returns error on connection failure."""
        # Given: A network failure scenario
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.api.interfaces import HealthResult

        adapter = GeminiAdapter(api_key="valid-key")
        
        # When: Connection error occurs
        with patch.object(adapter, '_fetch_models', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = httpx.ConnectError("Connection refused")
            result = await adapter.check_health()
        
        # Then: Status should be error
        assert isinstance(result, HealthResult)
        assert result.status == "error"


class TestGeminiGetUsage:
    """Tests for get_usage method."""

    @pytest.mark.asyncio
    async def test_get_usage_not_available(self):
        """[1.5-UNIT-028] AC2: Gemini API does not expose quota."""
        # Given: Gemini API doesn't expose usage via API
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.api.interfaces import UsageResult

        adapter = GeminiAdapter(api_key="valid-key")
        
        # When: get_usage is called
        result = await adapter.get_usage()
        
        # Then: Usage should be unavailable
        assert isinstance(result, UsageResult)
        assert result.available is False
        assert result.used is None
        assert result.limit is None
