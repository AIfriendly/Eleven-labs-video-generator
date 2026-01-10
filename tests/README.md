# Test Suite Documentation

## Overview
This directory contains the automated test suite for the Eleven Labs AI Video Generator.
Current coverage includes Unit, Integration, and End-to-End (E2E) tests.

## Structure
- `tests/unit/`: Unit tests for individual components.
- `tests/orchestrator/`: Integration tests for the VideoPipeline.
- `tests/e2e/`: End-to-End tests verifying CLI commands and full flows.
- `tests/fixtures/`: Shared test fixtures (offline API mocks).
- `tests/ui/`: Tests for interactive UI selectors.

## Running Tests
Run all tests:
```bash
uv run pytest
```

Run specific levels:
```bash
uv run pytest tests/e2e/
uv run pytest tests/orchestrator/
```

## Key Test Files
- **Video Duration Logic**:
  - `tests/orchestrator/test_video_pipeline_duration.py`: Verifies duration parameter propagation.
  - `tests/e2e/test_duration_e2e.py`: Verifies CLI `--duration` argument handling.

## Fixtures
Shared fixtures are defined in `tests/fixtures/`. The `mock_all_apis` fixture provides offline mock responses for ElevenLabs and Gemini APIs.
