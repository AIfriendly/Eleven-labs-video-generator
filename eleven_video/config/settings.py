"""Application settings using Pydantic BaseSettings.

Implements Story 1.2: API Key Configuration via Environment Variables
- AC1: .env file loading
- AC2: Shell environment precedence (12-factor app)
- AC3: SecretStr masking for security
- AC4: ConfigurationError for missing keys

Implements Story 1.3: Configuration File Integration
- JSON config loaded as additional settings source
- Priority: Environment vars > .env file > JSON config > Defaults
"""

from typing import Any, Tuple, Type

from pydantic import SecretStr, ValidationError, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource

from eleven_video.exceptions.custom_errors import ConfigurationError
from eleven_video.config.persistence import load_config


class JsonConfigSettingsSource(PydanticBaseSettingsSource):
    """Custom settings source that loads values from JSON config file.
    
    This allows user preferences set via `eleven-video setup` to be
    automatically available as defaults when Settings() is created.
    """
    
    def get_field_value(
        self, field: Any, field_name: str
    ) -> Tuple[Any, str, bool]:
        """Get a field value from JSON config.
        
        Returns:
            Tuple of (value, field_name, is_complex)
        """
        json_config = load_config()
        field_value = json_config.get(field_name)
        return field_value, field_name, False
    
    def __call__(self) -> dict[str, Any]:
        """Load all values from JSON config."""
        return load_config()


class _SettingsBase(BaseSettings):
    """Internal Settings class - use Settings() which wraps validation errors."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        """Customize settings sources to include JSON config.
        
        Priority (highest to lowest):
        1. init_settings - Passed directly to constructor
        2. env_settings - Shell environment variables
        3. dotenv_settings - .env file
        4. json_config - JSON config from platformdirs
        5. file_secret_settings - Secrets files
        """
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            JsonConfigSettingsSource(settings_cls),
            file_secret_settings,
        )
    
    elevenlabs_api_key: SecretStr
    gemini_api_key: SecretStr
    project_root: str = "."

    @model_validator(mode="after")
    def validate_non_empty_keys(self) -> "_SettingsBase":
        """Ensure API keys are not empty strings."""
        errors = []
        
        if not self.elevenlabs_api_key.get_secret_value():
            errors.append("ELEVENLABS_API_KEY")
        
        if not self.gemini_api_key.get_secret_value():
            errors.append("GEMINI_API_KEY")
        
        if errors:
            raise ConfigurationError(
                f"API keys cannot be empty: {', '.join(errors)}. "
                "Please provide valid API key values."
            )
        
        return self


def Settings(_profile_override: str | None = None, _env_file: str | None = None, **kwargs: Any) -> _SettingsBase:
    """Create application settings with proper error handling.
    
    API keys are loaded from:
    1. Shell environment variables (highest priority)
    2. .env file from active profile (or override or explicit _env_file)
    3. Default .env file in project root
    
    Both keys are required. Missing keys raise ConfigurationError.
    Keys are stored as SecretStr to prevent accidental logging.
    
    Args:
        _profile_override: Use this profile's .env for this call only (not persisted)
        _env_file: Explicit .env file path (takes precedence over profiles, for testing)
        **kwargs: Optional overrides for settings fields
    
    Returns:
        Settings instance with validated configuration
        
    Raises:
        ConfigurationError: If required API keys are missing or empty
    """
    from eleven_video.config.persistence import list_profiles, get_active_profile
    
    # Determine which .env file to use
    env_file = ".env"  # Default
    
    # Explicit _env_file takes highest precedence (for testing)
    if _env_file:
        env_file = _env_file
    elif _profile_override:
        # Use overridden profile's .env file
        profiles = list_profiles()
        if _profile_override in profiles:
            env_file = profiles[_profile_override]
    else:
        # Use active profile's .env file
        active = get_active_profile()
        if active:
            profiles = list_profiles()
            if active in profiles:
                env_file = profiles[active]
    
    # Create dynamic subclass with updated env_file
    # This is needed because pydantic-settings v2 doesn't accept _env_file as init param
    class _DynamicSettings(_SettingsBase):
        model_config = SettingsConfigDict(
            env_file=env_file,
            env_file_encoding="utf-8",
            extra="ignore",
        )
    
    try:
        return _DynamicSettings(**kwargs)
    except ValidationError as e:
        # Extract missing field names from Pydantic error
        missing_fields = []
        for error in e.errors():
            if error.get("type") == "missing":
                field_name = error.get("loc", ["unknown"])[0]
                # Convert to env var format
                if field_name == "elevenlabs_api_key":
                    missing_fields.append("ELEVENLABS_API_KEY")
                elif field_name == "gemini_api_key":
                    missing_fields.append("GEMINI_API_KEY")
                else:
                    missing_fields.append(str(field_name).upper())
        
        if missing_fields:
            raise ConfigurationError(
                f"Missing required API key configuration: {', '.join(missing_fields)}. "
                "Please set these environment variables or add them to your .env file."
            ) from e
        
        # Re-raise as ConfigurationError for other validation issues
        raise ConfigurationError(
            f"Invalid configuration: {str(e)}"
        ) from e
