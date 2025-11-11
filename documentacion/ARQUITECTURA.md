# 🏗️ NOVA - Arquitectura del Sistema

**Última actualización**: 11 Noviembre 2025
**Estado**: Phase 1 completo + Phase 2 funcional

---

## 📌 ¿Qué es NOVA?

**NOVA** (Neural Orchestration & Validation Agent) es un motor de ejecución de workflows basado en grafos dirigidos con lógica condicional y capacidades de generación de código con IA.

**Objetivo**: Ejecutar workflows complejos con decisiones dinámicas, auditoría completa, y capacidad de auto-generación de código usando LLMs.

---

## 🎯 Estado Actual del Proyecto

### **Phase 1: MVP con Código Estático** ✅ **COMPLETO**
- ✅ Graph Engine funcionando
- ✅ E2BExecutor (código hardcodeado)
- ✅ API REST (15 endpoints)
- ✅ PostgreSQL + Chain of Work
- ✅ Multi-tenant credentials
- ✅ Deployment en Railway
- ✅ E2B custom template (cold start optimizado)

### **Phase 2: AI Code Generation** 🟢 **FUNCIONAL**
- ✅ CachedExecutor implementado (genera código con OpenAI GPT-4o-mini)
- ✅ KnowledgeManager (context-aware prompts)
- ✅ Context validation y JSON serialization
- ✅ Error retry con feedback (max 3 intentos)
- ✅ **Smart validation** (permite campos actualizados, booleanos, números)
- ✅ **Full traceability** (guarda código generado incluso si falla)
- ✅ **Error history** (todos los intentos guardados en chain_of_work)
- ✅ Circuit breaker para E2B
- ✅ Tests automatizados pasando
- ❌ Cache de código (pendiente Phase 3)
- ❌ Semantic cache con embeddings (pendiente Phase 3)

---

## 🏗️ Stack Tecnológico

### Aplicación (Railway)
- **Backend**: FastAPI + Python 3.11
- **Workers**: Celery + Redis (para async tasks)
- **Base de Datos**: PostgreSQL (workflows, executions, chain_of_work, credentials)
- **Deployment**: Railway monolito modular (~$15-20/mes)

### Sandbox (E2B Cloud)
- **Runtime**: E2B cloud sandboxes (https://e2b.dev)
- **Características**:
  - Python 3.11 execution environments aislados
  - Network access habilitado (IMAP, SMTP, APIs, databases)
  - Custom template con PyMuPDF, pandas, requests pre-instalados
  - Resource limits y timeouts automáticos (60s default)
  - 5GB RAM, 1 CPU, 5GB disk
- **Pricing**:
  - Development: $0/mes (usa $100 free credits)
  - Production: ~$7-10/mes para uso típico

**Costo total**: ~$15-25/mes en producción

---

## 🧩 Componentes Principales

### 1. Graph Engine (`src/core/engine.py`)

Motor que ejecuta workflows representados como grafos dirigidos.

**Responsabilidades**:
- Parsear definiciones de workflows (JSON)
- Validar estructura del grafo (ciclos, nodos inalcanzables, edges válidos)
- Ejecutar nodos secuencialmente siguiendo edges
- Gestionar flujo condicional (decisiones)
- Persistir ejecución en PostgreSQL
- Registrar cada paso en Chain of Work

**Código**:
```python
from src.core.engine import GraphEngine

engine = GraphEngine()
result = await engine.execute_workflow(
    workflow_definition={...},
    initial_context={"input": "data"}
)
```

---

### 2. Executors (`src/core/executors.py`)

Estrategias para ejecutar código en nodos del workflow.

#### **E2BExecutor** (Phase 1 - DEFAULT)
Ejecuta código Python **hardcodeado** en workflow definitions.

**Características**:
- Código predefinido en campo `code` del nodo
- Network access para operaciones reales (IMAP, SMTP, APIs, databases)
- Pre-installed libraries (PyMuPDF, pandas, requests)
- Auditoría completa via Chain of Work
- Circuit breaker para proteger contra E2B downtime

**Uso**:
```json
{
  "id": "extract_pdf",
  "type": "action",
  "executor": "e2b",
  "code": "import fitz\npdf_bytes = base64.b64decode(context['pdf_b64'])\n...",
  "timeout": 30
}
```

#### **CachedExecutor** (Phase 2 - AI-POWERED)
Genera código Python dinámicamente usando OpenAI GPT-4o-mini.

**Características**:
- Código generado on-the-fly desde prompts en lenguaje natural
- Error retry con feedback (max 3 intentos)
- Context-aware prompts con KnowledgeManager
- JSON serialization validation
- Logs de AI metadata (tokens, cost, prompts)

**Uso**:
```json
{
  "id": "extract_pdf",
  "type": "action",
  "executor": "cached",
  "prompt": "Decode PDF from base64, extract text using PyMuPDF, clean control characters",
  "timeout": 60
}
```

**KnowledgeManager**: Sistema que inyecta documentación relevante en prompts basado en:
- Análisis del task (detección de integraciones: IMAP, SMTP, PDF, PostgreSQL)
- Contexto actual del workflow
- Error history (si hay reintentos)

---

### 3. Nodes (`src/core/nodes.py`)

Tipos de nodos en el grafo:

#### **StartNode**
- Marca el inicio del workflow
- Único nodo sin incoming edges

#### **ActionNode**
- Ejecuta una acción (extracción, validación, procesamiento)
- Usa un Executor para correr código Python
- Actualiza el contexto con resultados

#### **DecisionNode**
- Toma decisiones basadas en contexto
- Ejecuta código que retorna `branch_decision` (True/False o string)
- Determina siguiente nodo según resultado

#### **EndNode**
- Marca el fin del workflow
- Único nodo sin outgoing edges

---

### 4. Context Manager (`src/core/context.py`)

Mantiene estado compartido entre nodos durante ejecución.

**Funcionalidades**:
- Store/retrieve datos con dot notation: `context.get('email.subject')`
- Checkpoints para rollback
- Histórico de cambios
- JSON serialization para persistencia

**Validación**:
- Detecta objetos no serializables (bytes, Python objects)
- Fuerza conversion a primitivos (str, int, float, bool, list, dict)
- Previene errores de persistencia

---

### 5. Chain of Work (`src/models/chain_of_work.py`)

Sistema de auditoría que registra cada paso de ejecución en PostgreSQL.

**Registra**:
- `node_id`: Nodo ejecutado
- `code_executed`: Código Python ejecutado (o prompt si es AI)
- `input_context`: Contexto antes de ejecución
- `output_result`: Resultado después de ejecución
- `execution_time_ms`: Duración en milisegundos
- `status`: success / failed
- `error_message`: Si falló, mensaje de error
- `ai_metadata`: Si CachedExecutor, logs de AI (tokens, cost, prompts)

**Query de auditoría**:
```sql
SELECT node_id, execution_time_ms, status, ai_metadata
FROM chain_of_work
WHERE execution_id = 'exec_123'
ORDER BY created_at;
```

---

### 6. Credentials Management (`src/models/credentials.py`)

Sistema multi-tenant para gestionar credenciales por cliente.

**Tablas**:
- `clients`: Clientes (client_slug único)
- `client_email_credentials`: IMAP/SMTP por cliente
- `client_database_credentials`: PostgreSQL por cliente

**Auto-loading**: Cuando ejecutas un workflow con `client_slug`, las credenciales se inyectan automáticamente en el contexto inicial.

---

## 🔄 Flujo de Ejecución

```
1. API recibe petición: POST /workflows/{id}/execute
   └─> Body: {"client_slug": "idom"}

2. Load credentials from DB based on client_slug
   └─> Email credentials + Database credentials → initial_context

3. Load workflow definition from PostgreSQL
   └─> Parse JSON → Create Node objects

4. Validate graph structure
   └─> Check: single start, valid edges, no orphan nodes, no cycles

5. Create Execution record in DB
   └─> Store: workflow_id, client_slug, status=running

6. Execute workflow node by node:

   FOR EACH node in topological order:

   a. Context Manager provides current context

   b. Executor executes node:
      - E2BExecutor: Runs hardcoded Python code
      - CachedExecutor: Generates code with AI → Runs in E2B

   c. E2B Cloud Sandbox runs code in isolated container
      └─> Timeout: 60s, RAM: 5GB, CPU: 1 core

   d. Result merged into context

   e. Chain of Work records step (node_id, code, input, output, time)

   f. If DecisionNode: determine next node based on branch_decision

   g. Continue to next node

7. Workflow completes:
   └─> Update Execution: status=completed, end_time, final_context

8. Return result via API
```

---

## 📊 Estructura de Datos

### Workflow Definition (PostgreSQL `workflows` table)

```json
{
  "id": 1,
  "name": "Invoice Processing V3",
  "description": "Process invoices from email with PDF attachments",
  "graph_definition": {
    "nodes": [
      {
        "id": "start",
        "type": "start"
      },
      {
        "id": "read_email",
        "type": "action",
        "executor": "e2b",
        "code": "import imaplib\n...",
        "timeout": 30
      },
      {
        "id": "has_pdf_decision",
        "type": "decision",
        "code": "context['branch_decision'] = context.get('has_pdf', False)"
      }
    ],
    "edges": [
      {"from": "start", "to": "read_email"},
      {"from": "read_email", "to": "has_pdf_decision"},
      {"from": "has_pdf_decision", "to": "extract_pdf", "condition": true},
      {"from": "has_pdf_decision", "to": "reject", "condition": false}
    ]
  }
}
```

### Execution Context (Runtime)

```python
{
  # Auto-injected credentials
  "imap_host": "imap.gmail.com",
  "imap_port": 993,
  "email_user": "user@example.com",
  "email_password": "***",
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "db_host": "postgres.railway.app",
  "db_name": "facturas",

  # Workflow results
  "has_emails": True,
  "email_from": "sender@example.com",
  "email_subject": "Invoice #12345",
  "has_pdf": True,
  "pdf_data_b64": "JVBERi0xLjQK...",
  "ocr_text": "FACTURA\nTotal: 850.00 EUR",
  "total_amount": 850.0,
  "invoice_id": 42
}
```

### Chain of Work Entry (PostgreSQL)

**Ejemplo: Ejecución exitosa**
```json
{
  "id": 123,
  "execution_id": 42,
  "node_id": "extract_pdf",
  "node_type": "action",
  "code_executed": "import base64\nimport fitz\n...",
  "input_context": {"has_pdf": true, "pdf_data_b64": "..."},
  "output_result": {"ocr_text": "FACTURA\nTotal: 850.00 EUR", "pdf_pages": 2},
  "execution_time_ms": 2340,
  "status": "success",
  "ai_metadata": {
    "model": "gpt-4o-mini",
    "prompt": "Decode PDF from base64...",
    "generated_code": "import base64\nimport fitz\n...",
    "tokens_input": 7500,
    "tokens_output": 450,
    "cost_usd": 0.001125,
    "attempts": 1,
    "cache_hit": false
  }
}
```

**Ejemplo: Ejecución fallida tras 3 intentos** (⭐ Nueva funcionalidad de debugging)
```json
{
  "id": 124,
  "execution_id": 42,
  "node_id": "extract_text_from_pdf",
  "node_type": "action",
  "code_executed": "import fitz\nimport base64\n# Código generado en intento 3...",
  "input_context": {"pdf_data": "JVBERi0...", "recommended_method": "ocr"},
  "output_result": {"pdf_data": "JVBERi0...", "recommended_method": "ocr"},
  "execution_time_ms": 0,
  "status": "failed",
  "error_message": "Failed after 3 attempts. Last error: ValidationError(...)",
  "ai_metadata": {
    "model": "gpt-4o-mini",
    "attempts": 3,
    "status": "failed_after_retries",
    "final_error": "ValidationError: Code executed but produced EMPTY output",
    "all_attempts": [
      {
        "attempt": 1,
        "code": "import fitz\nimport base64\n# Primera versión (sin conversión a imagen)...",
        "error": "ValidationError: Code executed but produced EMPTY output"
      },
      {
        "attempt": 2,
        "code": "import fitz\nfrom PIL import Image\n# Segunda versión (timeout)...",
        "error": "E2BTimeoutError: Execution exceeded 30s"
      },
      {
        "attempt": 3,
        "code": "import fitz\nimport easyocr\n# Tercera versión (con OCR)...",
        "error": "CodeExecutionError: SyntaxError on line 15"
      }
    ]
  }
}
```

**Beneficios del debugging mejorado:**
- ✅ **Visibilidad total**: Nunca se pierde código generado, incluso si falla
- ✅ **Evolución del código**: Ver cómo la IA mejoró el código entre intentos
- ✅ **Análisis de errores**: Identificar patrones de fallos para mejorar prompts
- ✅ **Post-mortem debugging**: Reproducir y corregir fallos pasados

---

## 🎯 Ejemplo Completo: Invoice Processing

### Workflow como Grafo

```
Start
  │
  ├─→ Read Email from IMAP (ActionNode)
  │   └─→ Extract: from, subject, attachments
  │
  ├─→ [Decision: Has PDF?] (DecisionNode)
      │
      ├─→ YES
      │   │
      │   ├─→ Extract Text from PDF (ActionNode)
      │   │   └─→ Use PyMuPDF to extract text
      │   │
      │   ├─→ Find Total Amount (ActionNode)
      │   │   └─→ Regex: find €xxx.xx or xxx EUR
      │   │
      │   ├─→ [Decision: Amount > €1000?] (DecisionNode)
      │       │
      │       ├─→ YES → Send High Budget Email (ActionNode)
      │       │         └─→ SMTP: notify requires approval
      │       │
      │       └─→ NO → Send Low Budget Email (ActionNode)
      │                 └─→ SMTP: notify auto-approved
      │
      └─→ NO → Send Rejection Email (ActionNode)
              └─→ SMTP: explain missing PDF

  → Save to Database (ActionNode)
    └─→ PostgreSQL: INSERT invoice data

  → End
```

### Código con E2BExecutor (Phase 1)

```python
{
  "id": "read_email",
  "type": "action",
  "executor": "e2b",
  "code": """
import imaplib
import email
import base64

mail = imaplib.IMAP4_SSL(context['imap_host'], context['imap_port'])
mail.login(context['email_user'], context['email_password'])
mail.select('INBOX')

status, messages = mail.search(None, 'UNSEEN')
email_ids = messages[0].split()

if email_ids:
    email_id = email_ids[0]
    status, msg_data = mail.fetch(email_id, '(RFC822)')
    msg = email.message_from_bytes(msg_data[0][1])

    context['email_from'] = msg.get('From')
    context['email_subject'] = msg.get('Subject')

    # Extract PDF attachment
    for part in msg.walk():
        if part.get_filename() and part.get_filename().endswith('.pdf'):
            pdf_bytes = part.get_payload(decode=True)
            context['pdf_data_b64'] = base64.b64encode(pdf_bytes).decode()
            context['has_pdf'] = True
            break
else:
    context['has_pdf'] = False

mail.logout()
""",
  "timeout": 30
}
```

### Código con CachedExecutor (Phase 2)

```python
{
  "id": "read_email",
  "type": "action",
  "executor": "cached",
  "prompt": "Connect to IMAP server and read the first unread email. Extract From, Subject, and any PDF attachment (encode to base64). Mark email as read.",
  "timeout": 30
}
```

**KnowledgeManager** detecta "IMAP", "PDF", "base64" → Inyecta docs de `imap.md` y `pdf.md` en el prompt → OpenAI genera código → E2B ejecuta.

---

## 🔮 Evolución: Phase 1 → Phase 2

### Phase 1: Código Estático ✅
- Workflows con código **hardcodeado** en JSON
- E2BExecutor ejecuta código tal cual
- Útil para workflows bien definidos
- Control total sobre el código ejecutado

### Phase 2: AI Code Generation 🟡
- Workflows con **prompts en lenguaje natural**
- CachedExecutor genera código con OpenAI GPT-4o-mini
- Error retry automático con feedback
- Context-aware prompts (KnowledgeManager)
- Útil para workflows dinámicos y exploratorios

### Phase 3: Cache & Learning (Futuro) 🔮
- Hash-based cache de código generado
- Semantic cache con embeddings
- Learning from successful executions
- Human-in-the-loop approval
- Cost optimization (evitar regenerar código idéntico)

**Nota**: La arquitectura soporta ambas estrategias sin refactoring. Puedes mezclar E2BExecutor y CachedExecutor en el mismo workflow.

---

## 📝 Decisiones de Diseño

### ¿Por qué Grafos desde el Inicio?

Empezamos directamente con grafos condicionales (DecisionNodes), no con flujos lineales simples.

**Ventaja**: Más flexible desde el principio, no requiere refactoring posterior.

**Trade-off**: Más complejo de implementar inicialmente, pero vale la pena.

---

### ¿Por qué E2B Cloud en vez de Hetzner VM?

**E2B Pros**:
- ✅ Network access out-of-the-box (IMAP, SMTP, APIs)
- ✅ Zero infrastructure maintenance
- ✅ Pre-installed libraries (PyMuPDF, pandas)
- ✅ Resource limits automáticos
- ✅ $0 durante desarrollo (free credits)
- ✅ Custom templates (cold start 5x más rápido)

**Hetzner Contras**:
- ❌ Requiere configurar whitelist de dominios
- ❌ Mantener VM + Docker manualmente
- ❌ Sin network access (limitante para workflows reales)

**Decisión**: E2B es mejor fit para NOVA. Ver `/decisiones-tecnologia/ALTERNATIVAS.md` para análisis completo.

---

### ¿Por qué Código en PostgreSQL?

Los workflows (incluyendo código Python) se almacenan en PostgreSQL como JSON.

**Ventajas**:
- Editar workflows sin redesplegar aplicación
- Versionar workflows (crear nueva row con mismo `name`)
- Auditoría completa del código ejecutado (Chain of Work)
- Cargar workflows via API REST

**Desventaja**: Código no está en archivos `.py` tradicionales, sino en JSON.

---

### ¿Por qué Monolito Modular?

Aunque se despliega como un solo servicio en Railway, el código está organizado en módulos independientes (`/api`, `/core`, `/models`, `/workers`).

**Ventaja**: Fácil de separar en microservicios si escala.

**Trade-off**: Por ahora, más simple de mantener como monolito.

---

## 🚀 Setup y Deployment

### Setup Local

1. **Instalar dependencias**:
```bash
cd /nova
pip install -r requirements.txt
```

2. **Configurar E2B**:
```bash
# Crear cuenta: https://e2b.dev (gratis, $100 credits)
export E2B_API_KEY=e2b_...tu_api_key
export E2B_TEMPLATE_ID=wzqi57u2e8v2f90t6lh5
```

3. **Configurar PostgreSQL y Redis**:
```bash
export DATABASE_URL=postgresql://user:pass@host:5432/nova
export REDIS_URL=redis://host:6379
```

4. **Ejecutar migraciones**:
```bash
alembic upgrade head
```

5. **Ejecutar API**:
```bash
uvicorn src.api.main:app --reload
```

6. **Ejecutar Worker** (opcional):
```bash
celery -A src.workers.tasks worker --loglevel=info
```

---

### Deployment en Railway

Ver `/nova/DEPLOYMENT.md` para guía completa.

**Resumen**:
1. Crear proyecto Railway
2. Agregar PostgreSQL y Redis
3. Configurar variables de entorno (`E2B_API_KEY`, `E2B_TEMPLATE_ID`)
4. Conectar GitHub repo
5. Railway auto-deploya desde `main` branch
6. Ejecutar migraciones en production

---

## 📚 Documentación Adicional

- **Decisiones técnicas**: `/decisiones-tecnologia/ALTERNATIVAS.md`
- **Caso de uso Invoice Processing**: `WORKFLOW-FACTURAS.md`
- **AI Executor detallado**: `ARQUITECTURA-AIEXECUTOR.md`
- **Context management para AI**: `CONTEXT-SUMMARY-AI-EXECUTORS.md`
- **Backlog de features**: `/futuro/BACKLOG.md`

---

## 🔑 Testing

### Test Suite

```bash
# Ejecutar todos los tests
pytest

# Test específico
pytest tests/core/test_graph_engine.py

# Coverage
pytest --cov=src
```

**202 tests implementados** cubriendo:
- Graph Engine validation y execution
- E2BExecutor y CachedExecutor
- Context Manager
- Nodes (ActionNode, DecisionNode)
- KnowledgeManager
- Integration tests E2E

---

## 📊 Métricas y Monitoreo

### Health Check

```bash
GET /health
```

Verifica:
- PostgreSQL connection
- Redis connection
- E2B sandbox availability

### Chain of Work Analytics

```sql
-- Tiempo promedio por nodo
SELECT node_id, AVG(execution_time_ms) as avg_time_ms
FROM chain_of_work
WHERE status = 'success'
GROUP BY node_id;

-- Tasa de éxito por workflow
SELECT w.name,
       COUNT(*) as total_executions,
       SUM(CASE WHEN e.status = 'completed' THEN 1 ELSE 0 END) as successful,
       ROUND(100.0 * SUM(CASE WHEN e.status = 'completed' THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
FROM executions e
JOIN workflows w ON e.workflow_id = w.id
GROUP BY w.name;

-- AI cost tracking (Phase 2)
SELECT
    DATE(created_at) as date,
    SUM((ai_metadata->>'tokens_used')::int) as total_tokens,
    SUM((ai_metadata->>'estimated_cost')::float) as total_cost_usd
FROM chain_of_work
WHERE ai_metadata IS NOT NULL
GROUP BY DATE(created_at);
```

---

*Última actualización: 7 Noviembre 2025*
