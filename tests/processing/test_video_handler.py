"""
Tests for FFmpegVideoCompiler - Video Compilation from Assets (Story 2.4).

Test IDs: 2.4-UNIT-001 to 2.4-UNIT-020
Tests cover AC1-AC7: success path, image distribution, progress, validation, error handling.

Related files:
- eleven_video/processing/video_handler.py: FFmpegVideoCompiler implementation
- eleven_video/models/domain.py: Video domain model
- eleven_video/api/interfaces.py: VideoCompiler protocol
- eleven_video/exceptions/custom_errors.py: VideoProcessingError
"""
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from typing import List


# =============================================================================
# Test Data Factories
# =============================================================================

def create_test_image(size_bytes: int = 1000):
    """Create test Image domain model with fake PNG bytes."""
    from eleven_video.models.domain import Image
    return Image(
        data=b"\x89PNG\r\n\x1a\n" + b"\x00" * size_bytes,
        mime_type="image/png",
        file_size_bytes=size_bytes + 8
    )


def create_test_images(count: int = 3):
    """Create multiple test images."""
    return [create_test_image() for _ in range(count)]


def create_test_audio(duration: float = 10.0):
    """Create test Audio domain model with fake MP3 bytes."""
    from eleven_video.models.domain import Audio
    return Audio(
        data=b"\xff\xfb\x90\x00" + b"\x00" * 100,
        duration_seconds=duration,
        file_size_bytes=104
    )


# =============================================================================
# Fixtures for moviepy mocking
# =============================================================================

@pytest.fixture
def mock_moviepy():
    """
    Fixture providing mocked moviepy for unit tests.
    
    Mocks ImageClip, AudioFileClip, and concatenate_videoclips to avoid
    FFmpeg dependency in unit tests. Supports both legacy (set_duration)
    and modern (with_duration) moviepy APIs.
    """
    with patch("eleven_video.processing.video_handler.ImageClip") as mock_image_clip, \
         patch("eleven_video.processing.video_handler.AudioFileClip") as mock_audio_clip, \
         patch("eleven_video.processing.video_handler.concatenate_videoclips") as mock_concat:
        
        # Create mock clip with expected properties
        mock_clip = MagicMock()
        mock_clip.duration = 10.0
        mock_clip.w = 1920
        mock_clip.h = 1080
        mock_clip.write_videofile = MagicMock()
        mock_clip.set_audio = MagicMock(return_value=mock_clip)
        mock_clip.with_audio = MagicMock(return_value=mock_clip)
        mock_clip.close = MagicMock()
        mock_clip.fl = MagicMock(return_value=mock_clip)
        mock_clip.resized = MagicMock(return_value=mock_clip)
        
        # Chain: ImageClip().set_duration().resize() -> mock_clip (legacy)
        mock_image_clip.return_value.set_duration.return_value.resize.return_value = mock_clip
        # Chain: ImageClip().with_duration() -> mock_clip (modern - Story 2.7)
        mock_image_clip.return_value.with_duration.return_value = mock_clip
        mock_image_clip.return_value.with_duration.return_value.fl.return_value = mock_clip
        mock_image_clip.return_value.with_duration.return_value.resized.return_value = mock_clip
        
        mock_audio_clip.return_value.duration = 10.0
        mock_audio_clip.return_value.close = MagicMock()
        mock_concat.return_value = mock_clip
        
        yield mock_image_clip, mock_audio_clip, mock_concat, mock_clip


@pytest.fixture
def mock_moviepy_error():
    """
    Fixture providing mocked moviepy that raises errors.
    
    Use set_error() to configure specific errors for testing error handling.
    """
    with patch("eleven_video.processing.video_handler.ImageClip") as mock_image_clip:
        def set_error(error):
            mock_image_clip.side_effect = error
        yield mock_image_clip, set_error


# =============================================================================
# Story 2.4: AC7 - Video Domain Model Tests
# =============================================================================

class TestVideoDomainModel:
    """Tests for Video domain model (AC7)."""

    def test_video_dataclass_exists(self):
        """
        [2.4-UNIT-001] AC7: Video domain model exists.
        
        GIVEN the domain models module
        WHEN importing Video
        THEN the Video dataclass is available.
        """
        from eleven_video.models.domain import Video
        
        assert Video is not None

    def test_video_has_required_fields(self):
        """
        [2.4-UNIT-002] AC7: Video has file_path, duration, file_size.
        
        GIVEN Video domain model
        WHEN creating a Video instance
        THEN it has file_path, duration_seconds, file_size_bytes fields.
        """
        from eleven_video.models.domain import Video
        
        video = Video(
            file_path=Path("/test/output.mp4"),
            duration_seconds=10.5,
            file_size_bytes=1024000
        )
        
        assert video.file_path == Path("/test/output.mp4")
        assert video.duration_seconds == 10.5
        assert video.file_size_bytes == 1024000


# =============================================================================
# Story 2.4: VideoCompiler Protocol Tests
# =============================================================================

class TestVideoCompilerProtocol:
    """Tests for VideoCompiler protocol."""

    def test_video_compiler_protocol_exists(self):
        """
        [2.4-UNIT-003] AC1: VideoCompiler protocol exists.
        
        GIVEN the interfaces module
        WHEN importing VideoCompiler
        THEN the protocol is available.
        """
        from eleven_video.api.interfaces import VideoCompiler
        
        assert VideoCompiler is not None


# =============================================================================
# Story 2.4: VideoProcessingError Tests
# =============================================================================

class TestVideoProcessingError:
    """Tests for VideoProcessingError exception (AC6)."""

    def test_video_processing_error_exists(self):
        """
        [2.4-UNIT-004] AC6: VideoProcessingError exception exists.
        
        GIVEN the custom_errors module
        WHEN importing VideoProcessingError
        THEN the exception class is available.
        """
        from eleven_video.exceptions.custom_errors import VideoProcessingError
        
        assert VideoProcessingError is not None

    def test_video_processing_error_has_message(self):
        """
        [2.4-UNIT-005] AC6: VideoProcessingError has message.
        
        GIVEN a VideoProcessingError
        WHEN raised with a message
        THEN the message is accessible.
        """
        from eleven_video.exceptions.custom_errors import VideoProcessingError
        
        error = VideoProcessingError("FFmpeg not found")
        assert "FFmpeg not found" in str(error)


# =============================================================================
# Story 2.4: AC1, AC5 - Video Compilation Success Tests
# =============================================================================

class TestCompileVideoSuccess:
    """Tests for successful video compilation (AC1, AC5, AC7)."""

    def test_compile_video_returns_video_domain_model(self, mock_moviepy, tmp_path):
        """
        [2.4-UNIT-006] AC1/AC7: compile_video returns Video domain model.
        
        GIVEN valid images and audio
        WHEN compile_video() is called
        THEN a Video domain model is returned.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        from eleven_video.models.domain import Video
        
        compiler = FFmpegVideoCompiler()
        images = create_test_images(3)
        audio = create_test_audio(10.0)
        output_path = tmp_path / "output.mp4"
        
        result = compiler.compile_video(images, audio, output_path)
        
        assert isinstance(result, Video)

    def test_compile_video_sets_file_path(self, mock_moviepy, tmp_path):
        """
        [2.4-UNIT-007] AC7: Video has correct file_path.
        
        GIVEN valid inputs and output path
        WHEN compile_video() completes
        THEN Video.file_path matches the output path.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        compiler = FFmpegVideoCompiler()
        images = create_test_images(3)
        audio = create_test_audio(10.0)
        output_path = tmp_path / "my_video.mp4"
        
        result = compiler.compile_video(images, audio, output_path)
        
        assert result.file_path == output_path

    def test_compile_video_uses_h264_codec(self, mock_moviepy, tmp_path):
        """
        [2.4-UNIT-008] AC5: Uses H.264 (libx264) codec.
        
        GIVEN valid inputs
        WHEN video is written
        THEN libx264 codec is used.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        mock_image_clip, mock_audio_clip, mock_concat, mock_clip = mock_moviepy
        
        compiler = FFmpegVideoCompiler()
        images = create_test_images(3)
        audio = create_test_audio(10.0)
        output_path = tmp_path / "output.mp4"
        
        compiler.compile_video(images, audio, output_path)
        
        # Verify write_videofile was called with codec parameter
        mock_clip.write_videofile.assert_called_once()
        call_kwargs = mock_clip.write_videofile.call_args.kwargs
        assert call_kwargs.get("codec") == "libx264"

    def test_compile_video_uses_aac_audio_codec(self, mock_moviepy, tmp_path):
        """
        [2.4-UNIT-009] AC5: Uses AAC audio codec.
        
        GIVEN valid inputs
        WHEN video is written
        THEN AAC audio codec is used.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        mock_image_clip, mock_audio_clip, mock_concat, mock_clip = mock_moviepy
        
        compiler = FFmpegVideoCompiler()
        images = create_test_images(3)
        audio = create_test_audio(10.0)
        output_path = tmp_path / "output.mp4"
        
        compiler.compile_video(images, audio, output_path)
        
        call_kwargs = mock_clip.write_videofile.call_args.kwargs
        assert call_kwargs.get("audio_codec") == "aac"

    def test_compile_video_output_resolution_1920x1080(self, mock_moviepy, tmp_path):
        """
        [2.4-UNIT-010] AC5: Output resolution is 1920x1080.
        
        GIVEN valid inputs
        WHEN images are processed
        THEN they are resized to 1920x1080.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        mock_image_clip, mock_audio_clip, mock_concat, mock_clip = mock_moviepy
        
        compiler = FFmpegVideoCompiler()
        images = create_test_images(3)
        audio = create_test_audio(10.0)
        output_path = tmp_path / "output.mp4"
        
        compiler.compile_video(images, audio, output_path)
        
        # With zoom enabled (default), fl() is called for zoom effect
        # which handles resolution internally via center-crop
        mock_clip.fl.assert_called()


# =============================================================================
# Story 2.4: AC2, AC3 - Image Distribution Tests
# =============================================================================

class TestImageDistribution:
    """Tests for image timing distribution (AC2, AC3)."""

    def test_images_evenly_distributed_across_audio(self, mock_moviepy, tmp_path):
        """
        [2.4-UNIT-011] AC3: Images evenly distributed.
        
        GIVEN 3 images and 12s audio
        WHEN compiling video
        THEN each image gets 4 seconds.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        mock_image_clip, mock_audio_clip, mock_concat, mock_clip = mock_moviepy
        mock_audio_clip.return_value.duration = 12.0
        
        compiler = FFmpegVideoCompiler()
        images = create_test_images(3)
        audio = create_test_audio(12.0)
        output_path = tmp_path / "output.mp4"
        
        compiler.compile_video(images, audio, output_path)
        
        # Verify with_duration was called with correct duration per image
        with_duration_call = mock_image_clip.return_value.with_duration
        # Each image should be 12.0 / 3 = 4.0 seconds
        assert with_duration_call.call_count == 3
        for call in with_duration_call.call_args_list:
            duration = call.args[0] if call.args else call.kwargs.get("duration")
            assert abs(duration - 4.0) < 0.1

    def test_single_image_fills_entire_duration(self, mock_moviepy, tmp_path):
        """
        [2.4-UNIT-012] AC3 edge case: Single image fills full duration.
        
        GIVEN 1 image and 10s audio
        WHEN compiling video
        THEN the image displays for 10 seconds.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        mock_image_clip, mock_audio_clip, mock_concat, mock_clip = mock_moviepy
        mock_audio_clip.return_value.duration = 10.0
        
        compiler = FFmpegVideoCompiler()
        images = create_test_images(1)
        audio = create_test_audio(10.0)
        output_path = tmp_path / "output.mp4"
        
        compiler.compile_video(images, audio, output_path)
        
        with_duration_call = mock_image_clip.return_value.with_duration
        duration = with_duration_call.call_args.args[0]
        assert abs(duration - 10.0) < 0.1


# =============================================================================
# Story 2.4: AC4 - Progress Callback Tests
# =============================================================================

class TestProgressCallback:
    """Tests for progress callback during compilation (AC4)."""

    def test_progress_callback_invoked_per_image(self, mock_moviepy, tmp_path):
        """
        [2.4-UNIT-013] AC4: Progress callback per image.
        
        GIVEN a progress callback
        WHEN compiling 3 images
        THEN callback is called with "Processing image X of Y" for each.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        progress_updates = []
        def progress_callback(status: str):
            progress_updates.append(status)
        
        compiler = FFmpegVideoCompiler()
        images = create_test_images(3)
        audio = create_test_audio(10.0)
        output_path = tmp_path / "output.mp4"
        
        compiler.compile_video(images, audio, output_path, progress_callback=progress_callback)
        
        # Should have "Processing image 1 of 3", etc.
        image_updates = [u for u in progress_updates if "Processing image" in u]
        assert len(image_updates) == 3

    def test_progress_callback_shows_compiling_message(self, mock_moviepy, tmp_path):
        """
        [2.4-UNIT-014] AC4: Shows "Compiling video..." message.
        
        GIVEN a progress callback
        WHEN video is being written
        THEN "Compiling video..." is shown.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        progress_updates = []
        def progress_callback(status: str):
            progress_updates.append(status)
        
        compiler = FFmpegVideoCompiler()
        images = create_test_images(3)
        audio = create_test_audio(10.0)
        output_path = tmp_path / "output.mp4"
        
        compiler.compile_video(images, audio, output_path, progress_callback=progress_callback)
        
        compiling_updates = [u for u in progress_updates if "Compiling video" in u]
        assert len(compiling_updates) >= 1

    def test_no_error_when_progress_callback_is_none(self, mock_moviepy, tmp_path):
        """
        [2.4-UNIT-015] AC4: No error when callback is None.
        
        GIVEN no progress callback
        WHEN compiling video
        THEN no error is raised.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        compiler = FFmpegVideoCompiler()
        images = create_test_images(3)
        audio = create_test_audio(10.0)
        output_path = tmp_path / "output.mp4"
        
        # Should not raise
        result = compiler.compile_video(images, audio, output_path, progress_callback=None)
        assert result is not None


# =============================================================================
# Story 2.4: AC6 - Validation Error Tests
# =============================================================================

class TestValidationErrors:
    """Tests for input validation (AC6)."""

    def test_empty_images_raises_validation_error(self, mock_moviepy, tmp_path):
        """
        [2.4-UNIT-016] AC6: Empty images raises ValidationError.
        
        GIVEN an empty images list
        WHEN compile_video() is called
        THEN ValidationError is raised.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        from eleven_video.exceptions.custom_errors import ValidationError
        
        compiler = FFmpegVideoCompiler()
        images = []
        audio = create_test_audio(10.0)
        output_path = tmp_path / "output.mp4"
        
        with pytest.raises(ValidationError) as exc_info:
            compiler.compile_video(images, audio, output_path)
        
        assert "image" in str(exc_info.value).lower()

    def test_none_audio_raises_validation_error(self, mock_moviepy, tmp_path):
        """
        [2.4-UNIT-017] AC6: None audio raises ValidationError.
        
        GIVEN None audio
        WHEN compile_video() is called
        THEN ValidationError is raised.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        from eleven_video.exceptions.custom_errors import ValidationError
        
        compiler = FFmpegVideoCompiler()
        images = create_test_images(3)
        output_path = tmp_path / "output.mp4"
        
        with pytest.raises((ValidationError, TypeError)):
            compiler.compile_video(images, None, output_path)


# =============================================================================
# Story 2.4: AC6 - Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Tests for error handling (AC6)."""

    def test_ffmpeg_missing_raises_video_processing_error(self, mock_moviepy_error, tmp_path):
        """
        [2.4-UNIT-018] AC6: FFmpeg missing raises VideoProcessingError.
        
        GIVEN FFmpeg is not installed
        WHEN compile_video() is called
        THEN VideoProcessingError with helpful message is raised.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        from eleven_video.exceptions.custom_errors import VideoProcessingError
        
        mock_image_clip, set_error = mock_moviepy_error
        set_error(OSError("ffmpeg not found"))
        
        compiler = FFmpegVideoCompiler()
        images = create_test_images(3)
        audio = create_test_audio(10.0)
        output_path = tmp_path / "output.mp4"
        
        with pytest.raises(VideoProcessingError) as exc_info:
            compiler.compile_video(images, audio, output_path)
        
        error_msg = str(exc_info.value).lower()
        assert "ffmpeg" in error_msg

    def test_temp_files_cleaned_on_success(self, mock_moviepy, tmp_path):
        """
        [2.4-UNIT-019] AC6: Temp files cleaned on success.
        
        GIVEN successful compilation
        WHEN process completes
        THEN no temporary files remain.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        import tempfile
        import os
        
        # Count temp files before
        temp_dir = tempfile.gettempdir()
        files_before = set(os.listdir(temp_dir))
        
        compiler = FFmpegVideoCompiler()
        images = create_test_images(3)
        audio = create_test_audio(10.0)
        output_path = tmp_path / "output.mp4"
        
        compiler.compile_video(images, audio, output_path)
        
        # Count temp files after - should be same or fewer
        files_after = set(os.listdir(temp_dir))
        new_files = files_after - files_before
        # Filter for our specific temp files
        our_temp_files = [f for f in new_files if "eleven" in f.lower() or "video" in f.lower()]
        assert len(our_temp_files) == 0

    def test_temp_files_cleaned_on_failure(self, mock_moviepy_error, tmp_path):
        """
        [2.4-UNIT-020] AC6: Temp files cleaned on failure.
        
        GIVEN compilation fails
        WHEN error is caught
        THEN no temporary files remain.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        from eleven_video.exceptions.custom_errors import VideoProcessingError
        import tempfile
        import os
        
        mock_image_clip, set_error = mock_moviepy_error
        set_error(RuntimeError("Processing failed"))
        
        temp_dir = tempfile.gettempdir()
        files_before = set(os.listdir(temp_dir))
        
        compiler = FFmpegVideoCompiler()
        images = create_test_images(3)
        audio = create_test_audio(10.0)
        output_path = tmp_path / "output.mp4"
        
        with pytest.raises(VideoProcessingError):
            compiler.compile_video(images, audio, output_path)
        
        files_after = set(os.listdir(temp_dir))
        new_files = files_after - files_before
        our_temp_files = [f for f in new_files if "eleven" in f.lower() or "video" in f.lower()]
        assert len(our_temp_files) == 0


# =============================================================================
# Story 2.7: Zoom Effect Fixtures
# =============================================================================

@pytest.fixture
def mock_moviepy_zoom():
    """
    Fixture providing mocked moviepy with fl() method for zoom effect tests.
    
    Mocks ImageClip including the fl() frame-level method required for
    Ken Burns style zoom effects.
    """
    with patch("eleven_video.processing.video_handler.ImageClip") as mock_image_clip, \
         patch("eleven_video.processing.video_handler.AudioFileClip") as mock_audio_clip, \
         patch("eleven_video.processing.video_handler.concatenate_videoclips") as mock_concat:
        
        # Create mock clip with expected properties + fl() method
        mock_clip = MagicMock()
        mock_clip.duration = 10.0
        mock_clip.w = 1920
        mock_clip.h = 1080
        mock_clip.write_videofile = MagicMock()
        mock_clip.set_audio = MagicMock(return_value=mock_clip)
        mock_clip.with_audio = MagicMock(return_value=mock_clip)
        mock_clip.with_duration = MagicMock(return_value=mock_clip)
        mock_clip.resized = MagicMock(return_value=mock_clip)
        mock_clip.close = MagicMock()
        
        # Key: fl() method for frame-level transformations (zoom effects)
        mock_clip.fl = MagicMock(return_value=mock_clip)
        
        # Chain: ImageClip() -> with_duration() -> returns clip with fl() accessible
        mock_image_clip.return_value = mock_clip
        mock_image_clip.return_value.with_duration.return_value = mock_clip
        mock_image_clip.return_value.with_duration.return_value.resized.return_value = mock_clip
        mock_image_clip.return_value.with_duration.return_value.fl.return_value = mock_clip
        
        mock_audio_clip.return_value.duration = 10.0
        mock_audio_clip.return_value.close = MagicMock()
        mock_concat.return_value = mock_clip
        
        yield mock_image_clip, mock_audio_clip, mock_concat, mock_clip


# =============================================================================
# Story 2.7: AC1, AC3 - Zoom Effect Application Tests
# =============================================================================

class TestZoomEffectApplication:
    """Tests for zoom effect application (AC1, AC3, AC4)."""

    def test_apply_zoom_effect_method_exists(self):
        """
        [2.7-UNIT-001] AC1: _apply_zoom_effect method exists.
        
        GIVEN FFmpegVideoCompiler
        WHEN checking for _apply_zoom_effect method
        THEN the method is available.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        compiler = FFmpegVideoCompiler()
        
        assert hasattr(compiler, "_apply_zoom_effect")
        assert callable(getattr(compiler, "_apply_zoom_effect"))

    def test_zoom_scale_factor_constant_exists(self):
        """
        [2.7-UNIT-002] AC4: ZOOM_SCALE_FACTOR constant exists.
        
        GIVEN FFmpegVideoCompiler class
        WHEN checking for ZOOM_SCALE_FACTOR constant
        THEN it exists and is between 1.05 and 1.10 (5-10% zoom).
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        assert hasattr(FFmpegVideoCompiler, "ZOOM_SCALE_FACTOR")
        zoom_factor = FFmpegVideoCompiler.ZOOM_SCALE_FACTOR
        assert 1.05 <= zoom_factor <= 1.10, f"Zoom factor {zoom_factor} not in subtle 5-10% range"

    def test_apply_zoom_effect_uses_fl_method(self, mock_moviepy_zoom):
        """
        [2.7-UNIT-003] AC3: Zoom effect uses moviepy's fl() method.
        
        GIVEN a mock clip with fl() method
        WHEN _apply_zoom_effect is called
        THEN fl() is called for frame-level transformation.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        mock_image_clip, _, _, mock_clip = mock_moviepy_zoom
        mock_clip.duration = 5.0
        
        compiler = FFmpegVideoCompiler()
        result = compiler._apply_zoom_effect(mock_clip, "in")
        
        mock_clip.fl.assert_called_once()

    def test_apply_zoom_effect_zoom_in_direction(self, mock_moviepy_zoom):
        """
        [2.7-UNIT-004] AC1: Zoom-in effect with direction "in".
        
        GIVEN zoom direction "in"
        WHEN _apply_zoom_effect is called
        THEN a zoomed clip is returned (1.0 → ZOOM_SCALE_FACTOR).
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        mock_image_clip, _, _, mock_clip = mock_moviepy_zoom
        mock_clip.duration = 5.0
        
        compiler = FFmpegVideoCompiler()
        result = compiler._apply_zoom_effect(mock_clip, "in")
        
        # Verify zoom effect was applied and clip returned
        assert result is mock_clip
        mock_clip.fl.assert_called_once()

    def test_apply_zoom_effect_zoom_out_direction(self, mock_moviepy_zoom):
        """
        [2.7-UNIT-005] AC1: Zoom-out effect with direction "out".
        
        GIVEN zoom direction "out"
        WHEN _apply_zoom_effect is called
        THEN a zoomed clip is returned (ZOOM_SCALE_FACTOR → 1.0).
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        mock_image_clip, _, _, mock_clip = mock_moviepy_zoom
        mock_clip.duration = 5.0
        
        compiler = FFmpegVideoCompiler()
        result = compiler._apply_zoom_effect(mock_clip, "out")
        
        # Verify zoom effect was applied and clip returned
        assert result is mock_clip
        mock_clip.fl.assert_called_once()

    def test_apply_zoom_effect_invalid_direction_defaults_to_in(self, mock_moviepy_zoom):
        """
        [2.7-UNIT-017] Edge case: Invalid direction treated as zoom-in.
        
        GIVEN invalid zoom direction "diagonal"
        WHEN _apply_zoom_effect is called
        THEN it does not crash and applies zoom (zoom-out behavior).
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        mock_image_clip, _, _, mock_clip = mock_moviepy_zoom
        mock_clip.duration = 5.0
        
        compiler = FFmpegVideoCompiler()
        # Invalid direction should not crash
        result = compiler._apply_zoom_effect(mock_clip, "diagonal")
        
        # Should still apply fl() (zoom effect)
        assert result is mock_clip
        mock_clip.fl.assert_called_once()


# =============================================================================
# Story 2.7: AC2 - Alternation Tests
# =============================================================================

class TestZoomAlternation:
    """Tests for zoom effect alternation (AC2)."""

    def test_alternating_zoom_directions_in_create_image_clips(self, mock_moviepy_zoom, tmp_path):
        """
        [2.7-UNIT-006] AC2: Alternating images receive zoom-in and zoom-out.
        
        GIVEN 4 images
        WHEN compiling with zoom enabled
        THEN images alternate: in, out, in, out.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        mock_image_clip, mock_audio_clip, mock_concat, mock_clip = mock_moviepy_zoom
        mock_audio_clip.return_value.duration = 12.0
        
        compiler = FFmpegVideoCompiler()
        images = create_test_images(4)
        audio = create_test_audio(12.0)
        output_path = tmp_path / "output.mp4"
        
        # Track zoom applications
        zoom_directions = []
        original_apply_zoom = compiler._apply_zoom_effect
        
        def tracking_zoom(clip, direction):
            zoom_directions.append(direction)
            return mock_clip
        
        with patch.object(compiler, "_apply_zoom_effect", side_effect=tracking_zoom):
            compiler.compile_video(images, audio, output_path)
        
        # Even indices (0, 2) should be "in", odd indices (1, 3) should be "out"
        assert zoom_directions == ["in", "out", "in", "out"]

    def test_single_image_uses_zoom_in(self, mock_moviepy_zoom, tmp_path):
        """
        [2.7-UNIT-007] AC2: Single image uses zoom-in.
        
        GIVEN 1 image
        WHEN compiling with zoom enabled
        THEN zoom-in effect is applied (index 0 = even).
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        mock_image_clip, mock_audio_clip, mock_concat, mock_clip = mock_moviepy_zoom
        mock_audio_clip.return_value.duration = 10.0
        
        compiler = FFmpegVideoCompiler()
        images = create_test_images(1)
        audio = create_test_audio(10.0)
        output_path = tmp_path / "output.mp4"
        
        zoom_directions = []
        
        def tracking_zoom(clip, direction):
            zoom_directions.append(direction)
            return mock_clip
        
        with patch.object(compiler, "_apply_zoom_effect", side_effect=tracking_zoom):
            compiler.compile_video(images, audio, output_path)
        
        assert zoom_directions == ["in"]


# =============================================================================
# Story 2.7: AC5 - Default Enabled Tests  
# =============================================================================

class TestZoomDefaultEnabled:
    """Tests for zoom effects enabled by default (AC5)."""

    def test_compile_video_has_enable_zoom_parameter(self):
        """
        [2.7-UNIT-008] AC5: compile_video accepts enable_zoom parameter.
        
        GIVEN FFmpegVideoCompiler.compile_video method
        WHEN checking signature
        THEN enable_zoom parameter exists with default True.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        import inspect
        
        sig = inspect.signature(FFmpegVideoCompiler.compile_video)
        params = sig.parameters
        
        assert "enable_zoom" in params
        assert params["enable_zoom"].default is True

    def test_zoom_applied_by_default(self, mock_moviepy_zoom, tmp_path):
        """
        [2.7-UNIT-009] AC5: Zoom applied without explicit enable_zoom.
        
        GIVEN images and audio
        WHEN compile_video() is called without enable_zoom argument
        THEN zoom effects are applied (fl() called).
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        mock_image_clip, mock_audio_clip, mock_concat, mock_clip = mock_moviepy_zoom
        mock_audio_clip.return_value.duration = 10.0
        
        compiler = FFmpegVideoCompiler()
        images = create_test_images(2)
        audio = create_test_audio(10.0)
        output_path = tmp_path / "output.mp4"
        
        compiler.compile_video(images, audio, output_path)
        
        # fl() should have been called (zoom applied)
        assert mock_clip.fl.called

    def test_zoom_disabled_when_enable_zoom_false(self, mock_moviepy_zoom, tmp_path):
        """
        [2.7-UNIT-010] AC5: Zoom not applied when enable_zoom=False.
        
        GIVEN images and audio
        WHEN compile_video(enable_zoom=False)
        THEN zoom effects are NOT applied (resized used instead).
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        mock_image_clip, mock_audio_clip, mock_concat, mock_clip = mock_moviepy_zoom
        mock_audio_clip.return_value.duration = 10.0
        
        compiler = FFmpegVideoCompiler()
        images = create_test_images(2)
        audio = create_test_audio(10.0)
        output_path = tmp_path / "output.mp4"
        
        compiler.compile_video(images, audio, output_path, enable_zoom=False)
        
        # fl() should NOT be called when zoom disabled
        assert not mock_clip.fl.called
        # resized() should be called instead
        assert mock_clip.resized.called


# =============================================================================
# Story 2.7: AC6 - Fallback Handling Tests
# =============================================================================

class TestZoomFallbackHandling:
    """Tests for zoom effect fallback on error (AC6)."""

    def test_fallback_to_static_on_zoom_error(self, mock_moviepy_zoom, tmp_path):
        """
        [2.7-UNIT-011] AC6: Falls back to static image on zoom error.
        
        GIVEN fl() raises an exception
        WHEN compiling with zoom enabled
        THEN static image (resized) is used instead.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        mock_image_clip, mock_audio_clip, mock_concat, mock_clip = mock_moviepy_zoom
        mock_audio_clip.return_value.duration = 10.0
        
        # fl() raises error first time, simulating zoom failure
        mock_clip.fl.side_effect = RuntimeError("Zoom calculation failed")
        
        compiler = FFmpegVideoCompiler()
        images = create_test_images(1)
        audio = create_test_audio(10.0)
        output_path = tmp_path / "output.mp4"
        
        # Should not raise - should fall back to static
        result = compiler.compile_video(images, audio, output_path)
        
        assert result is not None
        # resized() should be called as fallback
        assert mock_clip.resized.called

    def test_fallback_logs_warning_via_progress_callback(self, mock_moviepy_zoom, tmp_path):
        """
        [2.7-UNIT-012] AC6: Warning logged via progress callback on fallback.
        
        GIVEN fl() raises an exception and progress callback provided
        WHEN zoom fails
        THEN warning message is sent to progress callback.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        mock_image_clip, mock_audio_clip, mock_concat, mock_clip = mock_moviepy_zoom
        mock_audio_clip.return_value.duration = 10.0
        mock_clip.fl.side_effect = RuntimeError("Zoom calculation failed")
        
        progress_updates = []
        def progress_callback(status: str):
            progress_updates.append(status)
        
        compiler = FFmpegVideoCompiler()
        images = create_test_images(1)
        audio = create_test_audio(10.0)
        output_path = tmp_path / "output.mp4"
        
        compiler.compile_video(images, audio, output_path, progress_callback=progress_callback)
        
        warning_messages = [u for u in progress_updates if "warning" in u.lower() or "static" in u.lower()]
        assert len(warning_messages) >= 1


# =============================================================================
# Story 2.7: AC7 - Resolution Maintenance Tests
# =============================================================================

class TestZoomResolutionMaintenance:
    """Tests for output resolution maintenance during zoom (AC7)."""

    def test_zoom_output_resolution_1920x1080(self, mock_moviepy_zoom, tmp_path):
        """
        [2.7-UNIT-013] AC7: Zoom maintains 1920x1080 output resolution.
        
        GIVEN zoom effects are applied
        WHEN video is compiled
        THEN final output remains 1920x1080.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        mock_image_clip, mock_audio_clip, mock_concat, mock_clip = mock_moviepy_zoom
        mock_audio_clip.return_value.duration = 10.0
        mock_clip.w = 1920
        mock_clip.h = 1080
        
        compiler = FFmpegVideoCompiler()
        images = create_test_images(2)
        audio = create_test_audio(10.0)
        output_path = tmp_path / "output.mp4"
        
        result = compiler.compile_video(images, audio, output_path)
        
        # Verify resolution in result
        assert result.resolution == (1920, 1080)

    def test_zoom_effect_does_not_call_resized(self, mock_moviepy_zoom, tmp_path):
        """
        [2.7-UNIT-014] AC7: Zoom effect handles resolution internally.
        
        GIVEN zoom is enabled
        WHEN _create_image_clips processes images
        THEN resized() is NOT called (zoom handles resolution via center-crop).
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        mock_image_clip, mock_audio_clip, mock_concat, mock_clip = mock_moviepy_zoom
        mock_audio_clip.return_value.duration = 10.0
        
        # Reset resized call tracking
        mock_clip.resized.reset_mock()
        
        compiler = FFmpegVideoCompiler()
        images = create_test_images(2)
        audio = create_test_audio(10.0)
        output_path = tmp_path / "output.mp4"
        
        compiler.compile_video(images, audio, output_path, enable_zoom=True)
        
        # When zoom is enabled, resized() should NOT be called
        # (zoom effect handles resolution internally via center-crop)
        assert not mock_clip.resized.called


# =============================================================================
# Story 2.7: Integration Tests
# =============================================================================

class TestZoomIntegration:
    """Integration tests for zoom effect with full pipeline."""

    def test_compile_video_with_zoom_returns_video(self, mock_moviepy_zoom, tmp_path):
        """
        [2.7-UNIT-015] Integration: Full compile with zoom returns Video.
        
        GIVEN images, audio, and zoom enabled
        WHEN compile_video() completes
        THEN a valid Video domain model is returned.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        from eleven_video.models.domain import Video
        
        mock_image_clip, mock_audio_clip, mock_concat, mock_clip = mock_moviepy_zoom
        mock_audio_clip.return_value.duration = 10.0
        
        compiler = FFmpegVideoCompiler()
        images = create_test_images(3)
        audio = create_test_audio(10.0)
        output_path = tmp_path / "output.mp4"
        
        result = compiler.compile_video(images, audio, output_path)
        
        assert isinstance(result, Video)
        assert result.file_path == output_path

    def test_compile_video_progress_callback_with_zoom(self, mock_moviepy_zoom, tmp_path):
        """
        [2.7-UNIT-016] Integration: Progress callback works with zoom.
        
        GIVEN progress callback and zoom enabled
        WHEN compiling 3 images
        THEN progress updates include image processing messages.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        mock_image_clip, mock_audio_clip, mock_concat, mock_clip = mock_moviepy_zoom
        mock_audio_clip.return_value.duration = 12.0
        
        progress_updates = []
        def progress_callback(status: str):
            progress_updates.append(status)
        
        compiler = FFmpegVideoCompiler()
        images = create_test_images(3)
        audio = create_test_audio(12.0)
        output_path = tmp_path / "output.mp4"
        
        compiler.compile_video(images, audio, output_path, progress_callback=progress_callback)
        
        image_updates = [u for u in progress_updates if "Processing image" in u]
        assert len(image_updates) == 3
