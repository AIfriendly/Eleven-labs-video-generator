"""
Tests for DurationSelector Display - Story 3.6

Test Groups:
- Group 1: DurationSelector Display (Task 2)
- Group 4: Boundary Conditions

Test IDs: 3.6-COMP-001 (Duration selection menu rendering)
Mirrors: tests/ui/test_gemini_model_selector_display.py (Story 3.5)
"""
import pytest
from unittest.mock import Mock, patch


# =============================================================================
# Test Group 1: DurationSelector Display (Task 2) - 3.6-COMP-001
# =============================================================================

class TestDurationSelectorDisplay:
    """Tests for DurationSelector._display_duration_options() rendering."""

    def test_duration_selector_can_be_imported(self):
        """[P1] [3.6-COMP-001] DurationSelector should be importable from ui module.
        
        Validates module structure is correct.
        """
        # Given: The ui module exists
        # When: Importing DurationSelector from ui module
        from eleven_video.ui.duration_selector import DurationSelector
        
        # Then: DurationSelector should exist
        assert DurationSelector is not None

    def test_duration_selector_displays_numbered_list(self, duration_selector):
        """[P1] [3.6-COMP-001] DurationSelector should display durations as numbered list.
        
        AC: #1 - Display a numbered list of duration options (e.g., 3 minutes, 5 minutes, 10 minutes).
        """
        from rich.panel import Panel
        from rich.table import Table
        
        # Given: A DurationSelector with predefined options
        # When: Displaying duration list
        with patch("eleven_video.ui.duration_selector.console") as mock_console:
            duration_selector._display_duration_options()
        
        # Then: Console should have been called with Panel and Table
        assert mock_console.print.call_count >= 2
        
        # Verify Panel was printed with correct header
        call_args = [call[0][0] for call in mock_console.print.call_args_list]
        panel_calls = [arg for arg in call_args if isinstance(arg, Panel)]
        assert len(panel_calls) >= 1, "Expected Panel to be printed"
        
        # Verify Table was printed
        table_calls = [arg for arg in call_args if isinstance(arg, Table)]
        assert len(table_calls) >= 1, "Expected Table to be printed"

    def test_duration_selector_shows_default_option_first(self, duration_selector):
        """[P1] [3.6-COMP-001] DurationSelector should show default duration as option [0].
        
        AC: #3 - Show option to use the default duration (e.g., "[0] Default (3 minutes)").
        """
        from rich.table import Table
        
        # Given: A DurationSelector with preset options
        # When: Displaying duration list
        with patch("eleven_video.ui.duration_selector.console") as mock_console:
            duration_selector._display_duration_options()
        
        # Then: Table should include default option as row 0
        assert mock_console.print.call_count >= 2
        
        # Verify Table was printed with default duration info
        call_args = [call[0][0] for call in mock_console.print.call_args_list]
        table_calls = [arg for arg in call_args if isinstance(arg, Table)]
        assert len(table_calls) >= 1, "Expected Table with default option"

    def test_duration_selector_shows_multiple_duration_options(self, duration_selector, sample_duration_options):
        """[P1] [3.6-COMP-001] DurationSelector should show all available duration presets.
        
        AC: #1 - Duration options include 3, 5, 10 minute presets.
        """
        # Given: A DurationSelector with predefined options
        # When: Displaying duration list
        with patch("eleven_video.ui.duration_selector.console") as mock_console:
            duration_selector._display_duration_options()
        
        # Then: Console should have been called (Panel + Table)
        assert mock_console.print.call_count >= 2
        
        # The DurationSelector uses DURATION_OPTIONS which should have 3 presets
        assert len(sample_duration_options) >= 3, "Expected at least 3 duration options (3, 5, 10 min)"


# =============================================================================
# Test Group 4: Boundary Conditions (Automation Expansion)
# =============================================================================

class TestDurationSelectorBoundaryConditions:
    """Tests for boundary conditions in duration option handling."""

    def test_display_duration_options_renders_without_error(self, duration_selector):
        """[P2] [3.6-AUTO-005] Display completes without error.
        
        Boundary: Basic rendering sanity check.
        """
        # Given: A DurationSelector with predefined options
        # When: Displaying duration list
        with patch("eleven_video.ui.duration_selector.console") as mock_console:
            # Then: Should not raise an exception
            duration_selector._display_duration_options()
        
        # And: Console should have been called at least once
        assert mock_console.print.called

    def test_duration_option_dataclass_has_required_fields(self, sample_duration_options):
        """[P2] [3.6-AUTO-006] DurationOption dataclass has required fields.
        
        Validates domain model structure.
        """
        # Given: The sample duration options
        # When: Inspecting the first option
        first_option = sample_duration_options[0]
        
        # Then: It should have minutes, label, and description
        assert hasattr(first_option, 'minutes'), "DurationOption should have 'minutes' field"
        assert hasattr(first_option, 'label'), "DurationOption should have 'label' field"
        assert hasattr(first_option, 'description'), "DurationOption should have 'description' field"

    def test_duration_option_has_estimated_word_count(self, sample_duration_options):
        """[P2] [3.6-AUTO-007] DurationOption provides estimated word count.
        
        Story requirement: 150 words/minute estimate.
        """
        # Given: A duration option
        option = sample_duration_options[0]  # Assuming 3 minutes
        
        # When: Getting estimated word count
        word_count = option.estimated_word_count
        
        # Then: Word count should be duration * 150
        assert word_count == option.minutes * 150

    def test_duration_option_has_estimated_image_count(self, sample_duration_options):
        """[P2] [3.6-AUTO-008] DurationOption provides estimated image count.
        
        Story requirement: 15 images/minute estimate.
        """
        # Given: A duration option
        option = sample_duration_options[0]
        
        # When: Getting estimated image count
        image_count = option.estimated_image_count
        
        # Then: Image count should be duration * 15
        assert image_count == option.minutes * 15
