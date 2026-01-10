"""
Tests for GeminiModelSelector Input Handling - Story 3.5

Test Groups:
- Group 2: Gemini Model Selection Input (Task 5)
- Group 3: Error Handling (Task 6)
- Group 5: Non-TTY Fallback (Task 9)
- Group 6: Edge Case Inputs

Test IDs: 3.5-COMP-001 (Gemini model selection menu rendering)
Mirrors: tests/ui/test_image_model_selector_input.py (Story 3.4)
"""
import pytest
from unittest.mock import Mock, patch

from eleven_video.models.domain import GeminiModelInfo


# =============================================================================
# Test Group 2: Gemini Model Selection Input (Task 5) - 3.5-COMP-001
# =============================================================================

class TestGeminiModelSelectorInput:
    """Tests for GeminiModelSelector._get_user_selection() input handling."""

    def test_select_model_returns_model_id_for_valid_number(self, gemini_model_selector):
        """[P0] [3.5-COMP-001] Selecting valid number returns corresponding model_id.
        
        AC: #2 - When I select a model by number, my selection is used.
        """
        # Given: A GeminiModelSelector with models
        models = [
            GeminiModelInfo(model_id="gemini-2.5-flash", name="Gemini Flash", description="Fast"),
            GeminiModelInfo(model_id="gemini-2.5-pro", name="Gemini Pro", description="Quality"),
        ]
        
        # When: User selects option 1
        with patch("eleven_video.ui.gemini_model_selector.Prompt") as mock_prompt:
            mock_prompt.ask.return_value = "1"
            result = gemini_model_selector._get_user_selection(models)
        
        # Then: Should return first model's model_id
        assert result == "gemini-2.5-flash"

    def test_select_model_returns_none_for_zero(self, gemini_model_selector, single_gemini_model):
        """[P0] [3.5-COMP-001] Selecting 0 returns None (use default model).
        
        AC: #4 - Option to use default model.
        """
        # Given: A GeminiModelSelector and user selects 0
        # When: User selects option 0
        with patch("eleven_video.ui.gemini_model_selector.Prompt") as mock_prompt:
            mock_prompt.ask.return_value = "0"
            result = gemini_model_selector._get_user_selection(single_gemini_model)
        
        # Then: Should return None (meaning use default)
        assert result is None

    def test_select_model_handles_invalid_number(self, gemini_model_selector, single_gemini_model):
        """[P1] [3.5-COMP-001] Invalid number selection falls back to default."""
        # Given: A GeminiModelSelector with models and invalid input
        # When: User enters invalid number (out of range)
        with patch("eleven_video.ui.gemini_model_selector.Prompt") as mock_prompt:
            with patch("eleven_video.ui.gemini_model_selector.console"):
                mock_prompt.ask.return_value = "99"
                result = gemini_model_selector._get_user_selection(single_gemini_model)
        
        # Then: Should return None (default)
        assert result is None

    def test_select_model_handles_non_numeric_input(self, gemini_model_selector, single_gemini_model):
        """[P1] [3.5-COMP-001] Non-numeric input falls back to default."""
        # Given: A GeminiModelSelector and non-numeric input
        # When: User enters non-numeric input
        with patch("eleven_video.ui.gemini_model_selector.Prompt") as mock_prompt:
            with patch("eleven_video.ui.gemini_model_selector.console"):
                mock_prompt.ask.return_value = "abc"
                result = gemini_model_selector._get_user_selection(single_gemini_model)
        
        # Then: Should return None (default) gracefully
        assert result is None


# =============================================================================
# Test Group 3: Error Handling (Task 6) - API Failures
# =============================================================================

class TestGeminiModelSelectorErrorHandling:
    """Tests for GeminiModelSelector error handling in select_model_interactive()."""

    def test_select_model_interactive_handles_api_failure(self, gemini_model_selector, mock_gemini_adapter):
        """[P1] [3.5-COMP-001] API failure gracefully falls back to default.
        
        AC: #3 - On API failure, show helpful error and fall back to default.
        """
        # Given: A GeminiModelSelector with adapter that raises exception
        mock_gemini_adapter.list_text_models.side_effect = Exception("API Error")
        
        # When: Calling select_model_interactive
        with patch("eleven_video.ui.gemini_model_selector.console") as mock_console:
            mock_console.is_terminal = True
            result = gemini_model_selector.select_model_interactive()
        
        # Then: Should return None (default) and show warning
        assert result is None
        assert mock_console.print.called

    def test_select_model_interactive_handles_empty_model_list(self, gemini_model_selector, mock_gemini_adapter):
        """[P1] [3.5-COMP-001] Empty model list falls back to default.
        
        Edge case: API returns empty list.
        """
        # Given: A GeminiModelSelector with adapter returning empty list
        mock_gemini_adapter.list_text_models.return_value = []
        
        # When: Calling select_model_interactive
        with patch("eleven_video.ui.gemini_model_selector.console") as mock_console:
            mock_console.is_terminal = True
            result = gemini_model_selector.select_model_interactive()
        
        # Then: Should return None (default)
        assert result is None


# =============================================================================
# Test Group 5: Non-TTY Fallback (Task 9) - R-004 Mitigation
# =============================================================================

class TestGeminiModelSelectorNonTTY:
    """Tests for non-TTY environment detection and fallback."""

    def test_select_model_interactive_skips_prompt_in_non_tty(self, gemini_model_selector, mock_gemini_adapter):
        """[P1] [3.5-COMP-001] Non-TTY environment skips prompt and uses default.
        
        AC: R-004 mitigation - Non-TTY fallback.
        """
        # Given: A GeminiModelSelector in non-TTY environment
        # When: Calling select_model_interactive
        with patch("eleven_video.ui.gemini_model_selector.console") as mock_console:
            mock_console.is_terminal = False
            result = gemini_model_selector.select_model_interactive()
        
        # Then: Should return None (default) without prompting
        assert result is None
        # Adapter should NOT be called (prompt skipped)
        mock_gemini_adapter.list_text_models.assert_not_called()

    def test_select_model_interactive_shows_message_in_non_tty(self, gemini_model_selector, mock_gemini_adapter):
        """[P2] [3.5-AUTO-008] Non-TTY environment shows informative message.
        
        User should know why selection was skipped.
        """
        # Given: A GeminiModelSelector in non-TTY environment
        # When: Calling select_model_interactive
        with patch("eleven_video.ui.gemini_model_selector.console") as mock_console:
            mock_console.is_terminal = False
            gemini_model_selector.select_model_interactive()
        
        # Then: Console should have printed a message
        assert mock_console.print.called


# =============================================================================
# Test Group 6: Edge Case Inputs (Automation Expansion)
# =============================================================================

class TestGeminiModelSelectorEdgeCases:
    """Tests for edge case input handling to expand coverage."""

    @pytest.mark.parametrize("invalid_input,description", [
        ("-1", "negative number"),
        ("9999", "very large number out of range"),
        ("abc", "non-numeric text input"),
        ("!@#$%", "special characters"),
        ("1.5", "decimal number"),
        ("  ", "whitespace only"),
    ])
    def test_select_model_handles_invalid_input(self, gemini_model_selector, single_gemini_model, invalid_input, description):
        """[P2] [3.5-AUTO-001-004] Invalid inputs should all fall back to default.
        
        Edge cases: negative numbers, large numbers, non-numeric, special chars.
        Parametrized for comprehensive coverage with minimal code duplication.
        """
        # Given: A GeminiModelSelector with models
        # When: User enters invalid input ({description})
        with patch("eleven_video.ui.gemini_model_selector.Prompt") as mock_prompt:
            with patch("eleven_video.ui.gemini_model_selector.console"):
                mock_prompt.ask.return_value = invalid_input
                result = gemini_model_selector._get_user_selection(single_gemini_model)
        
        # Then: Should return None (default) gracefully
        assert result is None, f"Expected None for {description} input '{invalid_input}'"

    def test_select_model_handles_empty_input(self, gemini_model_selector, single_gemini_model):
        """[P2] [3.5-AUTO-002] Empty string input uses default (via Rich default).
        
        Edge case: User presses Enter without typing anything.
        """
        # Given: A GeminiModelSelector with models
        # When: User enters empty string (Rich returns default "0")
        with patch("eleven_video.ui.gemini_model_selector.Prompt") as mock_prompt:
            mock_prompt.ask.return_value = "0"  # Rich default
            result = gemini_model_selector._get_user_selection(single_gemini_model)
        
        # Then: Should return None (use default model)
        assert result is None

    def test_select_last_model_in_list(self, gemini_model_selector):
        """[P2] [3.5-AUTO-009] Selecting last model in list works correctly.
        
        Boundary: Maximum valid index selection.
        """
        # Given: A GeminiModelSelector with multiple models
        models = [
            GeminiModelInfo(model_id="model-1", name="First", description="1"),
            GeminiModelInfo(model_id="model-2", name="Second", description="2"),
            GeminiModelInfo(model_id="model-3", name="Third", description="3"),
            GeminiModelInfo(model_id="last-model", name="Last", description="4"),
        ]
        
        # When: User selects last model (index 4)
        with patch("eleven_video.ui.gemini_model_selector.Prompt") as mock_prompt:
            mock_prompt.ask.return_value = "4"
            result = gemini_model_selector._get_user_selection(models)
        
        # Then: Should return the last model's ID
        assert result == "last-model"

    def test_select_model_interactive_full_flow(self, gemini_model_selector, mock_gemini_adapter, sample_gemini_models):
        """[P1] [3.5-AUTO-010] Full interactive flow works end-to-end.
        
        Integration test: List models, display, select, return model_id.
        """
        # Given: A GeminiModelSelector with working adapter
        mock_gemini_adapter.list_text_models.return_value = sample_gemini_models
        
        # When: User goes through full interactive flow
        with patch("eleven_video.ui.gemini_model_selector.console") as mock_console:
            with patch("eleven_video.ui.gemini_model_selector.Prompt") as mock_prompt:
                mock_console.is_terminal = True
                mock_prompt.ask.return_value = "2"  # Select second model
                result = gemini_model_selector.select_model_interactive()
        
        # Then: Should return second model's model_id
        assert result == sample_gemini_models[1].model_id
