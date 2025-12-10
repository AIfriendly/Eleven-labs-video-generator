# Complete Analysis Workflow - Validation Checklist

## Mode Configuration

### Enhancement Mode Check
- [ ] Enhancement mode configured in .bmad/bmm/config.yaml
  - [ ] `ENHANCEMENT_MODE: standard` - Sequential execution with manual checkpoints
  - [ ] `ENHANCEMENT_MODE: enhanced` - Parallel execution + quality gates + auto-validation
- [ ] Mode detected correctly at workflow start
- [ ] Appropriate features enabled based on mode

---

## Pre-Execution Validation

### Prerequisites (Both Modes)
- [ ] User has provided an app idea or concept
- [ ] Output folder is accessible: {output_folder}
- [ ] All sub-workflows are available:
  - [ ] brainstorm-project workflow exists
  - [ ] research workflow exists
  - [ ] domain-research workflow exists
  - [ ] product-brief workflow exists

### Configuration (Both Modes)
- [ ] Config variables loaded from .bmad/bmm/config.yaml
- [ ] enhancement_mode variable resolved correctly
- [ ] communication_language set correctly
- [ ] user_name configured
- [ ] date system variable available

### Variables (Both Modes)
- [ ] skip_checkpoints configured (default: false)
- [ ] max_retry_per_phase configured (default: 2)

### Enhanced Mode Prerequisites (When ENHANCEMENT_MODE=enhanced)
- [ ] enable_parallel_research: true
- [ ] enable_quality_gates: true
- [ ] enable_auto_validation: true
- [ ] Quality gate criteria loaded from workflow.yaml
- [ ] Auto-validation rules loaded from workflow.yaml
- [ ] Performance tracking initialized

---

## Phase 0: Introduction (Step 0)

### Mode Detection
- [ ] Enhancement mode detected from config
- [ ] Correct workflow explanation shown based on mode:
  - [ ] Standard mode: Shows sequential execution, 80 min, 4 checkpoints
  - [ ] Enhanced mode: Shows parallel execution, 40 min, quality gates

### App Idea Capture
- [ ] User prompted for app idea
- [ ] App idea stored as {{app_idea}} variable
- [ ] App idea available for all subsequent workflows

### Initialization (Enhanced Mode)
- [ ] Performance tracking timer started
- [ ] Quality gate thresholds loaded
- [ ] Auto-validation rules prepared

---

## Phase 1: Brainstorming (Step 1)

### Execution (Both Modes)
- [ ] brainstorm-project workflow invoked successfully
- [ ] App idea passed as input to workflow
- [ ] Analyst agent (Mary) facilitated brainstorming
- [ ] Workflow completed without errors

### Output Quality (Both Modes)
- [ ] Brainstorming notes generated
- [ ] Output saved to {output_folder}
- [ ] Creative exploration of app concept present
- [ ] Multiple perspectives and approaches documented
- [ ] Initial feature ideas captured

### Quality Gate Validation (Enhanced Mode Only)
- [ ] Quality gate enabled and executed
- [ ] Outputs captured and validated:
  - [ ] ideas_count extracted from output
  - [ ] perspectives_count extracted from output
  - [ ] feature_concepts_count extracted from output
  - [ ] has_user_value assessed

### Quality Criteria (Enhanced Mode Only)
- [ ] Min ideas: {{ideas_count >= 10 ? 'PASS ✅' : 'FAIL ❌'}}
- [ ] Min perspectives: {{perspectives_count >= 3 ? 'PASS ✅' : 'FAIL ❌'}}
- [ ] Min feature concepts: {{feature_concepts_count >= 5 ? 'PASS ✅' : 'FAIL ❌'}}
- [ ] Has user value: {{has_user_value ? 'PASS ✅' : 'FAIL ❌'}}

### Quality Score Calculation (Enhanced Mode Only)
- [ ] Quality score calculated correctly:
  - [ ] Ideas weight: 0.3
  - [ ] Perspectives weight: 0.3
  - [ ] Feature concepts weight: 0.2
  - [ ] User value weight: 0.2
- [ ] Total score: {{quality_score}}/1.0
- [ ] Pass threshold: 0.7 (70%)
- [ ] Result: {{quality_score >= 0.7 ? 'PASS ✅' : 'FAIL ❌'}}

### Auto-Retry Logic (Enhanced Mode Only)
- [ ] If quality_score < 0.7:
  - [ ] Feedback generated with specific gaps identified
  - [ ] Workflow re-invoked with feedback
  - [ ] Retry count incremented
  - [ ] Max retries checked (default: 2)
- [ ] If max retries exceeded:
  - [ ] User prompted for manual intervention
  - [ ] User decision recorded (continue or abort)

### Summary Display (Both Modes)
- [ ] Summary displayed to user with key metrics
- [ ] Standard mode: Basic counts shown
- [ ] Enhanced mode: Quality score and pass/fail status shown

### Checkpoint (Standard Mode or Enhanced with !skip_checkpoints)
- [ ] User presented with options: Continue / Re-run / Abort
- [ ] User choice recorded and acted upon
- [ ] If re-run: Brainstorming repeated
- [ ] If abort: Workflow exited cleanly with partial report

### Auto-Continue (Enhanced Mode with skip_checkpoints)
- [ ] Checkpoint skipped automatically
- [ ] Workflow continues to next step

---

## Phase 2: Research Phase (Step 2)

### Mode-Based Execution Path
- [ ] Correct execution path chosen based on enhancement_mode:
  - [ ] Standard mode: Sequential execution (2a → 2b)
  - [ ] Enhanced mode: Parallel execution

---

### Standard Mode: Sequential Execution

#### Step 2a: Market Research
- [ ] Market research workflow invoked successfully
- [ ] Context from brainstorming output provided
- [ ] Analyst agent (Mary) conducted research
- [ ] Workflow completed without errors

#### Output Quality (Market Research)
- [ ] Research findings document generated
- [ ] Output saved to {output_folder}
- [ ] Market landscape analysis present
- [ ] Competitive analysis completed
- [ ] User behavior insights documented
- [ ] Relevant trends and technologies identified

#### Checkpoint (After Market Research)
- [ ] Summary displayed to user
- [ ] User presented with options: Continue / Re-run / Abort
- [ ] User choice recorded and acted upon
- [ ] If re-run: Market research repeated
- [ ] If abort: Workflow exited cleanly with partial report

#### Step 2b: Domain Research
- [ ] Domain research workflow invoked successfully
- [ ] Context from brainstorming and market research provided
- [ ] Analyst agent (Mary) investigated domain
- [ ] Workflow completed without errors

#### Output Quality (Domain Research)
- [ ] Domain research analysis generated
- [ ] Output saved to {output_folder}
- [ ] Industry-specific requirements documented
- [ ] Regulatory and compliance considerations identified
- [ ] Domain patterns and conventions captured
- [ ] Technical constraints and opportunities outlined

#### Checkpoint (After Domain Research)
- [ ] Summary displayed to user
- [ ] User presented with options: Continue / Re-run / Abort
- [ ] User choice recorded and acted upon
- [ ] If re-run: Domain research repeated
- [ ] If abort: Workflow exited cleanly with partial report

---

### Enhanced Mode: Parallel Execution

#### Parallel Execution Initiation
- [ ] Parallel execution mode confirmed
- [ ] Performance timer started
- [ ] Both workflows configured for parallel launch

#### Parallel Thread 1: Market Research
- [ ] Market research workflow launched in parallel
- [ ] Input: Brainstorming output
- [ ] Timeout configured: 30 minutes
- [ ] Quality gate enabled
- [ ] Workflow executing independently

#### Parallel Thread 2: Domain Research
- [ ] Domain research workflow launched in parallel
- [ ] Input: Brainstorming output
- [ ] Timeout configured: 30 minutes
- [ ] Quality gate enabled
- [ ] Workflow executing independently

#### Orchestration Settings
- [ ] run_in_parallel: true
- [ ] wait_for_all: true (wait for both workflows)
- [ ] fail_fast: false (continue even if one fails)
- [ ] combine_outputs: true

#### Progress Monitoring
- [ ] Progress indicators displayed for both workflows
- [ ] First completion detected and shown
- [ ] Second completion detected
- [ ] Both workflows completed successfully

#### Performance Metrics
- [ ] Parallel execution time calculated
- [ ] Comparison to baseline (40 min vs 80 min)
- [ ] Time saved calculated and displayed

#### Quality Gate: Market Research (Enhanced Mode)
- [ ] Market research output validated
- [ ] Competitors analyzed: {{competitors_count}} (min: 5)
- [ ] Research sources: {{sources_count}} (min: 10)
- [ ] Trends identified: {{trends_count}} (min: 3)
- [ ] Has market size estimation: {{has_market_size}}
- [ ] Quality score calculated: {{research_quality_score}}/1.0
- [ ] Pass threshold: 0.7
- [ ] Result: {{research_quality_score >= 0.7 ? 'PASS ✅' : 'FAIL ❌'}}

#### Auto-Retry: Market Research (If Failed)
- [ ] If research_quality_score < 0.7:
  - [ ] Feedback generated
  - [ ] Market research workflow re-invoked (not domain)
  - [ ] Retry count incremented
  - [ ] Max retries checked

#### Quality Gate: Domain Research (Enhanced Mode)
- [ ] Domain research output validated
- [ ] Domain patterns: {{patterns_count}} (min: 3)
- [ ] Constraints identified: {{constraints_count}} (min: 2)
- [ ] Has regulatory check: {{has_regulatory_check}}
- [ ] Has technical constraints: {{has_technical_constraints}}
- [ ] Quality score calculated: {{domain_quality_score}}/1.0
- [ ] Pass threshold: 0.7
- [ ] Result: {{domain_quality_score >= 0.7 ? 'PASS ✅' : 'FAIL ❌'}}

#### Auto-Retry: Domain Research (If Failed)
- [ ] If domain_quality_score < 0.7:
  - [ ] Feedback generated
  - [ ] Domain research workflow re-invoked (not market)
  - [ ] Retry count incremented
  - [ ] Max retries checked

#### Combined Summary Display
- [ ] Combined summary shown for both workflows
- [ ] Execution time displayed
- [ ] Time saved vs standard mode shown
- [ ] Market research results with quality score
- [ ] Domain research results with quality score

#### Enhanced Checkpoint (After Parallel Research)
- [ ] User presented with enhanced options:
  - [ ] [c] Continue to Product Brief
  - [ ] [m] Re-run market research only
  - [ ] [d] Re-run domain research only
  - [ ] [b] Re-run both research workflows
  - [ ] [a] Abort workflow
- [ ] User choice recorded and acted upon
- [ ] If re-run market: Only market research repeated
- [ ] If re-run domain: Only domain research repeated
- [ ] If re-run both: Entire parallel step repeated
- [ ] If abort: Workflow exited cleanly

---

## Phase 3: Product Brief (Step 3)

### Execution (Both Modes)
- [ ] product-brief workflow invoked successfully
- [ ] All inputs provided:
  - [ ] App idea from Step 0
  - [ ] Brainstorming notes from Step 1
  - [ ] Market research findings from Step 2
  - [ ] Domain research analysis from Step 2
- [ ] Analyst or PM agent created brief
- [ ] Workflow completed without errors

### Output Quality (Both Modes)
- [ ] Product brief document generated
- [ ] Output saved to {output_folder}
- [ ] Product vision and goals clearly articulated
- [ ] Target audience and user needs defined
- [ ] Market positioning described
- [ ] Feature concepts outlined
- [ ] Success metrics specified
- [ ] Constraints and risks documented

### Quality Gate Validation (Enhanced Mode Only)
- [ ] Comprehensive quality gate executed

#### Required Sections Validation (Enhanced Mode)
- [ ] Vision: {{has_vision ? '✅' : '❌'}}
- [ ] Target Audience: {{has_target_audience ? '✅' : '❌'}}
- [ ] Market Positioning: {{has_market_positioning ? '✅' : '❌'}}
- [ ] Feature Concepts: {{has_feature_concepts ? '✅' : '❌'}}
- [ ] Success Metrics: {{has_success_metrics ? '✅' : '❌'}}
- [ ] Constraints: {{has_constraints ? '✅' : '❌'}}
- [ ] Risks: {{has_risks ? '✅' : '❌'}}

#### Integration Quality Validation (Enhanced Mode)
- [ ] References brainstorming: {{references_brainstorm ? '✅' : '❌'}}
- [ ] References research: {{references_research ? '✅' : '❌'}}
- [ ] References domain: {{references_domain ? '✅' : '❌'}}
- [ ] All previous phases integrated: {{all_integrated ? '✅' : '❌'}}

#### Content Quality Validation (Enhanced Mode)
- [ ] Word count: {{word_count}} (min: 2000) {{word_count >= 2000 ? '✅' : '❌'}}
- [ ] Success metrics count: {{metrics_count}} (min: 3) {{metrics_count >= 3 ? '✅' : '❌'}}
- [ ] Vision clarity score: {{vision_clarity_score}}/1.0
- [ ] Value proposition score: {{value_prop_score}}/1.0

### Quality Score Calculation (Enhanced Mode Only)
- [ ] Overall quality score calculated:
  - [ ] Completeness weight: 0.3
  - [ ] Clarity weight: 0.2
  - [ ] Integration weight: 0.3
  - [ ] Actionability weight: 0.2
- [ ] Total score: {{product_brief_quality_score}}/1.0
- [ ] Pass threshold: 0.8 (80% - higher bar)
- [ ] Result: {{product_brief_quality_score >= 0.8 ? 'PASS ✅' : 'FAIL ❌'}}

### Auto-Retry Logic (Enhanced Mode Only)
- [ ] If product_brief_quality_score < 0.8:
  - [ ] Detailed feedback generated with specific issues
  - [ ] Recommendations provided
  - [ ] Workflow re-invoked with feedback
  - [ ] Previous outputs provided as additional context
  - [ ] Retry count incremented
  - [ ] Max retries checked (default: 2)
- [ ] If max retries exceeded:
  - [ ] User prompted: Continue anyway? [y/n]
  - [ ] If no: Manually re-run product brief

### Summary Display
- [ ] Summary displayed with all sections
- [ ] Standard mode: Basic content shown
- [ ] Enhanced mode: Quality score and integration status shown

### Checkpoint (Standard Mode or Enhanced with !skip_checkpoints)
- [ ] User presented with options: Continue / Re-run / Abort
- [ ] User choice recorded and acted upon
- [ ] If re-run: Product brief regenerated
- [ ] If abort: Workflow exited cleanly

### Auto-Continue (Enhanced Mode with skip_checkpoints)
- [ ] Checkpoint skipped automatically
- [ ] Workflow continues to completion report

---

## Phase 4: Completion Report (Step 4)

### Metrics Calculation (Both Modes)
- [ ] Total execution time calculated
- [ ] Standard mode: Basic timing recorded
- [ ] Enhanced mode: Additional metrics calculated:
  - [ ] Time saved vs baseline (80 min)
  - [ ] Percentage faster
  - [ ] Total retry count
  - [ ] Average quality score across all phases

### Report Generation (Both Modes)
- [ ] Comprehensive report created
- [ ] Report includes workflow execution summary
- [ ] All 4 phases marked as complete (✅)
- [ ] Generated artifacts listed with locations

### Standard Mode Report Sections
- [ ] Workflow execution summary with all phases
- [ ] Generated artifacts with file paths
- [ ] Quality check checklist for manual review
- [ ] Next steps for Phase 2 (Planning)
- [ ] Recommendations based on analysis

### Enhanced Mode Additional Report Sections
- [ ] Performance metrics section:
  - [ ] Total time vs baseline
  - [ ] Time saved in minutes and percentage
  - [ ] Parallel execution status
  - [ ] Total retries across all phases
  - [ ] Average quality score
- [ ] Quality scores per phase:
  - [ ] Brainstorming: {{brainstorm_quality_score}}/1.0
  - [ ] Market research: {{research_quality_score}}/1.0
  - [ ] Domain research: {{domain_quality_score}}/1.0
  - [ ] Product brief: {{product_brief_quality_score}}/1.0
- [ ] Quality check with enhanced criteria:
  - [ ] All quality scores ≥ 0.7 (or ≥ 0.8 for product brief)
  - [ ] Product brief integrates all previous phases
- [ ] Warnings/Recommendations:
  - [ ] Warning if avg quality score < 0.75
  - [ ] Warning if total retries > 3

### Report Output (Both Modes)
- [ ] Report saved to {output_folder}/complete-analysis-report.md
- [ ] Report displayed to user
- [ ] Final success message shown
- [ ] Next action clearly communicated (proceed to PRD)

### Final Display (Both Modes)
- [ ] Success message displayed
- [ ] Mode indicated (Standard or Enhanced)
- [ ] Enhanced mode: Time saved displayed
- [ ] All artifacts listed
- [ ] Enhanced mode: Quality scores shown per artifact
- [ ] Files location displayed
- [ ] Next action specified

---

## Early Exit Handling (Step 6)

### Partial Completion Detection (Both Modes)
- [ ] Workflow correctly identifies which phases completed
- [ ] Completed phases list is accurate
- [ ] Remaining phases list is accurate

### Partial Report Generation (Both Modes)
- [ ] Partial completion report generated
- [ ] Report includes mode (Standard or Enhanced)
- [ ] Report saved to {output_folder}/complete-analysis-partial-report.md
- [ ] Report explains workflow status
- [ ] Report provides resume instructions
- [ ] Report lists individual workflow commands

### Enhanced Mode Partial Report
- [ ] Quality scores for completed phases included
- [ ] Quality scores summary displayed
- [ ] Performance metrics for completed phases

### User Communication (Both Modes)
- [ ] Abort message displayed clearly
- [ ] User understands what was completed
- [ ] User knows how to resume or complete manually
- [ ] Enhanced mode: Quality scores for completed work shown

---

## Overall Workflow Quality

### Structure (Both Modes)
- [ ] All steps executed in correct order (0→1→2→3→4 or abort→6)
- [ ] No steps skipped unintentionally
- [ ] Flow between steps is logical
- [ ] Checkpoints occur at appropriate times (or skipped if configured)

### Standard Mode User Experience
- [ ] Workflow introduction is clear and helpful
- [ ] User understands the 4-phase sequential process
- [ ] 4 checkpoints are manageable (not overwhelming)
- [ ] User has sufficient control (continue/re-run/abort)
- [ ] Progress is visible throughout
- [ ] Final outcome is clear

### Enhanced Mode User Experience
- [ ] Workflow introduction explains enhanced features
- [ ] User understands parallel execution
- [ ] User understands quality gates
- [ ] Auto-retry logic works transparently
- [ ] Quality scores provide confidence
- [ ] Performance metrics show time savings
- [ ] User can skip checkpoints if desired
- [ ] Final outcome includes quality assessment

### Integration Quality (Both Modes)
- [ ] Sub-workflows invoked correctly
- [ ] Context passed between workflows appropriately
- [ ] Out4puts from earlier phases inform later phases
- [ ] No data loss between workflow invocations

### Standard Mode Error Handling
- [ ] Workflow pauses on errors
- [ ] User prompted to retry or abort
- [ ] Partial progress preserved
- [ ] Error messages clear and actionable

### Enhanced Mode Error Handling
- [ ] Quality gates detect issues automatically
- [ ] Auto-retry with generated feedback
- [ ] Max retries enforced (2 per phase default)
- [ ] User prompted after retry exhaustion
- [ ] Quality scores tracked even on retry
- [ ] Partial progress preserved

### Parallel Execution Quality (Enhanced Mode Only)
- [ ] Both workflows launch simultaneously
- [ ] Both workflows complete before proceeding
- [ ] No race conditions or conflicts
- [ ] Outputs combined correctly
- [ ] Performance time savings achieved (~50%)
- [ ] User can re-run either workflow independently

---

## Completeness Validation

### All Required Artifacts Generated (Both Modes)
- [ ] Brainstorming notes exist in {output_folder}
- [ ] Research findings exist in {output_folder}
- [ ] Domain research analysis exists in {output_folder}
- [ ] Product brief exists in {output_folder}
- [ ] Completion report exists in {output_folder}

### Artifact Quality (Both Modes)
- [ ] Each artifact is complete (no placeholders)
- [ ] Each artifact is coherent and well-structured
- [ ] Artifacts build logically on each other
- [ ] Product brief is comprehensive and ready for Phase 2

### Enhanced Mode Quality Validation
- [ ] All quality scores calculated correctly
- [ ] Brainstorming quality score ≥ 0.7 (or retried)
- [ ] Market research quality score ≥ 0.7 (or retried)
- [ ] Domain research quality score ≥ 0.7 (or retried)
- [ ] Product brief quality score ≥ 0.8 (or retried)
- [ ] Average quality score across all phases calculated
- [ ] Quality scores included in completion report

### Readiness for Phase 2 (Both Modes)
- [ ] Product brief contains sufficient detail for PRD
- [ ] Market research provides competitive context
- [ ] Domain research identifies technical constraints
- [ ] Brainstorming captured creative feature ideas
- [ ] User is confident to proceed to planning phase

### Enhanced Mode Readiness Indicators
- [ ] Average quality score ≥ 0.75 (good quality)
- [ ] Product brief integrates all previous phases
- [ ] All quality gates passed (or user overrode consciously)
- [ ] No excessive retries (< 3 total retries)
- [ ] Performance metrics show efficient execution

---

## Success Criteria

### Full Success - Standard Mode
- [ ] ✅ All 4 phases completed successfully
- [ ] ✅ All artifacts generated and saved
- [ ] ✅ Product brief is comprehensive and accurate
- [ ] ✅ Completion report generated
- [ ] ✅ User ready to proceed to Phase 2 (PRD)
- [ ] ✅ Total time ≤ 80 minutes

### Full Success - Enhanced Mode
- [ ] ✅ All 4 phases completed successfully
- [ ] ✅ All quality gates passed (scores ≥ 0.7 or 0.8)
- [ ] ✅ Parallel execution saved time (~50% faster)
- [ ] ✅ All artifacts generated and saved
- [ ] ✅ Product brief is comprehensive with quality score ≥ 0.8
- [ ] ✅ Product brief integrates all previous phases
- [ ] ✅ Completion report generated with metrics
- [ ] ✅ Average quality score ≥ 0.75
- [ ] ✅ Total retries ≤ 2
- [ ] ✅ User ready to proceed to Phase 2 (PRD)
- [ ] ✅ Total time ≤ 40 minutes

### Partial Success - Standard Mode
- [ ] ⚠️ User re-ran 1-2 phases for refinement (acceptable)
- [ ] ⚠️ One phase needed 2+ iterations to satisfy user
- [ ] ⚠️ User aborted but key artifacts (brief) were completed
- [ ] ⚠️ Total time > 80 minutes but < 120 minutes

### Partial Success - Enhanced Mode
- [ ] ⚠️ Some quality scores 0.6-0.7 (below target but acceptable)
- [ ] ⚠️ Product brief quality 0.7-0.8 (acceptable but not excellent)
- [ ] ⚠️ Retries occurred but within limit (2-3 retries total)
- [ ] ⚠️ User manually overrode quality gate failures
- [ ] ⚠️ Parallel execution had issues but completed
- [ ] ⚠️ Time savings less than expected (20-30% vs 50%)
- [ ] ⚠️ Average quality score 0.70-0.75 (acceptable)

### Failure - Standard Mode
- [ ] ❌ Workflow crashed or failed to execute
- [ ] ❌ Sub-workflow invocation failed repeatedly
- [ ] ❌ Product brief not generated or incomplete
- [ ] ❌ User aborted early with minimal artifacts created
- [ ] ❌ Artifacts are low quality or incoherent
- [ ] ❌ Total time > 120 minutes

### Failure - Enhanced Mode
- [ ] ❌ Quality gates failed and max retries exceeded
- [ ] ❌ Quality scores consistently < 0.6
- [ ] ❌ Product brief quality score < 0.7
- [ ] ❌ Product brief does not integrate previous phases
- [ ] ❌ Parallel execution failed completely
- [ ] ❌ Auto-retry logic malfunctioned
- [ ] ❌ Quality validation did not run when enabled
- [ ] ❌ Performance tracking failed
- [ ] ❌ Total retries > 5 (excessive)
- [ ] ❌ Average quality score < 0.6

---

## Post-Workflow Actions

### If Successful (Both Modes)
1. [ ] Review all generated artifacts
2. [ ] Validate product brief against original app idea
3. [ ] Ensure all insights captured
4. [ ] Enhanced mode: Review quality scores
5. [ ] Enhanced mode: Verify all phases integrated in product brief
6. [ ] Proceed to Phase 2: Run `/bmad:bmm:workflows:prd`

### If Partial Success (Both Modes)
1. [ ] Review completed phases
2. [ ] Enhanced mode: Review quality scores to identify weak areas
3. [ ] Complete remaining phases individually if needed
4. [ ] Standard mode: Refine any phase with concerns
5. [ ] Enhanced mode: Re-run phases with quality scores < 0.7
6. [ ] Ensure product brief is finalized
7. [ ] Then proceed to Phase 2

### If Failed (Both Modes)
1. [ ] Review error logs and completion/partial report
2. [ ] Identify failure point
3. [ ] Enhanced mode: Review which quality gates failed and why
4. [ ] Fix issues (missing files, configuration, quality criteria)
5. [ ] Run individual workflows manually to complete Phase 1
6. [ ] Enhanced mode: Adjust quality thresholds if too strict
7. [ ] OR re-run complete-analysis workflow after fixes

---

## Continuous Improvement

### After Each Execution (Both Modes)
- [ ] Document any manual interventions required
- [ ] Note any phases that took longer than expected
- [ ] Identify any user confusion points
- [ ] Suggest workflow improvements
- [ ] Update checklist with new edge cases

### Standard Mode Metrics to Track
- [ ] Actual time per phase vs estimates
- [ ] Number of re-runs per phase
- [ ] User satisfaction with outputs
- [ ] Checkpoint effectiveness

### Enhanced Mode Metrics to Track
- [ ] Quality scores trending (improving or declining?)
- [ ] Auto-retry effectiveness (success rate?)
- [ ] Parallel execution time savings (actual vs expected 50%)
- [ ] False positive rate on quality gates
- [ ] User override frequency (quality gates too strict?)
- [ ] Average quality score per workflow type
- [ ] Performance baseline accuracy

### Workflow Optimization Ideas (Both Modes)
- Add option to skip phases (e.g., domain research not always needed)
- Cache outputs to allow resuming from last checkpoint
- Add time estimates that adapt based on app complexity
- Improve error recovery for sub-workflow failures

### Enhanced Mode Optimization Ideas
- Tune quality gate thresholds based on success rates
- Add quality gate confidence levels (strict/moderate/lenient)
- Implement adaptive retry limits based on phase complexity
- Add quality trend analysis (improving over retries?)
- Parallelize brainstorming with research prep (potential 3-way parallel)
- Add smart checkpoint skipping (auto-skip if quality scores excellent)
- Implement quality score predictions before workflow runs
