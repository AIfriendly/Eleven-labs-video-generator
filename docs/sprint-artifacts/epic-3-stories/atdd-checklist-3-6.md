# ATDD Checklist - Epic 3, Story 3.6: Video Duration Selection

**Date:** 2025-12-20
**Author:** Revenant
**Primary Test Level:** Unit + Component

---

## Story Summary

Implement video duration selection through interactive prompts, allowing users to control how long their generated video will be.

**As a** user
**I want** to select a target video duration through interactive prompts
**So that** I can control how long my generated video will be

---

## Acceptance Criteria

1. Display a numbered list of duration options (e.g., 3 minutes, 5 minutes, 10 minutes)
2. Select a duration by number and system generates script/assets appropriate for that duration
3. Show option to use the default duration (e.g., "[0] Default (3 minutes)")
4. CLI flag `--duration` skips interactive duration prompt
5. Generated script length approximately matches target duration, image count adjusted accordingly
6. Duration selection prompt appears BEFORE video topic/prompt input (configuration before content)

---

## Failing Tests Created (RED Phase)

### Unit Tests - Duration Domain Model (17 tests)

**File:** `tests/models/test_duration_option.py` (~165 lines)

- ✅ **Test:** `test_duration_option_can_be_imported`
  - **Status:** RED - `DurationOption` not defined in domain.py
  - **Verifies:** Module structure

- ✅ **Test:** `test_duration_option_creation_with_all_fields`
  - **Status:** RED - `DurationOption` class doesn't exist
  - **Verifies:** Dataclass creation

- ✅ **Test:** `test_estimated_word_count_for_3_minutes`
  - **Status:** RED - `estimated_word_count` property not implemented
  - **Verifies:** 3 min → 450 words calculation

- ✅ **Test:** `test_estimated_word_count_for_5_minutes`
  - **Status:** RED - Same as above
  - **Verifies:** 5 min → 750 words calculation

- ✅ **Test:** `test_estimated_image_count_for_*`
  - **Status:** RED - `estimated_image_count` property not implemented
  - **Verifies:** 15 images/minute calculation

- ✅ **Test:** `test_duration_options_*` (constants)
  - **Status:** RED - `DURATION_OPTIONS`, `DEFAULT_DURATION_MINUTES` not defined
  - **Verifies:** Preset constants exist

- ✅ **Test:** `test_video_duration_enum_*`
  - **Status:** RED - `VideoDuration` enum not defined
  - **Verifies:** Enum with SHORT=3, STANDARD=5, EXTENDED=10

### Component Tests - DurationSelector Display (10 tests)

**File:** `tests/ui/test_duration_selector_display.py` (~130 lines)

- ✅ **Test:** `test_duration_selector_can_be_imported`
  - **Status:** RED - `eleven_video.ui.duration_selector` module doesn't exist
  - **Verifies:** Module structure

- ✅ **Test:** `test_duration_selector_displays_numbered_list`
  - **Status:** RED - `_display_duration_options()` method not implemented
  - **Verifies:** AC #1 - Numbered list display

- ✅ **Test:** `test_duration_selector_shows_default_option_first`
  - **Status:** RED - Default option "[0]" not implemented
  - **Verifies:** AC #3 - Default option first

- ✅ **Test:** `test_duration_selector_shows_multiple_duration_options`
  - **Status:** RED - Options list not populated
  - **Verifies:** 3, 5, 10 minute presets displayed

### Component Tests - DurationSelector Input (14 tests)

**File:** `tests/ui/test_duration_selector_input.py` (~185 lines)

- ✅ **Test:** `test_select_duration_returns_minutes_for_valid_number`
  - **Status:** RED - `_get_user_selection()` not implemented
  - **Verifies:** AC #2 - Valid selection returns minutes

- ✅ **Test:** `test_select_duration_returns_none_for_zero`
  - **Status:** RED - Default selection handling not implemented
  - **Verifies:** AC #3 - Option 0 returns None (default)

- ✅ **Test:** `test_select_duration_handles_invalid_number`
  - **Status:** RED - Invalid input fallback not implemented
  - **Verifies:** Graceful input validation

- ✅ **Test:** `test_select_duration_interactive_skips_prompt_in_non_tty`
  - **Status:** RED - Non-TTY detection not implemented
  - **Verifies:** R-004 mitigation

- ✅ **Test:** `test_duration_options_contain_expected_values`
  - **Status:** RED - Constants not defined
  - **Verifies:** Preset options contain 3, 5, 10

### API Tests - GeminiAdapter Duration (12 tests)

**File:** `tests/api/test_gemini_duration.py` (~200 lines)

- ✅ **Test:** `test_generate_script_accepts_duration_minutes_parameter`
  - **Status:** RED - `duration_minutes` parameter not added to signature
  - **Verifies:** AC #5 - Duration parameter exists

- ✅ **Test:** `test_generate_script_with_3_minute_duration_includes_instruction`
  - **Status:** RED - Duration instruction not added to prompt
  - **Verifies:** 3.6-UNIT-001 - Duration in prompt

- ✅ **Test:** `test_generate_images_accepts_target_image_count_parameter`
  - **Status:** RED - `target_image_count` parameter not added
  - **Verifies:** AC #5 - Image count parameter exists

- ✅ **Test:** `test_adjust_segment_count_method_exists`
  - **Status:** RED - `_adjust_segment_count()` helper not implemented
  - **Verifies:** Segment adjustment method

- ✅ **Test:** `test_adjust_segment_count_trims_when_over_target`
  - **Status:** RED - Trim logic not implemented
  - **Verifies:** Task 5.4 - Trim excess segments

- ✅ **Test:** `test_adjust_segment_count_expands_when_under_target`
  - **Status:** RED - Expand logic not implemented
  - **Verifies:** Task 5.4 - Expand to fill target

---

## Data Factories Created

### DurationOption Factory

**File:** `tests/ui/conftest.py` (added to existing file)

**Exports:**

- `create_duration_option(minutes, label, description)` - Create single DurationOption with overrides

**Example Usage:**

```python
option = create_duration_option(minutes=5, label="Standard")
```

---

## Fixtures Created

### Duration Fixtures

**File:** `tests/ui/conftest.py` (added to existing file)

**Fixtures:**

- `duration_selector` - Creates DurationSelector instance
  - **Setup:** Imports and instantiates DurationSelector
  - **Provides:** Ready-to-use DurationSelector
  - **Cleanup:** None needed (no external resources)

- `sample_duration_options` - Returns DURATION_OPTIONS constant
  - **Setup:** Imports DURATION_OPTIONS from domain.py
  - **Provides:** List of DurationOption presets
  - **Cleanup:** None needed

- `mock_console_duration` - Patches console for DurationSelector
  - **Setup:** Patches `eleven_video.ui.duration_selector.console`
  - **Provides:** Mock console with `is_terminal=True`
  - **Cleanup:** Auto-restored by context manager

- `mock_prompt_duration` - Patches Prompt for DurationSelector
  - **Setup:** Patches `eleven_video.ui.duration_selector.Prompt`
  - **Provides:** Mock Prompt for testing user input
  - **Cleanup:** Auto-restored by context manager

---

## Mock Requirements

No external service mocking required for Story 3.6. Duration options are predefined presets.

---

## Required data-testid Attributes

N/A - Story 3.6 is a CLI/terminal UI story, not a web UI. No data-testid attributes needed.

---

## Implementation Checklist

### Test: DurationOption Domain Model

**File:** `tests/models/test_duration_option.py`

**Tasks to make these tests pass:**

- [ ] Add `VideoDuration` enum to `eleven_video/models/domain.py` with SHORT=3, STANDARD=5, EXTENDED=10
- [ ] Add `DurationOption` dataclass with fields: `minutes`, `label`, `description` (default="")
- [ ] Add `estimated_word_count` property (minutes * 150)
- [ ] Add `estimated_image_count` property (minutes * 15)
- [ ] Add `DURATION_OPTIONS` list constant with 3, 5, 10 minute presets
- [ ] Add `DEFAULT_DURATION_MINUTES = 5` constant
- [ ] Run tests: `uv run pytest tests/models/test_duration_option.py -v`
- [ ] ✅ Tests pass (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: DurationSelector Display

**File:** `tests/ui/test_duration_selector_display.py`

**Tasks to make these tests pass:**

- [ ] Create `eleven_video/ui/duration_selector.py` module
- [ ] Create `DurationSelector` class with `__init__()` that loads `DURATION_OPTIONS`
- [ ] Implement `_display_duration_options()` method using Rich Panel + Table
- [ ] Display "[0] Default (5 min)" as first row
- [ ] Display "[1] 3 min (Short)", "[2] 5 min (Standard)", "[3] 10 min (Extended)"
- [ ] Run tests: `uv run pytest tests/ui/test_duration_selector_display.py -v`
- [ ] ✅ Tests pass (green phase)

**Estimated Effort:** 1 hour

---

### Test: DurationSelector Input

**File:** `tests/ui/test_duration_selector_input.py`

**Tasks to make these tests pass:**

- [ ] Implement `_get_user_selection()` method returning `Optional[int]` (minutes)
- [ ] Return `None` for input "0" (default)
- [ ] Return `self._options[index-1].minutes` for valid 1-N input
- [ ] Return `None` with warning for invalid input
- [ ] Implement `select_duration_interactive()` method
- [ ] Add non-TTY check: `if not console.is_terminal: return None`
- [ ] Handle exceptions gracefully, return None on error
- [ ] Run tests: `uv run pytest tests/ui/test_duration_selector_input.py -v`
- [ ] ✅ Tests pass (green phase)

**Estimated Effort:** 1 hour

---

### Test: GeminiAdapter Duration Support

**File:** `tests/api/test_gemini_duration.py`

**Tasks to make these tests pass:**

- [ ] Add `duration_minutes: Optional[int] = None` parameter to `generate_script()`
- [ ] Calculate `effective_duration = duration_minutes or 3`
- [ ] Add duration instruction to prompt: "Generate a script for approximately a {N}-minute video..."
- [ ] Add `target_image_count: Optional[int] = None` parameter to `generate_images()`
- [ ] Implement `_adjust_segment_count(segments, target)` helper method
- [ ] Trim segments if len > target (take first N)
- [ ] Expand segments if len < target (cycle through originals)
- [ ] Run tests: `uv run pytest tests/api/test_gemini_duration.py -v`
- [ ] ✅ Tests pass (green phase)

**Estimated Effort:** 1.5 hours

---

### CLI Integration (No ATDD tests - manual verification)

**Tasks:**

- [ ] Add `--duration` / `-d` CLI option to `generate()` in `main.py`
- [ ] Validate CLI duration input: must be 3, 5, or 10
- [ ] Reorder prompts: Duration before Prompt (configuration before content)
- [ ] If duration is None, call DurationSelector before asking for video topic
- [ ] Skip duration prompt if `--duration` flag was provided
- [ ] Pass duration through pipeline to adapters
- [ ] Export `DurationSelector` from `eleven_video/ui/__init__.py`
- [ ] Export domain constants from `eleven_video/models/domain.py`

**Estimated Effort:** 1 hour

---

### Pipeline Integration (No ATDD tests - manual verification)

**Tasks:**

- [ ] Add `duration_minutes: Optional[int] = None` parameter to `VideoPipeline.generate()`
- [ ] Pass `duration_minutes` to `generate_script()` call
- [ ] Calculate `target_image_count = duration_minutes * 15` if duration provided
- [ ] Pass `target_image_count` to `generate_images()` call

**Estimated Effort:** 0.5 hours

---

## Running Tests

```bash
# Run all failing tests for this story
uv run pytest tests/ui/test_duration_selector_display.py tests/ui/test_duration_selector_input.py tests/models/test_duration_option.py tests/api/test_gemini_duration.py -v

# Run specific test file
uv run pytest tests/models/test_duration_option.py -v

# Run tests with verbose output
uv run pytest tests/ui/test_duration_selector_display.py -v --tb=short

# Debug specific test
uv run pytest tests/ui/test_duration_selector_input.py::TestDurationSelectorInput::test_select_duration_returns_minutes_for_valid_number -v -s
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete) ✅

**TEA Agent Responsibilities:**

- ✅ All tests written and failing
- ✅ Fixtures and factories created with auto-cleanup
- ✅ No mock requirements (duration uses presets)
- ✅ No data-testid requirements (CLI story)
- ✅ Implementation checklist created

**Verification:**

- All tests run and fail as expected
- Failure messages are clear (ImportError, AttributeError for missing code)
- Tests fail due to missing implementation, not test bugs

---

### GREEN Phase (DEV Team - Next Steps)

**DEV Agent Responsibilities:**

1. **Pick one failing test** from implementation checklist (start with domain model)
2. **Read the test** to understand expected behavior
3. **Implement minimal code** to make that specific test pass
4. **Run the test** to verify it now passes (green)
5. **Check off the task** in implementation checklist
6. **Move to next test** and repeat

**Key Principles:**

- One test at a time (don't try to fix all at once)
- Minimal implementation (don't over-engineer)
- Run tests frequently (immediate feedback)
- Use implementation checklist as roadmap

**Recommended Order:**

1. Domain model (`test_duration_option.py`) - Foundation
2. DurationSelector display (`test_duration_selector_display.py`) - UI
3. DurationSelector input (`test_duration_selector_input.py`) - User interaction
4. GeminiAdapter duration (`test_gemini_duration.py`) - Backend support
5. CLI and pipeline integration - Glue everything together

---

### REFACTOR Phase (DEV Team - After All Tests Pass)

**DEV Agent Responsibilities:**

1. **Verify all tests pass** (green phase complete)
2. **Review code for quality** (readability, maintainability, performance)
3. **Extract duplications** (DRY principle)
4. **Optimize performance** (if needed)
5. **Ensure tests still pass** after each refactor
6. **Update documentation** (if API contracts change)

---

## Next Steps

1. **Review this checklist** with team in standup or planning
2. **Run failing tests** to confirm RED phase: `uv run pytest tests/models/test_duration_option.py -v`
3. **Begin implementation** using implementation checklist as guide
4. **Work one test at a time** (red → green for each)
5. **Share progress** in daily standup
6. **When all tests pass**, refactor code for quality
7. **When refactoring complete**, manually update story status to 'in-progress' then 'done' in sprint-status.yaml

---

## Knowledge Base References Applied

This ATDD workflow consulted the following knowledge fragments:

- **data-factories.md** - Factory patterns using `@faker-js/faker` for test data generation (applied to create_duration_option)
- **fixture-architecture.md** - Test fixture patterns with Playwright's `test.extend()` (adapted for pytest fixtures)
- **test-quality.md** - Test design principles (Given-When-Then, one assertion per test, determinism, isolation)
- **component-tdd.md** - Component test strategies (applied to DurationSelector UI tests)

See `tea-index.csv` for complete knowledge fragment mapping.

---

## Test Execution Evidence

### Initial Test Run (RED Phase Verification)

**Command:** `uv run pytest tests/models/test_duration_option.py tests/ui/test_duration_selector_display.py tests/ui/test_duration_selector_input.py tests/api/test_gemini_duration.py -v --tb=short`

**Summary:**

- Total tests: ~53 tests collected
- Passing: 0 (expected)
- Failing: All (expected)
- Status: ✅ RED phase verified

**Expected Failure Messages:**

- `ModuleNotFoundError: No module named 'eleven_video.ui.duration_selector'`
- `ImportError: cannot import name 'DurationOption' from 'eleven_video.models.domain'`
- `ImportError: cannot import name 'DURATION_OPTIONS' from 'eleven_video.models.domain'`
- `AttributeError: 'GeminiAdapter' object has no attribute '_adjust_segment_count'`

---

## Notes

- **Key difference from other selectors:** DurationSelector uses predefined presets, no API call needed
- **Duration affects two downstream processes:** Script generation (word count) AND image generation (image count)
- **Prompt order is critical:** Duration must come BEFORE video topic prompt (AC #6)
- **R-003 mitigation:** Pass duration explicitly to ensure script/images match target duration
- **R-004 mitigation:** Non-TTY fallback returns None (uses default 5 minutes)

---

## Contact

**Questions or Issues?**

- Ask in team standup
- Tag @tea-agent in Slack/Discord
- Refer to `./bmm/docs/tea-README.md` for workflow documentation
- Consult `./bmm/testarch/knowledge` for testing best practices

---

**Generated by BMad TEA Agent** - 2025-12-20
