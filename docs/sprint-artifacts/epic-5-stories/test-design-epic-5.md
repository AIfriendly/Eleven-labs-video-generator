# Test Design: Epic 5 - Advanced API Monitoring

**Date:** 2026-01-06
**Author:** Revenant
**Status:** Approved

---

## Executive Summary

**Scope:** Epic-Level test design for Epic 5. Covers all stories related to real-time API usage and cost monitoring.

**Stories Covered:**
- **5.1**: Real-time API Usage Monitoring During Processing
- **5.2**: Model-specific Usage Metrics for Gemini API
- **5.3**: Live Consumption Data Viewing
- **5.4**: API Quota Information Display
- **5.5**: API Cost Tracking During Generation

**Risk Summary:**
- Total risks identified: 5
- High-priority risks (≥6): 2
- Critical categories: DATA (Cost Accuracy), OPS (UI Performance)

**Coverage Summary:**
- P0 scenarios: 5 (10 hours)
- P1 scenarios: 5 (5 hours)
- P2/P3 scenarios: 3 (2 hours)
- **Total effort**: ~17 hours (2 days)

---

## Risk Assessment

### High-Priority Risks (Score ≥6)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner | Timeline |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ---------- | ----- | -------- |
| R-001 | DATA | Inaccurate cost calculations due to stale pricing rates or wrong token counts | 3 (Likely) | 3 (Major) | 9 | Implement `PricingStrategy` pattern with unit tests for each model; Allow config override for rates | DEV | Sprint 5.1 |
| R-002 | OPS | UI freeze/flicker when updating live usage stats during heavy video processing | 3 (Likely) | 2 (Degraded) | 6 | Run monitoring UI in separate thread/async task using `rich.live`; decoupled from heavy FFMPEG ops | DEV | Sprint 5.1 |

### Medium-Priority Risks (Score 3-4)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ---------- | ----- |
| R-003 | TECH | API response schema changes for `usage_metadata` (Gemini/ElevenLabs) | 2 (Possible) | 2 (Degraded) | 4 | Defensive parsing in Adapters; log warnings if metadata missing but continue processing | DEV |
| R-004 | TECH | Quota API unavailability or rate limiting on quota checks | 2 (Possible) | 2 (Degraded) | 4 | Cache quota info; do not block generation if quota check fails | DEV |

### Low-Priority Risks (Score 1-2)

| Risk ID | Category | Description | Probability | Impact | Score | Action |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ------- |
| R-005 | UX | Accessing breakdown details (5.2) clutters the main UI | 2 (Possible) | 1 (Minor) | 2 | Show summary by default; detailed breakdown in final report or verbose mode |

---

## Test Coverage Plan

### P0 (Critical) - Run on every commit

**Criteria**: Accuracy of Costs & Usage Tracking

| Story | Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ----- | ----------- | ---------- | --------- | ---------- | ----- | ------- |
| 5.5 | `UsageMonitor` correctly accumulates cost per model | Unit | R-001 | 2 | DEV | Verify math for varying token counts |
| 5.2 | `UsageMonitor` separates stats by Model ID | Unit | R-001 | 1 | DEV | Verify aggregation logic |
| 5.1 | GeminiAdapter returns valid `usage_metadata` | API (Mock) | R-003 | 1 | DEV | Mock Google response |
| 5.1 | ElevenLabsAdapter returns valid char counts | API (Mock) | R-003 | 1 | DEV | Mock 11Labs response |

**Total P0**: 5 tests, 10 hours

### P1 (High) - Run on PR to main

**Criteria**: UI Experience & Real-time Feeds

| Story | Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ----- | ----------- | ---------- | --------- | ---------- | ----- | ------- |
| 5.1, 5.3 | `UsageDisplay` renders live stats without layout break | Component | R-002 | 1 | DEV | Visual snapshot |
| 5.1 | UI updates occur at 5s interval (Mocked time) | Unit | R-002 | 1 | DEV | Test observer trigger |
| 5.4 | Quota info is displayed if available | Component | R-004 | 1 | DEV | Mock quota response |
| 5.5 | Final Cost Report is generated at end of flow | Integration | - | 1 | DEV | Verify final log/print |
| 5.2 | Multi-model usage (e.g. Flash + Pro) tracks separately | Integration | - | 1 | DEV | Simulate mixed usage flow |

**Total P1**: 5 tests, 5 hours

### P2 (Medium) - Run nightly/weekly

**Criteria**: Edge Cases

| Story | Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ----- | ----------- | ---------- | --------- | ---------- | ----- | ------- |
| 5.4 | Graceful handling of Quota API failure | Unit | R-004 | 1 | DEV | Simulate 500 error on quota check |
| 5.5 | Zero-usage scenarios (dry runs) show 0 cost | Unit | - | 1 | DEV | |
| 5.2 | Unknown model ID falls back to default rate/warning | Unit | - | 1 | DEV | |

**Total P2**: 3 tests, 2 hours

---

## Execution Order

1.  **Core Logic (Stories 5.2, 5.5)**: Implement `UsageMonitor` and Pricing Logic. -> **Verify with P0 Unit Tests**.
2.  **Adapters (Story 5.1)**: Instrument Gemini/ElevenLabs adapters to feed `UsageMonitor`. -> **Verify with P0 API Mock Tests**.
3.  **UI Integration (Stories 5.1, 5.3, 5.4)**: Create `UsageDisplay` component and integrate into `VideoPipeline`. -> **Verify with P1 Component Tests**.

---

## Quality Gate Criteria

### Pass/Fail Thresholds

- **Cost Accuracy**: Token-to-Cost calculation must match expected values within $0.0001 precision.
- **UI Architecture**: Usage monitoring MUST NOT run on the main blocking thread (verify via code review/async patterns).

---

## Approval

**Test Design Approved By:**

- [x] Test Architect (Agent) Date: 2026-01-06

**Generated by**: BMad TEA Agent - Test Architect Module
**Workflow**: `.bmad/bmm/testarch/test-design`
