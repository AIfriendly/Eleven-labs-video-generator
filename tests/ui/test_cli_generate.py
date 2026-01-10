"""
Tests for CLI 'generate' command (Story 2.6, Story 3.4, Story 3.5).

Story 2.6: Interactive video generation command
Story 3.4: Interactive image model selection prompts (--image-model flag)
Story 3.5: Interactive Gemini model selection prompts (--gemini-model flag)
"""
import pytest
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from eleven_video.main import app
from eleven_video.models.domain import Resolution

runner = CliRunner()

@pytest.fixture
def mock_pipeline():
    with patch("eleven_video.orchestrator.VideoPipeline") as MockPipeline:
        pipeline_instance = MockPipeline.return_value
        yield pipeline_instance

@pytest.fixture
def mock_ui_selectors():
    """Mock all UI selector components to prevent them from being invoked during tests."""
    with patch("eleven_video.ui.resolution_selector.ResolutionSelector") as MockResSelector, \
         patch("eleven_video.ui.duration_selector.DurationSelector") as MockDurSelector, \
         patch("eleven_video.ui.voice_selector.VoiceSelector") as MockVoiceSelector, \
         patch("eleven_video.ui.image_model_selector.ImageModelSelector") as MockImageSelector, \
         patch("eleven_video.ui.gemini_model_selector.GeminiModelSelector") as MockGeminiSelector:
        
        # Configure resolution selector to return HD_1080P by default
        mock_res_instance = MockResSelector.return_value
        mock_res_instance.select_resolution.return_value = Resolution.HD_1080P
        
        yield {
            "resolution": MockResSelector,
            "duration": MockDurSelector,
            "voice": MockVoiceSelector,
            "image": MockImageSelector,
            "gemini": MockGeminiSelector
        }

def test_cli_generate_interactive(mock_pipeline, mock_ui_selectors):
    """
    [P1] [2.6-CLI-001] Interactive prompt test.
    
    GIVEN no args provided
    WHEN generate command run
    THEN it prompts for topic and runs pipeline
    """
    result = runner.invoke(app, ["generate"], input="Test Topic\n")
    
    assert result.exit_code == 0
    assert "Enter your video topic" in result.stdout
    # Story 3.5: generate() now takes gemini_model_id parameter
    # Story 3.6: generate() now takes duration_minutes parameter (defaults to 5 in interactive mode)
    # Story 3.8: generate() now takes resolution parameter (defaults to HD_1080P)
    mock_pipeline.generate.assert_called_once_with(prompt="Test Topic", voice_id=None, image_model_id=None, gemini_model_id=None, duration_minutes=5, resolution=Resolution.HD_1080P)

def test_cli_generate_with_args(mock_pipeline, mock_ui_selectors):
    """
    [P1] [2.6-CLI-002] Args passthrough test.
    
    GIVEN args provided
    WHEN generate command run
    THEN pipeline runs with those args
    """
    result = runner.invoke(app, ["generate", "--prompt", "My Topic", "--voice", "voice_123"])
    
    assert result.exit_code == 0
    # Story 3.5: generate() now takes gemini_model_id parameter
    # Story 3.6: generate() now takes duration_minutes parameter
    # Story 3.8: generate() now takes resolution parameter (defaults to HD_1080P)
    mock_pipeline.generate.assert_called_once_with(prompt="My Topic", voice_id="voice_123", image_model_id=None, gemini_model_id=None, duration_minutes=None, resolution=Resolution.HD_1080P)


def test_cli_generate_with_image_model_flag(mock_pipeline, mock_ui_selectors):
    """
    [P1] [3.4-CLI-001] Image model flag test.
    
    GIVEN --image-model flag provided
    WHEN generate command run
    THEN image model prompt is skipped and model_id is passed to pipeline
    """
    result = runner.invoke(app, [
        "generate", 
        "--prompt", "My Topic", 
        "--image-model", "gemini-3-flash"
    ])
    
    assert result.exit_code == 0
    # Story 3.5: image_model_id should be passed through when flag is provided
    # Story 3.6: generate() now takes duration_minutes parameter
    # Story 3.8: generate() now takes resolution parameter (defaults to HD_1080P)
    mock_pipeline.generate.assert_called_once_with(
        prompt="My Topic", 
        voice_id=None, 
        image_model_id="gemini-3-flash",
        gemini_model_id=None,
        duration_minutes=None,
        resolution=Resolution.HD_1080P
    )


def test_cli_generate_with_gemini_model_flag(mock_pipeline, mock_ui_selectors):
    """
    [P1] [Story 3.5 AC#5] GIVEN --gemini-model flag provided
    WHEN generate command run
    THEN Gemini model prompt is skipped and model_id is passed to pipeline
    """
    result = runner.invoke(app, [
        "generate", 
        "--prompt", "My Topic", 
        "--gemini-model", "gemini-2.5-pro"
    ])
    
    assert result.exit_code == 0
    # Story 3.5: gemini_model_id should be passed through when flag is provided
    # Story 3.6: generate() now takes duration_minutes parameter
    # Story 3.8: generate() now takes resolution parameter (defaults to HD_1080P)
    mock_pipeline.generate.assert_called_once_with(
        prompt="My Topic", 
        voice_id=None, 
        image_model_id=None,
        gemini_model_id="gemini-2.5-pro",
        duration_minutes=None,
        resolution=Resolution.HD_1080P
    )


def test_cli_generate_with_all_model_flags(mock_pipeline, mock_ui_selectors):
    """
    [P2] [Story 3.4, 3.5] GIVEN both model flags provided
    WHEN generate command run
    THEN both model IDs are passed to pipeline
    """
    result = runner.invoke(app, [
        "generate", 
        "--prompt", "My Topic", 
        "--voice", "voice-123",
        "--image-model", "gemini-3-flash",
        "--gemini-model", "gemini-2.5-pro"
    ])
    
    assert result.exit_code == 0
    # Story 3.6: generate() now takes duration_minutes parameter
    # Story 3.8: generate() now takes resolution parameter (defaults to HD_1080P)
    mock_pipeline.generate.assert_called_once_with(
        prompt="My Topic", 
        voice_id="voice-123", 
        image_model_id="gemini-3-flash",
        gemini_model_id="gemini-2.5-pro",
        duration_minutes=None,
        resolution=Resolution.HD_1080P
    )
