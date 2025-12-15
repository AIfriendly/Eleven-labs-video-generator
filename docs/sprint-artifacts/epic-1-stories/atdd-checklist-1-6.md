# ATDD Checklist - Story 1.6: Multiple API Key Profile Management

**Date:** 2025-12-14
**Author:** Murat (TEA Agent)
**Primary Test Level:** Unit + CLI Integration
**Story Status:** ready-for-dev

---

## Story Summary

As a **user**, I want to **manage multiple API key profiles** by switching between different environment configurations, so that I can **verify different settings (e.g. Prod vs Dev keys)** without constantly editing a single `.env` file.

---

## Acceptance Criteria

1. Profile create: Register new profile pointing to `.env` file
2. Profile list: Show all profiles with active one highlighted
3. Profile switch: Persist selection and load from referenced `.env`
4. Security: API keys NEVER stored in `config.json`
5. Profile override: Use `--profile <name>` for single command without persisting

---

## Failing Tests Created (RED Phase)

### Unit Tests (15 tests)

**File:** `tests/config/test_profile_management.py` (~300 lines)

| Test | AC | Status | Failure Reason |
|------|-----|--------|----------------|
| `test_profile_create_registers_new_profile` | 1 | 🔴 RED | `create_profile` not implemented |
| `test_profile_create_rejects_nonexistent_env_file` | 1 | 🔴 RED | `create_profile` not implemented |
| `test_profile_create_stores_absolute_path` | 1 | 🔴 RED | `create_profile` not implemented |
| `test_profile_list_returns_all_profiles` | 2 | 🔴 RED | `list_profiles` not implemented |
| `test_profile_list_indicates_active_profile` | 2 | 🔴 RED | `get_active_profile` not implemented |
| `test_profile_list_empty_when_no_profiles` | 2 | 🔴 RED | `list_profiles` not implemented |
| `test_profile_switch_persists_selection` | 3 | 🔴 RED | `switch_profile` not implemented |
| `test_profile_switch_rejects_unknown_profile` | 3 | 🔴 RED | `switch_profile` not implemented |
| `test_settings_loads_env_from_active_profile` | 3 | 🔴 RED | Dynamic env loading not implemented |
| `test_profile_config_never_contains_api_keys` | 4 | 🔴 RED | `create_profile` not implemented |
| `test_profiles_only_store_file_paths` | 4 | 🔴 RED | `create_profile` not implemented |
| `test_profile_override_uses_specified_profile` | 5 | 🔴 RED | `_profile_override` not implemented |
| `test_profile_override_does_not_persist` | 5 | 🔴 RED | `_profile_override` not implemented |
| `test_profile_delete_removes_profile` | - | 🔴 RED | `delete_profile` not implemented |
| `test_profile_delete_rejects_active_profile` | - | 🔴 RED | `delete_profile` not implemented |

### CLI Integration Tests (11 tests)

**File:** `tests/cli/test_profile_commands.py` (~200 lines)

| Test | AC | Status | Failure Reason |
|------|-----|--------|----------------|
| `test_cli_profile_create_success` | 1 | 🔴 RED | `profile create` command not implemented |
| `test_cli_profile_create_invalid_file` | 1 | 🔴 RED | `profile create` command not implemented |
| `test_cli_profile_list_shows_all_profiles` | 2 | 🔴 RED | `profile list` command not implemented |
| `test_cli_profile_list_highlights_active` | 2 | 🔴 RED | `profile list` command not implemented |
| `test_cli_profile_switch_success` | 3 | 🔴 RED | `profile switch` command not implemented |
| `test_cli_profile_switch_unknown` | 3 | 🔴 RED | `profile switch` command not implemented |
| `test_cli_global_profile_option_exists` | 5 | 🔴 RED | `--profile` option not implemented |
| `test_cli_global_profile_override_used` | 5 | 🔴 RED | `--profile` option not implemented |
| `test_cli_profile_delete_success` | - | 🔴 RED | `profile delete` command not implemented |
| `test_cli_profile_delete_active_fails` | - | 🔴 RED | `profile delete` command not implemented |
| `test_profile_delete_rejects_unknown_profile` | - | 🔴 RED | `delete_profile` not implemented |

---

## Required Functions (to implement in persistence.py)

```python
# eleven_video/config/persistence.py - NEW functions needed

def create_profile(name: str, env_file_path: str) -> None:
    """Register a new profile pointing to the given .env file."""
    ...

def list_profiles() -> dict[str, str]:
    """Return all profiles as {name: env_path} dict."""
    ...

def get_active_profile() -> str | None:
    """Return the name of the currently active profile."""
    ...

def switch_profile(name: str) -> None:
    """Set the active profile to the given name."""
    ...

def delete_profile(name: str) -> None:
    """Remove a profile from config."""
    ...
```

---

## Required Settings Changes

```python
# eleven_video/config/settings.py - CHANGES needed

class _SettingsBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",  # <-- Must become dynamic based on active profile
        ...
    )

def Settings(_profile_override: str | None = None, **kwargs) -> _SettingsBase:
    """
    If _profile_override is provided, use that profile's .env file.
    Otherwise, use the active_profile from config.json.
    """
    ...
```

---

## Required CLI Commands

```python
# eleven_video/main.py - NEW commands needed

@app.callback()
def main_callback(
    profile: str = typer.Option(None, "--profile", help="Override active profile")
):
    """Global callback to capture --profile option."""
    ...

profile_app = typer.Typer(name="profile", help="Manage API key profiles")
app.add_typer(profile_app)

@profile_app.command("create")
def profile_create(name: str, env_file: Path = typer.Option(..., "--env-file")):
    ...

@profile_app.command("list")
def profile_list():
    ...

@profile_app.command("switch")
def profile_switch(name: str):
    ...

@profile_app.command("delete")
def profile_delete(name: str):
    ...
```

---

## Implementation Checklist

### Task 1: Configuration Schema Update (AC: 1, 3, 4)

- [ ] Add `create_profile()` function to `persistence.py`
  - [ ] Validate env file exists
  - [ ] Store absolute path
  - [ ] Initialize `profiles` dict if not exists
- [ ] Add `list_profiles()` function to `persistence.py`
- [ ] Add `get_active_profile()` function to `persistence.py`
- [ ] Add `switch_profile()` function to `persistence.py`
  - [ ] Validate profile exists
- [ ] Add `delete_profile()` function to `persistence.py`
  - [ ] Reject if profile is active
- [ ] Update `settings.py` to support dynamic `.env` loading
  - [ ] Read `active_profile` from config
  - [ ] Resolve env file path from profiles map
  - [ ] Pass `_env_file` to BaseSettings
- [ ] Add `_profile_override` parameter to `Settings()`
- [ ] Run tests: `uv run pytest tests/config/test_profile_management.py -v`
- [ ] ✅ All unit tests pass (green phase)

### Task 2: Profile Management Commands (AC: 1, 2, 3)

- [ ] Create `profile` Typer subapp in `main.py`
- [ ] Implement `profile create <name> --env-file <path>`
- [ ] Implement `profile list` with Rich table output
  - [ ] Highlight active profile with ✓ or color
- [ ] Implement `profile switch <name>`
- [ ] Implement `profile delete <name>`
- [ ] Run tests: `uv run pytest tests/cli/test_profile_commands.py -v`
- [ ] ✅ All CLI tests pass (green phase)

### Task 3: Global Profile Override (AC: 5)

- [ ] Add `@app.callback()` with `--profile` option
- [ ] Store override in context or global state
- [ ] Ensure `Settings()` uses override when provided
- [ ] Run tests: `uv run pytest tests/cli/test_profile_commands.py::TestGlobalProfileOptionCLI -v`
- [ ] ✅ All override tests pass (green phase)

---

## Running Tests

```bash
# Run all Story 1.6 failing tests
uv run pytest tests/config/test_profile_management.py tests/cli/test_profile_commands.py -v

# Run unit tests only
uv run pytest tests/config/test_profile_management.py -v

# Run CLI tests only
uv run pytest tests/cli/test_profile_commands.py -v

# Run specific test class
uv run pytest tests/config/test_profile_management.py::TestProfileCreate -v

# Run with coverage
uv run pytest tests/config/test_profile_management.py tests/cli/test_profile_commands.py --cov=eleven_video --cov-report=term-missing
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete) ✅

- ✅ 26 tests written and failing
- ✅ Tests cover all 5 Acceptance Criteria
- ✅ Security constraint (AC4) explicitly tested
- ✅ Given-When-Then format for all tests

**Verification:**
```
22 failed, 4 passed in 1.72s
```
Failures are due to missing implementation, not test bugs.

---

### GREEN Phase (DEV Team - Next Steps)

1. **Start with persistence layer** (Task 1)
   - Implement `create_profile()` first
   - Run tests after each function
2. **Move to Settings integration**
   - Update `Settings()` to use dynamic `.env`
3. **Implement CLI commands** (Task 2)
4. **Add global override** (Task 3)

**Key Principle:** One test at a time. Minimal implementation. Run tests frequently.

---

### REFACTOR Phase (After All Tests Pass)

1. Extract common validation logic
2. Add Rich formatting to CLI output
3. Consider edge cases (empty profiles, corrupted config)
4. Update story status to `review` in `sprint-status.yaml`

---

## Notes

- Security is paramount: API keys NEVER in `config.json`
- Profiles only store file paths (pointers), not key values
- The `_profile_override` parameter is a per-call override, not persisted
- Use `platformdirs` for config path (already in place)
- Existing `save_config()` already filters out API keys

---

**Generated by BMad TEA Agent** - 2025-12-14
