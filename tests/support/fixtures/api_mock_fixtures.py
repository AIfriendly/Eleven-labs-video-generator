import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_elevenlabs_quota(mocker):
    """Mocks the ElevenLabs subscription API response."""
    mock_sub = MagicMock()
    mock_sub.character_count = 1000
    mock_sub.character_limit = 10000
    mock_sub.next_character_count_reset_unix = 1735689600
    
    # Assuming we patch where it is used or inject client
    # This might need adjustment based on how the adapter is actually instantiated
    # For now, it provides the mock data object
    return mock_sub

@pytest.fixture
def mock_gemini_quota(mocker):
    """Mocks Gemini quota info."""
    # Since Gemini quota is inferred, this might just mock empty/fallback behavior
    return None
