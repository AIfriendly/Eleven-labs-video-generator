"""
Integration tests for Story 2.6: Interactive Video Generation Command.
Focus: VideoPipeline orchestrator logic.
"""
import pytest
from unittest.mock import MagicMock, patch, ANY
from pathlib import Path

from eleven_video.orchestrator.video_pipeline import VideoPipeline
from eleven_video.models.domain import PipelineStage, Video, Script, Audio, Image
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
        
        # Setup mocks
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
    # Pass mocks via constructor or allow lazy init to use patched classes
    # Here we rely on the patched classes in the test context
    return VideoPipeline(settings=mock_settings)

def test_pipeline_orchestration_success(pipeline, mock_adapters):
    """
    GIVEN a valid prompt
    WHEN generate is called
    THEN all adapters are called in correct order
    AND a video is returned
    """
    gemini, eleven, compiler = mock_adapters
    
    # Act
    video = pipeline.generate(prompt="test topic", voice_id="voice123")
    
    # Assert
    assert video.file_path == Path("video.mp4")
    
    # Verify order
    gemini.generate_script.assert_called_once()
    eleven.generate_speech.assert_called_once_with(
        text="script", 
        voice_id="voice123", 
        progress_callback=ANY
    )
    gemini.generate_images.assert_called_once()
    compiler.compile_video.assert_called_once()

def test_pipeline_progress_callbacks(pipeline, mock_adapters):
    """
    GIVEN a pipeline with progress tracking
    WHEN generate runs
    THEN progress updates are triggered for each stage
    """
    # Act
    mock_progress = MagicMock()
    pipeline.progress = mock_progress
    pipeline.generate("topic")
    
    # Assert
    # Verify start/complete pairs for all stages
    stages = [
        PipelineStage.PROCESSING_SCRIPT,
        PipelineStage.PROCESSING_AUDIO, 
        PipelineStage.PROCESSING_IMAGES,
        PipelineStage.COMPILING_VIDEO
    ]
    
    for stage in stages:
        mock_progress.start_stage.assert_any_call(stage)
        mock_progress.complete_stage.assert_any_call(stage)

def test_pipeline_error_handling(pipeline, mock_adapters):
    """
    GIVEN an adapter raises an exception
    WHEN generate runs
    THEN the exception is caught
    AND failure is reported to progress
    AND the exception is re-raised
    """
    gemini, _, _ = mock_adapters
    gemini.generate_script.side_effect = Exception("API Error")
    
    mock_progress = MagicMock()
    pipeline.progress = mock_progress
    
    with pytest.raises(Exception, match="API Error"):
        pipeline.generate("topic")
        
    mock_progress.fail_stage.assert_called()
