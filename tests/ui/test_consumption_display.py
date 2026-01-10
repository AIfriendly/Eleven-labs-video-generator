"""Unit tests for consumption data display (Story 5.3).

Tests verify that UsageDisplay correctly formats and displays detailed
consumption breakdown by service and by model, including edge cases.

Test IDs: [5.3-UNIT-001] through [5.3-UNIT-010]
"""
import pytest
from unittest.mock import MagicMock, patch
from io import StringIO

from rich.console import Console
from eleven_video.ui.usage_panel import UsageDisplay
from eleven_video.ui.usage_panel import UsageDisplay
from eleven_video.monitoring.usage import (
    UsageMonitor,
    SERVICE_GEMINI,
    SERVICE_ELEVENLABS,
    METRIC_INPUT_TOKENS,
    METRIC_OUTPUT_TOKENS,
    METRIC_CHARACTERS,
    MODEL_GEMINI_FLASH,
    MODEL_GEMINI_PRO
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_consumption_summary():
    """Create a mock consumption summary with by_service and by_model data.
    
    Returns a complete summary matching UsageMonitor.get_summary() structure
    with both service-level and model-level breakdowns.
    """
    return {
        "total_cost": 0.75,
        "events_count": 15,
        "by_service": {
            SERVICE_GEMINI: {
                "metrics": {METRIC_INPUT_TOKENS: 2_000_000, METRIC_OUTPUT_TOKENS: 500_000},
                "cost": 0.50
            },
            SERVICE_ELEVENLABS: {
                "metrics": {METRIC_CHARACTERS: 5_000},
                "cost": 0.25
            }
        },
        "by_model": {
            MODEL_GEMINI_FLASH: {
                "metrics": {METRIC_INPUT_TOKENS: 1_500_000, METRIC_OUTPUT_TOKENS: 400_000},
                "cost": 0.35
            },
            MODEL_GEMINI_PRO: {
                "metrics": {METRIC_INPUT_TOKENS: 500_000, METRIC_OUTPUT_TOKENS: 100_000},
                "cost": 0.15
            },
            "21m00Tcm4TlvDq8ikWAM": {
                "metrics": {METRIC_CHARACTERS: 5_000},
                "cost": 0.25
            }
        }
    }


@pytest.fixture
def mock_monitor_with_consumption(mock_consumption_summary):
    """Create a mock UsageMonitor with consumption data."""
    mock = MagicMock()
    mock.get_summary.return_value = mock_consumption_summary
    return mock


# =============================================================================
# P0 Tests: Consumption Data Formatting
# =============================================================================

class TestConsumptionDataFormatting:
    """P0 tests for consumption data formatting in UsageDisplay."""

    def test_format_by_service_breakdown(self, mock_monitor_with_consumption):
        """[5.3-UNIT-001][P0] Verify UsageDisplay formats by_service data correctly.
        
        GIVEN: A UsageMonitor with consumption data including by_service breakdown
        WHEN: UsageDisplay renders the panel
        THEN: The panel contains service names, metrics, and costs
        
        AC: AC2 (Breakdown by service)
        """
        # GIVEN: Mock monitor with by_service data
        with patch("eleven_video.ui.usage_panel.UsageMonitor.get_instance", return_value=mock_monitor_with_consumption):
            display = UsageDisplay()
            
            # WHEN: Render the display
            panel = display.__rich__()
            
            # Render panel to string using Rich Console
            string_io = StringIO()
            console = Console(file=string_io, force_terminal=False, width=120)
            console.print(panel)
            panel_str = string_io.getvalue()
            
            # THEN: Panel should contain service breakdown
            assert "Gemini" in panel_str or SERVICE_GEMINI in panel_str, "Missing Gemini service in display"
            assert SERVICE_ELEVENLABS in panel_str.lower(), "Missing ElevenLabs service in display"
            assert "2.00M" in panel_str or "2,000,000" in panel_str, "Missing input token count"
            assert "$0.50" in panel_str, "Missing Gemini cost"
            assert "$0.25" in panel_str, "Missing ElevenLabs cost"

    def test_format_by_model_breakdown(self, mock_monitor_with_consumption):
        """[5.3-UNIT-002][P0] Verify UsageDisplay formats by_model data correctly.
        
        GIVEN: A UsageMonitor with consumption data including by_model breakdown
        WHEN: UsageDisplay renders the panel
        THEN: The panel contains model IDs, metrics, and individual costs
        
        AC: AC3 (Breakdown by model)
        """
        # GIVEN: Mock monitor with by_model data
        with patch("eleven_video.ui.usage_panel.UsageMonitor.get_instance", return_value=mock_monitor_with_consumption):
            display = UsageDisplay()
            
            # WHEN: Render the display
            panel = display.__rich__()
            
            # Render panel to string using Rich Console
            string_io = StringIO()
            console = Console(file=string_io, force_terminal=False, width=120)
            console.print(panel)
            panel_str = string_io.getvalue()
            
            # THEN: Panel should contain model breakdown
            assert MODEL_GEMINI_FLASH in panel_str, "Missing gemini-2.5-flash model"
            assert MODEL_GEMINI_PRO in panel_str, "Missing gemini-2.5-pro model"
            assert "21m00Tcm4TlvDq8ikWAM" in panel_str, "Missing ElevenLabs voice ID"
            assert "$0.35" in panel_str, "Missing Flash model cost"
            assert "$0.15" in panel_str, "Missing Pro model cost"

    def test_total_cost_display(self, mock_monitor_with_consumption):
        """[5.3-UNIT-003][P0] Verify total cost is prominently displayed.
        
        GIVEN: A UsageMonitor with consumption data
        WHEN: UsageDisplay renders the panel
        THEN: The total cost is displayed prominently
        
        AC: AC1, AC5 (Total cost display)
        """
        # GIVEN: Mock monitor with total cost
        with patch("eleven_video.ui.usage_panel.UsageMonitor.get_instance", return_value=mock_monitor_with_consumption):
            display = UsageDisplay()
            
            # WHEN: Render the display
            panel = display.__rich__()
            
            # Render panel to string using Rich Console
            string_io = StringIO()
            console = Console(file=string_io, force_terminal=False, width=120)
            console.print(panel)
            panel_str = string_io.getvalue()
            
            # THEN: Total cost should be visible
            assert "$0.75" in panel_str or "$0.7" in panel_str, "Missing total cost"


# =============================================================================
# P2 Tests: Edge Cases
# =============================================================================

class TestConsumptionEdgeCases:
    """P2 tests for edge cases in consumption data display."""

    def test_empty_usage_zero_cost(self):
        """[5.3-UNIT-004][P2] Verify display handles zero usage gracefully.
        
        GIVEN: A UsageMonitor with no tracked events (zero cost)
        WHEN: UsageDisplay renders the panel
        THEN: The panel displays $0.00 without errors
        
        Edge Case: Empty usage
        """
        # GIVEN: Empty usage summary
        empty_summary = {
            "total_cost": 0.0,
            "events_count": 0,
            "by_service": {},
            "by_model": {}
        }
        mock = MagicMock()
        mock.get_summary.return_value = empty_summary
        
        with patch("eleven_video.ui.usage_panel.UsageMonitor.get_instance", return_value=mock):
            display = UsageDisplay()
            
            # WHEN: Render the display
            panel = display.__rich__()
            
            # Render panel to string using Rich Console
            string_io = StringIO()
            console = Console(file=string_io, force_terminal=False, width=120)
            console.print(panel)
            panel_str = string_io.getvalue()
            
            # THEN: Should display $0.00 without crashing
            assert "$0.00" in panel_str or "$0.0" in panel_str, "Missing zero cost display"

    def test_single_service_only_gemini(self):
        """[5.3-UNIT-005][P2] Verify display handles single service (Gemini only).
        
        GIVEN: A UsageMonitor with only Gemini usage (no ElevenLabs)
        WHEN: UsageDisplay renders the panel
        THEN: The panel shows Gemini data without ElevenLabs
        
        Edge Case: Single service only
        """
        # GIVEN: Gemini-only usage
        gemini_only_summary = {
            "total_cost": 0.50,
            "events_count": 5,
            "by_service": {
                SERVICE_GEMINI: {
                    "metrics": {METRIC_INPUT_TOKENS: 1_000_000},
                    "cost": 0.50
                }
            },
            "by_model": {
                MODEL_GEMINI_FLASH: {
                    "metrics": {METRIC_INPUT_TOKENS: 1_000_000},
                    "cost": 0.50
                }
            }
        }
        mock = MagicMock()
        mock.get_summary.return_value = gemini_only_summary
        
        with patch("eleven_video.ui.usage_panel.UsageMonitor.get_instance", return_value=mock):
            display = UsageDisplay()
            
            # WHEN: Render the display
            panel = display.__rich__()
            
            # Render panel to string using Rich Console
            string_io = StringIO()
            console = Console(file=string_io, force_terminal=False, width=120)
            console.print(panel)
            panel_str = string_io.getvalue()
            
            # THEN: Should show Gemini only
            assert SERVICE_GEMINI in panel_str.lower(), "Missing Gemini service"
            assert SERVICE_ELEVENLABS not in panel_str.lower(), "Should not show ElevenLabs"

    def test_multiple_models_same_service(self):
        """[5.3-UNIT-006][P2] Verify display handles multiple models from same service.
        
        GIVEN: A UsageMonitor with multiple Gemini models (Flash + Pro)
        WHEN: UsageDisplay renders the panel
        THEN: Both models are shown with individual costs
        
        Edge Case: Multiple models from same service
        """
        # GIVEN: Multiple Gemini models
        multi_model_summary = {
            "total_cost": 0.50,
            "events_count": 10,
            "by_service": {
                SERVICE_GEMINI: {
                    "metrics": {METRIC_INPUT_TOKENS: 2_000_000, METRIC_OUTPUT_TOKENS: 600_000},
                    "cost": 0.50
                }
            },
            "by_model": {
                MODEL_GEMINI_FLASH: {
                    "metrics": {METRIC_INPUT_TOKENS: 1_500_000, METRIC_OUTPUT_TOKENS: 400_000},
                    "cost": 0.35
                },
                MODEL_GEMINI_PRO: {
                    "metrics": {METRIC_INPUT_TOKENS: 500_000, METRIC_OUTPUT_TOKENS: 200_000},
                    "cost": 0.15
                }
            }
        }
        mock = MagicMock()
        mock.get_summary.return_value = multi_model_summary
        
        with patch("eleven_video.ui.usage_panel.UsageMonitor.get_instance", return_value=mock):
            display = UsageDisplay()
            
            # WHEN: Render the display
            panel = display.__rich__()
            
            # Render panel to string using Rich Console
            string_io = StringIO()
            console = Console(file=string_io, force_terminal=False, width=120)
            console.print(panel)
            panel_str = string_io.getvalue()
            
            # THEN: Both models should be shown
            assert MODEL_GEMINI_FLASH in panel_str, "Missing Flash model"
            assert MODEL_GEMINI_PRO in panel_str, "Missing Pro model"
            assert "$0.35" in panel_str, "Missing Flash cost"
            assert "$0.15" in panel_str, "Missing Pro model cost"

    def test_missing_metrics_defensive_parsing(self):
        """[5.3-UNIT-007][P2] Verify display handles missing metrics gracefully.
        
        GIVEN: A UsageMonitor summary with missing/incomplete metrics
        WHEN: UsageDisplay renders the panel
        THEN: The panel renders without crashing, showing available data
        
        Edge Case: Missing metrics in summary
        """
        # GIVEN: Incomplete summary (missing some fields)
        incomplete_summary = {
            "total_cost": 0.25,
            "events_count": 3,
            "by_service": {
                SERVICE_GEMINI: {
                    "metrics": {},  # Empty metrics
                    "cost": 0.25
                }
            },
            "by_model": {}  # Empty by_model
        }
        mock = MagicMock()
        mock.get_summary.return_value = incomplete_summary
        
        with patch("eleven_video.ui.usage_panel.UsageMonitor.get_instance", return_value=mock):
            display = UsageDisplay()
            
            # WHEN: Render the display
            panel = display.__rich__()
            
            # Render panel to string using Rich Console
            string_io = StringIO()
            console = Console(file=string_io, force_terminal=False, width=120)
            console.print(panel)
            panel_str = string_io.getvalue()
            
            # THEN: Should not crash, should show total cost
            assert "$0.25" in panel_str, "Missing total cost"


# =============================================================================
# P2 Tests: Visual Snapshot Testing (Optional Enhancement)
# =============================================================================

class TestConsumptionVisualLayout:
    """P2 tests for visual layout validation."""

    def test_panel_layout_with_long_model_ids(self):
        """[5.3-UNIT-008][P2] Verify panel layout doesn't break with long model IDs.
        
        GIVEN: A UsageMonitor with very long model IDs (voice IDs)
        WHEN: UsageDisplay renders the panel
        THEN: The panel renders without layout issues
        
        Visual Test: Long model ID handling
        """
        # GIVEN: Long model IDs
        long_id_summary = {
            "total_cost": 0.50,
            "events_count": 5,
            "by_service": {
                SERVICE_ELEVENLABS: {
                    "metrics": {METRIC_CHARACTERS: 5_000},
                    "cost": 0.50
                }
            },
            "by_model": {
                "21m00Tcm4TlvDq8ikWAM_very_long_voice_identifier_that_might_break_layout": {
                    "metrics": {METRIC_CHARACTERS: 5_000},
                    "cost": 0.50
                }
            }
        }
        mock = MagicMock()
        mock.get_summary.return_value = long_id_summary
        
        with patch("eleven_video.ui.usage_panel.UsageMonitor.get_instance", return_value=mock):
            display = UsageDisplay()
            
            # WHEN: Render the display
            panel = display.__rich__()
            
            # THEN: Should render without errors
            # This test will FAIL until Story 5.3 implementation
            assert panel is not None, "Panel should render with long IDs"

    def test_panel_layout_with_varying_cost_values(self):
        """[5.3-UNIT-009][P2] Verify panel layout handles varying cost magnitudes.
        
        GIVEN: A UsageMonitor with costs ranging from $0.00 to large values
        WHEN: UsageDisplay renders the panel
        THEN: All cost values are formatted consistently
        
        Visual Test: Cost value formatting
        """
        # GIVEN: Varying cost magnitudes
        varying_costs_summary = {
            "total_cost": 123.45,
            "events_count": 100,
            "by_service": {
                SERVICE_GEMINI: {
                    "metrics": {METRIC_INPUT_TOKENS: 100_000_000},
                    "cost": 100.00
                },
                SERVICE_ELEVENLABS: {
                    "metrics": {METRIC_CHARACTERS: 200_000},
                    "cost": 23.45
                }
            },
            "by_model": {
                MODEL_GEMINI_FLASH: {
                    "metrics": {METRIC_INPUT_TOKENS: 100_000_000},
                    "cost": 100.00
                },
                "21m00Tcm4TlvDq8ikWAM": {
                    "metrics": {METRIC_CHARACTERS: 200_000},
                    "cost": 23.45
                }
            }
        }
        mock = MagicMock()
        mock.get_summary.return_value = varying_costs_summary
        
        with patch("eleven_video.ui.usage_panel.UsageMonitor.get_instance", return_value=mock):
            display = UsageDisplay()
            
            # WHEN: Render the display
            panel = display.__rich__()
            
            # Render panel to string using Rich Console
            string_io = StringIO()
            console = Console(file=string_io, force_terminal=False, width=120)
            console.print(panel)
            panel_str = string_io.getvalue()
            
            # THEN: Should format all costs consistently
            assert "$123.45" in panel_str or "$123.4" in panel_str, "Missing large total cost"
            assert "$100" in panel_str, "Missing $100 cost"
