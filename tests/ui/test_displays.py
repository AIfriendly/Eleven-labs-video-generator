"""
Tests for UI display components.

Test IDs: 1.5-UNIT-029 to 1.5-UNIT-037
Tests cover render_status_table and build_status_json functions.
"""
import pytest
from io import StringIO
from unittest.mock import patch

from eleven_video.api.interfaces import HealthResult, UsageResult


class TestRenderStatusTable:
    """Tests for render_status_table function."""

    def test_render_status_table_can_be_imported(self):
        """[1.5-UNIT-029] Function should be importable from displays module."""
        # Given: The displays module exists
        # When: render_status_table is imported
        from eleven_video.ui.displays import render_status_table
        # Then: It should not be None
        assert render_status_table is not None

    def test_render_status_table_with_multiple_services(self):
        """[1.5-UNIT-030] Should render table with multiple services."""
        # Given: Multiple services with different statuses
        from eleven_video.ui.displays import render_status_table
        from rich.console import Console
        
        services = [
            {
                "service_name": "TestService1",
                "health": HealthResult(status="ok", message="Connected", latency_ms=50.0),
                "usage": UsageResult(available=True, used=100, limit=1000, unit="chars", raw_data={})
            },
            {
                "service_name": "TestService2",
                "health": HealthResult(status="error", message="Failed", latency_ms=None),
                "usage": UsageResult(available=False, used=None, limit=None, unit=None, raw_data=None)
            }
        ]
        
        output = StringIO()
        test_console = Console(file=output, force_terminal=True)
        
        # When: render_status_table is called
        with patch("eleven_video.ui.displays.console", test_console):
            render_status_table(services)
        
        # Then: Both services should appear in output
        result = output.getvalue()
        assert "TestService1" in result
        assert "TestService2" in result

    def test_render_status_table_empty_list(self):
        """[1.5-UNIT-031] Should handle empty services list."""
        # Given: An empty services list
        from eleven_video.ui.displays import render_status_table
        from rich.console import Console
        
        output = StringIO()
        test_console = Console(file=output, force_terminal=True)
        
        # When: render_status_table is called with empty list
        with patch("eleven_video.ui.displays.console", test_console):
            render_status_table([])
        
        # Then: Table header should still render
        result = output.getvalue()
        assert "Service" in result or "Status" in result

    def test_render_status_table_truncates_long_message(self):
        """[1.5-UNIT-032] Should truncate messages longer than 50 chars."""
        # Given: A service with a very long message
        from eleven_video.ui.displays import render_status_table
        from rich.console import Console
        
        long_message = "A" * 100
        services = [
            {
                "service_name": "Test",
                "health": HealthResult(status="ok", message=long_message, latency_ms=10.0),
                "usage": UsageResult(available=False, used=None, limit=None, unit=None, raw_data=None)
            }
        ]
        
        output = StringIO()
        test_console = Console(file=output, force_terminal=True)
        
        # When: render_status_table is called
        with patch("eleven_video.ui.displays.console", test_console):
            render_status_table(services)
        
        # Then: Full message shouldn't appear (truncated)
        result = output.getvalue()
        assert long_message not in result


class TestBuildStatusJson:
    """Tests for build_status_json function."""

    def test_build_status_json_can_be_imported(self):
        """[1.5-UNIT-033] Function should be importable from displays module."""
        # Given: The displays module exists
        # When: build_status_json is imported
        from eleven_video.ui.displays import build_status_json
        # Then: It should not be None
        assert build_status_json is not None

    def test_build_status_json_structure(self):
        """[1.5-UNIT-034] Should return dict with services key."""
        # Given: A service with complete data
        from eleven_video.ui.displays import build_status_json
        
        services = [
            {
                "service_name": "TestAPI",
                "health": HealthResult(status="ok", message="OK", latency_ms=25.0),
                "usage": UsageResult(available=True, used=500, limit=5000, unit="tokens", raw_data={})
            }
        ]
        
        # When: build_status_json is called
        result = build_status_json(services)
        
        # Then: Result should have correct structure
        assert "services" in result
        assert len(result["services"]) == 1
        assert result["services"][0]["name"] == "TestAPI"
        assert result["services"][0]["status"] == "ok"
        assert result["services"][0]["latency_ms"] == 25.0

    def test_build_status_json_usage_structure(self):
        """[1.5-UNIT-035] Should include usage data in correct structure."""
        # Given: A service with usage data
        from eleven_video.ui.displays import build_status_json
        
        services = [
            {
                "service_name": "Test",
                "health": HealthResult(status="ok", message="OK", latency_ms=10.0),
                "usage": UsageResult(available=True, used=100, limit=1000, unit="chars", raw_data={})
            }
        ]
        
        # When: build_status_json is called
        result = build_status_json(services)
        
        # Then: Usage data should be correctly structured
        usage = result["services"][0]["usage"]
        assert usage["available"] is True
        assert usage["used"] == 100
        assert usage["limit"] == 1000
        assert usage["unit"] == "chars"

    def test_build_status_json_empty_list(self):
        """[1.5-UNIT-036] Should handle empty services list."""
        # Given: An empty services list
        from eleven_video.ui.displays import build_status_json
        
        # When: build_status_json is called with empty list
        result = build_status_json([])
        
        # Then: Services array should be empty
        assert "services" in result
        assert result["services"] == []

    def test_build_status_json_serializable(self):
        """[1.5-UNIT-037] Output should be JSON serializable."""
        # Given: A service with None values
        import json
        from eleven_video.ui.displays import build_status_json
        
        services = [
            {
                "service_name": "API",
                "health": HealthResult(status="error", message="Failed", latency_ms=None),
                "usage": UsageResult(available=False, used=None, limit=None, unit=None, raw_data=None)
            }
        ]
        
        # When: build_status_json is called
        result = build_status_json(services)
        
        # Then: Result should be JSON serializable
        json_str = json.dumps(result)
        assert json_str is not None
