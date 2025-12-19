# Story 3.4: Interactive Image Model Selection Prompts

**FR Coverage:** FR18 (Users can select from available image models through interactive prompts)

Status: Done

## Story

As a user,
I want to select from available image models through interactive prompts,
so that I can easily choose the image style I want without remembering specific model names.

## Acceptance Criteria

1. **Given** I am in an interactive session generating a video, **When** prompted to select an image model, **Then** the tool displays a numbered list of available image model options.

2. **Given** I see the image model list, **When** I select a model by number, **Then** my selection is used for image generation.

> [!NOTE]
> Image model selection by name search is deferred to P2 (R-008 mitigation). For MVP, numeric selection is sufficient.

3. **Given** the image model listing API fails, **When** I expect to see models, **Then** the system shows a helpful error message and falls back to the default model with a warning.

4. **Given** I run `eleven-video generate` without the `--image-model` flag, **When** I am prompted to select an image model, **Then** I see an option to use the default model (e.g., "[0] Use default model (gemini-2.5-flash-image)").

5. **Given** I run `eleven-video generate --image-model <id>`, **When** I specify an image model via CLI flag, **Then** the interactive image model prompt is skipped.

## Tasks / Subtasks

- [x] Task 1: Create image model selection prompt helper (AC: #1, #4)
  - [x] 1.1: Create `eleven_video/ui/image_model_selector.py` with `ImageModelSelector` class
  - [x] 1.2: Implement `display_model_list(models: list[ImageModelInfo])` method using Rich library
  - [x] 1.3: Display numbered list with format: "[1] Model Name (description)" 
  - [x] 1.4: Add "[0] Use default model (gemini-2.5-flash-image)" as first option
  - [x] 1.5: Write unit tests for `ImageModelSelector._display_model_list()`

- [x] Task 2: Implement image model selection input handling (AC: #2)
  - [x] 2.1: Add `select_model(models: list[ImageModelInfo]) -> Optional[str]` method
  - [x] 2.2: Accept numeric input (1-N) to select by index
  - [x] 2.3: Accept "0" for default model (returns None, meaning use default)
  - [x] 2.4: Return the selected `model_id` string
  - [x] 2.5: Write unit tests for input handling (mock Rich.Prompt)

- [x] Task 3: Add error handling for model listing failures (AC: #3)
  - [x] 3.1: Wrap `GeminiAdapter.list_image_models()` call in try/except
  - [x] 3.2: On failure, print warning message using Rich console
  - [x] 3.3: Return None to use default model on failure
  - [x] 3.4: Write unit tests for error handling path

- [x] Task 4: Integrate image model selection into generate command (AC: #4, #5)
  - [x] 4.1: Add `--image-model` / `-m` CLI option to `generate()` function in `main.py`
  - [x] 4.2: If None, call image model selection flow before pipeline.generate() (via ImageModelSelector)
  - [x] 4.3: Skip image model prompt if `--image-model` flag was provided
  - [x] 4.4: Update `VideoPipeline.generate()` to accept `image_model_id` parameter and pass to adapter
  - [x] 4.5: Pass selected model_id through pipeline to `adapter.generate_images(model_id=...)`
  - [x] 4.6: Write integration tests mocking both list_image_models and pipeline

- [x] Task 5: Export ImageModelSelector from ui module (AC: all)
  - [x] 5.1: Update `eleven_video/ui/__init__.py` to export `ImageModelSelector`
  - [x] 5.2: Verify import works from main.py

- [x] Task 6: Add non-TTY fallback (R-004 mitigation)
  - [x] 6.1: Detect non-TTY environment using `console.is_terminal`
  - [x] 6.2: If non-TTY, skip image model selection prompt and use default model with warning
  - [x] 6.3: Write unit tests for non-TTY detection and fallback
  - [x] 6.4: Document behavior in --help output (via code docstrings)

## Dev Notes

### Scope Clarification

> ⚠️ **UI/CLI story.** This story implements the interactive image model selection UI that uses Story 3.2's backend `list_image_models()` method.
>
> **Dependency Chain:** Story 3.2 (API) → **Story 3.4 (UI)** → User can interactively select image models

### Architecture Compliance

**Pattern:** Hexagonal (Ports & Adapters)
- CLI (`main.py`) is in the "driving adapter" layer
- `ImageModelSelector` is a UI helper in the presentation layer
- `GeminiAdapter.list_image_models()` provides the data (already implemented in Story 3.2)

**Source:** [docs/architecture/core-architectural-decisions.md#Consensus Decisions]

### Pattern Mirror: Story 3.3 (VoiceSelector)

This story **exactly mirrors Story 3.3 (Interactive Voice Selection Prompts)** but for image models:

| Story 3.3 (Voice) | Story 3.4 (Image) |
|-------------------|-------------------|
| `VoiceSelector` class | `ImageModelSelector` class |
| `ElevenLabsAdapter.list_voices()` | `GeminiAdapter.list_image_models()` |
| `VoiceInfo` domain model | `ImageModelInfo` domain model |
| `--voice` CLI flag | `--image-model` CLI flag |
| `select_voice_interactive()` | `select_model_interactive()` |
| `_display_voice_list()` | `_display_model_list()` |
| `_get_user_selection()` | `_get_user_selection()` |
| `voice.name, voice.category` | `model.name, model.description` |

**Follow Story 3.3 implementation patterns exactly** - the code structure should be nearly identical.

### Existing Image Model API (Story 3.2)

The `GeminiAdapter` already provides `list_image_models()`:

```python
# From eleven_video/api/gemini.py (Story 3.2 - lines 281-345)
def list_image_models(self, use_cache: bool = False) -> List[ImageModelInfo]:
    """List available image generation models from Gemini API."""
    # Returns List[ImageModelInfo] with:
    #   - model_id: str (e.g., "gemini-2.5-flash-image")
    #   - name: str (display name)
    #   - description: Optional[str]
    #   - supports_image_generation: bool
```

**Key Pattern: Use `use_cache=True`** - The model list is cached for 60 seconds, so repeated calls are fast.

**Source:** [eleven_video/api/gemini.py#list_image_models] (lines 281-345)

### ImageModelInfo Domain Model (Story 3.2)

```python
# From eleven_video/models/domain.py
@dataclass(frozen=True)
class ImageModelInfo:
    """Information about an available image generation model."""
    model_id: str
    name: str
    description: Optional[str] = None
    supports_image_generation: bool = True
```

**Source:** [eleven_video/models/domain.py#ImageModelInfo]

### Rich Library UI Patterns

This project uses the Rich library for all terminal UI. Use these patterns (from Story 3.3):

```python
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel
from eleven_video.ui.console import console  # Shared console instance

# Display a numbered list
table = Table(show_header=False, box=None)
table.add_column("#", style="cyan", width=4)
table.add_column("Model", style="white")
table.add_column("Description", style="dim")

for i, model in enumerate(models, start=1):
    table.add_row(str(i), model.name, model.description or "")

console.print(table)

# Get user input
choice = Prompt.ask("[bold cyan]Select an image model[/bold cyan]", default="0")
```

**Source:** [eleven_video/ui/console.py] - Shared Rich console instance
**Source:** [eleven_video/ui/voice_selector.py] - VoiceSelector implementation to mirror

### ImageModelSelector Class Design

**File:** `eleven_video/ui/image_model_selector.py`

```python
"""
Interactive Image Model Selection UI Component - Story 3.4

Provides user-friendly image model selection via Rich terminal prompts.
Uses GeminiAdapter.list_image_models() from Story 3.2 to fetch models.
"""
from typing import Optional, List, TYPE_CHECKING

from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

from eleven_video.ui.console import console
from eleven_video.models.domain import ImageModelInfo

if TYPE_CHECKING:
    from eleven_video.api.gemini import GeminiAdapter


class ImageModelSelector:
    """Interactive image model selection UI component.
    
    Displays available image models and prompts user to select one.
    Falls back to default model on errors or non-TTY environments.
    """
    
    DEFAULT_MODEL_ID = "gemini-2.5-flash-image"
    DEFAULT_MODEL_NAME = "Gemini 2.5 Flash Image"
    
    def __init__(self, adapter: "GeminiAdapter") -> None:
        """Initialize ImageModelSelector with Gemini adapter.
        
        Args:
            adapter: GeminiAdapter instance for fetching models
        """
        self._adapter = adapter
    
    def select_model_interactive(self) -> Optional[str]:
        """Display image model list and prompt user for selection.
        
        Returns:
            Model ID string, or None to use default model.
        """
        # R-004 mitigation: Non-TTY fallback
        if not console.is_terminal:
            console.print("[dim]Non-interactive mode detected. Using default image model.[/dim]")
            return None
        
        try:
            models = self._adapter.list_image_models(use_cache=True)
        except Exception as e:
            console.print(f"[yellow]⚠️ Could not fetch image model list: {e}[/yellow]")
            console.print("[dim]Using default image model...[/dim]")
            return None
        
        if not models:
            console.print("[yellow]No image models available. Using default.[/yellow]")
            return None
        
        self._display_model_list(models)
        return self._get_user_selection(models)
    
    def _display_model_list(self, models: List[ImageModelInfo]) -> None:
        """Display numbered image model options.
        
        Args:
            models: List of ImageModelInfo objects to display
        """
        console.print(Panel(
            "[bold cyan]Available Image Models[/bold cyan]",
            border_style="cyan"
        ))
        
        table = Table(show_header=False, box=None)
        table.add_column("#", style="cyan", width=4)
        table.add_column("Name", style="white")
        table.add_column("Description", style="dim")
        
        # Default option
        table.add_row("0", f"Default ({self.DEFAULT_MODEL_NAME})", "recommended")
        
        for i, model in enumerate(models, start=1):
            table.add_row(str(i), model.name, model.description or "")
        
        console.print(table)
    
    def _get_user_selection(self, models: List[ImageModelInfo]) -> Optional[str]:
        """Prompt user for image model selection and return model_id.
        
        Args:
            models: List of ImageModelInfo objects to select from
            
        Returns:
            Selected model_id, or None for default model
        """
        choice = Prompt.ask(
            "\n[bold cyan]Select an image model number[/bold cyan]",
            default="0"
        )
        
        try:
            index = int(choice)
            if index == 0:
                return None  # Use default
            if 1 <= index <= len(models):
                return models[index - 1].model_id
            console.print("[yellow]Invalid selection. Using default.[/yellow]")
            return None
        except ValueError:
            console.print("[yellow]Invalid input. Using default.[/yellow]")
            return None
```

### CLI Integration Points

**File to modify:** `eleven_video/main.py`

Add `--image-model` option and image model selection before `pipeline.generate()`:

```python
@app.command()
def generate(
    prompt: Optional[str] = typer.Option(None, "--prompt", "-p", help="Text prompt..."),
    voice: Optional[str] = typer.Option(None, "--voice", "-v", help="Voice ID to use"),
    image_model: Optional[str] = typer.Option(None, "--image-model", "-m", help="Image model ID"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
):
    # ... existing voice selection from Story 3.3 ...
    
    # Interactive image model selection if not provided via --image-model
    if image_model is None:
        from eleven_video.ui.image_model_selector import ImageModelSelector
        gemini_adapter = GeminiAdapter(settings=settings)
        try:
            selector = ImageModelSelector(gemini_adapter)
            image_model = selector.select_model_interactive()
        except Exception as e:
            console.print(f"[yellow]⚠️ Image model selection unavailable: {e}[/yellow]")
            console.print("[dim]Continuing with default image model...[/dim]")
    
    # Pass image_model to pipeline
    video = pipeline.generate(prompt=prompt, voice_id=voice, image_model_id=image_model)
```

### Testing Requirements

**Test IDs from Epic 3 Test Design:**

| Test ID | Description | Priority |
|---------|-------------|----------|
| 3.4-COMP-001 | Image model selection menu rendering | P1 |

**Test Groups:**

| Group | Tests | Description | Test ID |
|-------|-------|-------------|---------|
| TestImageModelSelectorDisplay | 3 | `_display_model_list()` formatting tests | 3.4-COMP-001 |
| TestImageModelSelectorInput | 4 | `_get_user_selection()` input handling | 3.4-COMP-001 |
| TestImageModelSelectorInteractive | 3 | Full `select_model_interactive()` flow | 3.4-COMP-001 |
| TestImageModelSelectorErrorHandling | 2 | API failure and empty list handling | - |
| TestNonTTYFallback | 2 | Non-TTY environment detection (R-004) | - |
| TestCLIImageModelIntegration | 3 | `generate` command image model selection flow | - |

**Test file locations (mirroring Story 3.3 split pattern):**
- `tests/ui/test_image_model_selector_display.py` - Display tests (NEW)
- `tests/ui/test_image_model_selector_input.py` - Input handling tests (NEW)
- `tests/ui/conftest.py` - Add `ImageModelInfo` fixtures (MODIFY)
- `tests/ui/test_cli_generate.py` - Add integration tests for image model selection

**Coverage target:** ≥80% for new code

**Test command:** `uv run pytest tests/ui/test_image_model_selector_display.py tests/ui/test_image_model_selector_input.py -v`

### Required Conftest Fixtures (tests/ui/conftest.py)

Add these fixtures mirroring the voice selector pattern:

```python
# =============================================================================
# Fixtures for ImageModelSelector (Story 3.4)
# =============================================================================

def create_image_model_info(
    model_id: str = "gemini-2.5-flash-image",
    name: str = "Gemini 2.5 Flash Image",
    description: Optional[str] = "Fast image generation",
    supports_image_generation: bool = True
):
    """Factory function for creating ImageModelInfo test data."""
    from eleven_video.models.domain import ImageModelInfo
    return ImageModelInfo(
        model_id=model_id,
        name=name,
        description=description,
        supports_image_generation=supports_image_generation
    )


@pytest.fixture
def mock_gemini_adapter():
    """Create a mock GeminiAdapter for ImageModelSelector testing."""
    return Mock()


@pytest.fixture
def image_model_selector(mock_gemini_adapter):
    """Create an ImageModelSelector instance with mock adapter."""
    from eleven_video.ui.image_model_selector import ImageModelSelector
    return ImageModelSelector(mock_gemini_adapter)


@pytest.fixture
def sample_image_models():
    """Return a standard list of 3 sample image models for testing."""
    from eleven_video.models.domain import ImageModelInfo
    return [
        ImageModelInfo(model_id="gemini-2.5-flash-image", name="Gemini 2.5 Flash Image", description="Fast generation"),
        ImageModelInfo(model_id="gemini-3-flash", name="Gemini 3 Flash", description="Latest model"),
        ImageModelInfo(model_id="imagen-3.0-generate-001", name="Imagen 3", description="Highest quality"),
    ]


@pytest.fixture
def single_image_model():
    """Return a single image model for minimal testing."""
    from eleven_video.models.domain import ImageModelInfo
    return [ImageModelInfo(model_id="gemini-2.5-flash-image", name="Test Model", description="Test")]
```

### Project Structure Notes

**Files to create:**
- `eleven_video/ui/image_model_selector.py` - ImageModelSelector class (NEW)
- `tests/ui/test_image_model_selector_display.py` - Display unit tests (NEW)
- `tests/ui/test_image_model_selector_input.py` - Input handling tests (NEW)

**Files to modify:**
- `eleven_video/main.py` - Add `--image-model` / `-i` option, add image model selection in `generate()` command
- `eleven_video/orchestrator.py` - Add `image_model_id` parameter to `VideoPipeline.generate()`
- `eleven_video/ui/__init__.py` - Export ImageModelSelector
- `tests/ui/conftest.py` - Add `ImageModelInfo` fixtures mirroring voice fixtures

**Note:** The adapter already accepts `model_id` parameter (Story 3.2), but the orchestrator needs to pass it through.

### Error Handling Pattern

Match existing error handling in `main.py` and `VoiceSelector`:

```python
try:
    # Image model selection
except Exception as e:
    console.print(f"[yellow]⚠️ Image model selection unavailable: {e}[/yellow]")
    console.print("[dim]Continuing with default image model...[/dim]")
    image_model = None  # Graceful degradation
```

### Risk Mitigation (from test-design-epic-3.md)

**Risks addressed in this story:**

| Risk ID | Description | Score | Story Mitigation |
|---------|-------------|-------|------------------|
| R-004 | Interactive prompts fail in non-TTY environments | 4 | Detect non-TTY via `console.is_terminal`, skip selection with warning, use default |
| R-001 | Gemini image model API changes/deprecation | 6 | Implemented in Story 3.2 - adapter pattern with model validation, graceful fallback |

**Source:** [docs/test-design-epic-3.md#Risk Assessment]

### Previous Story Intelligence

**Story 3.2 (Backend - Custom Image Generation Model Selection):**
- `list_image_models()` implemented with caching (60s TTL)
- Returns `List[ImageModelInfo]` with `model_id`, `name`, `description`, `supports_image_generation`
- Retry logic handles transient API failures
- `validate_image_model_id()` available for validation if needed
- `generate_images()` accepts `model_id` parameter

**Story 3.3 (VoiceSelector - Pattern to Follow):**
- Created `VoiceSelector` class with `select_voice_interactive()`, `_display_voice_list()`, `_get_user_selection()` methods
- Implemented non-TTY fallback using `console.is_terminal` check
- Error handling returns None (default voice) on API failures
- 14 unit tests in `tests/ui/test_voice_selector.py`
- Exported from `eleven_video.ui` module

**Key Pattern: Mirror VoiceSelector exactly** - The code structure should be nearly identical, just changing voice→image model terminology.

### References

- [Source: eleven_video/api/gemini.py#list_image_models] - Story 3.2 image model listing (lines 281-345)
- [Source: eleven_video/api/gemini.py#generate_images] - Image generation with model_id param (lines 359-426)
- [Source: eleven_video/ui/voice_selector.py] - Story 3.3 VoiceSelector to mirror
- [Source: eleven_video/ui/console.py] - Shared Rich console instance
- [Source: eleven_video/models/domain.py#ImageModelInfo] - Story 3.2 domain model
- [Source: eleven_video/main.py#generate] - CLI command to modify
- [Source: docs/sprint-artifacts/epic-3-stories/story-3-2-custom-image-generation-model-selection.md] - Story 3.2 implementation reference
- [Source: docs/sprint-artifacts/epic-3-stories/story-3-3-interactive-voice-selection-prompts.md] - Story 3.3 implementation to mirror
- [Source: docs/architecture/core-architectural-decisions.md#Consensus Decisions] - Hexagonal architecture
- [Source: docs/architecture/project-context.md] - Use `uv run pytest` for testing
- [Source: docs/test-design-epic-3.md#3.4-COMP-001] - Test IDs for this story
- [Source: docs/epics.md#Story 3.4] - Original story requirements

## Dev Agent Record

### Context Reference

- ATDD tests: `tests/ui/test_image_model_selector_display.py`, `tests/ui/test_image_model_selector_input.py`

### Agent Model Used

Gemini 2.5 Pro (Antigravity)

### Debug Log References

N/A

### Completion Notes List

- Created `ImageModelSelector` class with `select_model_interactive()`, `_display_model_list()`, `_get_user_selection()` methods
- Implemented non-TTY fallback using `console.is_terminal` check
- Error handling returns None (default model) on API failures or empty model list
- All 20 ATDD unit tests passing in `tests/ui/test_image_model_selector_*.py`
- Exported `ImageModelSelector` from `eleven_video.ui` module
- Updated `VideoPipeline.generate()` to accept and pass `image_model_id` parameter
- Added `--image-model` / `-m` CLI option to `generate` command
- Updated existing CLI generate tests to include new `image_model_id` parameter
- Pattern mirrors Story 3.3 (VoiceSelector) exactly as specified

### File List

- `eleven_video/ui/image_model_selector.py` (NEW) - ImageModelSelector class
- `eleven_video/ui/__init__.py` (MODIFIED) - Added ImageModelSelector export
- `eleven_video/orchestrator/video_pipeline.py` (MODIFIED) - Added image_model_id parameter to generate()
- `eleven_video/main.py` (MODIFIED) - Added --image-model option and interactive selection
- `tests/ui/test_image_model_selector_display.py` (NEW via ATDD) - 7 display tests
- `tests/ui/test_image_model_selector_input.py` (NEW via ATDD) - 13 input/error/fallback tests
- `tests/ui/conftest.py` (MODIFIED via ATDD) - Added ImageModelInfo fixtures
- `tests/ui/test_cli_generate.py` (MODIFIED) - Updated assertions for image_model_id param, added AC#5 test

## Senior Developer Review (AI)

**Reviewer:** Antigravity (Gemini 2.5 Pro)  
**Date:** 2025-12-19  
**Verdict:** ✅ APPROVED

### Review Findings Summary

| Severity | Count | Status |
|----------|-------|--------|
| High | 1 | ✅ Fixed |
| Medium | 2 | ✅ Fixed (1 deferred - git staging) |
| Low | 2 | ✅ Fixed |

### Fixes Applied

1. **H-001** [FIXED]: Added `test_cli_generate_with_image_model_flag` test for AC #5 coverage
2. **M-001** [INFO]: Untracked files - user should `git add` story files
3. **M-002** [FIXED]: Added `gemini_adapter.close()` in finally block to prevent resource leak
4. **L-001** [FIXED]: Updated test docstring to reference Story 3.4

### Acceptance Criteria Verification

- AC #1: ✅ Display numbered list - verified in `_display_model_list()` 
- AC #2: ✅ Select by number - verified in `_get_user_selection()`
- AC #3: ✅ API failure fallback - verified in `select_model_interactive()`
- AC #4: ✅ Default option [0] - verified at line 80
- AC #5: ✅ Skip with --image-model flag - verified in CLI and tested

### Test Results

- Total tests: 23 passing
- Coverage: All AC test IDs covered (3.4-COMP-001, 3.4-UNIT-001 to 010, 3.4-AUTO-001 to 010)

## Change Log

- 2025-12-19: Story 3.4 implementation complete (Dev Agent)
- 2025-12-19: Code review passed - 4 issues fixed (Senior Dev Review AI)

