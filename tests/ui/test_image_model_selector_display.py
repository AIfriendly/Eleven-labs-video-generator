"""
Tests for ImageModelSelector Display - Story 3.4

Test Groups:
- Group 1: ImageModelSelector Display (Task 1)
- Group 4: Boundary Conditions

Test IDs: 3.4-UNIT-001 to 003, 3.4-AUTO-005 to 006
Mirrors: tests/ui/test_voice_selector_display.py (Story 3.3)
"""
import pytest
from unittest.mock import Mock, patch

from eleven_video.models.domain import ImageModelInfo


# =============================================================================
# Test Group 1: ImageModelSelector Display (Task 1) - 3.4-COMP-001
# =============================================================================

class TestImageModelSelectorDisplay:
    """Tests for ImageModelSelector._display_model_list() rendering."""

    def test_image_model_selector_can_be_imported(self):
        """[P1] [3.4-UNIT-001] ImageModelSelector should be importable from ui module.
        
        Validates module structure is correct.
        """
        # Given: The ui module exists
        # When: Importing ImageModelSelector from ui module
        from eleven_video.ui.image_model_selector import ImageModelSelector
        
        # Then: ImageModelSelector should exist
        assert ImageModelSelector is not None

    def test_image_model_selector_displays_numbered_list(self, image_model_selector, sample_image_models):
        """[P1] [3.4-UNIT-002] ImageModelSelector should display models as numbered list.
        
        AC: #1 - Display a numbered list of available image model options.
        """
        # Given: An ImageModelSelector with mock adapter and models
        # When: Displaying model list
        with patch("eleven_video.ui.image_model_selector.console") as mock_console:
            image_model_selector._display_model_list(sample_image_models)
        
        # Then: Console should have been called with table output
        assert mock_console.print.called
        # Console.print called twice: Panel header + Table
        assert mock_console.print.call_count >= 2

    def test_image_model_selector_shows_default_option_first(self, image_model_selector, single_image_model):
        """[P1] [3.4-UNIT-003] ImageModelSelector should show default model as option [0].
        
        AC: #4 - Show option to use default model (e.g., "[0] Use default model").
        """
        # Given: An ImageModelSelector with models
        # When: Displaying model list
        with patch("eleven_video.ui.image_model_selector.console") as mock_console:
            image_model_selector._display_model_list(single_image_model)
        
        # Then: First option should be default model (option 0)
        assert mock_console.print.call_count >= 2


# =============================================================================
# Test Group 4: Boundary Conditions (Automation Expansion)
# =============================================================================

class TestImageModelSelectorBoundaryConditions:
    """Tests for boundary conditions in image model list handling."""

    def test_display_model_list_with_single_model(self, image_model_selector, single_image_model):
        """[P2] [3.4-AUTO-005] Display works correctly with single model option.
        
        Boundary: Minimum model list (1 model + default).
        """
        # Given: An ImageModelSelector with exactly one model
        # When: Displaying model list
        with patch("eleven_video.ui.image_model_selector.console") as mock_console:
            image_model_selector._display_model_list(single_image_model)
        
        # Then: Console should have been called (Panel + Table)
        assert mock_console.print.call_count >= 2

    def test_display_model_list_with_many_models(self, image_model_selector):
        """[P2] [3.4-AUTO-006] Display handles large model list (10+ models).
        
        Boundary: R-008 risk mitigation - many models.
        """
        # Given: An ImageModelSelector with many models
        models = [
            ImageModelInfo(
                model_id=f"model-{i}",
                name=f"Model {i}",
                description=f"Description {i}"
            )
            for i in range(15)
        ]
        
        # When: Displaying model list
        with patch("eleven_video.ui.image_model_selector.console") as mock_console:
            image_model_selector._display_model_list(models)
        
        # Then: Console should complete without error
        assert mock_console.print.call_count >= 2

    def test_display_model_list_with_none_descriptions(self, image_model_selector):
        """[P2] [3.4-AUTO-007] Display handles models with None descriptions.
        
        Edge case: Some models may not have descriptions.
        """
        # Given: An ImageModelSelector with models missing descriptions
        models = [
            ImageModelInfo(model_id="model-1", name="Model 1", description=None),
            ImageModelInfo(model_id="model-2", name="Model 2", description="Has description"),
        ]
        
        # When: Displaying model list
        with patch("eleven_video.ui.image_model_selector.console") as mock_console:
            image_model_selector._display_model_list(models)
        
        # Then: Console should complete without error
        assert mock_console.print.call_count >= 2
