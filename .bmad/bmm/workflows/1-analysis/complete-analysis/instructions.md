# Complete Analysis - Autonomous Phase 1 Workflow Instructions

<critical>The workflow execution engine is governed by: {project-root}/.bmad/core/tasks/workflow.xml</critical>
<critical>You MUST have already loaded and processed: {project-root}/.bmad/bmm/workflows/1-analysis/complete-analysis/workflow.yaml</critical>
<critical>Communicate in {communication_language} throughout the workflow execution</critical>

<workflow>

<step n="0" goal="Initialize Workflow and Capture App Idea">
  <action>Welcome {user_name} to the Complete Analysis workflow</action>

  <action>Detect enhancement mode from config:
  - Read enhancement_mode from workflow.yaml
  - If enhancement_mode == 'enhanced': Activate enhanced features
  - If enhancement_mode == 'standard' or unset: Use standard sequential mode
  </action>

  <action>Explain the workflow execution sequence:

  **This workflow will execute these BMM workflows in sequence:**

  1. `/bmad:bmm:workflows:workflow-init` - Initialize project tracking
  2. `/bmad:bmm:workflows:workflow-status` - Check current status
  3. `/bmad:bmm:workflows:brainstorm-project` - Brainstorm app concept
  4. `/bmad:bmm:workflows:research` - Market & competitive research
  5. `/bmad:bmm:workflows:domain-research` - Domain-specific analysis
  6. `/bmad:bmm:workflows:product-brief` - Synthesize into product brief

  **Mode: {{enhancement_mode == 'enhanced' ? 'ENHANCED MODE 🚀 (Parallel + Quality Gates)' : 'STANDARD MODE (Sequential)'}}**

  All outputs saved to: {output_folder}
  </action>

  <ask>Please describe your app idea or concept. Be as detailed or brief as you like - we'll explore it together:

  {{app_idea}}
  </ask>

  <action>Store the app idea as {{app_idea}} for use in all sub-workflows</action>
  <action>Initialize performance tracking if enhanced mode enabled</action>
</step>

<step n="0.1" goal="Initialize Project Workflow">
  <action>Announce: "🔧 **Initializing Project Workflow**"</action>
  <action>Explain: "Setting up project tracking and workflow status..."</action>

  <invoke-workflow path="{project-root}/.bmad/bmm/workflows/workflow-status/init/workflow.yaml">
    <input name="project_name" value="{{app_idea_summary}}" />
    <input name="output_folder" value="{output_folder}" />
  </invoke-workflow>

  <action>Workflow initialization complete</action>
</step>

<step n="0.2" goal="Check Workflow Status">
  <action>Announce: "📊 **Checking Workflow Status**"</action>
  <action>Explain: "Verifying project tracking is set up correctly..."</action>

  <invoke-workflow path="{project-root}/.bmad/bmm/workflows/workflow-status/workflow.yaml">
    <input name="output_folder" value="{output_folder}" />
  </invoke-workflow>

  <action>Status check complete</action>
</step>

<step n="1" goal="Execute Brainstorm Project Workflow">
  <action>Announce: "📊 **Step 1/4: Brainstorming Project**"</action>
  <action>Explain: "Executing /bmad:bmm:workflows:brainstorm-project to explore your app idea from multiple angles."</action>

  <action if="{{enhancement_mode == 'enhanced'}}">
  Enable quality gate validation:
  - Min ideas: 10
  - Min perspectives: 3
  - Min feature concepts: 5
  </action>

  <invoke-workflow path="{brainstorm_workflow}">
    <input name="app_idea" value="{{app_idea}}" />
    <input name="output_folder" value="{output_folder}" />
  </invoke-workflow>

  <action>After brainstorm-project completes, capture outputs:
  - brainstorm_notes: Document path
  - ideas_count: Count of ideas generated
  - perspectives_count: Count of perspectives explored
  - feature_concepts_count: Count of feature ideas
  </action>

  <check if="{{enhancement_mode == 'enhanced' AND enable_quality_gates}}">
    <action>Run quality gate validation</action>
    <action>Validate brainstorm output against criteria:
    - Min ideas: {{ideas_count >= 10 ? 'PASS ✅' : 'FAIL ❌'}}
    - Min perspectives: {{perspectives_count >= 3 ? 'PASS ✅' : 'FAIL ❌'}}
    - Min feature concepts: {{feature_concepts_count >= 5 ? 'PASS ✅' : 'FAIL ❌'}}
    - Has user value: {{has_user_value ? 'PASS ✅' : 'FAIL ❌'}}
    </action>

    <action>Calculate quality score:
    - Ideas weight: 0.3
    - Perspectives weight: 0.3
    - Feature concepts weight: 0.2
    - User value weight: 0.2
    - Total score: {{quality_score}}
    - Pass threshold: 0.7 (70%)
    </action>

    <check if="{{quality_score < 0.7}}">
      <action>Quality gate FAILED. Initiating auto-retry with feedback...</action>
      <action>Generate feedback for retry:
      - "Need {{10 - ideas_count}} more ideas (currently: {{ideas_count}})"
      - "Need {{3 - perspectives_count}} more perspectives (currently: {{perspectives_count}})"
      - "Need {{5 - feature_concepts_count}} more feature concepts (currently: {{feature_concepts_count}})"
      </action>
      <action>Re-invoke brainstorm-project workflow with feedback</action>
      <action>Max retries: {{max_retry_per_phase}} (default: 2)</action>
      <check if="{{retry_count >= max_retry_per_phase}}">
        <action>Max retries exceeded. Prompt user for manual intervention.</action>
        <ask>Quality gate validation failed after {{retry_count}} attempts. Continue anyway? [y/n]</ask>
      </check>
    </check>
  </check>

  <action>Display summary:

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ **Brainstorming Complete!**

  **Output Location:** Check {output_folder} for brainstorming notes

  **Key Insights Generated:**
  - Ideas generated: {{ideas_count}}
  - Perspectives explored: {{perspectives_count}}
  - Feature concepts: {{feature_concepts_count}}
  - Creative exploration of your app concept
  - Multiple perspectives and approaches
  - Initial feature ideas and directions

  {{enhancement_mode == 'enhanced' ? '**Quality Score:** ' + quality_score + '/1.0 ' + (quality_score >= 0.7 ? '✅ PASS' : '⚠️ NEEDS IMPROVEMENT') : ''}}

  **Next Phase:** {{enhancement_mode == 'enhanced' ? 'Parallel Research (Market + Domain)' : 'Market Research'}}
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  </action>

  <check if="{{!skip_checkpoints}}">
    <ask>How would you like to proceed?

    [c] **Continue** to {{enhancement_mode == 'enhanced' ? 'Parallel Research' : 'Market Research'}} (Step 2/4)
    [r] **Re-run** brainstorming with different approach
    [a] **Abort** workflow and exit

    Your choice:
    </ask>

    <check if="response == 'r' or response == 'R'">
      <action>User requested re-run of brainstorming</action>
      <goto step="1">Re-run brainstorming workflow</goto>
    </check>

    <check if="response == 'a' or response == 'A'">
      <action>User aborted workflow</action>
      <goto step="6">Exit with partial completion</goto>
    </check>

    <action if="response == 'c' or response == 'C'">Proceed to Step 2: Research</action>
  </check>

  <action if="{{skip_checkpoints}}">Auto-continuing to Step 2 (checkpoints disabled)</action>
</step>

<step n="2" goal="Execute Research Phase (Sequential or Parallel based on mode)">

  <!-- STANDARD MODE: Sequential Execution -->
  <check if="{{enhancement_mode != 'enhanced'}}">
    <action>Running in STANDARD MODE - Sequential execution</action>

    <!-- Market Research -->
    <action>Announce: "🔍 **Step 2a/4: Market & Competitive Research**"</action>
    <action>Explain: "Executing /bmad:bmm:workflows:research for market analysis and competitive insights."</action>

    <invoke-workflow path="{research_workflow}">
      <input name="brainstorm_output" value="{{brainstorm_notes}}" />
      <input name="app_idea" value="{{app_idea}}" />
      <input name="output_folder" value="{output_folder}" />
    </invoke-workflow>

    <action>After research completes, display summary:

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ✅ **Market Research Complete!**

    **Output Location:** Check {output_folder} for research findings

    **Research Coverage:**
    - Market landscape and opportunities
    - Competitive analysis
    - User behavior insights
    - Relevant trends and technologies

    **Next Phase:** Domain-Specific Research
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    </action>

    <check if="{{!skip_checkpoints}}">
      <ask>How would you like to proceed?

      [c] **Continue** to Domain Research (Step 2b/4)
      [r] **Re-run** market research with different focus
      [a] **Abort** workflow and exit

      Your choice:
      </ask>

      <check if="response == 'r' or response == 'R'">
        <action>User requested re-run of market research</action>
        <goto step="2">Re-run market research workflow</goto>
      </check>

      <check if="response == 'a' or response == 'A'">
        <action>User aborted workflow</action>
        <goto step="6">Exit with partial completion</goto>
      </check>
    </check>

    <!-- Domain Research -->
    <action>Announce: "🏛️ **Step 2b/4: Domain-Specific Research**"</action>
    <action>Explain: "Executing /bmad:bmm:workflows:domain-research for domain-specific requirements and regulations."</action>

    <invoke-workflow path="{domain_research_workflow}">
      <input name="brainstorm_output" value="{{brainstorm_notes}}" />
      <input name="research_findings" value="{{research_findings}}" />
      <input name="app_idea" value="{{app_idea}}" />
      <input name="output_folder" value="{output_folder}" />
    </invoke-workflow>

    <action>After domain-research completes, display summary:

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ✅ **Domain Research Complete!**

    **Output Location:** Check {output_folder} for domain research findings

    **Domain Coverage:**
    - Industry-specific requirements
    - Regulatory and compliance considerations
    - Domain patterns and conventions
    - Technical constraints and opportunities

    **Next Phase:** Product Brief Synthesis
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    </action>

    <check if="{{!skip_checkpoints}}">
      <ask>How would you like to proceed?

      [c] **Continue** to Product Brief (Step 3/4)
      [r] **Re-run** domain research with different focus
      [a] **Abort** workflow and exit

      Your choice:
      </ask>

      <check if="response == 'r' or response == 'R'">
        <action>User requested re-run of domain research</action>
        <action>Re-invoke domain-research workflow</action>
      </check>

      <check if="response == 'a' or response == 'A'">
        <action>User aborted workflow</action>
        <goto step="6">Exit with partial completion</goto>
      </check>
    </check>
  </check>

  <!-- ENHANCED MODE: Parallel Execution -->
  <check if="{{enhancement_mode == 'enhanced' AND enable_parallel_research}}">
    <action>Running in ENHANCED MODE - Parallel execution 🚀</action>
    <action>Announce: "🔍🏛️ **Step 2/4: Parallel Research (Market + Domain)**"</action>
    <action>Explain: "Executing /bmad:bmm:workflows:research AND /bmad:bmm:workflows:domain-research simultaneously for faster completion."</action>

    <action>Start performance timer for parallel execution</action>

    <action>Note: Launching both workflows in parallel (implementation depends on workflow execution engine's parallel support)</action>

    <!-- Market Research - Parallel Thread 1 -->
    <invoke-workflow path="{research_workflow}">
      <input name="brainstorm_output" value="{{brainstorm_notes}}" />
      <input name="app_idea" value="{{app_idea}}" />
      <input name="output_folder" value="{output_folder}" />
      <parallel>true</parallel>
      <timeout>30</timeout>
    </invoke-workflow>

    <!-- Domain Research - Parallel Thread 2 -->
    <invoke-workflow path="{domain_research_workflow}">
      <input name="brainstorm_output" value="{{brainstorm_notes}}" />
      <input name="app_idea" value="{{app_idea}}" />
      <input name="output_folder" value="{output_folder}" />
      <parallel>true</parallel>
      <timeout>30</timeout>
    </invoke-workflow>

    <action>Monitor both workflows in parallel:
    - Display progress indicators
    - Show which workflow completes first
    - Wait for both to finish
    </action>

    <action>After BOTH workflows complete, run quality gates</action>

    <!-- Quality Gate: Market Research -->
    <action>Validate Market Research output:
    - Competitors analyzed: {{competitors_count}} (min: 5) {{competitors_count >= 5 ? '✅' : '❌'}}
    - Research sources: {{sources_count}} (min: 10) {{sources_count >= 10 ? '✅' : '❌'}}
    - Trends identified: {{trends_count}} (min: 3) {{trends_count >= 3 ? '✅' : '❌'}}
    - Market size estimation: {{has_market_size ? '✅' : '❌'}}
    - Quality score: {{research_quality_score}}/1.0 (threshold: 0.7)
    </action>

    <check if="{{research_quality_score < 0.7}}">
      <action>Market research quality gate FAILED</action>
      <action>Auto-retry market research with feedback (enhanced mode)</action>
      <action>Re-run only market research workflow (not domain)</action>
    </check>

    <!-- Quality Gate: Domain Research -->
    <action>Validate Domain Research output:
    - Domain patterns: {{patterns_count}} (min: 3) {{patterns_count >= 3 ? '✅' : '❌'}}
    - Constraints identified: {{constraints_count}} (min: 2) {{constraints_count >= 2 ? '✅' : '❌'}}
    - Regulatory check: {{has_regulatory_check ? '✅' : '❌'}}
    - Technical constraints: {{has_technical_constraints ? '✅' : '❌'}}
    - Quality score: {{domain_quality_score}}/1.0 (threshold: 0.7)
    </action>

    <check if="{{domain_quality_score < 0.7}}">
      <action>Domain research quality gate FAILED</action>
      <action>Auto-retry domain research with feedback (enhanced mode)</action>
      <action>Re-run only domain research workflow (not market)</action>
    </check>

    <action>Stop performance timer and calculate parallel execution time</action>
    <action>Compare to baseline (standard mode would take ~40 min, parallel should take ~20 min)</action>

    <action>Display combined summary:

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ✅ **Parallel Research Complete!** 🚀

    **Execution Time:** {{parallel_execution_time}} minutes (Standard would take ~40 min)
    **Time Saved:** {{40 - parallel_execution_time}} minutes ({{((40 - parallel_execution_time) / 40 * 100).toFixed(0)}}% faster)

    **Market Research Results:**
    - Competitors analyzed: {{competitors_count}} ✅
    - Research sources: {{sources_count}} ✅
    - Trends identified: {{trends_count}} ✅
    - Quality score: {{research_quality_score}}/1.0 {{research_quality_score >= 0.7 ? '✅ PASS' : '⚠️'}}
    - Output: {output_folder}/research-findings.md

    **Domain Research Results:**
    - Domain patterns: {{patterns_count}} ✅
    - Constraints: {{constraints_count}} ✅
    - Regulatory check: {{has_regulatory_check ? 'Complete' : 'N/A'}}
    - Quality score: {{domain_quality_score}}/1.0 {{domain_quality_score >= 0.7 ? '✅ PASS' : '⚠️'}}
    - Output: {output_folder}/domain-research.md

    **Next Phase:** Product Brief Synthesis
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    </action>

    <check if="{{!skip_checkpoints}}">
      <ask>How would you like to proceed?

      [c] **Continue** to Product Brief (Step 3/4)
      [m] **Re-run** market research only
      [d] **Re-run** domain research only
      [b] **Re-run** both research workflows
      [a] **Abort** workflow and exit

      Your choice:
      </ask>

      <check if="response == 'm' or response == 'M'">
        <action>Re-run market research only</action>
        <action>Invoke {research_workflow} again</action>
      </check>

      <check if="response == 'd' or response == 'D'">
        <action>Re-run domain research only</action>
        <action>Invoke {domain_research_workflow} again</action>
      </check>

      <check if="response == 'b' or response == 'B'">
        <action>Re-run both research workflows in parallel</action>
        <goto step="2">Re-run entire parallel research step</goto>
      </check>

      <check if="response == 'a' or response == 'A'">
        <action>User aborted workflow</action>
        <goto step="6">Exit with partial completion</goto>
      </check>
    </check>
  </check>
</step>

<step n="3" goal="Execute Product Brief Workflow">
  <action>Announce: "📋 **Step 3/4: Product Brief Generation**"</action>
  <action>Explain: "Executing /bmad:bmm:workflows:product-brief to synthesize all insights into a comprehensive product brief."</action>

  <action if="{{enhancement_mode == 'enhanced'}}">
  Enable product brief quality gate:
  - All required sections present
  - Integration quality (references all previous phases)
  - Minimum word count: 2000
  - At least 3 success metrics
  - Pass threshold: 0.8 (80% - higher bar for final deliverable)
  </action>

  <invoke-workflow path="{product_brief_workflow}">
    <input name="app_idea" value="{{app_idea}}" />
    <input name="brainstorm_notes" value="{{brainstorm_notes}}" />
    <input name="research_findings" value="{{research_findings}}" />
    <input name="domain_analysis" value="{{domain_analysis}}" />
    <input name="output_folder" value="{output_folder}" />
  </invoke-workflow>

  <action>After product-brief completes, capture outputs and run validation</action>

  <check if="{{enhancement_mode == 'enhanced' AND enable_quality_gates}}">
    <action>Run comprehensive quality gate validation</action>

    <action>Validate product brief against criteria:

    **Required Sections:**
    - Vision: {{has_vision ? '✅' : '❌'}}
    - Target Audience: {{has_target_audience ? '✅' : '❌'}}
    - Market Positioning: {{has_market_positioning ? '✅' : '❌'}}
    - Feature Concepts: {{has_feature_concepts ? '✅' : '❌'}}
    - Success Metrics: {{has_success_metrics ? '✅' : '❌'}}
    - Constraints: {{has_constraints ? '✅' : '❌'}}
    - Risks: {{has_risks ? '✅' : '❌'}}

    **Integration Quality:**
    - References brainstorming: {{references_brainstorm ? '✅' : '❌'}}
    - References research: {{references_research ? '✅' : '❌'}}
    - References domain: {{references_domain ? '✅' : '❌'}}

    **Content Quality:**
    - Word count: {{word_count}} (min: 2000) {{word_count >= 2000 ? '✅' : '❌'}}
    - Success metrics count: {{metrics_count}} (min: 3) {{metrics_count >= 3 ? '✅' : '❌'}}
    - Vision clarity: {{vision_clarity_score}}/1.0
    - Value proposition: {{value_prop_score}}/1.0

    **Overall Quality Score:** {{product_brief_quality_score}}/1.0
    **Pass Threshold:** 0.8
    **Result:** {{product_brief_quality_score >= 0.8 ? '✅ PASS' : '❌ FAIL'}}
    </action>

    <check if="{{product_brief_quality_score < 0.8}}">
      <action>Product brief quality gate FAILED</action>
      <action>Generate detailed feedback:

      **Issues Found:**
      {{!has_vision ? '- Missing clear vision statement' : ''}}
      {{!has_target_audience ? '- Target audience not defined' : ''}}
      {{!references_brainstorm ? '- Does not reference brainstorming insights' : ''}}
      {{!references_research ? '- Does not reference market research data' : ''}}
      {{!references_domain ? '- Does not account for domain requirements' : ''}}
      {{word_count < 2000 ? '- Document too brief (need ' + (2000 - word_count) + ' more words)' : ''}}
      {{metrics_count < 3 ? '- Need ' + (3 - metrics_count) + ' more success metrics' : ''}}

      **Recommendations:**
      - Ensure all 7 required sections are complete
      - Reference specific insights from brainstorming, research, and domain analysis
      - Expand on product vision and value proposition
      - Add measurable success metrics (target: 3-5)
      </action>

      <action>Auto-retry with feedback (enhanced mode)</action>
      <action>Re-invoke product-brief workflow with feedback and previous outputs as additional context</action>
      <action>Max retries: {{max_retry_per_phase}}</action>

      <check if="{{retry_count >= max_retry_per_phase}}">
        <action>Max retries exceeded for product brief</action>
        <ask>Quality gate validation failed after {{retry_count}} attempts. Continue anyway? [y/n]</ask>
        <check if="response == 'n' or response == 'N'">
          <goto step="3">Manually re-run product brief generation</goto>
        </check>
      </check>
    </check>
  </check>

  <action>Display summary:

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ **Product Brief Complete!**

  **Output Location:** Check {output_folder} for product brief document

  **Brief Contents:**
  - Product vision and goals
  - Target audience and user needs
  - Market positioning
  - Feature concepts
  - Success metrics ({{metrics_count}})
  - Constraints and risks

  {{enhancement_mode == 'enhanced' ? '**Quality Score:** ' + product_brief_quality_score + '/1.0 ' + (product_brief_quality_score >= 0.8 ? '✅ EXCELLENT' : product_brief_quality_score >= 0.7 ? '⚠️ ACCEPTABLE' : '❌ NEEDS WORK') : ''}}

  {{enhancement_mode == 'enhanced' ? '**Integration Quality:** ' + (references_brainstorm && references_research && references_domain ? '✅ All phases integrated' : '⚠️ Missing integration') : ''}}

  **Phase 1 Analysis:** COMPLETE ✅
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  </action>

  <check if="{{!skip_checkpoints}}">
    <ask>How would you like to proceed?

    [c] **Continue** to completion report
    [r] **Re-run** product brief with refinements
    [a] **Abort** workflow

    Your choice:
    </ask>

    <check if="response == 'r' or response == 'R'">
      <action>User requested re-run of product brief</action>
      <goto step="3">Re-run product-brief workflow</goto>
    </check>

    <check if="response == 'a' or response == 'A'">
      <action>User aborted workflow</action>
      <goto step="6">Exit with partial completion</goto>
    </check>

    <action if="response == 'c' or response == 'C'">Proceed to Step 4: Completion Report</action>
  </check>

  <action if="{{skip_checkpoints}}">Auto-continuing to Step 4 (checkpoints disabled)</action>
</step>

<step n="4" goal="Generate Completion Report">
  <action>Create comprehensive completion report</action>

  <action>Calculate total workflow metrics:
  - Total execution time: {{total_workflow_time}} minutes
  - Baseline (standard mode): 80 minutes
  - Time saved (if enhanced): {{80 - total_workflow_time}} minutes ({{((80 - total_workflow_time) / 80 * 100).toFixed(0)}}%)
  - Quality scores (if enhanced): All quality gates
  - Retry count per phase: {{total_retries}}
  </action>

  <action>Generate report with following sections:

  # Complete Analysis - Workflow Report

  **Date:** {date}
  **User:** {user_name}
  **Mode:** {{enhancement_mode == 'enhanced' ? 'Enhanced Mode 🚀' : 'Standard Mode'}}
  **Project:** {{app_idea_summary}}

  ---

  ## Phase 1 Analysis: COMPLETE ✅

  ### Workflow Execution Summary

  All Phase 1 analysis steps completed successfully:

  1. ✅ **Brainstorming** - Creative exploration of app concept
     {{enhancement_mode == 'enhanced' ? '   - Quality Score: ' + brainstorm_quality_score + '/1.0' : ''}}
     {{enhancement_mode == 'enhanced' ? '   - Ideas: ' + ideas_count + ' | Perspectives: ' + perspectives_count : ''}}

  2. ✅ **Market Research** - Competitive landscape and trends
     {{enhancement_mode == 'enhanced' ? '   - Quality Score: ' + research_quality_score + '/1.0' : ''}}
     {{enhancement_mode == 'enhanced' ? '   - Competitors: ' + competitors_count + ' | Sources: ' + sources_count : ''}}

  3. ✅ **Domain Research** - Domain-specific requirements and patterns
     {{enhancement_mode == 'enhanced' ? '   - Quality Score: ' + domain_quality_score + '/1.0' : ''}}
     {{enhancement_mode == 'enhanced' ? '   - Patterns: ' + patterns_count + ' | Constraints: ' + constraints_count : ''}}

  4. ✅ **Product Brief** - Synthesized insights into structured brief
     {{enhancement_mode == 'enhanced' ? '   - Quality Score: ' + product_brief_quality_score + '/1.0' : ''}}
     {{enhancement_mode == 'enhanced' ? '   - Word Count: ' + word_count + ' | Metrics: ' + metrics_count : ''}}

  {{enhancement_mode == 'enhanced' ? '### Performance Metrics\n\n- **Total Time:** ' + total_workflow_time + ' minutes (Baseline: 80 min)\n- **Time Saved:** ' + (80 - total_workflow_time) + ' minutes (' + ((80 - total_workflow_time) / 80 * 100).toFixed(0) + '% faster)\n- **Parallel Execution:** ' + (enable_parallel_research ? 'Enabled ✅' : 'Disabled') + '\n- **Retries:** ' + total_retries + ' total\n- **Average Quality Score:** ' + avg_quality_score + '/1.0' : ''}}

  ### Generated Artifacts

  **Location:** {output_folder}

  - **Brainstorming Notes** - Creative ideas and directions
  - **Research Findings** - Market analysis and competitive insights
  - **Domain Research** - Industry requirements and regulations
  - **Product Brief** - Comprehensive product vision and strategy

  ### Quality Check

  Review the generated documents to ensure:
  - [ ] Product brief captures your vision accurately
  - [ ] Market research identified key competitors
  - [ ] Domain research covers relevant regulations/patterns
  - [ ] All insights from brainstorming incorporated
  {{enhancement_mode == 'enhanced' ? '- [ ] All quality scores ≥ 0.7 (brainstorm, research, domain) or ≥ 0.8 (product brief)' : ''}}
  {{enhancement_mode == 'enhanced' ? '- [ ] Product brief integrates all previous phases' : ''}}

  ### Next Steps: Phase 2 (Planning)

  You're now ready to proceed to Phase 2 - Planning:

  **Option 1: Full Planning (Recommended)**
  - Run `/bmad:bmm:workflows:prd` to generate Product Requirements Document
  - This creates detailed functional and technical requirements

  **Option 2: Quick Architecture**
  - Run `/bmad:bmm:workflows:architecture` to design system architecture
  - Use this if requirements are already clear

  **Option 3: Continue Complete Workflow**
  - If a "complete-planning" workflow exists, run it for automated Phase 2

  ### Recommendations

  Based on the analysis completed:
  - Review the product brief thoroughly before proceeding
  - Validate market assumptions with stakeholders if applicable
  - Ensure domain requirements are complete and accurate
  - Use the insights to inform PRD creation in Phase 2
  {{enhancement_mode == 'enhanced' && avg_quality_score < 0.75 ? '- ⚠️ Some quality scores below target - consider refining before Phase 2' : ''}}
  {{enhancement_mode == 'enhanced' && total_retries > 3 ? '- ⚠️ Multiple retries occurred - review outputs for quality' : ''}}

  ---

  **Congratulations!** Phase 1 (Analysis) is complete. You have a solid foundation to move into detailed planning.
  </action>

  <action>Save report to {default_output_file}</action>

  <action>Display final message to {user_name}:

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🎉 **Complete Analysis Workflow: SUCCESS!**

  {{enhancement_mode == 'enhanced' ? '**Mode:** Enhanced Mode 🚀 (Parallel + Quality Gates)' : '**Mode:** Standard Mode'}}
  {{enhancement_mode == 'enhanced' ? '**Time:** ' + total_workflow_time + ' minutes (Saved ' + (80 - total_workflow_time) + ' min vs standard)' : ''}}

  **All Phase 1 artifacts generated:**
  - Brainstorming notes {{enhancement_mode == 'enhanced' ? '(Score: ' + brainstorm_quality_score + ')' : ''}}
  - Market research findings {{enhancement_mode == 'enhanced' ? '(Score: ' + research_quality_score + ')' : ''}}
  - Domain research analysis {{enhancement_mode == 'enhanced' ? '(Score: ' + domain_quality_score + ')' : ''}}
  - Product brief {{enhancement_mode == 'enhanced' ? '(Score: ' + product_brief_quality_score + ')' : ''}}
  - Completion report

  **Files saved to:** {output_folder}

  **Next Action:** Review the product brief, then proceed to Phase 2 (PRD)

  Run: `/bmad:bmm:workflows:prd`
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  </action>
</step>

<step n="6" goal="Handle Early Exit">
  <action>User aborted workflow before completion</action>

  <action>Determine which phases were completed:
  - Check if brainstorming output exists
  - Check if research output exists
  - Check if domain research output exists
  - Check if product brief output exists
  </action>

  <action>Generate partial completion report:

  # Complete Analysis - Partial Completion Report

  **Date:** {date}
  **User:** {user_name}
  **Mode:** {{enhancement_mode == 'enhanced' ? 'Enhanced Mode' : 'Standard Mode'}}
  **Status:** Workflow aborted by user

  ---

  ## Completed Phases

  {{list_completed_phases}}

  {{enhancement_mode == 'enhanced' ? '### Quality Scores (Completed Phases)\n\n' + quality_scores_summary : ''}}

  ## Remaining Phases

  {{list_remaining_phases}}

  ## Next Steps

  To complete Phase 1 analysis:
  - Resume workflow: `/bmad:bmm:workflows:complete-analysis`
  - OR run individual workflows for remaining phases

  **Individual Workflows:**
  - Brainstorming: `/bmad:bmm:workflows:brainstorm-project`
  - Research: `/bmad:bmm:workflows:research`
  - Domain Research: `/bmad:bmm:workflows:domain-research`
  - Product Brief: `/bmad:bmm:workflows:product-brief`

  ---
  </action>

  <action>Save partial report to {output_folder}/complete-analysis-partial-report.md</action>

  <action>Display message:

  ⚠️ **Workflow Aborted**

  Partial completion report saved to: {output_folder}

  {{enhancement_mode == 'enhanced' ? 'Quality scores for completed phases saved in report.' : ''}}

  You can resume analysis at any time by running the individual workflows or re-running the complete-analysis workflow.
  </action>
</step>

</workflow>

## Workflow Notes

### Enhancement Mode

**Standard Mode** (ENHANCEMENT_MODE: standard or unset):
- Sequential execution (brainstorm → research → domain → brief)
- Manual checkpoints after each phase
- No automatic quality validation
- User controls all quality decisions
- Estimated time: 80 minutes

**Enhanced Mode** (ENHANCEMENT_MODE: enhanced):
- Parallel execution (research + domain run simultaneously)
- Automatic quality gate validation
- Auto-retry with feedback on failures
- Performance tracking and metrics
- Estimated time: 40 minutes (50% faster)
- Quality scores tracked for continuous improvement

### Agent Responsibilities

**Analyst Agent (Mary)** orchestrates this entire workflow:
- Executes all sub-workflows autonomously
- Reviews outputs for quality (enhanced mode)
- Provides checkpoint summaries
- Generates completion report
- Runs quality gate validation (enhanced mode)
- Initiates auto-retry logic (enhanced mode)

### User Experience

**Standard Mode:**
- Provide app idea at start
- Review and approve at 4 checkpoints (after each phase)
- Option to re-run any phase if output isn't satisfactory
- Manual quality assessment

**Enhanced Mode:**
- Provide app idea at start
- Automatic quality validation at each phase
- Fewer manual checkpoints (optional - can skip)
- Auto-retry if quality gates fail
- Performance metrics displayed
- Overall faster execution through parallelization

### Quality Gates (Enhanced Mode Only)

**Brainstorming:**
- Min 10 ideas, 3 perspectives, 5 feature concepts
- Must have clear user value proposition
- Pass threshold: 70%

**Market Research:**
- Min 5 competitors analyzed
- Min 10 research sources
- Min 3 trends identified
- Must have market size estimation
- Pass threshold: 70%

**Domain Research:**
- Min 3 domain patterns
- Min 2 constraints
- Must have regulatory check
- Must have technical constraints
- Pass threshold: 70%

**Product Brief:**
- All 7 required sections present
- Must reference all previous phases
- Min 2000 words
- Min 3 success metrics
- Pass threshold: 80% (higher bar)

### Error Handling

**Standard Mode:**
- Workflow pauses on errors
- User prompted to retry or abort
- Partial progress saved

**Enhanced Mode:**
- Auto-retry with generated feedback
- Max 2 retries per phase (configurable)
- If retries exhausted, prompt user
- Quality scores tracked even on retry
- Partial progress saved

### Parallel Execution (Enhanced Mode)

When enabled:
- Market and Domain research run simultaneously
- Both workflows must complete before proceeding
- Single combined checkpoint after both finish
- User can re-run either or both independently
- Time savings: ~50% (40 min vs 80 min)

### Output Organization

All artifacts saved to `{output_folder}`:
- Brainstorming notes
- Research findings document
- Domain research analysis
- Product brief
- Complete-analysis-report.md (or partial-report.md if aborted)

### Integration with Phase 2

This workflow prepares inputs for Phase 2 (Planning):
- Product brief feeds into PRD workflow
- Research findings inform requirements
- Domain research guides technical constraints
- Brainstorming ideas shape feature set
- Quality scores (enhanced mode) indicate readiness for next phase
