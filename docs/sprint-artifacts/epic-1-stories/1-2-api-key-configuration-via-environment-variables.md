# Story 1.2: API Key Configuration via Environment Variables

Status: done

## ATDD Checklist ✅

> [!TIP]
> **Implementation complete.** All 8 tests passing at `tests/config/test_settings.py`.

- **Checklist Document:** [atdd-checklist-1-2.md](../atdd-checklist-1-2.md)
- **Test File:** `tests/config/test_settings.py` ✅ Passing
- **Primary Test Level:** Unit Tests (pytest)
- **Total Tests:** 8 passing tests covering all 4 ACs

### Test Coverage Summary

| AC | Test Class | Tests |
|----|------------|-------|
| AC1 | `TestEnvFileLoading` | 2 tests (.env loading for both keys) |
| AC2 | `TestEnvironmentPrecedence` | 2 tests (shell > .env for both keys) |
| AC3 | `TestApiKeyMasking` | 3 tests (str masking, repr masking) |
| AC4 | `TestMissingKeyErrorHandling` | 1 test (ConfigurationError) |

---

## Story

As a user,
I want to configure my Eleven Labs and Google Gemini API keys via environment variables,
so that my keys are stored securely without being logged or displayed.

## Acceptance Criteria

1. **Given** I have an `.env` file with `ELEVEN_API_KEY` and `GEMINI_API_KEY` defined, **When** the application starts, **Then** these values are loaded into the configuration.
2. **Given** environment variables are set in the shell (export/set), **When** the application starts, **Then** these values take precedence over `.env` files (standard 12-factor app behavior).
3. **Given** the application is running, **When** configuration is logged or displayed, **Then** API key values are masked (e.g., `sk-****`).
4. **Given** missing API keys, **When** specific functionality requiring them is accessed, **Then** a clear error message indicates configuration is missing.

## Tasks / Subtasks

- [x] Task 1: Environment Variable Loading (AC: 1, 2)
  - [x] Add `python-dotenv` and `pydantic-settings` dependencies.
  - [x] Implement `src/config/settings.py` using Pydantic `BaseSettings`.
  - [x] Define `Settings` class with `eleven_api_key` and `gemini_api_key` fields.
  - [x] Ensure `.env` file loading is configured (via `Config` class or `model_config`).
- [x] Task 2: Security and Masking (AC: 3)
  - [x] Use Pydantic's `SecretStr` type for API key fields to enforce automatic masking in `__repr__` and logging.
  - [x] Implement `get_secret_value()` usage only where raw keys are strictly needed (in API adapters).
- [x] Task 3: Error Handling for Missing Keys (AC: 4)
  - [x] Create custom exception `ConfigurationError` in `src/exceptions/custom_errors.py`.
  - [x] Add validation (e.g., proper `@field_validator` or root validator) to raise `ConfigurationError` if keys are missing/empty when required.

## Dev Notes

### Architecture Patterns
- **Configuration**: Use `pydantic-settings` for robust environment variable handling.
- **Security**: "Environment variables via .env files" is a critical architectural decision. Use `SecretStr` to prevent accidental leakage in logs.
- **Structure**:
  - `src/config/settings.py`: Main settings model.
  - `.env`: Gitignored file (ensure in `.gitignore`).
  - `.env.example`: Template committed to git.

### Source Tree Components
- `src/config/settings.py`
- `src/config/__init__.py`
- `src/exceptions/custom_errors.py`
- `.env.example`

### Testing Standards
- Create `tests/config/test_settings.py`.
- Test precedence: Shell Env > .env file > Default.
- Use `pytest`'s `monkeypatch` fixture to simulate environment variables safely during tests.
- Verify that `str(settings.eleven_api_key)` returns `**********` (or similar masked value) and not the actual key.

## Dev Agent Record

### Context Reference
- `docs/architecture/core-architectural-decisions.md` (Security Guardian Persona)
- `docs/architecture/project-structure-boundaries.md`

### Agent Model Used
- Gemini-2.5-Pro

### Completion Notes List
- Implemented `Settings()` factory function with Pydantic BaseSettings via `pydantic-settings`
- Used `SecretStr` for both API key fields - automatic masking in str/repr
- Created `ConfigurationError` exception class in `src/exceptions/custom_errors.py`
- Added `model_validator` for empty key detection
- Wrapped Pydantic `ValidationError` to raise `ConfigurationError` for missing keys (AC4)
- All 8 ATDD tests passing, 32 total tests pass (no regressions)

## File List

### New Files
- `eleven_video/config/settings.py`
- `eleven_video/exceptions/custom_errors.py`
- `tests/config/__init__.py`
- `tests/config/test_settings.py`

### Modified Files
- `pyproject.toml` (added `pydantic-settings` dependency)
- `.env.example` (updated to use `ELEVENLABS_API_KEY`)
- `eleven_video/config/__init__.py` (exports Settings)
- `eleven_video/exceptions/__init__.py` (exports ConfigurationError)

## Change Log

| Date | Description |
|------|-------------|
| 2025-12-13 | Implemented Story 1-2: API Key Configuration. Added Settings class with SecretStr, ConfigurationError exception, and pydantic-settings integration. All 8 tests passing. |
| 2025-12-13 | **Code Review (AI):** Fixed `.env.example` env var name, added missing files to File List, added empty-key test. 9 tests now. |
| 2025-12-13 | **Fix:** Renamed `ELEVEN_API_KEY` → `ELEVENLABS_API_KEY` per official ElevenLabs documentation. Updated settings.py, .env.example, and all tests. |
| 2025-12-13 | **Refactor:** Consolidated code from `src/` to `eleven_video/` package. Deleted `src/`. Updated all imports and tests. 33 tests passing. |


