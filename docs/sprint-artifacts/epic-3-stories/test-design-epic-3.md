# Test Design: Epic 3 - Pre-generation Customization

**Date:** 2025-12-18
**Author:** Revenant
**Status:** Approved

---

## Executive Summary

**Scope:** Full test design for Epic 3 (Pre-generation Customization)

**Risk Summary:**
- Total risks identified: 12
- High-priority risks (≥6): 3
- Critical categories: TECH, BUS, OPS

**Coverage Summary:**
- P0 scenarios: 8 tests (~16 hours)
- P1 scenarios: 14 tests (~14 hours)
- P2/P3 scenarios: 12 tests (~6 hours)
- **Total effort**: ~36 hours (~4.5 days)

---

## Epic 3 Overview

**Goal:** Users can select specific voice models, image generation models, Gemini text generation models, and video duration before starting video generation.

**FRs Covered:** FR2, FR3, FR4, FR17, FR18, FR19, FR24, FR24.1, FR25.1, FR34, FR36.1

### Stories

| Story | Title | Acceptance Criteria Summary |
|-------|-------|----------------------------|
| 3.1 | Custom Voice Model Selection | User can specify voice model → TTS uses selected voice |
| 3.2 | Custom Image Generation Model Selection | User can select image model → Images use selected model |
| 3.3 | Interactive Voice Selection Prompts | Interactive menu displays numbered voice options |
| 3.4 | Interactive Image Model Selection Prompts | Interactive menu displays numbered image model options |
| 3.5 | Gemini Text Generation Model Selection | User can select Gemini model via prompt → Script uses selected model |
| 3.6 | Video Duration Selection | User can select duration (1, 3, 5 min) → Script/assets match duration |
| 3.7 | Gemini Model Preference Configuration | User can configure default Gemini model in settings |
| 3.8 | Custom Output Resolution Selection | User can select resolution (1080p, 720p) → Video uses resolution |

---

## Risk Assessment

### High-Priority Risks (Score ≥6)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner | Timeline |
|---------|----------|-------------|-------------|--------|-------|------------|-------|----------|
| R-001 | TECH | ElevenLabs voice model API changes/deprecation | 2 | 3 | 6 | Implement adapter pattern with model validation, graceful fallback to default voice | Dev | Sprint 3.1 |
| R-002 | TECH | Gemini model availability varies by API key/tier | 2 | 3 | 6 | Validate model availability at startup, show only available models in selection | Dev | Sprint 3.5 |
| R-003 | BUS | Duration selection creates mismatched content timing | 3 | 2 | 6 | Validate script length matches duration target, adjust image count dynamically | QA | Sprint 3.6 |

### Medium-Priority Risks (Score 3-4)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner |
|---------|----------|-------------|-------------|--------|-------|------------|-------|
| R-004 | TECH | Interactive prompts fail in non-TTY environments | 2 | 2 | 4 | Detect non-TTY and fall back to defaults with warning | Dev |
| R-005 | DATA | User preferences not persisted correctly | 2 | 2 | 4 | Validate config file schema on write/read, backup before update | Dev |
| R-006 | BUS | Resolution changes affect video quality/aspect ratio | 2 | 2 | 4 | Validate resolution aspect ratio matches 16:9, test output quality | QA |
| R-007 | OPS | API model lists become stale | 2 | 2 | 4 | Cache model lists with TTL, refresh on user action | Dev |

### Low-Priority Risks (Score 1-2)

| Risk ID | Category | Description | Probability | Impact | Score | Action |
|---------|----------|-------------|-------------|--------|-------|--------|
| R-008 | BUS | Voice selection menu too long (>20 options) | 1 | 2 | 2 | Add search/filter to voice selection UI | Monitor |
| R-009 | TECH | Image model switching mid-generation | 1 | 2 | 2 | Document model locked after start | Monitor |
| R-010 | OPS | Config migration between versions | 1 | 2 | 2 | Add version field to config, auto-migrate | Monitor |
| R-011 | TECH | Resolution not supported by FFmpeg codec | 1 | 1 | 1 | Validate resolution against codec capabilities | Monitor |
| R-012 | BUS | Duration options don't match user needs | 1 | 1 | 1 | Survey users, add custom duration in Phase 3 | Monitor |

### Risk Category Legend

- **TECH**: Technical/Architecture (API integration, model availability, environment detection)
- **SEC**: Security (N/A for this epic - no new security surfaces)
- **PERF**: Performance (N/A - no significant performance implications)
- **DATA**: Data Integrity (config persistence, model preferences)
- **BUS**: Business Impact (UX, content quality, user expectations)
- **OPS**: Operations (API model lists, config migration)

---

## Test Coverage Plan

### P0 (Critical) - Run on every commit

**Criteria**: Blocks core journey + High risk (≥6) + No workaround

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
|-------------|------------|-----------|------------|-------|-------|
| Story 3.1: Voice model selection flows to TTS | Unit + API | R-001 | 2 | DEV | Test adapter passes model to ElevenLabs |
| Story 3.2: Image model selection flows to generation | Unit + API | R-001 | 2 | DEV | Test adapter passes model to Gemini |
| Story 3.5: Gemini model selection flows to script gen | Unit + API | R-002 | 2 | DEV | Validate model parameter in API call |
| Story 3.6: Duration affects script length | Unit | R-003 | 2 | DEV | Script generator respects duration param |

**Total P0**: 8 tests, ~16 hours

### P1 (High) - Run on PR to main

**Criteria**: Important features + Medium risk (3-4) + Common workflows

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
|-------------|------------|-----------|------------|-------|-------|
| Story 3.3: Interactive voice selection UI | Unit + Component | R-004, R-008 | 3 | DEV | Rich prompt rendering, selection handling |
| Story 3.4: Interactive image model selection UI | Unit + Component | R-004 | 3 | DEV | Rich prompt rendering, selection handling |
| Story 3.5: Interactive Gemini model selection UI | Unit + Component | R-004 | 2 | DEV | Rich prompt rendering, selection handling |
| Story 3.6: Duration selection UI | Unit + Component | - | 2 | DEV | Duration options display and selection |
| Story 3.7: Config persistence for Gemini model | Unit | R-005 | 2 | DEV | Save/load default model preference |
| Story 3.8: Resolution selection and FFmpeg output | Unit + Integration | R-006, R-011 | 2 | DEV | Resolution passed to FFmpeg, output valid |

**Total P1**: 14 tests, ~14 hours

### P2 (Medium) - Run nightly/weekly

**Criteria**: Secondary features + Low risk (1-2) + Edge cases

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
|-------------|------------|-----------|------------|-------|-------|
| Story 3.1: Invalid voice model fallback | Unit | R-001 | 2 | DEV | Graceful fallback behavior |
| Story 3.2: Invalid image model fallback | Unit | R-001 | 2 | DEV | Graceful fallback behavior |
| Story 3.3: Voice list pagination/scroll | Component | R-008 | 2 | QA | Long list handling |
| Story 3.6: Duration boundary conditions | Unit | R-003 | 2 | DEV | 0, negative, very long durations |
| Story 3.7: Config corruption recovery | Unit | R-005 | 2 | DEV | Invalid config file handling |
| Story 3.8: Unsupported resolution fallback | Unit | R-011 | 2 | DEV | Fallback to default 1080p |

**Total P2**: 12 tests, ~6 hours

### P3 (Low) - Run on-demand

**Criteria**: Nice-to-have + Exploratory + Performance benchmarks

| Requirement | Test Level | Test Count | Owner | Notes |
|-------------|------------|------------|-------|-------|
| API model list refresh performance | Performance | 1 | QA | Cache TTL validation |
| Config migration between versions | Integration | 1 | DEV | Schema evolution |
| Voice selection with special characters | Unit | 1 | DEV | Unicode voice names |

**Total P3**: 3 tests, ~1.5 hours

---

## Execution Order

### Smoke Tests (<5 min)

**Purpose**: Fast feedback, catch build-breaking issues

- [ ] Voice selection returns valid model ID (30s)
- [ ] Image model selection returns valid model ID (30s)
- [ ] Gemini model selection returns valid model ID (30s)
- [ ] Duration selection returns valid minutes value (30s)

**Total**: 4 scenarios

### P0 Tests (<10 min)

**Purpose**: Critical path validation

- [ ] Voice model flows to ElevenLabs API (Unit)
- [ ] Image model flows to Gemini API (Unit)
- [ ] Gemini text model flows to script generation (Unit)
- [ ] Duration parameter affects script generation prompt (Unit)

**Total**: 8 scenarios

### P1 Tests (<30 min)

**Purpose**: Important feature coverage

- [ ] Interactive voice menu renders correctly (Component)
- [ ] Interactive image menu renders correctly (Component)
- [ ] Interactive Gemini menu renders correctly (Component)
- [ ] Duration menu shows valid options (Component)
- [ ] Config persistence saves/loads correctly (Unit)
- [ ] Resolution passed to FFmpeg (Integration)

**Total**: 14 scenarios

### P2/P3 Tests (<60 min)

**Purpose**: Full regression coverage

- [ ] All fallback scenarios (Unit)
- [ ] Edge cases for all selections (Unit)
- [ ] Error recovery tests (Unit)

**Total**: 15 scenarios

---

## Resource Estimates

### Test Development Effort

| Priority | Count | Hours/Test | Total Hours | Notes |
|----------|-------|------------|-------------|-------|
| P0 | 8 | 2.0 | 16 | Complex API integration mocking |
| P1 | 14 | 1.0 | 14 | Standard coverage |
| P2 | 12 | 0.5 | 6 | Simple scenarios |
| P3 | 3 | 0.5 | 1.5 | Exploratory |
| **Total** | **37** | **-** | **37.5** | **~4.5 days** |

### Prerequisites

**Test Data:**
- Voice model fixtures (list of valid ElevenLabs voice IDs)
- Image model fixtures (list of valid Gemini image models)
- Gemini text model fixtures (list of available text models)
- Duration configuration fixtures

**Tooling:**
- pytest for unit tests
- pytest-mock for API mocking
- Rich testing utilities for interactive prompt testing

**Environment:**
- Python 3.12+ with uv package manager
- Mock ElevenLabs and Gemini API responses
- Test configuration directory isolation

---

## Quality Gate Criteria

### Pass/Fail Thresholds

- **P0 pass rate**: 100% (no exceptions)
- **P1 pass rate**: ≥95% (waivers required for failures)
- **P2/P3 pass rate**: ≥90% (informational)
- **High-risk mitigations**: 100% complete or approved waivers

### Coverage Targets

- **Critical paths**: ≥80%
- **API integration logic**: 100%
- **Interactive UI flows**: ≥70%
- **Config persistence**: ≥80%

### Non-Negotiable Requirements

- [ ] All P0 tests pass
- [ ] No high-risk (≥6) items unmitigated
- [ ] Voice/Image/Gemini model selection flows work end-to-end
- [ ] Config persistence is reliable

---

## Mitigation Plans

### R-001: ElevenLabs Voice Model API Changes (Score: 6)

**Mitigation Strategy:** Implement adapter pattern with model validation before use. Query available voices at startup, cache list with TTL. If requested voice unavailable, fall back to default with user warning.
**Owner:** Dev Team
**Timeline:** Story 3.1 implementation
**Status:** Planned
**Verification:** Unit test for fallback behavior, integration test with invalid voice ID

### R-002: Gemini Model Availability by API Key (Score: 6)

**Mitigation Strategy:** Query available models via API at startup. Filter selection menu to only show available models. If configured default unavailable, prompt user to reselect.
**Owner:** Dev Team
**Timeline:** Story 3.5 implementation
**Status:** Planned
**Verification:** Unit test for model filtering, integration test with restricted API key

### R-003: Duration Selection Content Mismatch (Score: 6)

**Mitigation Strategy:** Pass duration to script generator as explicit parameter. Script generator includes duration in prompt ("Generate a X-minute script"). Validate output script length approximates target duration.
**Owner:** QA Team
**Timeline:** Story 3.6 implementation
**Status:** Planned
**Verification:** Unit test script length validation, integration test duration accuracy

---

## Assumptions and Dependencies

### Assumptions

1. ElevenLabs API provides a list voices endpoint for dynamic voice discovery
2. Gemini API provides model listing for available models per API key
3. Rich library handles interactive prompts correctly in terminal environments
4. FFmpeg supports all proposed resolutions (1080p, 720p)

### Dependencies

1. Epic 2 complete - Required by Sprint 3 start (Core pipeline must work before customization)
2. ElevenLabs voice listing API - Required for Story 3.1, 3.3
3. Gemini model listing API - Required for Story 3.5

### Risks to Plan

- **Risk**: ElevenLabs deprecates voice model
  - **Impact**: Voice selection fails silently
  - **Contingency**: Implement validation with graceful fallback

- **Risk**: Gemini model availability changes
  - **Impact**: Saved preferences become invalid
  - **Contingency**: Validate on startup, prompt for reselection

---

## Test ID Reference

| Test ID | Story | Level | Description |
|---------|-------|-------|-------------|
| 3.1-UNIT-001 | 3.1 | Unit | Voice model passed to ElevenLabs adapter |
| 3.1-UNIT-002 | 3.1 | Unit | Invalid voice model fallback |
| 3.1-INT-001 | 3.1 | Integration | Voice model in actual API call |
| 3.2-UNIT-001 | 3.2 | Unit | Image model passed to Gemini adapter |
| 3.2-UNIT-002 | 3.2 | Unit | Invalid image model fallback |
| 3.3-COMP-001 | 3.3 | Component | Voice selection menu rendering |
| 3.3-COMP-002 | 3.3 | Component | Voice selection keyboard navigation |
| 3.4-COMP-001 | 3.4 | Component | Image model selection menu rendering |
| 3.5-UNIT-001 | 3.5 | Unit | Gemini model parameter in script generation |
| 3.5-COMP-001 | 3.5 | Component | Gemini model selection menu rendering |
| 3.6-UNIT-001 | 3.6 | Unit | Duration parameter in script prompt |
| 3.6-UNIT-002 | 3.6 | Unit | Duration boundary validation |
| 3.6-COMP-001 | 3.6 | Component | Duration selection menu |
| 3.7-UNIT-001 | 3.7 | Unit | Save default Gemini model to config |
| 3.7-UNIT-002 | 3.7 | Unit | Load default Gemini model from config |
| 3.8-UNIT-001 | 3.8 | Unit | Resolution parameter in FFmpeg call |
| 3.8-INT-001 | 3.8 | Integration | Output video has correct resolution |

---

## Approval

**Test Design Approved By:**

- [ ] Product Manager: _________ Date: _________
- [ ] Tech Lead: _________ Date: _________
- [ ] QA Lead: _________ Date: _________

**Comments:**

---

---

---

## Appendix

### Knowledge Base References

- `risk-governance.md` - Risk classification framework
- `probability-impact.md` - Risk scoring methodology
- `test-levels-framework.md` - Test level selection
- `test-priorities-matrix.md` - P0-P3 prioritization

### Related Documents

- PRD: [prd.md](./prd.md)
- Epic: [epics.md](./epics.md#epic-3-pre-generation-customization)
- Architecture: [architecture.md](./architecture.md)
- Project Structure: [project-structure-boundaries.md](./architecture/project-structure-boundaries.md)

---

**Generated by**: BMad TEA Agent - Test Architect Module
**Workflow**: `.bmad/bmm/testarch/test-design`
**Version**: 4.0 (BMad v6)
