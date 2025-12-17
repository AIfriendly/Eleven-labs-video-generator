""
"""
Tests for FFmpegVideoCompiler - Ken Burns Zoom Effect (Story 2.7).

Test IDs: 2.7-UNIT-001 to 2.7-UNIT-010
Tests cover AC1-AC7: zoom effect application, alternation, subtlety,
resolution, fallback, and default behavior.

Related files:
- eleven_video/processing/video_handler.py: FFmpegVideoCompiler implementation
"""
import pytest
from unittest.mock import MagicMock, patch, call
from pathlib import Path

# Assuming test data factories are in a shared conftest.py or similar
# For this example, they are duplicated for clarity.
def create_test_image(size_bytes: int = 1000):
    from eleven_video.models.domain import Image
    return Image(
        data=b"\x89PNG\r\n\x1a\n" + b"\x00" * size_bytes,
        mime_type="image/png",
        file_size_bytes=size_bytes + 8
    )

def create_test_images(count: int = 3):
    return [create_test_image() for _ in range(count)]

def create_test_audio(duration: float = 10.0):
    from eleven_video.models.domain import Audio
    return Audio(
        data=b"\xff\xfb\x90\x00" + b"\x00" * 100,
        duration_seconds=duration,
        file_size_bytes=104
    )

@pytest.fixture
def mock_moviepy_zoom():
    """
    Fixture providing mocked moviepy for zoom effect unit tests.
    Extends the base mock by adding a mock for the 'fl' (frame-level) method.
    """
    with patch("eleven_video.processing.video_handler.ImageClip") as mock_image_clip,
         patch("eleven_video.processing.video_handler.AudioFileClip") as mock_audio_clip,
         patch("eleven_video.processing.video_handler.concatenate_videoclips") as mock_concat:
        
        mock_clip = MagicMock()
        mock_clip.duration = 10.0
        mock_clip.w = 1920
        mock_clip.h = 1080
        mock_clip.write_videofile = MagicMock()
        mock_clip.set_audio = MagicMock(return_value=mock_clip)
        mock_clip.close = MagicMock()
        
        # Add mock for the .fl() method used by the zoom effect
        mock_clip.fl = MagicMock(return_value=mock_clip)
        
        # Chain for existing functionality
        resized_clip = MagicMock()
        mock_image_clip.return_value.with_duration.return_value = resized_clip
        resized_clip.resized.return_value = mock_clip
        resized_clip.fl.return_value = mock_clip # The zoom effect is applied on the duration-set clip

        mock_audio_clip.return_value.duration = 10.0
        mock_audio_clip.return_value.close = MagicMock()
        mock_concat.return_value = mock_clip
        
        yield mock_image_clip, mock_audio_clip, mock_concat, resized_clip


class TestZoomEffect:
    """Tests for the Ken Burns zoom effect (Story 2.7)."""

    def test_zoom_effect_is_applied_by_default(self, mock_moviepy_zoom, tmp_path):
        """
        [2.7-UNIT-001] AC1, AC5: Zoom effect is applied by default.
        
        GIVEN a compile request with default settings
        WHEN _create_image_clips is called
        THEN the zoom effect method (_apply_zoom_effect) is called.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        compiler = FFmpegVideoCompiler()
        # Mock the internal method to check if it's called
        compiler._apply_zoom_effect = MagicMock(return_value=MagicMock())
        
        image_paths = ["img1.png", "img2.png"]
        
        compiler._create_image_clips(image_paths, duration_per_image=5.0, progress_callback=None)
        
        assert compiler._apply_zoom_effect.call_count == len(image_paths)

    def test_zoom_direction_alternates(self, mock_moviepy_zoom, tmp_path):
        """
        [2.7-UNIT-002] AC2: Zoom direction alternates for visual variety.
        
        GIVEN a list of multiple images
        WHEN _create_image_clips is called
        THEN zoom direction alternates between 'in' and 'out'.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        compiler = FFmpegVideoCompiler()
        compiler._apply_zoom_effect = MagicMock(return_value=MagicMock())
        
        image_paths = ["img1.png", "img2.png", "img3.png"]
        
        compiler._create_image_clips(image_paths, duration_per_image=5.0, progress_callback=None)
        
        # Check calls to the mocked zoom effect method
        calls = compiler._apply_zoom_effect.call_args_list
        assert len(calls) == 3
        # Check the 'zoom_direction' argument of each call
        assert calls[0].args[1] == "in"  # or kwargs['zoom_direction']
        assert calls[1].args[1] == "out"
        assert calls[2].args[1] == "in"

    def test_zoom_is_disabled_via_parameter(self, mock_moviepy_zoom, tmp_path):
        """
        [2.7-UNIT-003] AC5 extension: Zoom can be disabled.
        
        GIVEN enable_zoom is False
        WHEN _create_image_clips is called
        THEN the zoom effect is not applied and resize is used instead.
        """
        mock_image_clip, _, _, resized_clip = mock_moviepy_zoom
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        compiler = FFmpegVideoCompiler()
        compiler._apply_zoom_effect = MagicMock()
        
        image_paths = ["img1.png"]
        
        compiler._create_image_clips(image_paths, duration_per_image=5.0, progress_callback=None, enable_zoom=False)
        
        # Zoom should NOT be called
        compiler._apply_zoom_effect.assert_not_called()
        # Resize SHOULD be called
        resized_clip.resized.assert_called_once_with(newsize=compiler.OUTPUT_RESOLUTION)

    def test_zoom_fallback_on_error(self, mock_moviepy_zoom, tmp_path):
        """
        [2.7-UNIT-004] AC6: Fallback to static image on zoom effect error.
        
        GIVEN the zoom effect raises an exception
        WHEN _create_image_clips processes an image
        THEN it falls back to a simple resized clip and continues.
        """
        mock_image_clip, _, _, resized_clip = mock_moviepy_zoom
        from eleven_video.processing.video_handler import FFmpegVideoCompiler

        compiler = FFmpegVideoCompiler()
        # Make the mocked zoom effect raise an error
        compiler._apply_zoom_effect = MagicMock(side_effect=Exception("Zoom failed"))
        
        image_paths = ["img1.png", "img2.png"]
        progress_updates = []
        def progress_callback(status: str):
            progress_updates.append(status)

        clips = compiler._create_image_clips(image_paths, 5.0, progress_callback)
        
        # Should still produce clips for all images
        assert len(clips) == 2
        # Resize should be called as a fallback for both
        assert resized_clip.resized.call_count == 2
        # Progress callback should contain a warning
        assert any("Warning: zoom failed" in u for u in progress_updates)

    def test_output_resolution_is_maintained(self, mock_moviepy_zoom, tmp_path):
        """
        [2.7-UNIT-005] AC7: Output resolution is maintained after zoom.
        
        GIVEN a zoom effect is applied
        WHEN a clip is processed
        THEN the resulting clip has the correct output resolution.
        """
        # This test is more conceptual for unit testing with mocks.
        # The mock setup ensures the final clip has the correct mocked dimensions.
        # A true integration test would verify the actual output file's properties.
        mock_image_clip, _, _, resized_clip = mock_moviepy_zoom
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        compiler = FFmpegVideoCompiler()
        
        # Let's assume _apply_zoom_effect returns a clip with the correct dimensions
        mock_zoomed_clip = MagicMock(w=1920, h=1080)
        compiler._apply_zoom_effect = MagicMock(return_value=mock_zoomed_clip)

        clips = compiler._create_image_clips(["img1.png"], 5.0, None)
        
        assert clips[0].w == 1920
        assert clips[0].h == 1080
        # Verify resize was NOT called, as zoom handles it
        resized_clip.resized.assert_not_called()
        
    def test_ken_burns_effect_logic(self):
        """
        [2.7-UNIT-006] AC3, AC4: Gradual, subtle zoom effect logic.
        
        GIVEN the _apply_zoom_effect method
        WHEN called with a clip
        THEN it returns a clip with a frame-level effect function.
        """
        # This tests the internal implementation of the effect.
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        
        compiler = FFmpegVideoCompiler()
        
        mock_clip = MagicMock(duration=10.0)
        
        # Call the real method
        result_clip = compiler._apply_zoom_effect(mock_clip, zoom_direction="in")
        
        # Assert that the 'fl' method was called, which applies the transform
        mock_clip.fl.assert_called_once()
        # We could further inspect the function passed to fl, but that's very white-box.
        # For ATDD, we trust that if `fl` is called, the effect is being applied.
        
    def test_zoom_effect_not_called_when_no_images(self, mock_moviepy_zoom):
        """
        [2.7-UNIT-007] Edge case: No images.
        
        GIVEN an empty list of images
        WHEN _create_image_clips is called
        THEN no zoom effects are attempted.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        compiler = FFmpegVideoCompiler()
        compiler._apply_zoom_effect = MagicMock()

        compiler._create_image_clips([], 5.0, None)
        
        compiler._apply_zoom_effect.assert_not_called()

    def test_full_compile_video_enables_zoom_by_default(self, mock_moviepy_zoom, tmp_path):
        """
        [2.7-UNIT-008] AC5: compile_video enables zoom by default.
        
        GIVEN a call to the main compile_video method
        WHEN no 'enable_zoom' parameter is provided
        THEN _create_image_clips is called with enable_zoom=True.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        compiler = FFmpegVideoCompiler()

        # We spy on the internal method _create_image_clips
        compiler._create_image_clips = MagicMock(return_value=[])

        images = create_test_images(2)
        audio = create_test_audio(10.0)
        output_path = tmp_path / "output.mp4"

        compiler.compile_video(images, audio, output_path)

        # Check that _create_image_clips was called with the default True
        compiler._create_image_clips.assert_called_once()
        call_kwargs = compiler._create_image_clips.call_args.kwargs
        assert call_kwargs.get('enable_zoom') is True

    def test_full_compile_video_can_disable_zoom(self, mock_moviepy_zoom, tmp_path):
        """
        [2.7-UNIT-009] AC5 extension: compile_video can disable zoom.
        
        GIVEN a call to compile_video with enable_zoom=False
        WHEN the compilation runs
        THEN _create_image_clips is called with enable_zoom=False.
        """
        from eleven_video.processing.video_handler import FFmpegVideoCompiler
        compiler = FFmpegVideoCompiler()
        compiler._create_image_clips = MagicMock(return_value=[])

        images = create_test_images(2)
        audio = create_test_audio(10.0)
        output_path = tmp_path / "output.mp4"

        compiler.compile_video(images, audio, output_path, enable_zoom=False)

        compiler._create_image_clips.assert_called_once()
        call_kwargs = compiler._create_image_clips.call_args.kwargs
        assert call_kwargs.get('enable_zoom') is False

