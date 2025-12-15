# Implementation Patterns & Consistency Rules

## Pattern Categories Defined

**Critical Conflict Points Identified:**
6 areas where AI agents could make different choices that would cause conflicts

## Naming Patterns

**Python Naming Conventions:**
- Functions, variables, and modules: `snake_case` (e.g. `get_user_input`, `api_client`)
- Classes: `PascalCase` (e.g. `ElevenLabsAPI`, `VideoPipeline`)
- Constants: `UPPER_SNAKE_CASE` (e.g. `DEFAULT_TIMEOUT`, `MAX_RETRIES`)

**CLI Command Naming:**
- Commands and options: kebab-case (e.g. `video-generate`, `--api-key`, `--output-path`)

## Structure Patterns

**Project Organization:**
- `.env` - Environment file for API keys and configuration
- `.env.example` - Example environment file with template
- `src/api/` - API adapters for Eleven Labs, Google Gemini, etc.
- `src/orchestrator/` - Pipeline coordination and video generation workflow
- `src/ui/` - Terminal interface components using Rich
- `src/config/` - Configuration management with Pydantic
- `tests/` - Tests with same structure as `src/` (e.g., `tests/api/test_elevenlabs.py`)
- `src/utils/` - Shared utilities and helpers

**Module Structure:**
- Each module should have `__init__.py` for clear imports
- Public interfaces clearly defined in `__init__.py` files
- Internal implementation details in separate files within modules
- Each module must include comprehensive unit tests in corresponding test directory

## Architecture Patterns

**API Communication:**
- All API adapters must implement the same base interface with consistent error handling
- API responses should be immediately converted to Pydantic models
- All API calls must include timeout, retry logic, and rate limiting handling
- API adapters must support mocking for comprehensive testing of business logic

**Configuration Handling:**
- Use Pydantic BaseSettings model for configuration with .env file support
- API keys stored in environment variables via .env file (.env, .env.local, etc.)
- Configuration should be dependency injected, not accessed globally
- Provide sensible defaults with clear error messages for required values
- Configuration loading must be testable with clear interfaces for mocking

**State Management:**
- Video generation state tracked via orchestrator class with clear state transitions
- Progress reported through dedicated progress tracking objects
- State should be serializable for checkpointing and recovery
- State management components must expose clear interfaces for testing state changes

**Testability Patterns:**
- All components must expose clear interfaces for dependency injection
- External dependencies (APIs, file system) must be abstracted behind interfaces for mocking
- Module boundaries should enable comprehensive unit testing of business logic
- Error handling paths must be testable with predictable failure scenarios
- Logging and monitoring components must be mockable for test isolation

## Error Handling Patterns

**Error Types:**
- Define custom exception hierarchy: `VideoGenerationError` -> `APIError`/`ProcessingError`/`ConfigError`
- API errors: `APIRateLimitError`, `APIAuthenticationError`, `APITimeoutError`
- Processing errors: `VideoProcessingError`, `ImageProcessingError`
- All exceptions should include sufficient context for debugging

**User Feedback:**
- Terminal error messages follow format: `[ERROR] Description - (code: error_code, details: context)`
- API errors should suggest specific remediation steps
- All errors should be logged separately from user-facing messages

## Real-time Monitoring

**Progress Updates:**
- Use Rich progress bars with consistent format: description, percentage, elapsed time
- Progress tracking objects with standardized update interface
- API usage updates every 2 seconds or on significant changes
- Cost tracking updated after each API call with running totals

**Data Format:**
- API usage: Total requests, remaining quota, cost incurred, estimated remaining
- Progress: Current step, completion percentage, estimated time remaining, current status
- Display: Consistent Rich-based tables with color coding for different states

## Communication Patterns

**Internal Component Communication:**
- Use clear interfaces between components (typing protocols)
- Event system for progress updates using observer pattern
- Standardized data types for all component inputs/outputs

## Process Patterns

**Loading States:**
- Clear states: INITIALIZING, PROCESSING_SCRIPT, PROCESSING_AUDIO, PROCESSING_IMAGES, COMPILING_VIDEO
- Status messages updated at least every 5 seconds during long operations
- Graceful degradation when intermediate steps fail

**Pattern Enforcement:**
- All AI agents implementing this project MUST follow these patterns
- Code review checklist includes pattern compliance verification
- Type hints required for all function signatures to enforce consistency
