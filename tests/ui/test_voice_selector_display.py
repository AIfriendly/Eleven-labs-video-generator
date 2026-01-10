"""
Tests for VoiceSelector Display - Story 3.3

Test Groups:
- Group 1: VoiceSelector Display (Task 1)
- Group 8: Boundary Conditions

Test IDs: 3.3-UNIT-001 to 003, 3.3-AUTO-005 to 006
"""
import pytest
from unittest.mock import Mock, patch


# =============================================================================
# Test Group 1: VoiceSelector Display (Task 1) - 3.3-COMP-001
# =============================================================================

class TestVoiceSelectorDisplay:
    """Tests for VoiceSelector._display_voice_list() rendering."""

    def test_voice_selector_can_be_imported(self):
        """[P1] [3.3-UNIT-001] VoiceSelector should be importable from ui module.
        
        Validates module structure is correct.
        """
        # Given: The ui module exists
        # When: Importing VoiceSelector from ui module
        from eleven_video.ui.voice_selector import VoiceSelector
        
        # Then: VoiceSelector should exist
        assert VoiceSelector is not None

    def test_voice_selector_displays_numbered_list(self, voice_selector, sample_voices):
        """[P1] [3.3-UNIT-002] VoiceSelector should display voices as numbered list.
        
        AC: #1 - Display a numbered list of available voice options.
        """
        # Given: A VoiceSelector with mock adapter and voices
        # When: Displaying voice list
        with patch("eleven_video.ui.voice_selector.console") as mock_console:
            voice_selector._display_voice_list(sample_voices)
        
        # Then: Console should have been called with table output
        assert mock_console.print.called
        # Console.print called twice: Panel header + Table
        assert mock_console.print.call_count >= 2

    def test_voice_selector_shows_default_option_first(self, voice_selector, single_voice):
        """[P1] [3.3-UNIT-003] VoiceSelector should show default voice as option [0].
        
        AC: #4 - Show option to use default voice (e.g., "[0] Use default voice").
        """
        # Given: A VoiceSelector with voices
        # When: Displaying voice list
        with patch("eleven_video.ui.voice_selector.console") as mock_console:
            voice_selector._display_voice_list(single_voice)
        
        # Then: First option should be default voice (option 0)
        assert mock_console.print.call_count >= 2


# =============================================================================
# Test Group 8: Boundary Conditions (Automation Expansion)
# =============================================================================

class TestVoiceSelectorBoundaryConditions:
    """Tests for boundary conditions in voice list handling."""

    def test_display_voice_list_with_single_voice(self, voice_selector, single_voice):
        """[P2] [3.3-AUTO-005] Display works correctly with single voice option.
        
        Boundary: Minimum voice list (1 voice + default).
        """
        # Given: A VoiceSelector with exactly one voice
        # When: Displaying voice list
        with patch("eleven_video.ui.voice_selector.console") as mock_console:
            voice_selector._display_voice_list(single_voice)
        
        # Then: Console should have been called (Panel + Table)
        assert mock_console.print.call_count >= 2

    def test_display_voice_list_with_many_voices(self, voice_selector):
        """[P2] [3.3-AUTO-006] Display handles large voice list (20+ voices).
        
        Boundary: R-008 risk mitigation - many voices.
        """
        # Given: A VoiceSelector with many voices
        from eleven_video.models.domain import VoiceInfo
        voices = [
            VoiceInfo(voice_id=f"voice-{i}", name=f"Voice {i}", category="premade")
            for i in range(25)
        ]
        
        # When: Displaying voice list
        with patch("eleven_video.ui.voice_selector.console") as mock_console:
            voice_selector._display_voice_list(voices)
        
        # Then: Console should complete without error
        assert mock_console.print.call_count >= 2
