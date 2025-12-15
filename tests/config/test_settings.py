"""
Unit Tests for Story 1.2: API Key Configuration via Environment Variables

Tests follow ATDD red-green-refactor cycle - written BEFORE implementation.
All tests use pytest monkeypatch for safe environment variable manipulation.
"""

import pytest


# =============================================================================
# AC1: Environment Variable Loading from .env
# =============================================================================

class TestEnvFileLoading:
    """Tests for .env file loading (AC1)."""

    def test_settings_loads_elevenlabs_api_key_from_env_file(self, tmp_path, monkeypatch):
        """
        GIVEN a .env file with ELEVENLABS_API_KEY defined
        WHEN Settings is instantiated
        THEN elevenlabs_api_key is loaded from the .env file
        """
        # GIVEN: .env file with API key
        env_file = tmp_path / ".env"
        env_file.write_text("ELEVENLABS_API_KEY=sk-test-eleven-key-12345\nGEMINI_API_KEY=dummy\n")
        
        # Clear any existing env var to ensure .env is source
        monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.chdir(tmp_path)
        
        # WHEN: Settings is instantiated
        from eleven_video.config.settings import Settings
        settings = Settings(_env_file=str(env_file))
        
        # THEN: API key is loaded
        assert settings.elevenlabs_api_key.get_secret_value() == "sk-test-eleven-key-12345"

    def test_settings_loads_gemini_api_key_from_env_file(self, tmp_path, monkeypatch):
        """
        GIVEN a .env file with GEMINI_API_KEY defined
        WHEN Settings is instantiated
        THEN gemini_api_key is loaded from the .env file
        """
        # GIVEN: .env file with API key
        env_file = tmp_path / ".env"
        env_file.write_text("ELEVENLABS_API_KEY=dummy\nGEMINI_API_KEY=AIza-test-gemini-key-67890\n")
        
        # Clear any existing env var
        monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.chdir(tmp_path)
        
        # WHEN: Settings is instantiated
        from eleven_video.config.settings import Settings
        settings = Settings(_env_file=str(env_file))
        
        # THEN: API key is loaded
        assert settings.gemini_api_key.get_secret_value() == "AIza-test-gemini-key-67890"


# =============================================================================
# AC2: Shell Environment Precedence
# =============================================================================

class TestEnvironmentPrecedence:
    """Tests for shell env > .env precedence (AC2)."""

    def test_shell_env_overrides_dotenv_for_eleven_key(self, tmp_path, monkeypatch):
        """
        GIVEN a .env file with ELEVENLABS_API_KEY AND shell env var set
        WHEN Settings is instantiated
        THEN shell env var takes precedence over .env file
        """
        # GIVEN: .env file with one value, shell env with another
        env_file = tmp_path / ".env"
        env_file.write_text("ELEVENLABS_API_KEY=dotenv-value\nGEMINI_API_KEY=dummy\n")
        monkeypatch.chdir(tmp_path)
        
        # Set shell environment variable (should win)
        monkeypatch.setenv("ELEVENLABS_API_KEY", "shell-value-wins")
        monkeypatch.setenv("GEMINI_API_KEY", "dummy")
        
        # WHEN: Settings is instantiated
        from eleven_video.config.settings import Settings
        settings = Settings(_env_file=str(env_file))
        
        # THEN: Shell value takes precedence
        assert settings.elevenlabs_api_key.get_secret_value() == "shell-value-wins"

    def test_shell_env_overrides_dotenv_for_gemini_key(self, tmp_path, monkeypatch):
        """
        GIVEN a .env file with GEMINI_API_KEY AND shell env var set
        WHEN Settings is instantiated
        THEN shell env var takes precedence over .env file
        """
        # GIVEN: .env file with one value, shell env with another
        env_file = tmp_path / ".env"
        env_file.write_text("ELEVENLABS_API_KEY=dummy\nGEMINI_API_KEY=dotenv-gemini\n")
        monkeypatch.chdir(tmp_path)
        
        # Set shell environment variable (should win)
        monkeypatch.setenv("ELEVENLABS_API_KEY", "dummy")
        monkeypatch.setenv("GEMINI_API_KEY", "shell-gemini-wins")
        
        # WHEN: Settings is instantiated
        from eleven_video.config.settings import Settings
        settings = Settings(_env_file=str(env_file))
        
        # THEN: Shell value takes precedence
        assert settings.gemini_api_key.get_secret_value() == "shell-gemini-wins"


# =============================================================================
# AC3: API Key Masking
# =============================================================================

class TestApiKeyMasking:
    """Tests for API key masking in logs/display (AC3)."""

    def test_elevenlabs_api_key_is_masked_in_str_representation(self, monkeypatch):
        """
        GIVEN Settings with elevenlabs_api_key configured
        WHEN str(settings.elevenlabs_api_key) is called
        THEN the actual key value is NOT exposed (masked)
        """
        # GIVEN: Settings with API key
        monkeypatch.setenv("ELEVENLABS_API_KEY", "sk-super-secret-key")
        monkeypatch.setenv("GEMINI_API_KEY", "dummy")
        
        from eleven_video.config.settings import Settings
        settings = Settings()
        
        # WHEN: Converting to string
        key_str = str(settings.elevenlabs_api_key)
        
        # THEN: Actual value is NOT in string representation
        assert "sk-super-secret-key" not in key_str
        assert "**" in key_str or "SecretStr" in key_str

    def test_gemini_api_key_is_masked_in_str_representation(self, monkeypatch):
        """
        GIVEN Settings with gemini_api_key configured
        WHEN str(settings.gemini_api_key) is called
        THEN the actual key value is NOT exposed (masked)
        """
        # GIVEN: Settings with API key
        monkeypatch.setenv("ELEVENLABS_API_KEY", "dummy")
        monkeypatch.setenv("GEMINI_API_KEY", "AIza-top-secret-gemini")
        
        from eleven_video.config.settings import Settings
        settings = Settings()
        
        # WHEN: Converting to string
        key_str = str(settings.gemini_api_key)
        
        # THEN: Actual value is NOT in string representation
        assert "AIza-top-secret-gemini" not in key_str
        assert "**" in key_str or "SecretStr" in key_str

    def test_api_keys_not_exposed_in_settings_repr(self, monkeypatch):
        """
        GIVEN Settings with both API keys configured
        WHEN repr(settings) is called
        THEN neither raw API key value is exposed
        """
        # GIVEN: Settings with API keys
        monkeypatch.setenv("ELEVENLABS_API_KEY", "eleven-secret-value")
        monkeypatch.setenv("GEMINI_API_KEY", "gemini-secret-value")
        
        from eleven_video.config.settings import Settings
        settings = Settings()
        
        # WHEN: Getting repr
        settings_repr = repr(settings)
        
        # THEN: Neither secret is exposed
        assert "eleven-secret-value" not in settings_repr
        assert "gemini-secret-value" not in settings_repr


# =============================================================================
# AC4: Missing Key Error Handling
# =============================================================================

class TestMissingKeyErrorHandling:
    """Tests for clear error when API keys are missing (AC4)."""

    def test_missing_api_key_raises_configuration_error(self, tmp_path, monkeypatch):
        """
        GIVEN no API keys configured
        WHEN Settings is instantiated
        THEN ConfigurationError is raised with clear message
        """
        # GIVEN: No API keys set
        monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        
        # Create empty .env to avoid any existing .env influence
        env_file = tmp_path / ".env"
        env_file.write_text("")
        monkeypatch.chdir(tmp_path)
        
        # WHEN/THEN: Instantiation raises ConfigurationError
        from eleven_video.exceptions.custom_errors import ConfigurationError
        
        with pytest.raises(ConfigurationError) as exc_info:
            from eleven_video.config.settings import Settings
            Settings(_env_file=str(env_file))
        
        # THEN: Error message is clear
        error_message = str(exc_info.value).lower()
        assert "api" in error_message or "key" in error_message or "configuration" in error_message

    def test_empty_string_api_key_raises_configuration_error(self, tmp_path, monkeypatch):
        """
        GIVEN API keys set to empty strings
        WHEN Settings is instantiated
        THEN ConfigurationError is raised (empty keys are invalid)
        """
        # GIVEN: Empty string API keys
        env_file = tmp_path / ".env"
        env_file.write_text("ELEVENLABS_API_KEY=\nGEMINI_API_KEY=\n")
        monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.chdir(tmp_path)
        
        # WHEN/THEN: ConfigurationError raised
        from eleven_video.exceptions.custom_errors import ConfigurationError
        
        with pytest.raises(ConfigurationError) as exc_info:
            from eleven_video.config.settings import Settings
            Settings(_env_file=str(env_file))
        
        # Error message indicates empty keys
        assert "empty" in str(exc_info.value).lower() or "api" in str(exc_info.value).lower()

