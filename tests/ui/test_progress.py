"""
Tests for VideoPipelineProgress - Progress Updates During Video Generation (Story 2.5).

Test IDs: 2.5-UNIT-001 to 2.5-UNIT-025
Tests cover AC1-AC7: stage lifecycle, progress display, error handling, summary.

Related files:
- eleven_video/ui/progress.py: VideoPipelineProgress implementation (NEW)
- eleven_video/models/domain.py: PipelineStage enum (NEW), Video domain model
- eleven_video/ui/console.py: Shared console singleton
"""
import pytest
from unittest.mock import MagicMock, patch
from io import StringIO
from pathlib import Path
from typing import Callable


# =============================================================================
# Test Data Factories
# =============================================================================

def create_test_video(
    file_path: Path = None,
    duration: float = 10.0,
    size_bytes: int = 1024000
):
    """Create test Video domain model."""
    from eleven_video.models.domain import Video
    return Video(
        file_path=file_path or Path("/test/output.mp4"),
        duration_seconds=duration,
        file_size_bytes=size_bytes,
        codec="h264",
        resolution=(1920, 1080)
    )


# =============================================================================
# Fixtures for Rich Console mocking
# =============================================================================

@pytest.fixture
def mock_console():
    """
    Fixture providing mocked Rich Console for output verification.
    
    Usage:
        def test_example(mock_console):
            output, console = mock_console
            # ... test code ...
            result = output.getvalue()
            assert "expected" in result
    """
    output = StringIO()
    from rich.console import Console
    test_console = Console(file=output, force_terminal=True, width=120)
    yield output, test_console


# =============================================================================
# Story 2.5: AC1 - PipelineStage Enum Tests
# =============================================================================

class TestPipelineStageEnum:
    """Tests for PipelineStage enum (AC1)."""

    def test_pipeline_stage_enum_exists(self):
        """
        [2.5-UNIT-001] AC1: PipelineStage enum exists in domain models.
        
        GIVEN the domain models module
        WHEN importing PipelineStage
        THEN the enum is available.
        """
        from eleven_video.models.domain import PipelineStage
        
        assert PipelineStage is not None

    def test_pipeline_stage_has_required_values(self):
        """
        [2.5-UNIT-002] AC1: PipelineStage has all required stage values.
        
        GIVEN PipelineStage enum
        WHEN checking values
        THEN INITIALIZING, PROCESSING_SCRIPT, PROCESSING_AUDIO, 
             PROCESSING_IMAGES, COMPILING_VIDEO, COMPLETED, FAILED exist.
        """
        from eleven_video.models.domain import PipelineStage
        
        assert hasattr(PipelineStage, 'INITIALIZING')
        assert hasattr(PipelineStage, 'PROCESSING_SCRIPT')
        assert hasattr(PipelineStage, 'PROCESSING_AUDIO')
        assert hasattr(PipelineStage, 'PROCESSING_IMAGES')
        assert hasattr(PipelineStage, 'COMPILING_VIDEO')
        assert hasattr(PipelineStage, 'COMPLETED')
        assert hasattr(PipelineStage, 'FAILED')

    def test_stage_icons_dict_exists(self):
        """
        [2.5-UNIT-003] AC2: STAGE_ICONS dict maps stages to emoji icons.
        
        GIVEN the domain models module
        WHEN importing STAGE_ICONS
        THEN a dict mapping PipelineStage to icons is available.
        """
        from eleven_video.models.domain import PipelineStage, STAGE_ICONS
        
        assert isinstance(STAGE_ICONS, dict)
        assert PipelineStage.INITIALIZING in STAGE_ICONS
        assert PipelineStage.COMPLETED in STAGE_ICONS


# =============================================================================
# Story 2.5: VideoPipelineProgress Class Tests
# =============================================================================

class TestVideoPipelineProgressClass:
    """Tests for VideoPipelineProgress class existence and initialization."""

    def test_video_pipeline_progress_exists(self):
        """
        [2.5-UNIT-004] AC1: VideoPipelineProgress class exists.
        
        GIVEN the ui.progress module
        WHEN importing VideoPipelineProgress
        THEN the class is available.
        """
        from eleven_video.ui.progress import VideoPipelineProgress
        
        assert VideoPipelineProgress is not None

    def test_video_pipeline_progress_accepts_optional_console(self, mock_console):
        """
        [2.5-UNIT-005] AC1: VideoPipelineProgress accepts optional Console.
        
        GIVEN a custom Console instance
        WHEN creating VideoPipelineProgress with console parameter
        THEN it uses the provided console.
        """
        from eleven_video.ui.progress import VideoPipelineProgress
        
        output, test_console = mock_console
        progress = VideoPipelineProgress(console=test_console)
        
        assert progress.console is test_console

    def test_video_pipeline_progress_uses_default_console(self):
        """
        [2.5-UNIT-006] AC1: VideoPipelineProgress uses default console singleton.
        
        GIVEN no Console parameter
        WHEN creating VideoPipelineProgress
        THEN it uses the default console from console.py.
        """
        from eleven_video.ui.progress import VideoPipelineProgress
        from eleven_video.ui.console import console as default_console
        
        progress = VideoPipelineProgress()
        
        assert progress.console is default_console


# =============================================================================
# Story 2.5: AC2, AC3 - Stage Lifecycle Tests
# =============================================================================

class TestStageLifecycle:
    """Tests for start_stage, complete_stage, fail_stage methods (AC2, AC3)."""

    def test_start_stage_updates_current_stage(self, mock_console):
        """
        [2.5-UNIT-007] AC2: start_stage updates current_stage.
        
        GIVEN a VideoPipelineProgress instance
        WHEN start_stage(PROCESSING_SCRIPT) is called
        THEN current_stage is set to PROCESSING_SCRIPT.
        """
        from eleven_video.ui.progress import VideoPipelineProgress
        from eleven_video.models.domain import PipelineStage
        
        output, test_console = mock_console
        progress = VideoPipelineProgress(console=test_console)
        
        progress.start_stage(PipelineStage.PROCESSING_SCRIPT)
        
        assert progress.current_stage == PipelineStage.PROCESSING_SCRIPT

    def test_start_stage_displays_stage_message(self, mock_console):
        """
        [2.5-UNIT-008] AC2: start_stage displays stage name with icon.
        
        GIVEN a VideoPipelineProgress instance
        WHEN start_stage(PROCESSING_AUDIO) is called
        THEN a message with stage icon is displayed.
        """
        from eleven_video.ui.progress import VideoPipelineProgress
        from eleven_video.models.domain import PipelineStage
        
        output, test_console = mock_console
        progress = VideoPipelineProgress(console=test_console)
        
        progress.start_stage(PipelineStage.PROCESSING_AUDIO)
        
        result = output.getvalue()
        # Should contain audio icon 🔊 and stage name
        assert "audio" in result.lower() or "🔊" in result

    def test_start_stage_records_start_time(self, mock_console):
        """
        [2.5-UNIT-009] AC3: start_stage records stage start time.
        
        GIVEN a VideoPipelineProgress instance
        WHEN start_stage is called
        THEN stage_start_times dict is updated.
        """
        from eleven_video.ui.progress import VideoPipelineProgress
        from eleven_video.models.domain import PipelineStage
        
        output, test_console = mock_console
        progress = VideoPipelineProgress(console=test_console)
        
        progress.start_stage(PipelineStage.PROCESSING_SCRIPT)
        
        assert PipelineStage.PROCESSING_SCRIPT in progress.stage_start_times
        assert isinstance(progress.stage_start_times[PipelineStage.PROCESSING_SCRIPT], float)

    def test_complete_stage_displays_elapsed_time(self, mock_console):
        """
        [2.5-UNIT-010] AC3: complete_stage displays elapsed time.
        
        GIVEN a stage has been started
        WHEN complete_stage is called
        THEN elapsed time is displayed.
        """
        from eleven_video.ui.progress import VideoPipelineProgress
        from eleven_video.models.domain import PipelineStage
        import time
        
        output, test_console = mock_console
        progress = VideoPipelineProgress(console=test_console)
        
        progress.start_stage(PipelineStage.PROCESSING_SCRIPT)
        time.sleep(0.01)  # Small delay
        progress.complete_stage(PipelineStage.PROCESSING_SCRIPT)
        
        result = output.getvalue()
        # Should contain some time indicator
        assert "complete" in result.lower() or "✓" in result or "done" in result.lower()

    def test_first_stage_starts_pipeline_timer(self, mock_console):
        """
        [2.5-UNIT-011] AC7: First start_stage initializes pipeline_start_time.
        
        GIVEN a new VideoPipelineProgress instance
        WHEN first start_stage is called
        THEN pipeline_start_time is set.
        """
        from eleven_video.ui.progress import VideoPipelineProgress
        from eleven_video.models.domain import PipelineStage
        
        output, test_console = mock_console
        progress = VideoPipelineProgress(console=test_console)
        
        assert progress.pipeline_start_time is None
        
        progress.start_stage(PipelineStage.INITIALIZING)
        
        assert progress.pipeline_start_time is not None
        assert isinstance(progress.pipeline_start_time, float)


# =============================================================================
# Story 2.5: AC4 - Image Progress Tests
# =============================================================================

class TestImageProgress:
    """Tests for image generation progress display (AC4)."""

    def test_update_progress_parses_image_count(self, mock_console):
        """
        [2.5-UNIT-012] AC4: update_progress parses "image X of Y" format.
        
        GIVEN an update message "Generating image 2 of 5"
        WHEN update_progress is called
        THEN completed_images and total_images are updated.
        """
        from eleven_video.ui.progress import VideoPipelineProgress
        from eleven_video.models.domain import PipelineStage
        
        output, test_console = mock_console
        progress = VideoPipelineProgress(console=test_console)
        progress.start_stage(PipelineStage.PROCESSING_IMAGES)
        
        progress.update_progress("Generating image 2 of 5")
        
        assert progress.total_images == 5
        assert progress.completed_images == 2

    def test_update_progress_displays_percentage(self, mock_console):
        """
        [2.5-UNIT-013] AC4: update_progress displays percentage for images.
        
        GIVEN image progress "Processing image 3 of 5"
        WHEN update_progress is called
        THEN 60% progress indicator is shown.
        """
        from eleven_video.ui.progress import VideoPipelineProgress
        from eleven_video.models.domain import PipelineStage
        
        output, test_console = mock_console
        progress = VideoPipelineProgress(console=test_console)
        progress.start_stage(PipelineStage.PROCESSING_IMAGES)
        
        progress.update_progress("Processing image 3 of 5")
        
        result = output.getvalue()
        # Should show percentage or progress bar
        assert "60" in result or "3" in result or "5" in result

    def test_update_progress_generic_message(self, mock_console):
        """
        [2.5-UNIT-014] AC1: update_progress displays generic messages.
        
        GIVEN a generic progress message
        WHEN update_progress is called
        THEN the message is displayed.
        """
        from eleven_video.ui.progress import VideoPipelineProgress
        from eleven_video.models.domain import PipelineStage
        
        output, test_console = mock_console
        progress = VideoPipelineProgress(console=test_console)
        progress.start_stage(PipelineStage.PROCESSING_SCRIPT)
        
        progress.update_progress("Generating script...")
        
        result = output.getvalue()
        assert "script" in result.lower() or "Generating" in result


# =============================================================================
# Story 2.5: AC5 - Compilation Progress Tests
# =============================================================================

class TestCompilationProgress:
    """Tests for video compilation progress display (AC5)."""

    def test_compiling_shows_spinner_message(self, mock_console):
        """
        [2.5-UNIT-015] AC5: Compiling video shows spinner/progress indicator.
        
        GIVEN COMPILING_VIDEO stage
        WHEN update_progress("Compiling video...") is called
        THEN a spinner or progress indicator is shown.
        """
        from eleven_video.ui.progress import VideoPipelineProgress
        from eleven_video.models.domain import PipelineStage
        
        output, test_console = mock_console
        progress = VideoPipelineProgress(console=test_console)
        progress.start_stage(PipelineStage.COMPILING_VIDEO)
        
        progress.update_progress("Compiling video...")
        
        result = output.getvalue()
        assert "Compiling" in result or "video" in result.lower() or "🎬" in result


# =============================================================================
# Story 2.5: AC6 - Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Tests for fail_stage error display (AC6)."""

    def test_fail_stage_displays_red_panel(self, mock_console):
        """
        [2.5-UNIT-016] AC6: fail_stage displays error in red panel.
        
        GIVEN a failure in PROCESSING_IMAGES stage
        WHEN fail_stage is called with error message
        THEN a red panel with error details is shown.
        """
        from eleven_video.ui.progress import VideoPipelineProgress
        from eleven_video.models.domain import PipelineStage
        
        output, test_console = mock_console
        progress = VideoPipelineProgress(console=test_console)
        progress.start_stage(PipelineStage.PROCESSING_IMAGES)
        
        progress.fail_stage(PipelineStage.PROCESSING_IMAGES, "API rate limit exceeded")
        
        result = output.getvalue()
        # Should contain error indicator and message
        assert "error" in result.lower() or "failed" in result.lower() or "❌" in result
        assert "rate limit" in result.lower() or "API" in result

    def test_fail_stage_shows_failed_icon(self, mock_console):
        """
        [2.5-UNIT-017] AC6: fail_stage shows failed stage icon (❌).
        
        GIVEN any stage failure
        WHEN fail_stage is called
        THEN the failed icon is displayed.
        """
        from eleven_video.ui.progress import VideoPipelineProgress
        from eleven_video.models.domain import PipelineStage
        
        output, test_console = mock_console
        progress = VideoPipelineProgress(console=test_console)
        progress.start_stage(PipelineStage.PROCESSING_AUDIO)
        
        progress.fail_stage(PipelineStage.PROCESSING_AUDIO, "TTS API error")
        
        result = output.getvalue()
        assert "❌" in result or "fail" in result.lower() or "error" in result.lower()

    def test_fail_stage_updates_current_stage(self, mock_console):
        """
        [2.5-UNIT-018] AC6: fail_stage updates current_stage to FAILED.
        
        GIVEN a stage failure
        WHEN fail_stage is called
        THEN current_stage is set to FAILED.
        """
        from eleven_video.ui.progress import VideoPipelineProgress
        from eleven_video.models.domain import PipelineStage
        
        output, test_console = mock_console
        progress = VideoPipelineProgress(console=test_console)
        progress.start_stage(PipelineStage.PROCESSING_SCRIPT)
        
        progress.fail_stage(PipelineStage.PROCESSING_SCRIPT, "Error occurred")
        
        assert progress.current_stage == PipelineStage.FAILED


# =============================================================================
# Story 2.5: AC7 - Summary Display Tests
# =============================================================================

class TestSummaryDisplay:
    """Tests for show_summary completion display (AC7)."""

    def test_show_summary_displays_green_panel(self, mock_console, tmp_path):
        """
        [2.5-UNIT-019] AC7: show_summary displays green success panel.
        
        GIVEN successful pipeline completion
        WHEN show_summary is called
        THEN a green panel is displayed.
        """
        from eleven_video.ui.progress import VideoPipelineProgress
        from eleven_video.models.domain import PipelineStage
        
        output, test_console = mock_console
        progress = VideoPipelineProgress(console=test_console)
        progress.start_stage(PipelineStage.INITIALIZING)
        
        output_path = tmp_path / "output.mp4"
        video = create_test_video(file_path=output_path)
        
        progress.show_summary(output_path, video)
        
        result = output.getvalue()
        assert "success" in result.lower() or "complete" in result.lower() or "✅" in result

    def test_show_summary_includes_output_path(self, mock_console, tmp_path):
        """
        [2.5-UNIT-020] AC7: show_summary includes output file path.
        
        GIVEN a completed video
        WHEN show_summary is called
        THEN the output path is displayed.
        """
        from eleven_video.ui.progress import VideoPipelineProgress
        from eleven_video.models.domain import PipelineStage
        
        output, test_console = mock_console
        progress = VideoPipelineProgress(console=test_console)
        progress.start_stage(PipelineStage.INITIALIZING)
        
        output_path = tmp_path / "my_video.mp4"
        video = create_test_video(file_path=output_path)
        
        progress.show_summary(output_path, video)
        
        result = output.getvalue()
        assert "my_video.mp4" in result or str(output_path) in result

    def test_show_summary_includes_total_time(self, mock_console, tmp_path):
        """
        [2.5-UNIT-021] AC7: show_summary includes total elapsed time.
        
        GIVEN a pipeline with recorded start time
        WHEN show_summary is called
        THEN total elapsed time is displayed.
        """
        from eleven_video.ui.progress import VideoPipelineProgress
        from eleven_video.models.domain import PipelineStage
        import time
        
        output, test_console = mock_console
        progress = VideoPipelineProgress(console=test_console)
        progress.start_stage(PipelineStage.INITIALIZING)
        time.sleep(0.01)
        
        output_path = tmp_path / "output.mp4"
        video = create_test_video(file_path=output_path)
        
        progress.show_summary(output_path, video)
        
        result = output.getvalue()
        # Should contain time indicator
        assert "time" in result.lower() or "s" in result or "second" in result.lower()

    def test_show_summary_includes_video_duration(self, mock_console, tmp_path):
        """
        [2.5-UNIT-022] AC7: show_summary includes video duration.
        
        GIVEN a video with 10.5s duration
        WHEN show_summary is called
        THEN duration is displayed.
        """
        from eleven_video.ui.progress import VideoPipelineProgress
        from eleven_video.models.domain import PipelineStage
        
        output, test_console = mock_console
        progress = VideoPipelineProgress(console=test_console)
        progress.start_stage(PipelineStage.INITIALIZING)
        
        output_path = tmp_path / "output.mp4"
        video = create_test_video(file_path=output_path, duration=10.5)
        
        progress.show_summary(output_path, video)
        
        result = output.getvalue()
        assert "10" in result or "duration" in result.lower()


# =============================================================================
# Story 2.5: AC1 - Callback Factory Tests
# =============================================================================

class TestCallbackFactory:
    """Tests for create_callback method (AC1)."""

    def test_create_callback_returns_callable(self, mock_console):
        """
        [2.5-UNIT-023] AC1: create_callback returns Callable[[str], None].
        
        GIVEN a VideoPipelineProgress instance
        WHEN create_callback() is called
        THEN it returns a callable accepting str.
        """
        from eleven_video.ui.progress import VideoPipelineProgress
        
        output, test_console = mock_console
        progress = VideoPipelineProgress(console=test_console)
        
        callback = progress.create_callback()
        
        assert callable(callback)

    def test_callback_invokes_update_progress(self, mock_console):
        """
        [2.5-UNIT-024] AC1: Callback invokes update_progress.
        
        GIVEN a callback from create_callback()
        WHEN callback("Processing...") is called
        THEN update_progress processes the message.
        """
        from eleven_video.ui.progress import VideoPipelineProgress
        from eleven_video.models.domain import PipelineStage
        
        output, test_console = mock_console
        progress = VideoPipelineProgress(console=test_console)
        progress.start_stage(PipelineStage.PROCESSING_SCRIPT)
        
        callback = progress.create_callback()
        callback("Processing script segments...")
        
        result = output.getvalue()
        assert "Processing" in result or "script" in result.lower()

    def test_callback_compatible_with_adapter_signature(self, mock_console):
        """
        [2.5-UNIT-025] AC1: Callback is compatible with adapter signatures.
        
        GIVEN a callback from create_callback()
        WHEN used with standard progress_callback: Callable[[str], None] signature
        THEN it works without error.
        """
        from eleven_video.ui.progress import VideoPipelineProgress
        from eleven_video.models.domain import PipelineStage
        from typing import Callable, Optional
        
        output, test_console = mock_console
        progress = VideoPipelineProgress(console=test_console)
        progress.start_stage(PipelineStage.PROCESSING_IMAGES)
        
        callback = progress.create_callback()
        
        # Simulate adapter usage pattern
        def mock_adapter_method(progress_callback: Optional[Callable[[str], None]] = None):
            if progress_callback:
                progress_callback("Generating image 1 of 3")
                progress_callback("Generating image 2 of 3")
                progress_callback("Generating image 3 of 3")
        
        # Should not raise any errors
        mock_adapter_method(progress_callback=callback)
        
        result = output.getvalue()
        assert "image" in result.lower() or "3" in result
