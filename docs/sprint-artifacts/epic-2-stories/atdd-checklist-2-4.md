# ATDD Checklist - Epic 2, Story 2.4: Video Compilation from Assets

**Date:** 2025-12-16
**Author:** Murat (TEA) / Revenant
**Primary Test Level:** Unit Tests (mocked moviepy)

---

## Story Summary

Compile generated audio and images into a synchronized MP4 video using moviepy/FFmpeg.

**As a** user
**I want** the system to compile the generated script, audio, and images into a single video file
**So that** I have a complete video for my original prompt

---

## Acceptance Criteria

1. **AC1:** MP4 video created combining images and audio, synchronized
2. **AC2:** Images displayed sequentially matching audio duration with smooth transitions
3. **AC3:** Images evenly spaced, ~3-4 seconds each (per FR11)
4. **AC4:** Progress updates shown during compilation
5. **AC5:** Output is 16:9 (1920x1080), H.264/AAC encoded
6. **AC6:** Clear errors for failures, no partial files left behind
7. **AC7:** `Video` domain model returned with file path, duration, file size

---

## Failing Tests Created (RED Phase)

### Unit Tests (20 tests)

**File:** `tests/processing/test_video_handler.py` (~400 lines)

#### Success Path Tests (AC1, AC2, AC3, AC5, AC7)

- ✅ **Test:** `test_compile_video_returns_video_domain_model`
  - **Status:** RED - `Video` domain model not implemented
  - **Verifies:** AC1, AC7 - Returns Video with file_path, duration, file_size

- ✅ **Test:** `test_compile_video_creates_mp4_file`
  - **Status:** RED - `FFmpegVideoCompiler` not implemented
  - **Verifies:** AC1 - Creates MP4 file at output_path

- ✅ **Test:** `test_compile_video_uses_h264_codec`
  - **Status:** RED - Compiler not implemented
  - **Verifies:** AC5 - Uses libx264 codec parameter

- ✅ **Test:** `test_compile_video_uses_aac_audio_codec`
  - **Status:** RED - Compiler not implemented
  - **Verifies:** AC5 - Uses AAC audio codec

- ✅ **Test:** `test_compile_video_output_resolution_1920x1080`
  - **Status:** RED - Compiler not implemented
  - **Verifies:** AC5 - Output is 1920x1080 resolution

- ✅ **Test:** `test_compile_video_output_is_24fps`
  - **Status:** RED - Compiler not implemented
  - **Verifies:** AC5 - Output framerate is 24fps

- ✅ **Test:** `test_video_duration_matches_audio_duration`
  - **Status:** RED - Compiler not implemented
  - **Verifies:** AC1 - Video duration equals audio duration

#### Image Distribution Tests (AC2, AC3)

- ✅ **Test:** `test_images_evenly_distributed_across_audio`
  - **Status:** RED - Compiler not implemented
  - **Verifies:** AC3 - Each image gets `audio_duration / num_images` seconds

- ✅ **Test:** `test_single_image_fills_entire_duration`
  - **Status:** RED - Compiler not implemented
  - **Verifies:** AC3 edge case - Single image fills full audio duration

- ✅ **Test:** `test_many_images_distributed_correctly`
  - **Status:** RED - Compiler not implemented
  - **Verifies:** AC3 edge case - 10 images at 30s audio = 3s each

#### Progress Callback Tests (AC4)

- ✅ **Test:** `test_progress_callback_invoked_per_image`
  - **Status:** RED - Compiler not implemented
  - **Verifies:** AC4 - "Processing image X of Y" for each image

- ✅ **Test:** `test_progress_callback_shows_compiling_message`
  - **Status:** RED - Compiler not implemented
  - **Verifies:** AC4 - "Compiling video..." before write

- ✅ **Test:** `test_no_error_when_progress_callback_is_none`
  - **Status:** RED - Compiler not implemented
  - **Verifies:** AC4 - Optional callback gracefully handled

#### Validation Tests (AC6)

- ✅ **Test:** `test_empty_images_raises_validation_error`
  - **Status:** RED - `ValidationError` handling not implemented
  - **Verifies:** AC6 - Empty images list raises ValidationError

- ✅ **Test:** `test_empty_audio_raises_validation_error`
  - **Status:** RED - Validation not implemented
  - **Verifies:** AC6 - Empty audio data raises ValidationError

- ✅ **Test:** `test_none_audio_raises_validation_error`
  - **Status:** RED - Validation not implemented
  - **Verifies:** AC6 - None audio raises ValidationError

#### Error Handling Tests (AC6)

- ✅ **Test:** `test_ffmpeg_missing_raises_video_processing_error`
  - **Status:** RED - `VideoProcessingError` not implemented
  - **Verifies:** AC6 - FFmpeg not found shows helpful error

- ✅ **Test:** `test_permission_denied_raises_video_processing_error`
  - **Status:** RED - Error handling not implemented
  - **Verifies:** AC6 - Permission errors show clear message

- ✅ **Test:** `test_temp_files_cleaned_on_success`
  - **Status:** RED - Cleanup not implemented
  - **Verifies:** AC6 - No temp files left after success

- ✅ **Test:** `test_temp_files_cleaned_on_failure`
  - **Status:** RED - Cleanup not implemented
  - **Verifies:** AC6 - No temp files left after failure

---

## Data Factories Created

### Image Factory

**File:** `tests/processing/test_video_handler.py` (inline fixtures)

```python
def create_test_image(size_bytes: int = 1000) -> Image:
    """Create test Image domain model with fake PNG bytes."""
    return Image(
        data=b"\\x89PNG\\r\\n\\x1a\\n" + b"\\x00" * size_bytes,
        mime_type="image/png",
        file_size_bytes=size_bytes + 8
    )

def create_test_images(count: int = 3) -> List[Image]:
    """Create multiple test images."""
    return [create_test_image() for _ in range(count)]
```

### Audio Factory

```python
def create_test_audio(duration: float = 10.0) -> Audio:
    """Create test Audio domain model with fake MP3 bytes."""
    return Audio(
        data=b"\\xff\\xfb\\x90\\x00" + b"\\x00" * 100,
        duration_seconds=duration,
        file_size_bytes=104
    )
```

---

## Fixtures Created

### Moviepy Mock Fixtures

**File:** `tests/processing/test_video_handler.py` (inline)

```python
@pytest.fixture
def mock_moviepy():
    """Mock moviepy for unit tests."""
    with patch("moviepy.editor.ImageClip") as mock_image_clip, \\
         patch("moviepy.editor.AudioFileClip") as mock_audio_clip, \\
         patch("moviepy.editor.concatenate_videoclips") as mock_concat:
        
        mock_clip = MagicMock()
        mock_clip.duration = 10.0
        mock_clip.w = 1920
        mock_clip.h = 1080
        mock_clip.write_videofile = MagicMock()
        
        mock_image_clip.return_value.set_duration.return_value.resize.return_value = mock_clip
        mock_audio_clip.return_value.duration = 10.0
        mock_concat.return_value = mock_clip
        
        yield mock_image_clip, mock_audio_clip, mock_concat, mock_clip

@pytest.fixture
def mock_moviepy_error():
    """Mock moviepy that raises errors."""
    with patch("moviepy.editor.ImageClip") as mock_image_clip:
        def set_error(error):
            mock_image_clip.side_effect = error
        yield mock_image_clip, set_error
```

---

## Mock Requirements

### Moviepy Mock

**Purpose:** Avoid FFmpeg dependency in unit tests

**Mocked Classes:**
- `moviepy.editor.ImageClip` - Image to video clip conversion
- `moviepy.editor.AudioFileClip` - Audio loading from bytes
- `moviepy.editor.concatenate_videoclips` - Clip concatenation

**Success Behavior:**
- `ImageClip.return_value.set_duration.return_value.resize.return_value` → MagicMock clip
- `concatenate_videoclips.return_value.write_videofile` → No error

**Failure Behavior:**
- `ImageClip.side_effect = OSError("FFmpeg not found")` → Triggers VideoProcessingError

---

## Implementation Checklist

### Task 1: Add moviepy dependency (AC1)

**File:** `pyproject.toml`

- [ ] Add `moviepy>=1.0.3` to dependencies
- [ ] Run `uv pip install -e ".[dev]"`
- [ ] Verify import works: `python -c "import moviepy"`

**Estimated Effort:** 0.25 hours

---

### Task 2: Create Video domain model (AC7)

**File:** `eleven_video/models/domain.py`

- [ ] Add `Video` dataclass with `file_path: Path`, `duration_seconds: float`, `file_size_bytes: int`
- [ ] Include `codec: str = "h264"` and `resolution: tuple = (1920, 1080)` defaults
- [ ] Run test: `pytest tests/processing/test_video_handler.py::TestVideoDomainModel -v`
- [ ] ✅ Domain model tests pass

**Estimated Effort:** 0.25 hours

---

### Task 3: Add VideoCompiler protocol (AC1)

**File:** `eleven_video/api/interfaces.py`

- [ ] Add `VideoCompiler` protocol with `compile_video()` method
- [ ] Signature: `compile_video(images: List[Image], audio: Audio, output_path: Path, progress_callback: Optional[Callable[[str], None]] = None) -> Video`
- [ ] Run test: `pytest tests/processing/test_video_handler.py::TestVideoCompilerProtocol -v`
- [ ] ✅ Protocol tests pass

**Estimated Effort:** 0.25 hours

---

### Task 4: Add VideoProcessingError exception (AC6)

**File:** `eleven_video/exceptions/custom_errors.py`

- [ ] Add `VideoProcessingError(Exception)` class
- [ ] Include message parameter with default
- [ ] Export from `eleven_video/exceptions/__init__.py`
- [ ] Run test: `pytest tests/processing/test_video_handler.py::TestVideoProcessingError -v`
- [ ] ✅ Exception tests pass

**Estimated Effort:** 0.25 hours

---

### Task 5: Implement FFmpegVideoCompiler class (AC1, AC2, AC3, AC5)

**File:** `eleven_video/processing/video_handler.py`

- [ ] Create `FFmpegVideoCompiler` class implementing `VideoCompiler`
- [ ] Implement `compile_video()` method
- [ ] Use `tempfile.TemporaryDirectory` for image/audio temp files
- [ ] Create `ImageClip` for each image, set duration to `audio.duration_seconds / len(images)`
- [ ] Resize clips to 1920x1080
- [ ] Concatenate clips with `concatenate_videoclips()`
- [ ] Set audio from `AudioFileClip`
- [ ] Write with `codec="libx264"`, `audio_codec="aac"`, `fps=24`
- [ ] Return `Video` with metadata
- [ ] Run test: `pytest tests/processing/test_video_handler.py::TestCompileVideoSuccess -v`
- [ ] ✅ Success path tests pass

**Estimated Effort:** 2.0 hours

---

### Task 6: Add progress callback support (AC4)

**File:** `eleven_video/processing/video_handler.py`

- [ ] Call `progress_callback(f"Processing image {i+1} of {len(images)}")` per image
- [ ] Call `progress_callback("Compiling video...")` before `write_videofile`
- [ ] Handle `None` callback gracefully
- [ ] Run test: `pytest tests/processing/test_video_handler.py::TestProgressCallback -v`
- [ ] ✅ Progress tests pass

**Estimated Effort:** 0.5 hours

---

### Task 7: Implement validation and error handling (AC6)

**File:** `eleven_video/processing/video_handler.py`

- [ ] Validate `images` not empty → `ValidationError`
- [ ] Validate `audio` not None and has data → `ValidationError`
- [ ] Check FFmpeg availability → `VideoProcessingError`
- [ ] Wrap moviepy errors in `VideoProcessingError`
- [ ] Ensure temp file cleanup in `finally` block
- [ ] Run test: `pytest tests/processing/test_video_handler.py::TestValidationErrors -v`
- [ ] Run test: `pytest tests/processing/test_video_handler.py::TestErrorHandling -v`
- [ ] ✅ Validation and error tests pass

**Estimated Effort:** 1.0 hours

---

### Task 8: Export and integrate (AC1)

**File:** `eleven_video/processing/__init__.py`

- [ ] Export `FFmpegVideoCompiler` from `__init__.py`
- [ ] Run full test suite: `pytest tests/processing/test_video_handler.py -v`
- [ ] ✅ All tests pass

**Estimated Effort:** 0.25 hours

---

## Running Tests

```bash
# Run all failing tests for this story
pytest tests/processing/test_video_handler.py -v

# Run specific test class
pytest tests/processing/test_video_handler.py::TestCompileVideoSuccess -v

# Run with coverage
pytest tests/processing/test_video_handler.py --cov=eleven_video.processing --cov-report=term-missing

# Run only validation tests
pytest tests/processing/test_video_handler.py::TestValidationErrors -v

# Run only error handling tests
pytest tests/processing/test_video_handler.py::TestErrorHandling -v
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete) ✅

**TEA Agent Responsibilities:**

- ✅ All tests written and failing
- ✅ Fixtures and factories created with cleanup patterns
- ✅ Mock requirements documented for moviepy
- ✅ Implementation checklist with clear tasks

**Verification:**

- All tests run and fail as expected
- Failures are due to missing implementation (not test bugs)
- Test IDs follow pattern: `[2.4-UNIT-XXX]`

---

### GREEN Phase (DEV Team - Next Steps)

1. **Pick one failing test** from implementation checklist
2. **Read the test** to understand expected behavior
3. **Implement minimal code** to make it pass
4. **Run the test** to verify green
5. **Move to next test**

**Key Principles:**

- One test at a time
- Minimal implementation (don't over-engineer)
- Run tests frequently
- Use `tempfile.TemporaryDirectory` for cleanup

---

### REFACTOR Phase (DEV Team - After All Tests Pass)

1. Verify all tests pass
2. Review code for duplication
3. Ensure proper error messages
4. Optimize moviepy settings if needed
5. Ensure tests still pass after each refactor

---

## Knowledge Base References Applied

- **data-factories.md** - Factory patterns for Image/Audio domain models
- **test-quality.md** - Given-When-Then structure, isolated tests with cleanup
- **test-levels-framework.md** - Unit tests with mocks as primary level (moviepy is external)

---

## Test Execution Evidence

### Initial Test Run (RED Phase Verification)

**Command:** `pytest tests/processing/test_video_handler.py -v`

**Expected Results:**

```
FAILED test_compile_video_returns_video_domain_model - ModuleNotFoundError: No module named 'eleven_video.processing.video_handler'
FAILED test_compile_video_creates_mp4_file - ModuleNotFoundError
... (all 20 tests fail)

Summary: 20 failed, 0 passed
```

**Status:** ✅ RED phase verified - all tests fail due to missing implementation

---

## Notes

- **FFmpeg Dependency:** moviepy requires FFmpeg. Add detection and helpful error if missing
- **Temp Files:** Use `tempfile.TemporaryDirectory` context manager - never leave orphaned files
- **Audio Duration:** If `audio.duration_seconds` is None, calculate from audio file via moviepy
- **Suppress Logs:** Pass `logger=None` to `write_videofile()` to suppress verbose output
- **Integration Tests:** Add `@pytest.mark.integration` test with real FFmpeg (skip in CI)

---

**Generated by Murat (TEA Agent)** - 2025-12-16
