# NOVA Context Management Analysis
## Complete Flow Between Agents and Nodes

---

## EXECUTIVE SUMMARY

The NOVA workflow engine uses a **sophisticated context management system** with multiple layers:

1. **ContextManager** - Simple key-value store for workflow-level context
2. **ContextState** - Tracks context changes within a single node execution
3. **ExecutionState** - Metadata about agent execution (not context, but tracks it)
4. **Chain of Work** - Audit trail storing snapshots of context at each step

**Critical insight**: Context flows through THREE separate mechanisms:
- **Between nodes**: Via `ContextManager` (workflow-level)
- **Within a node**: Via `ContextState` (agent-level)
- **For audit**: Via `Chain of Work snapshots` (database-level)

---

## 1. CONTEXT FLOW BETWEEN NODES

### 1.1 Node Execution Loop (GraphEngine)

```
Start Node
    ↓
Execute Node A (ActionNode)
    - GraphEngine._execute_node() called
    - Executor.execute() called with context.get_all()
    - Context updated with executor results
    ↓
Find Next Node (based on context state)
    ↓
Execute Node B (DecisionNode)
    - Reads context to make decision
    - Sets context['branch_decision']
    - GraphEngine finds next node based on decision
    ↓
Execute Node C (ActionNode)
    - Reads updated context from previous nodes
    ...
```

**Location**: `/nova/src/core/engine.py` lines 457-791

### 1.2 Context Passing Mechanism

```python
# In GraphEngine.execute_workflow()
context = ContextManager(initial_context or {})  # Line 518

while current_node_id is not None:
    metadata = await self._execute_node(
        current_node,
        context,  # ← Passed as reference
        workflow_definition,
        execution.id if execution else None
    )
    
    # Context is mutated by _execute_node via executor.execute()
```

**Key point**: `ContextManager` is passed by reference, so mutations in one node are visible to the next.

### 1.3 Context Update in _execute_node()

For **ActionNode** (lines 267-345):

```python
# E2BExecutor returns updated_context
updated_context = await executor.execute(
    code=code_or_prompt,
    context=context.get_all(),  # Current state injected
    timeout=node.timeout,
    ...
)

# Extract AI metadata (only for CachedExecutor)
ai_metadata = updated_context.pop("_ai_metadata", None)

# Handle both formats:
if "context_updates" in updated_context:
    # AI-generated code format: {status, context_updates, message}
    actual_updates = updated_context.get("context_updates", {})
    context.update(actual_updates)  # ← Merge into ContextManager
else:
    # Traditional format: direct context update
    context.update(updated_context)
```

For **DecisionNode** (lines 347-429):

```python
# Same as ActionNode, but also extracts decision
updated_context = await executor.execute(...)
ai_metadata = updated_context.pop("_ai_metadata", None)

if "context_updates" in updated_context:
    context.update(updated_context.get("context_updates", {}))
else:
    context.update(updated_context)

# CRITICAL: Extract decision for branching
decision_result = context.get("branch_decision")
if decision_result is None:
    raise GraphExecutionError(f"DecisionNode {node_id} did not set 'branch_decision'")

metadata["decision_result"] = decision_str  # Converted to "true"/"false"
```

### 1.4 Context Snapshots for Chain of Work

```python
# Before execution
input_context = context.snapshot()  # Deep copy (line 243)

# After execution
metadata["output_result"] = context.snapshot()  # Deep copy (line 451)

# When persisting to DB
chain_entry = ChainOfWork(
    execution_id=execution.id,
    input_context=metadata['input_context'],      # Immutable snapshot
    output_result=metadata['output_result'],       # Immutable snapshot
    ...
)
```

**Crucial**: `snapshot()` creates a deep copy to prevent future mutations from affecting stored history.

---

## 2. CONTEXT WITHIN A NODE (Multi-Agent System)

### 2.1 ContextState - The Agent-Level Context

**Location**: `/nova/src/core/agents/state.py` lines 72-102

```python
@dataclass
class ContextState:
    """
    Datos que fluyen entre nodos del workflow.
    
    Pasa de nodo en nodo:
    - El siguiente nodo recibe `current`
    - `initial` se mantiene inmutable para comparación
    - `data_insights` del DataAnalyzer para uso del CodeGenerator
    """
    
    initial: Dict           # Original context (immutable)
    current: Dict           # Current context (mutable during node execution)
    data_insights: Optional[Dict] = None  # From DataAnalyzer for CodeGenerator
```

### 2.2 Agents Access Context via ContextState

**InputAnalyzer**:
```python
# Only reads context, doesn't modify
context_summary = self._summarize_context(context_state.current)
```

**DataAnalyzer**:
```python
# Generates Python code to analyze context
# Executes in E2B and returns analysis_code + results
data_analysis = await self.data_analyzer.execute(context_state)
# Updates: context_state.data_insights = data_analysis.data
```

**CodeGenerator**:
```python
# Uses FULL context as prompt input
prompt = self._build_prompt(
    task,
    context_state.current,          # Full context dict
    context_state.data_insights,    # Hints from DataAnalyzer
    error_history or [],
    node_type=node_type
)
# Returns: generated_code (not context update)
```

**CodeValidator**:
```python
# Validates code syntax against context keys
code_val = await self.code_validator.execute(
    code=code_gen.data["code"],
    context=context_state.current  # Used to validate variable references
)
```

**E2BExecutor** (within orchestrator):
```python
# Executes code, returns context_updates
updated_context = await self.e2b.execute_code(
    code=code_gen.data["code"],
    context=context_state.current,
    timeout=timeout
)
# MERGE: context_state.current.update(updated_context)
context_state.current.update(updated_context)
```

**OutputValidator**:
```python
# Validates results against original task
output_val = await self.output_validator.execute(
    task=task,
    context_before=context_state.initial,   # What we started with
    context_after=context_state.current,    # What we ended with
    generated_code=code_gen.data["code"]
)
```

### 2.3 Context Flow in Orchestrator.execute_workflow()

**Location**: `/nova/src/core/agents/orchestrator.py` lines 160-480

```python
# Initialize ContextState (lines 184-187)
context_state = ContextState(
    initial=context.copy(),        # Immutable original
    current=context.copy()         # Will be mutated
)

# Step 2: InputAnalyzer (doesn't modify context)
input_analysis = await self.input_analyzer.execute(task, context_state)

# Step 3: DataAnalyzer (if needed)
if input_analysis.data["needs_analysis"]:
    data_analysis = await self.data_analyzer.execute(context_state)
    context_state.data_insights = data_analysis.data
    # ← context_state.current may be updated by DataAnalyzer

# Step 4: CodeGenerator (reads context, generates code)
code_gen = await self.code_generator.execute(
    task=task,
    context_state=context_state,
    error_history=execution_state.errors,
    node_type=node_type
)

# Step 5: CodeValidator (validates against context)
code_val = await self.code_validator.execute(
    code=code_gen.data["code"],
    context=context_state.current
)

# Step 6: E2B Execution (UPDATES context)
updated_context = await self.e2b.execute_code(
    code=code_gen.data["code"],
    context=context_state.current,
    timeout=timeout
)
context_state.current.update(updated_context)  # ← MERGE!

# Step 7: OutputValidator (validates changes)
output_val = await self.output_validator.execute(
    task=task,
    context_before=context_state.initial,
    context_after=context_state.current,
    generated_code=code_gen.data["code"]
)

# Return with BOTH context and metadata
result = {
    **context_state.current,           # Actual updated context
    "_ai_metadata": {
        **execution_state.to_dict(),
        "_steps": steps_to_persist     # Granular audit trail
    }
}
```

**Critical flow**:
1. `initial` stays frozen throughout
2. `current` is updated only by E2B execution (the actual code)
3. All agents can READ context, only E2B can WRITE it
4. OutputValidator sees BEFORE/AFTER to validate

---

## 3. HOW AI IS PROMPTED TO UPDATE CONTEXT

### 3.1 CodeGenerator Prompt Instructions

**Location**: `/nova/src/core/agents/code_generator.py` lines 220-368

#### For ActionNode (lines 321-345):

```python
prompt += """
**IMPORTANTE - EL CÓDIGO DEBE IMPRIMIR OUTPUT:**
Tu código DEBE terminar imprimiendo SOLO los cambios realizados al contexto.
Al final del código, SIEMPRE incluye:

```python
# Al final de tu código, crea un dict con SOLO las keys que modificaste
context_updates = {
    'new_key': new_value,
    'another_key': another_value
    # Solo incluye las keys que agregaste o modificaste
}

# Imprime en formato estructurado (sin indent para evitar problemas de parsing)
print(json.dumps({
    "status": "success",
    "context_updates": context_updates
}, ensure_ascii=False))
```

⚠️ **CRÍTICO:**
- SIN este print final, el código se considerará INVÁLIDO
- SOLO imprime las keys que MODIFICASTE, NO todo el contexto
- Esto preserva datos existentes que no cambiaron (ej: archivos PDF en base64)
"""
```

#### For DecisionNode (lines 279-318):

```python
prompt += """
**🔀 IMPORTANTE - ESTE ES UN NODO DE DECISIÓN (DecisionNode):**

Los DecisionNodes evalúan una condición y deciden qué rama del workflow seguir.
Tu código DEBE:

1. **Evaluar la condición** descrita en la tarea
2. **Establecer `context['branch_decision']`** con el valor de la rama a seguir
3. El valor de `branch_decision` debe ser un string que coincida con las condiciones definidas en el workflow

**Ejemplo de código para DecisionNode:**

```python
# Evaluar la condición (ejemplo: verificar si hay PDF adjunto)
has_pdf = len(context.get('email_attachments', [])) > 0

# REQUERIDO: Establecer branch_decision con 'true' o 'false'
if has_pdf:
    context['branch_decision'] = 'true'
else:
    context['branch_decision'] = 'false'

# IMPORTANTE: Imprimir SOLO los cambios realizados, no todo el contexto
# Esto evita sobrescribir datos existentes que no cambiaron
context_updates = {
    'branch_decision': context['branch_decision']
    # Solo incluye las keys que modificaste
}
print(json.dumps({
    "status": "success",
    "context_updates": context_updates
}, ensure_ascii=False))
```

⚠️ **CRÍTICO:**
- El código DEBE establecer `context['branch_decision']` o fallará
- Los valores típicos son: 'true', 'false', 'yes', 'no', 'approved', 'rejected', etc.
- ⚠️ SOLO imprime las keys que MODIFICASTE, NO todo el contexto
"""
```

### 3.2 Context Injection in E2BExecutor

**Location**: `/nova/src/core/executors.py` lines 328-381

```python
def _inject_context(self, code: str, context: Dict[str, Any]) -> str:
    """
    Inject context into code so it can access workflow data.
    
    CRITICAL: Use ensure_ascii=True for BOTH injection and output
    This prevents UnicodeEncodeError in E2B sandbox when context contains
    special characters like \xa0 (non-breaking space), accented characters, etc.
    """
    context_json = json.dumps(context, ensure_ascii=True)
    escaped_json = context_json.replace('\\', '\\\\').replace("'", "\\'")
    
    # Check if code already has a print statement
    # AI-generated code (from CachedExecutor) already includes print(json.dumps(...))
    # So we should NOT add another print statement
    has_print = 'print(' in code and 'json.dumps' in code
    
    if has_print:
        # Code already prints output - just inject context
        full_code = f"""import json

# Injected context (workflow state)
context = json.loads('{escaped_json}')

# User code (already includes output print)
{code}
"""
    else:
        # Code doesn't print - add print statement for legacy code
        full_code = f"""import json

# Injected context (workflow state)
context = json.loads('{escaped_json}')

# User code
{code}

# Output updated context
print(json.dumps(context, ensure_ascii=True))
"""
    
    return full_code
```

**Flow**:
1. Serialize context to JSON with `ensure_ascii=True`
2. Escape quotes/backslashes to embed in Python string
3. Inject as: `context = json.loads('{escaped_json}')`
4. AI-generated code then modifies `context` dict
5. AI-generated code prints: `json.dumps({"status": "success", "context_updates": {...}})`

### 3.3 Output Parsing in E2BExecutor

**Location**: `/nova/src/core/executors.py` lines 556-609

```python
# Get output from E2B sandbox
stdout_output = execution.stdout or ""
stdout_lines = [line.strip() for line in stdout_output.split('\n') if line.strip()]

# Filter out empty JSON objects
valid_lines = []
for line in stdout_lines:
    if line.strip() in ['{}', '[]', 'null']:
        continue
    valid_lines.append(line)

# The last VALID line should be our JSON output
output = valid_lines[-1]

# Parse updated context
output_json = json.loads(output)

# Check if output has the expected structure: {status, context_updates, message}
# If it does, extract context_updates. Otherwise, use the whole JSON as context.
if isinstance(output_json, dict) and "context_updates" in output_json:
    # AI-generated code format: {status, context_updates, message}
    status = output_json.get("status")
    message = output_json.get("message")
    
    # If status is "error", treat it as a code execution error
    if status == "error":
        logger.warning(f"Code reported error status: {message}")
        raise CodeExecutionError(...)
    
    # Extract context updates and MERGE with original context
    # CRITICAL: Only return the updates, NOT the full merged context
    # The orchestrator will handle merging in context_state.current
    context_updates = output_json.get("context_updates", {})
    updated_context = context_updates  # ← Only return updates!
else:
    # Legacy format or direct context update
    updated_context = output_json

return updated_context
```

**Key insight**: E2BExecutor returns ONLY the updates, not the full merged context. Merging happens in the orchestrator:

```python
# orchestrator.py line 338
context_state.current.update(updated_context)
```

---

## 4. WHAT GETS STORED IN CHAIN OF WORK

### 4.1 ChainOfWork Table (Node-Level)

**Location**: `/nova/src/models/chain_of_work.py`

Each row = one node execution

```python
class ChainOfWork:
    # Node identification
    node_id: str              # "extract_data", "validate_invoice", etc.
    node_type: str            # "action", "decision", "start", "end"
    
    # Code and execution
    code_executed: str        # The actual code (AI-generated or hardcoded)
    
    # Context snapshots
    input_context: JSON       # Snapshot BEFORE execution
    output_result: JSON       # Snapshot AFTER execution
    
    # Execution metrics
    execution_time: float     # seconds
    status: str               # "success" or "failed"
    error_message: str        # If failed
    
    # Decision-specific
    decision_result: str      # "true" or "false" for DecisionNode
    path_taken: str           # Next node ID taken after decision
    
    # AI metadata (for CachedExecutor nodes)
    ai_metadata: JSON         # {
                              #   "input_analysis": {...},
                              #   "data_analysis": {...},
                              #   "code_generation": {...},
                              #   "code_validation": {...},
                              #   "output_validation": {...},
                              #   "attempts": 1-3,
                              #   "errors": [...],
                              #   "timings": {...},
                              #   "total_time_ms": 5234
                              # }
```

### 4.2 ChainOfWorkStep Table (Agent-Level)

**Location**: `/nova/src/models/chain_of_work_step.py`

Each row = one agent execution within a node

Example for 1 node with 2 retries:
```
Step 1: InputAnalyzer (attempt 1)
Step 2: DataAnalyzer (attempt 1) - optional
Step 3: CodeGenerator (attempt 1)
Step 4: CodeValidator (attempt 1)
Step 5: E2BExecutor (attempt 1) - FAILED
Step 6: CodeGenerator (attempt 2)
Step 7: CodeValidator (attempt 2)
Step 8: E2BExecutor (attempt 2) - SUCCESS
Step 9: OutputValidator (attempt 2)
```

Each row contains:

```python
class ChainOfWorkStep:
    # Step identification
    step_number: int          # 1-6 (which agent in sequence)
    step_name: str            # "input_analysis", "code_generation", etc.
    agent_name: str           # "InputAnalyzer", "CodeGenerator", etc.
    attempt_number: int       # 1-3 (retry attempt)
    
    # Agent I/O
    input_data: JSON          # What the agent received
    output_data: JSON         # What the agent returned
    generated_code: str       # Code generated (CodeGenerator, DataAnalyzer)
    
    # E2B execution
    sandbox_id: str           # E2B sandbox ID for debugging
    
    # AI metadata
    model_used: str           # "gpt-4o-mini", "gpt-4o", etc.
    tokens_input: int         # Tokens consumed
    tokens_output: int        # Tokens generated
    cost_usd: float           # Cost of this agent execution
    tool_calls: JSON          # RAG searches performed
    
    # Status and performance
    status: str               # "success" or "failed"
    error_message: str        # If failed
    execution_time_ms: float  # How long this agent took
```

### 4.3 Persistence Flow in GraphEngine

**Location**: `/nova/src/core/engine.py` lines 550-613

```python
# After executing a node
metadata = await self._execute_node(...)

if self.db_session and execution:
    from ..models.chain_of_work import ChainOfWork
    from ..models.chain_of_work_step import ChainOfWorkStep
    
    # Extract steps from AI metadata (only CachedExecutor generates these)
    ai_metadata = metadata.get('ai_metadata', {}) or {}
    steps_to_persist = ai_metadata.pop('_steps', [])  # Extract and remove
    
    # 1. Create main ChainOfWork entry
    chain_entry = ChainOfWork(
        execution_id=execution.id,
        node_id=metadata['node_id'],
        node_type=metadata['node_type'],
        code_executed=metadata.get('code_executed'),
        input_context=metadata['input_context'],              # Deep snapshot
        output_result=metadata['output_result'],              # Deep snapshot
        execution_time=metadata['execution_time'],
        status=metadata['status'],
        error_message=metadata.get('error_message'),
        decision_result=metadata.get('decision_result'),
        path_taken=metadata.get('path_taken'),
        ai_metadata=ai_metadata,  # Without _steps
        timestamp=datetime.utcnow()
    )
    db_session.add(chain_entry)
    db_session.flush()  # Get chain_entry.id
    
    # 2. Create ChainOfWorkStep entries (if they exist)
    if steps_to_persist:
        for step_data in steps_to_persist:
            step_entry = ChainOfWorkStep(
                chain_of_work_id=chain_entry.id,
                step_number=step_data['step_number'],
                step_name=step_data['step_name'],
                agent_name=step_data['agent_name'],
                attempt_number=step_data['attempt_number'],
                input_data=step_data.get('input_data'),
                output_data=step_data.get('output_data'),
                generated_code=step_data.get('generated_code'),
                sandbox_id=step_data.get('sandbox_id'),
                model_used=step_data.get('model_used'),
                tokens_input=step_data.get('tokens_input'),
                tokens_output=step_data.get('tokens_output'),
                cost_usd=step_data.get('cost_usd'),
                tool_calls=step_data.get('tool_calls'),
                status=step_data['status'],
                error_message=step_data.get('error_message'),
                execution_time_ms=step_data['execution_time_ms'],
                timestamp=step_data['timestamp']
            )
        db_session.add_all(step_entries)
    
    db_session.commit()
```

### 4.4 Failed Node Handling

**Location**: `/nova/src/core/engine.py` lines 615-731

```python
except GraphExecutionError as e:
    # Extract generated code from ExecutorError if available
    code_to_save = None
    ai_metadata_to_save = None
    
    original_error = e.__cause__  # The original ExecutorError
    
    if isinstance(original_error, ExecutorError):
        # Extract generated code from the last attempt
        if hasattr(original_error, 'generated_code') and original_error.generated_code:
            code_to_save = original_error.generated_code
        
        # Extract full history of ALL generation attempts
        if hasattr(original_error, 'error_history') and original_error.error_history:
            ai_metadata_to_save = {
                "model": "gpt-4o-mini",
                "attempts": len(original_error.error_history),
                "all_attempts": original_error.error_history,  # All failed attempts
                "final_error": str(e),
                "status": "failed_after_retries"
            }
    
    # Fallback: use original prompt/code from node
    if not code_to_save:
        code_to_save = getattr(current_node, 'prompt', None) or getattr(current_node, 'code', None)
    
    # Create metadata for failed node
    failed_metadata = {
        "node_id": current_node_id,
        "node_type": current_node.type,
        "status": "failed",
        "error_message": str(e),
        "input_context": context.snapshot(),
        "output_result": context.snapshot(),
        "code_executed": code_to_save,        # ✅ Generated code or prompt
        "ai_metadata": ai_metadata_to_save,   # ✅ All attempts with errors
        ...
    }
    
    # Persist to ChainOfWork with ALL attempts
    chain_entry = ChainOfWork(
        execution_id=execution.id,
        ...,
        code_executed=failed_metadata.get('code_executed'),
        ai_metadata=ai_metadata_failed,
        ...
    )
```

---

## 5. RELATIONSHIP BETWEEN CONTEXT AND EXECUTION TRACING

### 5.1 The Two-Stream Model

```
GraphEngine.execute_workflow()
    ├─ Stream 1: Context Flow
    │  └─ ContextManager
    │     └─ Node A → Node B → Node C
    │
    ├─ Stream 2: Metadata Flow
    │  └─ execution_trace (list of metadata dicts)
    │     └─ Each metadata dict contains:
    │        - input_context (snapshot)
    │        - output_result (snapshot)
    │        - code_executed
    │        - status, error_message
    │        - ai_metadata
    │        - _ai_metadata._steps (agents' details)
    │
    └─ Stream 3: Database Persistence
       └─ ChainOfWork table
          └─ Each row = node execution
             └─ ChainOfWorkStep table
                └─ Each row = agent execution within node
```

### 5.2 Why Both Context AND Execution Trace?

| Aspect | Context | Execution Trace | Chain of Work |
|--------|---------|-----------------|---------------|
| **What** | Workflow data | Node metadata | Immutable audit trail |
| **Scope** | Shared between nodes | Single node | Complete history |
| **Mutable** | Yes (in-memory) | Yes (in-memory) | No (read-only DB) |
| **Lifetime** | During workflow | During workflow | Permanent |
| **Purpose** | Execute next node | Debugging, analytics | Compliance, auditing |
| **Example** | `{"pdf_path": "...", "invoice_data": {...}}` | `{"code_executed": "...", "status": "success"}` | Row with input_context + output_result snapshots |

### 5.3 Context Isolation in Snapshots

```python
# Snapshot pattern prevents future mutations from affecting stored history
input_snapshot = context.snapshot()  # Deep copy BEFORE execution

# Later mutations don't affect the snapshot
context.update({"large_pdf": "new_value"})

# Snapshot is still immutable
print(input_snapshot)  # Still has old value (if it was there)

# Stored in ChainOfWork
chain_entry.input_context = input_snapshot  # Safe forever
```

### 5.4 Special Case: AI Metadata Embedding

For CachedExecutor nodes, AI metadata is EMBEDDED in the context update:

```python
# In orchestrator.execute_workflow()
result = {
    **context_state.current,      # Context updates (flows to next node)
    "_ai_metadata": {              # Metadata (flows to ChainOfWork)
        "input_analysis": {...},
        "data_analysis": {...},
        "code_generation": {...},
        "code_validation": {...},
        "output_validation": {...},
        "attempts": 1-3,
        "errors": [...],
        "timings": {...},
        "_steps": [...]            # Granular agent trace
    }
}
```

Then in GraphEngine:

```python
# Extract and remove from context before persisting
ai_metadata = updated_context.pop("_ai_metadata", None)

# Keep context clean for next node
context.update(updated_context)

# Store metadata separately
chain_entry.ai_metadata = ai_metadata
```

**Critical**: `_ai_metadata` is NOT merged into the context that flows to the next node. It's stored separately.

---

## 6. IDENTIFIED ISSUES & INCONSISTENCIES

### Issue 1: Context Merge Ambiguity

**Problem**: In orchestrator, E2B execution returns either:
- Format A: `{"key": "value"}` (direct context)
- Format B: `{"context_updates": {"key": "value"}, "status": "success"}` (wrapped)

**Current handling**:
```python
if "context_updates" in updated_context:
    context_state.current.update(updated_context.get("context_updates", {}))
else:
    context_state.current.update(updated_context)
```

**Risk**: If AI-generated code accidentally prints wrong format, entire context could be overwritten.

**Mitigation in place**: Prompt explicitly tells AI to use `{"status": "success", "context_updates": {...}}`

---

### Issue 2: AI Metadata Structure Inconsistency

**Problem**: AI metadata can be stored in two places:
1. In `ChainOfWork.ai_metadata` (node-level summary)
2. In `ChainOfWorkStep` rows (agent-level detail)

**When saving to DB**:
```python
ai_metadata = metadata.get('ai_metadata', {}) or {}
steps_to_persist = ai_metadata.pop('_steps', [])  # Extract and remove

chain_entry = ChainOfWork(
    ai_metadata=ai_metadata,  # WITHOUT _steps (to avoid duplication)
    ...
)
```

**Risk**: If steps aren't properly extracted, they get lost OR duplicated.

**Current safeguard**: Explicit `pop('_steps', [])` removes from parent before saving.

---

### Issue 3: Decision Context Not Isolated

**Problem**: DecisionNode reads `context['branch_decision']` which was SET by the code:

```python
# In GraphEngine._find_next_node()
decision_result = context.get("branch_decision")  # ← Could be stale from previous node!
```

**What if** a previous node accidentally set `branch_decision`?
- DecisionNode would read the WRONG value
- Wrong path would be taken

**Mitigation**: Code generation prompt explicitly says:
```
IMPORTANTE: Imprimir SOLO los cambios realizados al contexto
Esto preserva datos existentes que no cambiaron
```

But there's no explicit CLEARING of `branch_decision` before DecisionNode.

**Recommendation**: Clear `branch_decision` before each DecisionNode execution.

---

### Issue 4: Snapshot Size Explosion

**Problem**: For large PDFs/files in context:
- Each snapshot is a DEEP copy
- Multiple snapshots per node (input_context, output_result, agent input_data)
- Database stores FULL JSON

Example for 1 node with 50MB PDF in base64:
- input_context: 50MB
- E2B input_data (summarized): "< string: 50MB chars >"
- output_result: 50MB+
- Total: 150MB+ for ONE node

**Mitigation in place**:
- Orchestrator summarizes context for steps: `_summarize_context_for_step()`
- Truncates strings > 200 chars
- Shows: `"<string: 50000000 chars>"` instead of actual content

**Risk**: If someone disables summarization, DB bloats rapidly.

---

### Issue 5: Error Metadata Loss on First Attempt Failure

**Problem**: If E2BExecutor fails on first code execution, the error is caught but the generated code might be lost:

```python
try:
    updated_context = await self.e2b.execute_code(...)
except Exception as e:
    error_msg = f"Error en E2B: {str(e)}"
    execution_state.add_error("execution", error_msg)
    # ← Generated code is INSIDE the e2b_executor, not accessible here
```

**Mitigation in place**:
- E2BExecutor raises CodeExecutionError which carries generated_code
- GraphEngine catches and extracts: `original_error.generated_code`

**Location**: `/nova/src/core/engine.py` lines 625-632

---

## 7. CONTEXT UPDATE ENFORCEMENT IN AI PROMPTS

### Summary of Enforcement Mechanisms

| Mechanism | Location | Strength |
|-----------|----------|----------|
| **Prompt instruction** | CodeGenerator._build_prompt() | Strong - explicit rules |
| **Output format** | E2BExecutor._execute_sync() | Strong - validates JSON structure |
| **Retry with feedback** | MultiAgentOrchestrator | Strong - CodeGenerator gets error history |
| **Validation** | CodeValidator | Medium - checks syntax, not output format |
| **Post-execution check** | GraphEngine._execute_node() | Strong - extracts decision_result |

### Enforcement in Action

```
1. CodeGenerator creates prompt
   ↓
2. OpenAI generates code with:
   context_updates = {...}
   print(json.dumps({"status": "success", "context_updates": context_updates}))
   ↓
3. E2B executes code
   ↓
4. E2BExecutor parses output
   - Validates JSON structure
   - If "context_updates" missing: error
   - Extracts only context_updates (not full context)
   ↓
5. Orchestrator merges
   context_state.current.update(context_updates)
   ↓
6. GraphEngine stores snapshots
   input_context, output_result
```

---

## 8. KEY OBSERVATIONS

### 8.1 Context is NOT Shared with AI

Important: AI agents (CodeGenerator, InputAnalyzer, OutputValidator) **never see the full context as JSON**.

Instead:
- CodeGenerator sees: `context_schema` (keys + summarized values)
- CodeGenerator accesses actual values via `context['key']` AT RUNTIME
- AI generates code that modifies `context` dict

**Example**:
```python
# Prompt shows:
{
    "pdf_path": "/tmp/invoice.pdf",
    "email_body": "<string: 2000 chars>",
    "pdf_content": "<bytes: 150000 bytes>"
}

# Generated code does:
pdf_path = context['pdf_path']  # ← Gets actual value at runtime
```

### 8.2 Orchestrator Preserves Non-Modified Context

Critical pattern in orchestrator (line 338):

```python
updated_context = await self.e2b.execute_code(...)
context_state.current.update(updated_context)  # ← Merge, not replace!
```

**This means**: If code only modifies 2 keys, the other keys remain unchanged.

**Example**:
```python
# Before: context_state.current = {"pdf_path": "...", "user_id": 123, "results": {...}}
# After code execution: {"new_key": "value"}
# Merged: {"pdf_path": "...", "user_id": 123, "results": {...}, "new_key": "value"}
```

### 8.3 Decision Branching Requires Explicit Context Setting

For DecisionNode to work:
1. Code MUST set `context['branch_decision']`
2. Value must be: "true", "false", or matching edge condition
3. GraphEngine reads this value
4. Finds matching edge

**If code fails to set it**:
```python
decision_result = context.get("branch_decision")
if decision_result is None:
    raise GraphExecutionError(
        f"DecisionNode {node_id} did not set 'branch_decision' in context"
    )
```

---

## SUMMARY TABLE: Context Flow

| Layer | Component | Context Type | Mutable | Scope |
|-------|-----------|--------------|---------|-------|
| **1. Workflow** | ContextManager | Key-value dict | Yes | All nodes |
| **2. Node (multi-agent)** | ContextState | {initial, current, data_insights} | Yes (current only) | Within orchestrator |
| **3. Agent** | AgentResponse.data | Agent output (varies) | N/A | Single agent |
| **4. Execution** | ExecutionState | Metadata dict | Yes (in-memory) | Within node |
| **5. Database** | ChainOfWork | Immutable snapshots | No | Permanent |
| **6. Granular trace** | ChainOfWorkStep | Agent I/O snapshot | No | Permanent |

---

## CONCLUSION

NOVA's context management is **well-architected** with clear separation of concerns:

1. **ContextManager** handles workflow-level state
2. **ContextState** tracks changes within a node
3. **ExecutionState** records agent-level details
4. **Chain of Work** provides immutable audit trail
5. **Snapshots** prevent mutation of historical data

The **AI prompt enforcement** is strong:
- Explicit instructions for output format
- Validation of JSON structure
- Retry with error feedback
- Post-execution verification (especially for DecisionNodes)

**Minor risks** identified can be mitigated through:
- Clearing `branch_decision` before each DecisionNode
- Documenting context_updates format expectations
- Monitoring step extraction for duplication
