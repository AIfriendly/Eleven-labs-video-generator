# ATDD Checklist - Epic 2, Story 2.7: Apply Subtle Zoom Effects

**Date:** 2025-12-17
**Author:** Revenant
**Primary Test Level:** Unit Tests

---

## Story Summary

Apply Ken Burns-style zoom effects to images during video compilation to make videos appear dynamic and non-generic.

**As a** user,
**I want** the system to apply subtle zoom effects to images during video compilation,
**So that** the video appears dynamic and non-generic.

---

## Acceptance Criteria

1. Subtle zoom-in or zoom-out effects are applied to each image during compilation
2. Alternating images receive zoom-in and zoom-out effects for visual variety
3. Zoom is gradual over the clip duration (Ken Burns style)
4. Effect is subtle (5-10% scale change) and not disorienting
5. Zoom effects are applied by default without additional configuration
6. System falls back to static image on zoom error
7. 1920x1080 16:9 output resolution is maintained

---

## Failing Tests Created (RED Phase)

### Unit Tests (16 tests)

**File:** `tests/processing/test_video_handler.py` (1042 lines)

#### TestZoomEffectApplication (AC1, AC3, AC4)
- ✅ **Test:** `test_apply_zoom_effect_method_exists` [2.7-UNIT-001]
  - **Status:** RED - `_apply_zoom_effect` method doesn't exist
  - **Verifies:** AC1 - Zoom effect method available

- ✅ **Test:** `test_zoom_scale_factor_constant_exists` [2.7-UNIT-002]
  - **Status:** RED - `ZOOM_SCALE_FACTOR` constant missing
  - **Verifies:** AC4 - Subtle 5-10% zoom factor

- ✅ **Test:** `test_apply_zoom_effect_uses_fl_method` [2.7-UNIT-003]
  - **Status:** RED - fl() not called (method doesn't exist)
  - **Verifies:** AC3 - Ken Burns style via frame-level transform

- ✅ **Test:** `test_apply_zoom_effect_zoom_in_direction` [2.7-UNIT-004]
  - **Status:** RED - Method doesn't accept direction parameter
  - **Verifies:** AC1 - Zoom-in direction works

- ✅ **Test:** `test_apply_zoom_effect_zoom_out_direction` [2.7-UNIT-005]
  - **Status:** RED - Method doesn't accept direction parameter
  - **Verifies:** AC1 - Zoom-out direction works

#### TestZoomAlternation (AC2)
- ✅ **Test:** `test_alternating_zoom_directions_in_create_image_clips` [2.7-UNIT-006]
  - **Status:** RED - No zoom alternation implemented
  - **Verifies:** AC2 - Images alternate in/out

- ✅ **Test:** `test_single_image_uses_zoom_in` [2.7-UNIT-007]
  - **Status:** RED - No zoom applied
  - **Verifies:** AC2 - Single image gets zoom-in

#### TestZoomDefaultEnabled (AC5)
- ✅ **Test:** `test_compile_video_has_enable_zoom_parameter` [2.7-UNIT-008]
  - **Status:** RED - `enable_zoom` parameter missing
  - **Verifies:** AC5 - Parameter exists with default True

- ✅ **Test:** `test_zoom_applied_by_default` [2.7-UNIT-009]
  - **Status:** RED - No zoom applied by default
  - **Verifies:** AC5 - Zoom on without explicit config

- ✅ **Test:** `test_zoom_disabled_when_enable_zoom_false` [2.7-UNIT-010]
  - **Status:** RED - Unexpected keyword argument
  - **Verifies:** AC5 - Can disable zoom

#### TestZoomFallbackHandling (AC6)
- ✅ **Test:** `test_fallback_to_static_on_zoom_error` [2.7-UNIT-011]
  - **Status:** RED - No fallback handling
  - **Verifies:** AC6 - Falls back to static

- ✅ **Test:** `test_fallback_logs_warning_via_progress_callback` [2.7-UNIT-012]
  - **Status:** RED - No warning logged
  - **Verifies:** AC6 - Warning via callback

#### TestZoomResolutionMaintenance (AC7)
- ✅ **Test:** `test_zoom_output_resolution_1920x1080` [2.7-UNIT-013]
  - **Status:** RED - Resolution not verified after zoom
  - **Verifies:** AC7 - 1920x1080 maintained

- ✅ **Test:** `test_zoom_effect_does_not_call_resized` [2.7-UNIT-014]
  - **Status:** RED - resized() still called
  - **Verifies:** AC7 - Zoom handles resolution internally

#### TestZoomIntegration
- ✅ **Test:** `test_compile_video_with_zoom_returns_video` [2.7-UNIT-015]
  - **Status:** PASS - Existing functionality
  - **Verifies:** Integration - Video returned

- ✅ **Test:** `test_compile_video_progress_callback_with_zoom` [2.7-UNIT-016]
  - **Status:** PASS - Existing functionality
  - **Verifies:** Integration - Progress works

---

## Data Factories Created

### Existing Factories (Reused)

**File:** `tests/processing/test_video_handler.py`

**Exports:**
- `create_test_image(size_bytes=1000)` - Create single test Image
- `create_test_images(count=3)` - Create array of test Images
- `create_test_audio(duration=10.0)` - Create test Audio

---

## Fixtures Created

### Zoom Effect Fixture

**File:** `tests/processing/test_video_handler.py`

**Fixtures:**
- `mock_moviepy_zoom` - Extended moviepy mock with fl() method
  - **Setup:** Patches ImageClip, AudioFileClip, concatenate_videoclips
  - **Provides:** mock_image_clip, mock_audio_clip, mock_concat, mock_clip
  - **Key:** mock_clip.fl = MagicMock(return_value=mock_clip)
  - **Cleanup:** Context manager handles teardown

---

## Mock Requirements

### moviepy fl() Method

**Method:** `clip.fl(filter_func)`

**Purpose:** Frame-level transformation for Ken Burns zoom effect

**Mock Setup:**
```python
mock_clip.fl = MagicMock(return_value=mock_clip)
```

**Error Simulation:**
```python
mock_clip.fl.side_effect = RuntimeError("Zoom calculation failed")
```

---

## Required Constants

### FFmpegVideoCompiler Class

- `ZOOM_SCALE_FACTOR = 1.08` - 8% zoom (subtle, within 5-10% range)

---

## Implementation Checklist

### Test: _apply_zoom_effect method exists [2.7-UNIT-001]

**File:** `eleven_video/processing/video_handler.py`

**Tasks to make this test pass:**
- [ ] Add `ZOOM_SCALE_FACTOR = 1.08` class constant
- [ ] Create `_apply_zoom_effect(self, clip, zoom_direction)` method
- [ ] Run test: `uv run pytest tests/processing/test_video_handler.py -k "test_apply_zoom_effect_method_exists"`
- [ ] ✅ Test passes (green phase)

---

### Test: ZOOM_SCALE_FACTOR constant [2.7-UNIT-002]

**Tasks to make this test pass:**
- [ ] Add `ZOOM_SCALE_FACTOR = 1.08` (already done above)
- [ ] Verify value is between 1.05 and 1.10
- [ ] Run test: `uv run pytest tests/processing/test_video_handler.py -k "test_zoom_scale_factor_constant_exists"`
- [ ] ✅ Test passes (green phase)

---

### Test: fl() method usage [2.7-UNIT-003]

**Tasks to make this test pass:**
- [ ] Implement zoom transformation using `clip.fl(zoom_effect)`
- [ ] Create inner function for frame-level zoom calculation
- [ ] Run test: `uv run pytest tests/processing/test_video_handler.py -k "test_apply_zoom_effect_uses_fl_method"`
- [ ] ✅ Test passes (green phase)

---

### Test: enable_zoom parameter [2.7-UNIT-008]

**Tasks to make this test pass:**
- [ ] Add `enable_zoom: bool = True` to `compile_video()` signature
- [ ] Pass `enable_zoom` to `_create_image_clips()`
- [ ] Run test: `uv run pytest tests/processing/test_video_handler.py -k "test_compile_video_has_enable_zoom_parameter"`
- [ ] ✅ Test passes (green phase)

---

### Test: Alternation logic [2.7-UNIT-006]

**Tasks to make this test pass:**
- [ ] Modify `_create_image_clips()` to call `_apply_zoom_effect()`
- [ ] Use `"in" if i % 2 == 0 else "out"` for alternation
- [ ] Run test: `uv run pytest tests/processing/test_video_handler.py -k "test_alternating_zoom_directions"`
- [ ] ✅ Test passes (green phase)

---

### Test: Fallback handling [2.7-UNIT-011, 2.7-UNIT-012]

**Tasks to make this test pass:**
- [ ] Wrap zoom in try/except in `_create_image_clips()`
- [ ] Fall back to `resized()` on exception
- [ ] Log warning via progress_callback
- [ ] Run test: `uv run pytest tests/processing/test_video_handler.py -k "test_fallback"`
- [ ] ✅ Tests pass (green phase)

---

### Test: Resolution maintenance [2.7-UNIT-013, 2.7-UNIT-014]

**Tasks to make this test pass:**
- [ ] Implement center-crop in zoom_effect function
- [ ] Output frames at OUTPUT_RESOLUTION (1920x1080)
- [ ] Don't call `resized()` when zoom is enabled
- [ ] Run test: `uv run pytest tests/processing/test_video_handler.py -k "test_zoom_output_resolution"`
- [ ] ✅ Tests pass (green phase)

---

## Running Tests

```bash
# Run all Story 2.7 zoom tests
uv run pytest tests/processing/test_video_handler.py -k "Zoom" -v

# Run specific test class
uv run pytest tests/processing/test_video_handler.py::TestZoomEffectApplication -v

# Run single test
uv run pytest tests/processing/test_video_handler.py -k "test_apply_zoom_effect_method_exists" -v

# Run with coverage
uv run pytest tests/processing/test_video_handler.py -k "Zoom" --cov=eleven_video/processing/video_handler

# Debug mode
uv run pytest tests/processing/test_video_handler.py -k "Zoom" -v -s
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete) ✅

**TEA Agent Responsibilities:**
- ✅ All 16 tests written and failing (12 fail, 4 pass - expected)
- ✅ Fixture `mock_moviepy_zoom` created with fl() method
- ✅ Existing factories reused
- ✅ Mock requirements documented
- ✅ Implementation checklist created

**Verification:**
```
=============== 12 failed, 4 passed, 20 deselected in 4.48s ===============
```
- Failures due to `TypeError: FFmpegVideoCompiler.compile_video() got an unexpected keyword argument 'enable_zoom'`
- This is correct RED phase behavior

---

### GREEN Phase (DEV Team - Next Steps)

**DEV Agent Responsibilities:**

1. **Add constant and method** (Tasks 1, 2)
   - Add `ZOOM_SCALE_FACTOR = 1.08`
   - Create `_apply_zoom_effect(clip, direction)` method

2. **Modify compile_video signature** (Task 2)
   - Add `enable_zoom: bool = True` parameter
   - Pass to `_create_image_clips()`

3. **Implement zoom in _create_image_clips** (Task 2)
   - Call `_apply_zoom_effect()` with alternating directions
   - Remove `resized()` call when zoom enabled

4. **Add fallback handling** (Task 3)
   - Wrap zoom in try/except
   - Fall back to static image
   - Log warning

5. **Run tests after each change**
   - One test at a time → green
   - `uv run pytest tests/processing/test_video_handler.py -k "Zoom" -v`

---

### REFACTOR Phase (After All Tests Pass)

1. Verify all tests pass
2. Optimize zoom_effect function if needed
3. Ensure existing tests still pass
4. Consider extracting zoom logic if complex

---

## Next Steps

1. **Review this checklist** with Story 2.7 context
2. **Run failing tests** to confirm RED phase: `uv run pytest tests/processing/test_video_handler.py -k "Zoom" -v`
3. **Begin implementation** using checklist as guide
4. **Work one test at a time** (red → green)
5. **When all tests pass**, refactor and update story status

---

## Knowledge Base References Applied

- **data-factories.md** - Reused existing factories
- **fixture-architecture.md** - Extended mock fixture with fl() method
- **test-quality.md** - Given-When-Then format, one assertion per test
- **component-tdd.md** - Frame-level testing patterns

---

## Test Execution Evidence

### Initial Test Run (RED Phase Verification)

**Command:** `uv run pytest tests/processing/test_video_handler.py -k "Zoom" -v --tb=line`

**Results:**
```
=============== 12 failed, 4 passed, 20 deselected in 4.48s ===============
```

**Summary:**
- Total tests: 16
- Passing: 4 (expected - test existing behavior)
- Failing: 12 (expected - test new behavior)
- Status: ✅ RED phase verified

**Primary Failure Message:**
```
TypeError: FFmpegVideoCompiler.compile_video() got an unexpected keyword argument 'enable_zoom'
```

---

## Notes

- Tests 2.7-UNIT-015 and 2.7-UNIT-016 pass because they test existing behavior (Video return, progress callback)
- The `mock_moviepy_zoom` fixture extends the existing pattern with `fl()` method
- The story provides detailed implementation code in Developer Context section

---

**Generated by BMad TEA Agent** - 2025-12-17
