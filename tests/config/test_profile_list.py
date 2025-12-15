"""
ATDD Tests for Story 1.6: Multiple API Key Profile Management
AC2: Profile List Command

Tests follow red-green-refactor cycle - written BEFORE implementation.
"""

import json
from unittest.mock import patch


class TestProfileList:
    """Tests for profile list command (AC2)."""

    def test_1_6_UNIT_004_profile_list_returns_all_profiles(self, tmp_path):
        """
        AC2: Profile list returns all profiles.
        
        GIVEN multiple profiles exist
        WHEN I run `profile list`
        THEN all profiles are returned with their .env paths
        """
        # GIVEN: Config with multiple profiles
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "active_profile": "dev",
            "profiles": {
                "default": ".env",
                "dev": ".env.dev",
                "prod": "/secure/.env.prod"
            }
        }))
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(tmp_path)
            from eleven_video.config.persistence import list_profiles
            
            # WHEN: List profiles
            profiles = list_profiles()
            
            # THEN: All profiles returned
            assert len(profiles) == 3
            assert profiles["default"] == ".env"
            assert profiles["dev"] == ".env.dev"
            assert profiles["prod"] == "/secure/.env.prod"

    def test_1_6_UNIT_005_profile_list_indicates_active_profile(self, tmp_path):
        """
        AC2: Profile list indicates active profile.
        
        GIVEN multiple profiles with one active
        WHEN I run `profile list`
        THEN the active profile is indicated
        """
        # GIVEN: Config with active profile set
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "active_profile": "dev",
            "profiles": {"default": ".env", "dev": ".env.dev"}
        }))
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(tmp_path)
            from eleven_video.config.persistence import get_active_profile
            
            # WHEN: Get active profile
            active = get_active_profile()
            
            # THEN: Active profile identified
            assert active == "dev"

    def test_1_6_UNIT_006_profile_list_empty_when_no_profiles(self, tmp_path):
        """
        AC2: Profile list returns empty when no profiles.
        
        GIVEN no profiles exist
        WHEN I run `profile list`
        THEN empty dict returned
        """
        # GIVEN: Empty config
        config_file = tmp_path / "config.json"
        config_file.write_text("{}")
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(tmp_path)
            from eleven_video.config.persistence import list_profiles
            
            # WHEN: List profiles
            profiles = list_profiles()
            
            # THEN: Empty dict
            assert profiles == {}
