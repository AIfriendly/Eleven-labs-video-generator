"""Unit tests for GeminiAdapter.get_quota_info (Story 5.4 - Code Review Fix #1)."""
import pytest
from unittest.mock import MagicMock
from eleven_video.api.gemini import GeminiAdapter
from eleven_video.models.quota import QuotaInfo


@pytest.fixture
def adapter():
    """Create GeminiAdapter with fake API key for testing."""
    return GeminiAdapter(api_key="fake-key")


@pytest.mark.asyncio
async def test_get_quota_info_returns_static_limits(adapter):
    """Verifies GeminiAdapter.get_quota_info returns static tier limits.
    
    AC #2: Gemini API doesn't expose quotas - returns Free Tier RPM limit.
    """
    quota = await adapter.get_quota_info()
    
    assert isinstance(quota, QuotaInfo)
    assert quota.service == "Gemini"
    assert quota.limit == 15  # Free tier RPM
    assert quota.unit == "rpm"
    # used may be None or session-tracked value
    assert quota.is_available is True  # limit is known


@pytest.mark.asyncio
async def test_get_quota_info_is_always_available(adapter):
    """Verifies Gemini quota info never fails (static fallback).
    
    AC #4: Graceful failure - Gemini always returns static data.
    """
    # Even if called multiple times, should always succeed
    quota1 = await adapter.get_quota_info()
    quota2 = await adapter.get_quota_info()
    
    assert quota1.is_available is True
    assert quota2.is_available is True
    assert quota1.service == quota2.service
