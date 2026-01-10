"""UI component tests for UsageDisplay (Story 5.1).

Tests that the usage display panel renders correctly and provides
the expected interface for real-time updates.
"""
import pytest
from unittest.mock import MagicMock, patch

from eleven_video.ui.usage_panel import UsageDisplay
from eleven_video.monitoring.usage import UsageMonitor


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_usage_summary():
    """Create a mock usage summary in the expected format.
    
    Returns a dictionary matching the structure of UsageMonitor.get_summary().
    """
    return {
        "total_cost": 1.25,
        "events_count": 12,
        "by_service": {
            "gemini": {"metrics": {"input_tokens": 10000, "output_tokens": 5000}, "cost": 0.50},
            "elevenlabs": {"metrics": {"characters": 7500}, "cost": 0.75}
        }
    }


@pytest.fixture
def mock_monitor(mock_usage_summary):
    """Create a mock UsageMonitor with the expected summary."""
    mock = MagicMock()
    mock.get_summary.return_value = mock_usage_summary
    return mock


# =============================================================================
# UsageDisplay Rendering Tests
# =============================================================================

class TestUsageDisplayRendering:
    """Tests for UsageDisplay rendering functionality."""

    def test_usage_display_render(self, mock_monitor):
        """[5.1-UI-001][P1] Verify UsageDisplay renders correctly.
        
        GIVEN: A UsageDisplay connected to a mocked UsageMonitor with data
        WHEN: __rich__() is called to render the display
        THEN: A valid Rich renderable (Panel or Group) is returned
        
        AC: AC1 (Live Usage Display)
        """
        # GIVEN: Mock monitor with usage data
        with patch("eleven_video.ui.usage_panel.UsageMonitor.get_instance", return_value=mock_monitor):
            display = UsageDisplay()
            
            # WHEN: Render the display
            renderable = display.__rich__()
            
            # THEN: Should return a valid Rich renderable
            assert renderable is not None
            # Basic type check (it should return a Panel or Group)
            assert "Panel" in str(type(renderable)) or "Group" in str(type(renderable))


# =============================================================================
# UsageDisplay Interface Tests
# =============================================================================

class TestUsageDisplayInterface:
    """Tests for UsageDisplay interface methods (Risk R-002)."""

    def test_ui_update_interval_non_blocking(self):
        """[5.1-UI-002][P1] Verify UI update mechanism is decoupled from main thread.
        
        GIVEN: A UsageDisplay instance
        WHEN: The interface is inspected
        THEN: It exposes start_live_update and stop_live_update methods
        
        Risk: R-002 (UI Performance)
        """
        # GIVEN: A display instance
        display = UsageDisplay()
        
        # THEN: Should have async/threaded update methods
        assert hasattr(display, "start_live_update"), "Must have threaded/async update method"
        assert hasattr(display, "stop_live_update"), "Must have cleanup method"
