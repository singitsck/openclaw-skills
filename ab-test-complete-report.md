# AB Test Report - Swarm Solver Format Comparison

## Executive Summary

**Test Date:** 2026-03-20  
**Test Duration:** ~15 minutes  
**Test Task:** GitHub Repository Analysis (vercel/next.js)  
**Winner:** Version A (Original Format) by 0.8 points

---

## Detailed Results

### Version A (Original Format)

**Execution Summary:**
- **Start:** 10:55 AM
- **End:** 11:00 AM
- **Duration:** 5 minutes
- **Status:** ✅ Success (first try)

**Agents:**
| Agent | Model | Duration | Status |
|-------|-------|----------|--------|
| worker-research-v1 | MiniMax M2.7 | 1m54s | ✅ Success |
| worker-compile-v1 | k2p5 | 1m59s | ✅ Success |

**Output:**
- File: swarm-results-compile.md
- Size: ~15KB
- Quality: 9/10
- Content: Complete contribution guide with 5 sections

**Metrics:**
| Metric | Value | Score |
|--------|-------|-------|
| Success | Yes | 100% |
| Duration | 5 min | 89% |
| Quality | 9/10 | 90% |
| Token Usage | 245K | 51% |
| UX | 8/10 | 80% |
| **Weighted Score** | | **85.5** |

**Strengths:**
- Fast execution
- No errors or retries needed
- High quality output
- Smooth user experience

**Weaknesses:**
- Error handling not tested
- Higher token usage

---

### Version B (Anthropic Format)

**Execution Summary:**
- **Start:** 11:01 AM
- **End:** 11:07 AM
- **Duration:** 6 minutes
- **Status:** ✅ Success (with retry)

**Agents:**
| Agent | Model | Duration | Status |
|-------|-------|----------|--------|
| worker-research-v2 | MiniMax M2.7 | 2m56s | ⚠️ Timeout |
| worker-research-v2-retry | k2p5 | 1m23s | ✅ Success |
| worker-compile-v2 | k2p5 | 1m24s | ✅ Success |

**Output:**
- File: swarm-results-compile-v2.md
- Size: ~6KB
- Quality: 8/10
- Content: Structured guide with tables

**Metrics:**
| Metric | Value | Score |
|--------|-------|-------|
| Success | Yes (retry) | 100% |
| Duration | 6 min | 67% |
| Quality | 8/10 | 80% |
| Token Usage | 68K | 86% |
| UX | 7/10 | 70% |
| **Weighted Score** | | **84.7** |

**Strengths:**
- Error handling tested and successful
- 72% token savings
- Structured YAML frontmatter
- Complete documentation

**Weaknesses:**
- Initial research timeout
- Slower due to retry
- Slightly lower output quality

---

## Side-by-Side Comparison

| Aspect | Version A | Version B | Difference |
|--------|-----------|-----------|------------|
| **Time** | 5 min | 6 min | A +1 min faster |
| **Success Method** | First try | Retry needed | A more reliable |
| **Error Handling** | Not tested | ✅ Verified | B tested |
| **Output Quality** | 9/10 | 8/10 | A +1 point |
| **Token Usage** | 245K | 68K | B 72% less |
| **UX Score** | 8/10 | 7/10 | A +1 point |
| **Plan Structure** | Simple MD | YAML + Tables | B more structured |
| **Documentation** | Basic | Complete | B better |

---

## Key Findings

### 1. Performance
- **Version A** is faster and more reliable
- **Version B** has overhead from structured format

### 2. Robustness
- **Version A** didn't encounter errors
- **Version B** successfully handled timeout with retry

### 3. Cost Efficiency
- **Version A** uses more tokens (245K)
- **Version B** significantly cheaper (68K, 72% savings)

### 4. Quality
- **Version A** produces slightly better output
- **Version B** has good quality with better structure

---

## Unexpected Discoveries

⚠️ **Version B Research Agent Timeout**
- Likely cause: More detailed skill description led to deeper analysis
- Result: Error handling mechanism successfully triggered and recovered
- Impact: Added ~1 minute to total time

---

## Conclusion

### Winner: Version A (Original Format)

**Score:** 85.5 vs 84.7 (0.8 point margin)

**Reasons:**
1. Faster execution (5 vs 6 minutes)
2. More reliable (no retry needed)
3. Higher output quality (9 vs 8)
4. Better user experience (8 vs 7)

### Recommendation

**For current use:** Stick with Version A
- It's faster, more reliable, and produces better output
- Simpler structure is easier to maintain

**For future consideration:** Version B advantages
- Error handling is robust and tested
- 72% token cost savings significant for large-scale usage
- Better documentation and structure
- Could be optimized to reduce timeout issues

---

## Next Steps

### Option 1: Continue Testing
Run Task 2 (Web Application Architecture) to gather more data points

### Option 2: Optimize Version B
- Adjust timeouts for research tasks
- Simplify initial task descriptions
- Test again

### Option 3: Hybrid Approach
- Keep Version A for speed-critical tasks
- Use Version B structure for documentation
- Apply Version B's error handling to Version A

---

## Files Generated

- `ab-test-version-a-results.md`
- `ab-test-version-b-results.md`
- `swarm-plan.md` (Version A)
- `swarm-plan-v2.md` (Version B)
- `swarm-results-compile.md` (Version A output)
- `swarm-results-compile-v2.md` (Version B output)

---

## Appendix: Web Application Architecture Design

**Task 2 Description:**
Design architecture for an online todo application

**Expected Output:**
- Frontend architecture (React/Vue/Angular)
- Backend API design
- Database schema
- Authentication strategy
- Deployment approach

**Swarm Structure:**
```
[Requirements] → [Frontend Design]
              → [Backend Design] → [Integration]
```

**Agents:**
1. **Requirements Agent** - Research todo app best practices
2. **Frontend Agent** - Design React/Vue architecture
3. **Backend Agent** - Design API and database
4. **Integration Agent** - Combine into complete architecture doc

**Evaluation Criteria:**
- Completeness of architecture
- Technology choice justification
- Scalability considerations
- Security best practices
- Clear documentation

---

*Report generated: 2026-03-20 11:10 AM*
