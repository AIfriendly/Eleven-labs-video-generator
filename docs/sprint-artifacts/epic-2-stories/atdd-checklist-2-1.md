# ATDD Checklist - Story 2.1: Default Script Generation from Prompt

**Date:** 2025-12-15
**Author:** Murat (TEA Agent)
**Primary Test Level:** Unit + API Adapter
**Story Status:** ready-for-dev

---

## Story Summary

**As a** user,
**I want** the system to automatically generate a script from my text prompt using Google Gemini,
**So that** I don't need to write a script manually.

---

## Acceptance Criteria

1. **AC1:** Coherent script generated from valid prompt
2. **AC2:** API authentication via Settings class, key never exposed
3. **AC3:** Progress indicator during generation (FR23)
4. **AC4:** Clear error for empty/invalid prompts
5. **AC5:** User-friendly errors for API failures (401, 429, 500, timeout)

---

## Failing Tests Created (RED Phase)

### Unit Tests (17 tests)

**File:** `tests/api/test_gemini.py` (~600 lines total, ~460 new)

| Test ID | Test Name | AC | Status | Failure Reason |
|---------|-----------|-----|--------|----------------|
| 2.1-UNIT-001 | `test_generate_script_returns_coherent_content` | 1 | 🔴 RED | `generate_script` not implemented |
| 2.1-UNIT-002 | `test_generate_script_uses_default_model` | 1 | 🔴 RED | `generate_script` not implemented |
| 2.1-UNIT-003 | `test_generate_script_returns_script_model` | 1 | 🔴 RED | `Script` model not implemented |
| 2.1-UNIT-004 | `test_api_key_never_in_logs` | 2 | 🔴 RED | `generate_script` not implemented |
| 2.1-UNIT-005 | `test_api_key_never_in_error_messages` | 2 | 🔴 RED | `GeminiAPIError` not implemented |
| 2.1-UNIT-006 | `test_progress_callback_called_during_generation` | 3 | 🔴 RED | Progress callback not implemented |
| 2.1-UNIT-007 | `test_empty_prompt_raises_validation_error` | 4 | 🔴 RED | `ValidationError` not implemented |
| 2.1-UNIT-008 | `test_whitespace_only_prompt_raises_error` | 4 | 🔴 RED | Validation not implemented |
| 2.1-UNIT-009 | `test_none_prompt_raises_error` | 4 | 🔴 RED | Validation not implemented |
| 2.1-UNIT-010 | `test_auth_error_shows_user_friendly_message` | 5 | 🔴 RED | Error handling not implemented |
| 2.1-UNIT-011 | `test_rate_limit_error_suggests_retry` | 5 | 🔴 RED | Error handling not implemented |
| 2.1-UNIT-012 | `test_server_error_shows_retry_message` | 5 | 🔴 RED | Error handling not implemented |
| 2.1-UNIT-013 | `test_timeout_error_shows_timeout_message` | 5 | 🔴 RED | Error handling not implemented |
| 2.1-UNIT-014 | `test_gemini_adapter_has_generate_script_method` | - | 🔴 RED | Method not implemented |
| 2.1-UNIT-015 | `test_script_model_exists` | - | 🔴 RED | `Script` model not created |
| 2.1-UNIT-016 | `test_script_model_has_content_attribute` | - | 🔴 RED | `Script` model not created |
| 2.1-UNIT-017 | `test_gemini_api_error_exists` | - | 🔴 RED | `GeminiAPIError` not created |

---

## Required New Files

| File | Purpose |
|------|---------|
| `eleven_video/models/domain.py` | [NEW] `Script` dataclass with `content` attribute |
| `eleven_video/api/base_adapter.py` | [MODIFY] Add `ScriptGenerator` protocol |

---

## Required Code Changes

### 1. Domain Model (`eleven_video/models/domain.py`)

```python
from dataclasses import dataclass

@dataclass
class Script:
    """Generated video script from Gemini API."""
    content: str
```

### 2. Exception (`eleven_video/exceptions/custom_errors.py`)

```python
class GeminiAPIError(Exception):
    """Error from Gemini API with user-friendly message."""
    pass

class ValidationError(Exception):
    """Input validation error."""
    pass
```

### 3. GeminiAdapter Extension (`eleven_video/api/gemini.py`)

```python
from eleven_video.models.domain import Script
from eleven_video.exceptions.custom_errors import GeminiAPIError, ValidationError
from typing import Callable, Optional
import google.generativeai as genai

class GeminiAdapter:
    def generate_script(
        self, 
        prompt: str, 
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Script:
        """Generate video script from prompt using Gemini API."""
        # 1. Validate prompt (AC4)
        if not prompt or not prompt.strip():
            raise ValidationError("Prompt cannot be empty")
        
        # 2. Progress callback (AC3)
        if progress_callback:
            progress_callback("Generating script...")
        
        # 3. Call Gemini API
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            return Script(content=response.text)
        except Exception as e:
            # 4. Error handling (AC5)
            raise GeminiAPIError(self._format_error(e))
    
    def _format_error(self, error: Exception) -> str:
        """Format error message without exposing API key (AC2)."""
        msg = str(error).lower()
        if "401" in msg or "unauthorized" in msg:
            return "Authentication failed. Please check your GEMINI_API_KEY."
        elif "429" in msg or "rate limit" in msg:
            return "Rate limit exceeded. Please retry after a few minutes."
        elif "500" in msg or "server" in msg:
            return "Gemini server error. Please try again later."
        elif "timeout" in msg:
            return "Request timed out. Please check your connection."
        else:
            return f"Gemini API error: {str(error)}"
```

---

## Implementation Checklist

### Task 1: Create Domain Models (AC: 1)

- [ ] Create `eleven_video/models/` directory if not exists
- [ ] Create `eleven_video/models/__init__.py`
- [ ] Create `eleven_video/models/domain.py` with `Script` dataclass
- [ ] Run: `uv run pytest tests/api/test_gemini.py::TestScriptDomainModel -v`
- [ ] ✅ Tests 2.1-UNIT-015, 016 pass

### Task 2: Create Exception Classes (AC: 4, 5)

- [ ] Add `GeminiAPIError` to `eleven_video/exceptions/custom_errors.py`
- [ ] Add `ValidationError` to `eleven_video/exceptions/custom_errors.py`
- [ ] Run: `uv run pytest tests/api/test_gemini.py::TestGeminiAPIErrorExists -v`
- [ ] ✅ Test 2.1-UNIT-017 passes

### Task 3: Implement generate_script Method (AC: 1, 2, 3, 4, 5)

- [ ] Add `google-generativeai` to `pyproject.toml`
- [ ] Implement `generate_script()` in `GeminiAdapter`
- [ ] Add prompt validation (empty, whitespace, None)
- [ ] Add progress callback support
- [ ] Add error handling with user-friendly messages
- [ ] Ensure API key never in logs or error messages
- [ ] Run: `uv run pytest tests/api/test_gemini.py -k "2.1-UNIT" -v`
- [ ] ✅ All 17 Story 2.1 tests pass

---

## Running Tests

```bash
# Run all Story 2.1 failing tests
uv run pytest tests/api/test_gemini.py -k "2.1-UNIT" -v

# Run specific test class
uv run pytest tests/api/test_gemini.py::TestScriptGenerationSuccess -v

# Run with coverage
uv run pytest tests/api/test_gemini.py --cov=eleven_video --cov-report=term-missing

# Run full test suite (regression)
uv run pytest -v
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete) ✅

- ✅ 17 tests written and failing
- ✅ Tests cover all 5 Acceptance Criteria
- ✅ Security constraint (AC2) explicitly tested
- ✅ Given-When-Then format for all tests

### GREEN Phase (DEV Team - Next Steps)

1. **Start with domain model** (Task 1)
2. **Add exception classes** (Task 2)
3. **Implement generate_script method** (Task 3)
4. Run tests after each change

**Key Principle:** One test at a time. Minimal implementation. Run tests frequently.

### REFACTOR Phase (After All Tests Pass)

1. Extract prompt validation to helper
2. Add structured script parsing (Scene/Narration)
3. Update story status to `review` in `sprint-status.yaml`

---

## Notes

- Uses `google-generativeai` SDK (NOT httpx/requests)
- Uses existing `Settings` class for API key (NOT os.getenv)
- Default model: `gemini-2.5-flash`
- Progress callback is optional parameter
- API key must never appear in logs or error messages

---

**Generated by BMad TEA Agent** - 2025-12-15
