# Story 3.5: Gemini Text Generation Model Selection

**FR Coverage:** FR19 (Users can select from available Gemini text generation models through interactive prompts), FR24.1, FR36.1

Status: DONE

## Story

As a user,
I want to select from available Gemini text generation models through interactive prompts,
so that I can control the style and quality of the generated script.

## Acceptance Criteria

1. **Given** I am in an interactive session generating a video, **When** prompted to select a Gemini model, **Then** the tool displays a numbered list of available text generation model options.

2. **Given** I see the Gemini model list, **When** I select a model by number, **Then** my selection is used for script generation.

> [!NOTE]
> Gemini model selection by name search is deferred to P2 (R-008 mitigation). For MVP, numeric selection is sufficient.

3. **Given** the Gemini model listing API fails, **When** I expect to see models, **Then** the system shows a helpful error message and falls back to the default model with a warning.

4. **Given** I run `eleven-video generate` without the `--gemini-model` flag, **When** I am prompted to select a Gemini model, **Then** I see an option to use the default model (e.g., "[0] Use default model (gemini-2.5-flash-lite)").

5. **Given** I run `eleven-video generate --gemini-model <id>`, **When** I specify a Gemini model via CLI flag, **Then** the interactive Gemini model prompt is skipped.

## Tasks / Subtasks

- [x] Task 1: Add `GeminiModelInfo` domain model (AC: #1)
  - [x] 1.1: Add `GeminiModelInfo` dataclass to `eleven_video/models/domain.py`
  - [x] 1.2: Include fields: `model_id`, `name`, `description`, `supports_text_generation`
  - [x] 1.3: Write unit tests for `GeminiModelInfo` creation

- [x] Task 2: Add `list_text_models()` method to GeminiAdapter (AC: #1)
  - [x] 2.1: Add `_text_model_cache` attribute similar to `_image_model_cache`
  - [x] 2.2: Add `_text_model_cache_ttl` attribute with 60-second TTL
  - [x] 2.3: Implement `list_text_models(use_cache: bool = False)` method
  - [x] 2.4: Implement `_list_text_models_with_retry()` with retry logic
  - [x] 2.5: Filter models to only include text-generation capable models (look for `gemini` prefix, exclude `image` models)
  - [x] 2.6: Write unit tests for `list_text_models()` and caching behavior

- [x] Task 3: Add `validate_text_model_id()` method to GeminiAdapter (AC: #3)
  - [x] 3.1: Implement `validate_text_model_id(model_id: str) -> bool` method
  - [x] 3.2: Use cached model list for validation
  - [x] 3.3: Write unit tests for model ID validation

- [x] Task 4: Create Gemini model selection prompt helper (AC: #1, #4)
  - [x] 4.1: Create `eleven_video/ui/gemini_model_selector.py` with `GeminiModelSelector` class
  - [x] 4.2: Implement `_display_model_list(models: list[GeminiModelInfo])` method using Rich library
  - [x] 4.3: Display numbered list with format: "[1] Model Name (description)"
  - [x] 4.4: Add "[0] Use default model (gemini-2.5-flash-lite)" as first option
  - [x] 4.5: Write unit tests for `GeminiModelSelector._display_model_list()`

- [x] Task 5: Implement Gemini model selection input handling (AC: #2)
  - [x] 5.1: Add `select_model(models: list[GeminiModelInfo]) -> Optional[str]` method
  - [x] 5.2: Accept numeric input (1-N) to select by index
  - [x] 5.3: Accept "0" for default model (returns None, meaning use default)
  - [x] 5.4: Return the selected `model_id` string
  - [x] 5.5: Write unit tests for input handling (mock Rich.Prompt)

- [x] Task 6: Add error handling for model listing failures (AC: #3)
  - [x] 6.1: Wrap `GeminiAdapter.list_text_models()` call in try/except
  - [x] 6.2: On failure, print warning message using Rich console
  - [x] 6.3: Return None to use default model on failure
  - [x] 6.4: Write unit tests for error handling path

- [x] Task 7: Integrate Gemini model selection into generate command (AC: #4, #5)
  - [x] 7.1: Add `--gemini-model` / `-gm` CLI option to `generate()` function in `main.py` (NOTE: `-g` is already used for `--gemini-key`)
  - [x] 7.2: If None, call Gemini model selection flow before pipeline.generate() (via GeminiModelSelector)
  - [x] 7.3: Skip Gemini model prompt if `--gemini-model` flag was provided
  - [x] 7.4: Update `GeminiAdapter.generate_script()` to accept `model_id` parameter
  - [x] 7.5: Update `VideoPipeline.generate()` to accept `gemini_model_id` parameter and pass to adapter
  - [x] 7.6: Pass selected model_id through pipeline to `adapter.generate_script(model_id=...)`
  - [x] 7.7: Write integration tests mocking both list_text_models and pipeline

- [x] Task 8: Export GeminiModelSelector from ui module (AC: all)
  - [x] 8.1: Update `eleven_video/ui/__init__.py` to export `GeminiModelSelector`
  - [x] 8.2: Verify import works from main.py

- [x] Task 9: Add non-TTY fallback (R-004 mitigation)
  - [x] 9.1: Detect non-TTY environment using `console.is_terminal`
  - [x] 9.2: If non-TTY, skip Gemini model selection prompt and use default model with warning
  - [x] 9.3: Write unit tests for non-TTY detection and fallback
  - [x] 9.4: Document behavior in --help output (via code docstrings)

## Validation Summary

> **Adversarial Validation Completed:** 2025-12-20

### Verified Against Sources
- ✅ `docs/epics.md#Story 3.5` - Story statement and AC match
- ✅ `docs/test-design-epic-3.md` - Test IDs (3.5-UNIT-001, 3.5-COMP-001) and risk mitigations (R-002, R-004) aligned
- ✅ `docs/prd.md` - FR19, FR24.1, FR36.1 coverage verified
- ✅ `eleven_video/ui/image_model_selector.py` - Pattern correctly mirrored
- ✅ `eleven_video/api/gemini.py` - Existing structure analyzed

### Issues Found and Fixed
1. **CLI flag conflict** - `-g` already used for `--gemini-key`. Changed to no short option.
2. **Missing `_generate_with_retry` signature update** - Added guidance to update method signature.
3. **Cache initialization location** - Clarified cache attrs go in `__init__`, not class level.
4. **Missing import statement** - Added `GeminiModelInfo` to imports in gemini.py guidance.

## Dev Notes

### Scope Clarification

> ⚠️ **UI/CLI + Backend story.** This story implements:
> 1. Backend: `list_text_models()` method in GeminiAdapter (analogous to `list_image_models()`)
> 2. UI: `GeminiModelSelector` class for interactive model selection
> 3. CLI: `--gemini-model` flag and pipeline integration
>
> **Pattern:** Mirrors Stories 3.2 + 3.4 combined approach but for text generation models.

### Architecture Compliance

**Pattern:** Hexagonal (Ports & Adapters)
- CLI (`main.py`) is in the "driving adapter" layer
- `GeminiModelSelector` is a UI helper in the presentation layer
- `GeminiAdapter.list_text_models()` is in the "driven adapter" layer

**Source:** [docs/architecture/core-architectural-decisions.md#Consensus Decisions]

### Pattern Mirror: Stories 3.2 and 3.4

This story **combines patterns from Story 3.2 (backend) and Story 3.4 (UI)**:

| Pattern Source | This Story |
|----------------|------------|
| `list_image_models()` in Story 3.2 | `list_text_models()` method |
| `ImageModelInfo` domain model | `GeminiModelInfo` domain model |
| `ImageModelSelector` class (Story 3.4) | `GeminiModelSelector` class |
| `--image-model` CLI flag | `--gemini-model` CLI flag |
| `image_model_id` pipeline param | `gemini_model_id` pipeline param |

**Follow Story 3.2 + 3.4 implementation patterns exactly** - the code structure should be nearly identical.

### Existing GeminiAdapter Analysis

The `GeminiAdapter` already has:

```python
# From eleven_video/api/gemini.py

# Constants to update
DEFAULT_MODEL = "gemini-2.5-flash-lite"  # Used in generate_script()

# Existing pattern for image models (reuse for text models)
def list_image_models(self, use_cache: bool = False) -> List[ImageModelInfo]:
    """List available image generation models from Gemini API."""
    # Pattern to replicate for list_text_models()

def generate_script(
    self,
    prompt: str,
    progress_callback: Optional[Callable[[str], None]] = None
) -> Script:
    """Generate a video script from a text prompt using Gemini."""
    # Need to add model_id parameter here!
    response = self._genai_client.models.generate_content(
        model=self.DEFAULT_MODEL,  # <- Need to allow override
        contents=prompt
    )
```

**Key Change:** Update `generate_script()` to accept `model_id` parameter with fallback to `DEFAULT_MODEL`.

### GeminiModelInfo Domain Model

**File to modify:** `eleven_video/models/domain.py`

```python
@dataclass
class GeminiModelInfo:
    """Gemini text model information (Story 3.5 - FR19).
    
    Attributes:
        model_id: Unique identifier for the model (e.g., "gemini-2.5-flash").
        name: Human-readable display name of the model.
        description: Optional description of the model's capabilities.
        supports_text_generation: Whether the model supports text generation.
    """
    model_id: str
    name: str
    description: Optional[str] = None
    supports_text_generation: bool = True
```

**Source:** [eleven_video/models/domain.py#ImageModelInfo] - Pattern to replicate

### list_text_models() Implementation

**File to modify:** `eleven_video/api/gemini.py`

> [!IMPORTANT]
> Add import for `GeminiModelInfo` at top of file:
> ```python
> from eleven_video.models.domain import Script, Image, ImageModelInfo, GeminiModelInfo
> ```

**In `__init__` method, add cache attributes (after line ~65):**

```python
# Text model cache (Story 3.5 - add after _image_model_cache)
self._text_model_cache: Optional[tuple[List[GeminiModelInfo], float]] = None
self._text_model_cache_ttl: int = 60  # 60 seconds TTL
```

**Add after `list_image_models()` method:**

```python
def list_text_models(self, use_cache: bool = False) -> List[GeminiModelInfo]:
    """List available text generation models from Gemini API.
    
    Args:
        use_cache: If True, return cached models if available and not expired.
        
    Returns:
        List of GeminiModelInfo domain models with model metadata.
        
    Raises:
        GeminiAPIError: If API call fails.
    """
    # Check cache if enabled
    if use_cache and self._text_model_cache:
        cached_models, cache_time = self._text_model_cache
        if time.perf_counter() - cache_time < self._text_model_cache_ttl:
            return cached_models
    
    try:
        models = self._list_text_models_with_retry()
        # Cache the results
        self._text_model_cache = (models, time.perf_counter())
        return models
    except Exception as e:
        error_msg = self._format_error(e)
        raise GeminiAPIError(error_msg)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    reraise=True
)
def _list_text_models_with_retry(self) -> List[GeminiModelInfo]:
    """Internal method with retry logic for listing text models.
    
    Filters models to only include text-generation capable models.
    Excludes image-specific models.
    """
    models_response = self._genai_client.models.list()
    
    text_models: List[GeminiModelInfo] = []
    for model in models_response:
        model_name = getattr(model, 'name', '') or ''
        display_name = getattr(model, 'display_name', model_name) or model_name
        description = getattr(model, 'description', None)
        
        # Check if model is text-generation capable
        # Include: gemini-* models that are NOT image-specific
        is_text_capable = (
            'gemini' in model_name.lower() and
            'image' not in model_name.lower() and
            'imagen' not in model_name.lower() and
            'embedding' not in model_name.lower()
        )
        
        if is_text_capable:
            model_id = model_name.replace('models/', '') if model_name.startswith('models/') else model_name
            
            text_models.append(GeminiModelInfo(
                model_id=model_id,
                name=display_name,
                description=description,
                supports_text_generation=True
            ))
    
    return text_models

def validate_text_model_id(self, model_id: str) -> bool:
    """Validate if a text model ID exists in available models.
    
    Args:
        model_id: The text model ID to validate.
        
    Returns:
        True if the model ID exists, False otherwise.
    """
    available_models = self.list_text_models(use_cache=True)
    return any(model.model_id == model_id for model in available_models)
```

### GeminiModelSelector Class Design

**File:** `eleven_video/ui/gemini_model_selector.py`

```python
"""
Interactive Gemini Model Selection UI Component - Story 3.5

Provides user-friendly Gemini text model selection via Rich terminal prompts.
Uses GeminiAdapter.list_text_models() to fetch available models.
"""
from typing import Optional, List, TYPE_CHECKING

from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

from eleven_video.ui.console import console
from eleven_video.models.domain import GeminiModelInfo

if TYPE_CHECKING:
    from eleven_video.api.gemini import GeminiAdapter


class GeminiModelSelector:
    """Interactive Gemini model selection UI component.
    
    Displays available Gemini text models and prompts user to select one.
    Falls back to default model on errors or non-TTY environments.
    """
    
    DEFAULT_MODEL_ID = "gemini-2.5-flash-lite"
    DEFAULT_MODEL_NAME = "Gemini 2.5 Flash Lite"
    
    def __init__(self, adapter: "GeminiAdapter") -> None:
        """Initialize GeminiModelSelector with Gemini adapter.
        
        Args:
            adapter: GeminiAdapter instance for fetching models
        """
        self._adapter = adapter
    
    def select_model_interactive(self) -> Optional[str]:
        """Display Gemini model list and prompt user for selection.
        
        Returns:
            Model ID string, or None to use default model.
        """
        # R-004 mitigation: Non-TTY fallback
        if not console.is_terminal:
            console.print("[dim]Non-interactive mode detected. Using default Gemini model.[/dim]")
            return None
        
        try:
            models = self._adapter.list_text_models(use_cache=True)
        except Exception as e:
            console.print(f"[yellow]⚠️ Could not fetch Gemini model list: {e}[/yellow]")
            console.print("[dim]Using default Gemini model...[/dim]")
            return None
        
        if not models:
            console.print("[yellow]No Gemini models available. Using default.[/yellow]")
            return None
        
        self._display_model_list(models)
        return self._get_user_selection(models)
    
    def _display_model_list(self, models: List[GeminiModelInfo]) -> None:
        """Display numbered Gemini model options.
        
        Args:
            models: List of GeminiModelInfo objects to display
        """
        console.print(Panel(
            "[bold cyan]Available Gemini Text Models[/bold cyan]",
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
    
    def _get_user_selection(self, models: List[GeminiModelInfo]) -> Optional[str]:
        """Prompt user for Gemini model selection and return model_id.
        
        Args:
            models: List of GeminiModelInfo objects to select from
            
        Returns:
            Selected model_id, or None for default model
        """
        choice = Prompt.ask(
            "\n[bold cyan]Select a Gemini model number[/bold cyan]",
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

Add `--gemini-model` option and Gemini model selection before `pipeline.generate()`:

> [!WARNING]
> `-g` is already used for `--gemini-key` in `main.py` line 50. Use `-gm` or no short option.

```python
@app.command()
def generate(
    prompt: Optional[str] = typer.Option(None, "--prompt", "-p", help="Text prompt..."),
    voice: Optional[str] = typer.Option(None, "--voice", "-v", help="Voice ID to use"),
    image_model: Optional[str] = typer.Option(None, "--image-model", "-m", help="Image model ID"),
    gemini_model: Optional[str] = typer.Option(None, "--gemini-model", help="Gemini text model ID"),  # No short option to avoid conflict
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
):
    # ... existing voice and image model selection ...
    
    # Interactive Gemini model selection if not provided via --gemini-model (Story 3.5)
    if gemini_model is None:
        from eleven_video.ui.gemini_model_selector import GeminiModelSelector
        gemini_adapter = GeminiAdapter(settings=settings)
        try:
            selector = GeminiModelSelector(gemini_adapter)
            gemini_model = selector.select_model_interactive()
        except Exception as e:
            console.print(f"[yellow]⚠️ Gemini model selection unavailable: {e}[/yellow]")
            console.print("[dim]Continuing with default Gemini model...[/dim]")
            gemini_model = None  # Graceful degradation
        finally:
            asyncio.run(gemini_adapter.close())
    
    # Pass gemini_model to pipeline
    video = pipeline.generate(
        prompt=prompt, 
        voice_id=voice, 
        image_model_id=image_model, 
        gemini_model_id=gemini_model
    )
```

### Updating generate_script() to Accept model_id

**File to modify:** `eleven_video/api/gemini.py`

```python
def generate_script(
    self,
    prompt: str,
    progress_callback: Optional[Callable[[str], None]] = None,
    model_id: Optional[str] = None,  # NEW PARAMETER
    warning_callback: Optional[Callable[[str], None]] = None  # NEW PARAMETER
) -> Script:
    """Generate a video script from a text prompt using Gemini.
    
    Args:
        prompt: The text prompt describing the desired video.
        progress_callback: Optional callback for progress updates.
        model_id: Optional Gemini model ID (uses default if not provided).
        warning_callback: Optional callback for warnings (e.g., invalid model fallback).
        
    Returns:
        Script domain model with generated content.
        
    Raises:
        ValidationError: If prompt is empty or invalid.
        GeminiAPIError: If API call fails.
    """
    # ... existing validation ...
    
    # Story 3.5: Validate model_id and fallback if invalid
    effective_model_id = self.DEFAULT_MODEL
    if model_id:
        if self.validate_text_model_id(model_id):
            effective_model_id = model_id
        else:
            # Invalid model ID - fallback to default with warning
            if warning_callback:
                warning_callback(
                    f"Invalid Gemini model ID '{model_id}'. "
                    f"Falling back to default model '{self.DEFAULT_MODEL}'."
                )
    
    try:
        result = self._generate_with_retry(prompt, effective_model_id)  # Pass model_id
        # ...
```

> [!IMPORTANT]
> **Also update `_generate_with_retry` signature** (currently at line ~222):
> ```python
> def _generate_with_retry(self, prompt: str, model_id: Optional[str] = None) -> Script:
>     """Internal method with retry logic for API calls.
>     
>     Args:
>         prompt: The text prompt.
>         model_id: Optional model ID (uses DEFAULT_MODEL if not provided).
>     """
>     effective_model = model_id or self.DEFAULT_MODEL
>     response = self._genai_client.models.generate_content(
>         model=effective_model,
>         contents=prompt
>     )
>     return Script(content=response.candidates[0].content.parts[0].text)
> ```

### Testing Requirements

**Test IDs from Epic 3 Test Design:**

| Test ID | Description | Priority |
|---------|-------------|----------|
| 3.5-UNIT-001 | Gemini model parameter in script generation | P0 |
| 3.5-COMP-001 | Gemini model selection menu rendering | P1 |

**Test Groups:**

| Group | Tests | Description | Test ID |
|-------|-------|-------------|---------|
| TestGeminiModelInfo | 2 | Domain model creation | - |
| TestListTextModels | 4 | `list_text_models()` and caching | 3.5-UNIT-001 |
| TestValidateTextModelId | 3 | `validate_text_model_id()` | - |
| TestGeminiModelSelectorDisplay | 3 | `_display_model_list()` formatting | 3.5-COMP-001 |
| TestGeminiModelSelectorInput | 4 | `_get_user_selection()` input handling | 3.5-COMP-001 |
| TestGeminiModelSelectorInteractive | 3 | Full `select_model_interactive()` flow | 3.5-COMP-001 |
| TestGeminiModelSelectorErrorHandling | 2 | API failure and empty list handling | - |
| TestNonTTYFallback | 2 | Non-TTY environment detection (R-004) | - |
| TestCLIGeminiModelIntegration | 3 | `generate` command Gemini model selection flow | - |
| TestGenerateScriptWithModelId | 3 | `generate_script()` with model_id parameter | 3.5-UNIT-001 |

**Test file locations (mirroring Story 3.4 pattern):**
- `tests/api/test_gemini_text_models.py` - Backend tests for `list_text_models()` (NEW)
- `tests/ui/test_gemini_model_selector_display.py` - Display tests (NEW)
- `tests/ui/test_gemini_model_selector_input.py` - Input handling tests (NEW)
- `tests/ui/conftest.py` - Add `GeminiModelInfo` fixtures (MODIFY)
- `tests/ui/test_cli_generate.py` - Add integration tests for Gemini model selection (MODIFY)

**Coverage target:** ≥80% for new code

**Test command:** `uv run pytest tests/ui/test_gemini_model_selector_*.py tests/api/test_gemini_text_models.py -v`

### Required Conftest Fixtures (tests/ui/conftest.py)

Add these fixtures mirroring the image model selector pattern:

```python
# =============================================================================
# Fixtures for GeminiModelSelector (Story 3.5)
# =============================================================================

def create_gemini_model_info(
    model_id: str = "gemini-2.5-flash",
    name: str = "Gemini 2.5 Flash",
    description: Optional[str] = "Fast text generation",
    supports_text_generation: bool = True
):
    """Factory function for creating GeminiModelInfo test data."""
    from eleven_video.models.domain import GeminiModelInfo
    return GeminiModelInfo(
        model_id=model_id,
        name=name,
        description=description,
        supports_text_generation=supports_text_generation
    )


@pytest.fixture
def gemini_model_selector(mock_gemini_adapter):
    """Create a GeminiModelSelector instance with mock adapter."""
    from eleven_video.ui.gemini_model_selector import GeminiModelSelector
    return GeminiModelSelector(mock_gemini_adapter)


@pytest.fixture
def sample_gemini_models():
    """Return a standard list of 3 sample Gemini models for testing."""
    from eleven_video.models.domain import GeminiModelInfo
    return [
        GeminiModelInfo(model_id="gemini-2.5-flash", name="Gemini 2.5 Flash", description="Fast generation"),
        GeminiModelInfo(model_id="gemini-2.5-flash-lite", name="Gemini 2.5 Flash Lite", description="Ultra-fast, efficient"),
        GeminiModelInfo(model_id="gemini-2.5-pro", name="Gemini 2.5 Pro", description="Highest quality"),
    ]


@pytest.fixture
def single_gemini_model():
    """Return a single Gemini model for minimal testing."""
    from eleven_video.models.domain import GeminiModelInfo
    return [GeminiModelInfo(model_id="gemini-2.5-flash", name="Test Model", description="Test")]
```

### Project Structure Notes

**Files to create:**
- `eleven_video/ui/gemini_model_selector.py` - GeminiModelSelector class (NEW)
- `tests/api/test_gemini_text_models.py` - Backend unit tests (NEW)
- `tests/ui/test_gemini_model_selector_display.py` - Display unit tests (NEW)
- `tests/ui/test_gemini_model_selector_input.py` - Input handling tests (NEW)

**Files to modify:**
- `eleven_video/models/domain.py` - Add `GeminiModelInfo` dataclass
- `eleven_video/api/gemini.py` - Add `list_text_models()`, `validate_text_model_id()`, and update `generate_script()` to accept `model_id`
- `eleven_video/orchestrator/video_pipeline.py` - Add `gemini_model_id` parameter to `generate()`
- `eleven_video/main.py` - Add `--gemini-model` / `-g` option, add Gemini model selection in `generate()` command
- `eleven_video/ui/__init__.py` - Export GeminiModelSelector
- `tests/ui/conftest.py` - Add `GeminiModelInfo` fixtures mirroring image model fixtures

### Error Handling Pattern

Match existing error handling in `main.py` and previous selectors:

```python
try:
    # Gemini model selection
except Exception as e:
    console.print(f"[yellow]⚠️ Gemini model selection unavailable: {e}[/yellow]")
    console.print("[dim]Continuing with default Gemini model...[/dim]")
    gemini_model = None  # Graceful degradation
```

### Risk Mitigation (from test-design-epic-3.md)

**Risks addressed in this story:**

| Risk ID | Description | Score | Story Mitigation |
|---------|-------------|-------|------------------|
| R-002 | Gemini model availability varies by API key/tier | 6 | Validate model availability at startup, show only available models in selection, fallback to default |
| R-004 | Interactive prompts fail in non-TTY environments | 4 | Detect non-TTY via `console.is_terminal`, skip selection with warning, use default |

**Source:** [docs/test-design-epic-3.md#Risk Assessment]

### Previous Story Intelligence

**Story 3.2 (Backend - Custom Image Model Selection):**
- `list_image_models()` implemented with caching (60s TTL) - **PATTERN TO REPLICATE**
- Returns `List[ImageModelInfo]` with `model_id`, `name`, `description`, `supports_image_generation`
- Retry logic handles transient API failures
- `validate_image_model_id()` available for validation if needed

**Story 3.4 (ImageModelSelector - UI Pattern to Follow):**
- Created `ImageModelSelector` class with `select_model_interactive()`, `_display_model_list()`, `_get_user_selection()` methods
- Implemented non-TTY fallback using `console.is_terminal` check
- Error handling returns None (default model) on API failures or empty model list
- 20 unit tests in `tests/ui/test_image_model_selector_*.py`
- Exported from `eleven_video.ui` module

**Key Pattern: Combine 3.2 (backend) + 3.4 (UI) approaches** - Same structure, just for text models instead of image models.

### References

- [Source: eleven_video/api/gemini.py#list_image_models] - Pattern to replicate for text models (lines 281-345)
- [Source: eleven_video/api/gemini.py#generate_script] - Method to update with model_id param (lines 168-214)
- [Source: eleven_video/ui/image_model_selector.py] - Story 3.4 ImageModelSelector to mirror
- [Source: eleven_video/ui/voice_selector.py] - Story 3.3 VoiceSelector pattern
- [Source: eleven_video/ui/console.py] - Shared Rich console instance
- [Source: eleven_video/models/domain.py#ImageModelInfo] - Pattern for GeminiModelInfo domain model
- [Source: eleven_video/main.py#generate] - CLI command to modify (lines 287-368)
- [Source: eleven_video/orchestrator/video_pipeline.py] - Pipeline to update with gemini_model_id
- [Source: docs/sprint-artifacts/epic-3-stories/story-3-2-custom-image-generation-model-selection.md] - Story 3.2 implementation reference
- [Source: docs/sprint-artifacts/epic-3-stories/story-3-4-interactive-image-model-selection-prompts.md] - Story 3.4 implementation to mirror
- [Source: docs/architecture/core-architectural-decisions.md#Consensus Decisions] - Hexagonal architecture
- [Source: docs/architecture/project-context.md] - Use `uv run pytest` for testing
- [Source: docs/test-design-epic-3.md#3.5-UNIT-001, #3.5-COMP-001] - Test IDs for this story
- [Source: docs/epics.md#Story 3.5] - Original story requirements
- [Source: docs/prd.md#FR19, #FR24.1, #FR36.1] - Functional requirements

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

Antigravity (Code Review Agent)

### Debug Log References

### Completion Notes List

- **2025-12-20**: Story reviewed via code-review workflow. All 9 tasks verified as implemented. 38 tests passing (35 API/UI + 3 CLI).
- **AC#1 Verified**: `GeminiModelSelector._display_model_list()` displays numbered list with Panel and Table
- **AC#2 Verified**: `_get_user_selection()` returns `model_id` for valid selections, `generate_script()` accepts model_id
- **AC#3 Verified**: Error handling returns `None` on API failure, fallback to default with warning callback
- **AC#4 Verified**: Default option `[0] Default (Gemini 2.5 Flash Lite)` shown as first row
- **AC#5 Verified**: `--gemini-model` flag in `main.py:generate()` passes value through, skipping interactive prompt
- **R-004 Mitigated**: Non-TTY detection via `console.is_terminal` check with message before return

### Senior Developer Review (AI)

**Outcome**: ✅ APPROVED with notes

**Issues Fixed in Review**:
1. Story status updated from `ready-for-dev` to `review`
2. All task checkboxes marked complete
3. Dev Agent Record populated with File List and Completion Notes

**Note**: Implementation is complete and test-verified. Story ready for `done` status after sprint-status sync.

### File List

**New Files Created:**
- `eleven_video/ui/gemini_model_selector.py` - GeminiModelSelector class (112 lines)
- `tests/api/test_gemini_text_models.py` - Backend unit tests (355 lines, 12 tests)
- `tests/ui/test_gemini_model_selector_display.py` - Display tests (141 lines, 6 tests)
- `tests/ui/test_gemini_model_selector_input.py` - Input handling tests (246 lines, 17 tests)

**Modified Files:**
- `eleven_video/models/domain.py` - Added `GeminiModelInfo` dataclass (lines 123-136)
- `eleven_video/api/gemini.py` - Added `list_text_models()`, `validate_text_model_id()`, `_text_model_cache`, updated `generate_script()` with `model_id` param
- `eleven_video/orchestrator/video_pipeline.py` - Added `gemini_model_id` parameter to `generate()` method
- `eleven_video/main.py` - Added `--gemini-model` CLI option, passes `gemini_model_id` to pipeline
- `eleven_video/ui/__init__.py` - Exported `GeminiModelSelector`
- `tests/ui/conftest.py` - Added GeminiModelSelector fixtures (lines 186-259)
- `tests/ui/test_cli_generate.py` - Updated tests to include `gemini_model_id` parameter
