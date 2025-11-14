# NOVA Context Flow - Visual Diagrams

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    GraphEngine.execute_workflow()                    │
└─────────────────────────────────────────────────────────────────────┘
           │
           ├─► ContextManager (workflow-level state)
           │   └─ get_all(), update(), snapshot()
           │
           ├─► Node Execution Loop
           │   ├─ Node A (ActionNode)
           │   ├─ Node B (DecisionNode) 
           │   └─ Node C (ActionNode)
           │
           └─► Execution Trace + Chain of Work
               ├─ execution_trace (in-memory list)
               └─ ChainOfWork + ChainOfWorkStep (database)
```

---

## 1. Context Flow Between Nodes

### Workflow Execution with Context Progression

```
START
  │
  ├─► Node A (Extract)
  │   ├─ Input:  {"pdf_path": "/tmp/invoice.pdf", "user_id": 123}
  │   ├─ Code:   Parse PDF, extract invoice data
  │   └─ Output: {existing_keys} + {"amount": 1200, "vendor": "ACME"}
  │
  ├─► Node B (Validate)
  │   ├─ Input:  {"pdf_path": ..., "user_id": 123, "amount": 1200, "vendor": "ACME"}
  │   │          ↑ Includes output from Node A
  │   ├─ Code:   Validate amount > 0 AND vendor exists
  │   └─ Output: {existing_keys} + {"is_valid": true}
  │
  ├─► Node C (Decision: Amount > 1000?)
  │   ├─ Input:  {"pdf_path": ..., "user_id": 123, "amount": 1200, "vendor": "ACME", "is_valid": true}
  │   ├─ Code:   Set context['branch_decision'] = 'true' if amount > 1000
  │   └─ Output: {existing_keys} + {"branch_decision": "true"}
  │
  ├─ Decision: 'true' → Take path "high_value"
  │
  ├─► Node D (Manual Review - high value path)
  │   ├─ Input:  {all previous keys}
  │   └─ Output: {all previous keys} + {"reviewed_by": "manager_1"}
  │
  └─► END
```

### Context Update Mechanism (Detailed)

```
GraphEngine._execute_node(current_node, context, ...)
│
├─► 1. Snapshot input context
│   └─ input_context = context.snapshot()  [DEEP COPY]
│
├─► 2. Execute node
│   │
│   ├─ If E2BExecutor (hardcoded code):
│   │  └─ updated_context = await executor.execute(
│   │         code="context['amount'] = 1200",
│   │         context=context.get_all()
│   │     )
│   │     └─ Returns: {"amount": 1200}
│   │
│   └─ If CachedExecutor (AI-generated):
│      └─ updated_context = await executor.execute(
│             code="<prompt>",
│             context=context.get_all()
│         )
│         └─ Returns: {
│                "amount": 1200,
│                "_ai_metadata": {
│                    "model": "gpt-4o-mini",
│                    "generated_code": "...",
│                    "_steps": [...]
│                }
│            }
│
├─► 3. Extract AI metadata
│   └─ ai_metadata = updated_context.pop("_ai_metadata", None)
│      [Remove from context before updating ContextManager]
│
├─► 4. Update context
│   │
│   ├─ If "context_updates" in updated_context:
│   │  └─ context.update(updated_context["context_updates"])
│   │
│   └─ Else:
│      └─ context.update(updated_context)
│
├─► 5. For DecisionNode: Extract branch_decision
│   └─ decision_result = context.get("branch_decision")
│      if decision_result is None:
│          raise GraphExecutionError(...)
│
├─► 6. Snapshot output context
│   └─ output_result = context.snapshot()  [DEEP COPY]
│
└─► 7. Return metadata dict
    └─ {
        "node_id": "extract",
        "input_context": input_context,
        "output_result": output_result,
        "code_executed": "...",
        "ai_metadata": ai_metadata,
        "status": "success"
    }
```

---

## 2. Context Within a Node (Multi-Agent)

### ContextState: The Agent-Level Container

```
┌─────────────────────────────────────────────────────┐
│ CachedExecutor.execute()                            │
│ (Uses Multi-Agent Orchestrator)                     │
└─────────────────────────────────────────────────────┘
           │
           ├─► Initialize ContextState
           │   ├─ initial: {"pdf_path": "...", "user_id": 123}  [Immutable]
           │   ├─ current: {"pdf_path": "...", "user_id": 123}  [Mutable]
           │   └─ data_insights: None
           │
           ├─► Step 1: InputAnalyzer
           │   ├─ Input:  (task, context_state)
           │   ├─ Reads:  context_state.current
           │   ├─ Output: {needs_analysis: true, complexity: "medium"}
           │   └─ Mutates: ContextState? NO
           │
           ├─► Step 2: DataAnalyzer (if needs_analysis)
           │   ├─ Input:  context_state
           │   ├─ Reads:  context_state.current (e.g., PDF path)
           │   ├─ Output: {analysis_code: "...", num_pages: 5, ...}
           │   ├─ Updates: context_state.data_insights = {...}
           │   └─ Mutates: context_state.current? Maybe (code execution)
           │
           ├─► Step 3-6: Retry Loop (max 3 attempts)
           │   │
           │   ├─ 3. CodeGenerator
           │   │   ├─ Input:  (task, context_state, error_history, node_type)
           │   │   ├─ Uses:   context_state.current (as schema in prompt)
           │   │   │          context_state.data_insights (as hints)
           │   │   ├─ Output: {code: "...", tool_calls: [...], model: "gpt-4o"}
           │   │   └─ Mutates: NO
           │   │
           │   ├─ 4. CodeValidator
           │   │   ├─ Input:  (code, context_state.current)
           │   │   ├─ Validates: Code syntax + variable references
           │   │   ├─ Output: {valid: true, errors: []}
           │   │   └─ Mutates: NO
           │   │
           │   ├─ 5. E2BExecutor
           │   │   ├─ Input:  (code, context_state.current)
           │   │   ├─ Execution:
           │   │   │   1. Inject context as JSON
           │   │   │   2. Run code in E2B sandbox
           │   │   │   3. Parse output JSON
           │   │   │   4. Return only context_updates
           │   │   ├─ Output: {amount: 1200, vendor: "ACME"}
           │   │   ├─ Merge: context_state.current.update(output)
           │   │   └─ Mutates: YES ✓ (only agent that mutates)
           │   │
           │   └─ 6. OutputValidator
           │       ├─ Input:  (task, context_before, context_after, code)
           │       ├─ Validates: Task completed? Changes detected?
           │       ├─ Output: {valid: true, changes: ["amount", "vendor"]}
           │       └─ Mutates: NO
           │
           └─► Return result
               {
                   "amount": 1200,
                   "vendor": "ACME",
                   "_ai_metadata": {
                       "input_analysis": {...},
                       "data_analysis": {...},
                       "code_generation": {...},
                       "code_validation": {...},
                       "output_validation": {...},
                       "_steps": [...]
                   }
               }
```

### Critical: Only E2B Mutates Context

```
InputAnalyzer      DataAnalyzer       CodeGenerator      CodeValidator      E2BExecutor        OutputValidator
    │                 │                  │                  │                  │                   │
    ├─ Read only      ├─ Read/maybe      ├─ Read only      ├─ Read only      ├─ Read & WRITE     ├─ Read only
    │                 │  write           │                  │                  │                   │
    └─ No impact      └─ May update      └─ Generates      └─ Validates      └─ Updates          └─ Validates
       on context        data_insights       code           code            context ✓            results
```

---

## 3. AI Prompt Enforcement

### CodeGenerator Prompt for ActionNode

```
YOUR CODE:
├─ CAN read context via: context['key']
├─ CAN modify context via: context['key'] = value
├─ MUST print at end:
│  ┌──────────────────────────────────────┐
│  │ context_updates = {                  │
│  │     'new_key': new_value,            │
│  │     'another_key': another_value     │
│  │ }                                    │
│  │ print(json.dumps({                   │
│  │     "status": "success",             │
│  │     "context_updates": context_updates
│  │ }))                                  │
│  └──────────────────────────────────────┘
└─ MUST return ONLY updates, not full context
   (preserves existing data)
```

### CodeGenerator Prompt for DecisionNode

```
YOUR CODE:
├─ CAN read context via: context['key']
├─ MUST evaluate condition
├─ MUST set context['branch_decision'] with:
│  ├─ 'true' / 'false'
│  ├─ 'yes' / 'no'
│  ├─ 'approved' / 'rejected'
│  └─ Or any value matching workflow edges
└─ MUST print:
   ┌──────────────────────────────────────┐
   │ context_updates = {                  │
   │     'branch_decision': context['branch_decision']
   │ }                                    │
   │ print(json.dumps({                   │
   │     "status": "success",             │
   │     "context_updates": context_updates
   │ }))                                  │
   └──────────────────────────────────────┘
```

### Output Parsing: What E2BExecutor Expects

```
E2B Sandbox Output (stdout):
│
└─ Last valid JSON line should be:
   {
       "status": "success|error",
       "context_updates": {
           "key1": "value1",
           "key2": value2
       },
       "message": "optional message"
   }

E2BExecutor.execute_sync():
├─ 1. Get stdout from E2B
├─ 2. Split into lines
├─ 3. Filter empty JSON ([], {}, null)
├─ 4. Parse last valid line
├─ 5. Check for "context_updates" key
│  ├─ If present:
│  │  └─ Extract ONLY context_updates dict
│  │     └─ Return: {"key1": "value1", "key2": value2}
│  │
│  └─ If not present (legacy):
│     └─ Return full JSON as context
│
└─ Orchestrator.execute():
   └─ context_state.current.update(returned_dict)
```

---

## 4. Chain of Work Storage

### Persistence Hierarchy

```
Execution (database)
└─ ChainOfWork entries (one per node)
   │
   ├─ node_id: "extract"
   ├─ node_type: "action"
   ├─ code_executed: "import fitz\n..."
   ├─ input_context: SNAPSHOT {pdf_path: ..., user_id: 123}
   ├─ output_result: SNAPSHOT {pdf_path: ..., user_id: 123, amount: 1200, vendor: "ACME"}
   ├─ execution_time: 2.34
   ├─ status: "success"
   ├─ ai_metadata: {
   │  ├─ input_analysis: {...}
   │  ├─ data_analysis: {...}
   │  ├─ code_generation: {...}
   │  ├─ attempts: 1
   │  ├─ errors: []
   │  ├─ total_time_ms: 5234
   │  └─ _steps: [...]  ← Extracted to ChainOfWorkStep
   │ }
   │
   └─ ChainOfWorkStep entries (one per agent)
      │
      ├─ Step 1: InputAnalyzer
      │  ├─ step_number: 1
      │  ├─ agent_name: "InputAnalyzer"
      │  ├─ input_data: {task: "...", context_keys: [...]}
      │  ├─ output_data: {needs_analysis: true, ...}
      │  ├─ status: "success"
      │  ├─ execution_time_ms: 250
      │  └─ model_used: "gpt-4o-mini"
      │
      ├─ Step 2: DataAnalyzer
      │  ├─ step_number: 2
      │  ├─ agent_name: "DataAnalyzer"
      │  ├─ generated_code: "import fitz\n..."
      │  ├─ input_data: {context_keys, hint}
      │  ├─ output_data: {num_pages: 5, ...}
      │  └─ status: "success"
      │
      ├─ Step 3: CodeGenerator (attempt 1)
      │  ├─ step_number: 3
      │  ├─ attempt_number: 1
      │  ├─ agent_name: "CodeGenerator"
      │  ├─ generated_code: "import fitz\n..."
      │  ├─ status: "success"
      │  ├─ execution_time_ms: 1800
      │  ├─ model_used: "gpt-4o"
      │  ├─ tokens_input: 7000
      │  ├─ tokens_output: 450
      │  └─ cost_usd: 0.003
      │
      ├─ Step 4: CodeValidator (attempt 1)
      │  ├─ step_number: 4
      │  ├─ agent_name: "CodeValidator"
      │  ├─ status: "success"
      │  └─ execution_time_ms: 15
      │
      ├─ Step 5: E2BExecutor (attempt 1)
      │  ├─ step_number: 5
      │  ├─ agent_name: "E2BExecutor"
      │  ├─ sandbox_id: "sbx_abc123xyz"
      │  ├─ status: "failed"  ← FAILED!
      │  └─ error_message: "FileNotFoundError: ..."
      │
      ├─ Step 6: CodeGenerator (attempt 2)
      │  ├─ step_number: 3
      │  ├─ attempt_number: 2
      │  ├─ agent_name: "CodeGenerator"
      │  ├─ input_data: {..., error_history: [{error: "..."}]}
      │  ├─ generated_code: "import fitz; fitz.open(...)"
      │  └─ status: "success"
      │
      ├─ Step 7: CodeValidator (attempt 2)
      │  ├─ step_number: 4
      │  ├─ attempt_number: 2
      │  ├─ status: "success"
      │  └─ execution_time_ms: 15
      │
      ├─ Step 8: E2BExecutor (attempt 2)
      │  ├─ step_number: 5
      │  ├─ attempt_number: 2
      │  ├─ sandbox_id: "sbx_xyz789abc"
      │  ├─ status: "success" ✓
      │  └─ execution_time_ms: 1200
      │
      └─ Step 9: OutputValidator (attempt 2)
         ├─ step_number: 6
         ├─ agent_name: "OutputValidator"
         ├─ input_data: {task: "...", context_before: {...}, context_after: {...}}
         ├─ output_data: {valid: true, changes: ["amount", "vendor"]}
         ├─ status: "success"
         └─ execution_time_ms: 400
```

### Snapshot Safety

```
Before execution:
input_context = context.snapshot()  # DEEP COPY
{
    "pdf_path": "/tmp/invoice.pdf",
    "user_id": 123,
    "existing_list": [1, 2, 3]
}

During execution:
context.update({"new_key": "value"})
context.update({"existing_list": [1, 2, 3, 4, 5]})

After execution:
output_result = context.snapshot()  # DEEP COPY
{
    "pdf_path": "/tmp/invoice.pdf",
    "user_id": 123,
    "existing_list": [1, 2, 3, 4, 5],
    "new_key": "value"
}

Later mutation (should NOT affect stored snapshots):
context.update({"pdf_path": "/tmp/different.pdf"})

Stored in DB:
input_context = {
    "pdf_path": "/tmp/invoice.pdf",  ← NOT affected by later mutation
    "user_id": 123,
    "existing_list": [1, 2, 3]
}

output_result = {
    "pdf_path": "/tmp/invoice.pdf",  ← NOT affected by later mutation
    "user_id": 123,
    "existing_list": [1, 2, 3, 4, 5],
    "new_key": "value"
}
```

---

## 5. Decision Node Context Flow

### DecisionNode Execution

```
GraphEngine._execute_node(decision_node, context, ...)
│
├─► 1. Execute decision code
│   └─ Code sets: context['branch_decision'] = 'true'|'false'|...
│
├─► 2. Extract decision for branching
│   └─ decision_result = context.get("branch_decision")
│      if decision_result is None:
│          raise GraphExecutionError("DecisionNode didn't set branch_decision")
│
├─► 3. Find next edge
│   │
│   └─ edges = [
│        {"from": "validate", "to": "manual_review", "condition": "true"},
│        {"from": "validate", "to": "auto_approve", "condition": "false"}
│      ]
│
│     for edge in edges:
│        if edge.condition == decision_str:
│            next_node_id = edge.to
│            break
│
└─► 4. Continue execution
    └─ GraphEngine moves to next_node_id
```

### Important: branch_decision Context Key

```
Problem if NOT managed properly:
────────────────────────────────

Execution:
└─ Node A (ActionNode):
   └─ Sets context['branch_decision'] = 'true'  ← WRONG! This is action, not decision

└─ Node B (DecisionNode):
   └─ Reads context['branch_decision'] = 'true'  ← Would use stale value from Node A!
   └─ Wrong path taken!

Current safeguard:
──────────────────

Prompt tells CodeGenerator:
"SOLO imprime las keys que MODIFICASTE"

But there's NO explicit clearing of branch_decision before DecisionNode.

Recommendation:
───────────────

Before executing each DecisionNode:
context.delete('branch_decision')

This ensures DecisionNode MUST set it fresh.
```

---

## 6. The Three Streams of Data

```
WORKFLOW EXECUTION
│
├─ STREAM 1: Context Flow (In-Memory, Mutable)
│  │
│  ├─ Node A
│  │  ├─ Input:  ContextManager{...}
│  │  └─ Output: ContextManager{... + updates}
│  │
│  ├─ Node B
│  │  ├─ Input:  ContextManager{... + updates from A}
│  │  └─ Output: ContextManager{... + new updates}
│  │
│  └─ Node C
│     ├─ Input:  ContextManager{... + all previous updates}
│     └─ Output: ContextManager{... + final updates}
│
├─ STREAM 2: Execution Trace (In-Memory, Immutable After Node)
│  │
│  ├─ Node A:
│  │  ├─ input_context: snapshot at start
│  │  ├─ output_result: snapshot at end
│  │  ├─ code_executed: "..."
│  │  ├─ status: "success"|"failed"
│  │  ├─ ai_metadata: {...}
│  │  └─ _steps: [agent executions]
│  │
│  ├─ Node B:
│  │  └─ {...same structure...}
│  │
│  └─ Node C:
│     └─ {...same structure...}
│
└─ STREAM 3: Database Persistence (Permanent, Read-Only)
   │
   ├─ ChainOfWork (Node-level)
   │  ├─ execution_id
   │  ├─ node_id
   │  ├─ input_context (JSON snapshot)
   │  ├─ output_result (JSON snapshot)
   │  ├─ code_executed
   │  ├─ ai_metadata
   │  └─ status
   │
   └─ ChainOfWorkStep (Agent-level)
      ├─ agent_name
      ├─ step_number
      ├─ attempt_number
      ├─ input_data
      ├─ output_data
      ├─ generated_code
      ├─ status
      └─ execution_time_ms
```

---

## Summary: Context Is Immutable After Node

```
Important Pattern:
──────────────────

1. During Node Execution:
   context = ContextManager (MUTABLE)
   ├─ ContextState (agent-level, MUTABLE during orchestration)
   └─ All agents READ context
      But ONLY E2B WRITES context

2. Node Finishes:
   ├─ Snapshot input_context = deep copy
   ├─ Snapshot output_result = deep copy
   └─ These snapshots are IMMUTABLE forever

3. Store to Database:
   ChainOfWork {
       input_context: immutable snapshot,
       output_result: immutable snapshot,
       ai_metadata: {...},
       code_executed: "...",
       status: "success"|"failed"
   }

4. Next Node Starts:
   ├─ Reads context (next iteration)
   ├─ CANNOT affect stored snapshots
   └─ Chain of Work provides audit trail

This prevents:
- Historical data corruption
- Audit trail tampering
- Debugging confusion (snapshots are accurate)
```

