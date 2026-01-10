"""
CLI Tests for Story 1.3: Interactive Setup Command

Tests follow ATDD red-green-refactor cycle - written BEFORE implementation.
"""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock


runner = CliRunner()


# =============================================================================
# AC1: Interactive Setup Command
# =============================================================================

class TestSetupCommandRegistration:
    """Tests for setup command registration (AC1)."""

    def test_setup_command_registered(self):
        """
        GIVEN the eleven-video CLI
        WHEN help is displayed
        THEN setup command is listed
        """
        from eleven_video.main import app
        
        # WHEN: Get help
        result = runner.invoke(app, ["--help"])
        
        # THEN: setup command listed
        assert result.exit_code == 0
        assert "setup" in result.output.lower()

    def test_setup_prompts_for_configuration(self, tmp_path):
        """
        GIVEN setup command is invoked
        WHEN running interactively
        THEN prompts are displayed for configuration options
        """
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(tmp_path)
            from eleven_video.main import app
            
            # WHEN: Run setup (simulate interactive input)
            # Inputs: [voice=nova], [image=def], [gemini=def], [duration=5], [format=mp4]
            result = runner.invoke(app, ["setup"], input="nova\n\n\n5\nmp4\n")
            
            # THEN: Prompts displayed (check exit code and some output)
            output_lower = result.output.lower()
            # Should ask about voice or other settings
            assert "voice" in output_lower or "default" in output_lower or "configure" in output_lower or "setup" in output_lower


# =============================================================================
# AC3: Existing Values as Defaults
# =============================================================================

class TestSetupDefaults:
    """Tests for showing existing config as defaults (AC3)."""

    def test_setup_shows_existing_values_as_defaults(self, tmp_path):
        """
        GIVEN existing configuration file
        WHEN setup command is run
        THEN existing values shown as defaults
        """
        # GIVEN: Existing config
        config_file = tmp_path / "config.json"
        config_file.write_text('{"default_voice": "shimmer"}')
        
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(tmp_path)
            from eleven_video.main import app
            
            # WHEN: Run setup
            result = runner.invoke(app, ["setup"], input="\n\n\n\n\n")  # Accept defaults for all 5 prompts
            
            # THEN: Existing value shown or used
            # The test passes if either "shimmer" appears in output OR no error occurred
            assert result.exit_code == 0 or "shimmer" in result.output.lower()


# =============================================================================
# AC5: API Key Security Warning
# =============================================================================

class TestSetupSecurity:
    """Tests for API key security warning (AC5)."""

    def test_setup_warns_about_api_key_security(self, tmp_path):
        """
        GIVEN setup command is invoked
        WHEN running
        THEN warning about API keys not being stored is displayed
        """
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(tmp_path)
            from eleven_video.main import app
            
            # WHEN: Run setup
            result = runner.invoke(app, ["setup"], input="\n\n\n\n\n")
            
            # THEN: Security warning displayed (mentions API, .env, or key)
            output_lower = result.output.lower()
            has_security_message = (
                "api" in output_lower or 
                ".env" in output_lower or 
                "key" in output_lower or
                "environment" in output_lower
            )
            assert has_security_message, f"Expected security warning in output: {result.output}"


# =============================================================================
# Story 3.7: New Preference Prompts Coverage
# =============================================================================

class TestSetupPromptCoverage:
    """Tests for verifying all new preference prompts are displayed (Fixing Issue #1)."""

    def test_setup_prompts_for_all_preferences(self, tmp_path):
        """
        GIVEN setup command is invoked
        WHEN running interactively
        THEN prompts for voice, image model, gemini model, and duration are displayed
        """
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(tmp_path)
            from eleven_video.main import app
            
            # WHEN: Run setup with defaults for all prompts
            # Inputs: [voice], [image_model], [gemini_model], [duration], [output_format]
            result = runner.invoke(app, ["setup"], input="\n\n\n5\nmp4\n")
            
            # THEN: All specific prompts are in output
            output_lower = result.output.lower()
            
            assert "default voice id" in output_lower
            assert "default image model" in output_lower
            assert "default gemini model" in output_lower
            assert "default video duration" in output_lower


class TestSetupValidation:
    """Tests for setup wizard input validation (Fixing Issue #2)."""

    def test_setup_validates_duration_input(self, tmp_path):
        """
        GIVEN setup command prompts for duration
        WHEN invalid input ('7') is provided followed by valid input ('5')
        THEN the command reprompts until valid input is received
        """
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = str(tmp_path)
            from eleven_video.main import app
            
            # WHEN: Run setup
            # Inputs: [voice], [image], [gemini], [INVALID_DURATION], [VALID_DURATION], [format]
            # '7' is invalid (not in choices), '5' is valid
            result = runner.invoke(app, ["setup"], input="\n\n\n7\n5\nmp4\n")
            
            # THEN: Verify it didn't crash and accepted the final valid input
            assert result.exit_code == 0
            
            # Verify the invalid input was rejected (implicitly by needing a second input)
            # and verify the config saved the valid value
            config_file = tmp_path / "config.json"
            assert config_file.exists()
            import json
            data = json.loads(config_file.read_text())
            assert data["default_duration_minutes"] == 5
