# Story 2.5: Progress Updates During Video Generation

Status: done

## 1. Story

**As a** user,
**I want** to receive progress updates during video generation,
**so that** I can understand how long the process will take and its current status.

## 2. Acceptance Criteria

1. **Given** I have initiated video generation,
   **When** the generation process is running,
   **Then** I receive clear, textual progress updates for each stage (script, audio, images, compilation).

2. **Given** the pipeline is executing,
   **When** a stage begins (e.g., script generation),
   **Then** a progress message is displayed with the stage name and a visual indicator.

3. **Given** the pipeline is executing,
   **When** a stage completes,
   **Then** a completion message is displayed with elapsed time for that stage.

4. **Given** the images are being generated,
   **When** each image completes,
   **Then** I see progress like "Processing image 3 of 5" with a percentage.

5. **Given** the video is being compiled,
   **When** compilation is running,
   **Then** I see "Compiling video..." with a spinner or progress indicator.

6. **Given** an error occurs during any stage,
   **When** the error is detected,
   **Then** progress shows which stage failed with a clear error indicator.

7. **Given** the full pipeline completes successfully,
   **When** the video is ready,
   **Then** I see a summary with total elapsed time and output file path.

## 3. Developer Context

### Technical Requirements

- **Primary Goal:** Create unified `VideoPipelineProgress` class to coordinate progress across all generation stages
- **Location:** `eleven_video/ui/progress.py` (NEW file in ui module)
- **UI Library:** Rich library for progress bars, spinners, and status panels
- **Console Singleton:** Import `from eleven_video.ui.console import console` - use existing singleton
- **Pattern:** Observer pattern with `progress_callback: Callable[[str], None]` already established in Stories 2.2-2.4

> [!IMPORTANT]
> **Existing Progress Callbacks:** Stories 2.2, 2.3, and 2.4 already implemented `progress_callback` parameters. This story UNIFIES them into a Rich-based terminal display.

> [!CAUTION]
> **Do NOT modify existing adapter/compiler classes.** They already emit progress via callbacks. This story creates the display layer that consumes those callbacks.

### Architectural Compliance

- **Hexagonal Architecture:** UI layer (`eleven_video/ui/`) consumes domain events
- **Loading States (per architecture):** `INITIALIZING`, `PROCESSING_SCRIPT`, `PROCESSING_AUDIO`, `PROCESSING_IMAGES`, `COMPILING_VIDEO`
- **Progress Format:** Rich progress bars with "description, %, elapsed time" per architecture patterns
- **Update Frequency:** Status updates every 5 seconds during long operations (per architecture)
- **Observer Pattern:** Progress callbacks `Callable[[str], None]` already used in adapters

### File & Code Structure

| File | Purpose |
|------|---------|
| `eleven_video/ui/progress.py` | [NEW] VideoPipelineProgress class with Rich display |
| `eleven_video/ui/__init__.py` | [MODIFY] Export VideoPipelineProgress |
| `eleven_video/models/domain.py` | [MODIFY] Add PipelineStage enum |
| `tests/ui/test_progress.py` | [NEW] Unit tests for progress display |

### Domain Models

```python
from enum import Enum

class PipelineStage(Enum):
    """Video generation pipeline stages (Story 2.5)."""
    INITIALIZING = "initializing"
    PROCESSING_SCRIPT = "processing_script"
    PROCESSING_AUDIO = "processing_audio" 
    PROCESSING_IMAGES = "processing_images"
    COMPILING_VIDEO = "compiling_video"
    COMPLETED = "completed"
    FAILED = "failed"

# Stage icons for Rich display
STAGE_ICONS: dict[PipelineStage, str] = {
    PipelineStage.INITIALIZING: "⏳",
    PipelineStage.PROCESSING_SCRIPT: "📝",
    PipelineStage.PROCESSING_AUDIO: "🔊",
    PipelineStage.PROCESSING_IMAGES: "🖼️",
    PipelineStage.COMPILING_VIDEO: "🎬",
    PipelineStage.COMPLETED: "✅",
    PipelineStage.FAILED: "❌",
}
```

### VideoPipelineProgress Class

```python
from pathlib import Path
from typing import Callable, Optional
import time

from rich.console import Console
from rich.panel import Panel

from eleven_video.ui.console import console as default_console  # Singleton
from eleven_video.models.domain import PipelineStage, STAGE_ICONS

class VideoPipelineProgress:
    """Unified progress display for video generation pipeline."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or default_console
        self.current_stage: PipelineStage = PipelineStage.INITIALIZING
        self.stage_start_times: dict[PipelineStage, float] = {}
        self.pipeline_start_time: Optional[float] = None  # Track overall pipeline
        self.total_images: int = 0
        self.completed_images: int = 0
        
    def start_stage(self, stage: PipelineStage) -> None: ...
    def update_progress(self, message: str) -> None: ...
    def complete_stage(self, stage: PipelineStage) -> None: ...
    def fail_stage(self, stage: PipelineStage, error: str) -> None: ...
    def show_summary(self, output_path: Path, video: "Video") -> None: ...
    def create_callback(self) -> Callable[[str], None]:
        return self.update_progress
```

### Progress Display Format

Per architecture patterns, use Rich progress bars with consistent format:

```
[Stage Icon] Stage Name ━━━━━━━━━━━━ XX% • Elapsed: 00:05
```

Use `STAGE_ICONS` dict (defined in domain.py) to look up icons by `PipelineStage`.

> [!TIP]
> For simple spinner displays (like "Compiling video..."), use `console.status()` which is simpler than `Rich.Live`:
> ```python
> with self.console.status("Compiling video...", spinner="dots"):
>     # work happens here
> ```

### Error Display Format

```python
console.print(Panel(
    f"[red]❌ {stage.value} failed[/red]\n\n{error_message}",
    title="Pipeline Error",
    border_style="red"
))
```

### Summary Panel Format

```python
console.print(Panel.fit(
    f"[green]✅ Video Generated Successfully![/green]\n\n"
    f"Output: {output_path}\n"
    f"Duration: {video_duration}s\n"
    f"Size: {file_size_mb:.1f} MB\n"
    f"Total time: {total_time:.1f}s",
    title="Complete",
    border_style="green"
))
```

### Integration with Existing Adapters

Stories 2.1-2.4 already use `progress_callback: Optional[Callable[[str], None]]`:

| Adapter | Method | Start Message | Completion Message |
|---------|--------|---------------|--------------------|
| GeminiAdapter | `generate_script()` | "Generating script..." | "Script generation complete" |
| ElevenLabsAdapter | `generate_speech()` | "Generating audio..." | "Audio generation complete" |
| GeminiAdapter | `generate_images()` | "Generating image X of Y" | "Generated N images successfully" |
| FFmpegVideoCompiler | `compile_video()` | "Processing image X of Y", "Compiling video..." | (returns Video) |

The `VideoPipelineProgress.create_callback()` method returns a function that can be passed to these adapters.

### Testing Requirements

| Category | Tests |
|----------|-------|
| Stage Lifecycle | start_stage → update → complete_stage flow |
| Progress Display | Mock console output verification |
| Error Handling | fail_stage displays error correctly |
| Summary | show_summary includes all required fields |
| Callback | create_callback returns valid Callable |
| State Tracking | Stage transitions update internal state |
| Timing | Elapsed time tracked per stage |

### Previous Story Intelligence

**From Story 2.4:** `progress_callback` pattern: `Callable[[str], None]`
**From Stories 2.1-2.3:** Each adapter has optional `progress_callback` parameter
**From displays.py:** Existing Rich patterns: `Table`, `Panel`, `console.print()`
**From console.py:** Shared `console` singleton for output

### Key Implementation Details

1. Use `console.status()` for simple spinners, `Rich.Live` for complex progress bars
2. Track `stage_start_times` dict to calculate elapsed time per stage
3. Track `pipeline_start_time` when first stage starts for total elapsed time in summary
4. For image generation, parse "Generating image X of Y" to update progress bar percentage
5. `create_callback()` returns a closure that calls `update_progress()`
6. Console output should be suppressible for testing (pass mock Console)
7. Do NOT use `print()` - always use `console.print()` for Rich formatting
8. Import console singleton: `from eleven_video.ui.console import console`

## 4. Tasks

- [x] **Task 1:** Add `PipelineStage` enum to domain models (AC: 1)
  - [x] Add to `eleven_video/models/domain.py`
  - [x] Export from `__init__.py`

- [x] **Task 2:** Create `VideoPipelineProgress` class (AC: 1, 2, 3)
  - [x] Create `eleven_video/ui/progress.py`
  - [x] Implement `start_stage()`, `complete_stage()`, `fail_stage()`
  - [x] Use Rich Progress with SpinnerColumn, TextColumn, TimeElapsedColumn

- [x] **Task 3:** Implement progress update display (AC: 4, 5)
  - [x] Implement `update_progress()` with Rich Live context
  - [x] Parse "image X of Y" format for percentage calculation
  - [x] Display spinner during "Compiling video..."

- [x] **Task 4:** Implement error handling display (AC: 6)
  - [x] `fail_stage()` shows red Panel with error details
  - [x] Stops progress display cleanly

- [x] **Task 5:** Implement completion summary (AC: 7)
  - [x] `show_summary()` displays green Panel with all metrics
  - [x] Include output path, duration, size, total time

- [x] **Task 6:** Create callback factory (AC: 1)
  - [x] Implement `create_callback()` method
  - [x] Returns closure compatible with adapter signatures

- [x] **Task 7:** Write unit tests (All ACs)
  - [x] Create `tests/ui/test_progress.py`
  - [x] Mock Rich Console for output verification
  - [x] Test all stage transitions and display formats

- [x] **Task 8:** Update exports
  - [x] Export `VideoPipelineProgress` from `eleven_video/ui/__init__.py`
  - [x] Export `PipelineStage` from `eleven_video/models/__init__.py`

## 5. Dev Agent Record

### Agent Model Used

Gemini 2.5 Pro (Code Review)

### Completion Notes

**Implementation completed 2025-12-17:**
- `PipelineStage` enum with 7 stages (INITIALIZING → FAILED)
- `STAGE_ICONS` dict mapping stages to emoji icons
- `VideoPipelineProgress` class with full Rich integration
- All methods: `start_stage()`, `complete_stage()`, `update_progress()`, `fail_stage()`, `show_summary()`, `create_callback()`
- Image parsing via regex for "image X of Y" format
- 25 unit tests covering all acceptance criteria

**Code Review Fixes Applied:**
- Marked all tasks complete (were `[ ]` despite implementation)
- Updated status from `ready-for-dev` to `done`
- Filled in Dev Agent Record

### File List

| File | Change |
|------|--------|
| `eleven_video/models/domain.py` | MODIFY - add PipelineStage enum and STAGE_ICONS dict |
| `eleven_video/ui/progress.py` | NEW |
| `eleven_video/ui/__init__.py` | MODIFY |
| `tests/ui/test_progress.py` | NEW |
