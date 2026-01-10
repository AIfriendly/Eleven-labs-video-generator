"""Unit tests for QuotaInfo domain model (Story 5.4 - Test Automation Expansion).

Tests computed properties: percent_used, is_available, remaining.
Priority: P2 (edge case coverage)
"""
import pytest
from datetime import datetime
from eleven_video.models.quota import QuotaInfo


class TestQuotaInfoPercentUsed:
    """[P2] Tests for QuotaInfo.percent_used property."""

    def test_percent_used_normal_calculation(self):
        """Verifies percentage calculation with valid used/limit values."""
        # GIVEN: QuotaInfo with 250 used of 1000 limit
        quota = QuotaInfo(
            service="Test", used=250, limit=1000, unit="chars", reset_date=None
        )

        # WHEN: Accessing percent_used
        result = quota.percent_used

        # THEN: Should be 25.0%
        assert result == 25.0

    def test_percent_used_zero_usage(self):
        """Verifies 0% when no quota used."""
        # GIVEN: QuotaInfo with 0 used
        quota = QuotaInfo(
            service="Test", used=0, limit=1000, unit="chars", reset_date=None
        )

        # WHEN: Accessing percent_used
        result = quota.percent_used

        # THEN: Should be 0.0%
        assert result == 0.0

    def test_percent_used_full_usage(self):
        """Verifies 100% when fully consumed."""
        # GIVEN: QuotaInfo at limit
        quota = QuotaInfo(
            service="Test", used=1000, limit=1000, unit="chars", reset_date=None
        )

        # WHEN: Accessing percent_used
        result = quota.percent_used

        # THEN: Should be 100.0%
        assert result == 100.0

    def test_percent_used_over_limit(self):
        """Verifies >100% when over limit (edge case)."""
        # GIVEN: QuotaInfo over limit
        quota = QuotaInfo(
            service="Test", used=1200, limit=1000, unit="chars", reset_date=None
        )

        # WHEN: Accessing percent_used
        result = quota.percent_used

        # THEN: Should be 120.0%
        assert result == 120.0

    def test_percent_used_none_when_used_is_none(self):
        """Verifies None returned when used is None."""
        # GIVEN: QuotaInfo with None used
        quota = QuotaInfo(
            service="Test", used=None, limit=1000, unit="chars", reset_date=None
        )

        # WHEN: Accessing percent_used
        result = quota.percent_used

        # THEN: Should be None
        assert result is None

    def test_percent_used_none_when_limit_is_none(self):
        """Verifies None returned when limit is None."""
        # GIVEN: QuotaInfo with None limit
        quota = QuotaInfo(
            service="Test", used=500, limit=None, unit="chars", reset_date=None
        )

        # WHEN: Accessing percent_used
        result = quota.percent_used

        # THEN: Should be None
        assert result is None

    def test_percent_used_none_when_limit_is_zero(self):
        """Verifies None returned when limit is 0 (avoids division by zero)."""
        # GIVEN: QuotaInfo with 0 limit
        quota = QuotaInfo(
            service="Test", used=0, limit=0, unit="chars", reset_date=None
        )

        # WHEN: Accessing percent_used
        result = quota.percent_used

        # THEN: Should be None (not ZeroDivisionError)
        assert result is None


class TestQuotaInfoIsAvailable:
    """[P2] Tests for QuotaInfo.is_available property."""

    def test_is_available_true_when_limit_known(self):
        """Verifies True when limit is set."""
        # GIVEN: QuotaInfo with a limit
        quota = QuotaInfo(
            service="Test", used=500, limit=1000, unit="chars", reset_date=None
        )

        # WHEN: Checking is_available
        result = quota.is_available

        # THEN: Should be True
        assert result is True

    def test_is_available_false_when_limit_is_none(self):
        """Verifies False when limit is None (service unavailable)."""
        # GIVEN: QuotaInfo with None limit
        quota = QuotaInfo(
            service="Test", used=None, limit=None, unit="chars", reset_date=None
        )

        # WHEN: Checking is_available
        result = quota.is_available

        # THEN: Should be False
        assert result is False

    def test_is_available_true_when_limit_is_zero(self):
        """Verifies True even when limit is 0 (known limit, just exhausted)."""
        # GIVEN: QuotaInfo with 0 limit (exhausted tier)
        quota = QuotaInfo(
            service="Test", used=0, limit=0, unit="chars", reset_date=None
        )

        # WHEN: Checking is_available
        result = quota.is_available

        # THEN: Should be True (limit IS known)
        assert result is True


class TestQuotaInfoRemaining:
    """[P2] Tests for QuotaInfo.remaining property."""

    def test_remaining_normal_calculation(self):
        """Verifies remaining calculation with valid values."""
        # GIVEN: QuotaInfo with 250 used of 1000 limit
        quota = QuotaInfo(
            service="Test", used=250, limit=1000, unit="chars", reset_date=None
        )

        # WHEN: Accessing remaining
        result = quota.remaining

        # THEN: Should be 750
        assert result == 750

    def test_remaining_zero_when_at_limit(self):
        """Verifies 0 remaining when fully consumed."""
        # GIVEN: QuotaInfo at limit
        quota = QuotaInfo(
            service="Test", used=1000, limit=1000, unit="chars", reset_date=None
        )

        # WHEN: Accessing remaining
        result = quota.remaining

        # THEN: Should be 0
        assert result == 0

    def test_remaining_negative_when_over_limit(self):
        """Verifies negative remaining when over limit."""
        # GIVEN: QuotaInfo over limit
        quota = QuotaInfo(
            service="Test", used=1200, limit=1000, unit="chars", reset_date=None
        )

        # WHEN: Accessing remaining
        result = quota.remaining

        # THEN: Should be -200 (over quota)
        assert result == -200

    def test_remaining_none_when_used_is_none(self):
        """Verifies None returned when used is None."""
        # GIVEN: QuotaInfo with None used
        quota = QuotaInfo(
            service="Test", used=None, limit=1000, unit="chars", reset_date=None
        )

        # WHEN: Accessing remaining
        result = quota.remaining

        # THEN: Should be None
        assert result is None

    def test_remaining_none_when_limit_is_none(self):
        """Verifies None returned when limit is None."""
        # GIVEN: QuotaInfo with None limit
        quota = QuotaInfo(
            service="Test", used=500, limit=None, unit="chars", reset_date=None
        )

        # WHEN: Accessing remaining
        result = quota.remaining

        # THEN: Should be None
        assert result is None
