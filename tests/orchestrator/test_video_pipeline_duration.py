"""
Integration tests for Story 3.6: Video Duration Logic in Pipeline.
"""
import pytest
from unittest.mock import MagicMock, patch, ANY
from pathlib import Path

from eleven_video.orchestrator.video_pipeline import VideoPipeline
from eleven_video.models.domain import Script, Audio, Image, Video
from eleven_video.config import Settings

@pytest.fixture
def mock_settings():
    return Settings(
        elevenlabs_api_key="test_key",
        gemini_api_key="test_key",
        project_root="/tmp",
        output_dir="/tmp/output"
    )

@pytest.fixture
def mock_adapters():
    with patch("eleven_video.orchestrator.video_pipeline.GeminiAdapter") as MockGemini, \
         patch("eleven_video.orchestrator.video_pipeline.ElevenLabsAdapter") as MockEleven, \
         patch("eleven_video.orchestrator.video_pipeline.FFmpegVideoCompiler") as MockCompiler:
        
        gemini = MockGemini.return_value
        eleven = MockEleven.return_value
        compiler = MockCompiler.return_value
        
        # Default behaviors
        gemini.generate_script.return_value = Script(content="script")
        gemini.generate_images.return_value = [Image(data=b"img", mime_type="image/png")]
        eleven.generate_speech.return_value = Audio(data=b"audio", duration_seconds=10.0)
        compiler.compile_video.return_value = Video(file_path=Path("video.mp4"), duration_seconds=10.0, file_size_bytes=1024)
        
        yield gemini, eleven, compiler

@pytest.fixture
def pipeline(mock_settings):
    return VideoPipeline(settings=mock_settings)

def test_pipeline_propagates_duration_parameter(pipeline, mock_adapters):
    """
    [P0] [3.6-INT-001] Propagates duration parameter to adapters.
    
    GIVEN a duration_minutes argument
    WHEN generate is called
    THEN the duration is passed effectively to generate_script
    AND target_image_count is calculated and passed to generate_images
    """
    gemini, _, _ = mock_adapters
    duration = 5
    
    # Act
    pipeline.generate("topic", duration_minutes=duration)
    
    # Assert
    # 1. duration passed to script generation
    gemini.generate_script.assert_called_with(
        "topic", 
        progress_callback=ANY, 
        model_id=None,
        duration_minutes=duration # Crucial check
    )
    
    # 2. image count calculated (5 * 15 = 75) and passed
    expected_image_count = 5 * 15
    gemini.generate_images.assert_called_with(
        ANY, # script object
        progress_callback=ANY,
        model_id=None,
        target_image_count=expected_image_count # Crucial check
    )

def test_pipeline_calculates_correct_image_counts(pipeline, mock_adapters):
    """
    [P1] [3.6-INT-002] Verify image count calculation for different durations.
    """
    gemini, _, _ = mock_adapters
    
    test_cases = [
        (3, 45),
        (5, 75),
        (10, 150)
    ]
    
    for duration, expected_count in test_cases:
        pipeline.generate("topic", duration_minutes=duration)
        
        # Verify the most recent call arg for target_image_count
        call_args = gemini.generate_images.call_args
        assert call_args.kwargs['target_image_count'] == expected_count

def test_pipeline_handles_none_duration(pipeline, mock_adapters):
    """
    [P1] [3.6-INT-003] Handle None duration gracefully.

    GIVEN duration_minutes is None
    WHEN generate is called
    THEN None is passed to script generation (it has its own default)
    AND target_image_count is None (default behavior)
    """
    gemini, _, _ = mock_adapters
    
    pipeline.generate("topic", duration_minutes=None)
    
    gemini.generate_script.assert_called_with(
        "topic", 
        progress_callback=ANY, 
        model_id=None,
        duration_minutes=None
    )
    
    gemini.generate_images.assert_called_with(
        ANY,
        progress_callback=ANY,
        model_id=None,
        target_image_count=None
    )
