"""
Tests for VoiceSelector Input Handling - Story 3.3

Test Groups:
- Group 2: Voice Selection Input (Task 2)
- Group 7: Edge Case Inputs

Test IDs: 3.3-UNIT-004 to 007, 3.3-AUTO-001 to 004, 007
"""
import pytest
from unittest.mock import Mock, patch

from eleven_video.models.domain import VoiceInfo


# =============================================================================
# Test Group 2: Voice Selection Input (Task 2) - 3.3-COMP-002
# =============================================================================

class TestVoiceSelectorInput:
    """Tests for VoiceSelector._get_user_selection() input handling."""

    def test_select_voice_returns_voice_id_for_valid_number(self, voice_selector):
        """[P0] [3.3-UNIT-004] Selecting valid number returns corresponding voice_id.
        
        AC: #2 - When I select a voice by number, my selection is used.
        """
        # Given: A VoiceSelector with voices
        voices = [
            VoiceInfo(voice_id="voice-rachel", name="Rachel", category="premade"),
            VoiceInfo(voice_id="voice-domi", name="Domi", category="premade"),
        ]
        
        # When: User selects option 1
        with patch("eleven_video.ui.voice_selector.Prompt") as mock_prompt:
            mock_prompt.ask.return_value = "1"
            result = voice_selector._get_user_selection(voices)
        
        # Then: Should return first voice's voice_id
        assert result == "voice-rachel"

    def test_select_voice_returns_none_for_zero(self, voice_selector, single_voice):
        """[P0] [3.3-UNIT-005] Selecting 0 returns None (use default voice).
        
        AC: #4 - Option to use default voice.
        """
        # Given: A VoiceSelector and user selects 0
        # When: User selects option 0
        with patch("eleven_video.ui.voice_selector.Prompt") as mock_prompt:
            mock_prompt.ask.return_value = "0"
            result = voice_selector._get_user_selection(single_voice)
        
        # Then: Should return None (meaning use default)
        assert result is None

    def test_select_voice_handles_invalid_number(self, voice_selector, single_voice):
        """[P1] [3.3-UNIT-006] Invalid number selection falls back to default."""
        # Given: A VoiceSelector with voices and invalid input
        # When: User enters invalid number (out of range)
        with patch("eleven_video.ui.voice_selector.Prompt") as mock_prompt:
            with patch("eleven_video.ui.voice_selector.console"):
                mock_prompt.ask.return_value = "99"
                result = voice_selector._get_user_selection(single_voice)
        
        # Then: Should return None (default)
        assert result is None

    def test_select_voice_handles_non_numeric_input(self, voice_selector, single_voice):
        """[P1] [3.3-UNIT-007] Non-numeric input falls back to default."""
        # Given: A VoiceSelector and non-numeric input
        # When: User enters non-numeric input
        with patch("eleven_video.ui.voice_selector.Prompt") as mock_prompt:
            with patch("eleven_video.ui.voice_selector.console"):
                mock_prompt.ask.return_value = "abc"
                result = voice_selector._get_user_selection(single_voice)
        
        # Then: Should return None (default) gracefully
        assert result is None


# =============================================================================
# Test Group 7: Edge Case Inputs (Automation Expansion)
# =============================================================================

class TestVoiceSelectorEdgeCases:
    """Tests for edge case input handling to expand coverage."""

    def test_select_voice_handles_negative_number(self, voice_selector, single_voice):
        """[P2] [3.3-AUTO-001] Negative number input falls back to default.
        
        Edge case: User enters a negative number like -1.
        """
        # Given: A VoiceSelector with voices
        # When: User enters negative number
        with patch("eleven_video.ui.voice_selector.Prompt") as mock_prompt:
            with patch("eleven_video.ui.voice_selector.console"):
                mock_prompt.ask.return_value = "-1"
                result = voice_selector._get_user_selection(single_voice)
        
        # Then: Should return None (default)
        assert result is None

    def test_select_voice_handles_empty_input(self, voice_selector, single_voice):
        """[P2] [3.3-AUTO-002] Empty string input uses default (via Rich default).
        
        Edge case: User presses Enter without typing anything.
        """
        # Given: A VoiceSelector with voices
        # When: User enters empty string (Rich returns default "0")
        with patch("eleven_video.ui.voice_selector.Prompt") as mock_prompt:
            mock_prompt.ask.return_value = "0"  # Rich default
            result = voice_selector._get_user_selection(single_voice)
        
        # Then: Should return None (use default voice)
        assert result is None

    def test_select_voice_handles_very_large_number(self, voice_selector, single_voice):
        """[P2] [3.3-AUTO-003] Very large number falls back to default.
        
        Edge case: User enters a number much larger than voice count.
        """
        # Given: A VoiceSelector with a few voices
        # When: User enters very large number
        with patch("eleven_video.ui.voice_selector.Prompt") as mock_prompt:
            with patch("eleven_video.ui.voice_selector.console"):
                mock_prompt.ask.return_value = "9999"
                result = voice_selector._get_user_selection(single_voice)
        
        # Then: Should return None (default)
        assert result is None

    def test_select_voice_handles_special_characters(self, voice_selector, single_voice):
        """[P2] [3.3-AUTO-004] Special character input falls back to default.
        
        Edge case: User enters special characters like !@#$%.
        """
        # Given: A VoiceSelector with voices
        # When: User enters special characters
        with patch("eleven_video.ui.voice_selector.Prompt") as mock_prompt:
            with patch("eleven_video.ui.voice_selector.console"):
                mock_prompt.ask.return_value = "!@#$%"
                result = voice_selector._get_user_selection(single_voice)
        
        # Then: Should return None (default) gracefully
        assert result is None

    def test_select_last_voice_in_list(self, voice_selector):
        """[P2] [3.3-AUTO-007] Selecting last voice in list works correctly.
        
        Boundary: Maximum valid index selection.
        """
        # Given: A VoiceSelector with multiple voices
        voices = [
            VoiceInfo(voice_id="voice-1", name="First", category="premade"),
            VoiceInfo(voice_id="voice-2", name="Second", category="premade"),
            VoiceInfo(voice_id="voice-3", name="Third", category="premade"),
            VoiceInfo(voice_id="last-voice", name="Last", category="premade"),
        ]
        
        # When: User selects last voice (index 4)
        with patch("eleven_video.ui.voice_selector.Prompt") as mock_prompt:
            mock_prompt.ask.return_value = "4"
            result = voice_selector._get_user_selection(voices)
        
        # Then: Should return the last voice's ID
        assert result == "last-voice"
