# Tech-Spec: Epic 1 - CLI Foundation & Core Architecture

**Created:** 2025-12-12
**Status:** Ready for Development

## Overview

### Problem Statement
We need to establish the foundational CLI application structure, configuration management, and API connectivity to support the Eleven Labs AI Video generator. This foundation must be robust, secure, and developer-friendly to support future feature expansion.

### Solution
Implement a modular Python CLI using **Typer** and **Rich** for the interface, **Pydantic Settings** for robust 12-factor configuration, and **platformdirs** for OS-standard data persistence. Security will be enforced via **SecretStr** and `.env` file pointers.

### Scope (In/Out)
**IN:**
- Project scaffolding and tooling configuration.
- Configuration management (Env vars + JSON prefs).
- API Key security and profile management.
- Basic CLI structure and Help system.
- API connectivity checks (Status command).

**OUT:**
- Actual video generation logic (Epic 2).
- Complex voice cloning features (Epic 3).

## Context for Development

### Codebase Patterns

#### 1. CLI Architecture
- **Framework**: `typer` with `rich`.
- **Style**: Native Typer Rich integration (`rich_markup_mode="rich"`).
- **Console**: Singleton `Console` instance in `eleven_video/ui/console.py` to prevent stream conflicts.

#### 2. Configuration & Security
- **Settings**: `pydantic-settings` `BaseSettings` model.
- **Secrets**: API keys typed as `SecretStr` for automatic masking in logs/repr.
- **Persistence**: User preferences (e.g., active profile) stored in `config.json` located via `platformdirs.user_config_dir` (XDG/AppData).
- **Keys**: **NEVER** stored in JSON. JSON only stores *pointers* to `.env` files for profiles.

#### 3. API & Resilience
- **Client**: `httpx` (Async).
- **Resilience**: `tenacity` for retry logic on transient errors.
- **Interfaces**: `ServiceHealth` Protocol to standardize status checks across providers (ElevenLabs, Gemini).

### Files to Reference
- `docs/architecture/core-architectural-decisions.md`
- `docs/architecture/project-structure-boundaries.md`
- `docs/sprint-artifacts/1-*.md` (Detailed Stories)

### Technical Decisions
| Decision | Choice | Rationale |
| :--- | :--- | :--- |
| **CLI Lib** | `typer` | Modern, type-safe, easy submodule management. |
| **UI Lib** | `rich` | Best-in-class terminal formatting. |
| **Config** | `pydantic-settings` | Type-safe env var parsing, standard in modern Python. |
| **Pathing** | `platformdirs` | Respects OS standards (XDG/AppData) vs hardcoded `~/`. |
| **Testing** | `pytest` + `monkeypatch` | Standard robust testing framework. |

## Implementation Plan

### Tasks Summary
1.  **Scaffolding**: Initialize project with setuptools (`pyproject.toml`), strict `.gitignore`, and `eleven_video/` module layout.
2.  **Config Layer**: Implement `Settings` model, `SecretStr` security, and `Persistence` via `platformdirs`.
3.  **CLI Core**: Setup Typer app, centralized `Console`, and Help system.
4.  **API Layer**: Implement `ServiceHealth` protocol, Adapters with `tenacity`, and Status command.
5.  **Profiles**: Implement `.env` pointer logic for multiple profiles.

### Acceptance Criteria Consolidation
- **Security**: Keys never logged, never in JSON.
- **UX**: Rich formatting for tables and help. Standard OS config paths.
- **Quality**: `ruff`, `black`, `pre-commit` configured and passing.
- **Resilience**: Network calls verify connectivity and handle transient failures gracefully.

## Additional Context

### Dependencies
- `python >= 3.9`
- `typer`, `rich`, `shellingham` (for rich detection)
- `pydantic`, `pydantic-settings`
- `python-dotenv`
- `platformdirs`
- `httpx`
- `tenacity`

### Testing Strategy
- **Unit**: Mock file I/O and API calls.
- **Env**: Use `monkeypatch` to simulate env vars.
- **Integration**: Verify `eleven-video --help` executes.

### Notes
This spec serves as the technical "constitution" for Epic 1. All stories (1.1 - 1.6) are detailed implementations of these patterns.
