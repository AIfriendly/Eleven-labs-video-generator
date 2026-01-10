# ATDD Checklist - Epic 2, Story 2.3.1: Image Generation Reliability & API Compliance

**Date:** 2026-01-05
**Author:** Antigravity (Google DeepMind)
**Primary Test Level:** API

---

## Story Summary

As a user, I want image generation to work reliably with correct API usage and handle errors gracefully, so that video generation succeeds consistently without cryptic API errors or unnecessary failures due to safety filters.

---

## Acceptance Criteria

1.  `generate_content()` includes `response_modalities=["IMAGE"]`
2.  Dynamic model discovery with fallback to `gemini-2.5-flash-image`
3.  Defensive response parsing (check `finish_reason` and candidates)
4.  Retry safety-blocked content with modified prompt (max 2 retries)
5.  Default to `gemini-2.5-flash-image` for free tier optimization
6.  `list_image_models()` filters compatible models

---

## Failing Tests Created (RED Phase)

### API Tests

**File:** `tests/api/test_gemini_reliability.py`

- ✅ **Test:** `test_safety_filter_handling_retries_with_safe_prompt`
  - **Status:** RED - Retry logic not implemented
  - **Verifies:** Logic detects `SAFETY` finish reason and retries with modified suffix.

- ✅ **Test:** `test_safety_filter_fails_after_max_retries`
  - **Status:** RED - Retry logic not implemented
  - **Verifies:** Stops retrying after 2 attempts and raises appropriate error.

- ✅ **Test:** `test_defensive_parsing_raises_clear_error_on_empty`
  - **Status:** RED - Error message might differ or crash
  - **Verifies:** Raises `GeminiAPIError` with clear message when content is empty.

- ✅ **Test:** `test_defensive_parsing_checks_finish_reason`
  - **Status:** RED - Logic not implemented
  - **Verifies:** Checks `finish_reason` before accessing content.

- ✅ **Test:** `test_dynamic_model_discovery_prioritizes_gemini_image`
  - **Status:** RED - Logic likely missing helper method
  - **Verifies:** `_resolve_default_image_model` logic chain.

---

## Mock Requirements

### Google GenAI SDK

**Endpoint:** `models.generate_content`

**Blocked Response (Safety):**
```python
candidate.finish_reason = "SAFETY"
candidate.content = None
```

**Empty Response:**
```python
candidate.finish_reason = "STOP"
candidate.content.parts = []
```

---

## Required data-testid Attributes

*N/A - API Story*

---

## Implementation Checklist

### Test: Safety Filter Retry Logic

**File:** `eleven_video/api/gemini.py`

**Tasks:**
- [x] Implement `_resolve_default_image_model()` helper method
- [x] Add `finish_reason` check in `_generate_image_with_retry`
- [x] Implement retry loop with prompt modification in `generate_images`
- [x] Ensure specific `GeminiAPIError` raises for blocked content
- [x] Run test: `uv run pytest tests/api/test_gemini_reliability.py`
- [x] ✅ Test passes (green phase)

**Estimated Effort:** 2 hours

---

## Red-Green-Refactor Workflow

### RED Phase (Complete) ✅

**TEA Agent Responsibilities:**
- ✅ All tests written and failing
- ✅ Mock requirements documented
- ✅ Implementation checklist created

### GREEN Phase (DEV Team - Next Steps)

1.  **Pick one failing test**
2.  **Implement minimal code**
3.  **Run the test**
4.  **Repeat**

---

## Running Tests

```bash
# Run reliability tests
uv run pytest tests/api/test_gemini_reliability.py

# Run all API tests (regression check)
uv run pytest tests/api/
```
