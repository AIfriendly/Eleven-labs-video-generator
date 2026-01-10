# ATDD Checklist - Epic 3, Story 3.2: Custom Image Generation Model Selection

**Date:** 2025-12-18
**Author:** Revenant
**Primary Test Level:** Unit (API integration tests marked for API key)

---

## Story Summary

Enable users to select different image generation models for visual content, allowing customization of video image styles. Users can specify an image model ID via the pipeline, and the Gemini image generator will use that selection, with fallback to the default model when needed.

**As a** user,
**I want** to select different image generation models for visual content,
**So that** my video images match the style I want.

---

## Acceptance Criteria

1. **Given** I have access to multiple image generation models, **When** I specify an image model ID via the pipeline, **Then** the Gemini image generator uses my selected model.

2. **Given** I don't specify an image model, **When** image generation runs, **Then** the system uses the default model (`gemini-2.5-flash-image`).

3. **Given** I specify an invalid image model ID, **When** image generation runs, **Then** the system falls back to the default model with a warning message.

4. **Given** I want to see available image models, **When** I call the image model listing functionality, **Then** I receive a list of available image models with their IDs and display names.

---

## Passing Tests (GREEN Phase Complete)

### Unit Tests (22 tests)

**File:** [`tests/api/test_gemini_images.py`](file:///d:/Eleven-labs-AI-Video/tests/api/test_gemini_images.py) (~460 lines)

#### Test Group 1: ImageModelInfo Domain Model (4 tests)

| Test ID | Test Name | Status | Verifies |
|---------|-----------|--------|----------|
| 3.2-UNIT-001 | `test_imagemodelinfo_can_be_imported` | 🟢 GREEN | `ImageModelInfo` is importable |
| 3.2-UNIT-002 | `test_imagemodelinfo_has_required_fields` | 🟢 GREEN | Fields: `model_id`, `name`, `description`, `supports_image_generation` |
| 3.2-UNIT-003 | `test_imagemodelinfo_description_is_optional` | 🟢 GREEN | Optional `description` field defaults to None |
| 3.2-UNIT-004 | `test_imagemodelinfo_is_dataclass` | 🟢 GREEN | Decorated with `@dataclass` |

#### Test Group 2: ImageModelLister Protocol (3 tests)

| Test ID | Test Name | Status | Verifies |
|---------|-----------|--------|----------|
| 3.2-UNIT-005 | `test_imagemodellister_protocol_can_be_imported` | 🟢 GREEN | `ImageModelLister` is importable |
| 3.2-UNIT-006 | `test_imagemodellister_is_runtime_checkable` | 🟢 GREEN | `@runtime_checkable` decorator |
| 3.2-UNIT-007 | `test_gemini_adapter_implements_imagemodellister` | 🟢 GREEN | `GeminiAdapter` has `list_image_models` |

#### Test Group 3: list_image_models() Method (3 tests)

| Test ID | Test Name | Status | Verifies |
|---------|-----------|--------|----------|
| 3.2-UNIT-008 | `test_list_image_models_returns_list_of_imagemodelinfo` | 🟢 GREEN | Returns `list[ImageModelInfo]` |
| 3.2-UNIT-009 | `test_list_image_models_filters_image_capable_only` | 🟢 GREEN | Filters to image-capable models |
| 3.2-UNIT-010 | `test_list_image_models_handles_empty_response` | 🟢 GREEN | Returns `[]` when no models |

#### Test Group 4: Image Model ID Validation (2 tests)

| Test ID | Test Name | Status | Verifies |
|---------|-----------|--------|----------|
| 3.2-UNIT-011 | `test_validate_image_model_id_returns_true_for_valid_id` | 🟢 GREEN | Valid model ID → `True` |
| 3.2-UNIT-012 | `test_validate_image_model_id_returns_false_for_invalid_id` | 🟢 GREEN | Invalid model ID → `False` |

#### Test Group 5: Fallback With Warning (2 tests)

| Test ID | Test Name | Status | Verifies |
|---------|-----------|--------|----------|
| 3.2-UNIT-013 | `test_generate_images_falls_back_with_warning_on_invalid_model` | 🟢 GREEN | AC3: Fallback + warning_callback |
| 3.2-UNIT-014 | `test_generate_images_no_warning_for_valid_model` | 🟢 GREEN | No warning for valid model |

#### Test Group 6: Default Model Behavior (1 test)

| Test ID | Test Name | Status | Verifies |
|---------|-----------|--------|----------|
| 3.2-UNIT-015 | `test_generate_images_uses_default_when_no_model_specified` | 🟢 GREEN | AC2: Default model behavior |

#### Test Group 7: Retry Logic (2 tests)

| Test ID | Test Name | Status | Verifies |
|---------|-----------|--------|----------|
| 3.2-UNIT-016 | `test_list_image_models_retries_on_connection_error` | 🟢 GREEN | Retry on network errors |
| 3.2-UNIT-017 | `test_list_image_models_has_retry_decorator` | 🟢 GREEN | `@retry` decorator present |

#### Test Group 8: Image Model Caching (3 tests)

| Test ID | Test Name | Status | Verifies |
|---------|-----------|--------|----------|
| 3.2-UNIT-018 | `test_list_image_models_uses_cache_when_enabled` | 🟢 GREEN | `use_cache=True` returns cached |
| 3.2-UNIT-019 | `test_list_image_models_ignores_cache_when_disabled` | 🟢 GREEN | `use_cache=False` fetches fresh |
| 3.2-UNIT-020 | `test_list_image_models_refreshes_expired_cache` | 🟢 GREEN | 60s TTL cache expiry |

#### Test Group 9: Protocol Update (2 tests)

| Test ID | Test Name | Status | Verifies |
|---------|-----------|--------|----------|
| 3.2-UNIT-021 | `test_image_generator_protocol_accepts_model_id` | 🟢 GREEN | `model_id` parameter in signature |
| 3.2-UNIT-022 | `test_image_generator_protocol_accepts_warning_callback` | 🟢 GREEN | `warning_callback` parameter |

---

## Data Factories Created

### ImageModelInfo Factory

**File:** [`tests/api/test_gemini_images.py`](file:///d:/Eleven-labs-AI-Video/tests/api/test_gemini_images.py) (lines 448-460)

**Exports:**

- `create_image_model_info(overrides?)` - Create single `ImageModelInfo` with defaults
- `create_mock_gemini_model(overrides?)` - Create mock SDK model object

**Example Usage:**

```python
model_info = create_image_model_info(model_id="custom-model")
mock_sdk = create_mock_gemini_model(display_name="Custom Model")
```

---

## Mock Requirements

### Gemini SDK Models Mock

**Endpoint:** `client.models.list()`

**Success Response Mock:**
```python
mock_model = MagicMock()
mock_model.name = "models/gemini-2.5-flash-image"
mock_model.display_name = "Gemini 2.5 Flash Image"
mock_model.description = "Fast image generation"
mock_model.supported_generation_methods = ["generateContent"]
```

**Notes:** 
- Filter models by checking for "image" in name or `supported_generation_methods`
- Use `@patch.object(adapter, '_genai_client')` for mocking

---

## Required Changes Summary

### Files to Modify

| File | Changes |
|------|---------|
| [`eleven_video/models/domain.py`](file:///d:/Eleven-labs-AI-Video/eleven_video/models/domain.py) | Add `ImageModelInfo` dataclass |
| [`eleven_video/api/interfaces.py`](file:///d:/Eleven-labs-AI-Video/eleven_video/api/interfaces.py) | Add `ImageModelLister` protocol, update `ImageGenerator` |
| [`eleven_video/api/gemini.py`](file:///d:/Eleven-labs-AI-Video/eleven_video/api/gemini.py) | Add `list_image_models()`, `validate_image_model_id()`, update `generate_images()` |

---

## Implementation Checklist

### Task 1: Add `ImageModelInfo` Domain Model (AC: #4)

**Tests:** 3.2-UNIT-001 to 3.2-UNIT-004

- [x] Create `ImageModelInfo` dataclass in `eleven_video/models/domain.py`
- [x] Add fields: `model_id: str`, `name: str`, `description: Optional[str]`, `supports_image_generation: bool`
- [x] Run tests: `uv run pytest tests/api/test_gemini_images.py::TestImageModelInfoModel -v`
- [x] ✅ Tests pass (green phase)

---

### Task 2: Add `list_image_models()` Method (AC: #4)

**Tests:** 3.2-UNIT-008 to 3.2-UNIT-010, 3.2-UNIT-016 to 3.2-UNIT-020

- [x] Add `_image_model_cache` and `_image_model_cache_ttl = 60` in `GeminiAdapter.__init__`
- [x] Create `_list_image_models_with_retry()` with `@retry` decorator
- [x] Add `list_image_models(use_cache: bool = False)` public method
- [x] Filter SDK models.list() response for image-capable models
- [x] Map SDK response to `ImageModelInfo` domain models
- [x] Implement caching with 60s TTL
- [x] Run tests: `uv run pytest tests/api/test_gemini_images.py::TestListImageModels -v`
- [x] ✅ Tests pass (green phase)

---

### Task 3: Add `ImageModelLister` Protocol (AC: #4)

**Tests:** 3.2-UNIT-005 to 3.2-UNIT-007

- [x] Define `ImageModelLister` protocol in `eleven_video/api/interfaces.py`
- [x] Add `@runtime_checkable` decorator
- [x] Define `list_image_models()` method signature
- [x] Run tests: `uv run pytest tests/api/test_gemini_images.py::TestImageModelListerProtocol -v`
- [x] ✅ Tests pass (green phase)

---

### Task 4: Add Model ID Validation and Fallback (AC: #3)

**Tests:** 3.2-UNIT-011 to 3.2-UNIT-014

- [x] Add `validate_image_model_id(model_id: str) -> bool` method
- [x] Implement using `list_image_models(use_cache=True)`
- [x] Update `generate_images()` signature with `model_id` and `warning_callback`
- [x] Implement fallback logic: invalid → default + call warning_callback
- [x] Run tests: `uv run pytest tests/api/test_gemini_images.py::TestImageModelIdValidation -v`
- [x] ✅ Tests pass (green phase)

---

### Task 5: Update `generate_images()` for Model Selection (AC: #1, #2)

**Tests:** 3.2-UNIT-015, 3.2-UNIT-021, 3.2-UNIT-022

- [x] Add optional `model_id: Optional[str] = None` parameter
- [x] Add optional `warning_callback: Optional[Callable[[str], None]] = None` parameter
- [x] Pass model_id to `_generate_image_with_retry()`
- [x] Update `_generate_image_with_retry()` to use `model_id or self.IMAGE_MODEL`
- [x] Run tests: `uv run pytest tests/api/test_gemini_images.py::TestDefaultModelBehavior -v`
- [x] ✅ Tests pass (green phase)

---

### Task 6: Update `ImageGenerator` Protocol (AC: #1, #3)

**Tests:** 3.2-UNIT-021, 3.2-UNIT-022

- [x] Update `ImageGenerator` protocol in interfaces.py
- [x] Add `model_id: Optional[str] = None` parameter
- [x] Add `warning_callback: Optional[Callable[[str], None]] = None` parameter
- [x] Ensure backward compatibility
- [x] Run tests: `uv run pytest tests/api/test_gemini_images.py::TestImageGeneratorProtocolUpdate -v`
- [x] ✅ Tests pass (green phase)

---

## Running Tests

```bash
# Run all failing tests for this story
uv run pytest tests/api/test_gemini_images.py -v

# Run specific test class
uv run pytest tests/api/test_gemini_images.py::TestImageModelInfoModel -v

# Run tests with verbose failure output
uv run pytest tests/api/test_gemini_images.py -v --tb=long

# Run single test
uv run pytest tests/api/test_gemini_images.py::TestImageModelInfoModel::test_imagemodelinfo_can_be_imported -v
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete) ✅

**TEA Agent Responsibilities:**

- ✅ All 22 tests written and failing
- ✅ Factory functions created
- ✅ Mock requirements documented
- ✅ Implementation checklist created

**Verification:**

- All tests fail with expected errors (ImportError, AttributeError)
- Failures are due to missing implementation, not test bugs

---

### GREEN Phase (DEV Team - Next Steps)

1. **Pick one failing test** from implementation checklist (start with Task 1)
2. **Read the test** to understand expected behavior
3. **Implement minimal code** to make that specific test pass
4. **Run the test** to verify it now passes (green)
5. **Check off the task** in implementation checklist
6. **Move to next test** and repeat

**Recommended Order:** Task 1 → Task 3 → Task 2 → Task 6 → Task 4 → Task 5

---

### REFACTOR Phase (DEV Team - After All Tests Pass)

1. **Verify all tests pass** (green phase complete)
2. **Review code for quality** (follow Story 3.1 patterns exactly)
3. **Ensure caching matches** Story 3.1's TTL approach
4. **Run full test suite** to verify no regressions

---

## Next Steps

1. **Review this checklist** for Story 3.2 scope
2. **Run failing tests** to confirm RED phase: `uv run pytest tests/api/test_gemini_images.py -v`
3. **Begin implementation** using checklist as guide
4. **Work one test at a time** (red → green for each)
5. **When all tests pass**, update story status to 'done' in sprint-status.yaml

---

## Knowledge Base References Applied

- **fixture-architecture.md** - Test patterns with setup/teardown
- **data-factories.md** - Factory patterns for random test data
- **test-quality.md** - Given-When-Then structure, one assertion per test

---

## Test Execution Evidence (RED Phase Verification)

**Command:** `uv run pytest tests/api/test_gemini_images.py -v --tb=short`

**Summary:**

- Total tests: 22
- Passing: 0 (expected)
- Failing: 22 (expected)
- Status: ✅ RED phase verified

**Expected Failure Types:**

- `ImportError: cannot import name 'ImageModelInfo'` - Domain model not created
- `ImportError: cannot import name 'ImageModelLister'` - Protocol not created
- `AttributeError: 'GeminiAdapter' object has no attribute 'list_image_models'` - Method not implemented
- `AttributeError: 'GeminiAdapter' object has no attribute 'validate_image_model_id'` - Method not implemented

---

**Generated by BMad TEA Agent** - 2025-12-18
