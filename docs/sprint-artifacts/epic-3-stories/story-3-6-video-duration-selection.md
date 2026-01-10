# Story 3.6: Video Duration Selection

**FR Coverage:** FR24 (Users can select video format, length, and other options through interactive prompts)

Status: done

## Story

As a user,
I want to select a target video duration through interactive prompts,
so that I can control how long my generated video will be.

## Acceptance Criteria

1. **Given** I am setting up video generation, **When** I am prompted to select a video duration, **Then** the tool displays a numbered list of duration options (e.g., 3 minutes, 5 minutes, 10 minutes).

2. **Given** I see the duration list, **When** I select a duration by number, **Then** the system generates a script and assets appropriate for that duration.

3. **Given** I run `eleven-video generate` without the `--duration` flag, **When** I am prompted to select a duration, **Then** I see an option to use the default duration (e.g., "[0] Default (3 minutes)").

4. **Given** I run `eleven-video generate --duration 5`, **When** I specify a duration via CLI flag, **Then** the interactive duration prompt is skipped.

5. **Given** the script generation process runs, **When** a specific duration is selected, **Then** the generated script length approximately matches the target duration and the image count is adjusted accordingly.

6. **Given** I run `eleven-video generate` interactively, **When** the interactive prompts appear, **Then** the duration selection prompt appears BEFORE the video topic/prompt input (configuration before content).

## Tasks / Subtasks

- [x] Task 1: Create DurationOption enum/dataclass (AC: #1)
  - [x] 1.1: Add `DurationOption` to `eleven_video/models/domain.py`
  - [x] 1.2: Include preset durations: 3, 5, 10 minutes with labels
  - [x] 1.3: Add helper method to get word count estimate from duration
  - [x] 1.4: Write unit tests for `DurationOption` class

- [x] Task 2: Create DurationSelector UI component (AC: #1, #3)
  - [x] 2.1: Create `eleven_video/ui/duration_selector.py` with `DurationSelector` class
  - [x] 2.2: Implement `_display_duration_options()` method using Rich library
  - [x] 2.3: Display numbered list: "[0] Default (3 minutes)", "[1] 1 minute (short)", etc.
  - [x] 2.4: Add non-TTY fallback (R-004 mitigation)
  - [x] 2.5: Write unit tests for `DurationSelector._display_duration_options()`

- [x] Task 3: Implement duration selection input handling (AC: #2)
  - [x] 3.1: Add `select_duration()` method returning `Optional[int]` (minutes)
  - [x] 3.2: Accept numeric input (0-N) to select by index
  - [x] 3.3: Return `None` for default (3 minutes)
  - [x] 3.4: Handle invalid input gracefully (fallback to default)
  - [x] 3.5: Write unit tests for input handling

- [x] Task 4: Update script generation to respect duration (AC: #5)
  - [x] 4.1: Add `duration_minutes: Optional[int]` parameter to `GeminiAdapter.generate_script()`
  - [x] 4.2: Modify prompt to include duration instruction (e.g., "Generate a script for a 5-minute video")
  - [x] 4.3: Adjust prompt to request appropriate word count (150 words/minute estimate)
  - [x] 4.4: Write unit tests for duration parameter in script generation

- [x] Task 5: Update image generation to match duration (AC: #5)
  - [x] 5.1: Calculate target image count based on duration (3-4 seconds per image)
  - [x] 5.2: Add `target_image_count: Optional[int]` parameter to `GeminiAdapter.generate_images()`
  - [x] 5.3: **Modify `_segment_script()` to accept `target_count`** - when provided, limit segments to `target_count` (trim list) or expand by splitting longer paragraphs into more sentences
  - [x] 5.4: Fallback: if segments < target, repeat last segment prompts; if segments > target, take first N
  - [x] 5.5: Write unit tests for adaptive image count with various target values

- [x] Task 6: Integrate duration selection into generate command (AC: #3, #4, #6)
  - [x] 6.1: Add `--duration` / `-d` CLI option to `generate()` function in `main.py`
  - [x] 6.2: **Validate CLI duration input**: must be 3, 5, or 10. Show error for invalid values (e.g., 1, -1, 0)
  - [x] 6.3: **IMPORTANT: Reorder interactive prompts** - duration selection should happen BEFORE prompt input (configuration before content)
  - [x] 6.4: If duration is None, call DurationSelector before asking for video topic
  - [x] 6.5: Skip duration prompt if `--duration` flag was provided
  - [x] 6.6: Pass duration through pipeline to adapters
  - [x] 6.7: Write integration tests: valid durations, invalid durations, duration+prompt combo, non-numeric input

- [x] Task 7: Update VideoPipeline to pass duration (AC: #2, #5)
  - [x] 7.1: Add `duration_minutes: Optional[int]` parameter to `VideoPipeline.generate()`
  - [x] 7.2: Pass duration to `generate_script()` call
  - [x] 7.3: Calculate and pass target_image_count to `generate_images()`
  - [x] 7.4: Write unit tests for pipeline duration handling

- [x] Task 8: Export DurationSelector and constants (AC: all)
  - [x] 8.1: Update `eleven_video/ui/__init__.py` to export `DurationSelector`
  - [x] 8.2: Update `eleven_video/models/domain.py` exports to include `DurationOption`, `DURATION_OPTIONS`, `DEFAULT_DURATION_MINUTES`
  - [x] 8.3: Verify imports work from main.py and tests

## Dev Notes

### Scope Clarification

> ⚠️ **UI/CLI + Backend story.** This story implements:
> 1. UI: `DurationSelector` class for interactive duration selection
> 2. Backend: Duration parameter propagation to script and image generation
> 3. CLI: `--duration` flag and pipeline integration
>
> **This is more complex than other selectors** because duration affects multiple downstream processes (script length AND image count).

### Architecture Compliance

**Pattern:** Hexagonal (Ports & Adapters)
- CLI (`main.py`) is in the "driving adapter" layer
- `DurationSelector` is a UI helper in the presentation layer
- Duration affects both script generation and image generation adapters

**Source:** [docs/architecture/core-architectural-decisions.md#Consensus Decisions]

### Duration Options Design

**Preset duration options (R-012 consideration):**

| Option | Duration | Label | Est. Word Count | Est. Image Count |
|--------|----------|-------|-----------------|------------------|
| 0 | (default) | Use Default | Returns `None` | Uses 5 min internally |
| 1 | 3 min | Short | ~450 words | ~45-60 images |
| 2 | 5 min | Standard | ~750 words | ~75-100 images |
| 3 | 10 min | Extended | ~1500 words | ~150-200 images |

> **Note:** Option 0 returns `None`, meaning "use default". The pipeline interprets `None` as 5 minutes.

**Calculations:**
- Words per minute (spoken): ~150 words/minute
- Images per minute (3-4 seconds each): ~15-20 images/minute

### Domain Model: DurationOption

**File to create/modify:** `eleven_video/models/domain.py`

```python
from dataclasses import dataclass
from enum import Enum


class VideoDuration(Enum):
    """Predefined video duration options."""
    SHORT = 3     # 3 minutes
    STANDARD = 5    # 5 minutes (default)
    EXTENDED = 10    # 10 minutes


@dataclass
class DurationOption:
    """Video duration option for user selection.
    
    Attributes:
        minutes: Duration in minutes.
        label: Human-readable label (e.g., "Short", "Standard").
        description: Optional description for UI display.
    """
    minutes: int
    label: str
    description: str = ""
    
    @property
    def estimated_word_count(self) -> int:
        """Estimate word count for this duration (150 words/minute)."""
        return self.minutes * 150
    
    @property
    def estimated_image_count(self) -> int:
        """Estimate image count for this duration (15-20 images/minute, using 15)."""
        return self.minutes * 15


# Predefined duration options
DURATION_OPTIONS: list[DurationOption] = [
    DurationOption(minutes=3, label="Short", description="~3 minute video"),
    DurationOption(minutes=5, label="Standard", description="~5 minutes (recommended)"),
    DurationOption(minutes=10, label="Extended", description="~10 minutes"),
]

DEFAULT_DURATION_MINUTES = 5
```

### DurationSelector Class Design

**File:** `eleven_video/ui/duration_selector.py`

```python
"""
Interactive Video Duration Selection UI Component - Story 3.6

Provides user-friendly duration selection via Rich terminal prompts.
Uses predefined DurationOption presets for consistency.
"""
from typing import Optional, List

from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

from eleven_video.ui.console import console
from eleven_video.models.domain import DurationOption, DURATION_OPTIONS, DEFAULT_DURATION_MINUTES


class DurationSelector:
    """Interactive video duration selection UI component.
    
    Displays available duration options and prompts user to select one.
    Falls back to default duration on errors or non-TTY environments.
    """
    
    def __init__(self) -> None:
        """Initialize DurationSelector with predefined options."""
        self._options = DURATION_OPTIONS
    
    def select_duration_interactive(self) -> Optional[int]:
        """Display duration options and prompt user for selection.
        
        Returns:
            Duration in minutes, or None to use default (3 minutes).
        """
        # R-004 mitigation: Non-TTY fallback
        if not console.is_terminal:
            console.print("[dim]Non-interactive mode detected. Using default duration.[/dim]")
            return None
        
        self._display_duration_options()
        return self._get_user_selection()
    
    def _display_duration_options(self) -> None:
        """Display numbered duration options."""
        console.print(Panel(
            "[bold cyan]Select Video Duration[/bold cyan]",
            border_style="cyan"
        ))
        
        table = Table(show_header=False, box=None)
        table.add_column("#", style="cyan", width=4)
        table.add_column("Duration", style="white")
        table.add_column("Description", style="dim")
        
        # Default option
        table.add_row("0", f"Default ({DEFAULT_DURATION_MINUTES} min)", "recommended")
        
        for i, option in enumerate(self._options, start=1):
            table.add_row(str(i), f"{option.minutes} min ({option.label})", option.description)
        
        console.print(table)
    
    def _get_user_selection(self) -> Optional[int]:
        """Prompt user for duration selection and return minutes.
        
        Returns:
            Duration in minutes, or None for default
        """
        choice = Prompt.ask(
            "\n[bold cyan]Select a duration number[/bold cyan]",
            default="0"
        )
        
        try:
            index = int(choice)
            if index == 0:
                return None  # Use default
            if 1 <= index <= len(self._options):
                return self._options[index - 1].minutes
            console.print("[yellow]Invalid selection. Using default.[/yellow]")
            return None
        except ValueError:
            console.print("[yellow]Invalid input. Using default.[/yellow]")
            return None
```

### CLI Integration Points

**File to modify:** `eleven_video/main.py`

> [!IMPORTANT]
> **UX Prompt Order (AC #6):** Duration selection should happen BEFORE the video topic prompt.
> The order should be: Duration → Voice → Gemini Model → Image Model → **THEN** Prompt (if not provided via CLI).

Add `--duration` option and reorder the interactive prompts:

```python
@app.command()
def generate(
    prompt: Optional[str] = typer.Option(None, "--prompt", "-p", help="Text prompt..."),
    voice: Optional[str] = typer.Option(None, "--voice", "-v", help="Voice ID to use"),
    image_model: Optional[str] = typer.Option(None, "--image-model", "-m", help="Image model ID"),
    gemini_model: Optional[str] = typer.Option(None, "--gemini-model", help="Gemini text model ID"),
    duration: Optional[int] = typer.Option(None, "--duration", "-d", help="Video duration in minutes (1, 3, or 5)"),  # NEW
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
):
    # ============================================
    # CONFIGURATION PROMPTS (before content input)
    # ============================================
    
    # 1. Interactive duration selection FIRST (Story 3.6 - AC#6)
    if duration is None:
        from eleven_video.ui.duration_selector import DurationSelector
        try:
            selector = DurationSelector()
            duration = selector.select_duration_interactive()
        except Exception as e:
            console.print(f"[yellow]⚠️ Duration selection unavailable: {e}[/yellow]")
            duration = None  # Graceful degradation
    
    # 2. Voice selection (Story 3.3)
    # ... existing voice selection code ...
    
    # 3. Gemini model selection (Story 3.5)
    # ... existing gemini model selection code ...
    
    # 4. Image model selection (Story 3.4)
    # ... existing image model selection code ...
    
    # ============================================
    # CONTENT INPUT (after configuration)
    # ============================================
    
    # 5. Interactive prompt LAST (after all configuration is done)
    if not prompt:
        console.print(Panel.fit(
            "[bold cyan]Eleven Video Generator[/bold cyan]\n"
            "Generate a video from a text topic.",
            border_style="cyan"
        ))
        prompt = Prompt.ask("[bold green]Enter your video topic/prompt[/bold green]")
    
    # Pass duration to pipeline
    video = pipeline.generate(
        prompt=prompt, 
        voice_id=voice, 
        image_model_id=image_model, 
        gemini_model_id=gemini_model,
        duration_minutes=duration  # NEW
    )
```

### Updating generate_script() to Accept duration_minutes

**File to modify:** `eleven_video/api/gemini.py`

```python
def generate_script(
    self,
    prompt: str,
    progress_callback: Optional[Callable[[str], None]] = None,
    model_id: Optional[str] = None,
    warning_callback: Optional[Callable[[str], None]] = None,
    duration_minutes: Optional[int] = None,  # NEW PARAMETER
) -> Script:
    """Generate a video script from a text prompt using Gemini.
    
    Args:
        prompt: The text prompt describing the desired video.
        progress_callback: Optional callback for progress updates.
        model_id: Optional Gemini model ID (uses default if not provided).
        warning_callback: Optional callback for warnings.
        duration_minutes: Target video duration in minutes (affects script length).
        
    Returns:
        Script domain model with generated content.
    """
    # ... existing validation ...
    
    # Story 3.6: Build duration-aware prompt
    effective_duration = duration_minutes or 3  # Default to 3 minutes
    word_count = effective_duration * 150  # 150 words/minute estimate
    
    duration_instruction = (
        f"\n\nGenerate a script for approximately a {effective_duration}-minute video. "
        f"Target around {word_count} words. Structure the content with clear sections "
        f"suitable for visual accompaniment."
    )
    
    enhanced_prompt = prompt + duration_instruction
    
    # ... rest of existing logic with enhanced_prompt ...
```

```python
def generate_images(
    self,
    script: Script,
    progress_callback: Optional[Callable[[str], None]] = None,
    model_id: Optional[str] = None,
    target_image_count: Optional[int] = None,  # NEW PARAMETER
) -> List[Image]:
    """Generate images based on script content."""
    # ... validation code ...
    
    # Story 3.6: Get segments, then adjust to target count
    segments = self._segment_script(script.content)
    
    if target_image_count is not None:
        segments = self._adjust_segment_count(segments, target_image_count)
    
    # ... rest of image generation loop ...


def _adjust_segment_count(self, segments: List[str], target: int) -> List[str]:
    """Adjust segment count to match target (Story 3.6).
    
    Args:
        segments: Current list of image prompts.
        target: Target number of images.
        
    Returns:
        Adjusted list with approximately `target` segments.
    """
    current = len(segments)
    
    if current == target:
        return segments
    
    if current > target:
        # Trim: take first N segments (keeps beginning of video)
        return segments[:target]
    
    # Expand: repeat segments to fill target (cycle through)
    expanded = segments.copy()
    while len(expanded) < target:
        expanded.append(segments[len(expanded) % current])
    return expanded
```

> [!IMPORTANT]
> **Existing code reference:** The `_segment_script()` method (lines 539-576 in gemini.py) segments by paragraphs. The new `_adjust_segment_count()` helper post-processes the result to match duration.

### Updating VideoPipeline

**File to modify:** `eleven_video/orchestrator/video_pipeline.py`

```python
def generate(
    self, 
    prompt: str, 
    voice_id: Optional[str] = None, 
    image_model_id: Optional[str] = None, 
    gemini_model_id: Optional[str] = None,
    duration_minutes: Optional[int] = None  # NEW PARAMETER
) -> Video:
    """Run full pipeline.
    
    Args:
        prompt: Text topic.
        voice_id: Optional ElevenLabs voice ID.
        image_model_id: Optional Gemini image model ID.
        gemini_model_id: Optional Gemini text model ID.
        duration_minutes: Optional target duration in minutes (Story 3.6).
    """
    self._init_adapters()
    self.output_dir.mkdir(parents=True, exist_ok=True)
    
    callback = self.progress.create_callback()
    
    # Calculate target image count from duration (15 images/minute)
    target_image_count = None
    if duration_minutes:
        target_image_count = duration_minutes * 15
    
    try:
        # 1. Script (Pass duration_minutes - Story 3.6)
        self.progress.start_stage(PipelineStage.PROCESSING_SCRIPT)
        script = self._gemini.generate_script(
            prompt, 
            progress_callback=callback, 
            model_id=gemini_model_id,
            duration_minutes=duration_minutes  # NEW
        )
        self.progress.complete_stage(PipelineStage.PROCESSING_SCRIPT)

        # 2. Audio (unchanged)
        # ...

        # 3. Images (Pass target_image_count - Story 3.6)
        self.progress.start_stage(PipelineStage.PROCESSING_IMAGES)
        images = self._gemini.generate_images(
            script, 
            progress_callback=callback, 
            model_id=image_model_id,
            target_image_count=target_image_count  # NEW
        )
        self.progress.complete_stage(PipelineStage.PROCESSING_IMAGES)
        
        # ... rest of pipeline ...
```

### Testing Requirements

**Test IDs from Epic 3 Test Design:**

| Test ID | Description | Priority |
|---------|-------------|----------|
| 3.6-UNIT-001 | Duration parameter in script prompt | P0 |
| 3.6-UNIT-002 | Duration boundary validation | P2 |
| 3.6-COMP-001 | Duration selection menu rendering | P1 |

**Test Groups:**

| Group | Tests | Description | Test ID |
|-------|-------|-------------|---------|
| TestDurationOption | 3 | Domain model creation and calculations | - |
| TestDurationSelectorDisplay | 3 | `_display_duration_options()` formatting | 3.6-COMP-001 |
| TestDurationSelectorInput | 4 | `_get_user_selection()` input handling | 3.6-COMP-001 |
| TestDurationSelectorInteractive | 3 | Full `select_duration_interactive()` flow | 3.6-COMP-001 |
| TestNonTTYFallback | 2 | Non-TTY environment detection (R-004) | - |
| TestCLIDurationIntegration | 3 | `generate` command duration selection flow | - |
| TestGenerateScriptWithDuration | 3 | `generate_script()` with duration parameter | 3.6-UNIT-001 |
| TestGenerateImagesWithCount | 3 | `generate_images()` with target image count | 3.6-UNIT-001 |
| TestDurationBoundaries | 2 | 0, negative, very long durations | 3.6-UNIT-002 |

**Test file locations:**
- `tests/models/test_duration_option.py` - Domain model tests (NEW)
- `tests/ui/test_duration_selector_display.py` - Display tests (NEW)
- `tests/ui/test_duration_selector_input.py` - Input handling tests (NEW)
- `tests/api/test_gemini_duration.py` - Duration in script/image generation (NEW)
- `tests/orchestrator/test_pipeline_duration.py` - Pipeline duration handling (MODIFY or NEW)

**Coverage target:** ≥80% for new code

**Test command:** `uv run pytest tests/ui/test_duration_selector_*.py tests/models/test_duration_option.py tests/api/test_gemini_duration.py -v`

### Required Conftest Fixtures (tests/ui/conftest.py)

Add these fixtures mirroring the VoiceSelector/GeminiModelSelector patterns:

```python
# =============================================================================
# Fixtures for DurationSelector (Story 3.6)
# =============================================================================

def create_duration_option(
    minutes: int = 3,
    label: str = "Standard",
    description: str = "~3 minutes (recommended)"
):
    """Factory function for creating DurationOption test data."""
    from eleven_video.models.domain import DurationOption
    return DurationOption(minutes=minutes, label=label, description=description)


@pytest.fixture
def duration_selector():
    """Create a DurationSelector instance."""
    from eleven_video.ui.duration_selector import DurationSelector
    return DurationSelector()


@pytest.fixture
def sample_duration_options():
    """Return the standard DURATION_OPTIONS list for testing."""
    from eleven_video.models.domain import DURATION_OPTIONS
    return DURATION_OPTIONS


@pytest.fixture
def mock_console_duration():
    """Patch console for testing without terminal output (DurationSelector)."""
    with patch("eleven_video.ui.duration_selector.console") as mock:
        mock.is_terminal = True
        yield mock


@pytest.fixture
def mock_prompt_duration():
    """Patch Rich Prompt for testing user input (DurationSelector)."""
    with patch("eleven_video.ui.duration_selector.Prompt") as mock:
        yield mock
```

### Risk Mitigation (from test-design-epic-3.md)

**Risks addressed in this story:**

| Risk ID | Description | Score | Story Mitigation |
|---------|-------------|-------|------------------|
| R-003 | Duration selection creates mismatched content timing | 6 | Pass duration to script generator as explicit parameter, validate output script length approximates target duration, adjust image count dynamically |
| R-004 | Interactive prompts fail in non-TTY environments | 4 | Detect non-TTY via `console.is_terminal`, skip selection with warning, use default |
| R-012 | Duration options don't match user needs | 1 | Provide 3 presets (1, 3, 5 min) covering common use cases; custom duration deferred to Phase 3 |

**Source:** [docs/test-design-epic-3.md#Risk Assessment]

### Previous Story Intelligence

**Story 3.5 (Gemini Model Selection):**
- Created `GeminiModelSelector` class with `select_model_interactive()`, `_display_model_list()`, `_get_user_selection()` methods
- Implemented non-TTY fallback using `console.is_terminal` check
- Error handling returns None (default) on failures
- **Pattern to replicate for DurationSelector**

**Key Differences from Other Selectors:**
1. Duration doesn't require API calls - uses predefined presets
2. Duration affects TWO downstream processes (script + images)
3. Duration involves calculations (word count, image count)

### Image Count Calculation Details

**For R-003 mitigation - ensuring duration matches output:**

```python
# Constants (based on PRD requirement: 3-4 seconds per image)
WORDS_PER_MINUTE = 150  # Average speaking rate
IMAGES_PER_MINUTE = 15  # At ~4 seconds per image

def calculate_targets(duration_minutes: int) -> tuple[int, int]:
    """Calculate word count and image count for a given duration.
    
    Args:
        duration_minutes: Target video duration in minutes.
        
    Returns:
        Tuple of (word_count, image_count)
    """
    word_count = duration_minutes * WORDS_PER_MINUTE
    image_count = duration_minutes * IMAGES_PER_MINUTE
    return word_count, image_count

# Example outputs:
# 1 minute: ~150 words, ~15 images
# 3 minutes: ~450 words, ~45 images
# 5 minutes: ~750 words, ~75 images
```

### Project Structure Notes

**Files to create:**
- `eleven_video/ui/duration_selector.py` - DurationSelector class (NEW)
- `tests/models/test_duration_option.py` - Domain model tests (NEW)
- `tests/ui/test_duration_selector_display.py` - Display unit tests (NEW)
- `tests/ui/test_duration_selector_input.py` - Input handling tests (NEW)
- `tests/api/test_gemini_duration.py` - Duration parameter tests (NEW)

**Files to modify:**
- `eleven_video/models/domain.py` - Add `DurationOption`, `VideoDuration`, constants
- `eleven_video/api/gemini.py` - Add `duration_minutes` to `generate_script()`, `target_image_count` to `generate_images()`
- `eleven_video/orchestrator/video_pipeline.py` - Add `duration_minutes` parameter, calculate target image count
- `eleven_video/main.py` - Add `--duration` / `-d` option, add duration selection in `generate()` command
- `eleven_video/ui/__init__.py` - Export DurationSelector

### Error Handling Pattern

Match existing error handling in `main.py` and previous selectors:

```python
try:
    # Duration selection
    selector = DurationSelector()
    duration = selector.select_duration_interactive()
except Exception as e:
    console.print(f"[yellow]⚠️ Duration selection unavailable: {e}[/yellow]")
    console.print("[dim]Continuing with default duration (3 minutes)...[/dim]")
    duration = None  # Graceful degradation - use default
```

### References

- [Source: eleven_video/ui/voice_selector.py] - Story 3.3 VoiceSelector pattern to mirror
- [Source: eleven_video/ui/gemini_model_selector.py] - Story 3.5 GeminiModelSelector pattern
- [Source: eleven_video/ui/console.py] - Shared Rich console instance
- [Source: eleven_video/models/domain.py] - Domain models location
- [Source: eleven_video/main.py#generate] - CLI command to modify (lines 287-388)
- [Source: eleven_video/orchestrator/video_pipeline.py#generate] - Pipeline to update (lines 38-84)
- [Source: eleven_video/api/gemini.py#generate_script] - Method to update with duration param (lines 172-235)
- [Source: eleven_video/api/gemini.py#generate_images] - Method to update with target_image_count
- [Source: docs/sprint-artifacts/epic-3-stories/story-3-5-gemini-text-generation-model-selection.md] - Story 3.5 pattern reference
- [Source: docs/test-design-epic-3.md#3.6-UNIT-001, #3.6-UNIT-002, #3.6-COMP-001] - Test IDs for this story
- [Source: docs/epics.md#Story 3.6] - Original story requirements
- [Source: docs/prd.md#FR24] - Functional requirements
- [Source: docs/prd.md#Success Criteria] - 3-4 second image timing requirement

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
- eleven_video/models/domain.py
- eleven_video/ui/duration_selector.py
- eleven_video/ui/__init__.py
- eleven_video/api/gemini.py
- eleven_video/orchestrator/video_pipeline.py
- eleven_video/main.py
- tests/models/test_duration_option.py
- tests/ui/test_duration_selector_display.py
- tests/ui/test_duration_selector_input.py
- tests/api/test_gemini_duration.py
- tests/cli/test_duration_validation_cli.py

### Change Log
- [Fix] Implemented CLI duration validation (Story 3.6 - Task 6.2) in `main.py`
- [Fix] Added regression test `tests/cli/test_duration_validation_cli.py`

## Test Quality Review

> **Review Date:** 2025-12-20
> **Score:** 95/100 (A+ - Excellent)
> **Reviewer:** BMAD TEA Agent

**Summary:**
The test suite demonstrates high quality with strong adoption of BDD patterns and fixture architecture in Unit/UI tests. Coverage is comprehensive across domain logic and UI components.

**Key Findings:**
- ✅ **Excellent Domain Logic Coverage**: `test_duration_option.py` covers all edge cases.
- ✅ **Strong UI Isolation**: Robust use of factory patterns in `tests/ui/conftest.py`.
- ⚠️ **Traceability Gaps**: CLI and E2E tests missing Test ID references (3.6-CLI-001).

[View Full Review Report](../../test-reviews/test-review-story-3.6.md)

