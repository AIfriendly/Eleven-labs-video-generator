import pytest
from unittest.mock import MagicMock
from tests.support.factories.usage_factory import create_pricing_config

@pytest.fixture
def mock_pricing_config():
    """Returns a default pricing configuration."""
    return create_pricing_config()

@pytest.fixture
def clean_usage_monitor(monkeypatch):
    """
    Returns a fresh UsageMonitor instance for each test.
    Patches the singleton instance to ensure isolation.
    """
    # Pending implementation of the actual class
    # For now, we return a mock that mimics the expected interface
    monitor_mock = MagicMock()
    monitor_mock.track_event = MagicMock()
    monitor_mock.get_summary = MagicMock(return_value={"total_cost": 0.0})
    return monitor_mock

@pytest.fixture
def mock_usage_display():
    """Returns a mock implementation of UsageDisplay."""
    display_mock = MagicMock()
    display_mock.update = MagicMock()
    display_mock.render = MagicMock(return_value="[Panel] Live Usage")
    return display_mock
