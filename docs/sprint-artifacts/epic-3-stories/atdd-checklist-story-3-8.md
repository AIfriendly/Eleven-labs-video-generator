# ATDD Checklist - Epic 3, Story 3.8: Custom Output Resolution Selection

**Date:** 2026-01-05
**Author:** Revenant
**Primary Test Level:** Integration/CLI

---

## Story Summary

Users need to specify the output resolution (1080p, 720p, Portrait, Square) for generated videos to match platform requirements (e.g., TikTok, Instagram). This works via both CLI flags and interactive prompts.

**As a** user
**I want** to specify output resolution settings for my videos
**So that** I can match my video resolution to my specific requirements (e.g., YouTube vs TikTok)

---

## Acceptance Criteria

1. **Given** I am configuring video output, **When** I select a specific resolution (e.g., '1080p', '720p'), **Then** the video is generated at the specified resolution.
2. **Given** I am using the CLI, **When** I pass the `--resolution` flag (e.g., `--resolution 720p`), **Then** the interactive prompt is skipped and the specified resolution is used.
3. **Given** I am in an interactive session (no flag), **When** prompted for resolution, **Then** I see options for "1080p (Landscape)", "720p (Landscape)", "Portrait (9:16)", and "Square (1:1)".
4. **Given** a resolution is selected, **When** the video is compiled, **Then** FFmpeg resizes source images and output video to match the target dimensions.
5. **Given** invalid resolution input passed via CLI, **When** validating, **Then** the system displays an error and exits (or falls back to interactive if possible).
6. **Given** no resolution is specified, **When** generating, **Then** the system defaults to 1080p (1920x1080).

---

## Failing Tests Created (RED Phase)

### E2E / Integration Tests (2 tests)

**File:** `tests/integration/test_resolution_e2e.py`
- ✅ **Test:** `test_generate_video_custom_resolution_e2e`
  - **Status:** RED - ImportError / Missing Implementation
  - **Verifies:** The full CLI-to-Compiler flow delivers the correct resolution instruction.

**File:** `tests/cli/test_resolution_flag.py`
- ✅ **Test:** `test_resolution_flag_valid`
  - **Status:** RED - Missing CLI Option
  - **Verifies:** `-r` / `--resolution` flag is accepted.
- ✅ **Test:** `test_resolution_passed_to_pipeline`
  - **Status:** RED - Pipeline config mismatch
  - **Verifies:** Parsed CLI arg reaches backend config.

### Unit Tests (2 files)

**File:** `tests/ui/test_resolution_selector.py`
- ✅ **Test:** `test_resolution_enum_structure`
  - **Status:** RED - ImportError (Resolution enum missing)
  - **Verifies:** Resolution model exists with correct dimensions.
- ✅ **Test:** `test_selector_interactive_prompt`
  - **Status:** RED - ImportError
  - **Verifies:** Interactive menu options (1080p, 720p, Portrait, Square).
- ✅ **Test:** `test_selector_fallback_defaults`
  - **Status:** RED - ImportError
  - **Verifies:** Default to 1080p.

**File:** `tests/processing/test_ffmpeg_resolution.py`
- ✅ **Test:** `test_video_compiler_accepts_resolution`
  - **Status:** RED - Invalid Argument
  - **Verifies:** `compile_video` accepts `resolution` param.
- ✅ **Test:** `test_ffmpeg_command_generation_portrait`
  - **Status:** RED - Logic missing
  - **Verifies:** Correct `scale` and `crop` filters for vertical video.

---

## Technical Patterns Implementation

### Data Models
- **Enum:** `Resolution` in `eleven_video/models/domain.py`
- **Values:** `HD_1080P`, `HD_720P`, `PORTRAIT`, `SQUARE`

### UI Components
- **Selector:** `ResolutionSelector` in `eleven_video/ui/resolution_selector.py`
- **Library:** `rich` for TUI selection

### FFmpeg Logic
- **Scaling:** `scale=W:H:force_original_aspect_ratio=increase,crop=W:H` matches target aspect ratio.

---

## Implementation Checklist

### Test: `test_resolution_enum_structure`
**File:** `tests/ui/test_resolution_selector.py`

- [ ] Create `Resolution` enum in `eleven_video/models/domain.py`
- [ ] Define members with width/height attributes
- [ ] ✅ Test passes (green phase)

### Test: `test_selector_interactive_prompt` & `test_resolution_flag_valid`
**File:** `tests/ui/test_resolution_selector.py` / `tests/cli/test_resolution_flag.py`

- [ ] Create `eleven_video/ui/resolution_selector.py`
- [ ] Implement `PresentationSelector.select_resolution`
- [ ] Add `resolution` argument to `main.py`
- [ ] Implement flag parsing and fallback to selector
- [ ] ✅ Test passes (green phase)

### Test: `test_ffmpeg_command_generation_portrait` & E2E
**File:** `tests/processing/test_ffmpeg_resolution.py` / `tests/integration/test_resolution_e2e.py`

- [ ] Update `VideoCompiler.compile_video` signature
- [ ] Implement `_get_scale_filter(resolution)` logic
- [ ] Pass `resolution` from `main.py` to `VideoPipeline` to `VideoCompiler`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 4 hours

---

## Running Tests

```bash
# Run all failing tests for this story
pytest tests/ui/test_resolution_selector.py tests/processing/test_ffmpeg_resolution.py tests/cli/test_resolution_flag.py tests/integration/test_resolution_e2e.py

# Run specific test file
pytest tests/ui/test_resolution_selector.py
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete) ✅

**TEA Agent Responsibilities:**
- ✅ All tests written and failing
- ✅ Implementation checklist created

**Verification:**
- Tests fail due to missing modules (`eleven_video.ui.resolution_selector`, `eleven_video.models.domain.Resolution`) or arguments.

---

## Next Steps

1. **Review this checklist** with team.
2. **Begin implementation** starting with `Resolution` enum.
3. **Execute Unit Tests** first (`test_resolution_selector.py`), then Integration.
4. **Refactor** once GREEN.

---

**Generated by BMad TEA Agent** - 2026-01-05
