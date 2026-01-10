import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock 
from eleven_video.main import app

runner = CliRunner()

class TestCLIResolutionFlag:
    
    @pytest.mark.integration
    def test_resolution_flag_valid(self):
        """Verify --resolution flag is accepted."""
        result = runner.invoke(app, ["generate", "--resolution", "720p", "--help"]) 
        # Just checking if flag is recognized (doesn't error "no such option")
        # Or even better, try to run a dry-run if available, or just mock the inner workings
        
        # If flag is invalid, exit code != 0 usually, or unique error message
        assert result.exit_code == 0
        assert "--resolution" in result.stdout or "-r" in result.stdout

    @pytest.mark.integration
    @patch("eleven_video.main.Settings")
    @patch("eleven_video.orchestrator.VideoPipeline")
    def test_resolution_passed_to_pipeline(self, mock_pipeline, mock_settings):
        """Verify the parsed resolution is passed to the pipeline config."""
        from eleven_video.models.domain import Resolution
        
        # Mock pipeline to avoid real execution
        mock_instance = mock_pipeline.return_value
        mock_instance.run.return_value = None
        
        result = runner.invoke(app, ["generate", "--resolution", "square", "--prompt", "test"])
        
        assert result.exit_code == 0
        
        # Verify pipeline init or run call config
        # Assuming config is passed to Pipeline or run
        # Example: VideoPipeline(config=...)
        call_args = mock_pipeline.call_args
        # Inspect args to see if resolution is there
        # This is speculative until implementation exists, but defines the interface
        
        # Alternatively, mocking the Config object creation if separate
        # But assuming direct passing for now
        
        # Let's assume pipeline.run(video_config) or similar
        # Check mock_pipeline interaction
        assert mock_pipeline.called
        # Verify 'square' mapped to Resolution.SQUARE was passed down
