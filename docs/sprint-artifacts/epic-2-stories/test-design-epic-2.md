# Test Design and Risk Assessment

**Epic**: 2 (Interactive Video Generation)
**Scope**: Epic-Level Mode (Story 2.6 focus)
**Version**: 1.0

## Risk Assessment

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ---------- |
| R-001 | TECH | Orchestration failure between stages | 2 (Possible) | 3 (Critical) | **6** | Extensive integration tests with mocked adapters to verify data flow. |
| R-002 | BUS | Uncontrolled API costs due to loops/retries | 2 (Possible) | 3 (Critical) | **6** | Ensure all automated tests use robust mocks. Implement dry-run mode in later stories. |
| R-003 | BUS | Poor UX due to lack of progress feedback | 3 (Likely) | 2 (Degraded) | **6** | Unit tests for `VideoPipelineProgress` integration. |
| R-004 | OPS | Temporary files accumulation | 3 (Likely) | 1 (Minor) | 3 | Use auto-cleanup fixtures in tests; Verify cleanup in pipeline. |
| R-005 | SEC | API Key exposure in logs/errors | 1 (Unlikely) | 3 (Critical) | 3 | Security review of error logging; Sanitize outputs. |

## Test Coverage Plan

### Prioritization Strategy

- **P0 (Critical)**: Orchestrator wiring (VideoPipeline), Command execution success path. Run on PR.
- **P1 (High)**: Error handling, Progress updates, Parameter passing (Voice ID). Run on PR.
- **P2 (Medium)**: Edge cases (empty prompts, network timeouts). Run nightly.

### Test Levels

| Requirement | Test Level | Priority | Test Scenarios |
| ----------- | ---------- | -------- | -------------- |
| **Interactive Generation Command** | **E2E (Mocked)** | **P0** | 1. User runs `eleven-video generate`, enters prompt, gets success.<br>2. User runs `eleven-video generate --help`. |
| **Orchestrator Logic** | **Integration** | **P0** | 1. `VideoPipeline.generate()` calls all adapters in order.<br>2. `voice_id` is correctly passed to ElevenLabsAdapter. |
| **Error Handling** | **Integration** | **P1** | 1. Gemini failure -> Pipeline stops -> Error reported.<br>2. ElevenLabs failure -> Pipeline stops -> Error reported. |
| **Progress Reporting** | **Unit** | **P1** | 1. Progress callbacks are invoked for each stage.<br>2. Final video path is returned/displayed. |
| **Lazy Loading** | **Unit** | **P2** | 1. Adapters are initialized only when `generate()` is called. |

### Data and Tooling

- **Mocks**: `MockGeminiAdapter`, `MockElevenLabsAdapter`, `MockVideoCompiler`.
- **Fixtures**: `mock_settings` (with dummy keys), `temp_output_dir` (auto-cleanup).
- **Factories**: `create_video_object`, `create_script_object`.

## Execution Order

1. **Smoke Tests**: `test_cli_help`, `test_pipeline_init` (< 1 min)
2. **P0 Tests**: `test_pipeline_flow_success`, `test_cli_generate_success` (< 2 mins)
3. **P1 Tests**: `test_pipeline_errors`, `test_voice_id_propagation` (< 2 mins)

## Quality Gate Criteria

- All P0 tests MUST pass.
- Code coverage for `eleven_video/orchestrator` > 90%.
- No real API calls during automated testing (Mock Enforcement).

## Next Steps

1. Run `atdd` workflow for Story 2.6.
2. Implement `VideoPipeline` skeletons.
3. Create `tests/orchestrator/` directory.
