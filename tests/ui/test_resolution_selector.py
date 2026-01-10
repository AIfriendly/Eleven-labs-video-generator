import pytest
from unittest.mock import patch, MagicMock, ANY
from eleven_video.ui.resolution_selector import ResolutionSelector
from eleven_video.models.domain import Resolution

class TestResolutionSelector:
    
    @pytest.mark.unit
    def test_resolution_enum_structure(self):
        """Verify Resolution enum has required members.
        
        Test ID: 3.8-UNIT-003
        """
        # GIVEN the Resolution enum (imported at top level)
        
        # THEN it should have the expected members
        assert hasattr(Resolution, "HD_1080P")
        assert hasattr(Resolution, "HD_720P")
        assert hasattr(Resolution, "PORTRAIT")
        assert hasattr(Resolution, "SQUARE")
        
        # AND the values should be correct
        assert Resolution.HD_1080P.value == {"width": 1920, "height": 1080, "label": "1080p (Landscape)"}

    @pytest.mark.unit
    @patch("eleven_video.ui.resolution_selector.console")
    def test_selector_interactive_prompt(self, mock_console):
        """Verify the interactive prompt offers correct options.
        
        Test ID: 3.8-UNIT-002
        """
        # GIVEN the selector in interactive mode
        # Force is_terminal to True so Prompt.ask is reached
        mock_console.is_terminal = True
        
        with patch("eleven_video.ui.resolution_selector.Prompt.ask") as mock_ask:
            # Setup mock return
            mock_ask.return_value = "1080p (Landscape)"
            
            selector = ResolutionSelector()
            
            # WHEN selecting resolution interactively
            result = selector.select_resolution(interactive=True)
            
            # THEN Prompt.ask was called with correct choices
            assert mock_ask.called
            choices = mock_ask.call_args[1].get("choices", [])
            assert "1080p (Landscape)" in choices
            assert "720p (Landscape)" in choices
            assert "Portrait (9:16)" in choices
            assert "Square (1:1)" in choices

    @pytest.mark.unit
    def test_selector_fallback_defaults(self):
        """Verify default is chosen when not interactive.
        
        Test ID: 3.8-UNIT-002 (Variant)
        """
        # GIVEN the selector
        selector = ResolutionSelector()
        
        # WHEN selecting resolution non-interactively
        result = selector.select_resolution(interactive=False)
        
        # THEN it falls back to 1080p
        assert result == Resolution.HD_1080P
