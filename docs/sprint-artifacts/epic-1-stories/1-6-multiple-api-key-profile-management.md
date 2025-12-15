# Story 1.6: Multiple API Key Profile Management

Status: done

## Story

As a user,
I want to manage multiple API key profiles by switching between different environment configurations,
so that I can verify different settings (e.g. Prod vs Dev keys) without constantly editing a single `.env` file.

## Acceptance Criteria

1. **Given** I have multiple `.env` files (e.g., `.env.dev`, `.env.prod`), **When** I run `eleven-video profile create <name> --env-file <path>`, **Then** a new profile is registered pointing to that specific file.
2. **Given** multiple profiles, **When** I run `eleven-video profile list`, **Then** I see all profiles and the .env file they reference, with the active one highlighted.
3. **Given** multiple profiles, **When** I run `eleven-video profile switch <name>`, **Then** the application persists this selection and loads environment variables from the referenced file in future sessions.
4. **Security Constraint**: API keys must **NEVER** be stored in the profile configuration (`config.json`). They must remain in the referenced `.env` files.
5. **Given** I want to use a specific profile for a single command, **When** I run `eleven-video --profile <name> <command>`, **Then** the command uses the specified profile without changing the persisted active profile.

## Tasks / Subtasks

- [x] Task 1: Configuration Schema Update (AC: 1, 3, 4)
  - [x] Update `eleven_video/config/persistence.py` and `Config` model to store a `profiles` map: `Dict[str, FilePath]`.
  - [x] Update `eleven_video/config/settings.py` logic to load the `.env` file specified by `active_profile` in `config.json`.
  - [x] Implement dynamic `.env` resolution: call `load_config()` → get `active_profile` → resolve path → pass to `Settings(_env_file=...)`.
- [x] Task 2: Profile Management Commands (AC: 1, 2, 3)
  - [x] Implement `profile create <name> --env-file <path>` command.
    - [x] Validate that the target `.env` file exists.
  - [x] Implement `profile list` to show Name -> Env Path mapping.
  - [x] Implement `profile switch <name>` to update `active_profile` in `config.json`.
  - [x] Implement `profile delete <name>` to remove a profile from `config.json`.
  - [x] Use `eleven_video/ui/displays.py` for listing.
- [x] Task 3: Global Profile Override (AC: 5)
  - [x] Add `--profile` option to main Typer app as a global callback.
  - [x] Pass selected profile to `Settings()` to override active profile for that command only.

## Dev Notes

### Architecture Patterns
- **Security**: "Keys stay in .env". The CLI only manages *pointers* to these files.
- **Data Architecture**:
  ```json
  {
    "active_profile": "dev",
    "profiles": {
      "default": ".env",
      "dev": ".env.dev",
      "prod": "/home/user/secure/.env.prod"
    }
  }
  ```
- **CLI**: Typer command groups.

### Source Tree Components
- `eleven_video/main.py`
- `eleven_video/config/persistence.py`
- `eleven_video/config/settings.py`

### Testing Standards
- Test that switching profiles actually causes `Settings` to load values from the new target file.
- Verify `config.json` does NOT contain any API key data.
- Test invalid file paths are rejected.

## File List

- `eleven_video/config/persistence.py` - Added `create_profile`, `list_profiles`, `get_active_profile`, `switch_profile`, `delete_profile` functions; updated docstring
- `eleven_video/config/settings.py` - Updated `Settings()` to accept `_profile_override` and `_env_file` params
- `eleven_video/main.py` - Added `profile` subapp with create/list/switch/delete commands, added `--profile` global option; status command now uses profile override
- `tests/config/test_profile_management.py` - 16 unit tests for profile management
- `tests/cli/test_profile_commands.py` - 10 CLI integration tests
- `tests/e2e/test_environment.py` - Fixed test isolation issue (load_dotenv at module level)

## Dev Agent Record

### Context Reference
- `docs/architecture/core-architectural-decisions.md`
- `docs/sprint-artifacts/tech-spec-epic-1.md`
- `docs/epics.md` (FR27)

### Agent Model Used
- Gemini-2.0-Pro-Exp-02-05

### Completion Notes List
- Re-architected for security (Env file pointers).
- Defined switching logic.
- Implemented 5 profile functions in `persistence.py`: create, list, get_active, switch, delete
- Settings() now uses dynamic subclass to set `env_file` in `model_config` (pydantic-settings v2 compatible)
- Added `_profile_override` parameter to Settings() for AC5 single-command override
- Added `profile` Typer subapp with 4 commands: create, list, switch, delete
- Added `--profile` global option to main app callback
- All 131 tests pass (full regression suite)
- Code review fixes applied: `_env_file` backward compatibility, status command profile override, test isolation fix

## Change Log

- 2025-12-14: Implemented Story 1.6 - Multiple API Key Profile Management (Amelia/Dev Agent)
- 2025-12-14: Code review fixes - Added _env_file param, status command profile override, test isolation fix (Amelia/Dev Agent)

