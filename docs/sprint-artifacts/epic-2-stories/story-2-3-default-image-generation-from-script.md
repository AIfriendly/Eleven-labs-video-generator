# Story 2.3: Default Image Generation from Script

Status: done

## 1. Story

**As a** user,
**I want** the system to automatically generate matching images from the script using Google Gemini Nano Banana (`gemini-2.5-flash-image`),
**so that** I have visual content for my video without needing to create images manually.

## 2. Acceptance Criteria

1.  **Given** I have a generated script from Story 2.1,
    **When** the image generation process runs,
    **Then** images are generated based on thematic keywords extracted from the script sentences using Gemini Nano Banana (`gemini-2.5-flash-image`),
    **And** the images are of a consistent and appropriate style.

2.  **Given** the image generation process requires the Google Gemini API,
    **When** the system connects to the API,
    **Then** it successfully authenticates using the configured API key from the Settings class,
    **And** the API key is never exposed in logs, terminal output, or error messages.

3.  **Given** images are being generated,
    **When** the process is active,
    **Then** the user sees a progress indicator in the terminal (FR23),
    **And** progress updates for each image being generated.

4.  **Given** I provide an empty or invalid script,
    **When** the generation is attempted,
    **Then** a clear, actionable error message is displayed without exposing internal details.

5.  **Given** the Gemini API returns an error (401 Unauthorized, 429 Rate Limited, 500 Server Error, or timeout),
    **When** the error is detected,
    **Then** the system displays a user-friendly error message indicating the issue type,
    **And** suggests corrective action where applicable.

6.  **Given** the generated images,
    **When** the image generation completes,
    **Then** the images are returned as a list of Image domain models,
    **And** each image has metadata (file_size_bytes, mime_type) for downstream video compilation.

7.  **Given** a script with multiple sentences or segments,
    **When** images are generated,
    **Then** an appropriate number of images are generated to match the script content (typically one image per major sentence/paragraph).

## 3. Developer Context

### Technical Requirements

-   **Primary Goal:** Migrate `GeminiAdapter` to use `google-genai` SDK and add image generation via `generate_images()` method.
-   **SDK Migration:** Replace `google-generativeai` with `google-genai` (unified SDK for text + image generation).
-   **Interface Contract:** Implement the `ImageGenerator` protocol in `eleven_video/api/interfaces.py` with signature `generate_images(script: Script, progress_callback: Optional[Callable] = None) -> List[Image]`.
-   **Authentication:** Use the existing `Settings` class from `eleven_video/config/settings.py` to retrieve the `GEMINI_API_KEY`.
-   **Security:** API keys must never be logged, displayed in terminal output, or included in error messages.
-   **Output Format:** Generate images in PNG format, targeting **16:9 aspect ratio (1920x1080)** for YouTube compatibility (FR13).
-   **Style Consistency:** Append style suffix to all prompts: `", photorealistic, cinematic composition, 16:9 aspect ratio, high quality"`

> [!CAUTION]
> **SDK Migration Required:** This story requires migrating from `google-generativeai` (deprecated Aug 2025) to `google-genai`. This affects the existing `generate_script()` method in Story 2.1.
> 
> | Aspect | Old SDK (`google-generativeai`) | New SDK (`google-genai`) |
> |--------|--------------------------------|--------------------------|
> | Import | `import google.generativeai as genai` | `from google import genai` |
> | Client | `genai.configure()` + `genai.GenerativeModel()` | `genai.Client(api_key=...)` |
> | Call | `model.generate_content(prompt)` | `client.models.generate_content(model=..., contents=...)` |

> [!IMPORTANT]
> **Hybrid Adapter Pattern Preserved:** After migration, `GeminiAdapter` will use:
> - **httpx** for health checks (`check_health()`) and usage queries (`get_usage()`)
> - **google-genai SDK** for all content generation (`generate_script()`, `generate_images()`)

### Architectural Compliance

-   **Hexagonal Architecture:** The Gemini adapter belongs in the infrastructure layer (`eleven_video/api/`).
-   **Separation of Concerns:**
    - `eleven_video/api/gemini.py` — API adapter (infrastructure)
    - `eleven_video/api/interfaces.py` — Protocol definitions (port)
    - `eleven_video/models/domain.py` — Image domain model
-   **Configuration:** Use dependency injection for Settings instance.
-   **Retry Logic:** Use `tenacity` with exponential backoff for transient failures.

### Library & Framework Requirements

-   **SDK:** `google-genai>=0.5.0` — **Replaces** `google-generativeai` (remove from pyproject.toml)
-   **Dependencies:** Update `pyproject.toml`:
    ```diff
    - "google-generativeai>=0.8.0",
    + "google-genai>=0.5.0",
    ```

### File & Code Structure

| File | Purpose |
|------|---------|
| `eleven_video/api/gemini.py` | [MODIFY] Migrate SDK + add `generate_images()` |
| `eleven_video/api/interfaces.py` | [MODIFY] Add `ImageGenerator` protocol |
| `eleven_video/models/domain.py` | [MODIFY] Add `Image` domain model |
| `pyproject.toml` | [MODIFY] Replace `google-generativeai` with `google-genai` |
| `tests/api/test_gemini.py` | [MODIFY] Update mocks for new SDK |
| `tests/api/test_gemini_images.py` | [NEW] Unit tests for image generation |

### API Reference

**Model:** `gemini-2.5-flash-image` (Nano Banana)

**SDK Usage (New `google-genai`):**
```python
from google import genai

# Initialize client
client = genai.Client(api_key=settings.gemini_api_key.get_secret_value())

# Generate image
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents="Sunrise over mountains, photorealistic, cinematic, 16:9 aspect ratio"
)

# Extract image data from response
for part in response.candidates[0].content.parts:
    if hasattr(part, 'inline_data'):
        image_bytes = part.inline_data.data  # Binary image data
        mime_type = part.inline_data.mime_type  # e.g., "image/png"
```

**Text Generation (Migrated):**
```python
# Before (old SDK):
# genai.configure(api_key=key)
# model = genai.GenerativeModel("gemini-2.5-flash")
# response = model.generate_content(prompt)

# After (new SDK):
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)
script_text = response.candidates[0].content.parts[0].text
```

### Script Segmentation Strategy

1. Split script into paragraphs or major sentences
2. For each segment, extract key visual themes
3. Generate scene description prompt with style suffix
4. Call image generation API for each prompt
5. Return list of Image objects with metadata

**Style Suffix (append to all prompts):**
```
", photorealistic, cinematic composition, 16:9 aspect ratio, high quality"
```

### Testing Requirements

| Test Category | Test Cases |
|---------------|------------|
| **Success** | Valid script → generates images; Multi-segment → multiple images |
| **Validation** | Empty script → ValidationError; Whitespace-only → ValidationError |
| **Errors** | 401 → "Check GEMINI_API_KEY"; 429 → "Rate limit"; 500 → "Server error" |
| **Security** | API key never in error messages |
| **Edge Cases** | Unicode/emojis in script; Very long script content |
| **Progress** | Callback invoked per image; Format "Generating image X of Y" |
| **SDK Migration** | Verify `generate_script()` still works after migration |

### Previous Story Intelligence

**From Story 2.1 & 2.2:**
-   Settings class injection pattern
-   `@retry` decorator with `stop_after_attempt(3)`, `wait_exponential`
-   `_format_error()` for user-friendly messages
-   Progress callback pattern
-   Python 3.9 compatible type hints (`Optional[X]` not `X | Y`)
-   Mock patch paths use module path, not import path

### Project Context Reference

-   **PRD:** `docs/prd.md` — FR7, FR13 (16:9 aspect ratio), FR35.1
-   **Epics:** `docs/epics.md` — Epic 2, Story 2.3
-   **Architecture:** `docs/architecture/core-architectural-decisions.md`

## 4. Tasks

- [x] **Task 1:** SDK Migration Preparation
  - [x] Update `pyproject.toml`: replace `google-generativeai` with `google-genai>=1.0.0`
  - [x] Run `uv pip install` to update dependencies (installed `google-genai==1.55.0`)
- [x] **Task 2:** Migrate `generate_script()` to new SDK
  - [x] Refactor `GeminiAdapter.__init__` to use `genai.Client`
  - [x] Update `generate_script()` to use new API pattern (`client.models.generate_content`)
  - [x] Verify existing tests pass after migration (17/18 pass, 1 integration test skipped)
- [x] **Task 3:** Create `Image` domain model in `eleven_video/models/domain.py`
  - [x] Dataclass with `data: bytes`, `mime_type: str`, `file_size_bytes: Optional[int]`
- [x] **Task 4:** Add `ImageGenerator` protocol to `eleven_video/api/interfaces.py`
- [x] **Task 5:** Implement script segmentation utility
  - [x] Split script into segments (paragraphs or sentences) via `_segment_script()`
  - [x] Generate image prompts with style suffix
- [x] **Task 6:** Implement `GeminiAdapter.generate_images()` method
  - [x] Image generation using `gemini-2.5-flash-image`
  - [x] Response parsing to extract image bytes + mime_type via `_generate_image_with_retry()`
  - [x] Progress callback support with "Generating image X of Y" format
- [x] **Task 7:** Implement error handling and retry logic
  - [x] Validate script non-empty before API call (raises `ValidationError`)
  - [x] Tenacity retry decorator for transient failures
  - [x] Reuse `_format_error()` pattern for user-friendly messages
- [x] **Task 8:** Write unit tests in `tests/api/test_gemini_images.py` (23 tests)
- [x] **Task 9:** Update `tests/api/test_gemini.py` for SDK migration (updated fixtures and assertions)
- [x] **Task 10:** Write integration test (skip in CI) - marked @pytest.mark.integration

## 5. Dev Notes

### Architecture Patterns

- Hexagonal architecture with ports/adapters pattern
- Settings class dependency injection for API key security
- Implement against `ImageGenerator` protocol interface
- Reuse `_format_error()` pattern from existing adapter

### Project Structure

| Path | Purpose |
|------|---------|
| `eleven_video/api/gemini.py` | Migrate SDK + add `generate_images()` |
| `eleven_video/api/interfaces.py` | Add `ImageGenerator` protocol |
| `eleven_video/models/domain.py` | Add `Image` dataclass |
| `tests/api/test_gemini_images.py` | New test file |

### References

- [Source: docs/prd.md#FR7-FR13-FR35.1]
- [Source: docs/architecture/core-architectural-decisions.md]
- [Source: docs/sprint-artifacts/story-2-1-default-script-generation-from-prompt.md]
- [Source: docs/sprint-artifacts/story-2-2-default-text-to-speech-generation.md]

## 6. Dev Agent Record

### Agent Model Used

Amelia (Developer Agent) - Claude

### Completion Notes List

- ✅ SDK migrated from `google-generativeai` to `google-genai==1.55.0`
- ✅ `GeminiAdapter` now uses `genai.Client(api_key=...)` pattern
- ✅ `generate_script()` continues to work post-migration
- ✅ `Image` domain model added to `eleven_video/models/domain.py`
- ✅ `ImageGenerator` protocol added to `eleven_video/api/interfaces.py`
- ✅ `generate_images()` implemented with script segmentation, style suffix, progress callbacks
- ✅ Using `gemini-2.5-flash-image` model for image generation (Nano Banana)
- ✅ Style suffix appended: ", photorealistic, cinematic composition, 16:9 aspect ratio, high quality"
- ✅ Retry logic via `@retry` decorator with exponential backoff
- ✅ Error handling reuses `_format_error()` for user-friendly messages
- ✅ 42/43 tests pass (24 image tests + 18 script tests, 1 integration skipped)

### File List

| File | Change |
|------|--------|
| `pyproject.toml` | MODIFIED - replaced `google-generativeai` with `google-genai>=1.0.0` |
| `eleven_video/api/gemini.py` | MODIFIED - SDK migration + `generate_images()` implementation |
| `eleven_video/api/interfaces.py` | MODIFIED - added `ImageGenerator` protocol |
| `eleven_video/models/domain.py` | MODIFIED - added `Image` dataclass |
| `tests/api/conftest.py` | MODIFIED - updated fixtures for new SDK |
| `tests/api/test_gemini_script.py` | MODIFIED - updated mocks and assertions for new SDK |
| `tests/api/test_gemini_images.py` | NEW - 24 tests for image generation |
| `docs/atdd-checklist-2-3.md` | NEW - ATDD checklist |

