"""Extended component tests for QuotaDisplay (Story 5.4 - Test Automation Expansion).

Tests color threshold boundaries and edge cases.
Priority: P1-P2
"""
import pytest
from rich.console import Console
from eleven_video.ui.quota_display import QuotaDisplay
from eleven_video.models.quota import QuotaInfo


@pytest.fixture
def console():
    """Rich console with forced terminal for testing."""
    return Console(force_terminal=True)


class TestQuotaDisplayColorBoundaries:
    """[P1] Tests for exact color threshold boundaries (AC #3)."""

    def test_color_at_exactly_80_percent(self, console):
        """Verifies yellow color at exactly 80% usage threshold."""
        # GIVEN: QuotaInfo at exactly 80%
        quota = QuotaInfo(
            service="Boundary", used=800, limit=1000, unit="chars", reset_date=None
        )
        display = QuotaDisplay([quota])

        # WHEN: Getting usage color
        color = display.get_usage_color(quota)

        # THEN: Should be yellow (>= 80%)
        assert color == "yellow"

    def test_color_just_below_80_percent(self, console):
        """Verifies green color at 79.9% usage (just below threshold)."""
        # GIVEN: QuotaInfo at 79.9%
        quota = QuotaInfo(
            service="JustUnder", used=799, limit=1000, unit="chars", reset_date=None
        )
        display = QuotaDisplay([quota])

        # WHEN: Getting usage color
        color = display.get_usage_color(quota)

        # THEN: Should be green (< 80%)
        assert color == "green"

    def test_color_at_exactly_90_percent(self, console):
        """Verifies red color at exactly 90% usage threshold."""
        # GIVEN: QuotaInfo at exactly 90%
        quota = QuotaInfo(
            service="Critical", used=900, limit=1000, unit="chars", reset_date=None
        )
        display = QuotaDisplay([quota])

        # WHEN: Getting usage color
        color = display.get_usage_color(quota)

        # THEN: Should be red (>= 90%)
        assert color == "red"

    def test_color_just_below_90_percent(self, console):
        """Verifies yellow color at 89.9% usage (just below red threshold)."""
        # GIVEN: QuotaInfo at 89.9%
        quota = QuotaInfo(
            service="JustUnder", used=899, limit=1000, unit="chars", reset_date=None
        )
        display = QuotaDisplay([quota])

        # WHEN: Getting usage color
        color = display.get_usage_color(quota)

        # THEN: Should be yellow (>= 80% but < 90%)
        assert color == "yellow"

    def test_color_at_100_percent_exhausted(self, console):
        """Verifies red color when quota is fully exhausted."""
        # GIVEN: QuotaInfo at 100%
        quota = QuotaInfo(
            service="Exhausted", used=1000, limit=1000, unit="chars", reset_date=None
        )
        display = QuotaDisplay([quota])

        # WHEN: Getting usage color
        color = display.get_usage_color(quota)

        # THEN: Should be red (>= 90%)
        assert color == "red"

    def test_color_over_100_percent(self, console):
        """Verifies red color when over quota limit."""
        # GIVEN: QuotaInfo over limit
        quota = QuotaInfo(
            service="OverLimit", used=1200, limit=1000, unit="chars", reset_date=None
        )
        display = QuotaDisplay([quota])

        # WHEN: Getting usage color
        color = display.get_usage_color(quota)

        # THEN: Should be red
        assert color == "red"


class TestQuotaDisplayUnavailable:
    """[P2] Tests for unavailable/dim color states."""

    def test_color_dim_when_not_available(self, console):
        """Verifies dim color when quota info is unavailable."""
        # GIVEN: QuotaInfo with None limit (unavailable)
        quota = QuotaInfo(
            service="Unavailable", used=None, limit=None, unit="chars", reset_date=None
        )
        display = QuotaDisplay([quota])

        # WHEN: Getting usage color
        color = display.get_usage_color(quota)

        # THEN: Should be dim
        assert color == "dim"

    def test_color_dim_when_percent_used_is_none(self, console):
        """Verifies dim color when percent_used cannot be calculated."""
        # GIVEN: QuotaInfo with limit but no used value
        quota = QuotaInfo(
            service="PartialInfo", used=None, limit=1000, unit="chars", reset_date=None
        )
        display = QuotaDisplay([quota])

        # WHEN: Getting usage color
        color = display.get_usage_color(quota)

        # THEN: Should be dim (percent_used is None)
        assert color == "dim"


class TestQuotaDisplayEdgeCases:
    """[P2] Tests for edge cases and rendering scenarios."""

    def test_empty_quota_list_renders(self, console):
        """Verifies table renders correctly with empty quota list."""
        # GIVEN: Empty quota list
        display = QuotaDisplay([])

        # WHEN: Capturing render output
        with console.capture() as capture:
            console.print(display)

        output = capture.get()

        # THEN: Table header should still appear
        assert "API Quota Status" in output

    def test_single_service_renders(self, console):
        """Verifies table renders with single service."""
        # GIVEN: Single quota
        quota = QuotaInfo(
            service="OnlyOne", used=500, limit=1000, unit="chars", reset_date=None
        )
        display = QuotaDisplay([quota])

        # WHEN: Capturing render output
        with console.capture() as capture:
            console.print(display)

        output = capture.get()

        # THEN: Should display single service
        assert "OnlyOne" in output
        assert "500 / 1000 chars" in output
        assert "50.0%" in output

    def test_unavailable_service_shows_unavailable_text(self, console):
        """Verifies 'Unavailable' text for unavailable services."""
        # GIVEN: Unavailable quota
        quota = QuotaInfo(
            service="Down", used=None, limit=None, unit="rpm", reset_date=None
        )
        display = QuotaDisplay([quota])

        # WHEN: Capturing render output
        with console.capture() as capture:
            console.print(display)

        output = capture.get()

        # THEN: Should show Unavailable
        assert "Down" in output
        assert "Unavailable" in output

    def test_percent_shows_dash_when_unavailable(self, console):
        """Verifies dash shown for percentage when unavailable."""
        # GIVEN: Quota with no percent_used
        quota = QuotaInfo(
            service="NoPct", used=None, limit=1000, unit="chars", reset_date=None
        )
        display = QuotaDisplay([quota])

        # WHEN: Capturing render output
        with console.capture() as capture:
            console.print(display)

        output = capture.get()

        # THEN: Should show dash for percentage
        assert "—" in output or "-" in output
