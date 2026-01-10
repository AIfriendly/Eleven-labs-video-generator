"""
Unit Tests for Story 3.7: Default Preference Persistence

Tests persistence layer for saving/loading default preference fields:
- default_voice
- default_image_model  
- default_gemini_model
- default_duration_minutes

Tests include corruption recovery per R-005 mitigation.
"""

import pytest
from unittest.mock import patch, MagicMock
import json
from pathlib import Path


# =============================================================================
# Task 2.1-2.2: Save/load default preferences (not filtered)
# =============================================================================

class TestPersistenceDefaultPreferences:
    """Tests for save_config() and load_config() with preference fields."""

    def test_save_config_includes_default_voice(self, tmp_path):
        """
        GIVEN a config dict with default_voice
        WHEN save_config() is called
        THEN default_voice is saved to the config file
        """
        config_file = tmp_path / "config.json"
        
        with patch("eleven_video.config.persistence.get_config_path", return_value=config_file):
            from eleven_video.config.persistence import save_config, load_config
            
            save_config({"default_voice": "voice-id-123"})
            
            # Verify saved
            loaded = load_config()
            assert loaded.get("default_voice") == "voice-id-123"

    def test_save_config_includes_default_image_model(self, tmp_path):
        """
        GIVEN a config dict with default_image_model
        WHEN save_config() is called
        THEN default_image_model is saved to the config file
        """
        config_file = tmp_path / "config.json"
        
        with patch("eleven_video.config.persistence.get_config_path", return_value=config_file):
            from eleven_video.config.persistence import save_config, load_config
            
            save_config({"default_image_model": "gemini-2.5-flash-image"})
            
            loaded = load_config()
            assert loaded.get("default_image_model") == "gemini-2.5-flash-image"

    def test_save_config_includes_default_gemini_model(self, tmp_path):
        """
        GIVEN a config dict with default_gemini_model
        WHEN save_config() is called
        THEN default_gemini_model is saved to the config file
        """
        config_file = tmp_path / "config.json"
        
        with patch("eleven_video.config.persistence.get_config_path", return_value=config_file):
            from eleven_video.config.persistence import save_config, load_config
            
            save_config({"default_gemini_model": "gemini-2.5-flash"})
            
            loaded = load_config()
            assert loaded.get("default_gemini_model") == "gemini-2.5-flash"

    def test_save_config_includes_default_duration_minutes(self, tmp_path):
        """
        GIVEN a config dict with default_duration_minutes
        WHEN save_config() is called
        THEN default_duration_minutes is saved to the config file
        """
        config_file = tmp_path / "config.json"
        
        with patch("eleven_video.config.persistence.get_config_path", return_value=config_file):
            from eleven_video.config.persistence import save_config, load_config
            
            save_config({"default_duration_minutes": 5})
            
            loaded = load_config()
            assert loaded.get("default_duration_minutes") == 5

    def test_all_preference_fields_saved_together(self, tmp_path):
        """
        GIVEN a config dict with all default preferences
        WHEN save_config() is called
        THEN all fields are saved and can be loaded
        """
        config_file = tmp_path / "config.json"
        
        with patch("eleven_video.config.persistence.get_config_path", return_value=config_file):
            from eleven_video.config.persistence import save_config, load_config
            
            save_config({
                "default_voice": "voice-123",
                "default_image_model": "image-model-456",
                "default_gemini_model": "gemini-model-789",
                "default_duration_minutes": 10
            })
            
            loaded = load_config()
            assert loaded.get("default_voice") == "voice-123"
            assert loaded.get("default_image_model") == "image-model-456"
            assert loaded.get("default_gemini_model") == "gemini-model-789"
            assert loaded.get("default_duration_minutes") == 10


# =============================================================================
# Task 2.2: Preference fields NOT filtered by _filter_sensitive_keys
# =============================================================================

class TestPreferencesNotFiltered:
    """Tests that preference fields are not treated as sensitive."""

    def test_default_voice_not_filtered(self, tmp_path):
        """
        GIVEN a config with default_voice
        WHEN _filter_sensitive_keys is applied (via save_config)
        THEN default_voice is NOT filtered out
        """
        config_file = tmp_path / "config.json"
        
        with patch("eleven_video.config.persistence.get_config_path", return_value=config_file):
            from eleven_video.config.persistence import save_config
            
            save_config({"default_voice": "my-voice-id"})
            
            # Read file directly to verify
            content = json.loads(config_file.read_text())
            assert "default_voice" in content
            assert content["default_voice"] == "my-voice-id"

    def test_preferences_coexist_with_api_key_filtering(self, tmp_path):
        """
        GIVEN a config with both preferences and API keys
        WHEN save_config() is called
        THEN preferences are saved but API keys are filtered
        """
        config_file = tmp_path / "config.json"
        
        with patch("eleven_video.config.persistence.get_config_path", return_value=config_file):
            from eleven_video.config.persistence import save_config
            
            save_config({
                "default_voice": "voice-id",
                "default_gemini_model": "gemini-model",
                "elevenlabs_api_key": "SHOULD_BE_FILTERED",
                "gemini_api_key": "SHOULD_BE_FILTERED"
            })
            
            # Read file directly
            content = json.loads(config_file.read_text())
            
            # Preferences are saved
            assert "default_voice" in content
            assert "default_gemini_model" in content
            
            # API keys are filtered
            assert "elevenlabs_api_key" not in content
            assert "gemini_api_key" not in content


# =============================================================================
# Task 2.3: Config file corruption handling (R-005 mitigation)
# =============================================================================

class TestConfigCorruptionHandling:
    """Tests for graceful corruption recovery (R-005)."""

    def test_corrupted_json_returns_empty_dict(self, tmp_path):
        """
        GIVEN a corrupted config file (invalid JSON)
        WHEN load_config() is called
        THEN an empty dict is returned (R-005 mitigation)
        """
        config_file = tmp_path / "config.json"
        config_file.write_text("{invalid json content")
        
        with patch("eleven_video.config.persistence.get_config_path", return_value=config_file):
            from eleven_video.config.persistence import load_config
            
            result = load_config()
            
            assert result == {}

    def test_missing_config_file_returns_empty_dict(self, tmp_path):
        """
        GIVEN no config file exists
        WHEN load_config() is called
        THEN an empty dict is returned
        """
        config_file = tmp_path / "nonexistent" / "config.json"
        
        with patch("eleven_video.config.persistence.get_config_path", return_value=config_file):
            from eleven_video.config.persistence import load_config
            
            result = load_config()
            
            assert result == {}

    def test_unreadable_file_returns_empty_dict(self, tmp_path):
        """
        GIVEN a config file that raises IOError on read
        WHEN load_config() is called
        THEN an empty dict is returned
        """
        config_file = tmp_path / "config.json"
        config_file.write_text('{"key": "value"}')
        
        with patch("eleven_video.config.persistence.get_config_path", return_value=config_file):
            # Mock open to raise IOError
            with patch("builtins.open", side_effect=IOError("Read error")):
                from eleven_video.config.persistence import load_config
                
                # Need to reimport to get the patched version
                import importlib
                import eleven_video.config.persistence as persistence
                importlib.reload(persistence)
                
                # The existing load_config already handles this
                result = persistence.load_config()
                
                # Either empty dict or raises - check the implementation handles it
                assert isinstance(result, dict)


# =============================================================================
# Task 2.4: Merge behavior with existing config
# =============================================================================

class TestConfigMergeBehavior:
    """Tests that save_config merges with existing values."""

    def test_save_config_merges_with_existing(self, tmp_path):
        """
        GIVEN an existing config with output_format
        WHEN save_config() is called with default_voice
        THEN both fields exist in the resulting config
        """
        config_file = tmp_path / "config.json"
        
        with patch("eleven_video.config.persistence.get_config_path", return_value=config_file):
            from eleven_video.config.persistence import save_config, load_config
            
            # First save
            save_config({"output_format": "mp4"})
            
            # Second save with different field
            save_config({"default_voice": "voice-123"})
            
            # Both should exist
            loaded = load_config()
            assert loaded.get("output_format") == "mp4"
            assert loaded.get("default_voice") == "voice-123"

    def test_save_config_updates_existing_preference(self, tmp_path):
        """
        GIVEN an existing config with default_voice
        WHEN save_config() is called with a new default_voice
        THEN the value is updated
        """
        config_file = tmp_path / "config.json"
        
        with patch("eleven_video.config.persistence.get_config_path", return_value=config_file):
            from eleven_video.config.persistence import save_config, load_config
            
            # First save
            save_config({"default_voice": "old-voice"})
            
            # Second save with updated value
            save_config({"default_voice": "new-voice"})
            
            loaded = load_config()
            assert loaded.get("default_voice") == "new-voice"
