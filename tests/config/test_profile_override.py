"""
ATDD Tests for Story 1.6: Multiple API Key Profile Management
AC5: Global --profile Override

Tests follow red-green-refactor cycle - written BEFORE implementation.
"""

import json
from unittest.mock import patch


class TestGlobalProfileOverride:
    """Tests for global --profile option (AC5)."""

    def test_1_6_UNIT_012_profile_override_uses_specified_profile(self, tmp_path):
        """
        AC5: Profile override uses specified profile.
        
        GIVEN --profile <name> is passed
        WHEN any command runs
        THEN that profile is used for this command only
        """
        # GIVEN: Two different .env files
        env_dev = tmp_path / ".env.dev"
        env_dev.write_text("ELEVENLABS_API_KEY=dev_key\nGEMINI_API_KEY=dev_gemini")
        env_prod = tmp_path / ".env.prod"
        env_prod.write_text("ELEVENLABS_API_KEY=prod_key\nGEMINI_API_KEY=prod_gemini")
        
        from eleven_video.config.settings import Settings
        
        # Mock the profile functions AND environment variables
        with patch("eleven_video.config.persistence.list_profiles") as mock_list, \
             patch("eleven_video.config.persistence.get_active_profile") as mock_active, \
             patch.dict('os.environ', {}, clear=True):  # Clear real environment variables
            mock_active.return_value = "dev"  # Dev is default
            mock_list.return_value = {"dev": str(env_dev), "prod": str(env_prod)}
            
            # WHEN: Override to prod profile
            settings = Settings(_profile_override="prod")
            
            # THEN: Prod keys loaded
            assert settings.elevenlabs_api_key.get_secret_value() == "prod_key"

    def test_1_6_UNIT_013_profile_override_does_not_persist(self, tmp_path):
        """
        AC5: Profile override does not persist.
        
        GIVEN --profile <name> is used for a command
        WHEN the command completes
        THEN the active_profile in config.json is unchanged
        """
        # GIVEN: Active profile is dev
        env_dev = tmp_path / ".env.dev"
        env_dev.write_text("ELEVENLABS_API_KEY=dev\nGEMINI_API_KEY=dev")
        env_prod = tmp_path / ".env.prod"
        env_prod.write_text("ELEVENLABS_API_KEY=prod\nGEMINI_API_KEY=prod")
        
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / "config.json"
        config_file.write_text(json.dumps({
            "active_profile": "dev",
            "profiles": {"dev": str(env_dev), "prod": str(env_prod)}
        }))
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(config_dir)
            from eleven_video.config.settings import Settings
            from eleven_video.config.persistence import load_config
            
            # WHEN: Use override
            Settings(_profile_override="prod")
            
            # THEN: Persisted active_profile unchanged
            config = load_config()
            assert config["active_profile"] == "dev"
