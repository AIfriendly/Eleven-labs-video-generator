"""
Tests for CLI 'generate' command (Story 2.6).
"""
import pytest
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from eleven_video.main import app

runner = CliRunner()

@pytest.fixture
def mock_pipeline():
    with patch("eleven_video.orchestrator.VideoPipeline") as MockPipeline:
        pipeline_instance = MockPipeline.return_value
        yield pipeline_instance

def test_cli_generate_interactive(mock_pipeline):
    """
    GIVEN no args provided
    WHEN generate command run
    THEN it prompts for topic and runs pipeline
    """
    result = runner.invoke(app, ["generate"], input="Test Topic\n")
    
    assert result.exit_code == 0
    assert "Enter your video topic" in result.stdout
    mock_pipeline.generate.assert_called_once_with(prompt="Test Topic", voice_id=None)

def test_cli_generate_with_args(mock_pipeline):
    """
    GIVEN args provided
    WHEN generate command run
    THEN pipeline runs with those args
    """
    result = runner.invoke(app, ["generate", "--prompt", "My Topic", "--voice", "voice_123"])
    
    assert result.exit_code == 0
    mock_pipeline.generate.assert_called_once_with(prompt="My Topic", voice_id="voice_123")
