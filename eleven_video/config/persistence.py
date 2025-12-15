"""
Configuration Persistence Layer for Stories 1.3 and 1.6

Handles JSON configuration file I/O using platformdirs for OS-standard paths.
- Story 1.3: Interactive setup and config file creation
- Story 1.6: Multiple API key profile management
Security: API keys are explicitly filtered and never stored in config files.
"""

import json
from pathlib import Path
from typing import Any

import platformdirs

# Application name used for config directory
APP_NAME = "eleven-video"

# Keys that should NEVER be stored in config (security constraint AC5)
FORBIDDEN_KEYS = frozenset({
    "api_key",
    "elevenlabs_api_key", 
    "gemini_api_key",
    "google_api_key",
    "secret",
    "password",
    "token",
})


def get_config_path() -> Path:
    """
    Get the path to the configuration file.
    
    Uses platformdirs to determine OS-standard config directory:
    - Windows: C:\\Users\\{user}\\AppData\\Local\\eleven-video\\config.json
    - Linux: ~/.config/eleven-video/config.json
    - macOS: ~/Library/Application Support/eleven-video/config.json
    
    Returns:
        Path to config.json file
    """
    config_dir = platformdirs.user_config_dir(APP_NAME)
    return Path(config_dir) / "config.json"


def load_config() -> dict[str, Any]:
    """
    Load configuration from the JSON file.
    
    Returns:
        dict: Configuration values, or empty dict if file doesn't exist
    """
    config_path = get_config_path()
    
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # Return empty dict on corrupted/unreadable file
        return {}


def _filter_sensitive_keys(data: dict[str, Any]) -> dict[str, Any]:
    """
    Remove any keys that might contain sensitive information like API keys.
    
    Args:
        data: Configuration dict to filter
        
    Returns:
        Filtered dict with sensitive keys removed
    """
    filtered = {}
    for key, value in data.items():
        key_lower = key.lower()
        # Check if key matches any forbidden pattern
        is_sensitive = any(
            forbidden in key_lower 
            for forbidden in FORBIDDEN_KEYS
        )
        if not is_sensitive:
            filtered[key] = value
    return filtered


def save_config(data: dict[str, Any]) -> None:
    """
    Save configuration to the JSON file.
    
    - Creates directory if it doesn't exist
    - Merges with existing config (partial updates supported)
    - Filters out API keys and sensitive data (security constraint)
    
    Args:
        data: Configuration values to save
    """
    config_path = get_config_path()
    
    # Ensure directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing config to merge
    existing = load_config()
    
    # Filter sensitive keys from new data
    filtered_data = _filter_sensitive_keys(data)
    
    # Merge new data into existing
    existing.update(filtered_data)
    
    # Write merged config
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)


# =============================================================================
# Profile Management Functions (Story 1.6)
# =============================================================================

def create_profile(name: str, env_file_path: str) -> None:
    """
    Register a new profile pointing to the given .env file.
    
    Args:
        name: Profile name (e.g., "dev", "prod")
        env_file_path: Path to the .env file
        
    Raises:
        ConfigurationError: If the .env file does not exist
    """
    from eleven_video.exceptions.custom_errors import ConfigurationError
    
    # Convert to absolute path
    env_path = Path(env_file_path).resolve()
    
    # Validate file exists
    if not env_path.exists():
        raise ConfigurationError(f"Environment file does not exist: {env_path}")
    
    # Load current config
    config = load_config()
    
    # Initialize profiles dict if not exists
    if "profiles" not in config:
        config["profiles"] = {}
    
    # Add profile with absolute path
    config["profiles"][name] = str(env_path)
    
    # Set as active if this is the first profile
    if "active_profile" not in config:
        config["active_profile"] = name
    
    # Save (using direct write to include profiles)
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def list_profiles() -> dict[str, str]:
    """
    Return all profiles as {name: env_path} dict.
    
    Returns:
        dict mapping profile names to their .env file paths
    """
    config = load_config()
    return config.get("profiles", {})


def get_active_profile() -> str | None:
    """
    Return the name of the currently active profile.
    
    Returns:
        Active profile name, or None if not set
    """
    config = load_config()
    return config.get("active_profile")


def switch_profile(name: str) -> None:
    """
    Set the active profile to the given name.
    
    Args:
        name: Profile name to switch to
        
    Raises:
        ConfigurationError: If the profile does not exist
    """
    from eleven_video.exceptions.custom_errors import ConfigurationError
    
    config = load_config()
    profiles = config.get("profiles", {})
    
    if name not in profiles:
        raise ConfigurationError(f"Profile not found: {name}")
    
    config["active_profile"] = name
    
    # Save config directly
    config_path = get_config_path()
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def delete_profile(name: str) -> None:
    """
    Remove a profile from config.
    
    Args:
        name: Profile name to delete
        
    Raises:
        ConfigurationError: If profile is active or doesn't exist
    """
    from eleven_video.exceptions.custom_errors import ConfigurationError
    
    config = load_config()
    profiles = config.get("profiles", {})
    
    if name not in profiles:
        raise ConfigurationError(f"Profile not found: {name}")
    
    if config.get("active_profile") == name:
        raise ConfigurationError(f"Cannot delete active profile: {name}")
    
    del config["profiles"][name]
    
    # Save config directly
    config_path = get_config_path()
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

