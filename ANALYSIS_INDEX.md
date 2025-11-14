# NOVA Context Management Analysis - Complete Index

## Overview

This analysis provides a comprehensive examination of how context is managed between agents in the NOVA workflow engine. Three detailed documents provide different perspectives:

1. **CONTEXT_MANAGEMENT_SUMMARY.md** - START HERE
   - Executive summary with key findings
   - Issues identified and recommendations
   - Best suited for: Quick overview, decision-makers

2. **CONTEXT_MANAGEMENT_ANALYSIS.md** - DETAILED REFERENCE
   - Complete technical analysis with code references
   - 1,026 lines of detailed documentation
   - Covers all flow mechanisms and database storage
   - Best suited for: Developers, implementation, debugging

3. **CONTEXT_FLOW_DIAGRAMS.md** - VISUAL GUIDE
   - ASCII diagrams and flowcharts
   - Visual representations of all layers
   - State transitions and data flows
   - Best suited for: Understanding architecture, training

---

## Quick Navigation

### If you want to understand...

**How context flows between nodes:**
→ Read: `CONTEXT_MANAGEMENT_SUMMARY.md` Section 2
→ Diagrams: `CONTEXT_FLOW_DIAGRAMS.md` Section 1
→ Code: `CONTEXT_MANAGEMENT_ANALYSIS.md` Section 1

**How agents communicate within a node:**
→ Read: `CONTEXT_MANAGEMENT_SUMMARY.md` Section 3
→ Diagrams: `CONTEXT_FLOW_DIAGRAMS.md` Section 2
→ Code: `CONTEXT_MANAGEMENT_ANALYSIS.md` Section 2

**How AI is prompted to update context:**
→ Read: `CONTEXT_MANAGEMENT_SUMMARY.md` Section 4
→ Diagrams: `CONTEXT_FLOW_DIAGRAMS.md` Section 3
→ Code: `CONTEXT_MANAGEMENT_ANALYSIS.md` Section 3

**What gets stored in the database:**
→ Read: `CONTEXT_MANAGEMENT_SUMMARY.md` Section 5
→ Diagrams: `CONTEXT_FLOW_DIAGRAMS.md` Section 4
→ Code: `CONTEXT_MANAGEMENT_ANALYSIS.md` Section 4

**The relationship between context and tracing:**
→ Read: `CONTEXT_MANAGEMENT_SUMMARY.md` Section 6
→ Diagrams: `CONTEXT_FLOW_DIAGRAMS.md` Section 6
→ Code: `CONTEXT_MANAGEMENT_ANALYSIS.md` Section 5

**Issues and risks:**
→ Read: `CONTEXT_MANAGEMENT_SUMMARY.md` - Issues Identified
→ Detailed: `CONTEXT_MANAGEMENT_ANALYSIS.md` Section 6

**Recommendations for improvement:**
→ Read: `CONTEXT_MANAGEMENT_SUMMARY.md` - Recommendations

---

## Key Concepts at a Glance

### Three Layers of Context Management

| Layer | Component | Scope | Mutability | Persistence |
|-------|-----------|-------|-----------|-------------|
| **Workflow** | ContextManager | All nodes | Mutable | In-memory only |
| **Node** | ContextState | One node | Mutable (current only) | In-memory only |
| **Database** | ChainOfWork* | Permanent | Immutable | PostgreSQL |

*ChainOfWork and ChainOfWorkStep tables

### Context Flow Pattern

```
GraphEngine
├─ context = ContextManager()
└─ for each node:
   ├─ input_snapshot = context.snapshot()
   ├─ Executor.execute(context.get_all())
   ├─ context.update(result)
   └─ output_snapshot = context.snapshot()
   └─ Save to ChainOfWork
```

### AI Enforcement Mechanisms

```
1. CodeGenerator Prompt
   ├─ Explicit instructions for output format
   ├─ Examples of correct code
   └─ Warnings about what NOT to do

2. Output Format Validation
   ├─ Parse JSON structure
   ├─ Check for "context_updates" key
   └─ Error if format wrong

3. Retry with Feedback
   ├─ Up to 3 attempts
   ├─ Pass previous errors to CodeGenerator
   └─ CodeGenerator adjusts code

4. Post-Execution Check
   ├─ For DecisionNode: verify branch_decision set
   ├─ For ActionNode: verify context updated
   └─ Fail gracefully if validation fails
```

### Issues Summary

| Issue | Risk | Status | Fix |
|-------|------|--------|-----|
| Context merge ambiguity | Low | Handled | Prompt enforces format |
| branch_decision staleness | Medium | Design limitation | Clear before DecisionNode |
| Snapshot size explosion | Low | Monitored | Context summarization |
| Error metadata loss | None | Already handled | Error object preservation |

---

## Code Locations Quick Reference

### Core Engine
- **GraphEngine**: `/nova/src/core/engine.py` (lines 47-791)
  - `execute_workflow()` - Main entry point
  - `_execute_node()` - Node execution with snapshotting
  - `_find_next_node()` - Decision branching logic

### Context Management
- **ContextManager**: `/nova/src/core/context.py` (lines 15-225)
  - `update()` - Merge context from executor
  - `snapshot()` - Deep copy for audit trail
  - `get_all()` - Get current state

- **ContextState**: `/nova/src/core/agents/state.py` (lines 72-102)
  - `initial` - Original context (immutable)
  - `current` - Mutable during agent execution
  - `data_insights` - Insights from DataAnalyzer

### Multi-Agent Orchestration
- **MultiAgentOrchestrator**: `/nova/src/core/agents/orchestrator.py` (lines 32-481)
  - `execute_workflow()` - Coordinates all agents
  - `_create_step_record()` - Records agent execution
  - Agent execution loop with retries

- **CodeGenerator**: `/nova/src/core/agents/code_generator.py` (lines 24-368)
  - `_build_prompt()` - Constructs AI prompt
  - Context schema + data_insights injection
  - Node-type-specific instructions

### Executors
- **E2BExecutor**: `/nova/src/core/executors.py` (lines 278-660)
  - `_inject_context()` - Serialize context into code
  - `_execute_sync()` - Run in E2B sandbox
  - Output parsing and validation

- **CachedExecutor**: `/nova/src/core/executors.py` (lines 71-258)
  - Wrapper around MultiAgentOrchestrator
  - Returns context + AI metadata

### Database Models
- **ChainOfWork**: `/nova/src/models/chain_of_work.py` (lines 12-86)
  - Node-level audit trail
  - input_context, output_result snapshots
  - ai_metadata storage

- **ChainOfWorkStep**: `/nova/src/models/chain_of_work_step.py` (lines 29-421)
  - Agent-level granular trace
  - Step-by-step execution details
  - Retry attempt tracking

---

## Testing Scenarios

### To verify context flows correctly:

1. **Single node test**
   - Create workflow: Start → ActionNode → End
   - ActionNode updates context
   - Verify: input_context vs output_result in ChainOfWork

2. **Multi-node test**
   - Create: Start → Node A → Node B → Node C → End
   - Each node reads previous outputs
   - Verify: Context accumulates properly

3. **Decision branching test**
   - Create: Start → ActionNode → DecisionNode → [Yes/No] → End
   - DecisionNode sets branch_decision
   - Verify: Correct path taken

4. **AI enforcement test**
   - Use CachedExecutor with intentional errors
   - Verify: Retry mechanism works
   - Verify: Error feedback passed to CodeGenerator

5. **Snapshot safety test**
   - Store snapshots, then mutate context
   - Verify: Stored snapshots unchanged
   - Database accuracy maintained

---

## Performance Considerations

### Context Size Impact
- Each snapshot is a deep copy
- Multiple snapshots per node
- Large files (PDF base64) can bloat database
- **Mitigation**: Context summarization for agent steps

### Executor Performance
- E2B sandbox creation: ~500ms
- Code execution: varies by complexity
- Typical node: 2-5 seconds total
- **Optimization**: Template caching, parallel execution

### Database Growth
- ChainOfWork: 1 row per node execution
- ChainOfWorkStep: 6-14 rows per node
- Context snapshots: JSON-serialized
- **Management**: Archive old executions, summarization

---

## Maintenance & Operations

### Monitoring Checklist
- [ ] ChainOfWorkStep._steps extracted cleanly (no duplication)
- [ ] Context snapshots complete and serializable
- [ ] Decision nodes setting branch_decision correctly
- [ ] Error metadata captured for failed nodes
- [ ] Database size growing at expected rate

### Debugging Guide

**Issue: Context not updating between nodes**
1. Check: Did executor return updated_context?
2. Check: context.update() called?
3. Check: AI returning correct format? → Look at stdout from E2B
4. Check: ChainOfWork output_result shows expected values

**Issue: Decision node taking wrong path**
1. Check: branch_decision value in context
2. Check: Edge conditions match decision value
3. Check: DecisionNode code executed (in ChainOfWorkStep)
4. Check: Is branch_decision stale from previous node?

**Issue: Large database growth**
1. Check: Context summarization enabled?
2. Check: Steps properly extracted (not storing full data)?
3. Check: Old executions being archived?
4. Solution: Run with summarization enabled

---

## Future Enhancements

### Potential improvements (not yet implemented)
1. Context compression for large files
2. Lazy snapshot loading (don't store intermediate states)
3. Context versioning (track which agent modified which keys)
4. Selective context passing (node only gets relevant keys)
5. Context encryption (sensitive data in database)

---

## Document Statistics

| Document | Lines | Sections | Purpose |
|----------|-------|----------|---------|
| CONTEXT_MANAGEMENT_SUMMARY.md | ~300 | 8 | Executive overview |
| CONTEXT_MANAGEMENT_ANALYSIS.md | 1,026 | 8 | Complete technical reference |
| CONTEXT_FLOW_DIAGRAMS.md | ~500 | 6 | Visual explanations |
| ANALYSIS_INDEX.md | This file | Navigation | Quick lookup |

---

## How to Use This Analysis

### For new developers:
1. Start: CONTEXT_MANAGEMENT_SUMMARY.md (Sections 1-3)
2. Visualize: CONTEXT_FLOW_DIAGRAMS.md (Sections 1-3)
3. Deep dive: CONTEXT_MANAGEMENT_ANALYSIS.md as needed
4. Implement: Use code references to understand implementation

### For debugging:
1. Quick reference: ANALYSIS_INDEX.md (this file)
2. Find location: Look up in "Code Locations Quick Reference"
3. Understand flow: Refer to CONTEXT_FLOW_DIAGRAMS.md
4. Detailed analysis: CONTEXT_MANAGEMENT_ANALYSIS.md for specifics

### For design decisions:
1. Read: CONTEXT_MANAGEMENT_SUMMARY.md "Recommendations"
2. Evaluate: vs. "Issues Identified"
3. Verify: Code patterns in CONTEXT_MANAGEMENT_ANALYSIS.md

### For presentation/training:
1. Use CONTEXT_FLOW_DIAGRAMS.md for visuals
2. Reference CONTEXT_MANAGEMENT_SUMMARY.md for talking points
3. Have ANALYSIS_INDEX.md for quick questions
4. CONTEXT_MANAGEMENT_ANALYSIS.md for detailed Q&A

---

## Feedback & Updates

This analysis is based on codebase state as of November 15, 2025.

If the implementation changes:
- Update the code location references
- Verify AI prompt instructions still enforce context updates
- Check snapshot safety pattern still in use
- Validate ChainOfWork persistence still working

---

Generated: November 15, 2025
Analyzed by: Claude Code
Total files examined: 9
Total lines analyzed: 4,000+

