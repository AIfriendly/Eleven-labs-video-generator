
import pytest
from unittest.mock import MagicMock, patch, ANY
from pathlib import Path
from eleven_video.processing.video_handler import FFmpegVideoCompiler
from eleven_video.models.domain import Resolution
from tests.support.factories.media_factory import create_image, create_audio

class TestFFmpegResolution:
    
    @pytest.fixture
    def mock_moviepy(self):
        with patch("eleven_video.processing.video_handler.ImageClip") as mock_img, \
             patch("eleven_video.processing.video_handler.AudioFileClip") as mock_audio, \
             patch("eleven_video.processing.video_handler.concatenate_videoclips") as mock_concat:
            
            # Setup mock chain for clips
            mock_clip = MagicMock()
            mock_img.return_value = mock_clip
            mock_clip.with_duration.return_value = mock_clip
            mock_clip.resized.return_value = mock_clip
            mock_clip.fl.return_value = mock_clip # for zoom
            
            mock_concat.return_value = mock_clip
            mock_clip.with_audio.return_value = mock_clip
            
            yield {
                "ImageClip": mock_img,
                "AudioFileClip": mock_audio,
                "concatenate_videoclips": mock_concat,
                "clip": mock_clip
            }

    @pytest.mark.unit
    def test_video_compiler_resolution_variants(self, mock_moviepy):
        """Verify compile_video handles all resolution variants correctly (no zoom).
        
        Test ID: 3.8-UNIT-001
        """
        # GIVEN a compiler and input media
        compiler = FFmpegVideoCompiler()
        images = [create_image()]
        audio = create_audio()
        output = Path("out.mp4")
        
        test_cases = [
            (Resolution.HD_720P, (1280, 720)),
            (Resolution.PORTRAIT, (1080, 1920)),
            (Resolution.SQUARE, (1080, 1080)),
            (Resolution.HD_1080P, (1920, 1080))
        ]
        
        for res_enum, expected_size in test_cases:
            # WHEN compiling video with a specific resolution
            compiler.compile_video(
                images=images, 
                audio=audio, 
                output_path=output,
                resolution=res_enum,
                enable_zoom=False
            )
            
            # THEN the clip is resized to the expected dimensions
            # Use ANY for newsize if called multiple times, but here we want specific
            # mock_moviepy["clip"] is reused, so check latest call
            mock_moviepy["clip"].resized.assert_called_with(newsize=expected_size)

    @pytest.mark.unit
    def test_ffmpeg_zoom_uses_resolution(self, mock_moviepy):
        """Verify zoom effect uses target resolution.
        
        Test ID: 3.8-UNIT-001 (Variant)
        """
        # GIVEN a compiler with zoom enabled
        compiler = FFmpegVideoCompiler()
        images = [create_image()]
        audio = create_audio()
        output = Path("out.mp4")
        
        with patch.object(compiler, "_apply_zoom_effect") as mock_zoom:
            mock_zoom.return_value = mock_moviepy["clip"]
            
            # WHEN compiling in Portrait mode
            compiler.compile_video(
                images=images, 
                audio=audio, 
                output_path=output,
                resolution=Resolution.PORTRAIT,
                enable_zoom=True
            )
            
            # THEN zoom is applied with Portrait dimensions
            mock_zoom.assert_called_with(ANY, ANY, (1080, 1920))
            
            # WHEN compiling in Square mode
            compiler.compile_video(
                images=images, 
                audio=audio, 
                output_path=output,
                resolution=Resolution.SQUARE,
                enable_zoom=True
            )
            
            # THEN zoom is applied with Square dimensions
            mock_zoom.assert_called_with(ANY, ANY, (1080, 1080))

    @pytest.mark.unit
    def test_default_resolution(self, mock_moviepy):
        """Verify defaults to 1080p if None passed."""
        # GIVEN a compiler with no resolution specified
        compiler = FFmpegVideoCompiler()
        images = [create_image()]
        audio = create_audio()
        output = Path("out.mp4")
        
        # WHEN compiling video
        compiler.compile_video(
            images=images, 
            audio=audio, 
            output_path=output,
            resolution=None,
            enable_zoom=False
        )
        
        # THEN it defaults to 1080p (1920x1080)
        mock_moviepy["clip"].resized.assert_called_with(newsize=(1920, 1080))

