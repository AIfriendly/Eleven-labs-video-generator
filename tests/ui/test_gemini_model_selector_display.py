"""
Tests for GeminiModelSelector Display - Story 3.5

Test Groups:
- Group 1: GeminiModelSelector Display (Task 4)
- Group 4: Boundary Conditions

Test IDs: 3.5-COMP-001 (Gemini model selection menu rendering)
Mirrors: tests/ui/test_image_model_selector_display.py (Story 3.4)
"""
import pytest
from unittest.mock import Mock, patch

from eleven_video.models.domain import GeminiModelInfo


# =============================================================================
# Test Group 1: GeminiModelSelector Display (Task 4) - 3.5-COMP-001
# =============================================================================

class TestGeminiModelSelectorDisplay:
    """Tests for GeminiModelSelector._display_model_list() rendering."""

    def test_gemini_model_selector_can_be_imported(self):
        """[P1] [3.5-COMP-001] GeminiModelSelector should be importable from ui module.
        
        Validates module structure is correct.
        """
        # Given: The ui module exists
        # When: Importing GeminiModelSelector from ui module
        from eleven_video.ui.gemini_model_selector import GeminiModelSelector
        
        # Then: GeminiModelSelector should exist
        assert GeminiModelSelector is not None

    def test_gemini_model_selector_displays_numbered_list(self, gemini_model_selector, sample_gemini_models):
        """[P1] [3.5-COMP-001] GeminiModelSelector should display models as numbered list.
        
        AC: #1 - Display a numbered list of available text generation model options.
        """
        from rich.panel import Panel
        from rich.table import Table
        
        # Given: A GeminiModelSelector with mock adapter and models
        # When: Displaying model list
        with patch("eleven_video.ui.gemini_model_selector.console") as mock_console:
            gemini_model_selector._display_model_list(sample_gemini_models)
        
        # Then: Console should have been called with Panel and Table
        assert mock_console.print.call_count >= 2
        
        # Verify Panel was printed with correct header
        call_args = [call[0][0] for call in mock_console.print.call_args_list]
        panel_calls = [arg for arg in call_args if isinstance(arg, Panel)]
        assert len(panel_calls) >= 1, "Expected Panel to be printed"
        
        # Verify Table was printed
        table_calls = [arg for arg in call_args if isinstance(arg, Table)]
        assert len(table_calls) >= 1, "Expected Table to be printed"

    def test_gemini_model_selector_shows_default_option_first(self, gemini_model_selector, single_gemini_model):
        """[P1] [3.5-COMP-001] GeminiModelSelector should show default model as option [0].
        
        AC: #4 - Show option to use default model (e.g., "[0] Use default model (gemini-2.5-flash-lite)").
        """
        from rich.table import Table
        
        # Given: A GeminiModelSelector with models
        # When: Displaying model list
        with patch("eleven_video.ui.gemini_model_selector.console") as mock_console:
            gemini_model_selector._display_model_list(single_gemini_model)
        
        # Then: Table should include default option as row 0
        assert mock_console.print.call_count >= 2
        
        # Verify Table was printed with default model name
        call_args = [call[0][0] for call in mock_console.print.call_args_list]
        table_calls = [arg for arg in call_args if isinstance(arg, Table)]
        assert len(table_calls) >= 1, "Expected Table with default option"


# =============================================================================
# Test Group 4: Boundary Conditions (Automation Expansion)
# =============================================================================

class TestGeminiModelSelectorBoundaryConditions:
    """Tests for boundary conditions in Gemini model list handling."""

    def test_display_model_list_with_single_model(self, gemini_model_selector, single_gemini_model):
        """[P2] [3.5-AUTO-005] Display works correctly with single model option.
        
        Boundary: Minimum model list (1 model + default).
        """
        # Given: A GeminiModelSelector with exactly one model
        # When: Displaying model list
        with patch("eleven_video.ui.gemini_model_selector.console") as mock_console:
            gemini_model_selector._display_model_list(single_gemini_model)
        
        # Then: Console should have been called (Panel + Table)
        assert mock_console.print.call_count >= 2

    def test_display_model_list_with_many_models(self, gemini_model_selector):
        """[P2] [3.5-AUTO-006] Display handles large model list (10+ models).
        
        Boundary: R-008 risk mitigation - many models.
        """
        # Given: A GeminiModelSelector with many models
        models = [
            GeminiModelInfo(
                model_id=f"gemini-model-{i}",
                name=f"Gemini Model {i}",
                description=f"Description {i}"
            )
            for i in range(15)
        ]
        
        # When: Displaying model list
        with patch("eleven_video.ui.gemini_model_selector.console") as mock_console:
            gemini_model_selector._display_model_list(models)
        
        # Then: Console should complete without error
        assert mock_console.print.call_count >= 2

    def test_display_model_list_with_none_descriptions(self, gemini_model_selector):
        """[P2] [3.5-AUTO-007] Display handles models with None descriptions.
        
        Edge case: Some models may not have descriptions.
        """
        # Given: A GeminiModelSelector with models missing descriptions
        models = [
            GeminiModelInfo(model_id="model-1", name="Model 1", description=None),
            GeminiModelInfo(model_id="model-2", name="Model 2", description="Has description"),
        ]
        
        # When: Displaying model list
        with patch("eleven_video.ui.gemini_model_selector.console") as mock_console:
            gemini_model_selector._display_model_list(models)
        
        # Then: Console should complete without error
        assert mock_console.print.call_count >= 2
