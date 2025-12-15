"""
ATDD Tests for Story 1.6: Multiple API Key Profile Management
AC1: Profile Create Command

Tests follow red-green-refactor cycle - written BEFORE implementation.
"""

import pytest
from pathlib import Path
from unittest.mock import patch


class TestProfileCreate:
    """Tests for profile create command (AC1)."""

    def test_1_6_UNIT_001_profile_create_registers_new_profile(self, tmp_path):
        """
        AC1: Profile creation registers new profile.
        
        GIVEN a valid .env file exists
        WHEN I run `profile create <name> --env-file <path>`
        THEN a new profile is registered pointing to that file
        """
        # GIVEN: A valid .env file
        env_file = tmp_path / ".env.dev"
        env_file.write_text("ELEVENLABS_API_KEY=test_key")
        config_dir = tmp_path / "config"
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(config_dir)
            from eleven_video.config.persistence import create_profile, load_config
            
            # WHEN: Create profile
            create_profile("dev", str(env_file))
            
            # THEN: Profile registered in config
            config = load_config()
            assert "profiles" in config
            assert "dev" in config["profiles"]
            assert config["profiles"]["dev"] == str(env_file)

    def test_1_6_UNIT_002_profile_create_rejects_nonexistent_env_file(self, tmp_path):
        """
        AC1: Profile creation rejects non-existent env file.
        
        GIVEN a .env file path that does not exist
        WHEN I run `profile create <name> --env-file <path>`
        THEN an error is raised
        """
        # GIVEN: Non-existent .env file
        fake_env = tmp_path / ".env.fake"
        config_dir = tmp_path / "config"
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(config_dir)
            from eleven_video.config.persistence import create_profile
            from eleven_video.exceptions.custom_errors import ConfigurationError
            
            # WHEN/THEN: Create profile raises error
            with pytest.raises(ConfigurationError, match="does not exist"):
                create_profile("fake", str(fake_env))

    def test_1_6_UNIT_003_profile_create_stores_absolute_path(self, tmp_path):
        """
        AC1: Profile creation stores absolute path.
        
        GIVEN a relative .env file path
        WHEN I run `profile create <name> --env-file <relative_path>`
        THEN the absolute path is stored in config
        """
        # GIVEN: .env file with relative path
        env_file = tmp_path / ".env.dev"
        env_file.write_text("ELEVENLABS_API_KEY=test")
        config_dir = tmp_path / "config"
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(config_dir)
            from eleven_video.config.persistence import create_profile, load_config
            
            # WHEN: Create profile
            create_profile("dev", str(env_file))
            
            # THEN: Absolute path stored
            config = load_config()
            stored_path = Path(config["profiles"]["dev"])
            assert stored_path.is_absolute()
