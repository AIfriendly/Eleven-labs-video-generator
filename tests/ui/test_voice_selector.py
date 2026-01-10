"""
Tests for VoiceSelector Integration - Story 3.3

Test Groups:
- Group 3: Interactive Selection Flow (Tasks 3, 4)
- Group 4: Error Handling
- Group 5: Non-TTY Fallback
- Group 6: CLI Generate Command Integration
- Group 9: CLI Integration with VoiceSelector

Test IDs: 3.3-UNIT-008 to 014, 3.3-AUTO-008
"""
import pytest
from unittest.mock import Mock, MagicMock, patch

from eleven_video.models.domain import VoiceInfo


# =============================================================================
# Test Group 3: Interactive Selection Flow (Tasks 3, 4)
# =============================================================================

class TestVoiceSelectorInteractive:
    """Tests for VoiceSelector.select_voice_interactive() full flow."""

    def test_select_voice_interactive_fetches_voices(self, voice_selector, mock_adapter):
        """[P0] [3.3-UNIT-008] select_voice_interactive() calls adapter.list_voices()."""
        # Given: A VoiceSelector with mock adapter
        mock_adapter.list_voices.return_value = [
            VoiceInfo(voice_id="v1", name="Voice 1", category="premade")
        ]
        
        # When: Calling select_voice_interactive in terminal mode
        with patch("eleven_video.ui.voice_selector.console") as mock_console:
            mock_console.is_terminal = True
            with patch("eleven_video.ui.voice_selector.Prompt") as mock_prompt:
                mock_prompt.ask.return_value = "0"
                voice_selector.select_voice_interactive()
        
        # Then: list_voices should be called with caching enabled
        mock_adapter.list_voices.assert_called_once_with(use_cache=True)

    def test_select_voice_interactive_returns_selected_voice_id(self, voice_selector, mock_adapter):
        """[P0] [3.3-UNIT-009] Full flow returns selected voice_id correctly."""
        # Given: A VoiceSelector with voices and user selection
        mock_adapter.list_voices.return_value = [
            VoiceInfo(voice_id="selected-voice", name="Selected", category="premade"),
            VoiceInfo(voice_id="other-voice", name="Other", category="premade"),
        ]
        
        # When: User selects voice 1
        with patch("eleven_video.ui.voice_selector.console") as mock_console:
            mock_console.is_terminal = True
            with patch("eleven_video.ui.voice_selector.Prompt") as mock_prompt:
                mock_prompt.ask.return_value = "1"
                result = voice_selector.select_voice_interactive()
        
        # Then: Should return the selected voice_id
        assert result == "selected-voice"


# =============================================================================
# Test Group 4: Error Handling (Task 3) - AC: #3
# =============================================================================

class TestVoiceSelectorErrorHandling:
    """Tests for error handling when voice listing fails."""

    def test_select_voice_handles_api_failure(self, voice_selector, mock_adapter):
        """[P0] [3.3-UNIT-010] API failure shows warning and returns None (default).
        
        AC: #3 - System shows helpful error and falls back to default voice.
        """
        # Given: A VoiceSelector where list_voices raises exception
        mock_adapter.list_voices.side_effect = Exception("API Error: Rate limited")
        
        # When: Calling select_voice_interactive
        with patch("eleven_video.ui.voice_selector.console") as mock_console:
            mock_console.is_terminal = True
            result = voice_selector.select_voice_interactive()
        
        # Then: Should return None (default) and print warning
        assert result is None
        warning_printed = any(
            "warning" in str(call).lower() or "error" in str(call).lower() 
            for call in mock_console.print.call_args_list
        )
        assert warning_printed, "Should print warning message on API failure"

    def test_select_voice_handles_empty_voice_list(self, voice_selector, mock_adapter):
        """[P1] [3.3-UNIT-011] Empty voice list returns None (default)."""
        # Given: A VoiceSelector where list_voices returns empty list
        mock_adapter.list_voices.return_value = []
        
        # When: Calling select_voice_interactive
        with patch("eleven_video.ui.voice_selector.console") as mock_console:
            mock_console.is_terminal = True
            result = voice_selector.select_voice_interactive()
        
        # Then: Should return None (use default)
        assert result is None


# =============================================================================
# Test Group 5: Non-TTY Fallback (Task 6) - R-004 Mitigation
# =============================================================================

class TestNonTTYFallback:
    """Tests for non-TTY environment detection and fallback."""

    def test_select_voice_skips_prompt_in_non_tty(self, voice_selector, mock_adapter):
        """[P1] [3.3-UNIT-012] Non-TTY environment skips selection, returns None.
        
        R-004 mitigation: Detect non-TTY and skip voice selection.
        """
        # Given: A VoiceSelector in non-TTY environment
        # When: Calling select_voice_interactive in non-TTY
        with patch("eleven_video.ui.voice_selector.console") as mock_console:
            mock_console.is_terminal = False
            result = voice_selector.select_voice_interactive()
        
        # Then: Should return None without prompting
        assert result is None
        # list_voices should NOT be called (no point fetching in non-TTY)
        mock_adapter.list_voices.assert_not_called()

    def test_select_voice_prints_message_in_non_tty(self, voice_selector):
        """[P2] [3.3-UNIT-013] Non-TTY mode prints informative message."""
        # Given: A VoiceSelector in non-TTY environment
        # When: Calling select_voice_interactive in non-TTY
        with patch("eleven_video.ui.voice_selector.console") as mock_console:
            mock_console.is_terminal = False
            voice_selector.select_voice_interactive()
        
        # Then: Should print non-interactive mode message
        mock_console.print.assert_called()
        printed_content = str(mock_console.print.call_args_list).lower()
        assert "non-interactive" in printed_content or "default" in printed_content


# =============================================================================
# Test Group 6: CLI Generate Command Integration (Task 4) - AC: #5
# =============================================================================

class TestCLIVoiceIntegration:
    """Tests for voice selection integration with generate command."""

    def test_generate_skips_voice_prompt_when_voice_provided(self):
        """[P0] [3.3-UNIT-014] --voice flag skips interactive voice prompt.
        
        AC: #5 - Voice prompt is skipped when --voice flag is provided.
        """
        # Given: CLI runner with --voice flag
        from typer.testing import CliRunner
        from eleven_video.main import app
        
        runner = CliRunner()
        
        # When: Running generate with --voice flag
        with patch("eleven_video.orchestrator.VideoPipeline") as MockPipeline:
            pipeline_instance = MockPipeline.return_value
            result = runner.invoke(
                app, 
                ["generate", "--prompt", "Test", "--voice", "explicit-voice-id"]
            )
        
        # Then: Pipeline should receive the explicit voice_id
        pipeline_instance.generate.assert_called_once()
        call_kwargs = pipeline_instance.generate.call_args[1]
        assert call_kwargs.get("voice_id") == "explicit-voice-id"


# =============================================================================
# Test Group 9: CLI Integration with VoiceSelector (Automation Expansion)
# =============================================================================

class TestCLIVoiceSelectorIntegration:
    """Tests for VoiceSelector integration in main.py generate command."""

    def test_voice_selector_import_in_generate_command(self, mock_adapter):
        """[P1] [3.3-AUTO-008] VoiceSelector can be imported and used in CLI context.
        
        Integration: Verifies the VoiceSelector module is properly accessible
        and works with the ElevenLabsAdapter interface.
        """
        # Given: VoiceSelector class exists and is importable
        from eleven_video.ui.voice_selector import VoiceSelector
        
        # When: Creating a VoiceSelector with a mock adapter
        mock_adapter.list_voices.return_value = [
            VoiceInfo(voice_id="test-voice", name="Test", category="premade")
        ]
        
        selector = VoiceSelector(mock_adapter)
        
        # Then: select_voice_interactive should work with mocked console
        with patch("eleven_video.ui.voice_selector.console") as mock_console:
            mock_console.is_terminal = True
            with patch("eleven_video.ui.voice_selector.Prompt") as mock_prompt:
                mock_prompt.ask.return_value = "1"
                result = selector.select_voice_interactive()
        
        # Verify the flow executed correctly
        assert result == "test-voice"
        mock_adapter.list_voices.assert_called_once_with(use_cache=True)
