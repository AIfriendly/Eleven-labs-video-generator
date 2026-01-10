---
project_name: 'Eleven-labs-AI-Video'
user_name: 'Revenant'
date: '2025-12-20'
sections_completed: ['technology_stack', 'critical_rules', 'patterns', 'testing']
---

# Project Context for AI Agents

_Critical rules and patterns for implementing code in this project. Focus on unobvious details._

---

## Technology Stack & Versions

| Component | Technology | Version | Notes |
|-----------|------------|---------|-------|
| Language | Python | ≥3.9 | Use type hints |
| CLI | Typer | Latest | With `rich_markup_mode="rich"` |
| Terminal UI | Rich | Latest | Use shared `console` instance |
| HTTP | HTTPX | ≥0.25.0 | Async methods |
| Retry | Tenacity | ≥8.2.0 | Exponential backoff |
| Settings | Pydantic-Settings | Latest | `.env` file support |
| Video | MoviePy | ≥1.0.3 | FFmpeg required |
| AI Text/Images | google-genai | ≥1.0.0 | Gemini API |
| AI TTS | elevenlabs | ≥1.0.0 | ElevenLabs SDK |
| Linting | Ruff | py39 target | Line length 120 |
| Testing | pytest | Latest | With pytest-asyncio, pytest-mock |

---

## Critical Implementation Rules

### 1. Console Instance (NEVER create new)

```python
# ✅ CORRECT - use shared console
from eleven_video.ui.console import console
console.print("[green]Success[/green]")

# ❌ WRONG - never create new Console
from rich.console import Console
console = Console()  # DON'T DO THIS
```

### 2. API Adapter Pattern

All external APIs must use adapter classes in `eleven_video/api/`:

```python
class MyAdapter:
    def __init__(self, api_key: str = None, settings: Settings = None):
        # Accept both direct key and settings object
        
    async def some_api_call(self) -> Result:
        # All API calls are async
        
    async def close(self):
        # Always implement close() for cleanup
```

### 3. UI Selector Pattern

Interactive selectors in `eleven_video/ui/` must follow:

```python
class MySelector:
    def __init__(self, adapter: ApiAdapter):
        self._adapter = adapter
    
    def select_interactive(self) -> Optional[str]:
        # Non-TTY fallback is REQUIRED
        if not console.is_terminal:
            console.print("[dim]Non-interactive mode. Using default.[/dim]")
            return None
        
        self._display_options()
        return self._get_user_selection()
```

### 4. Error Handling Pattern

Graceful degradation with yellow warnings:

```python
try:
    result = selector.select_interactive()
except Exception as e:
    console.print(f"[yellow]⚠️ Selection unavailable: {e}[/yellow]")
    console.print("[dim]Continuing with default...[/dim]")
    result = None  # Graceful degradation
```

### 5. Settings Access

```python
# ✅ CORRECT - through Settings class
from eleven_video.config import Settings
settings = Settings()
api_key = settings.elevenlabs_api_key.get_secret_value()

# ❌ WRONG - direct env access in application code
import os
api_key = os.getenv("ELEVENLABS_API_KEY")  # DON'T DO THIS
```

### 6. Async Adapter Cleanup

Always close adapters after use:

```python
adapter = ElevenLabsAdapter(settings=settings)
try:
    result = await adapter.some_call()
finally:
    await adapter.close()  # REQUIRED
```

---

## Architecture Rules

### Hexagonal (Ports & Adapters)

```
eleven_video/
├── api/           # Driven adapters (external APIs)
├── config/        # Infrastructure (settings, persistence)
├── models/        # Domain models (Script, Audio, Video)
├── orchestrator/  # Application services (VideoPipeline)
├── ui/            # Driving adapters (CLI, selectors)
├── processing/    # Infrastructure (FFmpeg, video handling)
├── constants/     # Shared constants
└── exceptions/    # Custom exceptions
```

**Rules:**
- Domain models have NO external dependencies
- Adapters depend on domain, not vice versa
- CLI (`main.py`) is a driving adapter
- External APIs are driven adapters

---

## Testing Rules

### Test File Naming

```
tests/
├── api/test_gemini.py           # API adapter tests
├── ui/test_voice_selector.py    # UI component tests
├── models/test_domain.py        # Domain model tests
├── cli/test_generate.py         # CLI integration tests
└── e2e/test_full_pipeline.py    # End-to-end tests
```

### Fixtures Location

- Global fixtures: `tests/conftest.py`
- Domain-specific: `tests/{domain}/conftest.py`
- Factory functions over fixture objects when possible

### Mocking Pattern

```python
# Mock at the adapter level, not internal implementations
@patch("eleven_video.api.gemini.GeminiAdapter.generate_script")
def test_pipeline(mock_generate):
    mock_generate.return_value = Script(content="Test")
    # ...
```

### Test Markers

```python
@pytest.mark.integration  # Requires API keys / external services
def test_real_api():
    pass
```

Run without integration: `pytest -m "not integration"`

---

## CLI Command Structure

```python
@app.command()
def my_command(
    required_arg: str = typer.Argument(..., help="Description"),
    optional_flag: Optional[str] = typer.Option(None, "--flag", "-f", help="Description"),
):
    """
    Command docstring shown in --help.
    """
    # Validation first
    if invalid:
        console.print("[red]Error message[/red]")
        raise typer.Exit(1)
    
    # Success message
    console.print("[green]✓ Success![/green]")
```

---

## Duration/Validation Constants

Valid durations: `[3, 5, 10]` minutes only.

```python
# In eleven_video/models/domain.py
DURATION_OPTIONS = [
    DurationOption(minutes=3, label="Short"),
    DurationOption(minutes=5, label="Standard"),
    DurationOption(minutes=10, label="Extended"),
]
DEFAULT_DURATION_MINUTES = 5
```

---

## Configuration Priority

1. **CLI flags** (`--voice`, `--duration`) - Highest
2. **JSON config defaults** (`~/.config/eleven-video/config.json`)
3. **Interactive prompts** (if not set above)
4. **Hardcoded fallbacks** - Lowest

---

## Common Mistakes to Avoid

| ❌ Don't | ✅ Do |
|----------|-------|
| Create new `Console()` | Use `from eleven_video.ui.console import console` |
| Access `os.getenv()` directly | Use `Settings()` class |
| Forget `await adapter.close()` | Always cleanup in `finally` |
| Skip non-TTY check | Check `console.is_terminal` |
| Use sync HTTP calls | Use `async` with HTTPX |
| Put business logic in CLI | Put in domain/orchestrator |
