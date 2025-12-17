"""
Success rate monitoring for video generation operations.

This module provides tracking for the 80% success rate NFR threshold.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class SuccessRateTracker:
    """
    Tracks success rate for video generation operations.

    Used to monitor the 80% success rate NFR threshold from PRD.

    Example:
        tracker = SuccessRateTracker()
        tracker.record_success()
        tracker.record_success()
        tracker.record_failure()
        print(f"Success rate: {tracker.success_rate}%")  # 66.67%
    """

    _successful: int = field(default=0, init=False)
    _failed: int = field(default=0, init=False)

    def record_success(self) -> None:
        """Record a successful video generation operation."""
        self._successful += 1

    def record_failure(self, error: Optional[Exception] = None) -> None:
        """
        Record a failed video generation operation.

        Args:
            error: Optional exception that caused the failure.
        """
        self._failed += 1

    @property
    def total_attempts(self) -> int:
        """Total number of recorded attempts."""
        return self._successful + self._failed

    @property
    def successful_attempts(self) -> int:
        """Number of successful attempts."""
        return self._successful

    @property
    def failed_attempts(self) -> int:
        """Number of failed attempts."""
        return self._failed

    @property
    def success_rate(self) -> float:
        """
        Calculate success rate as percentage.

        Returns:
            Success rate from 0.0 to 100.0. Returns 0.0 if no attempts.
        """
        if self.total_attempts == 0:
            return 0.0
        return (self._successful / self.total_attempts) * 100.0

    def meets_threshold(self, threshold: float = 80.0) -> bool:
        """
        Check if success rate meets the given threshold.

        Args:
            threshold: Minimum success rate percentage (default: 80.0 from PRD)

        Returns:
            True if success rate >= threshold
        """
        return self.success_rate >= threshold

    def reset(self) -> None:
        """Reset all counters to zero."""
        self._successful = 0
        self._failed = 0

    def summary(self) -> str:
        """
        Get a human-readable summary of the success rate.

        Returns:
            Summary string with success rate and counts.
        """
        return (
            f"Success Rate: {self.success_rate:.1f}% "
            f"({self.successful_attempts}/{self.total_attempts} successful)"
        )
