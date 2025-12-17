# Project Structure & Boundaries

## Debate Club Showdown Analysis

**Controversy Evaluation:** The proposed structure was evaluated using a debate approach between opposing viewpoints:

**Minimalist Architect Position:** "The structure is over-engineered for a CLI tool"
- **Argument:** This is just a script that chains API calls together; the proposed structure with 6+ modules is unnecessary complexity
- **Supporting Points:** Fewer files and directories would make the codebase easier to understand; simpler structure might enable faster initial development

**Enterprise Architect Position:** "The structure is necessary for maintainability and scalability"
- **Argument:** The structure follows proven architectural principles that will prevent technical debt as the project grows
- **Supporting Points:** API orchestration with rate limiting, retries, and circuit breakers requires proper architecture; real-time monitoring and progress tracking need specialized modules

**Synthesis and Moderator's Verdict:**
The structure strikes the right balance between appropriate architectural boundaries and unnecessary over-engineering because:
- The complexity is justified by the PRD requirements (80% success rate, API rate limiting, real-time monitoring)
- The boundaries between API adapters, orchestrator, and UI are clear and necessary
- The project is not a simple script but a sophisticated API orchestration tool
- The test structure properly mirrors the source structure for maintainability
- The hexagonal architecture supports API abstraction and future extensibility

**Final Position:** The Enterprise Architect's position wins, but with acknowledgment that we should start with the proposed structure but implement it incrementally to avoid upfront complexity. The boundaries are necessary for the requirements but can be built iteratively.

## Complete Project Directory Structure

```
eleven-video/
├── README.md
├── pyproject.toml
├── poetry.lock
├── .env
├── .env.example
├── .gitignore
├── LICENSE
├── docs/
│   ├── architecture.md
│   ├── user-guide.md
│   └── api-reference.md
├── eleven_video/
│   ├── __init__.py
│   ├── main.py              # Entry point with Typer CLI
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py      # Pydantic configuration model with .env support
│   │   ├── persistence.py   # JSON config file I/O via platformdirs
│   │   └── validators.py    # Configuration validation helpers
│   ├── api/
│   │   ├── __init__.py
│   │   ├── base_adapter.py  # Base API adapter interface
│   │   ├── elevenlabs.py    # Eleven Labs API integration
│   │   ├── gemini.py        # Google Gemini API integration
│   │   └── adapters.py      # API abstraction layer with circuit breaker
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── base_pipeline.py # Base pipeline interface
│   │   ├── video_pipeline.py # Coordinate the full pipeline
│   │   ├── timing_controller.py # Handle 3-4 second image timing
│   │   └── edit_compiler.py # FFmpeg video compilation and effects
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── image_handler.py # Handle image processing
│   │   ├── audio_handler.py # Handle audio processing
│   │   └── video_handler.py # Handle video compilation
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── terminal.py      # Rich-based UI components
│   │   ├── prompts.py       # Terminal interaction prompts
│   │   └── displays.py      # Rich display components
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py      # API request models
│   │   ├── responses.py     # API response models
│   │   └── domain.py        # Domain models
│   ├── exceptions/
│   │   ├── __init__.py
│   │   └── custom_errors.py # Custom exception hierarchy
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── helpers.py       # General utility functions
│   │   ├── validators.py    # Input validation helpers
│   │   └── logger.py        # Logging configuration
│   └── constants/
│       ├── __init__.py
│       └── config.py        # Application constants
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest configuration
│   ├── test_main.py         # CLI interface tests
│   ├── config/
│   │   ├── __init__.py
│   │   └── test_settings.py # Configuration tests
│   ├── api/
│   │   ├── __init__.py
│   │   ├── test_elevenlabs.py # Eleven Labs API adapter tests
│   │   ├── test_gemini.py   # Google Gemini API adapter tests
│   │   └── test_adapters.py # API adapter base tests
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── test_video_pipeline.py # Video pipeline tests
│   │   ├── test_timing_controller.py # Timing controller tests
│   │   └── test_edit_compiler.py # Edit compiler tests
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── test_image_handler.py # Image processing tests
│   │   ├── test_audio_handler.py # Audio processing tests
│   │   └── test_video_handler.py # Video processing tests
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── test_terminal.py # Terminal UI tests
│   │   └── test_prompts.py  # Prompt tests
│   └── utils/
│       ├── __init__.py
│       ├── test_helpers.py  # Utility function tests
│       └── test_validators.py # Validation tests
├── scripts/
│   ├── __init__.py
│   ├── setup.py            # Setup and installation script
│   ├── build.py            # Build and packaging script
│   └── dev.py              # Development utilities
└── .github/
    └── workflows/
        └── ci.yml          # CI/CD pipeline configuration
```

## Architectural Boundaries

**API Boundaries:**
- External API endpoints: Eleven Labs API, Google Gemini API
- Internal service boundaries: API adapters layer abstracts external services
- Authentication boundaries: API key management handled in configuration layer
- Data access boundaries: API responses converted to domain models in adapter layer

**Component Boundaries:**
- Main CLI component: Coordinates user interaction via Typer (Epic 1)
- **Orchestrator component:** Central coordinator for video generation pipeline (Story 2.6). The `video_pipeline.py` orchestrates the interactive `eleven-video generate` command by:
  - Prompting user for video topic (via `ui/prompts.py`)
  - Calling `GeminiAdapter.generate_script()` (Story 2.1)
  - Calling `ElevenLabsAdapter.generate_speech()` (Story 2.2)
  - Calling `GeminiAdapter.generate_images()` (Story 2.3)
  - Calling `FFmpegVideoCompiler.compile_video()` (Story 2.4)
  - Displaying progress via `VideoPipelineProgress` (Story 2.5)
- API adapter component: Handles all external API communication
- UI component: Handles terminal interface using Rich


**Service Boundaries:**
- API service boundary: All external API calls go through adapter layer
- Processing service boundary: Image, audio, and video processing are separate
- Configuration service boundary: Configuration management is centralized
- Validation service boundary: Input validation occurs at boundaries

**Data Boundaries:**
- Domain model boundary: API responses converted to domain models
- Configuration boundary: Configuration data handled separately
- Temporary file boundary: Processing artifacts stored temporarily
- Cache boundary: API response caching handled separately

## Requirements to Structure Mapping

**Feature Mapping:**

Interactive Terminal Interface:
- Components: `eleven_video/ui/terminal.py`, `eleven_video/ui/prompts.py`
- Main entry: `eleven_video/main.py`
- Tests: `tests/ui/test_terminal.py`, `tests/test_main.py`

API Integration (Eleven Labs & Google Gemini):
- Components: `eleven_video/api/elevenlabs.py`, `eleven_video/api/gemini.py`
- Base layer: `eleven_video/api/base_adapter.py`, `eleven_video/api/adapters.py`
- Tests: `tests/api/test_elevenlabs.py`, `tests/api/test_gemini.py`

Video Processing Pipeline:
- Components: `eleven_video/orchestrator/video_pipeline.py`, `eleven_video/orchestrator/timing_controller.py`
- Processing: `eleven_video/processing/image_handler.py`, `eleven_video/processing/audio_handler.py`, `eleven_video/processing/video_handler.py`
- Tests: `tests/orchestrator/test_video_pipeline.py`, `tests/processing/`

Real-time Monitoring:
- Components: `eleven_video/ui/displays.py`, `eleven_video/ui/terminal.py`
- Integration: Rich progress bars and API usage tracking
- Tests: `tests/ui/test_terminal.py`

Configuration Management:
- Components: `eleven_video/config/settings.py`, `eleven_video/config/validators.py`
- Environment files: `.env` (for API keys), `.env.example` (template)
- Tests: `tests/config/test_settings.py`

**Cross-Cutting Concerns:**
Error Handling: `eleven_video/exceptions/custom_errors.py`, consistent across all modules
Logging: `eleven_video/utils/logger.py`, integrated in all components
Validation: `eleven_video/utils/validators.py`, `eleven_video/config/validators.py`, at all boundaries
Testing: `tests/` directory with parallel structure, comprehensive test coverage across all modules

## Integration Points

**Internal Communication:**
- API adapters return Pydantic models that orchestrator consumes
- Orchestrator reports progress to UI layer for display
- Configuration dependency injected into all components

**External Integrations:**
- Eleven Labs API: `eleven_video/api/elevenlabs.py`
- Google Gemini API: `eleven_video/api/gemini.py`
- File system for temporary processing and output

**Data Flow:**
Text prompt → Gemini API (`gemini-2.5-flash`) → Script → Eleven Labs TTS → Audio → Gemini Nano Banana (`gemini-2.5-flash-image`) → Images → FFmpeg → Video

## File Organization Patterns

**Configuration Files:**
- `pyproject.toml` and `poetry.lock` at project root
- `.env.example` for environment variable examples
- `eleven_video/config/` for application-specific configuration

**Source Organization:**
- Hexagonal architecture with clear separation of concerns
- Domain logic in orchestrator, infrastructure in api/processing
- Co-located tests following same directory structure

**Test Organization:**
- Tests parallel source structure (e.g., `tests/api/` matches `eleven_video/api/`)
- Integration tests in orchestrator module
- Unit tests for all components

**Asset Organization:**
- Static assets would go in project root or docs/
- Temporary assets handled in processing layer during execution

## Development Workflow Integration

**Development Server Structure:**
- Poetry for dependency management
- Pytest for testing with comprehensive coverage reporting
- Pre-commit hooks configuration would go in root
- Code coverage validation (≥80% coverage required for all components)

**Build Process Structure:**
- Packaging configuration in `pyproject.toml`
- Build scripts in `scripts/build.py`
- Distribution artifacts built to `dist/` directory
- Automated test execution during build process

**Deployment Structure:**
- Single executable output via PyInstaller configuration
- Cross-platform compatibility through Python packaging

## Testing Strategy & Quality Gates

**Test Levels Distribution:**
- Unit Tests (40%): Focus on business logic, API adapter core logic, utility functions, and configuration validation
- Integration Tests (30%): Validate API adapter interactions, configuration loading, and component boundaries
- E2E Tests (30%): Complete video generation workflow, terminal UI behavior, and real-time monitoring features

**Quality Requirements:**
- Code coverage: ≥80% for all components
- Performance: <10 second startup time, <5 minute per video processing
- Reliability: 80% success rate for complete video generation with circuit breaker patterns
- Security: No API keys logged, proper file permissions for config files
- Test execution: All tests must complete in deterministic fashion without hard waits

**Test Environment Requirements:**
- Local Development: Unit and integration tests with mocked API dependencies
- Integration: Test API keys for Eleven Labs and Google Gemini for end-to-end validation
- Performance: Load testing environment with realistic API rate limits
- Cross-Platform: Terminal UI testing across Windows, macOS, and Linux environments

**Test Design Principles:**
- Deterministic: No hard waits, conditionals controlling flow, or random data without seeds
- Isolated: Each test cleans up after itself, parallel execution safe
- Explicit: Assertions visible in test bodies, not hidden in helpers
- Focused: Tests under 300 lines, <1.5 minutes execution time
- Fast: API setup instead of UI navigation, parallel operations where possible
