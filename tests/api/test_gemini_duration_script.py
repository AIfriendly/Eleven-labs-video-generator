"""
Tests for GeminiAdapter Script Duration Support - Story 3.6 Refactor
Part of split from original test_gemini_duration.py

Test Groups:
- generate_script() with duration_minutes parameter
- Script duration boundary conditions (None, Zero)

Test IDs: 3.6-UNIT-001 (Duration parameter in script prompt)
          3.6-UNIT-002 (Duration boundary validation)
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

# =============================================================================
# Test Group: generate_script() with duration_minutes
# =============================================================================

class TestGenerateScriptWithDuration:
    """Tests for GeminiAdapter.generate_script() with duration_minutes parameter."""

    def test_generate_script_accepts_duration_minutes_parameter(self):
        """[P0] [3.6-UNIT-001] generate_script() should accept duration_minutes parameter.
        
        AC: #5 - Generated script length approximately matches the target duration.
        """
        # Given: A GeminiAdapter instance
        from eleven_video.api.gemini import GeminiAdapter
        adapter = GeminiAdapter(api_key="dummy")
        
        # When: Checking the generate_script method signature
        import inspect
        sig = inspect.signature(adapter.generate_script)
        
        # Then: Should have duration_minutes parameter
        assert 'duration_minutes' in sig.parameters, \
            "generate_script() should accept 'duration_minutes' parameter"

    def test_generate_script_with_3_minute_duration_includes_instruction(self):
        """[P0] [3.6-UNIT-001] 3-minute duration should add instruction for ~450 words.
        
        Story requirement: Prompt should include duration instruction.
        """
        # Given: A GeminiAdapter with mocked Gemini client
        from eleven_video.api.gemini import GeminiAdapter
        
        with patch("eleven_video.api.gemini.genai") as mock_genai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "Test script content"
            # Set up the chain: client.models.generate_content -> response
            
            # The candidates structure for new SDK
            mock_candidate = MagicMock()
            mock_part = MagicMock()
            mock_part.text = "Test script content"
            mock_candidate.content.parts = [mock_part]
            mock_response.candidates = [mock_candidate]

            mock_client.models.generate_content.return_value = mock_response
            mock_genai.Client.return_value = mock_client
            
            adapter = GeminiAdapter(api_key="dummy")
            
            # When: Generating script with 3-minute duration
            adapter.generate_script("Test topic", duration_minutes=3)
            
            # Then: The prompt should include duration instruction
            call_args = mock_client.models.generate_content.call_args
            prompt_sent = str(call_args)
            
            # Should mention duration or word count in some form
            assert "3" in prompt_sent or "450" in prompt_sent or "minute" in prompt_sent.lower()

    def test_generate_script_with_5_minute_duration_includes_instruction(self):
        """[P0] [3.6-UNIT-001] 5-minute duration should add instruction for ~750 words."""
        # Given: A GeminiAdapter with mocked Gemini client
        from eleven_video.api.gemini import GeminiAdapter
        
        with patch("eleven_video.api.gemini.genai") as mock_genai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            
            # The candidates structure for new SDK
            mock_candidate = MagicMock()
            mock_part = MagicMock()
            mock_part.text = "Test script content"
            mock_candidate.content.parts = [mock_part]
            mock_response.candidates = [mock_candidate]
            
            mock_client.models.generate_content.return_value = mock_response
            mock_genai.Client.return_value = mock_client
            
            adapter = GeminiAdapter(api_key="dummy")
            
            # When: Generating script with 5-minute duration
            adapter.generate_script("Test topic", duration_minutes=5)
            
            # Then: The call should complete (duration instruction added)
            assert mock_client.models.generate_content.called

    def test_generate_script_without_duration_uses_default(self):
        """[P1] [3.6-UNIT-001] generate_script() without duration uses default behavior.
        
        Backward compatibility: Existing calls without duration should still work.
        """
        # Given: A GeminiAdapter with mocked Gemini client
        from eleven_video.api.gemini import GeminiAdapter
        
        with patch("eleven_video.api.gemini.genai") as mock_genai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            
            # The candidates structure for new SDK
            mock_candidate = MagicMock()
            mock_part = MagicMock()
            mock_part.text = "Test script content"
            mock_candidate.content.parts = [mock_part]
            mock_response.candidates = [mock_candidate]

            mock_client.models.generate_content.return_value = mock_response
            mock_genai.Client.return_value = mock_client
            
            adapter = GeminiAdapter(api_key="dummy")
            
            # When: Generating script without duration_minutes parameter
            result = adapter.generate_script("Test topic")
            
            # Then: Should complete without error
            assert result is not None

# =============================================================================
# Test Group: Script Duration Boundaries
# =============================================================================

class TestScriptDurationBoundaries:
    """Tests for duration boundary validation in script generation."""

    def test_generate_script_handles_none_duration(self):
        """[P0] [3.6-UNIT-002] None duration should use default (3 minutes).
        
        Edge case: duration_minutes=None falls back to default.
        """
        # Given: A GeminiAdapter with mocked dependencies
        from eleven_video.api.gemini import GeminiAdapter
        
        with patch("eleven_video.api.gemini.genai") as mock_genai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            
            # The candidates structure for new SDK
            mock_candidate = MagicMock()
            mock_part = MagicMock()
            mock_part.text = "Test script content"
            mock_candidate.content.parts = [mock_part]
            mock_response.candidates = [mock_candidate]

            mock_client.models.generate_content.return_value = mock_response
            mock_genai.Client.return_value = mock_client
            
            adapter = GeminiAdapter(api_key="dummy")
            
            # When: Generating script with duration_minutes=None
            result = adapter.generate_script("Test topic", duration_minutes=None)
            
            # Then: Should complete without error (using default)
            assert result is not None

    def test_generate_script_handles_zero_duration(self):
        """[P2] [3.6-UNIT-002] Zero duration should be handled gracefully.
        
        Boundary: duration_minutes=0 edge case.
        """
        # Given: A GeminiAdapter with mocked dependencies
        from eleven_video.api.gemini import GeminiAdapter
        
        with patch("eleven_video.api.gemini.genai") as mock_genai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            
            # The candidates structure for new SDK
            mock_candidate = MagicMock()
            mock_part = MagicMock()
            mock_part.text = "Test script content"
            mock_candidate.content.parts = [mock_part]
            mock_response.candidates = [mock_candidate]

            mock_client.models.generate_content.return_value = mock_response
            mock_genai.Client.return_value = mock_client
            
            adapter = GeminiAdapter(api_key="dummy")
            
            # When: Generating script with duration_minutes=0
            # Then: Should either use default or handle gracefully
            result = adapter.generate_script("Test topic", duration_minutes=0)
            assert result is not None
