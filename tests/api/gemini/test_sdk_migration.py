"""
Tests for Gemini API adapter - SDK Migration (Story 2.3).

Test IDs: 2.3-SDK-001 to 2.3-SDK-002
Tests verify the SDK migration from google-generativeai to google-genai.
"""
import pytest
from unittest.mock import MagicMock, patch


class TestSDKMigration:
    """Tests for SDK migration from google-generativeai to google-genai."""

    def test_new_sdk_client_initialization(self):
        """
        [2.3-SDK-002] SDK migration: New Client pattern used.
        
        GIVEN the GeminiAdapter class
        WHEN initializing with an API key
        THEN it should use genai.Client(api_key=...) instead of genai.configure().
        """
        with patch("google.genai.Client") as mock_client:
            from eleven_video.api.gemini import GeminiAdapter
            
            adapter = GeminiAdapter(api_key="test-key")
            
            # Verify new SDK pattern is used
            mock_client.assert_called_once_with(api_key="test-key")

    def test_sdk_migration_generate_script_still_works(self, mock_genai_new_sdk):
        """
        [2.3-SDK-001] SDK migration: generate_script() works after migration.
        
        GIVEN the SDK has been migrated to google-genai
        WHEN generate_script() is called
        THEN it should return a Script domain model.
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import Script
        
        mock_client_cls, mock_client, mock_response = mock_genai_new_sdk
        
        adapter = GeminiAdapter(api_key="test-key")
        script = adapter.generate_script("Create a video about mountains")
        
        assert isinstance(script, Script)
        assert len(script.content) > 0
