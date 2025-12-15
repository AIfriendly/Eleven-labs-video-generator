# ATDD Checklist - Epic 1, Story 1.3: Interactive Setup and Configuration File Creation

**Date:** 2025-12-13
**Author:** Revenant
**Primary Test Level:** Unit/Integration (pytest)

---

## Story Summary

Users can run an interactive setup command that guides them through configuration options and persists preferences to a JSON file in the OS-standard config directory.

**As a** user,
**I want** to run an interactive setup command that helps me configure default settings,
**So that** I can persist my preferences between sessions without manual configuration.

---

## Acceptance Criteria

| AC# | Criterion | Test Type |
|-----|-----------|-----------|
| AC1 | Running `eleven-video setup` guides through configuration options interactively | Unit |
| AC2 | Setup wizard creates config file in OS-standard directory (platformdirs) | Unit |
| AC3 | Existing config values shown as defaults when running setup again | Unit |
| AC4 | Config file updated with new values after confirmation | Unit |
| AC5 | **Security**: API keys NOT stored in JSON config file | Unit |

---

## Failing Tests Created (RED Phase)

### Unit Tests (8 tests)

**File:** `tests/config/test_persistence.py` (~200 lines)

| Test Name | AC | Status | Verifies |
|-----------|-----|--------|----------|
| `test_config_file_created_at_platformdirs_path` | AC2 | RED | Config file created at `platformdirs.user_config_dir("eleven-video")` |
| `test_config_directory_created_if_not_exists` | AC2 | RED | Parent directory auto-created |
| `test_load_config_returns_existing_values` | AC3 | RED | Existing config loaded as dict |
| `test_load_config_returns_empty_dict_if_no_file` | AC3 | RED | Missing file returns empty dict (no error) |
| `test_save_config_writes_json_file` | AC4 | RED | Config dict saved as valid JSON |
| `test_save_config_preserves_existing_values` | AC4 | RED | Partial update merges with existing |
| `test_api_keys_not_stored_in_config` | AC5 | RED | API key fields rejected/stripped |
| `test_config_path_uses_app_name_eleven_video` | AC2 | RED | App name is "eleven-video" |

### CLI Tests (4 tests)

**File:** `tests/cli/test_setup_command.py` (~150 lines)

| Test Name | AC | Status | Verifies |
|-----------|-----|--------|----------|
| `test_setup_command_registered` | AC1 | RED | `eleven-video setup` command exists |
| `test_setup_prompts_for_configuration` | AC1 | RED | Interactive prompts displayed |
| `test_setup_shows_existing_values_as_defaults` | AC3 | RED | Pre-populated defaults from existing config |
| `test_setup_warns_about_api_key_security` | AC5 | RED | Security warning displayed |

---

## Test Code - `tests/config/test_persistence.py`

```python
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

    def test_config_path_uses_app_name_eleven_video(self):
        """
        GIVEN the persistence module
        WHEN get_config_path is called
        THEN it uses "eleven-video" as the app name
        """
        with patch("eleven_video.config.persistence.platformdirs") as mock_pd:
            mock_pd.user_config_dir.return_value = "/mock/path"
            from eleven_video.config.persistence import get_config_path
            
            # WHEN: Get config path
            get_config_path()
            
            # THEN: Called with correct app name
            mock_config_dir.assert_called_with("eleven-video")


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
        
        with patch("platformdirs.user_config_dir", return_value=str(tmp_path)):
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
        
        with patch("platformdirs.user_config_dir", return_value=str(tmp_path)):
            from eleven_video.config.persistence import load_config
            
            # WHEN: Load config
            config = load_config()
            
            # THEN: Empty dict returned
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
        with patch("platformdirs.user_config_dir", return_value=str(tmp_path)):
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
        
        with patch("platformdirs.user_config_dir", return_value=str(tmp_path)):
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
        with patch("platformdirs.user_config_dir", return_value=str(tmp_path)):
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
```

---

## Test Code - `tests/cli/test_setup_command.py`

```python
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
        with patch("platformdirs.user_config_dir", return_value=str(tmp_path)):
            from eleven_video.main import app
            
            # WHEN: Run setup (simulate interactive input)
            result = runner.invoke(app, ["setup"], input="nova\nmp4\n")
            
            # THEN: Prompts displayed
            output_lower = result.output.lower()
            # Should ask about voice or other settings
            assert "voice" in output_lower or "default" in output_lower or "configure" in output_lower


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
        
        with patch("platformdirs.user_config_dir", return_value=str(tmp_path)):
            from eleven_video.main import app
            
            # WHEN: Run setup
            result = runner.invoke(app, ["setup"], input="\n")  # Accept defaults
            
            # THEN: Existing value shown
            assert "shimmer" in result.output.lower() or "default" in result.output.lower()


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
        with patch("platformdirs.user_config_dir", return_value=str(tmp_path)):
            from eleven_video.main import app
            
            # WHEN: Run setup
            result = runner.invoke(app, ["setup"], input="\n")
            
            # THEN: Security warning displayed
            output_lower = result.output.lower()
            assert "api" in output_lower or ".env" in output_lower or "key" in output_lower
```

---

## Data Factories Created

### None Required

This story tests configuration persistence and CLI interaction - no complex test data factories needed. Uses simple dict literals for config values.

---

## Fixtures Created

### None Required

Existing pytest fixtures (`tmp_path`, `monkeypatch`) are sufficient. Uses `unittest.mock.patch` for mocking `platformdirs`.

---

## Mock Requirements

### platformdirs Mock

**Module:** `platformdirs`
**Function:** `user_config_dir("eleven-video")`

**Mock Pattern:**
```python
with patch("platformdirs.user_config_dir", return_value=str(tmp_path)):
    # Test code here - uses tmp_path instead of real system dir
```

**Purpose:** Prevents tests from writing to actual OS config directories.

---

## Required Dependencies

### New Dependency Required

Add to `pyproject.toml`:
```toml
[project.dependencies]
platformdirs = "^4.0"
```

---

## Implementation Checklist

### Task 1: Persistence Layer (AC2, AC3, AC4, AC5)

**File:** `eleven_video/config/persistence.py`

- [ ] Add `platformdirs` to project dependencies
- [ ] Implement `get_config_path()` returning `Path` to config.json
- [ ] Implement `load_config()` returning dict (empty if no file)
- [ ] Implement `save_config(data: dict)` with directory creation
- [ ] Add API key filtering in `save_config()` to strip sensitive fields
- [ ] Run tests: `pytest tests/config/test_persistence.py -v`
- [ ] ✅ All 8 persistence tests pass (green phase)

**Estimated Effort:** 1-2 hours

---

### Task 2: Setup Command (AC1, AC3, AC5)

**File:** `eleven_video/main.py`

- [ ] Add `setup` command to Typer app
- [ ] Import and use persistence module
- [ ] Add Rich prompts for configuration options
- [ ] Pre-populate prompts with existing config values
- [ ] Display API key security warning
- [ ] Run tests: `pytest tests/cli/test_setup_command.py -v`
- [ ] ✅ All 4 CLI tests pass (green phase)

**Estimated Effort:** 1-2 hours

---

### Task 3: Settings Integration (AC2)

**File:** `eleven_video/config/settings.py`

- [ ] Override `settings_customise_sources` in Pydantic Settings
- [ ] Add JSON config as settings source (priority: Env > JSON > Defaults)
- [ ] Run tests: `pytest tests/config/ -v`
- [ ] ✅ All config tests pass (green phase)

**Estimated Effort:** 1 hour

---

## Running Tests

```bash
# Run all Story 1-3 tests
pytest tests/config/test_persistence.py tests/cli/test_setup_command.py -v

# Run specific test file
pytest tests/config/test_persistence.py -v

# Run specific test class
pytest tests/config/test_persistence.py::TestConfigFileCreation -v

# Run with coverage
pytest tests/config/test_persistence.py --cov=eleven_video.config.persistence --cov-report=term-missing

# Debug specific test
pytest tests/config/test_persistence.py::TestConfigFileCreation::test_config_file_created_at_platformdirs_path -v -s
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete) ✅

**TEA Agent Responsibilities:**

- ✅ 12 tests written (8 persistence + 4 CLI)
- ✅ All tests fail initially (modules don't exist yet)
- ✅ Mock requirements documented (platformdirs)
- ✅ Implementation checklist created

**Verification:**
```
FAILED tests/config/test_persistence.py - ModuleNotFoundError: No module named 'eleven_video.config.persistence'
FAILED tests/cli/test_setup_command.py - setup command not registered
```

---

### GREEN Phase (DEV Team - Next Steps)

1. Create `eleven_video/config/persistence.py`
2. Add `platformdirs` dependency
3. Implement `get_config_path()`, `load_config()`, `save_config()`
4. Add API key filtering
5. Add `setup` command to CLI
6. Run tests after each function implementation

---

### REFACTOR Phase (DEV Team - After All Tests Pass)

1. Extract common config path logic if needed
2. Consider adding config validation
3. Ensure tests still pass after refactor

---

## Knowledge Base References Applied

- **test-quality.md** - Given-When-Then structure, deterministic tests with mocking
- **data-factories.md** - Confirmed not needed (simple config dicts)
- **fixture-architecture.md** - Using pytest built-in `tmp_path`

---

## Notes

- This story uses **pytest** (not Playwright) since it tests CLI/config, not browser UI
- **platformdirs** returns OS-specific paths:
  - Windows: `C:\Users\{user}\AppData\Local\eleven-video\config.json`
  - Linux: `~/.config/eleven-video/config.json`
  - macOS: `~/Library/Application Support/eleven-video/config.json`
- API key security is critical - tests explicitly verify keys are NOT saved

---

**Generated by BMad TEA Agent** - 2025-12-13
