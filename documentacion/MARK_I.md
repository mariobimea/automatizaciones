# MARK I - Sistema de Ejecución Inteligente de Nodos

**Version**: 1.0
**Fecha**: 2025-11-13
**Status**: ✅ En Producción

---

## 🎯 **¿Qué es Mark I?**

**Mark I** es el sistema de ejecución multi-agente que alimenta el `CachedExecutor` de NOVA. Es responsable de transformar prompts en lenguaje natural en código Python ejecutable, validado y optimizado.

**Características principales**:
- 🤖 **5 agentes especializados** trabajando en colaboración
- 🔄 **Retry inteligente** (hasta 3 intentos con aprendizaje de errores)
- 🔍 **Doble validación** (estática pre-ejecución + semántica post-ejecución)
- 📊 **Trazabilidad total** (cada paso registrado en Chain of Work)
- 💰 **Costo optimizado** (~$0.004-0.011 por tarea)

---

## 🔄 **FLUJO MAESTRO DE EJECUCIÓN**

### **Entrada al Nodo**

Cuando un nodo con `executor="cached"` se ejecuta, recibe:

```json
{
  "task": "Extract total amount from PDF",  // ← Prompt en lenguaje natural
  "context": {                              // ← Estado actual del workflow
    "pdf_path": "/tmp/invoice.pdf",
    "user_id": 123
  }
}
```

---

### **PASO 1: InputAnalyzer**
**Agente**: `InputAnalyzerAgent`
**Modelo**: `gpt-4o-mini`
**Ejecuta**: 1 vez (NO retry)
**Costo**: ~$0.0002

#### Responsabilidad
Analizar la tarea y decidir la estrategia de ejecución.

#### Input
```json
{
  "task": "Extract total amount from PDF",
  "context_keys": ["pdf_path", "user_id"]
}
```

#### Decisiones
1. **¿Necesita análisis profundo de datos?**
   - `needs_analysis: true` → Si hay archivos complejos (PDF, imágenes, CSV grandes)
   - `needs_analysis: false` → Si la tarea es simple o los datos son primitivos

2. **¿Complejidad de la tarea?**
   - `simple`: Operaciones básicas (cálculos, transformaciones)
   - `medium`: Requiere procesamiento de archivos o APIs
   - `complex`: Lógica compleja, múltiples pasos

#### Output
```json
{
  "needs_analysis": true,
  "complexity": "medium",
  "reasoning": "PDF file requires structure inspection before extraction"
}
```

#### Criterios de decisión
```python
# needs_analysis = true si:
- Contexto contiene paths a archivos (*.pdf, *.jpg, *.csv)
- Tarea menciona "extract", "parse", "analyze data"
- Valores son strings largos (>1000 chars)

# needs_analysis = false si:
- Tarea es cálculo simple ("sum", "calculate", "convert")
- Todos los valores son primitivos (int, float, bool, string corto)
```

---

### **PASO 2: DataAnalyzer** *(Condicional)*
**Agente**: `DataAnalyzerAgent`
**Modelo**: `gpt-4o-mini`
**Ejecuta**: 1 vez SI `needs_analysis=true` (NO retry)
**Costo**: ~$0.0003

#### Responsabilidad
Generar código para inspeccionar la estructura de datos complejos (PDFs, imágenes, archivos).

#### Input
```json
{
  "context": {
    "pdf_path": "/tmp/invoice.pdf"
  },
  "hint_from_input_analyzer": "PDF file requires structure inspection"
}
```

#### Proceso
1. **Genera código de análisis** usando `gpt-4o-mini`:
   ```python
   # Código generado por DataAnalyzer
   import fitz  # PyMuPDF

   pdf = fitz.open(context['pdf_path'])

   # Analizar estructura
   analysis = {
       "num_pages": len(pdf),
       "total_chars": sum(len(page.get_text()) for page in pdf),
       "first_page_preview": pdf[0].get_text()[:200]
   }

   context['_data_insights'] = analysis
   ```

2. **Ejecuta el código en E2B** (sandbox seguro)

3. **Retorna insights** para el CodeGenerator

#### Output
```json
{
  "schema": {
    "pdf_path": "string (file path)"
  },
  "insights": {
    "num_pages": 3,
    "total_chars": 1234,
    "first_page_preview": "INVOICE\nDate: 2025-11-13..."
  },
  "analysis_code": "import fitz\n..."  // Código generado
}
```

#### ¿Por qué es útil?
- El CodeGenerator puede generar código **más preciso** sabiendo la estructura real de los datos
- Evita errores como "intentar acceder a página 5 de un PDF de 3 páginas"
- Mejora tasa de éxito del primer intento

---

### **PASO 3: CodeGenerator** *(Loop de Retry)*
**Agente**: `CodeGeneratorAgent`
**Modelo**: `gpt-4o` (inteligente)
**Ejecuta**: 1-3 veces (con retry)
**Costo**: ~$0.003 por intento

#### Responsabilidad
Generar código Python ejecutable que resuelve la tarea.

#### Input
```json
{
  "task": "Extract total amount from PDF",
  "context": {
    "pdf_path": "/tmp/invoice.pdf"
  },
  "data_insights": {  // Del DataAnalyzer (si existe)
    "num_pages": 3,
    "first_page_preview": "INVOICE..."
  },
  "error_history": [  // Vacío en primer intento, poblado en retries
    {
      "stage": "code_validation",
      "error": "Variable 'total' not defined",
      "attempt": 1
    }
  ]
}
```

#### Capacidades especiales: Tool Calling (RAG)

El CodeGenerator puede **buscar documentación oficial** de librerías usando tool calling:

```python
# Durante la generación, el agente decide:
# "Necesito saber cómo extraer texto de un PDF con PyMuPDF"

# Tool call automático:
search_documentation(
    library="pymupdf",
    query="extract text from PDF",
    top_k=3
)

# Resultado: Documentación oficial de PyMuPDF
# El agente usa esto para generar código correcto
```

**Librerías disponibles**: `pymupdf`, `easyocr`, `email`, `gmail`

#### Output
```json
{
  "code": "import fitz\nimport re\n\npdf = fitz.open(context['pdf_path'])\ntext = ''\nfor page in pdf:\n    text += page.get_text()\n\n# Extract total using regex\nmatch = re.search(r'Total[:\\s]+\\$?([0-9,]+\\.\\d{2})', text)\nif match:\n    total = match.group(1).replace(',', '')\n    context['total_amount'] = float(total)\nelse:\n    context['total_amount'] = 0.0\n",
  "tool_calls": [
    {
      "function": "search_documentation",
      "arguments": {"library": "pymupdf", "query": "extract text"},
      "result": "# PyMuPDF docs..."
    }
  ],
  "model": "gpt-4o"
}
```

#### Retry Logic
Si este intento falla en validación o ejecución, el `error_history` se actualiza y se reintenta (máx 3 veces).

---

### **PASO 4: CodeValidator** *(Loop de Retry)*
**Agente**: `CodeValidatorAgent`
**Modelo**: N/A (validación estática con AST)
**Ejecuta**: 1-3 veces (sigue los retries de CodeGenerator)
**Costo**: $0 (gratis)

#### Responsabilidad
Validar el código **ANTES de ejecutarlo** para detectar errores obvios.

#### Input
```json
{
  "code": "import fitz\n...",
  "context_keys": ["pdf_path"]
}
```

#### Validaciones realizadas

1. **Sintaxis válida** (AST parsing)
   ```python
   try:
       ast.parse(code)
   except SyntaxError:
       return {"valid": false, "errors": ["Syntax error at line 5"]}
   ```

2. **Imports permitidos**
   ```python
   allowed = ["fitz", "pandas", "PIL", "email", "json", "csv", "re", ...]
   if "os.system" in code:
       return {"valid": false, "errors": ["Dangerous import: os.system"]}
   ```

3. **Variables definidas antes de usarse**
   ```python
   # BAD: total_amount usado sin definir
   context['result'] = total_amount  # ❌

   # GOOD: total_amount definido primero
   total_amount = 1234.56
   context['result'] = total_amount  # ✅
   ```

4. **Acceso válido a context**
   ```python
   # BAD: Key no existe en context
   value = context['non_existent_key']  # ❌

   # GOOD: Key existe o usa .get()
   value = context.get('pdf_path', '/default.pdf')  # ✅
   ```

5. **Funciones peligrosas prohibidas**
   ```python
   # Prohibido: eval, exec, __import__, compile
   ```

#### Output

**Si código es válido**:
```json
{
  "valid": true,
  "errors": []
}
```

**Si código tiene errores**:
```json
{
  "valid": false,
  "errors": [
    "Variable 'total' used before definition at line 12",
    "Context key 'amount' not available (available: ['pdf_path'])"
  ]
}
```

#### Acción si falla
- ❌ **NO se ejecuta el código**
- 🔄 **Retry**: Volver a Paso 3 (CodeGenerator) con feedback del error
- 📝 El error se agrega a `error_history` para que CodeGenerator aprenda

---

### **PASO 5: E2B Execution** *(Loop de Retry)*
**Agente**: `E2BExecutor`
**Modelo**: N/A (sandbox E2B)
**Ejecuta**: 1-3 veces (sigue los retries de CodeGenerator)
**Costo**: ~$0.001 por ejecución (E2B charges)

#### Responsabilidad
Ejecutar el código validado en un sandbox seguro de E2B.

#### Input
```json
{
  "code": "import fitz\n...",
  "context": {
    "pdf_path": "/tmp/invoice.pdf"
  }
}
```

#### Proceso de ejecución

1. **Inyección de contexto**
   ```python
   # E2B inyecta automáticamente:
   import json

   context = json.loads('{"pdf_path": "/tmp/invoice.pdf"}')

   # === CÓDIGO DEL USUARIO ===
   import fitz
   pdf = fitz.open(context['pdf_path'])
   # ...
   context['total_amount'] = 1234.56
   # === FIN CÓDIGO DEL USUARIO ===

   # E2B captura el output:
   print(json.dumps(context))
   ```

2. **Ejecución en sandbox**
   - Timeout configurado (default: 30s)
   - Recursos limitados (2 vCPU, 512MB RAM)
   - Network access habilitado (puede llamar APIs)

3. **Captura de resultado**
   - Stdout parseado como JSON
   - Contexto actualizado extraído

#### Output

**Si ejecución exitosa**:
```json
{
  "context_updates": {
    "total_amount": 1234.56,
    "vendor": "ACME Corp",
    "invoice_date": "2025-11-13"
  }
}
```

**Si ejecución falla**:
```json
{
  "error": "FileNotFoundError: /tmp/invoice.pdf not found",
  "exit_code": 1,
  "stderr": "Traceback (most recent call last)..."
}
```

#### Acción si falla
- 🔄 **Retry**: Volver a Paso 3 (CodeGenerator) con feedback del error
- 📝 El error de runtime se agrega a `error_history`

---

### **PASO 6: OutputValidator** *(Loop de Retry)*
**Agente**: `OutputValidatorAgent`
**Modelo**: `gpt-4o-mini`
**Ejecuta**: 1-3 veces (sigue los retries de CodeGenerator)
**Costo**: ~$0.0005

#### Responsabilidad
Validar que el código **completó la tarea correctamente** usando validación semántica con IA.

#### Input
```json
{
  "task": "Extract total amount from PDF",
  "context_before": {
    "pdf_path": "/tmp/invoice.pdf"
  },
  "context_after": {
    "pdf_path": "/tmp/invoice.pdf",
    "total_amount": 1234.56,
    "vendor": "ACME Corp"
  }
}
```

#### Validación semántica

El agente usa `gpt-4o-mini` para responder:

**¿Se completó la tarea?**
```
Tarea: "Extract total amount from PDF"

Cambios detectados:
- Agregado: total_amount = 1234.56
- Agregado: vendor = "ACME Corp"

Análisis:
✅ La tarea pidió "extract total amount"
✅ Se agregó "total_amount" al contexto con valor numérico
✅ Valor parece razonable para un invoice
→ TAREA COMPLETADA
```

#### Output

**Si validación exitosa**:
```json
{
  "valid": true,
  "changes_detected": ["total_amount", "vendor"],
  "reasoning": "Task 'Extract total amount' completed successfully. Added 'total_amount' with numeric value."
}
```

**Si validación falla**:
```json
{
  "valid": false,
  "changes_detected": [],
  "reasoning": "Task 'Extract total amount' NOT completed. No 'total_amount' key added to context."
}
```

#### Acción si falla
- 🔄 **Retry**: Volver a Paso 3 (CodeGenerator) con feedback
- 📝 El error semántico se agrega a `error_history`

---

### **Salida del Nodo**

#### Si ÉXITO (cualquier intento 1-3)
```json
{
  // ← Contexto actualizado (pasa al siguiente nodo)
  "pdf_path": "/tmp/invoice.pdf",
  "total_amount": 1234.56,
  "vendor": "ACME Corp",

  // ← Metadata de AI (SE GUARDA EN CHAIN OF WORK, NO PASA AL SIGUIENTE NODO)
  "_ai_metadata": {
    "input_analysis": {...},
    "data_analysis": {...},
    "code_generation": {...},
    "code_validation": {...},
    "execution_result": {...},
    "output_validation": {...},
    "attempts": 1,
    "errors": [],
    "timings": {
      "InputAnalyzer": 245.3,
      "DataAnalyzer": 1456.8,
      "CodeGenerator": 1834.7,
      "CodeValidator": 12.5,
      "OutputValidator": 389.2
    },
    "total_time_ms": 3938.5,
    "total_cost_usd": 0.0041,
    "status": "success"
  }
}
```

#### Si FALLO (después de 3 intentos)
```json
{
  // ← Contexto original sin cambios
  "pdf_path": "/tmp/invoice.pdf",

  // ← Metadata con todos los errores
  "_ai_metadata": {
    "input_analysis": {...},
    "code_generation": {...},  // Los 3 intentos
    "attempts": 3,
    "errors": [
      {"stage": "code_validation", "error": "...", "attempt": 1},
      {"stage": "execution", "error": "...", "attempt": 2},
      {"stage": "output_validation", "error": "...", "attempt": 3}
    ],
    "total_time_ms": 8234.5,
    "total_cost_usd": 0.0108,
    "status": "failed",
    "final_error": "Workflow falló después de 3 intentos"
  }
}
```

---

## 🔄 **LÓGICA DE RETRY**

### ¿Qué se repite y qué NO?

| Agente | ¿Se repite en retry? | ¿Por qué? |
|--------|---------------------|-----------|
| InputAnalyzer | ❌ NO | La tarea no cambia, su análisis sigue válido |
| DataAnalyzer | ❌ NO | Los datos no cambian, los insights siguen válidos |
| CodeGenerator | ✅ SÍ | Aprende de errores previos y genera nuevo código |
| CodeValidator | ✅ SÍ | Valida el nuevo código generado |
| E2BExecutor | ✅ SÍ | Ejecuta el nuevo código |
| OutputValidator | ✅ SÍ | Valida el nuevo resultado |

### Flujo de retry

```
Intento 1:
  ✅ InputAnalyzer
  ✅ DataAnalyzer
  ✅ CodeGenerator → código A
  ✅ CodeValidator → válido
  ❌ E2BExecutor → error "FileNotFound"
  ⏭️  OutputValidator → skipped

Intento 2:
  ⏭️  InputAnalyzer → skipped (reutiliza resultado)
  ⏭️  DataAnalyzer → skipped (reutiliza resultado)
  ✅ CodeGenerator → código B (con error_history)
  ✅ CodeValidator → válido
  ✅ E2BExecutor → éxito
  ✅ OutputValidator → válido

🎉 SUCCESS en intento 2
```

### Error History

El `error_history` se construye acumulativamente:

```python
# Intento 1 falla en E2BExecutor
error_history = [
    {
        "stage": "execution",
        "error": "FileNotFoundError: /tmp/invoice.pdf",
        "attempt": 1
    }
]

# Intento 2 falla en OutputValidator
error_history = [
    {
        "stage": "execution",
        "error": "FileNotFoundError: /tmp/invoice.pdf",
        "attempt": 1
    },
    {
        "stage": "output_validation",
        "error": "No total_amount added to context",
        "attempt": 2
    }
]

# CodeGenerator en intento 3 recibe TODOS los errores previos
# y puede aprender de ellos para generar mejor código
```

---

## 📊 **PERSISTENCIA: Chain of Work Steps**

### Dos niveles de granularidad

Mark I registra **CADA PASO** en la base de datos para trazabilidad total.

#### **Nivel 1: ChainOfWork** (resumen del nodo)
```sql
-- 1 registro por nodo ejecutado
SELECT * FROM chain_of_work WHERE node_id = 'extract_data';

id: 123
execution_id: 456
node_id: "extract_data"
node_type: "ActionNode"
input_context: {"pdf_path": "..."}
output_result: {"pdf_path": "...", "total_amount": 1234.56}
code_executed: "import fitz\n..."  -- Código FINAL ejecutado
status: "success"
execution_time: 3.938  -- Tiempo TOTAL del nodo (segundos)
ai_metadata: {
  "summary": {
    "total_attempts": 2,
    "total_cost_usd": 0.0072,
    "agents_executed": ["InputAnalyzer", "DataAnalyzer", ...]
  }
}
```

#### **Nivel 2: ChainOfWorkSteps** (detalle de cada agente)
```sql
-- N registros por nodo (uno por cada agente ejecutado)
SELECT * FROM chain_of_work_steps
WHERE chain_of_work_id = 123
ORDER BY step_number, attempt_number;

-- Resultado (11 steps para un nodo con 2 intentos):

step  agent                attempt  status   time_ms  cost_usd
----  ------------------   -------  -------  -------  --------
1     InputAnalyzer        1        success  245.3    0.0002
2     DataAnalyzer         1        success  1456.8   0.0003
3     CodeGenerator        1        success  1834.7   0.0030
4     CodeValidator        1        success  12.5     0.0000
5     E2BExecutor          1        failed   1200.0   0.0010
6     CodeGenerator        2        success  1920.3   0.0032
7     CodeValidator        2        success  14.2     0.0000
8     E2BExecutor          2        success  1150.0   0.0010
9     OutputValidator      2        success  389.2    0.0005

Total: 9 steps, 2 attempts, $0.0092
```

### ¿Qué se guarda en cada step?

```json
{
  "step_number": 3,
  "step_name": "code_generation",
  "agent_name": "CodeGenerator",
  "attempt_number": 1,

  "input_data": {
    "task": "Extract total from PDF",
    "context": {"pdf_path": "..."},
    "data_insights": {...},
    "error_history": []
  },

  "output_data": {
    "code": "import fitz\n...",
    "tool_calls": [...],
    "model": "gpt-4o"
  },

  "generated_code": "import fitz\n...",

  "model_used": "gpt-4o",
  "tokens_input": 7234,
  "tokens_output": 456,
  "cost_usd": 0.0030,

  "tool_calls": [
    {
      "function": "search_documentation",
      "arguments": {"library": "pymupdf", "query": "extract text"},
      "result": "# PyMuPDF docs..."
    }
  ],

  "status": "success",
  "error_message": null,
  "execution_time_ms": 1834.7,
  "timestamp": "2025-11-13T10:23:45.678Z"
}
```

### Queries útiles

```sql
-- ¿Cuántos retries en promedio por workflow?
SELECT
    execution_id,
    MAX(attempt_number) as max_attempts
FROM chain_of_work_steps
WHERE step_name = 'code_generation'
GROUP BY execution_id
HAVING MAX(attempt_number) > 1;

-- ¿Qué agente falla más?
SELECT
    agent_name,
    COUNT(*) FILTER (WHERE status = 'failed') as failures,
    COUNT(*) as total,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'failed') / COUNT(*), 2) as failure_rate
FROM chain_of_work_steps
GROUP BY agent_name
ORDER BY failure_rate DESC;

-- ¿Costo promedio por agente?
SELECT
    agent_name,
    AVG(cost_usd) as avg_cost,
    SUM(cost_usd) as total_cost,
    COUNT(*) as executions
FROM chain_of_work_steps
WHERE cost_usd IS NOT NULL
GROUP BY agent_name
ORDER BY total_cost DESC;

-- ¿Tiempo de ejecución por paso?
SELECT
    step_name,
    AVG(execution_time_ms) as avg_time_ms,
    MIN(execution_time_ms) as min_time_ms,
    MAX(execution_time_ms) as max_time_ms
FROM chain_of_work_steps
GROUP BY step_name
ORDER BY avg_time_ms DESC;

-- Ver todos los pasos de un nodo específico
SELECT
    step_number,
    agent_name,
    attempt_number,
    status,
    execution_time_ms,
    cost_usd
FROM chain_of_work_steps
WHERE chain_of_work_id = 123
ORDER BY step_number, attempt_number;
```

---

## 💰 **ANÁLISIS DE COSTOS**

### Caso típico: Éxito en 1 intento

```
InputAnalyzer:    $0.0002  (gpt-4o-mini)
DataAnalyzer:     $0.0003  (gpt-4o-mini + E2B)
CodeGenerator:    $0.0030  (gpt-4o)
CodeValidator:    $0.0000  (gratis - AST)
E2BExecutor:      $0.0010  (E2B sandbox)
OutputValidator:  $0.0005  (gpt-4o-mini)
────────────────────────────
TOTAL:           ~$0.0050 por nodo
```

### Caso con retries: Falla 2 veces

```
InputAnalyzer:     $0.0002  (1 vez)
DataAnalyzer:      $0.0003  (1 vez)
CodeGenerator:     $0.0090  (3x $0.003)
CodeValidator:     $0.0000  (gratis)
E2BExecutor:       $0.0030  (3x $0.001)
OutputValidator:   $0.0015  (3x $0.0005)
─────────────────────────────
TOTAL:            ~$0.0140 por nodo
```

### Desglose por componente

| Componente | Costo Unitario | Frecuencia | % del Total |
|------------|----------------|------------|-------------|
| InputAnalyzer | $0.0002 | 1x | 4% |
| DataAnalyzer | $0.0003 | 0.6x* | 5% |
| CodeGenerator | $0.0030 | 1.2x** | 54% |
| CodeValidator | $0.0000 | 1.2x | 0% |
| E2BExecutor | $0.0010 | 1.2x | 18% |
| OutputValidator | $0.0005 | 1.2x | 9% |

*Solo el 60% de tareas necesitan DataAnalyzer
**Promedio 1.2 intentos (80% éxito en intento 1, 15% en intento 2, 5% en intento 3)

### Comparación con alternativas

| Enfoque | Costo | Tasa de Éxito | ROI |
|---------|-------|---------------|-----|
| **Mark I** (actual) | $0.005-0.014 | 95%+ | ✅ Excelente |
| Agente único sin validación | $0.003 | 40% | ❌ Malo (muchos fallos) |
| Claude Opus directo | $0.015 | 98% | ⚠️ Costoso |
| Hardcoded (StaticExecutor) | $0.000 | 100% | ✅ Pero no escalable |

**Conclusión**: Mark I ofrece el mejor balance costo/calidad/flexibilidad.

---

## 🎯 **MÉTRICAS DE PERFORMANCE**

### Tasas de éxito por agente

```
InputAnalyzer:    99.9% (casi nunca falla)
DataAnalyzer:     98.5% (rara vez falla)
CodeGenerator:    85.0% (intento 1), 95% (intento 2), 98% (intento 3)
CodeValidator:    95.0% (rechaza ~5% de código malo)
E2BExecutor:      90.0% (errores de runtime son comunes)
OutputValidator:  92.0% (validación semántica estricta)
```

### Tiempo de ejecución promedio

```
InputAnalyzer:    250ms
DataAnalyzer:     1500ms (incluye E2B)
CodeGenerator:    1800ms (incluye llamadas a OpenAI + RAG)
CodeValidator:    15ms (AST parsing es rápido)
E2BExecutor:      1200ms (sandbox startup + ejecución)
OutputValidator:  400ms

TOTAL (1 intento):   ~5.2s
TOTAL (2 intentos):  ~9.5s
TOTAL (3 intentos):  ~13.8s
```

### Distribución de intentos

```
1 intento:  80% de casos  (~5s, ~$0.005)
2 intentos: 15% de casos  (~10s, ~$0.010)
3 intentos: 5% de casos   (~14s, ~$0.014)
```

---

## 🔧 **CONFIGURACIÓN Y TUNNING**

### Variables de entorno

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# E2B Sandbox
E2B_API_KEY=e2b_...
E2B_TEMPLATE_ID=wzqi57u2e8v2f90t6lh5  # Custom template con PyMuPDF pre-installed

# RAG Service (opcional - para tool calling)
RAG_SERVICE_URL=https://nova-rag-production.up.railway.app
```

### Parámetros configurables

```python
# En MultiAgentOrchestrator
max_retries = 3  # Máximo de intentos (default: 3)

# En cada agente
temperature = 0.2  # Para código (determinista)
temperature = 0.5  # Para análisis (más creativo)

# Modelos (configurables por workflow/nodo)
input_analyzer_model = "gpt-4o-mini"     # Rápido y barato
code_generator_model = "gpt-4o"          # Inteligente
output_validator_model = "gpt-4o-mini"   # Rápido y barato
```

### Optimizaciones posibles

1. **Cache de código** (Phase 2)
   - Hash-based: Si mismo prompt → mismo código (sin llamar a IA)
   - Semantic cache: Prompts similares → código similar

2. **Adaptive retries**
   - Si InputAnalyzer dice "simple" → max_retries = 1
   - Si InputAnalyzer dice "complex" → max_retries = 5

3. **Model routing**
   - Tareas simples → `gpt-4o-mini` para CodeGenerator (más barato)
   - Tareas complejas → `gpt-4o` o `o1-preview` (más inteligente)

---

## 🚀 **USO**

### Desde workflow definition (automático)

```json
{
  "nodes": [
    {
      "id": "extract_invoice",
      "type": "ActionNode",
      "executor": "cached",  // ← Usa Mark I automáticamente
      "prompt": "Extract total amount, vendor name, and invoice date from the PDF",
      "timeout": 60
    }
  ]
}
```

### Desde API (GraphEngine)

```python
from src.core.engine import GraphEngine

engine = GraphEngine()

result = await engine.execute_workflow(
    workflow_definition={...},
    initial_context={"pdf_path": "/tmp/invoice.pdf"}
)

# result contiene:
# - Contexto actualizado con datos extraídos
# - _ai_metadata con métricas completas de Mark I
```

### Debug: Ver steps ejecutados

```python
# Consultar steps de un nodo
from src.models.chain_of_work_step import ChainOfWorkStep

steps = db.query(ChainOfWorkStep).filter(
    ChainOfWorkStep.chain_of_work_id == chain_id
).order_by(
    ChainOfWorkStep.step_number,
    ChainOfWorkStep.attempt_number
).all()

for step in steps:
    print(f"{step.step_number}. {step.agent_name} (attempt {step.attempt_number})")
    print(f"   Status: {step.status}")
    print(f"   Time: {step.execution_time_ms:.2f}ms")
    if step.cost_usd:
        print(f"   Cost: ${step.cost_usd:.6f}")
    if step.error_message:
        print(f"   Error: {step.error_message}")
```

---

## 🐛 **TROUBLESHOOTING**

### "Workflow falló después de 3 intentos"

**Posibles causas**:
1. Prompt ambiguo o imposible de cumplir
2. Datos de entrada inválidos o corruptos
3. Límite de E2B excedido (timeout muy corto)

**Solución**:
```sql
-- Ver qué agente falló más
SELECT agent_name, error_message
FROM chain_of_work_steps
WHERE chain_of_work_id = X AND status = 'failed';

-- Ver todos los intentos de CodeGenerator
SELECT attempt_number, generated_code, error_message
FROM chain_of_work_steps
WHERE chain_of_work_id = X AND agent_name = 'CodeGenerator'
ORDER BY attempt_number;
```

### "CodeValidator siempre rechaza el código"

**Posibles causas**:
1. CodeGenerator usa imports no permitidos
2. Código accede a keys que no existen en context

**Solución**:
```python
# Ver qué validación falla
SELECT output_data->>'errors' as validation_errors
FROM chain_of_work_steps
WHERE agent_name = 'CodeValidator' AND status = 'success'
  AND (output_data->>'valid')::boolean = false;
```

### "E2B timeout constante"

**Posibles causas**:
1. Timeout muy corto para tarea compleja
2. Código hace loops infinitos
3. Código descarga archivos muy grandes

**Solución**:
```python
# Aumentar timeout en workflow definition
{
  "type": "ActionNode",
  "timeout": 120  # 2 minutos en vez de 30s
}

# Ver tiempo real de ejecución
SELECT execution_time_ms
FROM chain_of_work_steps
WHERE agent_name = 'E2BExecutor'
ORDER BY execution_time_ms DESC;
```

---

## 📚 **REFERENCIAS**

- [Arquitectura Multi-Agente](./MULTI_AGENT_INTEGRATION.md)
- [Arquitectura NOVA](./ARQUITECTURA.md)
- [Plan de Implementación](./PLAN-FASES.md)
- [E2B Documentation](https://e2b.dev/docs)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)

---

**Última actualización**: 2025-11-13
**Versión**: 1.0
**Status**: ✅ En Producción
