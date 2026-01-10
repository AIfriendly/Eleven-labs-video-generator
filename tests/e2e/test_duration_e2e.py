"""
E2E Test to verify the Video Duration Selection feature interaction.
"""
import pytest
from typer.testing import CliRunner
from unittest.mock import MagicMock, ANY
from pathlib import Path

from eleven_video.main import app
from eleven_video.models.domain import Resolution
from tests.fixtures.api_fixtures import mock_all_apis  # Use the shared offline fixtures

runner = CliRunner()


@pytest.fixture
def mock_pipeline_spy(mocker):
    """
    Patches VideoPipeline in main.py to spy on its usage, 
    while preventing actual execution.
    """
    # Create a mock instance that will be returned by the constructor
    mock_instance = MagicMock()
    # Ensure generate returns a dummy valid response so CLI checks pass (e.g. file_path access)
    mock_instance.generate.return_value.file_path = Path("output/video.mp4")
    
    # Patch the CLASS at the source, because main.py imports it locally inside the function
    # from eleven_video.orchestrator import VideoPipeline
    mock_class = mocker.patch("eleven_video.orchestrator.VideoPipeline", return_value=mock_instance)
    
    # Patch Settings to avoid ConfigurationError
    mock_settings = MagicMock()
    mock_settings.elevenlabs_api_key.get_secret_value.return_value = "clean_mock_key"
    mock_settings.gemini_api_key.get_secret_value.return_value = "clean_mock_key"
    mocker.patch("eleven_video.main.Settings", return_value=mock_settings)
    
    return mock_instance

def test_generate_command_with_duration(mock_pipeline_spy, mock_all_apis):
    """
    [P0] [3.6-E2E-001] Test the full 'generate' command flow with the --duration flag.
    """
    # Run Command
    result = runner.invoke(app, [
        "generate", 
        "--prompt", "Test Video Topic", 
        "--duration", "3",
        "--duration", "3",
        "--voice", "21m00Tcm4TlvDq8ikWAM", # Rachel
        "--gemini-model", "models/gemini-2.5-flash",
        "--image-model", "dummy_image_model",
    ])
    
    # Assertions
    if result.exit_code != 0:
        print("\nCOMMAND OUTPUT:\n", result.stdout)
        print("EXCEPTION:", result.exception)
    assert result.exit_code == 0, "Command failed"
    
    # Verify the pipeline generate was called with correct duration
    mock_pipeline_spy.generate.assert_called_with(
        prompt="Test Video Topic",
        voice_id="21m00Tcm4TlvDq8ikWAM",
        image_model_id="dummy_image_model",
        gemini_model_id="models/gemini-2.5-flash",
        duration_minutes=3,
        resolution=Resolution.HD_1080P
    )

