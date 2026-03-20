---
name: swarm-plan
description: GitHub Analysis for Next.js contribution guide
type: execution-plan
---

# Swarm Execution Plan - GitHub Analysis (AB Test Version B)

## Task Overview
**Task Name:** Next.js Contribution Guide
**Objective:** Analyze vercel/next.js and create comprehensive contribution guide
**Success Criteria:** Guide covers setup, coding standards, PR process, and testing
**Estimated Duration:** 10 minutes

## Sub-Task Decomposition

| ID | Agent | Role | Task Description | Dependencies | Timeout | Model |
|----|-------|------|------------------|--------------|---------|-------|
| 1 | research | Researcher | Analyze repo structure, find CONTRIBUTING.md, identify key files and test setup | None | 180s | minimax-m2.7 |
| 2 | compile | Developer | Create comprehensive contribution guide with all sections | 1 | 300s | k2p5 |

## Execution Order
```
[1] Research → [2] Compile
```

## Output Files

| Agent | Output File | Description |
|-------|-------------|-------------|
| research | swarm-results-research-v2.md | Research findings |
| compile | swarm-results-compile-v2.md | Final contribution guide |

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Research timeout | Low | Medium | Use MiniMax for speed |
| Compile quality | Low | High | Use k2p5 for quality |

## Start Time: 11:01 AM
