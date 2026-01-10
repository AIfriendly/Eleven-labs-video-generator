# Story 3.2: Custom Image Generation Model Selection

**FR Coverage:** FR3 (Users can select different image generation models for visual content)

Status: done

## Story

As a user,
I want to select different image generation models for visual content,
so that my video images match the style I want.

## Acceptance Criteria

1. **Given** I have access to multiple image generation models, **When** I specify an image model ID via the pipeline, **Then** the Gemini image generator uses my selected model.

2. **Given** I don't specify an image model, **When** image generation runs, **Then** the system uses the default model (`gemini-2.5-flash-image` - current behavior preserved).

3. **Given** I specify an invalid image model ID, **When** image generation runs, **Then** the system falls back to the default model with a warning message.

4. **Given** I want to see available image models, **When** I call the image model listing functionality, **Then** I receive a list of available image models with their IDs and display names.

## Tasks / Subtasks

- [x] Task 1: Add `ImageModelInfo` domain model (AC: #4)
  - [x] 1.1: Create `ImageModelInfo` dataclass in `eleven_video/models/domain.py`
  - [x] 1.2: Include fields: `model_id: str`, `name: str`, `description: Optional[str]`, `supports_image_generation: bool`
  - [x] 1.3: Write unit tests for `ImageModelInfo` model

- [x] Task 2: Add `list_image_models()` method to `GeminiAdapter` (AC: #4)
  - [x] 2.1: Add `list_image_models(use_cache: bool = False) -> list[ImageModelInfo]` method (same pattern as `list_voices`)
  - [x] 2.2: Call Gemini SDK to list available models (filter for image-capable models)
  - [x] 2.3: Map SDK response to `ImageModelInfo` domain models
  - [x] 2.4: Add `_image_model_cache` and `_image_model_cache_ttl` instance variables in `GeminiAdapter.__init__`
  - [x] 2.5: Implement caching logic with 60s TTL (same pattern as `list_voices`)
  - [x] 2.6: Create internal `_list_image_models_with_retry()` method with `@retry` decorator
  - [x] 2.7: Write unit tests with mocked SDK responses
  - [x] 2.8: Write integration test (marked for API key requirement)

- [x] Task 3: Add `ImageModelLister` protocol to interfaces (AC: #4)
  - [x] 3.1: Define `ImageModelLister` protocol in `eleven_video/api/interfaces.py`
  - [x] 3.2: Ensure `GeminiAdapter` implements the protocol
  - [x] 3.3: Write protocol conformance tests

- [x] Task 4: Add image model ID validation and fallback (AC: #3)
  - [x] 4.1: Add `validate_image_model_id(model_id: str) -> bool` method to adapter
  - [x] 4.2: Implement validation using `list_image_models(use_cache=True)` (same pattern as `validate_voice_id`)
  - [x] 4.3: Update `generate_images()` signature to accept `model_id` and `warning_callback` parameters
  - [x] 4.4: Implement fallback logic: invalid model ID → use default + call warning_callback
  - [x] 4.5: Write tests for invalid model ID handling and fallback

- [x] Task 5: Update `generate_images()` to accept model_id parameter (AC: #1, #2)
  - [x] 5.1: Add optional `model_id: Optional[str] = None` parameter to `generate_images()` signature
  - [x] 5.2: Pass `model_id` through to internal `_generate_image_with_retry()` method
  - [x] 5.3: Update `_generate_image_with_retry()` to use `model_id or self.IMAGE_MODEL`
  - [x] 5.4: Write tests validating model ID flows to API call

- [x] Task 6: Update `ImageGenerator` protocol (AC: #1, #3)
  - [x] 6.1: Update `ImageGenerator` protocol signature to include optional `model_id` and `warning_callback` parameters
  - [x] 6.2: Ensure backward compatibility (existing callers work without changes)
  - [x] 6.3: Write protocol conformance tests

## Dev Notes

### Scope Clarification

> ⚠️ **Backend-only story.** This story implements the API-level image model selection. The interactive UI for model selection is handled by **Story 3.4: Interactive Image Model Selection Prompts**.
>
> **Dependency Chain:** Story 3.2 (API) → Story 3.4 (UI) → User can interactively select image models

### Pattern Mirror: Story 3.1

This story **exactly mirrors Story 3.1 (Custom Voice Model Selection)** but for image generation:

| Story 3.1 (Voice) | Story 3.2 (Image) |
|-------------------|-------------------|
| `VoiceInfo` dataclass | `ImageModelInfo` dataclass |
| `list_voices()` method | `list_image_models()` method |
| `VoiceLister` protocol | `ImageModelLister` protocol |
| `validate_voice_id()` | `validate_image_model_id()` |
| `voice_id` parameter in `generate_speech()` | `model_id` parameter in `generate_images()` |
| `warning_callback` for voice fallback | `warning_callback` for model fallback |

**Follow Story 3.1 implementation patterns exactly** - the code structure should be nearly identical.

### Architecture Compliance

**Pattern:** Hexagonal (Ports & Adapters)
- `ImageModelLister` protocol = Port (in `api/interfaces.py`)
- `GeminiAdapter.list_image_models()` = Adapter implementation
- `ImageModelInfo` domain model stays in `models/domain.py`

**Source:** [docs/architecture/core-architectural-decisions.md#Consensus Decisions]

### Existing Code Analysis

**Current `GeminiAdapter` Image Generation (gemini.py lines 266-396):**

```python
class GeminiAdapter:
    IMAGE_MODEL = "gemini-2.5-flash-image"  # Default hardcoded
    STYLE_SUFFIX = ", photorealistic, cinematic composition, 16:9 aspect ratio, high quality"
    
    def generate_images(
        self,
        script: Script,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> List[Image]:
        # Currently uses self.IMAGE_MODEL hardcoded
        ...
    
    def _generate_image_with_retry(self, prompt: str) -> Image:
        response = self._genai_client.models.generate_content(
            model=self.IMAGE_MODEL,  # ← This needs to accept model_id parameter
            contents=prompt
        )
        ...
```

**Key Changes Required:**
1. Add optional `model_id` parameter to `generate_images()` (like `voice_id` in `generate_speech`)
2. Add optional `warning_callback` parameter for fallback warnings
3. Pass `model_id` to `_generate_image_with_retry()` 
4. Use `model_id or self.IMAGE_MODEL` pattern for default fallback
5. Add `list_image_models()` method to fetch available models
6. Add `validate_image_model_id()` method for validation

### Google Gemini SDK Reference

The Google Gemini SDK (google-genai) provides model listing:

```python
from google import genai

client = genai.Client(api_key="...")

# List all models
models = client.models.list()

# Filter for image-capable models
# Models with image generation capability typically have:
# - name pattern like "models/gemini-2.5-flash-image" or similar
# - supported_generation_methods including 'generateContent'

# Example response structure:
# model.name: "models/gemini-2.5-flash-image"
# model.display_name: "Gemini 2.5 Flash Image"
# model.description: "Fast image generation model"
# model.supported_generation_methods: ['generateContent']
```

**SDK Docs:** https://github.com/google-gemini/generative-ai-python

### Known Image-Capable Models (December 2025)

| Model ID | Display Name | Status | Notes |
|----------|--------------|--------|-------|
| `gemini-2.5-flash-image` | Gemini 2.5 Flash Image | ✅ **Current default** | Fast, 1024px, codename "Nano Banana" |
| `gemini-3-pro-image-preview` | Gemini 3 Pro Image | 🆕 Preview (paid) | 4K resolution, 14 reference images |
| `gemini-3-flash` | Gemini 3 Flash | 🆕 Released Dec 17 | Replaces 2.5 Flash, multimodal |
| `imagen-3.0-generate-001` | Imagen 3 | ✅ Available | Highest quality, dedicated image model |

> ⚠️ **Retired:** `gemini-2.0-flash-exp` was retired October 31, 2025 - do not use.

> ⚠️ **Important:** Model availability varies by API key/tier. Always validate models via `list_image_models()` rather than hardcoding lists.

### Testing Requirements

**Test Groups (matching Story 3.1 pattern):**

| Group | Tests | Description |
|-------|-------|-------------|
| TestImageModelInfoModel | 4 | `ImageModelInfo` dataclass tests |
| TestImageModelListerProtocol | 3 | Protocol conformance tests |
| TestListImageModels | 3 | `list_image_models()` method tests |
| TestImageModelIdValidation | 2 | `validate_image_model_id()` tests |
| TestFallbackWithWarning | 2 | Fallback + warning_callback tests |
| TestDefaultModelBehavior | 1 | Default model when none specified |
| TestRetryLogic | 2 | `_list_image_models_with_retry()` tests |
| TestImageModelCaching | 3 | Cache TTL and refresh tests |

**Test file locations:**
- `tests/api/test_gemini_images.py` - Unit tests (new file, ~20 tests)
- `tests/api/test_gemini_integration.py` - Integration test (requires API key)

**Coverage target:** ≥80% for new code

### Risk Mitigation

From [docs/test-design-epic-3.md]:
- **R-001 (Score 6):** Gemini image model API changes
  - **Mitigation:** Validate model exists before use, fallback to default with warning
  
- **R-002 (Score 6):** Gemini model availability varies by API key/tier
  - **Mitigation:** Query available models at runtime, show only available models

### Error Handling Pattern

Reuse existing `_format_error()` pattern from `GeminiAdapter`:
```python
def _format_error(self, error: Exception) -> str:
    # Sanitizes errors, never exposes API key (AC2)
    # Maps HTTP codes to user-friendly messages
```

**Source:** [eleven_video/api/gemini.py#_format_error]

### Previous Story Intelligence (Story 3.1)

**Completion Notes from Story 3.1:**
- Added `VoiceInfo` dataclass to domain models
- Added `VoiceLister` protocol with `@runtime_checkable`
- Added `list_voices()` with retry logic + caching (TTL)
- Added `validate_voice_id()` method checking against cached voice list
- Updated `generate_speech()` with `warning_callback` parameter
- Fixed existing tests that had hardcoded IDs

**Key Pattern: Caching with TTL**
```python
# From Story 3.1 implementation:
_voices_cache: Optional[List[VoiceInfo]] = None
_voices_cache_time: Optional[float] = None
CACHE_TTL_SECONDS = 300  # 5 minutes

def list_voices(self) -> List[VoiceInfo]:
    if self._voices_cache and self._voices_cache_time:
        if time.time() - self._voices_cache_time < self.CACHE_TTL_SECONDS:
            return self._voices_cache
    # Fetch fresh data...
```

**Apply same caching pattern for `list_image_models()`**

### Project Structure Notes

**Files to modify:**
- `eleven_video/models/domain.py` - Add `ImageModelInfo` dataclass
- `eleven_video/api/interfaces.py` - Add `ImageModelLister` protocol, update `ImageGenerator`
- `eleven_video/api/gemini.py` - Add `list_image_models()`, `validate_image_model_id()`, update `generate_images()`

**New files to create:**
- `tests/api/test_gemini_images.py` - Unit tests for Story 3.2

**No orchestrator changes required** - `model_id` parameter can be passed through once Story 3.4 (UI) is implemented.

### References

- [Source: eleven_video/api/gemini.py#generate_images] - Current image generation (lines 273-323)
- [Source: eleven_video/api/gemini.py#_generate_image_with_retry] - Internal retry method to modify (lines 364-396)
- [Source: eleven_video/api/gemini.py#IMAGE_MODEL] - Default model constant (line 270)
- [Source: docs/architecture/core-architectural-decisions.md#Consensus Decisions] - Hexagonal architecture
- [Source: docs/test-design-epic-3.md] - Epic 3 Test Design with risk assessment
- [Source: docs/test-design-epic-3.md#R-001] - Risk mitigation for model API changes
- [Source: docs/test-design-epic-3.md#Test ID Reference] - Test IDs 3.2-UNIT-001, 3.2-UNIT-002
- [Source: docs/sprint-artifacts/epic-3-stories/story-3-1-custom-voice-model-selection.md] - **Story 3.1 implementation to mirror**
- [Source: docs/architecture/project-context.md] - Use `uv run pytest` for testing
- [Source: docs/epics.md#Story 3.2] - Original story requirements

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

Gemini 2.5 Flash (Antigravity Agent)

### Debug Log References

- No debug issues encountered during implementation

### Completion Notes List

- ✅ **Task 1 Complete**: Added `ImageModelInfo` dataclass to `domain.py` with fields: `model_id`, `name`, `description`, `supports_image_generation`
- ✅ **Task 2 Complete**: Added `list_image_models()` method with caching (60s TTL) and retry logic (`_list_image_models_with_retry()` with `@retry` decorator)
- ✅ **Task 3 Complete**: Added `ImageModelLister` protocol with `@runtime_checkable` decorator
- ✅ **Task 4 Complete**: Added `validate_image_model_id()` method using cached model list
- ✅ **Task 5 Complete**: Updated `generate_images()` to accept `model_id` and `warning_callback` parameters, passes through to `_generate_image_with_retry()`
- ✅ **Task 6 Complete**: Updated `ImageGenerator` protocol signature with new optional parameters, ensures backward compatibility
- ✅ **All 22 Tests Passing**: 4 domain model, 3 protocol, 3 list method, 2 validation, 2 fallback, 1 default, 2 retry, 3 cache, 2 protocol update tests

### Implementation Approach

Followed Story 3.1 (Voice Model Selection) patterns exactly:
- Used `time.perf_counter()` for cache timestamps
- Filters models by 'image' or 'imagen' in model name
- Extracts model_id by removing 'models/' prefix
- Returns cached models if TTL not expired

### File List

| File | Action | Description |
|------|--------|-------------|
| `eleven_video/models/domain.py` | MODIFIED | Added `ImageModelInfo` dataclass |
| `eleven_video/api/interfaces.py` | MODIFIED | Added `ImageModelLister` protocol, updated `ImageGenerator` |
| `eleven_video/api/gemini.py` | MODIFIED | Added `list_image_models()`, `validate_image_model_id()`, updated `generate_images()` |
| `tests/api/test_gemini_images.py` | ADDED | 22 unit tests for Story 3.2 |
| `docs/atdd-checklist-story-3-2.md` | ADDED | ATDD checklist document |

### Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-12-18 | Story created by SM agent - comprehensive developer context | Antigravity Agent |
| 2025-12-18 | Quality review: Added use_cache param, internal retry method, cache variables, test coverage table, fixed line refs | Antigravity Agent |
| 2025-12-18 | Implementation complete: All 6 tasks done, 22 tests passing, story marked Ready for Review | Antigravity Agent |
| 2025-12-18 | Code review complete: 22/22 tests passing, all ACs verified, documentation updated, story marked done | Antigravity Agent |

---

## Senior Developer Review (AI)

**Reviewer:** Antigravity Agent
**Date:** 2025-12-18
**Outcome:** ✅ APPROVED

### Verification Results

| Acceptance Criteria | Status | Evidence |
|---------------------|--------|----------|
| AC1: Custom model via pipeline | ✅ PASS | `generate_images()` accepts `model_id` param (gemini.py:359-398) |
| AC2: Default model behavior | ✅ PASS | Uses `IMAGE_MODEL` when `model_id=None` (gemini.py:388) |
| AC3: Invalid model fallback | ✅ PASS | Validates + warns via callback (gemini.py:389-398) |
| AC4: List available models | ✅ PASS | `list_image_models()` returns `ImageModelInfo` list (gemini.py:281-345) |

### Test Coverage

- **Total Tests:** 22
- **Passing:** 22 (100%)
- **Test File:** `tests/api/test_gemini_images.py`

### Issues Found & Resolved

| Severity | Issue | Resolution |
|----------|-------|------------|
| HIGH | Sprint status mismatch (ready-for-dev → done) | Updated sprint-status.yaml |
| HIGH | ATDD checklist showed RED instead of GREEN | Updated all 22 test statuses to GREEN |
| HIGH | Test docstring claimed RED phase | Updated to reflect GREEN phase |
| MEDIUM | Caching TTL (60s vs 300s in Story 3.1) | Kept 60s per story specification |

### Notes

- Implementation correctly mirrors Story 3.1 patterns for consistency
- 60s TTL for image model cache is intentional per story task definition (differs from 300s voice cache for faster model discovery)
- All files in story File List verified against git changes
