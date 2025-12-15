"""
Unit Tests for Story 1.3: Interactive Setup and Configuration File Creation
Persistence Layer Tests

Tests follow ATDD red-green-refactor cycle - written BEFORE implementation.
"""

import json
import pytest
from unittest.mock import patch, MagicMock


# =============================================================================
# AC2: Config File Creation at Platformdirs Path
# =============================================================================

class TestConfigFileCreation:
    """Tests for config file creation at OS-standard path (AC2)."""

    def test_config_file_created_at_platformdirs_path(self, tmp_path):
        """
        GIVEN a persistence module using platformdirs
        WHEN save_config is called
        THEN config file is created at platformdirs.user_config_dir path
        """
        # GIVEN: Mock platformdirs to return our tmp_path
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(tmp_path)
            from eleven_video.config.persistence import save_config, get_config_path
            
            # WHEN: Save config
            save_config({"default_voice": "alloy"})
            
            # THEN: File exists at expected path
            config_path = get_config_path()
            assert config_path.exists()
            assert config_path.name == "config.json"

    def test_config_directory_created_if_not_exists(self, tmp_path):
        """
        GIVEN config directory does not exist
        WHEN save_config is called
        THEN directory is created automatically
        """
        # GIVEN: Non-existent nested directory
        config_dir = tmp_path / "eleven-video"
        assert not config_dir.exists()
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(config_dir)
            from eleven_video.config.persistence import save_config
            
            # WHEN: Save config
            save_config({"key": "value"})
            
            # THEN: Directory was created
            assert config_dir.exists()

    def test_config_path_uses_app_name_eleven_video(self, tmp_path):
        """
        GIVEN the persistence module
        WHEN get_config_path is called
        THEN it uses "eleven-video" as the app name
        """
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(tmp_path)
            from eleven_video.config.persistence import get_config_path
            
            # WHEN: Get config path
            get_config_path()
            
            # THEN: Called with correct app name
            mock_pd.user_config_dir.assert_called_with("eleven-video")


# =============================================================================
# AC3: Existing Config Defaults
# =============================================================================

class TestConfigLoading:
    """Tests for loading existing configuration (AC3)."""

    def test_load_config_returns_existing_values(self, tmp_path):
        """
        GIVEN a config file exists with values
        WHEN load_config is called
        THEN existing values are returned as dict
        """
        # GIVEN: Existing config file
        config_file = tmp_path / "config.json"
        config_file.write_text('{"default_voice": "echo", "output_format": "mp4"}')
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(tmp_path)
            from eleven_video.config.persistence import load_config
            
            # WHEN: Load config
            config = load_config()
            
            # THEN: Values returned
            assert config == {"default_voice": "echo", "output_format": "mp4"}

    def test_load_config_returns_empty_dict_if_no_file(self, tmp_path):
        """
        GIVEN no config file exists
        WHEN load_config is called
        THEN empty dict returned (no error)
        """
        # GIVEN: No config file
        assert not (tmp_path / "config.json").exists()
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(tmp_path)
            from eleven_video.config.persistence import load_config
            
            # WHEN: Load config
            config = load_config()
            
            # THEN: Empty dict returned
            assert config == {}

    def test_load_config_handles_corrupted_json(self, tmp_path):
        """
        GIVEN config file contains invalid JSON
        WHEN load_config is called
        THEN empty dict returned (graceful degradation)
        """
        # GIVEN: Corrupted JSON file
        config_file = tmp_path / "config.json"
        config_file.write_text("{ not valid json }")
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(tmp_path)
            from eleven_video.config.persistence import load_config
            
            # WHEN: Load config
            config = load_config()
            
            # THEN: Empty dict returned, no exception raised
            assert config == {}


# =============================================================================
# AC4: Config File Update
# =============================================================================

class TestConfigUpdate:
    """Tests for updating configuration (AC4)."""

    def test_save_config_writes_json_file(self, tmp_path):
        """
        GIVEN config data
        WHEN save_config is called
        THEN valid JSON file is written
        """
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(tmp_path)
            from eleven_video.config.persistence import save_config
            
            # WHEN: Save config
            save_config({"default_voice": "nova", "video_length": 5})
            
            # THEN: Valid JSON written
            config_file = tmp_path / "config.json"
            assert config_file.exists()
            content = json.loads(config_file.read_text())
            assert content == {"default_voice": "nova", "video_length": 5}

    def test_save_config_preserves_existing_values(self, tmp_path):
        """
        GIVEN existing config with some values
        WHEN save_config called with partial update
        THEN existing values preserved, new values merged
        """
        # GIVEN: Existing config
        config_file = tmp_path / "config.json"
        config_file.write_text('{"existing_key": "preserved", "update_key": "old"}')
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(tmp_path)
            from eleven_video.config.persistence import save_config
            
            # WHEN: Save partial update
            save_config({"update_key": "new", "new_key": "added"})
            
            # THEN: Merged correctly
            content = json.loads(config_file.read_text())
            assert content["existing_key"] == "preserved"
            assert content["update_key"] == "new"
            assert content["new_key"] == "added"


# =============================================================================
# AC5: Security - API Keys Not Stored
# =============================================================================

class TestApiKeySecurity:
    """Tests for API key security constraint (AC5)."""

    def test_api_keys_not_stored_in_config(self, tmp_path):
        """
        GIVEN config data containing API key fields
        WHEN save_config is called
        THEN API key fields are rejected/stripped
        """
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(tmp_path)
            from eleven_video.config.persistence import save_config
            
            # WHEN: Try to save API keys
            save_config({
                "elevenlabs_api_key": "sk-secret-key",
                "gemini_api_key": "AIza-secret",
                "default_voice": "allowed"
            })
            
            # THEN: API keys NOT in saved file
            config_file = tmp_path / "config.json"
            content = json.loads(config_file.read_text())
            assert "elevenlabs_api_key" not in content
            assert "gemini_api_key" not in content
            assert "api_key" not in str(content).lower()
            # But non-secret values are saved
            assert content.get("default_voice") == "allowed"
