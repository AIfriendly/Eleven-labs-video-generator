"""Integration tests for VideoPipeline usage display integration (Story 5.3).

Tests verify that the VideoPipeline correctly interacts with the UsageDisplay component
to show consumption data at the end of a session, and handles display errors gracefully.

Test IDs: [5.3-INT-004] through [5.3-INT-005]
"""
import pytest
from unittest.mock import MagicMock, patch
from eleven_video.orchestrator.video_pipeline import VideoPipeline

class TestPipelineUsageIntegration:
    """Integration tests for VideoPipeline usage display logic."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings for pipeline instantiation."""
        mock = MagicMock()
        mock.elevenlabs_api_key.get_secret_value.return_value = "test-key"
        mock.gemini_api_key.get_secret_value.return_value = "test-key"
        return mock

    @pytest.fixture
    def mock_monitor_with_usage(self):
        """Create a mock UsageMonitor that reports non-zero usage."""
        # Story 5.3: Pipeline only prints summary if events_count > 0
        summary = {
            "total_cost": 0.50,
            "events_count": 5,
            "by_service": {"gemini": {"cost": 0.50}},
            "by_model": {}
        }
        mock = MagicMock()
        mock.get_summary.return_value = summary
        return mock

    def test_pipeline_invokes_usage_display_at_session_end(self, mock_settings, mock_monitor_with_usage):
        """[5.3-INT-004][P1] Verify pipeline invokes UsageDisplay at session end.
        
        GIVEN: A VideoPipeline instance with tracked usage
        WHEN: _print_final_usage_summary is called (simulating session end)
        THEN: UsageDisplay.render_once() is called exactly once
        """
        # GIVEN: Pipeline with mocked settings
        pipeline = VideoPipeline(settings=mock_settings)
        
        # Patch UsageMonitor to return valid usage
        with patch("eleven_video.orchestrator.video_pipeline.UsageMonitor.get_instance", 
                   return_value=mock_monitor_with_usage):
            
            # Patch UsageDisplay to verify invocation
            with patch("eleven_video.orchestrator.video_pipeline.UsageDisplay") as MockDisplay:
                mock_display_instance = MockDisplay.return_value
                
                # WHEN: Session ends (simulated by calling _print_final_usage_summary)
                pipeline._print_final_usage_summary()
                
                # THEN: UsageDisplay should be instantiated and rendered
                MockDisplay.assert_called()
                mock_display_instance.render_once.assert_called_once()

    def test_pipeline_handles_usage_display_errors(self, mock_settings, mock_monitor_with_usage):
        """[5.3-INT-005][P2] Verify pipeline survives UsageDisplay errors.
        
        GIVEN: A VideoPipeline where UsageDisplay raises an error
        WHEN: _print_final_usage_summary is called
        THEN: The error is caught and does not crash the pipeline
        """
        pipeline = VideoPipeline(settings=mock_settings)
        
        with patch("eleven_video.orchestrator.video_pipeline.UsageMonitor.get_instance", 
                   return_value=mock_monitor_with_usage):
            
            with patch("eleven_video.orchestrator.video_pipeline.UsageDisplay") as MockDisplay:
                mock_display_instance = MockDisplay.return_value
                # Simulate a rendering error
                mock_display_instance.render_once.side_effect = Exception("Rendering failed")
                
                # WHEN: Session ends
                try:
                    pipeline._print_final_usage_summary()
                except Exception as e:
                    # THEN: Should not raise the rendering exception
                    pytest.fail(f"Pipeline crashed on usage display error: {e}")
                
                # Verify attempted call
                mock_display_instance.render_once.assert_called_once()
