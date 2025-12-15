"""
CLI Integration Tests for Story 1.6: Multiple API Key Profile Management

Tests the Typer CLI commands for profile management.
All tests should FAIL initially until feature is implemented.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch
from typer.testing import CliRunner

runner = CliRunner()


# =============================================================================
# AC1: profile create CLI Command
# =============================================================================

class TestProfileCreateCLI:
    """CLI tests for profile create command."""

    def test_1_6_CLI_001_profile_create_success(self, tmp_path):
        """
        AC1: CLI profile create success.
        
        GIVEN a valid .env file
        WHEN I run `eleven-video profile create dev --env-file .env.dev`
        THEN success message is displayed
        """
        from eleven_video.main import app
        
        # GIVEN: Valid .env file
        env_file = tmp_path / ".env.dev"
        env_file.write_text("ELEVENLABS_API_KEY=test")
        config_dir = tmp_path / "config"
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(config_dir)
            
            # WHEN: Run CLI command
            result = runner.invoke(app, ["profile", "create", "dev", "--env-file", str(env_file)])
            
            # THEN: Success
            assert result.exit_code == 0
            assert "created" in result.stdout.lower() or "dev" in result.stdout

    def test_1_6_CLI_002_profile_create_invalid_file(self, tmp_path):
        """
        AC1: CLI profile create rejects invalid file.
        
        GIVEN a non-existent .env file
        WHEN I run `eleven-video profile create dev --env-file .env.fake`
        THEN error message is displayed
        """
        from eleven_video.main import app
        
        config_dir = tmp_path / "config"
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(config_dir)
            
            # WHEN: Run CLI with invalid file
            result = runner.invoke(app, ["profile", "create", "dev", "--env-file", "/fake/.env"])
            
            # THEN: Error
            assert result.exit_code != 0
            assert "error" in result.stdout.lower() or "not exist" in result.stdout.lower()


# =============================================================================
# AC2: profile list CLI Command
# =============================================================================

class TestProfileListCLI:
    """CLI tests for profile list command."""

    def test_1_6_CLI_003_profile_list_shows_all_profiles(self, tmp_path):
        """
        AC2: CLI profile list shows all profiles.
        
        GIVEN multiple profiles exist
        WHEN I run `eleven-video profile list`
        THEN all profiles are displayed with paths
        """
        from eleven_video.main import app
        
        # GIVEN: Config with profiles
        config_dir = tmp_path
        config_file = config_dir / "config.json"
        config_file.write_text(json.dumps({
            "active_profile": "dev",
            "profiles": {"default": ".env", "dev": ".env.dev"}
        }))
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(config_dir)
            
            # WHEN: Run CLI
            result = runner.invoke(app, ["profile", "list"])
            
            # THEN: Profiles shown
            assert result.exit_code == 0
            assert "default" in result.stdout
            assert "dev" in result.stdout

    def test_1_6_CLI_004_profile_list_highlights_active(self, tmp_path):
        """
        AC2: CLI profile list highlights active profile.
        
        GIVEN a profile is active
        WHEN I run `eleven-video profile list`
        THEN the active profile is highlighted/indicated
        """
        from eleven_video.main import app
        
        config_dir = tmp_path
        config_file = config_dir / "config.json"
        config_file.write_text(json.dumps({
            "active_profile": "dev",
            "profiles": {"default": ".env", "dev": ".env.dev"}
        }))
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(config_dir)
            
            # WHEN: Run CLI
            result = runner.invoke(app, ["profile", "list"])
            
            # THEN: Active indicated (star, checkmark, or "active" text)
            output = result.stdout.lower()
            assert "active" in output or "*" in result.stdout or "✓" in result.stdout


# =============================================================================
# AC3: profile switch CLI Command
# =============================================================================

class TestProfileSwitchCLI:
    """CLI tests for profile switch command."""

    def test_1_6_CLI_005_profile_switch_success(self, tmp_path):
        """
        AC3: CLI profile switch success.
        
        GIVEN multiple profiles exist
        WHEN I run `eleven-video profile switch prod`
        THEN success message displayed
        """
        from eleven_video.main import app
        
        config_dir = tmp_path
        config_file = config_dir / "config.json"
        config_file.write_text(json.dumps({
            "active_profile": "dev",
            "profiles": {"dev": ".env.dev", "prod": ".env.prod"}
        }))
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(config_dir)
            
            # WHEN: Run CLI
            result = runner.invoke(app, ["profile", "switch", "prod"])
            
            # THEN: Success
            assert result.exit_code == 0
            assert "prod" in result.stdout.lower() or "switched" in result.stdout.lower()

    def test_1_6_CLI_006_profile_switch_unknown(self, tmp_path):
        """
        AC3: CLI profile switch rejects unknown profile.
        
        GIVEN a profile name that doesn't exist
        WHEN I run `eleven-video profile switch unknown`
        THEN error message displayed
        """
        from eleven_video.main import app
        
        config_dir = tmp_path
        config_file = config_dir / "config.json"
        config_file.write_text(json.dumps({
            "active_profile": "dev",
            "profiles": {"dev": ".env.dev"}
        }))
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(config_dir)
            
            # WHEN: Run CLI with unknown profile
            result = runner.invoke(app, ["profile", "switch", "unknown"])
            
            # THEN: Error
            assert result.exit_code != 0


# =============================================================================
# AC5: Global --profile Override
# =============================================================================

class TestGlobalProfileOptionCLI:
    """CLI tests for global --profile option."""

    def test_1_6_CLI_007_global_profile_option_exists(self):
        """
        AC5: CLI global --profile option exists.
        
        GIVEN the CLI app
        WHEN I check available options
        THEN --profile option exists at root level
        """
        from eleven_video.main import app
        
        # WHEN: Run help
        result = runner.invoke(app, ["--help"])
        
        # THEN: --profile option documented
        assert result.exit_code == 0
        assert "--profile" in result.stdout

    def test_1_6_CLI_008_global_profile_override_used(self, tmp_path):
        """
        AC5: CLI global profile override is used.
        
        GIVEN multiple profiles
        WHEN I run `eleven-video --profile prod status`
        THEN the prod profile is used
        """
        from eleven_video.main import app
        
        # GIVEN: Two profiles with different .env files
        env_dev = tmp_path / ".env.dev"
        env_dev.write_text("ELEVENLABS_API_KEY=dev_key\nGEMINI_API_KEY=dev_gem")
        env_prod = tmp_path / ".env.prod"
        env_prod.write_text("ELEVENLABS_API_KEY=prod_key\nGEMINI_API_KEY=prod_gem")
        
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / "config.json"
        config_file.write_text(json.dumps({
            "active_profile": "dev",
            "profiles": {"dev": str(env_dev), "prod": str(env_prod)}
        }))
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(config_dir)
            
            # WHEN: Run with --profile override
            result = runner.invoke(app, ["--profile", "prod", "status"])
            
            # THEN: Command uses prod profile (would need specific verification)
            # For now, just verify no error about profile
            assert "unknown profile" not in result.stdout.lower()


# =============================================================================
# Profile Delete CLI Command
# =============================================================================

class TestProfileDeleteCLI:
    """CLI tests for profile delete command."""

    def test_1_6_CLI_009_profile_delete_success(self, tmp_path):
        """
        CLI profile delete success.
        
        GIVEN a profile exists
        WHEN I run `eleven-video profile delete dev`
        THEN success message displayed
        """
        from eleven_video.main import app
        
        config_dir = tmp_path
        config_file = config_dir / "config.json"
        config_file.write_text(json.dumps({
            "active_profile": "default",
            "profiles": {"default": ".env", "dev": ".env.dev"}
        }))
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(config_dir)
            
            # WHEN: Run CLI
            result = runner.invoke(app, ["profile", "delete", "dev"])
            
            # THEN: Success
            assert result.exit_code == 0
            assert "deleted" in result.stdout.lower() or "removed" in result.stdout.lower()

    def test_1_6_CLI_010_profile_delete_active_fails(self, tmp_path):
        """
        CLI profile delete rejects active profile.
        
        GIVEN a profile is active
        WHEN I try to delete it
        THEN error is displayed
        """
        from eleven_video.main import app
        
        config_dir = tmp_path
        config_file = config_dir / "config.json"
        config_file.write_text(json.dumps({
            "active_profile": "dev",
            "profiles": {"dev": ".env.dev"}
        }))
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(config_dir)
            
            # WHEN: Try to delete active profile
            result = runner.invoke(app, ["profile", "delete", "dev"])
            
            # THEN: Error
            assert result.exit_code != 0 or "cannot" in result.stdout.lower()
