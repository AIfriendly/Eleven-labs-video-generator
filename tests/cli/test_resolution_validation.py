
import pytest
from typer.testing import CliRunner
from eleven_video.main import app

runner = CliRunner()

class TestResolutionValidation:
    
    @pytest.mark.integration
    def test_resolution_flag_invalid(self):
        """Verify CLI rejects invalid resolution values.
        
        Test ID: 3.8-INT-002 (AC5)
        """
        # Story 3.8 - AC5: "Given invalid resolution input ... Then the system displays an error and exits"
        
        # GIVEN the CLI
        # WHEN the user provides an invalid resolution flag
        result = runner.invoke(app, ["generate", "--resolution", "invalid_res", "--prompt", "test"])
        
        # THEN the command fails
        assert result.exit_code != 0
        
        # AND an appropriate error message is displayed
        assert "Invalid resolution" in result.stdout
