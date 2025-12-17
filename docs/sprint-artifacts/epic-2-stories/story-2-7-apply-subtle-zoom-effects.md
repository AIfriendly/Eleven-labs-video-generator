# Story 2.7: Apply Subtle Zoom Effects

Status: done

## 1. Story

**As a** user,
**I want** the system to apply subtle zoom effects to images during video compilation,
**so that** the video appears dynamic and non-generic.

## 2. Acceptance Criteria

1. **Given** I have images for my video,
   **When** the video compilation runs,
   **Then** subtle zoom-in or zoom-out effects are applied to each image.

2. **Given** images are being compiled,
   **When** zoom effects are applied,
   **Then** alternating images receive zoom-in and zoom-out effects for visual variety.

3. **Given** a zoom effect is applied,
   **When** the clip is rendered,
   **Then** the zoom is gradual over the clip duration (Ken Burns style).

4. **Given** the zoom effect is applied,
   **When** the video plays,
   **Then** the effect is subtle (5-10% scale change) and not disorienting.

5. **Given** zoom effects are enabled by default,
   **When** the user runs `eleven-video generate`,
   **Then** zoom effects are applied without requiring additional configuration.

6. **Given** a compile request,
   **When** an error occurs during zoom effect application,
   **Then** the system falls back to a static image (no zoom) for that clip.

7. **Given** zoom effects are applied,
   **When** the video is compiled,
   **Then** the 1920x1080 16:9 output resolution is maintained.

## 3. Developer Context

### Technical Requirements

- **Primary Goal:** Enhance `FFmpegVideoCompiler._create_image_clips()` to apply Ken Burns-style zoom effects
- **Location:** Modify `eleven_video/processing/video_handler.py`
- **Pattern:** Time-based frame transformation using moviepy's `fl` (frame-level) method
- **FR Coverage:** FR10 (subtle zoom effects), FR9 (professional video editing)
- **New Constant:** Add `ZOOM_SCALE_FACTOR = 1.08` alongside existing `OUTPUT_RESOLUTION`

> [!IMPORTANT]
> **Subtle Effects Only:** Zoom should be 5-10% scale change (e.g., 1.0 → 1.08). Aggressive zooms appear unprofessional.

> [!CAUTION]
> **Maintain Resolution:** Final output must remain 1920x1080. The effect crops into a slightly larger scaled image, then crops back to output resolution.

> [!WARNING]
> **Resize Order:** Do NOT call `clip.resized()` before `_apply_zoom_effect()`. The zoom effect already outputs at `OUTPUT_RESOLUTION` via center-crop. Double resize causes quality degradation.

### Performance Considerations

- **Frame-level processing:** `fl()` runs per-frame (24 frames/second). For a 10-second clip = 240 operations.
- **ImageClip optimization:** Moviepy caches static frames internally, so zoom calculations happen once per unique time value.
- **PIL operation:** Single resize + crop per frame is efficient; avoid nested transforms.

### Architectural Boundaries

- **Hexagonal Architecture:** Processing layer modification only
- **No New Dependencies:** Use existing moviepy capabilities
- **Backward Compatibility:** Existing tests must continue passing

### Zoom Effect Implementation

**File:** `eleven_video/processing/video_handler.py`

The Ken Burns effect is achieved by:
1. Starting with an oversized image (e.g., 110% of target resolution)
2. Gradually changing zoom scale over the clip duration
3. Cropping to final 1920x1080 resolution

```python
def _apply_zoom_effect(
    self,
    clip: ImageClip,
    zoom_direction: str = "in"  # "in" or "out"
) -> ImageClip:
    """Apply Ken Burns-style zoom effect to an image clip.
    
    Args:
        clip: The base ImageClip to apply the effect to.
        zoom_direction: "in" for zoom-in, "out" for zoom-out.
        
    Returns:
        Modified clip with zoom effect applied.
    """
    # Zoom parameters (subtle 5-8% change) - use class constant
    zoom_factor = self.ZOOM_SCALE_FACTOR  # 1.08
    if zoom_direction == "in":
        start_scale, end_scale = 1.0, zoom_factor
    else:
        start_scale, end_scale = zoom_factor, 1.0
    
    w, h = self.OUTPUT_RESOLUTION
    duration = clip.duration
    
    def zoom_effect(get_frame, t):
        """Apply zoom for frame at time t."""
        # Linear interpolation of scale
        progress = t / duration if duration > 0 else 0
        scale = start_scale + (end_scale - start_scale) * progress
        
        # Calculate dimensions for scaled frame
        new_w, new_h = int(w * scale), int(h * scale)
        
        # Get frame and resize
        frame = get_frame(t)
        # Use PIL or numpy/scipy for resize
        from PIL import Image
        import numpy as np
        
        img = Image.fromarray(frame)
        img_scaled = img.resize((new_w, new_h), Image.LANCZOS)
        
        # Center crop to output resolution
        x_off = (new_w - w) // 2
        y_off = (new_h - h) // 2
        img_cropped = img_scaled.crop((x_off, y_off, x_off + w, y_off + h))
        
        return np.array(img_cropped)
    
    # Note: apply_to parameter not needed for ImageClip without mask
    return clip.fl(zoom_effect)
```

### Modified compile_video Signature

```python
# In compile_video(), add enable_zoom parameter and pass to _create_image_clips:
def compile_video(
    self,
    images: List[Image],
    audio: Audio,
    output_path: Path,
    progress_callback: Optional[Callable[[str], None]] = None,
    enable_zoom: bool = True  # NEW: expose zoom toggle
) -> Video:
    # ... existing code ...
    clips = self._create_image_clips(
        image_paths, duration_per_image, progress_callback, enable_zoom=enable_zoom
    )
```

### Modified _create_image_clips Method

```python
def _create_image_clips(
    self,
    image_paths: List[str],
    duration_per_image: float,
    progress_callback: Optional[Callable[[str], None]],
    enable_zoom: bool = True  # NEW: Default True
) -> List:
    """Create video clips from images with optional zoom effects.
    
    Args:
        image_paths: Paths to image files.
        duration_per_image: Duration each image should display.
        progress_callback: Optional progress callback.
        enable_zoom: Whether to apply Ken Burns zoom effects.
        
    Returns:
        List of ImageClip objects.
    """
    clips = []
    total = len(image_paths)
    
    for i, path in enumerate(image_paths):
        if progress_callback:
            progress_callback(f"Processing image {i + 1} of {total}")
        
        try:
            # Create clip, set duration
            clip = ImageClip(path)
            clip = clip.with_duration(duration_per_image)
            
            # Apply zoom effect (alternate in/out)
            # NOTE: Do NOT resize before zoom - zoom handles output resolution
            if enable_zoom:
                zoom_direction = "in" if i % 2 == 0 else "out"
                clip = self._apply_zoom_effect(clip, zoom_direction)
            else:
                # Only resize if NOT zooming (zoom handles resolution internally)
                clip = clip.resized(newsize=self.OUTPUT_RESOLUTION)
            
            clips.append(clip)
        except Exception as e:
            # Fallback: static image (AC6)
            if progress_callback:
                progress_callback(f"Warning: zoom failed for image {i + 1}, using static")
            clip = ImageClip(path)
            clip = clip.with_duration(duration_per_image)
            clip = clip.resized(newsize=self.OUTPUT_RESOLUTION)
            clips.append(clip)
    
    return clips
```

### Testing Requirements

| Category | Tests |
|----------|-------|
| Zoom In | Single image with zoom-in produces scaled frames |
| Zoom Out | Single image with zoom-out produces scaled frames |
| Alternation | Multiple images alternate zoom directions |
| Resolution | Output remains 1920x1080 after zoom |
| Fallback | Zoom exception falls back to static image |
| Integration | Full compile with zoom produces valid video |

### Previous Story Intelligence

**From Story 2.4:**
- `_create_image_clips()` already creates clips with duration and resize
- `OUTPUT_RESOLUTION = (1920, 1080)` constant exists
- Progress callback pattern established
- Uses `ImageClip.resized()` and `with_duration()`

**From Story 2.6:**
- `VideoPipeline` orchestrates compilation via `FFmpegVideoCompiler`
- No changes needed to orchestrator; zoom is internal to compiler

### Test Mock Pattern Guidance

Existing tests use this mock chain:
```python
mock_image_clip.return_value.set_duration.return_value.resize.return_value = mock_clip
```

For zoom tests, you'll need to mock `clip.fl()` to return a modified clip. Add:
```python
# In mock fixture, after creating mock_clip:
mock_clip.fl = MagicMock(return_value=mock_clip)
```

### Key Implementation Details

1. **Scale Range:** Use class constant `ZOOM_SCALE_FACTOR = 1.08` (8% zoom) for subtle effect
2. **Alternation:** Even-indexed images zoom in, odd zoom out
3. **Centering:** Always center-crop to maintain focus
4. **Performance:** `fl()` runs per-frame, keep operations efficient
5. **Fallback:** On any zoom exception, use static image silently

### References

- [Source: docs/epics.md#Epic-2-Story-2.7](file:///d:/Eleven-labs-AI-Video/docs/epics.md) - FR10 requirement
- [Source: docs/architecture/core-architectural-decisions.md](file:///d:/Eleven-labs-AI-Video/docs/architecture/core-architectural-decisions.md) - Hexagonal architecture
- [Source: eleven_video/processing/video_handler.py](file:///d:/Eleven-labs-AI-Video/eleven_video/processing/video_handler.py) - Existing video compiler

## 4. Tasks

- [x] **Task 1: Add zoom constant and effect method** (AC: 1, 3, 4, 7)
  - [x] Add `ZOOM_SCALE_FACTOR = 1.08` class constant
  - [x] Create `_apply_zoom_effect(clip, zoom_direction)` method
  - [x] Implement Ken Burns style with scale change using constant
  - [x] Use PIL/numpy for frame transformation via moviepy `fl()`

- [x] **Task 2: Modify compile_video and _create_image_clips** (AC: 2, 5)
  - [x] Add `enable_zoom: bool = True` to `compile_video()` signature
  - [x] Pass `enable_zoom` to `_create_image_clips()`
  - [x] Apply alternating zoom directions (even=in, odd=out)
  - [x] Remove `resized()` call when zoom is enabled (zoom handles resolution)
  - [x] Keep `resized()` in else branch when zoom is disabled

- [x] **Task 3: Add fallback handling** (AC: 6)
  - [x] Wrap zoom application in try/except
  - [x] Fall back to static clip on any zoom error
  - [x] Log warning via progress_callback

- [x] **Task 4: Write unit tests**
  - [x] Add `mock_clip.fl = MagicMock(return_value=mock_clip)` to fixture
  - [x] Test zoom-in effect produces scaled frames
  - [x] Test zoom-out effect produces scaled frames
  - [x] Test alternation logic (even/odd)
  - [x] Test output resolution remains 1920x1080
  - [x] Test fallback on zoom error
  - [x] Test `enable_zoom=False` uses `resized()` instead

- [x] **Task 5: Integration verification**
  - [x] Run existing video_handler tests (ensure no regression)
  - [x] Test full pipeline with `eleven-video generate` (tests pass, ready for manual verification)
  - [x] All 36 tests passing

## 5. Dev Agent Record

### Agent Model Used

Gemini 2.5 Pro

### Completion Notes

**Implementation Summary:**
- Added `ZOOM_SCALE_FACTOR = 1.08` class constant (8% zoom, within 5-10% subtle range)
- Created `_apply_zoom_effect(clip, zoom_direction)` method using moviepy's `fl()` for frame-level Ken Burns zoom
- Modified `compile_video()` to accept `enable_zoom: bool = True` parameter
- Updated `_create_image_clips()` with alternating zoom directions (even=in, odd=out) and try/except fallback
- Zoom uses PIL for high-quality LANCZOS resize and center-crop to maintain 1920x1080 output

**Test Updates:**
- All 16 Story 2.7 zoom tests pass
- Updated `mock_moviepy` fixture to support both legacy `set_duration()` and modern `with_duration()` APIs
- Updated 3 legacy tests to use `with_duration` API and work with zoom-enabled default
- All 36 video handler tests pass with no regressions

### Change Log

| Date | Change |
|------|--------|
| 2025-12-17 | Implemented Ken Burns zoom effects (AC1-AC7) |
| 2025-12-17 | Added ZOOM_SCALE_FACTOR constant and _apply_zoom_effect method |
| 2025-12-17 | Added enable_zoom parameter to compile_video |
| 2025-12-17 | Updated legacy tests to work with with_duration API |
| 2025-12-17 | Code review: Fixed zoom-out quality, narrowed exceptions, added type hints |

### File List

| File | Change |
|------|--------|
| `eleven_video/processing/video_handler.py` | MODIFY - add ZOOM_SCALE_FACTOR, _apply_zoom_effect method, enable_zoom param, fallback handling |
| `tests/processing/test_video_handler.py` | MODIFY - add zoom tests, update mock_moviepy fixture, fix legacy tests |

## 6. Senior Developer Review (AI)

**Review Date:** 2025-12-17
**Review Outcome:** ✅ Approved (all issues fixed)

### Issues Found and Fixed

| Severity | Issue | Fix |
|----------|-------|-----|
| HIGH | Zoom-out quality loss from upscaling | Pre-upscale source to max scale before shrinking |
| MEDIUM | Module docstring outdated | Updated to include Story 2.7 |
| MEDIUM | Exception too broad | Narrowed to specific exception types |
| LOW | Missing type hints | Added ImageClip type hints |
| LOW | Unused exception variable | Removed unused `e` variable |

**All 36 tests pass after fixes.**
