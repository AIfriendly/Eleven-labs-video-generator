import pytest
from rich.console import Console
from rich.table import Table
from eleven_video.ui.quota_display import QuotaDisplay
from eleven_video.models.quota import QuotaInfo

@pytest.fixture
def console():
    return Console(force_terminal=True)

def test_quota_display_rendering(console):
    """Verifies that QuotaDisplay renders a table with correct data."""
    quotas = [
        QuotaInfo(service="ElevenLabs", used=100, limit=1000, unit="chars", reset_date=None),
        QuotaInfo(service="Gemini", used=None, limit=None, unit="rpm", reset_date=None)
    ]
    
    display = QuotaDisplay(quotas)
    
    # Capture rendering
    with console.capture() as capture:
        console.print(display)
    
    output = capture.get()
    
    assert "ElevenLabs" in output
    assert "100 / 1000 chars" in output
    assert "10.0%" in output
    assert "Gemini" in output
    assert "Unavailable" in output or "Unknown" in output # AC #2 fallback

def test_quota_display_color_coding(console):
    """Verifies color coding logic for high usage."""
    # > 90% usage -> Red
    critical_quota = QuotaInfo(service="Critical", used=950, limit=1000, unit="chars", reset_date=None)
    display = QuotaDisplay([critical_quota])
    
    with console.capture() as capture:
        console.print(display)
    output = capture.get()
    
    # Check for red style (implementation dependent, but conceptually strict)
    # Rich often uses ANSI codes, but we can verify logic via method if we expose it,
    # or rely on simple string presence if we test _get_color logic directly.
    # For now, let's assume visual inspection via "red" or similar color name isn't easy in plaintext capture
    # unless we check markup.
    
    # Better: Test the color logic method directly if possible, or verify style tags if using console.print(markup=True)
    # This test acts as a placeholder for the color logic verification.
    assert display.get_usage_color(critical_quota) == "red"
    
    # > 80% usage -> Yellow
    warning_quota = QuotaInfo(service="Warning", used=850, limit=1000, unit="chars", reset_date=None)
    display_warn = QuotaDisplay([warning_quota])
    assert display_warn.get_usage_color(warning_quota) == "yellow"
    
    # < 80% usage -> Green
    ok_quota = QuotaInfo(service="OK", used=100, limit=1000, unit="chars", reset_date=None)
    display_ok = QuotaDisplay([ok_quota])
    assert display_ok.get_usage_color(ok_quota) == "green"
