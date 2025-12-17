# ATDD Checklist - Story 2.5: Progress Updates During Video Generation

**Date:** 2025-12-16  
**Author:** TEA (Murat)  
**Primary Test Level:** Unit Tests (pytest + Rich Console mocking)

---

## Story Summary

**As a** user,  
**I want** to receive progress updates during video generation,  
**So that** I can understand how long the process will take and its current status.

---

## Acceptance Criteria

1. Receive clear, textual progress updates for each stage
2. Progress message with stage name and visual indicator when stage begins
3. Completion message with elapsed time when stage completes
4. Image progress like "Processing image 3 of 5" with percentage
5. "Compiling video..." with spinner/progress indicator
6. Error shows which stage failed with clear error indicator
7. Summary with total elapsed time and output file path

---

## Failing Tests Created (RED Phase)

### Unit Tests (25 tests)

**File:** [test_progress.py](file:///d:/Eleven-labs-AI-Video/tests/ui/test_progress.py)

| Test ID | Test Name | Status | Verifies |
|---------|-----------|--------|----------|
| 2.5-UNIT-001 | `test_pipeline_stage_enum_exists` | 🟢 GREEN | AC1 - PipelineStage enum |
| 2.5-UNIT-002 | `test_pipeline_stage_has_required_values` | 🟢 GREEN | AC1 - All stage values |
| 2.5-UNIT-003 | `test_stage_icons_dict_exists` | 🟢 GREEN | AC2 - STAGE_ICONS dict |
| 2.5-UNIT-004 | `test_video_pipeline_progress_exists` | 🟢 GREEN | AC1 - Class exists |
| 2.5-UNIT-005 | `test_video_pipeline_progress_accepts_optional_console` | 🟢 GREEN | AC1 - DI for Console |
| 2.5-UNIT-006 | `test_video_pipeline_progress_uses_default_console` | 🟢 GREEN | AC1 - Default singleton |
| 2.5-UNIT-007 | `test_start_stage_updates_current_stage` | 🟢 GREEN | AC2 - Stage transition |
| 2.5-UNIT-008 | `test_start_stage_displays_stage_message` | 🟢 GREEN | AC2 - Stage display |
| 2.5-UNIT-009 | `test_start_stage_records_start_time` | 🟢 GREEN | AC3 - Timing |
| 2.5-UNIT-010 | `test_complete_stage_displays_elapsed_time` | 🟢 GREEN | AC3 - Elapsed time |
| 2.5-UNIT-011 | `test_first_stage_starts_pipeline_timer` | 🟢 GREEN | AC7 - Total timing |
| 2.5-UNIT-012 | `test_update_progress_parses_image_count` | 🟢 GREEN | AC4 - Image parsing |
| 2.5-UNIT-013 | `test_update_progress_displays_percentage` | 🟢 GREEN | AC4 - Percentage |
| 2.5-UNIT-014 | `test_update_progress_generic_message` | 🟢 GREEN | AC1 - Generic msgs |
| 2.5-UNIT-015 | `test_compiling_shows_spinner_message` | 🟢 GREEN | AC5 - Spinner |
| 2.5-UNIT-016 | `test_fail_stage_displays_red_panel` | 🟢 GREEN | AC6 - Error display |
| 2.5-UNIT-017 | `test_fail_stage_shows_failed_icon` | 🟢 GREEN | AC6 - Failed icon |
| 2.5-UNIT-018 | `test_fail_stage_updates_current_stage` | 🟢 GREEN | AC6 - State update |
| 2.5-UNIT-019 | `test_show_summary_displays_green_panel` | 🟢 GREEN | AC7 - Success panel |
| 2.5-UNIT-020 | `test_show_summary_includes_output_path` | 🟢 GREEN | AC7 - Path display |
| 2.5-UNIT-021 | `test_show_summary_includes_total_time` | 🟢 GREEN | AC7 - Total time |
| 2.5-UNIT-022 | `test_show_summary_includes_video_duration` | 🟢 GREEN | AC7 - Duration |
| 2.5-UNIT-023 | `test_create_callback_returns_callable` | 🟢 GREEN | AC1 - Callback factory |
| 2.5-UNIT-024 | `test_callback_invokes_update_progress` | 🟢 GREEN | AC1 - Callback works |
| 2.5-UNIT-025 | `test_callback_compatible_with_adapter_signature` | 🟢 GREEN | AC1 - Adapter compat |

---

## Test Infrastructure

### Factories Created

**File:** Included in [test_progress.py](file:///d:/Eleven-labs-AI-Video/tests/ui/test_progress.py)

- `create_test_video(file_path, duration, size_bytes)` - Creates Video domain model for testing

### Fixtures Created

```python
@pytest.fixture
def mock_console():
    """Mock Rich Console for output verification."""
    output = StringIO()
    test_console = Console(file=output, force_terminal=True, width=120)
    yield output, test_console
```

---

## Implementation Checklist

### Task 1: Add PipelineStage Enum (AC1)

**Tests:** 2.5-UNIT-001, 2.5-UNIT-002, 2.5-UNIT-003

- [ ] Add `PipelineStage` enum to [domain.py](file:///d:/Eleven-labs-AI-Video/eleven_video/models/domain.py)
- [ ] Add values: INITIALIZING, PROCESSING_SCRIPT, PROCESSING_AUDIO, PROCESSING_IMAGES, COMPILING_VIDEO, COMPLETED, FAILED
- [ ] Add `STAGE_ICONS` dict mapping stages to emoji icons
- [ ] Export from `__init__.py`
- [ ] Run: `python -m pytest tests/ui/test_progress.py::TestPipelineStageEnum -v`
- [ ] ✅ Tests pass (3 tests)

**Effort:** ~15 min

---

### Task 2: Create VideoPipelineProgress Class (AC1, AC2)

**Tests:** 2.5-UNIT-004, 2.5-UNIT-005, 2.5-UNIT-006

- [ ] Create [progress.py](file:///d:/Eleven-labs-AI-Video/eleven_video/ui/progress.py)
- [ ] Implement `VideoPipelineProgress.__init__(console: Optional[Console] = None)`
- [ ] Use default console from `eleven_video.ui.console`
- [ ] Initialize instance variables: `current_stage`, `stage_start_times`, `pipeline_start_time`, `total_images`, `completed_images`
- [ ] Export from [ui/__init__.py](file:///d:/Eleven-labs-AI-Video/eleven_video/ui/__init__.py)
- [ ] Run: `python -m pytest tests/ui/test_progress.py::TestVideoPipelineProgressClass -v`
- [ ] ✅ Tests pass (3 tests)

**Effort:** ~20 min

---

### Task 3: Implement Stage Lifecycle (AC2, AC3, AC7)

**Tests:** 2.5-UNIT-007 to 2.5-UNIT-011

- [ ] Implement `start_stage(stage: PipelineStage)` with:
  - Update `current_stage`
  - Record start time in `stage_start_times`
  - Set `pipeline_start_time` if first stage
  - Display stage icon and name using Rich
- [ ] Implement `complete_stage(stage: PipelineStage)` with:
  - Calculate elapsed time from `stage_start_times`
  - Display completion message with elapsed time
- [ ] Run: `python -m pytest tests/ui/test_progress.py::TestStageLifecycle -v`
- [ ] ✅ Tests pass (5 tests)

**Effort:** ~30 min

---

### Task 4: Implement Progress Updates (AC4, AC5)

**Tests:** 2.5-UNIT-012 to 2.5-UNIT-015

- [ ] Implement `update_progress(message: str)` with:
  - Parse "image X of Y" format using regex
  - Update `completed_images` and `total_images`
  - Calculate and display percentage
  - Handle generic messages
- [ ] Display spinner for "Compiling video..." messages
- [ ] Run: `python -m pytest tests/ui/test_progress.py::TestImageProgress tests/ui/test_progress.py::TestCompilationProgress -v`
- [ ] ✅ Tests pass (4 tests)

**Effort:** ~30 min

---

### Task 5: Implement Error Handling (AC6)

**Tests:** 2.5-UNIT-016, 2.5-UNIT-017, 2.5-UNIT-018

- [ ] Implement `fail_stage(stage: PipelineStage, error: str)` with:
  - Update `current_stage` to FAILED
  - Display red Panel with error details
  - Show ❌ failed icon
- [ ] Run: `python -m pytest tests/ui/test_progress.py::TestErrorHandling -v`
- [ ] ✅ Tests pass (3 tests)

**Effort:** ~20 min

---

### Task 6: Implement Summary Display (AC7)

**Tests:** 2.5-UNIT-019 to 2.5-UNIT-022

- [ ] Implement `show_summary(output_path: Path, video: Video)` with:
  - Display green success Panel
  - Include output file path
  - Calculate total elapsed time from `pipeline_start_time`
  - Show video duration and file size
- [ ] Run: `python -m pytest tests/ui/test_progress.py::TestSummaryDisplay -v`
- [ ] ✅ Tests pass (4 tests)

**Effort:** ~20 min

---

### Task 7: Implement Callback Factory (AC1)

**Tests:** 2.5-UNIT-023, 2.5-UNIT-024, 2.5-UNIT-025

- [ ] Implement `create_callback() -> Callable[[str], None]` with:
  - Return closure that calls `update_progress`
  - Compatible with adapter `progress_callback` signature
- [ ] Run: `python -m pytest tests/ui/test_progress.py::TestCallbackFactory -v`
- [ ] ✅ Tests pass (3 tests)

**Effort:** ~10 min

---

## Running Tests

```bash
# Run all failing tests for this story
python -m pytest tests/ui/test_progress.py -v

# Run specific test class
python -m pytest tests/ui/test_progress.py::TestPipelineStageEnum -v

# Run with coverage
python -m pytest tests/ui/test_progress.py --cov=eleven_video.ui.progress --cov-report=term-missing

# Debug specific test
python -m pytest tests/ui/test_progress.py::TestStageLifecycle::test_start_stage_updates_current_stage -v --pdb
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete) ✅

- ✅ 25 tests written covering all 7 acceptance criteria
- ✅ Test fixtures for Console mocking
- ✅ Test factories for Video domain model
- ✅ Tests fail due to missing implementation

### GREEN Phase (DEV Team)

1. Pick one test class from implementation checklist
2. Implement minimal code to make tests pass
3. Run tests to verify green
4. Move to next test class
5. Repeat until all 25 tests pass

### REFACTOR Phase (DEV Team)

1. All tests passing (green)
2. Review code quality
3. Extract common patterns
4. Ensure tests still pass
5. Update story status to 'done'

---

## File Changes Summary

| File | Change | Purpose |
|------|--------|---------|
| [domain.py](file:///d:/Eleven-labs-AI-Video/eleven_video/models/domain.py) | MODIFY | Add PipelineStage enum, STAGE_ICONS dict |
| [progress.py](file:///d:/Eleven-labs-AI-Video/eleven_video/ui/progress.py) | NEW | VideoPipelineProgress class |
| [ui/__init__.py](file:///d:/Eleven-labs-AI-Video/eleven_video/ui/__init__.py) | MODIFY | Export VideoPipelineProgress |
| [test_progress.py](file:///d:/Eleven-labs-AI-Video/tests/ui/test_progress.py) | NEW | 25 unit tests (created) |

---

## Notes

- Use Rich `console.status()` for simple spinners (simpler than `Live`)
- Console singleton from `eleven_video.ui.console import console`
- Progress callbacks from Stories 2.2-2.4 already use `Callable[[str], None]` signature
- Do NOT use `print()` - always use `console.print()` for Rich formatting

---

**Generated by TEA Agent** - 2025-12-16
