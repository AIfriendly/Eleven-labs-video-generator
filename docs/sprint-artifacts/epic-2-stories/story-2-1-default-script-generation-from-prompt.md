# Story 2.1: Default Script Generation from Prompt

Status: done

## 1. Story

**As a** user,
**I want** the system to automatically generate a script from my text prompt using Google Gemini,
**so that** I don't need to write a script manually.

## 2. Acceptance Criteria

1.  **Given** I have provided a valid text prompt through the interactive terminal,
    **When** the script generation process is initiated,
    **Then** a coherent and relevant script is generated based on my prompt,
    **And** the script contains structured content suitable for video narration.

2.  **Given** the script generation process requires the Google Gemini API,
    **When** the system connects to the API,
    **Then** it successfully authenticates using the configured API key from the Settings class,
    **And** the API key is never exposed in logs, terminal output, or error messages.

3.  **Given** the script is being generated,
    **When** the process is active,
    **Then** the user sees a progress indicator in the terminal (FR23).

4.  **Given** I provide an empty or invalid prompt,
    **When** the generation is attempted,
    **Then** a clear, actionable error message is displayed without exposing internal details.

5.  **Given** the Gemini API returns an error (401 Unauthorized, 429 Rate Limited, 500 Server Error, or timeout),
    **When** the error is detected,
    **Then** the system displays a user-friendly error message indicating the issue type,
    **And** suggests corrective action where applicable.

## 3. Developer Context

### Technical Requirements
-   **Primary Goal:** Implement a `GeminiAdapter` class in `eleven_video/api/gemini.py` that integrates with the Google Gemini API to generate scripts from user prompts.
-   **Interface Contract:** Implement the `ScriptGenerator` protocol defined in `eleven_video/api/interfaces.py` with the signature `generate_script(prompt: str) -> Script`.
-   **SDK:** Use the official `google-generativeai` Python SDK (NOT raw HTTP clients like `requests` or `httpx`).
-   **Authentication:** Use the existing `Settings` class from `eleven_video/config/settings.py` to retrieve the `GEMINI_API_KEY`. Do NOT use `os.getenv()` directly.
-   **Security:** API keys must never be logged, displayed in terminal output, or included in error messages. Use `SecretStr` masking from Pydantic.
-   **Error Handling:** Implement robust error handling for:
    - Empty or invalid prompts (client-side validation)
    - Authentication failures (401)
    - Rate limiting (429)
    - Server errors (500, 503)
    - Network timeouts
-   **User Feedback:** Provide progress indication using the `rich` library's progress display during script generation.

### Architectural Compliance

-   **Hexagonal Architecture:** The Gemini API adapter belongs in the infrastructure layer (`eleven_video/api/`), implementing a domain port (interface).
-   **Separation of Concerns:**
    - `eleven_video/api/gemini.py` — API adapter for Gemini (infrastructure)
    - `eleven_video/api/interfaces.py` — Protocol/interface definitions (port)
    - `eleven_video/models/domain.py` — Script domain model
-   **Configuration:** Use dependency injection to provide the Settings instance to the adapter.
-   **Circuit Breaker:** Follow the circuit breaker pattern established in architecture decisions for API resilience (may be deferred to Epic 5/6 for full implementation, but basic error handling required now).

### Library & Framework Requirements
-   **SDK:** `google-generativeai` — Official Google Generative AI Python SDK
-   **Progress UI:** `rich` — For terminal progress indication
-   **Configuration:** `pydantic-settings` — Already in use via `Settings` class
-   **Dependencies:** Add `google-generativeai` to `pyproject.toml` under `[project.dependencies]`

### File & Code Structure

| File | Purpose |
|------|---------|
| `eleven_video/api/gemini.py` | [MODIFY] Gemini API adapter implementing `ScriptGenerator` |
| `eleven_video/api/interfaces.py` | [MODIFY] Add `ScriptGenerator` protocol |
| `eleven_video/models/domain.py` | [NEW/MODIFY] Add `Script` domain model |
| `eleven_video/exceptions/custom_errors.py` | [MODIFY] Add Gemini-specific exceptions |
| `pyproject.toml` | [MODIFY] Add `google-generativeai` dependency |
| `tests/api/test_gemini.py` | [NEW] Unit tests for Gemini adapter |

### Testing Requirements

-   **Unit Tests:** Create unit tests in `tests/api/test_gemini.py`:
    -   Mock the `google-generativeai` SDK responses to test without real API calls
    -   Test successful script generation with valid prompt
    -   Test empty prompt validation (raises error before API call)
    -   Test 401 Unauthorized handling
    -   Test 429 Rate Limit handling  
    -   Test 500/503 Server Error handling
    -   Test network timeout handling
    -   Test that API key is never exposed in error messages
    
-   **Integration Tests:** Create integration test marked to skip in CI:
    -   Test real API connection with valid credentials
    -   Verify script output format and quality

### API Reference

**Endpoint:** `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`

**Authentication Header:** `x-goog-api-key: $GEMINI_API_KEY`

**Default Model:** `gemini-2.5-flash` (switchable per PRD)

**SDK Usage:**
```python
import google.generativeai as genai

genai.configure(api_key=settings.gemini_api_key.get_secret_value())
model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content(prompt)
```

### Git Intelligence
-   No prior commits exist for this functionality.
-   Follow standard commit message conventions: `feat(api): Add Gemini script generation adapter`

### Project Context Reference
-   **PRD:** `docs/prd.md` — FR5 (auto-generate scripts), FR36 (Gemini integration)
-   **Epics:** `docs/epics.md` — Epic 2, Story 2.1
-   **Architecture:** `docs/architecture/core-architectural-decisions.md` — API adapter patterns
-   **Structure:** `docs/architecture/project-structure-boundaries.md` — File locations
-   **API Reference:** `docs/architecture/api-reference.md` — Endpoint details
-   **Tech Spec:** `docs/sprint-artifacts/tech-spec-epic-2.md` — Implementation guidance

## 4. Tasks

- [x] Add `google-generativeai` dependency to `pyproject.toml`
- [x] Create `Script` domain model in `eleven_video/models/domain.py`
- [x] Add `ScriptGenerator` protocol to `eleven_video/api/interfaces.py`
- [x] Add Gemini-specific exceptions to `eleven_video/exceptions/custom_errors.py`
- [x] Implement `GeminiAdapter.generate_script()` in `eleven_video/api/gemini.py`
- [x] Implement progress indicator via callback in generate_script
- [x] Write unit tests in `tests/api/test_gemini.py` (17 tests)
- [x] Integration test deferred to Epic 5/6 for real API validation
- [x] Verify all tests pass (148 total) and no API key exposure

## 5. File List

| File | Action |
|------|--------|
| `pyproject.toml` | MODIFIED - added google-generativeai>=0.8.0 |
| `eleven_video/models/domain.py` | NEW - Script dataclass |
| `eleven_video/models/__init__.py` | MODIFIED - exports Script |
| `eleven_video/api/interfaces.py` | MODIFIED - added ScriptGenerator protocol |
| `eleven_video/exceptions/custom_errors.py` | MODIFIED - added GeminiAPIError, ValidationError |
| `eleven_video/api/gemini.py` | MODIFIED - added generate_script() with Settings support |
| `tests/api/test_gemini.py` | MODIFIED - 17 unit tests + 2 integration tests |
| `docs/sprint-artifacts/sprint-status.yaml` | MODIFIED - status updates |

## 6. Completion Status

**Status:** Ready for Review
**Completion Date:** 2025-12-15

### Dev Agent Record

**Implementation Notes:**
-   Added `google-generativeai>=0.8.0` to project dependencies
-   Created `Script` domain model in `eleven_video/models/domain.py`
-   Added `ScriptGenerator` protocol to `eleven_video/api/interfaces.py`
-   Added `GeminiAPIError` and `ValidationError` to custom exceptions
-   Extended `GeminiAdapter` with `generate_script()` method:
    -   **Settings class support** (dependency injection for SecretStr security)
    -   Prompt validation (empty/whitespace/None) before API call
    -   Progress callback support for FR23 compliance
    -   **Retry logic with tenacity** for transient failures
    -   User-friendly error messages for 401/429/500/timeout
    -   API key sanitization in all error messages
-   All 17 Story 2.1 unit tests passing
-   2 integration tests added (skip in CI)
-   Full regression suite passing
-   No API key exposure in logs or error messages verified

### Code Review Fixes (2025-12-15)

-   **HIGH #1**: Added Settings class support to GeminiAdapter (optional injection)
-   **HIGH #2**: Fixed story documentation to reference `interfaces.py` instead of `base_adapter.py`
-   **MEDIUM #3**: Added tenacity retry logic to `generate_script` for transient failures
-   **MEDIUM #4**: Added 2 integration tests (skip in CI) for real API validation
-   **MEDIUM #5**: Added `sprint-status.yaml` to File List
-   **LOW #6**: Test docstrings status update deferred (cosmetic)
-   **LOW #7**: Fixed Python 3.9 compatibility in interfaces.py type hints
