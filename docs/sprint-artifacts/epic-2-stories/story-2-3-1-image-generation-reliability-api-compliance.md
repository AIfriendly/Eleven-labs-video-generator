# Story 2.3.1: Image Generation Reliability & API Compliance

Status: done

## 1. Story

**As a** user,
**I want** image generation to work reliably with correct API usage and handle errors gracefully,
**so that** video generation succeeds consistently without cryptic API errors or unnecessary failures due to safety filters.

## 2. Acceptance Criteria

1.  **Given** the system calls the Gemini Image API,
    **When** `generate_content()` is called,
    **Then** the `response_modalities=["IMAGE"]` configuration is explicitly included in the request to ensure image output.

2.  **Given** a model ID is not specified by the user,
    **When** selecting a default image model,
    **Then** the system queries available models dynamically and selects the first valid Gemini image model (e.g., `gemini-2.5-flash-image`),
    **And** falls back to the hardcoded `gemini-2.5-flash-image` if dynamic discovery fails.

3.  **Given** the API returns an empty response or strictly safety-blocked content,
    **When** parsing the response from the SDK,
    **Then** the system checks `response.candidates[0].finish_reason` for safety blocks AND defensively checks for `candidates[0].content`,
    **And** raises a specific, user-friendly error message if blocked or empty, instead of crashing.

4.  **Given** content is blocked by safety filters (detected via empty response or block reason),
    **When** the first attempt fails,
    **Then** the system automatically retries up to 2 times with a modified prompt (appending ", safe for work, educational" suffix) to attempt to bypass false positives.

5.  **Given** I am using the free tier,
    **When** generating images,
    **Then** the default model preference prioritizes `gemini-2.5-flash-image` (500/day free limit) over other models to maximize free usage.

6.  **Given** the `list_image_models()` method,
    **When** querying for models,
    **Then** it filters *out* models that do not support the `generate_content` method with image modality (e.g., legacy Imagen models requiring different API calls), ensuring only compatible models are returned.

## 3. Tasks / Subtasks

- [ ] **Task 1: Defensive Response Parsing** (AC3)
    - [ ] Modify `_generate_image_with_retry` in `eleven_video/api/gemini.py`.
    - [ ] Check `response.candidates[0].finish_reason` for `SAFETY` or `BLOCK` status.
    - [ ] Add checks for `response.candidates[0].content` before access.
    - [ ] Raise specific `GeminiAPIError` for "Image generation blocked or empty response".
- [ ] **Task 2: Safety Filter Retry Logic** (AC4)
    - [ ] Implement a retry loop *inside* `generate_images` or a wrapper around the API call.
    - [ ] Detect "blocked" or "empty" errors.
    - [ ] On failure, modify prompt with safe suffix (`", safe for work, educational"`) and retry.
    - [ ] Limit to 2 retries (3 attempts total).
- [ ] **Task 3: Dynamic Model Discovery** (AC2, AC6)
    - [ ] Update `list_image_models` to strictly filter for Gemini Image models (check capabilities/name).
    - [ ] Implement `_resolve_default_image_model()` helper to encapsulate logic: `User Config` > `CLI Flag` > `Dynamic List[0]` > `Hardcoded Fallback`.
- [ ] **Task 4: Update API Configuration** (AC1)
    - [ ] Verify `response_modalities=["IMAGE"]` is correctly set in `types.GenerateContentConfig` (already present, verify correctness).
- [ ] **Task 5: Testing**
    - [ ] Create `tests/api/test_gemini_reliability.py`.
    - [ ] Test empty response handling (mock empty candidates).
    - [ ] Test retry logic (fail 1st, succeed 2nd with suffix).
    - [ ] Test dynamic model fallback chain.

## 4. Developer Context

### Architecture & Compliance

-   **ADR Reference:** This story implements **ADR-005: Gemini Image Generation API Architecture**.
-   **SDK:** Uses `google-genai` SDK.
    -   Import: `from google import genai`
    -   Types: `from google.genai import types` for `GenerateContentConfig`.
-   **Security:** Continue to use `Settings` for API keys.
-   **Reliability:** The retry logic for safety filters is *distinct* from the connection error retries handled by `tenacity`. This is a *logic* retry, not a *network* retry.

### Technical Implementation Details

**Response Parsing & Safety Checks (Defensive):**
```python
# Check finish reason explicitly first
candidate = response.candidates[0]
if candidate.finish_reason in ["SAFETY", "BLOCK", "RECITATION"]:
     raise GeminiAPIError(f"Image generation blocked: {candidate.finish_reason}")

# Then check content existence
if not candidate.content or not candidate.content.parts:
    raise GeminiAPIError("Empty content returned (Safety Block?)")

# ... safe to access parts[0]
return candidate.content.parts[0]
```

**Safety Retry Logic:**
The API often flags benign prompts. A common fix is appending "educational" or "safe for work".
```python
RETRIES = 2
for attempt in range(RETRIES + 1):
    try:
        return _generate_api_call(current_prompt)
    except GeminiAPIError as e:
        if "blocked" in str(e) or "empty" in str(e):
            if attempt < RETRIES:
                current_prompt += ", safe for work, educational"
                continue
        raise
```

**Free Tier Limits:**
-   `gemini-2.5-flash-image`: 500 images/day (Free) vs $0.039/image (Paid).
-   `imagen-3.0`: Lower limits, often paid only.
-   **Constraint:** Prioritize `gemini-2.5-flash-image` as default.

### Project Structure Notes

-   **Target File:** `eleven_video/api/gemini.py`
-   **Tests:** Add new test file `tests/api/test_gemini_reliability.py` to separate these edge case tests from main functionality tests.

### References

-   [Source: docs/architecture/architecture-decision-records.md#adr-005-gemini-image-generation-api-architecture]
-   [Source: docs/epics.md#story-231-image-generation-reliability--api-compliance]

## 5. Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

Antigravity (Google DeepMind)

### Debug Log References

-   Previous issues with `NoneType` on `response.candidates[0].content`.

### Completion Notes List

### File List

- `eleven_video/api/gemini.py`
- `tests/api/test_gemini_reliability.py`
