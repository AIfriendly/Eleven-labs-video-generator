"""Unit tests for ElevenLabsAdapter.get_quota_info (Story 5.4).

Tests HTTP-based quota info retrieval using _fetch_subscription.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from eleven_video.api.elevenlabs import ElevenLabsAdapter


@pytest.fixture
def adapter():
    """Create ElevenLabsAdapter with fake API key for testing."""
    return ElevenLabsAdapter(api_key="fake-key")


@pytest.mark.asyncio
async def test_get_quota_info_success(adapter):
    """Verifies that get_quota_info returns a correctly populated QuotaInfo object."""
    # GIVEN: Mock HTTP response with subscription data
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "character_count": 12500,
        "character_limit": 50000,
        "next_character_count_reset_unix": 1735689600
    }
    
    # Mock the _fetch_subscription method
    adapter._fetch_subscription = AsyncMock(return_value=mock_response)
    
    # WHEN: Calling get_quota_info
    quota = await adapter.get_quota_info()
    
    # THEN: Should return populated QuotaInfo
    assert quota.service == "ElevenLabs"
    assert quota.used == 12500
    assert quota.limit == 50000
    assert quota.unit == "chars"
    assert quota.percent_used == 25.0
    assert quota.reset_date is not None


@pytest.mark.asyncio
async def test_get_quota_info_api_failure(adapter):
    """Verifies that get_quota_info returns an unavailable state on API error."""
    # GIVEN: _fetch_subscription raises an exception
    adapter._fetch_subscription = AsyncMock(side_effect=Exception("API Error"))
    
    # WHEN: Calling get_quota_info
    quota = await adapter.get_quota_info()
    
    # THEN: Should return unavailable state
    assert quota.service == "ElevenLabs"
    assert quota.limit is None
    assert quota.used is None
    assert quota.is_available is False


@pytest.mark.asyncio
async def test_get_quota_info_http_error(adapter):
    """Verifies that get_quota_info handles non-200 HTTP status gracefully."""
    # GIVEN: HTTP response with error status
    mock_response = MagicMock()
    mock_response.status_code = 401
    
    adapter._fetch_subscription = AsyncMock(return_value=mock_response)
    
    # WHEN: Calling get_quota_info
    quota = await adapter.get_quota_info()
    
    # THEN: Should return unavailable state
    assert quota.service == "ElevenLabs"
    assert quota.limit is None
    assert quota.used is None
    assert quota.is_available is False


@pytest.mark.asyncio
async def test_get_quota_info_missing_fields(adapter):
    """Verifies handling when some fields are missing from response."""
    # GIVEN: HTTP response with partial data
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "character_count": 5000,
        # character_limit is missing
    }
    
    adapter._fetch_subscription = AsyncMock(return_value=mock_response)
    
    # WHEN: Calling get_quota_info
    quota = await adapter.get_quota_info()
    
    # THEN: Should handle missing fields gracefully
    assert quota.service == "ElevenLabs"
    assert quota.used == 5000
    assert quota.limit is None  # Missing from response
    assert quota.is_available is False  # No limit = unavailable
