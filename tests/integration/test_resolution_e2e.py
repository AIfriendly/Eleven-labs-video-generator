import pytest
from typer.testing import CliRunner
from unittest.mock import patch, ANY, MagicMock
from eleven_video.main import app
from eleven_video.models.domain import Resolution, Video
from pathlib import Path

runner = CliRunner()

class TestResolutionE2E:
    
    @pytest.mark.integration
    @patch("eleven_video.main.Settings")
    @patch("eleven_video.api.gemini.GeminiAdapter.generate_script")
    @patch("eleven_video.api.elevenlabs.ElevenLabsAdapter.generate_speech")
    @patch("eleven_video.api.gemini.GeminiAdapter.generate_images")
    @patch("eleven_video.processing.video_handler.FFmpegVideoCompiler.compile_video")
    def test_generate_video_custom_resolution_e2e(self, mock_compile, mock_images, mock_speech, mock_script, mock_settings):
         # Setup mocks
         mock_script.return_value = MagicMock(content="script")
         mock_speech.return_value = MagicMock(data=b"audio")
         mock_images.return_value = [MagicMock(data=b"image")]
         mock_compile.return_value = Video(
             file_path=Path("out.mp4"), 
             duration_seconds=10.0, 
             file_size_bytes=100, 
             resolution=(1080, 1920) # Portrait dimensions
         )
         
         # Run CLI
         result = runner.invoke(app, ["generate", "--prompt", "test", "--resolution", "portrait"])
         
         assert result.exit_code == 0, f"CLI output: {result.stdout}"
         
         # Verify compile_video called with correct resolution
         mock_compile.assert_called_with(
             ANY, ANY, ANY, progress_callback=ANY, 
             resolution=Resolution.PORTRAIT
         )
