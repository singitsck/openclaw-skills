# Swarm Execution Templates

This file contains reusable templates for swarm execution.

## swarm-plan.md Template

```markdown
# Swarm Execution Plan

## Task Overview
**Task Name:** [Name]
**Objective:** [Clear objective statement]
**Success Criteria:** [How to know it's done]
**Estimated Duration:** [X minutes]

## Sub-Task Decomposition

| ID | Agent | Role | Task Description | Dependencies | Timeout | Model |
|----|-------|------|------------------|--------------|---------|-------|
| 1 | research | Researcher | [Specific research task] | None | 180s | minimax-m2.7 |
| 2 | design | Designer | [Design task] | None | 240s | minimax-m2.7 |
| 3 | dev | Developer | [Development task] | 1, 2 | 600s | k2p5 |
| 4 | test | Tester | [Testing task] | 3 | 120s | minimax-m2.7 |

## Execution Order
```
[1] Research ──┐
               ├──→ [3] Development ──→ [4] Testing
[2] Design  ───┘
```

## Output Files

| Agent | Output File | Description |
|-------|-------------|-------------|
| research | swarm-results-research.md | Research findings |
| design | swarm-results-design.md | Design specifications |
| dev | swarm-results-dev.md | Code and implementation |
| test | swarm-results-test.md | Test results |

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| [Risk 1] | Low/Med/High | Low/Med/High | [Strategy] |
| [Risk 2] | Low/Med/High | Low/Med/High | [Strategy] |

## Integration Plan

1. Read all individual result files
2. Extract key findings from each
3. Resolve any conflicts
4. Combine into cohesive deliverable
5. Write to swarm-results-integrated.md
```

---

## swarm-status.md Template

```markdown
# Swarm Execution Status

**Started:** [Timestamp]
**Last Updated:** [Timestamp]
**Overall Status:** [Planning | Running | Complete | Failed]

## Agent Status

| Agent | Status | Started | Completed | Retries | Notes |
|-------|--------|---------|-----------|---------|-------|
| research | pending/running/complete/failed | - | - | 0/2 | - |
| design | pending/running/complete/failed | - | - | 0/2 | - |
| dev | pending/running/complete/failed | - | - | 0/2 | - |
| test | pending/running/complete/failed | - | - | 0/2 | - |

## Progress Timeline

- [T+0] Swarm initialized
- [T+X] Agent [name] started
- [T+X] Agent [name] completed
- [T+X] Integration started
- [T+X] Swarm complete

## Blockers

| Issue | Agent | Severity | Action Required |
|-------|-------|----------|-----------------|
| [Description] | [Agent] | Low/Med/High | [Action] |

## Metrics

- **Total Agents:** [N]
- **Completed:** [N]
- **Failed:** [N]
- **Retries:** [N]
- **Total Duration:** [X minutes]
- **Total Tokens:** [N]
```

---

## swarm-results-[agent].md Templates

### Research Agent Results

```markdown
# Research Results

**Agent:** research
**Task:** [Task description]
**Completed:** [Timestamp]
**Duration:** [X minutes]

## Key Findings

### Finding 1: [Title]
[Detailed description]
- Source: [URL or reference]
- Relevance: [High/Med/Low]

### Finding 2: [Title]
[Detailed description]
- Source: [URL or reference]
- Relevance: [High/Med/Low]

## Data Collected

| Item | Value | Source |
|------|-------|--------|
| [Metric] | [Value] | [Source] |

## Analysis

[Interpretation of findings]

## Recommendations

1. [Recommendation 1]
2. [Recommendation 2]

## Sources

1. [URL] - [Description]
2. [URL] - [Description]
```

### Developer Agent Results

```markdown
# Development Results

**Agent:** dev
**Task:** [Task description]
**Completed:** [Timestamp]
**Duration:** [X minutes]

## Files Created

| File | Lines | Purpose |
|------|-------|---------|
| [path/to/file] | [N] | [Description] |

## Code Structure

```
[Directory structure or module overview]
```

## Key Implementation Details

### [Component 1]
- Purpose: [Description]
- Approach: [How it works]
- Dependencies: [List]

### [Component 2]
- Purpose: [Description]
- Approach: [How it works]
- Dependencies: [List]

## Testing

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Known Issues

| Issue | Severity | Notes |
|-------|----------|-------|
| [Description] | Low/Med/High | [Notes] |

## Next Steps

1. [Step 1]
2. [Step 2]
```

### Designer Agent Results

```markdown
# Design Results

**Agent:** design
**Task:** [Task description]
**Completed:** [Timestamp]
**Duration:** [X minutes]

## Design System

### Colors
| Name | Hex | Usage |
|------|-----|-------|
| Primary | #XXX | [Usage] |
| Secondary | #XXX | [Usage] |

### Typography
| Element | Font | Size | Weight |
|---------|------|------|--------|
| H1 | [Font] | [Size] | [Weight] |
| Body | [Font] | [Size] | [Weight] |

### Spacing
| Element | Value |
|---------|-------|
| Margin | [Value] |
| Padding | [Value] |

## Layouts

### Layout 1: [Name]
[Description or ASCII diagram]

### Layout 2: [Name]
[Description or ASCII diagram]

## Assets

| Asset | Format | Location |
|-------|--------|----------|
| [Name] | [Format] | [Path] |

## Accessibility Notes

- [Note 1]
- [Note 2]
```

### Tester Agent Results

```markdown
# Test Results

**Agent:** test
**Task:** [Task description]
**Completed:** [Timestamp]
**Duration:** [X minutes]

## Test Summary

| Metric | Value |
|--------|-------|
| Total Tests | [N] |
| Passed | [N] |
| Failed | [N] |
| Skipped | [N] |
| Coverage | [X%] |

## Test Cases

### Test 1: [Name]
- **Status:** ✅ Pass / ❌ Fail
- **Description:** [What it tests]
- **Steps:** [Test steps]
- **Expected:** [Expected result]
- **Actual:** [Actual result]

### Test 2: [Name]
[Same format]

## Issues Found

| ID | Severity | Description | Reproduction |
|----|----------|-------------|--------------|
| 1 | Low/Med/High | [Description] | [Steps] |

## Performance Metrics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Load time | [X]s | < [Y]s | ✅/❌ |
| Memory usage | [X]MB | < [Y]MB | ✅/❌ |

## Recommendations

1. [Recommendation 1]
2. [Recommendation 2]
```

---

## swarm-results-integrated.md Template

```markdown
# Integrated Results

**Generated:** [Timestamp]
**Agents:** [List of contributing agents]
**Status:** Complete / Partial / Failed

## Executive Summary

[Brief overview of what was accomplished]

## Detailed Results

### Research Insights
[Summary of research findings]

### Design Specifications
[Summary of design system]

### Implementation
[Summary of development work]

### Quality Assurance
[Summary of testing results]

## Deliverables

| Item | Status | Location |
|------|--------|----------|
| [Deliverable 1] | ✅ Complete | [Path] |
| [Deliverable 2] | ⚠️ Partial | [Path] |
| [Deliverable 3] | ❌ Failed | N/A |

## Known Limitations

1. [Limitation 1]
2. [Limitation 2]

## Next Actions

1. [Action 1]
2. [Action 2]

## Appendix

- Research details: swarm-results-research.md
- Design details: swarm-results-design.md
- Development details: swarm-results-dev.md
- Test details: swarm-results-test.md
```

---

## Agent Role Definition Templates

### supervisor-role.md

```markdown
# Supervisor Agent Role

## Identity
- **Name:** Supervisor
- **Model:** k2-thinking
- **Role:** CEO / Orchestrator

## Responsibilities
1. Task analysis and decomposition
2. Agent spawning and coordination
3. Progress monitoring
4. Error recovery
5. Result integration

## Decision Authority
- Can spawn/kill agents
- Can switch models
- Can modify execution plan
- Cannot directly execute sub-tasks

## Success Criteria
- All sub-tasks complete or properly handled
- Results integrated successfully
- No unhandled failures
```

### worker-research-role.md

```markdown
# Research Agent Role

## Identity
- **Name:** Researcher
- **Model:** MiniMax M2.7
- **Role:** Information Gatherer

## Responsibilities
1. Search for information
2. Analyze sources
3. Synthesize findings
4. Write to swarm-results-research.md

## Tools
- web_search
- web_fetch
- write

## Output Format
See: templates.md#research-agent-results
```

[Similar for Developer, Designer, Tester roles]
