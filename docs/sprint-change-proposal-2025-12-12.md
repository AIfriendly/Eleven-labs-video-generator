# Sprint Change Proposal: Dependency Resolution for Epics
**Date:** 2025-12-12
**Status:** DRAFT

## 1. Issue Summary
**Trigger:** Implementation Readiness workflow failed due to a **Critical Dependency Violation**.
**Problem:** Epic 2 (MVP Video Generation) requires functional API integration to work, but the "Integration" stories were isolated in Epic 5 (scheduled later).
**Impact:** It is impossible to complete Epic 2 as a "Vertical Slice" because the code to call APIs wouldn't exist yet. The project plan is technically invalid.

## 2. Impact Analysis
*   **Epic Impact**: Epic 2 cannot be verified. Epic 5 is redundant in its current form.
*   **Artifacts**: `epics.md` requires structural refactoring. `implementation-readiness-report` flagged this as a blocker.
*   **Risk**: Low technical risk (just moving items), High process value (unblocks development).

## 3. Recommended Approach
**Refactor for Independence**:
Absorb the "Basic Integration" work into the functional stories of Epic 2. This treats integration as a *means* to an *end* (generating a video) rather than a separate activity.

## 4. Detailed Change Proposals

### A. Modify Epic 2 Stories (Absorb Integration)

**Story 2.2: Default Script Generation from Prompt**
*   **Rationale**: Explicitly include Gemini connection in the story that needs it.
*   **Add Acceptance Criteria**:
    *   `AND the system successfully authenticates with the Google Gemini API`
    *   `AND connection errors are handled gracefully`

**Story 2.3: Default Text-to-Speech Generation**
*   **Rationale**: Explicitly include Eleven Labs connection in the story that needs it.
*   **Add Acceptance Criteria**:
    *   `AND the system successfully authenticates with the Eleven Labs API`

### B. Refactor Epic 5 (Scope Reduction)

**Rename Epic**:
*   **OLD**: `Epic 5: API Integration and Monitoring`
*   **NEW**: `Epic 5: Advanced API Monitoring and Resilience`

**Delete Stories**:
*   **DELETE Story 5.1** (Eleven Labs Integration) - *moved to 2.3*
*   **DELETE Story 5.2** (Google Gemini Integration) - *moved to 2.2*

## 5. Implementation Handoff
*   **Scope**: **Minor** (Direct editing of `epics.md`).
*   **Action**: Development Agent to apply edits to `epics.md` immediately upon approval.
*   **Success Criteria**: Implementation Readiness workflow run again yields "READY".
