"""
Unit Tests for Story 3.7: Default Preference Configuration

Tests Settings model extension with default preference fields:
- default_voice
- default_image_model  
- default_gemini_model
- default_duration_minutes

Tests follow ATDD red-green-refactor cycle.
"""

import pytest
from unittest.mock import patch
import json


# =============================================================================
# Task 1.1-1.4: Settings loads default preference fields
# =============================================================================

class TestSettingsDefaultPreferenceFields:
    """Tests for default preference fields in Settings (Task 1.1-1.4)."""

    def test_settings_loads_default_voice_from_json_config(self, tmp_path, monkeypatch):
        """
        GIVEN a JSON config with default_voice set
        WHEN Settings is instantiated
        THEN default_voice is loaded from JSON config
        """
        # GIVEN: JSON config with default_voice
        config_data = {"default_voice": "test-voice-id-123"}
        
        # Set up environment
        monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        
        with patch("eleven_video.config.settings.load_config", return_value=config_data):
            from eleven_video.config.settings import Settings
            settings = Settings()
        
            # THEN: default_voice is loaded
            assert settings.default_voice == "test-voice-id-123"

    def test_settings_loads_default_image_model_from_json_config(self, tmp_path, monkeypatch):
        """
        GIVEN a JSON config with default_image_model set
        WHEN Settings is instantiated
        THEN default_image_model is loaded from JSON config
        """
        config_data = {"default_image_model": "gemini-2.5-flash-image"}
        
        monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        
        with patch("eleven_video.config.settings.load_config", return_value=config_data):
            from eleven_video.config.settings import Settings
            settings = Settings()
        
            assert settings.default_image_model == "gemini-2.5-flash-image"

    def test_settings_loads_default_gemini_model_from_json_config(self, tmp_path, monkeypatch):
        """
        GIVEN a JSON config with default_gemini_model set
        WHEN Settings is instantiated
        THEN default_gemini_model is loaded from JSON config
        """
        config_data = {"default_gemini_model": "gemini-2.5-flash"}
        
        monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        
        with patch("eleven_video.config.settings.load_config", return_value=config_data):
            from eleven_video.config.settings import Settings
            settings = Settings()
        
            assert settings.default_gemini_model == "gemini-2.5-flash"

    def test_settings_loads_default_duration_minutes_from_json_config(self, tmp_path, monkeypatch):
        """
        GIVEN a JSON config with default_duration_minutes set
        WHEN Settings is instantiated
        THEN default_duration_minutes is loaded from JSON config
        """
        config_data = {"default_duration_minutes": 5}
        
        monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        
        with patch("eleven_video.config.settings.load_config", return_value=config_data):
            from eleven_video.config.settings import Settings
            settings = Settings()
        
            assert settings.default_duration_minutes == 5


# =============================================================================
# Task 1.5: Empty string handling (treat as None)
# =============================================================================

class TestEmptyStringHandling:
    """Tests for empty string to None conversion (Task 1.5)."""

    def test_empty_string_default_voice_becomes_none(self, monkeypatch):
        """
        GIVEN a JSON config with default_voice as empty string
        WHEN Settings is instantiated
        THEN default_voice is None (not configured)
        """
        config_data = {"default_voice": ""}
        
        monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        
        with patch("eleven_video.config.settings.load_config", return_value=config_data):
            from eleven_video.config.settings import Settings
            settings = Settings()
        
            assert settings.default_voice is None

    def test_whitespace_only_default_voice_becomes_none(self, monkeypatch):
        """
        GIVEN a JSON config with default_voice as whitespace only
        WHEN Settings is instantiated
        THEN default_voice is None (not configured)
        """
        config_data = {"default_voice": "   "}
        
        monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        
        with patch("eleven_video.config.settings.load_config", return_value=config_data):
            from eleven_video.config.settings import Settings
            settings = Settings()
        
            assert settings.default_voice is None

    def test_empty_string_default_image_model_becomes_none(self, monkeypatch):
        """
        GIVEN a JSON config with default_image_model as empty string
        WHEN Settings is instantiated
        THEN default_image_model is None (not configured)
        """
        config_data = {"default_image_model": ""}
        
        monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        
        with patch("eleven_video.config.settings.load_config", return_value=config_data):
            from eleven_video.config.settings import Settings
            settings = Settings()
        
            assert settings.default_image_model is None

    def test_empty_string_default_gemini_model_becomes_none(self, monkeypatch):
        """
        GIVEN a JSON config with default_gemini_model as empty string
        WHEN Settings is instantiated
        THEN default_gemini_model is None (not configured)
        """
        config_data = {"default_gemini_model": ""}
        
        monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        
        with patch("eleven_video.config.settings.load_config", return_value=config_data):
            from eleven_video.config.settings import Settings
            settings = Settings()
        
            assert settings.default_gemini_model is None

    def test_empty_string_default_duration_becomes_none(self, monkeypatch):
        """
        GIVEN a JSON config with default_duration_minutes as empty string
        WHEN Settings is instantiated
        THEN default_duration_minutes is None (not configured)
        """
        config_data = {"default_duration_minutes": ""}
        
        monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        
        with patch("eleven_video.config.settings.load_config", return_value=config_data):
            from eleven_video.config.settings import Settings
            settings = Settings()
        
            assert settings.default_duration_minutes is None


# =============================================================================
# Task 1.4: Duration validation (must be 3, 5, or 10)
# =============================================================================

class TestDurationValidation:
    """Tests for duration validation (Task 1.4)."""

    @pytest.mark.parametrize("valid_duration", [3, 5, 10])
    def test_valid_duration_values_accepted(self, monkeypatch, valid_duration):
        """
        GIVEN a JSON config with valid duration (3, 5, or 10)
        WHEN Settings is instantiated
        THEN default_duration_minutes equals the configured value
        """
        config_data = {"default_duration_minutes": valid_duration}
        
        monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        
        with patch("eleven_video.config.settings.load_config", return_value=config_data):
            from eleven_video.config.settings import Settings
            settings = Settings()
        
            assert settings.default_duration_minutes == valid_duration

    @pytest.mark.parametrize("invalid_duration", [1, 2, 4, 7, 15, 30])
    def test_invalid_duration_values_become_none(self, monkeypatch, invalid_duration):
        """
        GIVEN a JSON config with invalid duration (not 3, 5, or 10)
        WHEN Settings is instantiated
        THEN default_duration_minutes is None (invalid = not configured)
        """
        config_data = {"default_duration_minutes": invalid_duration}
        
        monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        
        with patch("eleven_video.config.settings.load_config", return_value=config_data):
            from eleven_video.config.settings import Settings
            settings = Settings()
        
            assert settings.default_duration_minutes is None

    def test_duration_as_string_is_converted(self, monkeypatch):
        """
        GIVEN a JSON config with duration as string "5"
        WHEN Settings is instantiated
        THEN default_duration_minutes is integer 5
        """
        config_data = {"default_duration_minutes": "5"}
        
        monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        
        with patch("eleven_video.config.settings.load_config", return_value=config_data):
            from eleven_video.config.settings import Settings
            settings = Settings()
        
            assert settings.default_duration_minutes == 5

    def test_invalid_string_duration_becomes_none(self, monkeypatch):
        """
        GIVEN a JSON config with duration as non-numeric string
        WHEN Settings is instantiated
        THEN default_duration_minutes is None
        """
        config_data = {"default_duration_minutes": "invalid"}
        
        monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        
        with patch("eleven_video.config.settings.load_config", return_value=config_data):
            from eleven_video.config.settings import Settings
            settings = Settings()
        
            assert settings.default_duration_minutes is None


# =============================================================================
# Task 1.6: Settings defaults to None when not in config
# =============================================================================

class TestSettingsDefaultsToNone:
    """Tests that preference fields default to None when not configured."""

    def test_default_fields_are_none_when_config_empty(self, monkeypatch):
        """
        GIVEN an empty JSON config
        WHEN Settings is instantiated
        THEN all default preference fields are None
        """
        config_data = {}
        
        monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        
        with patch("eleven_video.config.settings.load_config", return_value=config_data):
            from eleven_video.config.settings import Settings
            settings = Settings()
        
            assert settings.default_voice is None
            assert settings.default_image_model is None
            assert settings.default_gemini_model is None
            assert settings.default_duration_minutes is None

    def test_all_default_fields_load_together(self, monkeypatch):
        """
        GIVEN a JSON config with all default preferences set
        WHEN Settings is instantiated
        THEN all default preference fields are loaded correctly
        """
        config_data = {
            "default_voice": "voice-123",
            "default_image_model": "gemini-image-model",
            "default_gemini_model": "gemini-2.5-flash",
            "default_duration_minutes": 5
        }
        
        monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        
        with patch("eleven_video.config.settings.load_config", return_value=config_data):
            from eleven_video.config.settings import Settings
            settings = Settings()
        
            assert settings.default_voice == "voice-123"
            assert settings.default_image_model == "gemini-image-model"
            assert settings.default_gemini_model == "gemini-2.5-flash"
            assert settings.default_duration_minutes == 5
