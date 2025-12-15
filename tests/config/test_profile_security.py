"""
ATDD Tests for Story 1.6: Multiple API Key Profile Management
AC4: Security - API Keys Never in config.json

Tests follow red-green-refactor cycle - written BEFORE implementation.
"""

from unittest.mock import patch


class TestProfileSecurity:
    """Tests for security constraint (AC4)."""

    def test_1_6_UNIT_010_profile_config_never_contains_api_keys(self, tmp_path):
        """
        AC4: Profile config never contains API keys.
        
        GIVEN profile operations are performed
        WHEN config.json is saved
        THEN it NEVER contains API key values
        """
        # GIVEN: .env file with API keys
        env_file = tmp_path / ".env.dev"
        env_file.write_text("ELEVENLABS_API_KEY=secret_key\nGEMINI_API_KEY=another_secret")
        config_dir = tmp_path / "config"
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(config_dir)
            from eleven_video.config.persistence import create_profile
            
            # WHEN: Create profile
            create_profile("dev", str(env_file))
            
            # THEN: Config file never contains API keys
            config_file = config_dir / "config.json"
            content = config_file.read_text()
            assert "secret_key" not in content
            assert "another_secret" not in content
            assert "api_key" not in content.lower() or "profiles" in content

    def test_1_6_UNIT_011_profiles_only_store_file_paths(self, tmp_path):
        """
        AC4: Profiles only store file paths.
        
        GIVEN a profile is created
        WHEN config is saved
        THEN only file paths are stored, not key values
        """
        env_file = tmp_path / ".env.secure"
        env_file.write_text("ELEVENLABS_API_KEY=super_secret")
        config_dir = tmp_path / "config"
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(config_dir)
            from eleven_video.config.persistence import create_profile, load_config
            
            # WHEN: Create profile
            create_profile("secure", str(env_file))
            
            # THEN: Only path stored
            config = load_config()
            profile_value = config["profiles"]["secure"]
            assert profile_value == str(env_file)
            assert "super_secret" not in str(config)
