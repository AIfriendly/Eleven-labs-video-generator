"""
Tests for DurationSelector Input Handling - Story 3.6

Test Groups:
- Group 2: Duration Selection Input (Task 3)
- Group 3: Error Handling
- Group 5: Non-TTY Fallback (R-004 Mitigation)
- Group 6: Edge Case Inputs

Test IDs: 3.6-COMP-001 (Duration selection menu rendering)
Mirrors: tests/ui/test_gemini_model_selector_input.py (Story 3.5)
"""
import pytest
from unittest.mock import Mock, patch


# =============================================================================
# Test Group 2: Duration Selection Input (Task 3) - 3.6-COMP-001
# =============================================================================

class TestDurationSelectorInput:
    """Tests for DurationSelector._get_user_selection() input handling."""

    def test_select_duration_returns_minutes_for_valid_number(self, duration_selector, sample_duration_options):
        """[P0] [3.6-COMP-001] Selecting valid number returns corresponding duration in minutes.
        
        AC: #2 - When I select a duration by number, the system uses that duration.
        """
        # Given: A DurationSelector with preset options
        # When: User selects option 1 (first duration preset, should be 3 minutes)
        with patch("eleven_video.ui.duration_selector.Prompt") as mock_prompt:
            mock_prompt.ask.return_value = "1"
            result = duration_selector._get_user_selection()
        
        # Then: Should return first option's minutes value
        assert result == sample_duration_options[0].minutes

    def test_select_duration_returns_none_for_zero(self, duration_selector):
        """[P0] [3.6-COMP-001] Selecting 0 returns None (use default duration).
        
        AC: #3 - Option to use default duration.
        """
        # Given: A DurationSelector and user selects 0
        # When: User selects option 0
        with patch("eleven_video.ui.duration_selector.Prompt") as mock_prompt:
            mock_prompt.ask.return_value = "0"
            result = duration_selector._get_user_selection()
        
        # Then: Should return None (meaning use default)
        assert result is None

    def test_select_duration_handles_invalid_number(self, duration_selector):
        """[P1] [3.6-COMP-001] Invalid number selection falls back to default."""
        # Given: A DurationSelector and invalid input
        # When: User enters invalid number (out of range)
        with patch("eleven_video.ui.duration_selector.Prompt") as mock_prompt:
            with patch("eleven_video.ui.duration_selector.console"):
                mock_prompt.ask.return_value = "99"
                result = duration_selector._get_user_selection()
        
        # Then: Should return None (default)
        assert result is None

    def test_select_duration_handles_non_numeric_input(self, duration_selector):
        """[P1] [3.6-COMP-001] Non-numeric input falls back to default."""
        # Given: A DurationSelector and non-numeric input
        # When: User enters non-numeric input
        with patch("eleven_video.ui.duration_selector.Prompt") as mock_prompt:
            with patch("eleven_video.ui.duration_selector.console"):
                mock_prompt.ask.return_value = "abc"
                result = duration_selector._get_user_selection()
        
        # Then: Should return None (default) gracefully
        assert result is None


# =============================================================================
# Test Group 3: Error Handling
# =============================================================================

class TestDurationSelectorErrorHandling:
    """Tests for DurationSelector error handling in select_duration_interactive()."""

    def test_select_duration_interactive_graceful_exception_handling(self, duration_selector):
        """[P1] [3.6-COMP-001] Unexpected errors fall back to default gracefully.
        
        Edge case: Any unexpected exception should not crash the CLI.
        """
        # Given: A DurationSelector that encounters an unexpected error
        # When: Calling select_duration_interactive with mocked exception
        with patch("eleven_video.ui.duration_selector.console") as mock_console:
            mock_console.is_terminal = True
            with patch.object(duration_selector, '_display_duration_options', side_effect=Exception("Unexpected error")):
                result = duration_selector.select_duration_interactive()
        
        # Then: Should return None (fallback to default) without crashing
        # Note: Implementation needs try-except wrapper, test will fail until implemented
        assert result is None


# =============================================================================
# Test Group 5: Non-TTY Fallback (R-004 Mitigation)
# =============================================================================

class TestDurationSelectorNonTTY:
    """Tests for non-TTY environment detection and fallback."""

    def test_select_duration_interactive_skips_prompt_in_non_tty(self, duration_selector):
        """[P1] [3.6-COMP-001] Non-TTY environment skips prompt and uses default.
        
        AC: R-004 mitigation - Non-TTY fallback.
        """
        # Given: A DurationSelector in non-TTY environment
        # When: Calling select_duration_interactive
        with patch("eleven_video.ui.duration_selector.console") as mock_console:
            mock_console.is_terminal = False
            result = duration_selector.select_duration_interactive()
        
        # Then: Should return None (default) without prompting
        assert result is None

    def test_select_duration_interactive_shows_message_in_non_tty(self, duration_selector):
        """[P2] [3.6-AUTO-008] Non-TTY environment shows informative message.
        
        User should know why selection was skipped.
        """
        # Given: A DurationSelector in non-TTY environment
        # When: Calling select_duration_interactive
        with patch("eleven_video.ui.duration_selector.console") as mock_console:
            mock_console.is_terminal = False
            duration_selector.select_duration_interactive()
        
        # Then: Console should have printed a message
        assert mock_console.print.called


# =============================================================================
# Test Group 6: Edge Case Inputs (Automation Expansion)
# =============================================================================

class TestDurationSelectorEdgeCases:
    """Tests for edge case input handling to expand coverage."""

    @pytest.mark.parametrize("invalid_input,description", [
        ("-1", "negative number"),
        ("9999", "very large number out of range"),
        ("abc", "non-numeric text input"),
        ("!@#$%", "special characters"),
        ("1.5", "decimal number"),
        ("  ", "whitespace only"),
    ])
    def test_select_duration_handles_invalid_input(self, duration_selector, invalid_input, description):
        """[P2] [3.6-AUTO-001-004] Invalid inputs should all fall back to default.
        
        Edge cases: negative numbers, large numbers, non-numeric, special chars.
        Parametrized for comprehensive coverage with minimal code duplication.
        """
        # Given: A DurationSelector
        # When: User enters invalid input ({description})
        with patch("eleven_video.ui.duration_selector.Prompt") as mock_prompt:
            with patch("eleven_video.ui.duration_selector.console"):
                mock_prompt.ask.return_value = invalid_input
                result = duration_selector._get_user_selection()
        
        # Then: Should return None (default) gracefully
        assert result is None, f"Expected None for {description} input '{invalid_input}'"

    def test_select_duration_handles_empty_input(self, duration_selector):
        """[P2] [3.6-AUTO-002] Empty string input uses default (via Rich default).
        
        Edge case: User presses Enter without typing anything.
        """
        # Given: A DurationSelector
        # When: User enters empty string (Rich returns default "0")
        with patch("eleven_video.ui.duration_selector.Prompt") as mock_prompt:
            mock_prompt.ask.return_value = "0"  # Rich default
            result = duration_selector._get_user_selection()
        
        # Then: Should return None (use default duration)
        assert result is None

    def test_select_last_duration_in_list(self, duration_selector, sample_duration_options):
        """[P2] [3.6-AUTO-009] Selecting last duration in list works correctly.
        
        Boundary: Maximum valid index selection.
        """
        # Given: A DurationSelector with multiple options
        num_options = len(sample_duration_options)
        
        # When: User selects last option
        with patch("eleven_video.ui.duration_selector.Prompt") as mock_prompt:
            mock_prompt.ask.return_value = str(num_options)  # Last option
            result = duration_selector._get_user_selection()
        
        # Then: Should return the last option's minutes
        assert result == sample_duration_options[-1].minutes

    def test_select_duration_interactive_full_flow(self, duration_selector, sample_duration_options):
        """[P1] [3.6-AUTO-010] Full interactive flow works end-to-end.
        
        Integration test: Display options, select, return minutes.
        """
        # Given: A DurationSelector
        # When: User goes through full interactive flow
        with patch("eleven_video.ui.duration_selector.console") as mock_console:
            with patch("eleven_video.ui.duration_selector.Prompt") as mock_prompt:
                mock_console.is_terminal = True
                mock_prompt.ask.return_value = "2"  # Select second option (5 min typically)
                result = duration_selector.select_duration_interactive()
        
        # Then: Should return second option's minutes value
        assert result == sample_duration_options[1].minutes


# =============================================================================
# Test Group 7: Unique to DurationSelector (Duration-specific tests)
# =============================================================================

class TestDurationSelectorSpecific:
    """Tests specific to DurationSelector functionality (not in other selectors)."""

    def test_duration_selector_does_not_require_api_call(self, duration_selector):
        """[P1] [3.6-UNIT-002] DurationSelector uses predefined options, no API needed.
        
        Key difference from other selectors: Duration options are hardcoded presets.
        """
        # Given: A DurationSelector
        # When: Checking its internal options
        # Then: It should have predefined options without needing an adapter
        assert hasattr(duration_selector, '_options')
        assert len(duration_selector._options) > 0

    def test_duration_options_contain_expected_values(self, sample_duration_options):
        """[P1] [3.6-UNIT-002] Duration options contain 3, 5, and 10 minute presets.
        
        Story requirement: Preset durations 3, 5, 10 minutes.
        """
        # Given: The sample duration options
        # When: Extracting minutes values
        minutes_values = [opt.minutes for opt in sample_duration_options]
        
        # Then: Should contain 3, 5, and 10 minute options
        assert 3 in minutes_values, "Expected 3-minute duration option"
        assert 5 in minutes_values, "Expected 5-minute duration option"
        assert 10 in minutes_values, "Expected 10-minute duration option"
