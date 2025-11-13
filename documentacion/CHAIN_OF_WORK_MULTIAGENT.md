# Chain of Work con Multi-Agente

## 📊 Qué se guarda en la base de datos

Cuando un workflow se ejecuta con la **arquitectura multi-agente**, cada nodo guarda información completa en la tabla `chain_of_work`.

---

## 🗄️ Estructura de la Tabla

```sql
CREATE TABLE chain_of_work (
    id INTEGER PRIMARY KEY,
    execution_id INTEGER,  -- FK a executions.id

    -- Identificación del nodo
    node_id VARCHAR(255),
    node_type VARCHAR(50),  -- "ActionNode", "DecisionNode", "StartNode", "EndNode"

    -- Ejecución
    code_executed TEXT,           -- Código Python ejecutado (generado por AI o hardcoded)
    input_context JSON,           -- Contexto ANTES de ejecutar
    output_result JSON,           -- Contexto DESPUÉS de ejecutar
    execution_time FLOAT,         -- Segundos que tardó en ejecutar
    status VARCHAR(50),           -- "success" o "failed"
    error_message TEXT,           -- Mensaje de error si falló
    timestamp DATETIME,

    -- Específico para DecisionNode
    decision_result VARCHAR(10),  -- "true" o "false"
    path_taken VARCHAR(255),      -- ID del siguiente nodo elegido

    -- ⭐ METADATA DE MULTI-AGENTE (NUEVO)
    ai_metadata JSON              -- Información completa de todos los agentes
);
```

---

## 🎯 Campo `ai_metadata` - Estructura Completa

Cuando un nodo usa `executor: "cached"` (multi-agente), el campo `ai_metadata` contiene:

```json
{
  // ═══════════════════════════════════════════════════════════
  // 1. INPUT ANALYZER - Decisión de estrategia
  // ═══════════════════════════════════════════════════════════
  "input_analysis": {
    "needs_analysis": false,           // ¿Necesita DataAnalyzer?
    "complexity": "simple",            // "simple" | "medium" | "complex"
    "reasoning": "Simple arithmetic"   // Por qué tomó esta decisión
  },

  // ═══════════════════════════════════════════════════════════
  // 2. DATA ANALYZER - Análisis de estructura (si needs_analysis=true)
  // ═══════════════════════════════════════════════════════════
  "data_analysis": {
    "type": "pdf",                     // Tipo de dato detectado
    "pages": 3,                        // Metadata extraída
    "has_text_layer": true,
    "file_size_kb": 256,
    "analysis_code": "import fitz..."  // Código que ejecutó para analizar
  },
  // O null si no se ejecutó

  // ═══════════════════════════════════════════════════════════
  // 3. CODE GENERATOR - Generación de código Python
  // ═══════════════════════════════════════════════════════════
  "code_generation": {
    "code": "import fitz\n...",        // Código generado
    "tool_calls": [],                  // Búsquedas de documentación (futuro)
    "generation_time_ms": 1234.5
  },

  // ═══════════════════════════════════════════════════════════
  // 4. CODE VALIDATOR - Validación estática (AST)
  // ═══════════════════════════════════════════════════════════
  "code_validation": {
    "valid": true,
    "errors": [],                      // Lista de errores encontrados
    "checks_passed": [                 // Validaciones que pasaron
      "syntax",
      "variables",
      "context_access",
      "imports",
      "functions"
    ]
  },

  // ═══════════════════════════════════════════════════════════
  // 5. E2B EXECUTION - Resultado de ejecutar el código
  // ═══════════════════════════════════════════════════════════
  "execution_result": {
    "status": "success"                // "success" | "error"
  },

  // ═══════════════════════════════════════════════════════════
  // 6. OUTPUT VALIDATOR - Validación semántica post-ejecución
  // ═══════════════════════════════════════════════════════════
  "output_validation": {
    "valid": true,
    "reason": "Task completed successfully",
    "changes_detected": [              // Qué keys se modificaron
      "invoice_total",
      "invoice_vendor"
    ]
  },

  // ═══════════════════════════════════════════════════════════
  // ORCHESTRATOR METADATA - Gestión de retries y errores
  // ═══════════════════════════════════════════════════════════
  "attempts": 1,                       // Cuántos intentos necesitó (1-3)
  "status": "success",                 // "success" | "failed"

  "errors": [                          // Historial de errores (si hubo retries)
    {
      "attempt": 1,
      "stage": "code_validation",
      "error": "Variable 'x' not defined"
    },
    {
      "attempt": 2,
      "stage": "output_validation",
      "error": "No changes detected in context"
    }
  ],

  "timings": {                         // Tiempo de cada agente (ms)
    "InputAnalyzer": 12.3,
    "DataAnalyzer": 45.6,              // Solo si se ejecutó
    "CodeGenerator": 1234.5,
    "CodeValidator": 5.2,
    "OutputValidator": 15.8
  },

  "total_time_ms": 1313.4,             // Tiempo total de orchestrator

  // ═══════════════════════════════════════════════════════════
  // FINAL ERROR (solo si status="failed")
  // ═══════════════════════════════════════════════════════════
  "final_error": "Failed after 3 attempts: Output validation failed"
}
```

---

## 📝 Ejemplo Real: Extracción de PDF

### Workflow Node Definition

```json
{
  "id": "extract_invoice",
  "type": "ActionNode",
  "executor": "cached",
  "prompt": "Extract total amount and vendor name from invoice PDF",
  "timeout": 60
}
```

### Chain of Work Entry (Éxito)

```json
{
  "id": 123,
  "execution_id": 45,
  "node_id": "extract_invoice",
  "node_type": "ActionNode",

  // Código ejecutado (generado por CodeGenerator)
  "code_executed": "import fitz\nimport re\n\npdf_bytes = base64.b64decode(context['pdf_data_b64'])\ndoc = fitz.open(stream=pdf_bytes, filetype='pdf')\n\ntext = ''\nfor page in doc:\n    text += page.get_text()\n\ntotal_match = re.search(r'Total:\\s*\\$([\\d,]+\\.\\d{2})', text)\nvendor_match = re.search(r'Vendor:\\s*(.+)', text)\n\ncontext['invoice_total'] = total_match.group(1) if total_match else None\ncontext['invoice_vendor'] = vendor_match.group(1).strip() if vendor_match else None",

  // Contexto ANTES
  "input_context": {
    "pdf_data_b64": "JVBERi0xLjQKJeLj...",
    "user_id": 123
  },

  // Contexto DESPUÉS
  "output_result": {
    "pdf_data_b64": "JVBERi0xLjQKJeLj...",
    "user_id": 123,
    "invoice_total": "1,234.56",
    "invoice_vendor": "ACME Corporation"
  },

  "execution_time": 2.345,
  "status": "success",
  "error_message": null,
  "timestamp": "2025-10-27T14:30:45",

  // METADATA DE MULTI-AGENTE
  "ai_metadata": {
    "input_analysis": {
      "needs_analysis": true,
      "complexity": "complex",
      "reasoning": "PDF data requires structure analysis"
    },

    "data_analysis": {
      "type": "pdf",
      "pages": 1,
      "has_text_layer": true,
      "file_size_kb": 45,
      "analysis_code": "import fitz\nimport base64\n\npdf_bytes = base64.b64decode(context['pdf_data_b64'])\ndoc = fitz.open(stream=pdf_bytes, filetype='pdf')\n\nresult = {\n  'type': 'pdf',\n  'pages': len(doc),\n  'has_text_layer': bool(doc[0].get_text().strip()),\n  'file_size_kb': len(pdf_bytes) // 1024\n}\n\ncontext['_data_insights'] = result"
    },

    "code_generation": {
      "code": "import fitz\nimport re...",
      "tool_calls": [],
      "generation_time_ms": 1523.4
    },

    "code_validation": {
      "valid": true,
      "errors": [],
      "checks_passed": ["syntax", "variables", "context_access", "imports", "functions"]
    },

    "execution_result": {
      "status": "success"
    },

    "output_validation": {
      "valid": true,
      "reason": "Task completed: extracted total and vendor",
      "changes_detected": ["invoice_total", "invoice_vendor"]
    },

    "attempts": 1,
    "status": "success",
    "errors": [],

    "timings": {
      "InputAnalyzer": 10.2,
      "DataAnalyzer": 234.5,
      "CodeGenerator": 1523.4,
      "CodeValidator": 5.8,
      "OutputValidator": 12.3
    },

    "total_time_ms": 1786.2
  }
}
```

---

## 🔁 Ejemplo con Retry

### Chain of Work Entry (Éxito después de 2 intentos)

```json
{
  "id": 124,
  "execution_id": 46,
  "node_id": "calculate_tax",
  "node_type": "ActionNode",

  "code_executed": "tax_rate = 0.21\ncontext['total_with_tax'] = context['subtotal'] * (1 + tax_rate)",

  "input_context": {
    "subtotal": 1000.0
  },

  "output_result": {
    "subtotal": 1000.0,
    "total_with_tax": 1210.0
  },

  "execution_time": 1.567,
  "status": "success",

  "ai_metadata": {
    "input_analysis": {
      "needs_analysis": false,
      "complexity": "simple",
      "reasoning": "Simple arithmetic calculation"
    },

    "data_analysis": null,

    "code_generation": {
      "code": "tax_rate = 0.21\ncontext['total_with_tax'] = context['subtotal'] * (1 + tax_rate)",
      "tool_calls": []
    },

    "code_validation": {
      "valid": true,
      "errors": []
    },

    "execution_result": {
      "status": "success"
    },

    "output_validation": {
      "valid": true,
      "reason": "Tax calculated correctly",
      "changes_detected": ["total_with_tax"]
    },

    // ⭐ TUVO 2 INTENTOS (primer intento falló)
    "attempts": 2,
    "status": "success",

    // ⭐ HISTORIAL DE ERRORES
    "errors": [
      {
        "attempt": 1,
        "stage": "code_validation",
        "error": "Variable 'tax_rate' used before definition"
      }
    ],

    "timings": {
      "InputAnalyzer": 8.5,
      "CodeGenerator": 945.3,
      "CodeValidator": 4.2,
      "OutputValidator": 10.1
    },

    "total_time_ms": 968.1
  }
}
```

---

## ❌ Ejemplo de Fallo Total

### Chain of Work Entry (Falló después de 3 intentos)

```json
{
  "id": 125,
  "execution_id": 47,
  "node_id": "parse_complex_data",
  "node_type": "ActionNode",

  // El último código que intentó generar
  "code_executed": "import json\ndata = json.loads(context['json_str'])...",

  "input_context": {
    "json_str": "{invalid json"
  },

  "output_result": {
    "json_str": "{invalid json"
  },

  "execution_time": 0,
  "status": "failed",
  "error_message": "Multi-Agent execution failed: Workflow falló después de 3 intentos",

  "ai_metadata": {
    "input_analysis": {
      "needs_analysis": false,
      "complexity": "simple"
    },

    "data_analysis": null,
    "code_generation": null,
    "code_validation": null,
    "execution_result": null,
    "output_validation": null,

    // ⭐ AGOTÓ LOS 3 INTENTOS
    "attempts": 3,
    "status": "failed",

    // ⭐ TODOS LOS ERRORES
    "errors": [
      {
        "attempt": 1,
        "stage": "execution",
        "error": "JSONDecodeError: Invalid JSON syntax at position 1"
      },
      {
        "attempt": 2,
        "stage": "execution",
        "error": "JSONDecodeError: Invalid JSON syntax at position 1"
      },
      {
        "attempt": 3,
        "stage": "execution",
        "error": "JSONDecodeError: Invalid JSON syntax at position 1"
      }
    ],

    "timings": {
      "InputAnalyzer": 9.2
    },

    "total_time_ms": 2456.8,

    // ⭐ ERROR FINAL
    "final_error": "Workflow falló después de 3 intentos: JSONDecodeError: Invalid JSON syntax"
  }
}
```

---

## 🔍 Queries Útiles

### Ver metadata de todos los nodos de una ejecución

```sql
SELECT
    node_id,
    node_type,
    status,
    ai_metadata->>'attempts' as attempts,
    ai_metadata->>'status' as ai_status,
    json_array_length(ai_metadata->'errors') as error_count,
    ai_metadata->'timings'->>'InputAnalyzer' as input_analyzer_ms,
    ai_metadata->'timings'->>'CodeGenerator' as code_generator_ms,
    ai_metadata->>'total_time_ms' as total_time_ms
FROM chain_of_work
WHERE execution_id = 45
ORDER BY id;
```

### Ver solo nodos que necesitaron retry

```sql
SELECT
    node_id,
    ai_metadata->>'attempts' as attempts,
    ai_metadata->'errors' as error_history,
    status
FROM chain_of_work
WHERE
    execution_id = 45
    AND CAST(ai_metadata->>'attempts' AS INTEGER) > 1;
```

### Ver análisis de datos (DataAnalyzer)

```sql
SELECT
    node_id,
    ai_metadata->'data_analysis'->>'type' as data_type,
    ai_metadata->'data_analysis'->>'pages' as pages,
    ai_metadata->'data_analysis'->>'has_text_layer' as has_text,
    ai_metadata->'data_analysis'->'analysis_code' as analysis_code
FROM chain_of_work
WHERE
    execution_id = 45
    AND ai_metadata->'data_analysis' IS NOT NULL;
```

### Ver código generado por AI

```sql
SELECT
    node_id,
    code_executed,
    ai_metadata->'code_generation'->>'generation_time_ms' as gen_time,
    ai_metadata->'code_validation'->'checks_passed' as checks_passed
FROM chain_of_work
WHERE
    execution_id = 45
    AND node_type = 'ActionNode';
```

---

## 📊 Diferencias con Implementación Anterior

### ANTES (sin multi-agente)

```json
"ai_metadata": {
  "model": "gpt-4o-mini",
  "prompt": "Extract total from invoice",
  "generated_code": "import fitz...",
  "tokens_input": 7000,
  "tokens_output": 450,
  "cost_usd": 0.0012,
  "generation_time_ms": 1800,
  "execution_time_ms": 1200,
  "attempts": 1,
  "cache_hit": false
}
```

### AHORA (con multi-agente)

```json
"ai_metadata": {
  // ⭐ INFORMACIÓN DE 5 AGENTES
  "input_analysis": {...},        // Estrategia
  "data_analysis": {...},         // Análisis de estructura
  "code_generation": {...},       // Generación
  "code_validation": {...},       // Validación estática
  "output_validation": {...},     // Validación semántica

  // ⭐ ORCHESTRATOR INFO
  "attempts": 2,                  // Retries
  "status": "success",
  "errors": [...],                // Historial completo
  "timings": {...},               // Timing por agente
  "total_time_ms": 1786.2,
  "final_error": null             // Si falló
}
```

---

## 💡 Valor de la Metadata

### 1. **Debugging**
- Ver exactamente qué código generó la AI
- Identificar en qué stage falló
- Entender por qué necesitó retries

### 2. **Análisis de Performance**
- Identificar agentes lentos
- Optimizar prompts que generan mucho retry
- Detectar patrones de fallo

### 3. **Auditoría**
- Trazabilidad completa de decisiones AI
- Código ejecutado preservado
- Historial de errores para mejora continua

### 4. **Cost Tracking** (futuro)
- Agregar tokens y costos por agente
- Identificar nodos caros
- Optimizar presupuesto

---

**Resumen**: El campo `ai_metadata` guarda información completa y estructurada de los 5 agentes + orchestrator, permitiendo debugging, análisis y auditoría detallada de cada ejecución.
