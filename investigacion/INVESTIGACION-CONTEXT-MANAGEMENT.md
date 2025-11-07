# Investigación: Context Management para Graph Engines

**Fecha**: 2025-10-27
**Propósito**: Definir el mejor approach para gestión de contexto en NOVA

---

## Resumen Ejecutivo

La gestión de contexto es **crítica** en workflow engines basados en grafos. Permite que nodos independientes compartan estado, tomen decisiones condicionales y mantengan coherencia durante la ejecución.

**Decisión clave para NOVA**: Implementar **Shared Mutable State** con inyección de contexto en cada nodo.

---

## 1. Análisis de Frameworks Existentes

### 1.1 LangGraph (State Management de Referencia)

**Approach**: Shared State con TypedDict/Schema

**Características clave**:
- **State Schema**: Define estructura con TypedDict (Python) o Zod (TypeScript)
- **Automatic Merging**: Los nodos retornan solo los campos a actualizar, el framework hace merge automático
- **Persistence**: Guarda estado después de cada paso (checkpointer)
- **Immutable Context**: Contexto estático (runtime config) separado de estado mutable

**Ejemplo de implementación**:
```python
from typing_extensions import TypedDict
from langgraph.graph import StateGraph

class CustomState(TypedDict):
    messages: list[AnyMessage]
    extra_field: int

def node(state: CustomState):
    # Lee estado actual
    messages = state["messages"]

    # Retorna solo actualizaciones (merge automático)
    return {
        "extra_field": state["extra_field"] + 1
    }

builder = StateGraph(CustomState)
builder.add_node(node)
graph = builder.compile()
```

**Ventajas**:
- ✅ Separación clara entre estado mutable y contexto inmutable
- ✅ Automatic state merging reduce errores
- ✅ Persistence built-in para pause/resume
- ✅ Type-safe con TypedDict

**Desventajas**:
- ❌ Requiere definir schema completo upfront
- ❌ Más complejo para casos simples

---

### 1.2 Apache Airflow (XCom)

**Approach**: Message Passing entre tareas independientes

**Características clave**:
- **XCom (Cross-Communication)**: Push/Pull explícito de datos
- **Task Isolation**: Tareas completamente aisladas por defecto
- **External Storage**: Para datos grandes (>1MB) usa S3/HDFS y pasa referencias
- **Auto-Push**: Return values automáticamente van a XCom key "return_value"

**Ejemplo de implementación**:
```python
# Push explícito
def task_1(**context):
    context['task_instance'].xcom_push(key='invoice_data', value={'amount': 1200})

# Pull explícito
def task_2(**context):
    invoice = context['task_instance'].xcom_pull(key='invoice_data', task_ids='task_1')
    validate(invoice)

# Auto-push con return
def task_3(**context):
    return {'result': 'approved'}  # Automáticamente en XCom['return_value']
```

**Ventajas**:
- ✅ Task isolation fuerte (seguridad)
- ✅ Escalable (external storage para datos grandes)
- ✅ Auto-push simplifica casos comunes

**Desventajas**:
- ❌ Verboso (push/pull explícito)
- ❌ No mantiene estado global coherente
- ❌ Dificulta decisiones condicionales complejas

---

### 1.3 Temporal (Context Propagation)

**Approach**: Context Propagators para metadata, State Persistence para workflow data

**Características clave**:
- **Context Propagators**: Para metadata (user_id, trace_id) que fluye workflow → activity → child workflow
- **Workflow State**: Automáticamente persistido por Temporal backend
- **Deterministic Execution**: Workflow code debe ser determinístico
- **Encryption**: Context values van a DB, encriptar data sensible

**Ejemplo de implementación**:
```go
// Context Propagator para metadata
type ContextPropagator interface {
    Inject(ctx context.Context, headers map[string]string) error
    Extract(headers map[string]string) (context.Context, error)
}

// Workflow state (auto-persistido)
func InvoiceWorkflow(ctx workflow.Context, invoiceData InvoiceData) error {
    // State se persiste automáticamente
    var validationResult bool
    err := workflow.ExecuteActivity(ctx, ValidateActivity, invoiceData).Get(ctx, &validationResult)

    if validationResult {
        // Workflow state incluye esta decisión
        return workflow.ExecuteActivity(ctx, ApproveActivity, invoiceData).Get(ctx, nil)
    }
    return nil
}
```

**Ventajas**:
- ✅ State persistence automática (fault tolerance)
- ✅ Separación clara: metadata (propagated) vs state (persisted)
- ✅ Escalable para workflows long-running

**Desventajas**:
- ❌ Complejidad de setup (Temporal server required)
- ❌ Overhead para workflows simples
- ❌ Curva de aprendizaje alta

---

### 1.4 Prefect (Runtime Context)

**Approach**: Thread-safe global context con Runtime module

**Características clave**:
- **Runtime Context**: Acceso global thread-safe a flow/task info
- **State Management**: Estados ricos (Pending, Running, Completed, Failed)
- **State Hooks**: Ejecutar código en cambios de estado
- **No Explicit Passing**: Contexto accesible desde cualquier task

**Ejemplo de implementación**:
```python
from prefect import flow, task
from prefect.context import get_run_context

@task
def process_invoice():
    # Acceso implícito a contexto
    ctx = get_run_context()
    flow_run_id = ctx.flow_run.id
    task_run_id = ctx.task_run.id

    # State automáticamente gestionado
    return {"invoice_data": {...}}

@flow
def invoice_workflow():
    result = process_invoice()
    # Context propagado automáticamente
    validate(result)
```

**Ventajas**:
- ✅ Acceso implícito reduce boilerplate
- ✅ Thread-safe
- ✅ State management automático

**Desventajas**:
- ❌ Global state puede causar side effects
- ❌ Testing más complejo (mock global context)
- ❌ Menos explícito (harder to debug)

---

### 1.5 n8n (Node Data Passing)

**Approach**: Direct node output → input passing

**Características clave**:
- **Direct Passing**: Output de nodo N → Input de nodo N+1
- **Set Node**: Para variables intermedias (problemático si no en main execution path)
- **Sub-workflows**: Para compartir entre workflows diferentes
- **Limitations**: Difícil pasar datos entre nodos distantes

**Ventajas**:
- ✅ Simple para workflows lineales
- ✅ Visual (UX clara)

**Desventajas**:
- ❌ No escala para grafos complejos
- ❌ Dificulta branching condicional
- ❌ Variables intermedias problemáticas

---

## 2. Patrones de Diseño Identificados

### Pattern 1: **Shared Mutable State**
- **Usado por**: LangGraph, Prefect
- **Descripción**: Un diccionario global que todos los nodos pueden leer/escribir
- **Pros**: Simple, coherencia de estado, decisiones condicionales fáciles
- **Cons**: Requiere sincronización, potential race conditions (si paralelo)

### Pattern 2: **Message Passing**
- **Usado por**: Airflow XCom, n8n
- **Descripción**: Nodos envían mensajes explícitos entre sí
- **Pros**: Task isolation, escalable, debuggable
- **Cons**: Verboso, dificulta estado global coherente

### Pattern 3: **Context Propagation**
- **Usado por**: Temporal
- **Descripción**: Metadata inmutable fluye top-down, state mutable se persiste
- **Pros**: Separación clara, fault tolerance
- **Cons**: Complejidad, overhead

### Pattern 4: **Implicit Global Context**
- **Usado por**: Prefect
- **Descripción**: Context accesible globalmente sin pasar como parámetro
- **Pros**: Menos boilerplate, DX limpio
- **Cons**: Side effects, testing difícil

---

## 3. Comparación: State Isolation vs Shared State

| Aspecto | State Isolation | Shared State |
|---------|----------------|--------------|
| **Seguridad** | ✅ Alta (nodos independientes) | ⚠️ Media (mutual dependencies) |
| **Complejidad** | ❌ Alta (push/pull explícito) | ✅ Baja (read/write directo) |
| **Decisiones condicionales** | ❌ Difícil (requiere pull múltiple) | ✅ Fácil (todo el state disponible) |
| **Debugging** | ✅ Fácil (trace claro) | ⚠️ Medio (state mutations) |
| **Escalabilidad** | ✅ Alta (parallelismo natural) | ⚠️ Media (sincronización requerida) |
| **Performance** | ⚠️ Overhead de serialización | ✅ Acceso directo rápido |
| **Use case ideal** | Workflows long-running, distribuidos | Workflows secuenciales, single-machine |

---

## 4. Decisión para NOVA

### Contexto de NOVA:
- **Ejecución**: Sequential node-by-node (no paralelo en Phase 1)
- **Deployment**: Monolith en Railway (single machine)
- **Sandbox**: External (Hetzner) pero stateless (no persiste nada)
- **Use case**: Workflows cortos (~segundos), secuenciales
- **Complejidad**: MVP simple, escalar en Phase 2

### Approach Elegido: **Shared Mutable State con Inyección**

**Inspirado en**: LangGraph (state schema) + Temporal (context injection)

**Justificación**:
1. **Simplicidad**: MVP requiere approach simple, no overhead de message passing
2. **Decisiones condicionales**: DecisionNodes necesitan acceso completo al state
3. **Trazabilidad**: ContextManager centralizado facilita logging en chain_of_work
4. **Inyección en Hetzner**: Sandbox no tiene estado → inyectamos context en cada llamada
5. **Type-safe futuro**: Fácil agregar schema validation en Phase 2

**Rechazamos**:
- ❌ **Message Passing (Airflow XCom)**: Muy verboso para MVP, dificulta decisiones condicionales
- ❌ **Implicit Global (Prefect)**: Complicaría testing, menos explícito
- ❌ **Context Propagation (Temporal)**: Overhead innecesario para workflows simples

---

## 5. Diseño de Implementación para NOVA

### 5.1 Arquitectura

```
[GraphEngine]
      ↓
[ContextManager] ← Estado compartido (dict)
      ↓
[Node Execution Loop]
      ↓
Para cada nodo:
  1. context_dict = context_manager.get_all()
  2. Inyectar context en código de nodo
  3. Enviar a Hetzner: código + context
  4. Recibir output con context actualizado
  5. context_manager.update(new_context)
  6. Guardar en chain_of_work (input_context, output_result)
      ↓
[Next Node]
```

### 5.2 API del ContextManager

```python
class ContextManager:
    def __init__(self, initial_context: dict = None):
        """Initialize with optional initial context"""
        self._context: dict = initial_context or {}

    def get(self, key: str, default=None) -> Any:
        """Get single value from context"""
        return self._context.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set single value in context"""
        self._context[key] = value

    def update(self, data: dict) -> None:
        """Update multiple values (merge)"""
        self._context.update(data)

    def get_all(self) -> dict:
        """Return complete context (copy for safety)"""
        return self._context.copy()

    def clear(self) -> None:
        """Clear all context (useful for testing)"""
        self._context = {}

    def snapshot(self) -> dict:
        """Create immutable snapshot for chain_of_work"""
        import copy
        return copy.deepcopy(self._context)
```

### 5.3 Inyección en Hetzner Sandbox

**Problema**: Hetzner sandbox es stateless, cada ejecución es aislada.

**Solución**: Inyectar context como variable global en el código ejecutado.

```python
# En GraphEngine, antes de enviar a Hetzner:
def execute_node(node: ActionNode, context_manager: ContextManager):
    # 1. Obtener contexto actual
    context_dict = context_manager.get_all()

    # 2. Preparar código con contexto inyectado
    full_code = f"""
import json

# Context inyectado como variable global
context = {json.dumps(context_dict)}

# Código del nodo (puede leer/escribir context)
{node.code}

# Retornar context actualizado
print(json.dumps(context))
"""

    # 3. Enviar a Hetzner
    response = requests.post(
        "http://188.245.183.74:8000/execute",
        json={"code": full_code, "timeout": 10}
    )

    # 4. Parsear output (context actualizado)
    output = response.json()["output"]
    new_context = json.loads(output)

    # 5. Actualizar ContextManager
    context_manager.update(new_context)

    # 6. Guardar en chain_of_work
    save_to_chain_of_work(
        input_context=context_dict,
        output_result=new_context,
        code_executed=node.code
    )
```

### 5.4 Ejemplo de Uso en Workflow

**Workflow JSON**:
```json
{
  "nodes": [
    {
      "id": "extract",
      "type": "action",
      "code": "context['invoice_data'] = {'amount': 1200, 'vendor': 'ACME'}"
    },
    {
      "id": "validate",
      "type": "action",
      "code": "amount = context['invoice_data']['amount']\ncontext['is_valid'] = amount > 0"
    },
    {
      "id": "decide",
      "type": "decision",
      "condition": "context['is_valid'] == True"
    }
  ]
}
```

**Ejecución paso a paso**:

| Step | Node | Context Antes | Código Ejecutado | Context Después |
|------|------|---------------|------------------|-----------------|
| 1 | extract | `{}` | `context['invoice_data'] = {...}` | `{"invoice_data": {"amount": 1200}}` |
| 2 | validate | `{"invoice_data": {...}}` | `context['is_valid'] = True` | `{"invoice_data": {...}, "is_valid": true}` |
| 3 | decide | `{"invoice_data": {...}, "is_valid": true}` | Evalúa condición (local) | (sin cambios) |

---

## 6. Trade-offs Aceptados

### ✅ Ventajas de este approach:

1. **Simplicidad**: Implementación < 100 líneas de código
2. **Trazabilidad**: Context snapshots en chain_of_work
3. **Debuggable**: Podemos ver exactamente qué context tenía cada nodo
4. **Flexible**: Nodos pueden escribir cualquier dato al context
5. **Type-safe futuro**: Fácil agregar Pydantic schemas en Phase 2

### ⚠️ Trade-offs aceptados:

1. **Serialization overhead**: JSON encode/decode en cada nodo (~ms)
   - **Aceptable**: Workflows MVP son cortos, overhead < 10ms total

2. **No parallelism**: Context manager no es thread-safe
   - **Aceptable**: Phase 1 es sequential, agregamos locks en Phase 2 si necesario

3. **Memory**: Todo el context en RAM
   - **Aceptable**: Contexts pequeños (<1MB), Railway tiene 512MB RAM

4. **No type validation**: Context es dict genérico
   - **Aceptable**: MVP prioriza velocidad, agregamos Pydantic en Phase 2

---

## 7. Mejoras Futuras (Phase 2+)

### 7.1 Schema Validation
```python
from pydantic import BaseModel

class InvoiceContext(BaseModel):
    invoice_data: dict
    is_valid: bool
    needs_approval: bool

# En GraphEngine:
context_manager = ContextManager(schema=InvoiceContext)
```

### 7.2 Context Versioning
```python
# Guardar snapshots versionados
context_manager.save_version("before_validation")
context_manager.rollback_to("before_validation")
```

### 7.3 Thread-Safe Context
```python
import threading

class ThreadSafeContextManager(ContextManager):
    def __init__(self):
        super().__init__()
        self._lock = threading.Lock()

    def update(self, data: dict):
        with self._lock:
            super().update(data)
```

### 7.4 External Storage
```python
# Para contexts grandes (>1MB)
class RedisContextManager(ContextManager):
    def __init__(self, redis_client, execution_id):
        self.redis = redis_client
        self.key = f"context:{execution_id}"

    def get_all(self):
        return json.loads(self.redis.get(self.key) or "{}")

    def update(self, data):
        current = self.get_all()
        current.update(data)
        self.redis.set(self.key, json.dumps(current))
```

---

## 8. Conclusiones

### Decisión Final:
**Implementar ContextManager como diccionario Python centralizado con inyección en sandbox.**

### Razones:
1. ✅ **Simplicidad**: MVP funcional en <2 horas de implementación
2. ✅ **Suficiente**: Cubre todos los use cases de Phase 1
3. ✅ **Escalable**: Fácil mejorar en Phase 2 sin breaking changes
4. ✅ **Proven**: Pattern usado por LangGraph (framework líder en 2025)

### Próximos Pasos:
1. Implementar `ContextManager` en `/nova/src/core/context.py`
2. Integrar en `GraphEngine` con inyección de context
3. Testing con workflow de ejemplo
4. Documentar en chain_of_work para trazabilidad

---

## Referencias

- LangGraph State Management: https://langchain-ai.github.io/langgraph/concepts/low_level/
- Airflow XCom Best Practices: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/xcoms.html
- Temporal Context Propagation: https://docs.temporal.io/workflows
- Prefect Runtime Context: https://docs.prefect.io/3.0/develop/runtime-context
- State Pattern in Workflows: https://www.momentslog.com/development/design-pattern/applying-the-state-pattern-in-workflow-engines-for-dynamic-process-management
