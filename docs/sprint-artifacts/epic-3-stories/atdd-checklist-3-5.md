# ATDD Checklist - Epic 3, Story 3.5: Gemini Text Generation Model Selection

**Date:** 2025-12-20
**Author:** Revenant
**Primary Test Level:** Unit + Component

---

## Story Summary

Enable users to select from available Gemini text generation models through interactive prompts, providing control over the style and quality of generated scripts.

**As a** user
**I want** to select from available Gemini text generation models through interactive prompts
**So that** I can control the style and quality of the generated script

---

## Acceptance Criteria

1. Display a numbered list of available text generation model options
2. When I select a model by number, my selection is used for script generation
3. On API failure, show helpful error message and fall back to default model with warning
4. Show option to use default model (e.g., "[0] Use default model (gemini-2.5-flash-lite)")
5. When `--gemini-model <id>` flag is provided, skip interactive Gemini model prompt

---

## Failing Tests Created (RED Phase)

### Backend Tests (12 tests)

**File:** `tests/api/test_gemini_text_models.py` (281 lines)

**Test Group 1: GeminiModelInfo Domain Model**
- ✅ **Test:** `test_gemini_model_info_can_be_created_with_required_fields`
  - **Status:** RED - `ImportError: cannot import name 'GeminiModelInfo'`
  - **Verifies:** Domain model structure with required fields
- ✅ **Test:** `test_gemini_model_info_can_be_created_with_all_fields`
  - **Status:** RED - `ImportError: cannot import name 'GeminiModelInfo'`
  - **Verifies:** Domain model accepts all optional fields

**Test Group 2: list_text_models() Method (3.5-UNIT-001)**
- ✅ **Test:** `test_list_text_models_returns_gemini_model_info_list`
  - **Status:** RED - Method does not exist
  - **Verifies:** AC #1 - Returns List[GeminiModelInfo]
- ✅ **Test:** `test_list_text_models_filters_out_image_models`
  - **Status:** RED - Method does not exist
  - **Verifies:** Excludes image-specific models
- ✅ **Test:** `test_list_text_models_with_cache_enabled`
  - **Status:** RED - Method does not exist
  - **Verifies:** Cache behavior (60s TTL)
- ✅ **Test:** `test_list_text_models_cache_expires_correctly`
  - **Status:** RED - Method does not exist
  - **Verifies:** Cache expiration and refresh

**Test Group 3: validate_text_model_id() Method**
- ✅ **Test:** `test_validate_text_model_id_returns_true_for_valid_id`
  - **Status:** RED - Method does not exist
  - **Verifies:** Returns True for existing model ID
- ✅ **Test:** `test_validate_text_model_id_returns_false_for_invalid_id`
  - **Status:** RED - Method does not exist
  - **Verifies:** Returns False for non-existent model ID
- ✅ **Test:** `test_validate_text_model_id_uses_cached_models`
  - **Status:** RED - Method does not exist
  - **Verifies:** Uses cached model list for efficiency

**Test Group 4: generate_script() with model_id (3.5-UNIT-001)**
- ✅ **Test:** `test_generate_script_accepts_model_id_parameter`
  - **Status:** RED - Parameter not yet supported
  - **Verifies:** AC #2 - Selected model is used for generation
- ✅ **Test:** `test_generate_script_uses_default_when_model_id_none`
  - **Status:** RED - Parameter not yet supported
  - **Verifies:** Fallback to DEFAULT_MODEL constant
- ✅ **Test:** `test_generate_script_falls_back_on_invalid_model_id`
  - **Status:** RED - Parameter not yet supported
  - **Verifies:** AC #3 - Fallback with warning

---

### UI Component Tests - Display (6 tests)

**File:** `tests/ui/test_gemini_model_selector_display.py` (117 lines)

**Test Group 1: GeminiModelSelector Display (3.5-COMP-001)**
- ✅ **Test:** `test_gemini_model_selector_can_be_imported`
  - **Status:** RED - `ModuleNotFoundError: No module named 'gemini_model_selector'`
  - **Verifies:** Module structure is correct
- ✅ **Test:** `test_gemini_model_selector_displays_numbered_list`
  - **Status:** RED - Module does not exist
  - **Verifies:** AC #1 - Display numbered list
- ✅ **Test:** `test_gemini_model_selector_shows_default_option_first`
  - **Status:** RED - Module does not exist
  - **Verifies:** AC #4 - Default model as option [0]

**Test Group 4: Boundary Conditions**
- ✅ **Test:** `test_display_model_list_with_single_model`
  - **Status:** RED - Module does not exist
  - **Verifies:** Minimum model list (1 model + default)
- ✅ **Test:** `test_display_model_list_with_many_models`
  - **Status:** RED - Module does not exist
  - **Verifies:** R-008 mitigation - many models
- ✅ **Test:** `test_display_model_list_with_none_descriptions`
  - **Status:** RED - Module does not exist
  - **Verifies:** Handle models with None descriptions

---

### UI Component Tests - Input (14 tests)

**File:** `tests/ui/test_gemini_model_selector_input.py` (207 lines)

**Test Group 2: Gemini Model Selection Input (3.5-COMP-001)**
- ✅ **Test:** `test_select_model_returns_model_id_for_valid_number`
  - **Status:** RED - Module does not exist
  - **Verifies:** AC #2 - Valid number returns model_id
- ✅ **Test:** `test_select_model_returns_none_for_zero`
  - **Status:** RED - Module does not exist
  - **Verifies:** AC #4 - Zero = default model
- ✅ **Test:** `test_select_model_handles_invalid_number`
  - **Status:** RED - Module does not exist
  - **Verifies:** Invalid number falls back to default
- ✅ **Test:** `test_select_model_handles_non_numeric_input`
  - **Status:** RED - Module does not exist
  - **Verifies:** Non-numeric input falls back to default

**Test Group 3: Error Handling**
- ✅ **Test:** `test_select_model_interactive_handles_api_failure`
  - **Status:** RED - Module does not exist
  - **Verifies:** AC #3 - API failure graceful fallback
- ✅ **Test:** `test_select_model_interactive_handles_empty_model_list`
  - **Status:** RED - Module does not exist
  - **Verifies:** Empty list falls back to default

**Test Group 5: Non-TTY Fallback (R-004 Mitigation)**
- ✅ **Test:** `test_select_model_interactive_skips_prompt_in_non_tty`
  - **Status:** RED - Module does not exist
  - **Verifies:** R-004 - Non-TTY uses default
- ✅ **Test:** `test_select_model_interactive_shows_message_in_non_tty`
  - **Status:** RED - Module does not exist
  - **Verifies:** Informative message in non-TTY

**Test Group 6: Edge Case Inputs (6 parametrized tests)**
- ✅ **Test:** `test_select_model_handles_invalid_input[negative/-1]`
  - **Status:** RED - Module does not exist
  - **Verifies:** Negative number handled
- ✅ **Test:** `test_select_model_handles_invalid_input[large/9999]`
  - **Status:** RED - Module does not exist
  - **Verifies:** Large number handled
- ✅ **Test:** `test_select_model_handles_invalid_input[text/abc]`
  - **Status:** RED - Module does not exist
  - **Verifies:** Text input handled
- ✅ **Test:** `test_select_model_handles_invalid_input[special/!@#$%]`
  - **Status:** RED - Module does not exist
  - **Verifies:** Special chars handled
- ✅ **Test:** `test_select_model_handles_empty_input`
  - **Status:** RED - Module does not exist
  - **Verifies:** Empty input uses default
- ✅ **Test:** `test_select_last_model_in_list`
  - **Status:** RED - Module does not exist
  - **Verifies:** Boundary - last model selection
- ✅ **Test:** `test_select_model_interactive_full_flow`
  - **Status:** RED - Module does not exist
  - **Verifies:** End-to-end interactive flow

---

## Data Factories Created

### GeminiModelInfo Factory

**File:** `tests/ui/conftest.py` (added lines 183-258)

**Exports:**
- `create_gemini_model_info(overrides?)` - Create single GeminiModelInfo with optional overrides
- `create_mock_gemini_model_list(count)` - Create array of test models

**Example Usage:**

```python
model = create_gemini_model_info(model_id="gemini-2.5-pro", name="Pro")
models = create_mock_gemini_model_list(5)  # Generate 5 random models
```

---

## Fixtures Created

### GeminiModelSelector Fixtures

**File:** `tests/ui/conftest.py`

**Fixtures:**
- `gemini_model_selector` - Create GeminiModelSelector with mock adapter
  - **Setup:** Creates instance with `mock_gemini_adapter`
  - **Provides:** `GeminiModelSelector` instance
  - **Cleanup:** N/A (mocked)

- `sample_gemini_models` - Standard list of 3 models for testing
  - **Setup:** Creates gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.5-pro
  - **Provides:** `List[GeminiModelInfo]`
  - **Cleanup:** N/A

- `single_gemini_model` - Single model for minimal testing
  - **Setup:** Creates one test model
  - **Provides:** `List[GeminiModelInfo]` with 1 item
  - **Cleanup:** N/A

- `mock_console_gemini` - Patched console for GeminiModelSelector
  - **Setup:** Patches `eleven_video.ui.gemini_model_selector.console`
  - **Provides:** Mock console with `is_terminal=True`
  - **Cleanup:** Context manager restores

- `mock_prompt_gemini` - Patched Rich Prompt for input testing
  - **Setup:** Patches `eleven_video.ui.gemini_model_selector.Prompt`
  - **Provides:** Mock Prompt
  - **Cleanup:** Context manager restores

**Example Usage:**

```python
def test_example(gemini_model_selector, sample_gemini_models):
    # gemini_model_selector is ready with mock adapter
    result = gemini_model_selector._display_model_list(sample_gemini_models)
```

---

## Mock Requirements

### Gemini API Mock (list_text_models)

**Endpoint:** `client.models.list()`

**Success Response:**

```json
[
  {"name": "models/gemini-2.5-flash", "display_name": "Gemini 2.5 Flash", "description": "Fast"},
  {"name": "models/gemini-2.5-pro", "display_name": "Gemini 2.5 Pro", "description": "Quality"}
]
```

**Filtered Out (image models):**

```json
[
  {"name": "models/imagen-3.0-generate-001", "display_name": "Imagen 3", "description": "Images"}
]
```

**Notes:** Filter excludes models with `image`, `imagen`, or `embedding` in name.

---

## Required data-testid Attributes

No UI data-testid attributes required for this story - Rich library handles terminal rendering directly.

---

## Implementation Checklist

### Test: GeminiModelInfo Domain Model Creation

**File:** `eleven_video/models/domain.py`

**Tasks to make this test pass:**

- [ ] Add `GeminiModelInfo` dataclass after `ImageModelInfo`
- [ ] Add fields: `model_id: str`, `name: str`, `description: Optional[str] = None`, `supports_text_generation: bool = True`
- [ ] Add docstring with Story 3.5 reference
- [ ] Run test: `uv run pytest tests/api/test_gemini_text_models.py::TestGeminiModelInfo -v`
- [ ] ✅ Tests pass (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: list_text_models() Method

**File:** `eleven_video/api/gemini.py`

**Tasks to make this test pass:**

- [ ] Add import for `GeminiModelInfo` at top of file
- [ ] Add `_text_model_cache` attribute in `__init__` (after `_image_model_cache`)
- [ ] Add `_text_model_cache_ttl` attribute (60 seconds)
- [ ] Implement `list_text_models(use_cache: bool = False)` method
- [ ] Implement `_list_text_models_with_retry()` with retry decorator
- [ ] Add filtering logic: include `gemini` prefix, exclude `image`, `imagen`, `embedding`
- [ ] Run test: `uv run pytest tests/api/test_gemini_text_models.py::TestListTextModels -v`
- [ ] ✅ Tests pass (green phase)

**Estimated Effort:** 1.5 hours

---

### Test: validate_text_model_id() Method

**File:** `eleven_video/api/gemini.py`

**Tasks to make this test pass:**

- [ ] Implement `validate_text_model_id(model_id: str) -> bool` method
- [ ] Use `list_text_models(use_cache=True)` for validation
- [ ] Return `any(model.model_id == model_id for model in available_models)`
- [ ] Run test: `uv run pytest tests/api/test_gemini_text_models.py::TestValidateTextModelId -v`
- [ ] ✅ Tests pass (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: generate_script() with model_id Parameter

**Files:** `eleven_video/api/gemini.py`, `eleven_video/orchestrator/video_pipeline.py`

**Tasks to make this test pass:**

- [ ] Add `model_id: Optional[str] = None` parameter to `generate_script()`
- [ ] Add `warning_callback: Optional[Callable[[str], None]] = None` parameter
- [ ] Validate model_id using `validate_text_model_id()`
- [ ] If invalid, call `warning_callback` and use `DEFAULT_MODEL`
- [ ] Update `_generate_with_retry()` signature to accept `model_id`
- [ ] Pass `model_id` to `_genai_client.models.generate_content(model=...)`
- [ ] Update `VideoPipeline.generate()` to accept and pass `gemini_model_id`
- [ ] Run test: `uv run pytest tests/api/test_gemini_text_models.py::TestGenerateScriptWithModelId -v`
- [ ] ✅ Tests pass (green phase)

**Estimated Effort:** 1.5 hours

---

### Test: GeminiModelSelector Class

**File:** `eleven_video/ui/gemini_model_selector.py` (NEW)

**Tasks to make this test pass:**

- [ ] Create new file `eleven_video/ui/gemini_model_selector.py`
- [ ] Add imports: `typing`, `rich.table`, `rich.panel`, `rich.prompt`, `console`, `GeminiModelInfo`
- [ ] Create `GeminiModelSelector` class with `__init__(adapter: GeminiAdapter)`
- [ ] Add class constants: `DEFAULT_MODEL_ID`, `DEFAULT_MODEL_NAME`
- [ ] Implement `_display_model_list(models)` with Rich Table
- [ ] Add row 0 for "Default (gemini-2.5-flash-lite)"
- [ ] Implement `_get_user_selection(models)` with Rich Prompt
- [ ] Implement `select_model_interactive()` main entry point
- [ ] Export from `eleven_video/ui/__init__.py`
- [ ] Run test: `uv run pytest tests/ui/test_gemini_model_selector_display.py tests/ui/test_gemini_model_selector_input.py -v`
- [ ] ✅ Tests pass (green phase)

**Estimated Effort:** 2.0 hours

---

### Test: Non-TTY Fallback (R-004)

**File:** `eleven_video/ui/gemini_model_selector.py`

**Tasks to make this test pass:**

- [ ] Check `console.is_terminal` at start of `select_model_interactive()`
- [ ] If non-TTY: print message and return None (use default)
- [ ] Skip API call in non-TTY mode
- [ ] Run test: `uv run pytest tests/ui/test_gemini_model_selector_input.py::TestGeminiModelSelectorNonTTY -v`
- [ ] ✅ Tests pass (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: CLI Integration (--gemini-model flag)

**File:** `eleven_video/main.py`

**Tasks to make this test pass:**

- [ ] Add `--gemini-model` option to `generate()` function (no `-gm` short option due to `-g` conflict)
- [ ] If None, call `GeminiModelSelector.select_model_interactive()`
- [ ] If provided, skip interactive prompt
- [ ] Pass `gemini_model` to `pipeline.generate(gemini_model_id=...)`
- [ ] Add error handling with graceful fallback
- [ ] Run test: `uv run pytest tests/ui/test_cli_generate.py -v` (integration tests)
- [ ] ✅ Tests pass (green phase)

**Estimated Effort:** 1.0 hours

---

## Running Tests

```bash
# Run all failing tests for this story
uv run pytest tests/api/test_gemini_text_models.py tests/ui/test_gemini_model_selector_display.py tests/ui/test_gemini_model_selector_input.py -v

# Run specific test file
uv run pytest tests/api/test_gemini_text_models.py -v

# Run tests with coverage
uv run pytest tests/api/test_gemini_text_models.py tests/ui/test_gemini_model_selector_*.py -v --cov=eleven_video

# Debug specific test
uv run pytest tests/api/test_gemini_text_models.py::TestListTextModels::test_list_text_models_returns_gemini_model_info_list -v --tb=long
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete) ✅

**TEA Agent Responsibilities:**

- ✅ All tests written and failing (32 tests)
- ✅ Fixtures and factories created with patterns from Story 3.4
- ✅ Implementation checklist created
- ✅ Tests fail due to missing implementation, not test bugs

**Verification:**

- Tests fail with `ImportError: cannot import name 'GeminiModelInfo'`
- Tests fail with `ModuleNotFoundError: No module named 'gemini_model_selector'`
- Tests fail with `AttributeError` for missing methods

---

### GREEN Phase (DEV Team - Next Steps)

**DEV Agent Responsibilities:**

1. **Pick one failing test** from implementation checklist (start with domain model)
2. **Read the test** to understand expected behavior
3. **Implement minimal code** to make that specific test pass
4. **Run the test** to verify it now passes (green)
5. **Check off the task** in implementation checklist
6. **Move to next test** and repeat

**Recommended Order:**

1. `GeminiModelInfo` domain model (unblocks all other tests)
2. `list_text_models()` method
3. `validate_text_model_id()` method
4. `GeminiModelSelector` class (display + input)
5. `generate_script()` model_id parameter
6. CLI integration

**Key Principles:**

- One test at a time (don't try to fix all at once)
- Minimal implementation (don't over-engineer)
- Run tests frequently (immediate feedback)
- Use implementation checklist as roadmap

---

### REFACTOR Phase (DEV Team - After All Tests Pass)

**DEV Agent Responsibilities:**

1. **Verify all tests pass** (green phase complete)
2. **Review code for quality** (readability, maintainability)
3. **Extract duplications** if any (DRY principle)
4. **Ensure tests still pass** after each refactor
5. **Update story status** to done

---

## Next Steps

1. **Run failing tests** to confirm RED phase: `uv run pytest tests/api/test_gemini_text_models.py tests/ui/test_gemini_model_selector_*.py -v`
2. **Begin implementation** using implementation checklist as guide
3. **Start with `GeminiModelInfo`** domain model (unblocks all tests)
4. **Work one test at a time** (red → green for each)
5. **When all tests pass**, refactor code for quality
6. **When refactoring complete**, manually update story status to 'done' in sprint-status.yaml

---

## Knowledge Base References Applied

This ATDD workflow consulted the following knowledge fragments:

- **data-factories.md** - Factory patterns using `@faker-js/faker` for random test data generation with overrides support
- **test-quality.md** - Test design principles (Given-When-Then, one assertion per test, determinism, isolation)

See `tea-index.csv` for complete knowledge fragment mapping.

---

## Test Execution Evidence

### Initial Test Run (RED Phase Verification)

**Command:** `uv run pytest tests/api/test_gemini_text_models.py tests/ui/test_gemini_model_selector_*.py -v`

**Results:**

```
ERROR tests/api/test_gemini_text_models.py - ImportError: cannot import name 'GeminiModelInfo'
ERROR tests/ui/test_gemini_model_selector_display.py - ModuleNotFoundError: No module named 'gemini_model_selector'
ERROR tests/ui/test_gemini_model_selector_input.py - ModuleNotFoundError: No module named 'gemini_model_selector'
```

**Summary:**

- Total tests: 32 (planned)
- Passing: 0 (expected)
- Failing: 3 collection errors (expected - missing implementation)
- Status: ✅ RED phase verified

**Expected Failure Messages:**

- `ImportError: cannot import name 'GeminiModelInfo' from 'eleven_video.models.domain'`
- `ModuleNotFoundError: No module named 'eleven_video.ui.gemini_model_selector'`
- `AttributeError: 'GeminiAdapter' object has no attribute 'list_text_models'`

---

## Notes

- **Pattern:** This story combines Stories 3.2 (backend) + 3.4 (UI) patterns but for text generation models
- **CLI Conflict:** `-g` is already used by `--gemini-key`, so `--gemini-model` has no short option
- **Cache Pattern:** 60-second TTL matches `list_image_models()` implementation
- **R-004 Mitigation:** Non-TTY detection via `console.is_terminal` same as Story 3.4

---

## Contact

**Questions or Issues?**

- Ask in team standup
- Refer to `docs/sprint-artifacts/epic-3-stories/story-3-5-gemini-text-generation-model-selection.md` for full story context
- Consult Story 3.4 implementation for UI patterns

---

**Generated by BMad TEA Agent** - 2025-12-20
