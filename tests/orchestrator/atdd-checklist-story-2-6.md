# ATDD Checklist: Story 2.6 - Interactive Video Generation

**Story**: 2.6 Interactive Video Generation Command
**Impact**: High (User Facing)
**Primary Test Level**: Integration/E2E

## Acceptance Criteria & Test Mapping

| Criteria | Test File | Status |
|/---|---|---|
| 1. Interactive Prompt for Topic | `tests/e2e/test_cli_generated.py` (Planned) | 🔴 RED |
| 2. Orchestration Pipeline | `tests/orchestrator/test_video_pipeline.py` | 🔴 RED |
| 3. Progress Updates | `tests/orchestrator/test_video_pipeline.py` | 🔴 RED |
| 4. Error Handling | `tests/orchestrator/test_video_pipeline.py` | 🔴 RED |
| 5. Final Path Display | `tests/unit/test_video_pipeline.py` (Planned) | 🔴 RED |

## Failing Tests Created

- [x] **Integration**: `tests/orchestrator/test_video_pipeline.py`
    - `test_pipeline_orchestration_success`
    - `test_pipeline_progress_callbacks`
    - `test_pipeline_error_handling`

## Data Infrastructure

- [x] **Mocks**: Using Standard Mocks (`GeminiAdapter`, `ElevenLabsAdapter`, `FFmpegVideoCompiler`) via `unittest.mock.patch`.
- [x] **Fixtures**: `mock_settings` in test file.

## Implementation Checklist

### Phase 1: Orchestrator Core
- [ ] Create `eleven_video/orchestrator/` directory and `__init__.py`.
- [ ] Create `eleven_video/orchestrator/video_pipeline.py`.
- [ ] Implement `VideoPipeline` class shell.
- [ ] Implement `_init_adapters` (Lazy Loading).

### Phase 2: Pipeline Logic (Green Phase)
- [ ] Implement `generate(prompt, voice_id)` method.
- [ ] Wire Script Generation -> `GeminiAdapter`.
- [ ] Wire Audio Generation -> `ElevenLabsAdapter`.
- [ ] Wire Image Generation -> `GeminiAdapter`.
- [ ] Wire Compilation -> `FFmpegVideoCompiler`.
- [ ] Run `test_pipeline_orchestration_success` (Should Pass).

### Phase 3: Progress & Error Handling
- [ ] Integrate `VideoPipelineProgress` callbacks.
- [ ] Map pipeline stages (`PROCESSING_SCRIPT`, etc.).
- [ ] Implement try/except blocks for error reporting.
- [ ] Run `test_pipeline_progress_callbacks` and `test_pipeline_error_handling` (Should Pass).

### Phase 4: CLI Integration
- [ ] Add `generate` command to `eleven_video/main.py`.
- [ ] Use `typer.Option` for prompt, voice, output.
- [ ] Connect `VideoPipeline` to CLI command.
- [ ] Verify interactively.

## Execution Commands

```bash
# Run the orchestration tests
uv run pytest tests/orchestrator/test_video_pipeline.py -v
```
