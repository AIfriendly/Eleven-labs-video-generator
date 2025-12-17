# Project Context

## Input Documents Analyzed:
- PRD: docs/prd.md

## Project Overview:
Based on the PRD for Eleven-labs-AI-Video, this is an interactive terminal tool that enables users to generate AI-powered videos from text prompts using APIs from Eleven Labs and Google Gemini. The core functionality includes script generation, TTS, image generation, and video compilation with professional editing.

---

## CRITICAL RULES (All Agents Must Follow)

### Python Package Manager: `uv` (MANDATORY)

> [!CAUTION]
> **NEVER use `python`, `pip`, or `python -m` directly.** Always use `uv` commands.

| Task | ❌ WRONG | ✅ CORRECT |
|------|----------|------------|
| Run tests | `python -m pytest` | `uv run pytest` |
| Run scripts | `python script.py` | `uv run python script.py` |
| Install packages | `pip install X` | `uv pip install X` |
| Create venv | `python -m venv .venv` | `uv venv` |
| Sync dependencies | `pip install -e .` | `uv sync` |

### Common Commands

```bash
# Run tests
uv run pytest tests/ -v

# Run a specific test file
uv run pytest tests/ui/test_progress.py -v

# Run with coverage
uv run pytest --cov=eleven_video tests/

# Run the CLI
uv run eleven-video --help

# Sync all dependencies
uv sync
```

### Why `uv`?
- Faster than pip (10-100x)
- Handles virtual environment automatically
- Ensures consistent dependencies via `uv.lock`
- Required for this project - venv may break without it

