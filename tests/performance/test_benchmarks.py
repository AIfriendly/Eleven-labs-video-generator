"""
Performance benchmark tests for NFR validation.

Tests validate the following NFR thresholds from PRD:
- Startup time: <10 seconds
- Video generation: <5 minutes (mocked test)
- Success rate: 80% target
"""

import subprocess
import time
from unittest.mock import Mock, patch

import pytest

from eleven_video.monitoring import SuccessRateTracker


class TestStartupTimeBenchmark:
    """NFR: Terminal startup time <10 seconds."""

    def test_cli_help_startup_time_under_10_seconds(self):
        """
        [NFR-PERF-001] CLI startup time must be under 10 seconds.

        GIVEN the eleven-video CLI is installed
        WHEN I run the --help command
        THEN it completes in under 10 seconds
        """
        start_time = time.time()

        result = subprocess.run(
            ["uv", "run", "eleven-video", "--help"],
            capture_output=True,
            text=True,
            timeout=15,  # Allow extra time but expect <10s
        )

        elapsed_time = time.time() - start_time

        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        assert elapsed_time < 10.0, (
            f"Startup time {elapsed_time:.2f}s exceeds 10s threshold"
        )
        # Record actual time for baseline
        print(f"\n✅ CLI startup time: {elapsed_time:.2f}s (threshold: <10s)")

    def test_cli_version_startup_time(self):
        """
        [NFR-PERF-002] CLI version check also under 10 seconds.

        GIVEN the eleven-video CLI is installed
        WHEN I run the --version command
        THEN it completes in under 10 seconds
        """
        start_time = time.time()

        result = subprocess.run(
            ["uv", "run", "eleven-video", "--version"],
            capture_output=True,
            text=True,
            timeout=15,
        )

        elapsed_time = time.time() - start_time

        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        assert elapsed_time < 10.0, (
            f"Startup time {elapsed_time:.2f}s exceeds 10s threshold"
        )
        print(f"\n✅ CLI version time: {elapsed_time:.2f}s (threshold: <10s)")


class TestVideoGenerationTiming:
    """NFR: Video generation <5 minutes per video."""

    def test_video_generation_timing_mock(self):
        """
        [NFR-PERF-003] Video generation pipeline timing (mocked).

        GIVEN a mocked video generation pipeline
        WHEN all stages complete
        THEN total time is tracked and under 5 minutes

        Note: Uses mocks since actual generation requires API keys.
        """
        from eleven_video.ui.progress import VideoPipelineProgress
        from eleven_video.models.domain import PipelineStage

        progress = VideoPipelineProgress()
        
        # Simulate pipeline execution with timing
        start_time = time.time()

        # Script generation (~20s in real scenario)
        progress.start_stage(PipelineStage.PROCESSING_SCRIPT)
        time.sleep(0.01)  # Simulate minimal work
        progress.complete_stage(PipelineStage.PROCESSING_SCRIPT)

        # TTS generation
        progress.start_stage(PipelineStage.PROCESSING_AUDIO)
        time.sleep(0.01)
        progress.complete_stage(PipelineStage.PROCESSING_AUDIO)

        # Image generation
        progress.start_stage(PipelineStage.PROCESSING_IMAGES)
        time.sleep(0.01)
        progress.complete_stage(PipelineStage.PROCESSING_IMAGES)

        # Video compilation
        progress.start_stage(PipelineStage.COMPILING_VIDEO)
        time.sleep(0.01)
        progress.complete_stage(PipelineStage.COMPILING_VIDEO)

        elapsed_time = time.time() - start_time
        
        # In mocked test, should be very fast
        assert elapsed_time < 1.0, "Mocked pipeline took too long"
        assert progress.current_stage == PipelineStage.COMPILING_VIDEO
        
        print(f"\n✅ Mocked pipeline time: {elapsed_time:.3f}s")


class TestSuccessRateMonitoring:
    """NFR: 80% success rate for complete video generation."""

    def test_success_rate_calculation_100_percent(self):
        """
        [NFR-PERF-004] Success rate tracking with 100% success.

        GIVEN a success rate tracker
        WHEN 10 operations succeed
        THEN success rate is 100%
        """
        tracker = SuccessRateTracker()

        for _ in range(10):
            tracker.record_success()

        assert tracker.success_rate == 100.0
        assert tracker.total_attempts == 10
        assert tracker.successful_attempts == 10
        assert tracker.meets_threshold(80.0) is True

    def test_success_rate_calculation_80_percent(self):
        """
        [NFR-PERF-005] Success rate at exactly 80% threshold.

        GIVEN a success rate tracker
        WHEN 8 operations succeed and 2 fail
        THEN success rate is exactly 80%
        """
        tracker = SuccessRateTracker()

        for _ in range(8):
            tracker.record_success()
        for _ in range(2):
            tracker.record_failure()

        assert tracker.success_rate == 80.0
        assert tracker.meets_threshold(80.0) is True

    def test_success_rate_below_threshold(self):
        """
        [NFR-PERF-006] Success rate below 80% threshold.

        GIVEN a success rate tracker
        WHEN 7 operations succeed and 3 fail
        THEN success rate is 70% (below threshold)
        """
        tracker = SuccessRateTracker()

        for _ in range(7):
            tracker.record_success()
        for _ in range(3):
            tracker.record_failure()

        assert tracker.success_rate == 70.0
        assert tracker.meets_threshold(80.0) is False

    def test_success_rate_zero_attempts(self):
        """
        [NFR-PERF-007] Success rate with zero attempts.

        GIVEN a fresh success rate tracker
        WHEN no operations have been recorded
        THEN success rate is 0%
        """
        from eleven_video.monitoring import SuccessRateTracker

        tracker = SuccessRateTracker()

        assert tracker.success_rate == 0.0
        assert tracker.total_attempts == 0
