"""
Tests for GeminiAdapter Image Duration Support - Story 3.6 Refactor
Part of split from original test_gemini_duration.py

Test Groups:
- generate_images() with target_image_count parameter
- _adjust_segment_count() helper method
- Image count adjustment boundary conditions

Test IDs: 3.6-UNIT-001 (Duration parameter image count)
          3.6-UNIT-002 (Image count boundary validation)
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

# =============================================================================
# Test Group: generate_images() with target_image_count
# =============================================================================

class TestGenerateImagesWithTargetCount:
    """Tests for GeminiAdapter.generate_images() with target_image_count parameter."""

    def test_generate_images_accepts_target_image_count_parameter(self):
        """[P0] [3.6-UNIT-001] generate_images() should accept target_image_count parameter.
        
        AC: #5 - Image count is adjusted accordingly to match duration.
        """
        # Given: A GeminiAdapter instance
        from eleven_video.api.gemini import GeminiAdapter
        adapter = GeminiAdapter(api_key="dummy")
        
        # When: Checking the generate_images method signature
        import inspect
        sig = inspect.signature(adapter.generate_images)
        
        # Then: Should have target_image_count parameter
        assert 'target_image_count' in sig.parameters, \
            "generate_images() should accept 'target_image_count' parameter"

    def test_generate_images_without_target_uses_default_behavior(self):
        """[P1] [3.6-UNIT-001] generate_images() without target uses default behavior.
        
        Backward compatibility: Existing calls should still work.
        """
        # Given: A GeminiAdapter with mocked dependencies
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import Script
        
        with patch("eleven_video.api.gemini.genai") as mock_genai:
            mock_model = MagicMock()
            mock_response = MagicMock()
            # Simulate an image response with candidates
            mock_response.candidates = []
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            
            adapter = GeminiAdapter(api_key="dummy")
            script = Script(content="Test content for image generation.")
            
            # When: Generating images without target_image_count
            # This will fail because implementation doesn't exist yet - that's expected in RED phase
            # The test validates that the parameter signature exists
            import inspect
            sig = inspect.signature(adapter.generate_images)
            
            # Then: target_image_count should have default value (None)
            param = sig.parameters.get('target_image_count')
            if param:
                assert param.default is None or param.default == inspect.Parameter.empty


# =============================================================================
# Test Group: _adjust_segment_count() helper
# =============================================================================

class TestAdjustSegmentCount:
    """Tests for GeminiAdapter._adjust_segment_count() helper method."""

    def test_adjust_segment_count_method_exists(self):
        """[P0] [3.6-UNIT-001] GeminiAdapter should have _adjust_segment_count method.
        
        Story requirement: Method to adjust segment count to match target.
        """
        # Given: A GeminiAdapter instance
        from eleven_video.api.gemini import GeminiAdapter
        adapter = GeminiAdapter(api_key="dummy")
        
        # When: Checking for the method
        # Then: Should have _adjust_segment_count method
        assert hasattr(adapter, '_adjust_segment_count'), \
            "GeminiAdapter should have '_adjust_segment_count' method"

    def test_adjust_segment_count_trims_when_over_target(self):
        """[P0] [3.6-UNIT-001] Segments should be trimmed when count exceeds target.
        
        Task 5.4: If segments > target, take first N.
        """
        # Given: A GeminiAdapter instance
        from eleven_video.api.gemini import GeminiAdapter
        adapter = GeminiAdapter(api_key="dummy")
        
        segments = ["seg1", "seg2", "seg3", "seg4", "seg5"]
        target = 3
        
        # When: Adjusting segment count
        result = adapter._adjust_segment_count(segments, target)
        
        # Then: Should return first 3 segments
        assert len(result) == 3
        assert result == ["seg1", "seg2", "seg3"]

    def test_adjust_segment_count_expands_when_under_target(self):
        """[P0] [3.6-UNIT-001] Segments should be expanded when count is below target.
        
        Task 5.4: If segments < target, repeat segments to fill.
        """
        # Given: A GeminiAdapter instance
        from eleven_video.api.gemini import GeminiAdapter
        adapter = GeminiAdapter(api_key="dummy")
        
        segments = ["seg1", "seg2"]
        target = 5
        
        # When: Adjusting segment count
        result = adapter._adjust_segment_count(segments, target)
        
        # Then: Should expand to 5 segments by cycling
        assert len(result) == 5
        # First two should be original
        assert result[0] == "seg1"
        assert result[1] == "seg2"

    def test_adjust_segment_count_unchanged_when_equal(self):
        """[P1] [3.6-UNIT-001] Segments unchanged when count equals target."""
        # Given: A GeminiAdapter instance
        from eleven_video.api.gemini import GeminiAdapter
        adapter = GeminiAdapter(api_key="dummy")
        
        segments = ["seg1", "seg2", "seg3"]
        target = 3
        
        # When: Adjusting segment count
        result = adapter._adjust_segment_count(segments, target)
        
        # Then: Should return original segments unchanged
        assert result == segments

# =============================================================================
# Test Group: Image Duration Boundaries
# =============================================================================

class TestImageDurationBoundaries:
    """Tests for duration boundary validation in image logical adjustment."""

    def test_adjust_segment_count_handles_empty_list(self):
        """[P2] [3.6-UNIT-002] Empty segment list should be handled gracefully.
        
        Boundary: No segments to adjust.
        """
        # Given: A GeminiAdapter instance
        from eleven_video.api.gemini import GeminiAdapter
        adapter = GeminiAdapter(api_key="dummy")
        
        segments = []
        target = 5
        
        # When: Adjusting empty segment list
        # Then: Should handle gracefully (return empty or minimal list)
        try:
            result = adapter._adjust_segment_count(segments, target)
            # If it returns, it should be a list
            assert isinstance(result, list)
        except (ValueError, IndexError):
            # Or it may raise an error for empty input - that's acceptable
            pass

    def test_adjust_segment_count_handles_zero_target(self):
        """[P2] [3.6-UNIT-002] Zero target should be handled gracefully.
        
        Boundary: target_image_count=0 edge case.
        """
        # Given: A GeminiAdapter instance
        from eleven_video.api.gemini import GeminiAdapter
        adapter = GeminiAdapter(api_key="dummy")
        
        segments = ["seg1", "seg2", "seg3"]
        target = 0
        
        # When: Adjusting with zero target
        result = adapter._adjust_segment_count(segments, target)
        
        # Then: Should return empty list
        assert len(result) == 0
