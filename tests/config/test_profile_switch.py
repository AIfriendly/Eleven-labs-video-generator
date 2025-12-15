"""
ATDD Tests for Story 1.6: Multiple API Key Profile Management
AC3: Profile Switch Command

Tests follow red-green-refactor cycle - written BEFORE implementation.
"""

import json
import pytest
from unittest.mock import patch


class TestProfileSwitch:
    """Tests for profile switch command (AC3)."""

    def test_1_6_UNIT_007_profile_switch_persists_selection(self, tmp_path):
        """
        AC3: Profile switch persists selection.
        
        GIVEN multiple profiles exist
        WHEN I run `profile switch <name>`
        THEN the selection is persisted in config.json
        """
        # GIVEN: Config with profiles
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "active_profile": "default",
            "profiles": {"default": ".env", "prod": ".env.prod"}
        }))
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(tmp_path)
            from eleven_video.config.persistence import switch_profile, load_config
            
            # WHEN: Switch profile
            switch_profile("prod")
            
            # THEN: Selection persisted
            config = load_config()
            assert config["active_profile"] == "prod"

    def test_1_6_UNIT_008_profile_switch_rejects_unknown_profile(self, tmp_path):
        """
        AC3: Profile switch rejects unknown profile.
        
        GIVEN a profile name that doesn't exist
        WHEN I run `profile switch <name>`
        THEN an error is raised
        """
        # GIVEN: Config without the target profile
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "active_profile": "default",
            "profiles": {"default": ".env"}
        }))
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(tmp_path)
            from eleven_video.config.persistence import switch_profile
            from eleven_video.exceptions.custom_errors import ConfigurationError
            
            # WHEN/THEN: Switch to unknown profile raises error
            with pytest.raises(ConfigurationError, match="not found"):
                switch_profile("unknown")

    def test_1_6_UNIT_009_settings_loads_env_from_active_profile(self, tmp_path):
        """
        AC3: Settings loads env from active profile.
        
        GIVEN an active profile pointing to a specific .env file
        WHEN Settings() is created
        THEN environment variables are loaded from that .env file
        """
        # GIVEN: Profile pointing to specific .env
        env_prod = tmp_path / ".env.prod"
        env_prod.write_text("ELEVENLABS_API_KEY=prod_key_123\nGEMINI_API_KEY=prod_gemini_456")
        
        from eleven_video.config.settings import Settings
        
        # Mock the profile functions to return our test config
        with patch("eleven_video.config.persistence.list_profiles") as mock_list, \
             patch("eleven_video.config.persistence.get_active_profile") as mock_active:
            mock_active.return_value = "prod"
            mock_list.return_value = {"prod": str(env_prod)}
            
            # WHEN: Create Settings
            settings = Settings()
            
            # THEN: Keys loaded from prod .env
            assert settings.elevenlabs_api_key.get_secret_value() == "prod_key_123"
            assert settings.gemini_api_key.get_secret_value() == "prod_gemini_456"
