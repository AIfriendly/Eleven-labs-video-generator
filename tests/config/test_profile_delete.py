"""
ATDD Tests for Story 1.6: Multiple API Key Profile Management
Profile Delete Command (Additional CRUD)

Tests follow red-green-refactor cycle - written BEFORE implementation.
"""

import json
import pytest
from unittest.mock import patch


class TestProfileDelete:
    """Tests for profile delete command."""

    def test_1_6_UNIT_014_profile_delete_removes_profile(self, tmp_path):
        """
        Profile delete removes profile from config.
        
        GIVEN a profile exists
        WHEN I run `profile delete <name>`
        THEN the profile is removed from config
        """
        # GIVEN: Config with profiles
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "active_profile": "default",
            "profiles": {"default": ".env", "dev": ".env.dev"}
        }))
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(tmp_path)
            from eleven_video.config.persistence import delete_profile, load_config
            
            # WHEN: Delete profile
            delete_profile("dev")
            
            # THEN: Profile removed
            config = load_config()
            assert "dev" not in config["profiles"]
            assert "default" in config["profiles"]

    def test_1_6_UNIT_015_profile_delete_rejects_active_profile(self, tmp_path):
        """
        Profile delete rejects active profile.
        
        GIVEN a profile is currently active
        WHEN I try to delete it
        THEN an error is raised
        """
        # GIVEN: Active profile
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "active_profile": "dev",
            "profiles": {"default": ".env", "dev": ".env.dev"}
        }))
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(tmp_path)
            from eleven_video.config.persistence import delete_profile
            from eleven_video.exceptions.custom_errors import ConfigurationError
            
            # WHEN/THEN: Delete active profile raises error
            with pytest.raises(ConfigurationError, match="Cannot delete active profile"):
                delete_profile("dev")

    def test_1_6_UNIT_016_profile_delete_rejects_unknown_profile(self, tmp_path):
        """
        Profile delete rejects unknown profile.
        
        GIVEN a profile name that doesn't exist
        WHEN I try to delete it
        THEN an error is raised
        """
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "profiles": {"default": ".env"}
        }))
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(tmp_path)
            from eleven_video.config.persistence import delete_profile
            from eleven_video.exceptions.custom_errors import ConfigurationError
            
            # WHEN/THEN: Delete unknown profile raises error
            with pytest.raises(ConfigurationError, match="not found"):
                delete_profile("nonexistent")
