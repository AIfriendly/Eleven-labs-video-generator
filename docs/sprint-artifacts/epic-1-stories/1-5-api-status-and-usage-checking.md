# Story 1.5: API Status and Usage Checking

Status: Done

## Story

As a user,
I want to check API status and my current usage quotas from the terminal,
so that I can verify my API keys are working and monitor my consumption.

## Acceptance Criteria

1. **Given** configured API keys, **When** I run the API status command (e.g. `eleven-video status`), **Then** I see the current connectivity status of both Eleven Labs and Google Gemini APIs.
2. **Given** valid credentials, **When** I check status, **Then** I see my current usage/quota (e.g., remaining characters for Eleven Labs). Note: Gemini API does not expose quota via API; only connectivity is verified.
3. **Given** invalid credentials or connection issues, **Then** a clear error message indicates which service is failing.
4. The output must be formatted as a readable table using Rich.
5. **Given** the `--json` flag is provided, **Then** the output is raw JSON (useful for scripting).
6. **Given** one API is reachable but another fails, **Then** the status command shows partial results with clear indicators for each service's state (graceful degradation).

## Tasks / Subtasks

- [x] Task 1: API Adapter & Interfaces (AC: 1, 3)
  - [x] Add `tenacity` dependency for retry logic.
  - [x] Define `ServiceHealth` Protocol in `eleven_video/api/interfaces.py` with methods `check_health()` and `get_usage()`.
  - [x] Implement `eleven_video/api/elevenlabs.py` adapter (fetches `GET /v1/user/subscription`).
  - [x] Implement `eleven_video/api/gemini.py` adapter (fetches `GET /v1beta/models?page_size=1` for lightweight auth check).
- [x] Task 2: Status Command UI (AC: 2, 4, 5)
  - [x] Implement `status` command in `eleven_video/main.py`.
  - [x] Implement logic to iterate over registered services.
  - [x] Use `eleven_video/ui/displays.py` to render the "Service Status" table.
  - [x] Implement `--json` output formatted via `json.dumps`.
  - [x] Use `httpx` async execution to check services in parallel.

## Dev Notes

### Architecture Patterns
- **API Integration**: HTTPX for both sync and async.
- **Resilience**: Use `tenacity` for handling transient network errors/timeouts cleanly.
- **Polymorphism**: Use `ServiceHealth` protocol to decouple the CLI command from specific service implementations.
- **UI**: Rich Tables for human output, standard JSON for machine output.

### Dependencies
- `httpx` — async HTTP client for parallel service checks
- `tenacity` — retry logic for transient failures

### Source Tree Components
- `eleven_video/api/interfaces.py` (New)
- `eleven_video/api/elevenlabs.py`
- `eleven_video/api/gemini.py`
- `eleven_video/main.py`
- `eleven_video/ui/displays.py`

### Testing Standards
- Mock API responses for success/failure scenarios.
- Verify `status --json` output structure.
- Test error display when API is down (verify graceful degradation).

## Dev Agent Record

### Context Reference
- `docs/architecture/core-architectural-decisions.md` (API & Communication Patterns)
- `docs/epics.md` (FR22)

### Agent Model Used
- Gemini-2.5-Pro

### Completion Notes
- **Task 1**: Implemented `ServiceHealth` protocol with `HealthResult` and `UsageResult` dataclasses; created `ElevenLabsAdapter` (subscription endpoint) and `GeminiAdapter` (models endpoint) with tenacity retry logic.
- **Task 2**: Implemented `status` command with Rich table output, `--json` flag, async parallel checks via `asyncio.gather()`, and graceful degradation.
- **Tests**: 11 interface + 11 ElevenLabs + 8 Gemini + 5 status command + 9 displays = 44 tests.
- **Regression**: Full suite of 105 tests passes.

## File List

### New Files
- `eleven_video/api/interfaces.py` - ServiceHealth protocol, HealthResult, UsageResult dataclasses
- `eleven_video/api/elevenlabs.py` - ElevenLabs API adapter
- `eleven_video/api/gemini.py` - Gemini API adapter
- `eleven_video/ui/displays.py` - render_status_table, build_status_json functions
- `tests/api/__init__.py` - Test package init
- `tests/api/test_interfaces.py` - Tests for protocol and dataclasses
- `tests/api/test_elevenlabs.py` - Tests for ElevenLabs adapter
- `tests/api/test_gemini.py` - Tests for Gemini adapter
- `tests/cli/test_status_command.py` - Tests for status command
- `tests/ui/__init__.py` - Test package init for UI module
- `tests/ui/test_displays.py` - Tests for render_status_table and build_status_json

### Modified Files
- `pyproject.toml` - Added httpx and tenacity dependencies
- `eleven_video/api/__init__.py` - Added exports for adapters and interfaces
- `eleven_video/main.py` - Added status command, fixed parallel checks
- `eleven_video/ui/__init__.py` - UI module exports

## Change Log

- 2025-12-14: Story implementation complete. All acceptance criteria satisfied.
- 2025-12-14: Code review fixes applied: M1 (asyncio.gather for true parallel), L2 (429 rate limit handling), L3 (RemoteProtocolError retry), M2 (9 displays tests added), M3/L4 (File List updated).
