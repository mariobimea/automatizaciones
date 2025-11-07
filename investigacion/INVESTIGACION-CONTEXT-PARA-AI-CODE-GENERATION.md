# AI Code Generation: Investigación de Contexto Necesario

**Fecha**: 2025-11-05
**Objetivo**: Documentar comprehensivamente qué contexto el AI (Claude/GPT-4) necesita para generar código ejecutable de calidad en NOVA
**Scope**: Phase 2 (AIExecutor) - Sistema que genera código Python on-the-fly para ejecutarse en E2B sandbox

---

## RESUMEN EJECUTIVO

Para que un LLM genere código Python ejecutable en NOVA, necesita:

1. **Especificación del Runtime** - Qué Python, qué librerías, qué ambiente
2. **Definición de Tareas** - Qué debe hacer el código (descripción + ejemplos)
3. **Formato de Entrada/Salida** - Cómo recibe datos (context dict) y cómo retorna (actualiza context)
4. **Restricciones de Seguridad** - Qué NO puede hacer (imports peligrosos, etc.)
5. **Ejemplos de Código** - Patrones exitosos previos (few-shot learning)
6. **Manejo de Errores** - Cómo fallar gracefully
7. **Context Provider** - Estructura de datos disponibles en runtime
8. **Performance Expectations** - Timeouts, límites de memoria

**Criticidad**: Sin este contexto bien estructurado, el AI generará código que:
- No compila (syntax errors)
- Falla al ejecutar (missing imports, type errors)
- No retorna datos correctamente (formato JSON incorrecto)
- Excede timeouts (código ineficiente)
- No está auditable (no hay logging)

---

## PARTE 1: RUNTIME ENVIRONMENT SPECIFICATION

### 1.1 Python Environment

**Qué el AI debe saber**:

```yaml
Python Version: 3.11
Runtime Location: E2B Cloud Sandbox (https://e2b.dev)
Execution Model: Synchronous (code runs in isolation, returns stdout)
Execution Timeout: Configurable (default 30s per node)
Memory Limit: Unlimited in E2B (good for analysis, bad for safety)
CPU Limit: E2B manages automatically
Network Access: YES - can call APIs, databases, email servers
Filesystem Access: Read-only /input, write to /output (future)
```

**Prompt snippet for AI**:

```
You will generate Python 3.11 code that runs in an E2B cloud sandbox.
The environment has:
- Full network access (HTTP, SMTP, IMAP, databases)
- Pre-installed packages (see below)
- Standard library + common scientific packages
- No filesystem write access (inputs are read-only)
- 30 second execution timeout per operation
```

### 1.2 Pre-installed Libraries

**Current (E2B Base Template)**:
- pandas 2.0+ (data manipulation)
- requests 2.31+ (HTTP client)
- beautifulsoup4 4.12+ (HTML/XML parsing)
- pillow 10+ (image processing)
- numpy 1.24+ (numerical computing)
- openpyxl 3.1+ (Excel files)
- PyMuPDF (fitz) 1.23+ (PDF text extraction)
- reportlab 4.0+ (PDF generation)
- smtplib (standard library - email sending)
- imaplib (standard library - email reading)
- json (standard library - serialization)
- re (standard library - regex)
- os, sys, pathlib (standard library)

**Template in E2B**:
- ID: `nova-workflow-fresh` (or base template if not set)
- Custom pre-built image with above packages
- Fast cold start ~5-10s

**What AI needs to know**:
```python
# Available libraries in E2B sandbox:
AVAILABLE_LIBS = {
    "data": ["pandas", "numpy", "openpyxl"],
    "web": ["requests", "beautifulsoup4"],
    "files": ["PIL/pillow", "PyMuPDF/fitz", "reportlab"],
    "email": ["smtplib", "imaplib", "email"],  # stdlib
    "serialization": ["json"],  # stdlib
    "text": ["re"],  # stdlib
}

# Libraries NOT available:
# - Anything requiring system commands (subprocess, os.system)
# - Database drivers NOT listed (check before using)
# - ML libraries (sklearn, torch - too heavy)
# - External APIs requiring special setup
```

### 1.3 Dangerous Patterns to Avoid

**Prompt snippet**:
```
NEVER use these patterns (will fail in sandbox):
- import subprocess (no system commands)
- import os.system (no shell access)
- import __import__ (security risk)
- socket-level networking (use requests instead)
- file I/O outside /input and /output (doesn't exist)
- eval() or exec() (security risk)
- multiprocessing (not available)

ALWAYS:
- Treat context as mutable dict
- Return final context by printing JSON
- Handle missing keys gracefully
- Test imports before using
```

---

## PARTE 2: WORKFLOW CONTEXT STRUCTURE

### 2.1 Input Context Format

**What the AI receives at node execution**:

```python
context = {
    # Workflow metadata
    "workflow_id": "invoice_processing_v1",
    "execution_id": 12345,
    "node_id": "extract_invoice_data",
    "client_slug": "idom_company",
    
    # Previous node results (accumulate through workflow)
    "invoice_pdf": b"<binary pdf data>",      # From earlier node
    "has_emails": True,                       # From earlier node
    "email_from": "sender@example.com",       # From earlier node
    
    # Client configuration (if available)
    "email_credentials": {...},  # Sensitive - handle carefully
    "database_credentials": {...},
    
    # Constants/config
    "threshold_amount": 1000.0,
    "approval_required_count": 2,
    
    # Internal (for decision nodes)
    "branch_decision": None,  # Will be set by this node
}
```

### 2.2 Output Context Format

**What the AI code must return**:

```python
# At END of code, context must be updated and printed as JSON:

context['extracted_amount'] = 1500.00
context['vendor_name'] = "ACME Corp"
context['is_valid'] = True
context['branch_decision'] = True  # For DecisionNode

# CRITICAL: Must print final context as valid JSON
print(json.dumps(context, ensure_ascii=True))
```

**Why `ensure_ascii=True`**:
- E2B sandbox may have encoding issues with special characters
- Spanish characters (á, é, ñ, etc.) need proper escaping
- Unicode characters escaped as `\uXXXX` = valid JSON everywhere

### 2.3 Context Access Patterns

**Patterns AI must understand**:

```python
# SAFE: Read from context
amount = context.get('total_amount', 0.0)  # With default
vendor = context['vendor_name']  # Direct access (might fail)

# SAFE: Write to context
context['processed_at'] = datetime.utcnow().isoformat()
context['invoice_id'] = db_insert_result

# UNSAFE: Delete from context (don't - just don't use it)
# del context['sensitive_field']  # BAD

# AVOID: Modifying nested structures without copying
# context['nested']['field'] = value  # Might cause issues
# DO THIS instead:
nested = context.get('nested', {})
nested['field'] = value
context['nested'] = nested
```

### 2.4 Typical Context Evolution Through Workflow

```
Start Node
  context = {
    "workflow_id": "invoice_processing",
    "client_slug": "idom",
  }
  ↓
read_emails Node
  context['has_emails'] = True
  context['email_from'] = "..."
  context['email_subject'] = "..."
  ↓
extract_pdf Node
  context['pdf_data'] = b"..."
  context['pdf_filename'] = "invoice.pdf"
  ↓
ocr_extract Node
  context['ocr_text'] = "TOTAL: 1500.00 EUR"
  ↓
find_amount Node
  context['total_amount'] = 1500.00
  context['currency'] = 'EUR'
  ↓
amount_decision Node (DecisionNode)
  context['branch_decision'] = True  # Amount > 1000
  ↓
[Decision branches to different nodes based on branch_decision]
```

---

## PARTE 3: CODE GENERATION PROMPT TEMPLATE

### 3.1 Prompt Structure (Few-Shot Example)

```
System Prompt:
============

You are an expert Python developer generating code for NOVA workflow engine.

Your code will:
1. Execute in E2B cloud sandbox (Python 3.11)
2. Receive input via 'context' dict (already injected)
3. Modify context to return data
4. Print final context as JSON

RULES:
- Single operation per node (focused, debuggable)
- Handle missing context keys gracefully
- Include error handling with try/except
- Log important steps with print() statements
- Always end with: print(json.dumps(context, ensure_ascii=True))
- No imports for __builtin__ or dangerous modules
- No file writes outside /output (not available yet)

LIBRARIES AVAILABLE:
pandas, requests, beautifulsoup4, pillow, numpy, openpyxl,
fitz (PyMuPDF), reportlab, json, re, imaplib, smtplib

---

User Prompt:
============

TASK: Extract total amount from PDF invoice

CONTEXT INPUT:
{
  "pdf_data": <binary>,
  "pdf_filename": "invoice.pdf"
}

EXPECTED OUTPUT:
{
  "total_amount": <float>,
  "currency": "EUR",
  "extraction_method": "pymupdf"
}

REQUIREMENTS:
- Use PyMuPDF to extract text from PDF
- Find amount patterns like "Total: €1200" or "TOTAL €1200.00"
- Handle missing amount gracefully (return 0.0)
- Log extraction steps

CONSTRAINTS:
- Timeout: 30 seconds
- No external API calls
- Context is mutable - modify in-place

Generate ONLY the Python code. No explanations.
```

### 3.2 Response Code Pattern

```python
# What AI should generate:

import fitz  # PyMuPDF
import re
import json

try:
    # Extract
    pdf_data = context.get('pdf_data')
    if not pdf_data:
        context['total_amount'] = 0.0
        context['currency'] = 'EUR'
        context['extraction_method'] = 'none'
    else:
        # Convert bytes to PDF stream
        pdf_stream = BytesIO(pdf_data)
        doc = fitz.open(stream=pdf_stream, filetype='pdf')
        
        # Extract text
        full_text = ''
        for page in doc:
            full_text += page.get_text()
        doc.close()
        
        # Find amount
        pattern = r'total[:\s]+€?\s*(\d+[.,]\d{2})'
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        
        if matches:
            amount_str = matches[-1].replace(',', '.')
            context['total_amount'] = float(amount_str)
        else:
            context['total_amount'] = 0.0
        
        context['currency'] = 'EUR'
        context['extraction_method'] = 'pymupdf'
        
except Exception as e:
    # Error handling
    print(f"ERROR: {str(e)}", file=sys.stderr)
    context['total_amount'] = 0.0
    context['error'] = str(e)

# CRITICAL: Return updated context as JSON
print(json.dumps(context, ensure_ascii=True))
```

---

## PARTE 4: EXAMPLES & FEW-SHOT LEARNING

### 4.1 Example 1: Simple Data Extraction

**Example for AI to learn from**:

```python
# EXAMPLE: Extract email attachments (worked successfully before)
import email
import io

try:
    email_msg = context.get('email_message')
    
    if not email_msg:
        context['has_attachment'] = False
        context['attachment_data'] = None
    else:
        attachment_data = None
        for part in email_msg.walk():
            if part.get_content_disposition() == 'attachment':
                filename = part.get_filename()
                if filename and filename.endswith('.pdf'):
                    attachment_data = part.get_payload(decode=True)
                    context['has_attachment'] = True
                    context['attachment_filename'] = filename
                    break
        
        if not attachment_data:
            context['has_attachment'] = False
            
except Exception as e:
    context['has_attachment'] = False
    context['error'] = str(e)

print(json.dumps(context, ensure_ascii=True))
```

**What AI learns**:
- Pattern of try/except
- How to read from context safely with `.get()`
- How to set multiple keys
- Error handling without crashing
- JSON print at end

### 4.2 Example 2: External API Call

```python
# EXAMPLE: Get sender from email and validate with public API
import requests

try:
    email_from = context.get('email_from', '')
    
    if not email_from:
        context['sender_verified'] = False
    else:
        # Extract email from "Name <email@domain>" format
        email_addr = email_from.split('<')[-1].strip('>')
        
        # Optional: Call verification API
        response = requests.get(
            f"https://api.hunter.io/v2/email-verifier",
            params={"email": email_addr},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            context['sender_verified'] = data.get('result') == 'deliverable'
        else:
            context['sender_verified'] = False
            
except requests.Timeout:
    context['sender_verified'] = False
    context['error'] = 'API timeout'
except Exception as e:
    context['sender_verified'] = False
    context['error'] = str(e)

print(json.dumps(context, ensure_ascii=True))
```

**What AI learns**:
- Network calls with timeout
- Error handling for specific exceptions
- Safe extraction of data from strings
- Status code checking

### 4.3 Example 3: Decision Node

```python
# EXAMPLE: Decide if amount exceeds threshold (worked successfully)
try:
    amount = context.get('total_amount', 0.0)
    threshold = context.get('threshold_amount', 1000.0)
    
    # Set decision
    exceeds = amount > threshold
    context['branch_decision'] = exceeds
    
    # Log decision
    context['decision_reason'] = f"Amount {amount} vs threshold {threshold}"
    
except Exception as e:
    # If error, safe default
    context['branch_decision'] = False
    context['error'] = str(e)

print(json.dumps(context, ensure_ascii=True))
```

**What AI learns**:
- Decision nodes MUST set `branch_decision` boolean
- Can add metadata about the decision
- Safe defaults on error

### 4.4 Example 4: Database Operation

```python
# EXAMPLE: Save invoice to database (worked successfully)
from src.models.credentials import get_database_connection

try:
    conn = get_database_connection(context['client_slug'])
    cursor = conn.cursor()
    
    # Insert data
    cursor.execute("""
        INSERT INTO invoices (
            amount, vendor, date_processed
        ) VALUES (%s, %s, NOW())
        RETURNING id
    """, (
        context['total_amount'],
        context['vendor_name'],
    ))
    
    invoice_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    
    context['invoice_id'] = invoice_id
    context['saved_to_db'] = True
    
except Exception as e:
    context['saved_to_db'] = False
    context['error'] = str(e)
    if conn:
        conn.rollback()

print(json.dumps(context, ensure_ascii=True))
```

**What AI learns**:
- How to use context credentials safely
- Database transaction handling
- RETURNING clause for IDs
- Parameter passing with %s

---

## PARTE 5: ERROR HANDLING PATTERNS

### 5.1 Graceful Degradation

**Pattern AI should use**:

```python
# PATTERN: Graceful degradation (don't crash, set error fields)

try:
    # Try primary method
    result = primary_operation()
    context['result'] = result
    context['method'] = 'primary'
    
except PrimaryException:
    # Try fallback
    try:
        result = fallback_operation()
        context['result'] = result
        context['method'] = 'fallback'
        
    except FallbackException as e:
        # Final fallback: empty/default result
        context['result'] = None
        context['method'] = 'none'
        context['error'] = str(e)

print(json.dumps(context, ensure_ascii=True))
```

### 5.2 Timeout Prevention

```python
# PATTERN: Prevent timeouts with explicit resource limits

import requests

# Always set timeout on HTTP calls
response = requests.get(
    url,
    timeout=5  # Max 5 seconds for API call
)

# Don't process huge files
pdf_data = context.get('pdf_data')
if len(pdf_data) > 10_000_000:  # 10 MB limit
    context['error'] = 'PDF too large'
    context['file_size'] = len(pdf_data)
else:
    # Process
    pass
```

---

## PARTE 6: SECURITY CONTEXT

### 6.1 What AI Must Know About Security

```
SECURE:
✓ Read from context (it's pre-injected)
✓ Write to context (it's returned)
✓ Use requests library (sandbox sandboxed)
✓ Use database credentials from context
✓ Email operations (IMAP/SMTP)

INSECURE:
✗ import subprocess, os.system (no shell)
✗ import socket directly (use requests)
✗ eval(), exec() (no dynamic code execution)
✗ __import__() (no reflection)
✗ File operations outside /input /output (doesn't exist yet)
✗ Hardcoded credentials (use context instead)
✗ Printing unencoded strings with special chars

CAREFUL:
⚠️ Database connections (must close properly)
⚠️ Email attachments (might be malware)
⚠️ External API calls (rate limits, timeouts)
⚠️ Regex patterns (ReDoS attacks on huge strings)
```

### 6.2 Validation Pattern

```python
# PATTERN: Validate input before processing

import json

def validate_input_context(context):
    """Validate context has required fields"""
    required = ['workflow_id', 'client_slug']
    missing = [k for k in required if k not in context]
    
    if missing:
        raise ValueError(f"Missing context fields: {missing}")
    
    return True

try:
    validate_input_context(context)
    # Process
except ValueError as e:
    context['validation_error'] = str(e)
    context['status'] = 'error'

print(json.dumps(context, ensure_ascii=True))
```

---

## PARTE 7: MULTI-TEMPLATE FUTURE SUPPORT

### 7.1 How Templates Affect Code Generation

**What the AI needs to know**:

```
Templates = Different sandbox environments with different pre-installed packages

Current (E2B Base):
- Python 3.11 + standard libs
- pandas, requests, beautifulsoup4, pillow, numpy
- PyMuPDF, reportlab, openpyxl
- IMAP/SMTP email support

Future Templates (Phase 2+):
1. "ML Template": sklearn, tensorflow, pytorch (for predictions)
2. "Database Template": psycopg2, mysql-connector, sqlite3 (for DB work)
3. "Web Template": selenium, playwright (for scraping/automation)
4. "Office Template": openpyxl, python-docx, pptx (for office automation)
```

### 7.2 Template Context Injection

**For Phase 2 AI Executor**:

```python
# The GraphEngine will tell AI which template is available

prompt = f"""
This workflow uses the {template_name} sandbox template.

Available packages in this template:
{list_packages_for_template(template_name)}

... rest of prompt
"""
```

**Prompt modification per template**:

```python
TEMPLATE_CONTEXTS = {
    "base": {
        "libs": ["pandas", "requests", "beautifulsoup4", "pillow"],
        "example_use": "data processing, web scraping, PDF handling",
        "sample_code": "extract_data_with_pandas()",
    },
    "ml": {
        "libs": ["sklearn", "tensorflow", "pandas"],
        "example_use": "predictions, classification, regression",
        "sample_code": "train_model_with_sklearn()",
    },
    "database": {
        "libs": ["psycopg2", "openpyxl"],
        "example_use": "database queries, data insertion",
        "sample_code": "connect_to_postgres()",
    },
}

def get_template_prompt_injection(template_name: str) -> str:
    """Get prompt context for template"""
    if template_name in TEMPLATE_CONTEXTS:
        tc = TEMPLATE_CONTEXTS[template_name]
        return f"""
This workflow uses the {template_name} sandbox template.

Available libraries: {', '.join(tc['libs'])}
Best for: {tc['example_use']}
"""
    else:
        return f"Using custom template: {template_name}"
```

---

## PARTE 8: CHAIN-OF-WORK LOGGING CONTEXT

### 8.1 What Needs to be Logged

**For auditing generated code**:

```python
# The GraphEngine will automatically log:
chain_of_work_entry = {
    "execution_id": 12345,
    "node_id": "extract_invoice",
    "node_type": "action",
    "step_number": 3,
    
    # Generated code
    "code_generated": "import fitz\n...",
    
    # Execution context
    "input_context": {
        "pdf_data": "<binary>",
        "pdf_filename": "invoice.pdf"
    },
    "output_result": {
        "pdf_data": "<binary>",
        "pdf_filename": "invoice.pdf",
        "total_amount": 1500.00,
        "currency": "EUR"
    },
    
    # Execution results
    "stdout": "All output printed during execution",
    "stderr": "Any errors from code",
    "exit_code": 0,
    "execution_time": 2.34,  # seconds
    
    # LLM metadata (Phase 2)
    "llm_model": "gpt-4",
    "llm_tokens_used": 450,
    "llm_prompt_hash": "sha256...",
    
    "status": "success",
    "timestamp": "2025-11-05T10:30:00Z"
}
```

### 8.2 What AI Code Should Log

**Patterns for good auditability**:

```python
# PATTERN: Explicit step logging

import json

print("STEP 1: Reading PDF from context...")
pdf_data = context.get('pdf_data')

if pdf_data:
    print(f"STEP 1 COMPLETE: Got PDF ({len(pdf_data)} bytes)")
else:
    print("STEP 1 FAILED: No PDF data in context")

print("STEP 2: Extracting text...")
# ... extract ...
print(f"STEP 2 COMPLETE: Extracted {num_pages} pages")

print("STEP 3: Finding amount...")
# ... find ...
print(f"STEP 3 COMPLETE: Found amount €{amount}")

# Update context
context['total_amount'] = amount
context['extraction_steps'] = 3

# Return
print(json.dumps(context, ensure_ascii=True))
```

**Benefits**:
- Chain-of-Work stdout shows what happened
- Each step is traceable
- Easy to debug if something fails

---

## PARTE 9: IMPLEMENTATION CHECKLIST FOR AI CONTEXT

### 9.1 What NOVA Must Provide to AI

**Before generating code, ensure AI has**:

- [ ] **Runtime spec**: Python version, timeout, memory constraints
- [ ] **Available libraries**: Complete list with versions
- [ ] **Forbidden patterns**: What imports/operations fail
- [ ] **Context format**: Input dict structure + output requirements
- [ ] **Examples**: 3-5 working code examples for pattern matching
- [ ] **Error handling**: What to do when operations fail
- [ ] **Security constraints**: What's safe vs unsafe
- [ ] **Template info**: Which sandbox template is being used
- [ ] **Node metadata**: node_id, execution_id, workflow_id
- [ ] **Timeout**: Explicit timeout for this specific node
- [ ] **Performance expectations**: What "good" performance looks like

### 9.2 What AI Must Do

**When generating code, ensure**:

- [ ] **Single import section**: All imports at top
- [ ] **Try/except wrapping**: Main logic in try block
- [ ] **Context validation**: Check required fields exist
- [ ] **Error handling**: Never crash, set error fields instead
- [ ] **Logging**: Print progress for debugging
- [ ] **Context modification**: Update context in-place
- [ ] **JSON output**: Always print json.dumps(context, ensure_ascii=True) at end
- [ ] **No side effects**: Don't rely on state outside context
- [ ] **Timeout awareness**: No infinite loops, set explicit timeouts
- [ ] **Type handling**: Serialize non-JSON-serializable types properly

### 9.3 Prompt Template Summary

```
SYSTEM PROMPT:
- You are a code generation AI for NOVA workflow engine
- Your code runs in E2B Python 3.11 sandbox
- Context is injected as dict at start
- Return updated context as JSON at end
- No dangerous imports (subprocess, eval, etc.)

RUNTIME CONTEXT:
- Available libraries: [list]
- Timeout: 30s
- Template: base
- No filesystem writes

TASK DEFINITION:
- What should the code do?
- What input context fields?
- What output context fields?
- Success/failure criteria?

EXAMPLES:
- [2-3 similar working examples]
- Show error handling patterns
- Show context access patterns

CONSTRAINTS:
- Single focused operation
- Handle missing keys gracefully
- Explicit error messages
- Performance: [expected time]

Generate ONLY Python code.
```

---

## PARTE 10: GAPS & FUTURE IMPROVEMENTS

### 10.1 Current Gaps in NOVA

**What's missing for full AI Code Generation**:

1. **Sandbox Health Check**: AI needs to know if a library is available
   - Solution: Have AI try imports with try/except
   - Better: Have GraphEngine pre-validate available libs

2. **Context Schema Validation**: No validation of input/output context
   - Solution: Use Pydantic models for node input/output
   - Example: Each node defines expected context shape

3. **Code Templates**: No pre-built code templates to guide AI
   - Solution: Store successful code in PostgreSQL
   - Use semantic search to find similar code

4. **Determinism Metrics**: AI doesn't know if generated code is deterministic
   - Solution: Track if code produces same output for same input
   - Mark deterministic vs non-deterministic code

5. **Multi-model Support**: Currently assumes GPT-4, needs Claude
   - Solution: Abstract LLM interface
   - Different prompts for different models

### 10.2 Recommended Enhancements

**For Phase 2 AI Executor**:

```python
# Enhancement 1: Node Input/Output Schemas
@dataclass
class NodeSchema:
    node_id: str
    input_fields: Dict[str, Type]  # What context keys are used
    output_fields: Dict[str, Type]  # What context keys are set
    examples: List[CodeExample]
    
# Enhancement 2: Available Libraries API
class SandboxLibrariesContext:
    def get_available_libs(self) -> List[str]:
        return ["pandas", "requests", ...]
    
    def get_lib_version(self, lib: str) -> str:
        return "2.0.3"

# Enhancement 3: Code Template Library
class CodeTemplateCache:
    def find_similar(self, task: str, threshold: float = 0.85) -> List[CodeTemplate]:
        """Semantic search for similar successful code"""
        embeddings = encode_task(task)
        return search_db(embeddings, threshold)

# Enhancement 4: Code Validation Before Execution
class CodeValidator:
    def validate_syntax(self, code: str) -> bool:
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False
    
    def validate_security(self, code: str) -> bool:
        dangerous = ['subprocess', 'eval', '__import__']
        return all(d not in code for d in dangerous)
```

---

## PARTE 11: REAL EXAMPLE: E2B SANDBOX CONTEXT

### 11.1 Actual Invoice Workflow Context

**From /nova/fixtures/invoice_processing_workflow.json**:

```
Node: read_emails (ActionNode)
├─ Input context: { client_slug, workflow_id, execution_id }
├─ Code: Read unread emails via IMAP
├─ Output context: { 
│   has_emails, email_from, email_subject, email_date, 
│   passes_whitelist, imap_connection 
│ }
└─ Timeout: 30s

Node: check_pdf (ActionNode)
├─ Input: { has_emails, passes_whitelist, email_message }
├─ Code: Extract PDF from email attachment
├─ Output: { has_pdf, pdf_data, pdf_filename }
└─ Timeout: 10s

Node: has_pdf_decision (DecisionNode)
├─ Input: { has_pdf }
├─ Code: Set branch_decision = has_pdf
├─ Output: { branch_decision }
└─ Timeout: 5s

Node: extract_pdf_text (ActionNode)
├─ Input: { pdf_data }
├─ Code: Use PyMuPDF to OCR text
├─ Output: { ocr_text, ocr_method, pdf_size_bytes }
└─ Timeout: 30s

Node: find_total_amount (ActionNode)
├─ Input: { ocr_text }
├─ Code: Regex to find "Total: €1200" pattern
├─ Output: { total_amount, currency }
└─ Timeout: 10s

Node: amount_threshold_decision (DecisionNode)
├─ Input: { total_amount }
├─ Code: Set branch_decision = (total_amount > 1000)
├─ Output: { branch_decision }
└─ Timeout: 5s

Node: save_to_database (ActionNode)
├─ Input: { total_amount, pdf_data, ocr_text, ... }
├─ Code: INSERT INTO invoices
├─ Output: { invoice_id, invoice_saved }
└─ Timeout: 30s
```

**What AI needs to know**:
- Each node has specific input/output contract
- PDF data is bytes, OCR text is string
- Decisions are boolean
- Database connection via credentials from context

---

## CONCLUSIONES

### Context Necessities Summary

Para que un LLM genere código ejecutable en NOVA's AI Executor, NOVA debe proporcionar:

| Component | Purpose | Example |
|-----------|---------|---------|
| **Runtime Spec** | Know environment constraints | Python 3.11, 30s timeout, E2B |
| **Library List** | Know what to import | pandas, requests, PyMuPDF |
| **Context Schema** | Know input/output structure | { pdf_data, total_amount, ... } |
| **Examples** | Learn patterns from success | 3-5 working code samples |
| **Error Patterns** | Fail gracefully | try/except, default values |
| **Security Rules** | Avoid dangerous ops | No subprocess, eval, etc. |
| **Node Metadata** | Include for audit | workflow_id, node_id, execution_id |
| **Template Info** | Adjust to sandbox type | "base", "ml", "database" |

### Recomendación

**Para Phase 2, estructurar AIExecutor así**:

```python
class AIExecutor(ExecutorStrategy):
    def __init__(self, llm_client, code_validator):
        self.llm = llm_client
        self.validator = code_validator
    
    async def execute(self, code: str, context: Dict, timeout: int):
        # For Phase 2: code will be generated, not provided
        # But we keep interface same
        
        # 1. Build comprehensive prompt with all context
        prompt = self._build_prompt(code, context, timeout)
        
        # 2. Generate code with LLM
        generated_code = await self.llm.generate(prompt)
        
        # 3. Validate before executing
        validation = self.validator.validate(generated_code)
        if not validation.success:
            raise CodeGenerationError(validation.error)
        
        # 4. Execute in sandbox
        result = await self._execute_in_e2b(generated_code, context, timeout)
        
        return result
    
    def _build_prompt(self, task: str, context: Dict, timeout: int) -> str:
        """Build comprehensive AI prompt with ALL necessary context"""
        template = """
        You are generating Python code for NOVA workflow engine.
        
        RUNTIME:
        {runtime_spec}
        
        AVAILABLE LIBRARIES:
        {available_libs}
        
        INPUT CONTEXT:
        {context_schema}
        
        CURRENT CONTEXT:
        {current_context}
        
        TASK:
        {task}
        
        EXAMPLES (patterns to follow):
        {examples}
        
        CONSTRAINTS:
        {constraints}
        
        Generate ONLY Python code.
        """
        
        return template.format(
            runtime_spec=self._get_runtime_spec(),
            available_libs=self._get_available_libs(),
            context_schema=self._get_context_schema(context),
            current_context=self._serialize_context(context),
            task=task,
            examples=self._get_code_examples(),
            constraints=self._get_constraints(timeout),
        )
```

---

**Última actualización**: 2025-11-05
**Próximo paso**: Implementar AIExecutor en Phase 2 con contexto completo descrito aquí

