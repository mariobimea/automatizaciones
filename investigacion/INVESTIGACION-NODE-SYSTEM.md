# Investigación: Node System Design para Workflow Engines

**Fecha**: 2025-10-27
**Propósito**: Diseñar la mejor arquitectura de nodos para NOVA basándose en frameworks líderes y best practices

---

## Resumen Ejecutivo

El **Node System** es el corazón del workflow engine. Los nodos representan unidades de ejecución (acciones, decisiones, control de flujo) que forman un grafo dirigido acíclico (DAG).

**Decisión clave para NOVA**: Implementar nodos como **Pydantic BaseModels** con **Factory Pattern + Strategy Pattern** para ejecutores, inspirado en LangGraph (state management) + Airflow (operator abstraction) + n8n (declarative + programmatic styles).

---

## 1. Análisis de Frameworks Existentes

### 1.1 LangGraph (State-First Node Design)

**Approach**: Nodos como funciones puras que reciben y retornan state

**Características clave**:

```python
from typing_extensions import TypedDict
from langgraph.graph import StateGraph

class State(TypedDict):
    messages: list
    extra_field: int

def node(state: State) -> dict:
    """Node returns partial state updates"""
    return {"extra_field": state["extra_field"] + 1}

builder = StateGraph(State)
builder.add_node("my_node", node)
```

**Pros**:
- ✅ **Simplicidad**: Nodos son solo funciones
- ✅ **Type-safe**: TypedDict proporciona validación de tipos
- ✅ **State Management**: Automatic merging de state updates
- ✅ **Validation**: Runtime validation con Pydantic en inputs/outputs
- ✅ **Caching**: Node-level caching con `CachePolicy(ttl=seconds)`

**Cons**:
- ❌ No hay abstracción de nodo como objeto (solo funciones)
- ❌ Dificulta agregar metadata a nodos individuales

**Patterns usados**:
- **Strategy Pattern**: Diferentes node functions = diferentes estrategias
- **Decorator Pattern**: `@task` decorator para concurrent execution

---

### 1.2 Apache Airflow (Operator Pattern)

**Approach**: Nodos como Operators (templates de tareas)

**Características clave**:

```python
from airflow.operators.python import PythonOperator

def my_task(**context):
    # Task logic
    return result

task = PythonOperator(
    task_id='my_task',
    python_callable=my_task,
    dag=dag
)
```

**Arquitectura**:
- **Operator** = Template abstracto
- **Task** = Operator instanciado con parámetros
- **Hook** = Communication layer (reusable)

**Pros**:
- ✅ **Reusabilidad**: Operators son reutilizables como templates
- ✅ **Separación**: Hooks separan comunicación de lógica
- ✅ **Extensibilidad**: Fácil crear custom operators
- ✅ **Modularidad**: Cada operator es self-contained

**Cons**:
- ❌ Overhead de abstracción para casos simples
- ❌ Curva de aprendizaje (Operator + Hook + DAG)

**Patterns usados**:
- **Template Method Pattern**: Operator como template abstracto
- **Hook Pattern**: Separación de communication layer
- **Factory Pattern**: Operator instantiation

---

### 1.3 n8n (Declarative + Programmatic Styles)

**Approach**: Dos estilos de nodos (JSON declarativo + TypeScript programático)

**Declarative Style** (JSON):
```json
{
  "name": "Extract Invoice",
  "type": "n8n-nodes-base.function",
  "typeVersion": 1,
  "position": [250, 300],
  "parameters": {
    "functionCode": "return items.map(item => ({ ...item, amount: 1200 }));"
  }
}
```

**Programmatic Style** (TypeScript):
```typescript
export class FriendGrid implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'FriendGrid',
    name: 'friendGrid',
    group: ['transform'],
    version: 1,
    description: 'Interact with FriendGrid API',
    defaults: { name: 'FriendGrid' },
    inputs: ['main'],
    outputs: ['main'],
    properties: [...]
  };

  async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
    // Execution logic
  }
}
```

**Pros**:
- ✅ **Flexibilidad**: Declarativo para simplicidad, programático para complejidad
- ✅ **Type Safety**: TypeScript para nodos complejos
- ✅ **Visual**: JSON se mapea directamente a UI
- ✅ **Self-contained**: Cada nodo tiene toda su lógica

**Cons**:
- ❌ Duplicación potencial entre estilos
- ❌ Requiere compilación (TypeScript)

**Patterns usados**:
- **Strategy Pattern**: Dos estilos = dos estrategias
- **Facade Pattern**: INodeType interface simplifica implementación

---

### 1.4 Prefect (Task Decorators + Flow Composition)

**Approach**: Tasks como funciones decoradas

```python
from prefect import task, flow

@task
def extract_invoice(pdf_path: str):
    return extract_data(pdf_path)

@task
def validate_invoice(data: dict):
    return is_valid(data)

@flow
def invoice_workflow(pdf_path: str):
    data = extract_invoice(pdf_path)
    valid = validate_invoice(data)
    return valid
```

**Pros**:
- ✅ **Pythonic**: Decorators son naturales en Python
- ✅ **Composición**: Flows componen tasks fácilmente
- ✅ **Type hints**: Aprovecha Python typing

**Cons**:
- ❌ Difícil serializar (decorators no JSON-friendly)
- ❌ Menos declarativo (más imperativo)

---

### 1.5 Temporal (Workflow + Activity Pattern)

**Approach**: Workflows (orchestration) + Activities (execution)

```python
@workflow.defn
class InvoiceWorkflow:
    @workflow.run
    async def run(self, invoice_data: dict) -> bool:
        # Orchestration logic
        data = await workflow.execute_activity(
            extract_invoice,
            invoice_data,
            start_to_close_timeout=timedelta(seconds=10)
        )
        return data

@activity.defn
async def extract_invoice(invoice_data: dict) -> dict:
    # Execution logic
    return result
```

**Pros**:
- ✅ **Durability**: State automáticamente persistido
- ✅ **Fault tolerance**: Retry automático
- ✅ **Separación**: Workflow (orchestration) vs Activity (execution)

**Cons**:
- ❌ Requiere Temporal server (overhead)
- ❌ Curva de aprendizaje alta

---

## 2. Patrones de Diseño Identificados

### Pattern 1: **Template Method** (Airflow Operators)

**Descripción**: Clase base define estructura, subclases implementan detalles

```python
class BaseOperator(ABC):
    def execute(self, context):
        self.pre_execute(context)
        result = self.execute_impl(context)  # Subclass implements
        self.post_execute(result)
        return result

    @abstractmethod
    def execute_impl(self, context):
        pass
```

**Pros**: Reutiliza código común (pre/post-execution)
**Cons**: Rigid hierarchy

---

### Pattern 2: **Strategy** (Executor Strategies)

**Descripción**: Algoritmo intercambiable en runtime

```python
class ExecutorStrategy(ABC):
    @abstractmethod
    def execute(self, code: str, context: dict) -> dict:
        pass

class StaticExecutor(ExecutorStrategy):
    def execute(self, code, context):
        # Execute hardcoded code
        pass

class AIExecutor(ExecutorStrategy):
    def execute(self, code, context):
        # Generate code with AI, then execute
        pass
```

**Pros**: Fácil agregar nuevas estrategias
**Cons**: Puede crecer el número de clases

---

### Pattern 3: **Factory** (Node Creation)

**Descripción**: Crea objetos sin especificar clases concretas

```python
def create_node(node_data: dict) -> BaseNode:
    node_type = node_data["type"]

    if node_type == "action":
        return ActionNode(**node_data)
    elif node_type == "decision":
        return DecisionNode(**node_data)
    else:
        raise ValueError(f"Unknown node type: {node_type}")
```

**Pros**: Centraliza lógica de creación, fácil extensión
**Cons**: Puede volverse complejo con muchos tipos

---

### Pattern 4: **Decorator** (Validation + Caching)

**Descripción**: Agrega funcionalidad sin modificar clase base

```python
from pydantic import validate_call

@validate_call
def execute_node(node_id: str, context: dict) -> dict:
    # Pydantic validates arguments automatically
    return execute(node_id, context)
```

**Pros**: Separation of concerns, composable
**Cons**: Puede dificultar debugging

---

### Pattern 5: **Dependency Injection** (Executor Injection)

**Descripción**: Provee dependencias desde afuera (no hardcodeadas)

```python
class ActionNode:
    def __init__(self, code: str, executor: ExecutorStrategy):
        self.code = code
        self.executor = executor  # Injected!

    def execute(self, context: dict):
        return self.executor.execute(self.code, context)
```

**Pros**: Testeable (mock executors), flexible
**Cons**: Más verboso

---

## 3. Validación: Pydantic vs TypedDict vs Dataclass

### Comparación

| Aspecto | Pydantic BaseModel | TypedDict | Dataclass |
|---------|-------------------|-----------|-----------|
| **Validación runtime** | ✅ Sí (automática) | ❌ No (solo type hints) | ⚠️ Con `@dataclass(kw_only=True)` |
| **Serialización JSON** | ✅ `.model_dump()`, `.model_dump_json()` | ❌ Manual | ⚠️ Manual (asdict) |
| **Deserialización JSON** | ✅ `.model_validate()` | ❌ Manual | ❌ Manual |
| **Performance** | ⚠️ Overhead de validación | ✅ Sin overhead | ✅ Sin overhead |
| **Type Safety** | ✅ Runtime + Static | ✅ Static only | ✅ Static only |
| **Validation decorators** | ✅ `@field_validator`, `@model_validator` | ❌ No | ❌ No |
| **Default values** | ✅ `Field(default=...)` | ⚠️ Limitado | ✅ `field(default=...)` |
| **Immutability** | ✅ `frozen=True` | ❌ No | ✅ `frozen=True` |

### Recomendación para NOVA

**Usar Pydantic BaseModel** porque:
1. ✅ **Validación automática**: Evita errores de runtime
2. ✅ **Serialización**: JSON workflows → Python objects fácilmente
3. ✅ **Type-safe**: Static + runtime validation
4. ✅ **Extensibilidad**: Custom validators con `@field_validator`
5. ✅ **Industry standard**: Usado por FastAPI, LangChain, etc.

**Trade-off aceptado**: Overhead de validación (~ms) es insignificante comparado con ejecución en Hetzner (~500ms)

---

## 4. Arquitectura de Nodos para NOVA

### 4.1 Jerarquía de Clases

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from abc import ABC, abstractmethod

# Base class (no instanciable)
class BaseNode(BaseModel, ABC):
    """Base class for all workflow nodes"""
    id: str = Field(..., description="Unique node identifier")
    type: Literal["start", "end", "action", "decision"]
    label: Optional[str] = Field(None, description="Human-readable label")

    class Config:
        frozen = True  # Immutable after creation
        extra = "forbid"  # Reject unknown fields

    @abstractmethod
    def validate_node(self) -> None:
        """Custom validation logic (override in subclasses)"""
        pass

# Start/End nodes (control flow)
class StartNode(BaseNode):
    type: Literal["start"] = "start"

    def validate_node(self):
        pass  # No custom validation needed

class EndNode(BaseNode):
    type: Literal["end"] = "end"

    def validate_node(self):
        pass

# Action node (executes code)
class ActionNode(BaseNode):
    type: Literal["action"] = "action"
    code: str = Field(..., min_length=1, description="Python code to execute")
    executor: Literal["static", "cached", "ai"] = Field("static", description="Execution strategy")
    timeout: int = Field(10, ge=1, le=60, description="Execution timeout in seconds")

    @field_validator("code")
    def validate_code_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Code cannot be empty or whitespace only")
        return v

    def validate_node(self):
        # Additional validation (e.g., syntax check)
        try:
            compile(self.code, "<string>", "exec")
        except SyntaxError as e:
            raise ValueError(f"Invalid Python syntax: {e}")

# Decision node (conditional branching)
class DecisionNode(BaseNode):
    type: Literal["decision"] = "decision"
    condition: str = Field(..., min_length=1, description="Python expression returning bool")

    @field_validator("condition")
    def validate_condition_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Condition cannot be empty")
        return v

    def validate_node(self):
        # Validate it's a valid Python expression
        try:
            compile(self.condition, "<string>", "eval")
        except SyntaxError as e:
            raise ValueError(f"Invalid Python expression: {e}")
```

### 4.2 Factory Pattern

```python
from typing import Union

NodeType = Union[StartNode, EndNode, ActionNode, DecisionNode]

def create_node_from_dict(node_data: dict) -> NodeType:
    """
    Factory function to create nodes from JSON/dict.

    Args:
        node_data: Dictionary with node configuration

    Returns:
        Node instance (StartNode, EndNode, ActionNode, or DecisionNode)

    Raises:
        ValueError: If node type is unknown
        ValidationError: If node data is invalid (Pydantic validation)

    Example:
        >>> node_data = {"id": "extract", "type": "action", "code": "print('hello')"}
        >>> node = create_node_from_dict(node_data)
        >>> isinstance(node, ActionNode)
        True
    """
    node_type = node_data.get("type")

    # Factory dispatch
    node_classes = {
        "start": StartNode,
        "end": EndNode,
        "action": ActionNode,
        "decision": DecisionNode,
    }

    node_class = node_classes.get(node_type)
    if not node_class:
        raise ValueError(
            f"Unknown node type: {node_type}. "
            f"Valid types: {list(node_classes.keys())}"
        )

    # Pydantic validates automatically
    node = node_class(**node_data)

    # Custom validation
    node.validate_node()

    return node


def create_nodes_from_workflow(workflow_definition: dict) -> dict[str, NodeType]:
    """
    Create all nodes from a workflow definition.

    Args:
        workflow_definition: Dict with "nodes" key containing list of node dicts

    Returns:
        Dictionary mapping node_id -> Node instance

    Example:
        >>> workflow = {
        ...     "nodes": [
        ...         {"id": "start", "type": "start"},
        ...         {"id": "extract", "type": "action", "code": "..."},
        ...         {"id": "end", "type": "end"}
        ...     ]
        ... }
        >>> nodes = create_nodes_from_workflow(workflow)
        >>> len(nodes)
        3
    """
    nodes = {}

    for node_data in workflow_definition.get("nodes", []):
        node = create_node_from_dict(node_data)

        # Check for duplicate IDs
        if node.id in nodes:
            raise ValueError(f"Duplicate node ID: {node.id}")

        nodes[node.id] = node

    return nodes
```

### 4.3 Strategy Pattern para Executors

```python
from abc import ABC, abstractmethod

class ExecutorStrategy(ABC):
    """Abstract executor interface"""

    @abstractmethod
    async def execute(self, code: str, context: dict, timeout: int) -> dict:
        """
        Execute code with given context.

        Args:
            code: Python code to execute
            context: Execution context (dict)
            timeout: Max execution time in seconds

        Returns:
            Updated context after execution
        """
        pass


class StaticExecutor(ExecutorStrategy):
    """Executes hardcoded Python code in Hetzner sandbox"""

    def __init__(self, sandbox_url: str):
        self.sandbox_url = sandbox_url

    async def execute(self, code: str, context: dict, timeout: int) -> dict:
        import json
        import requests

        # Inject context into code
        full_code = f"""
import json

# Injected context
context = {json.dumps(context)}

# User code
{code}

# Return updated context
print(json.dumps(context))
"""

        # Send to Hetzner
        response = requests.post(
            f"{self.sandbox_url}/execute",
            json={"code": full_code, "timeout": timeout}
        )

        # Parse output
        output = response.json()["output"]
        new_context = json.loads(output)

        return new_context


class CachedExecutor(ExecutorStrategy):
    """Executes code, caching successful results (Phase 2)"""

    async def execute(self, code: str, context: dict, timeout: int) -> dict:
        # TODO: Check cache first
        # TODO: If miss, generate code with AI or use hardcoded
        # TODO: Execute and cache result
        raise NotImplementedError("CachedExecutor is Phase 2")


class AIExecutor(ExecutorStrategy):
    """Always generates fresh code with LLM (Phase 2)"""

    async def execute(self, code: str, context: dict, timeout: int) -> dict:
        # TODO: Generate code with LLM based on node description
        # TODO: Execute generated code
        raise NotImplementedError("AIExecutor is Phase 2")


# Executor factory
def get_executor(executor_type: str, **kwargs) -> ExecutorStrategy:
    """
    Factory for creating executor instances.

    Example:
        >>> executor = get_executor("static", sandbox_url="http://...")
        >>> isinstance(executor, StaticExecutor)
        True
    """
    executors = {
        "static": StaticExecutor,
        "cached": CachedExecutor,
        "ai": AIExecutor,
    }

    executor_class = executors.get(executor_type)
    if not executor_class:
        raise ValueError(f"Unknown executor type: {executor_type}")

    return executor_class(**kwargs)
```

---

## 5. Workflow Validation

### 5.1 Validaciones Estructurales

```python
from typing import List

def validate_workflow_structure(nodes: dict[str, NodeType], edges: List[dict]) -> None:
    """
    Validate workflow structure.

    Checks:
    1. Exactly 1 StartNode
    2. At least 1 EndNode
    3. All edges reference valid nodes
    4. No orphan nodes (except EndNodes)
    5. DecisionNodes have 2+ outgoing edges

    Raises:
        ValueError: If validation fails
    """
    # Count node types
    start_nodes = [n for n in nodes.values() if isinstance(n, StartNode)]
    end_nodes = [n for n in nodes.values() if isinstance(n, EndNode)]

    if len(start_nodes) != 1:
        raise ValueError(f"Workflow must have exactly 1 StartNode, found {len(start_nodes)}")

    if len(end_nodes) < 1:
        raise ValueError("Workflow must have at least 1 EndNode")

    # Validate edges
    node_ids = set(nodes.keys())

    for edge in edges:
        from_id = edge.get("from")
        to_id = edge.get("to")

        if from_id not in node_ids:
            raise ValueError(f"Edge references unknown 'from' node: {from_id}")
        if to_id not in node_ids:
            raise ValueError(f"Edge references unknown 'to' node: {to_id}")

    # Validate DecisionNodes have multiple edges
    outgoing_edges = {}
    for edge in edges:
        from_id = edge["from"]
        outgoing_edges.setdefault(from_id, []).append(edge)

    for node_id, node in nodes.items():
        if isinstance(node, DecisionNode):
            edges_from_node = outgoing_edges.get(node_id, [])
            if len(edges_from_node) < 2:
                raise ValueError(
                    f"DecisionNode '{node_id}' must have at least 2 outgoing edges, "
                    f"found {len(edges_from_node)}"
                )
```

---

## 6. Mejores Prácticas Identificadas

### 6.1 Design Principles

1. **Fail Fast**: Validar temprano (en creación de nodo, no en ejecución)
2. **Immutability**: Nodos son inmutables (`frozen=True`)
3. **Single Responsibility**: Cada nodo hace una cosa
4. **Open/Closed**: Abierto a extensión (nuevos tipos), cerrado a modificación
5. **Dependency Injection**: Inyectar executors, no hardcodear

### 6.2 Validation Best Practices

1. **Pydantic field validators**: Para validaciones simples (not empty, range)
2. **Custom validators**: Para lógica compleja (syntax checking)
3. **Structural validation**: Separar validación de nodo vs workflow
4. **Error messages**: Claros y accionables

### 6.3 Performance Considerations

1. **Node creation**: Validar solo una vez (al crear), no en cada ejecución
2. **Caching**: Compilar code/condition solo una vez
3. **Lazy loading**: Cargar executors solo cuando se necesitan
4. **Async execution**: Usar `async/await` para I/O (Hetzner calls)

---

## 7. Decisión de Diseño para NOVA

### Arquitectura Elegida

**Base**: Pydantic BaseModel con jerarquía de clases

**Patterns**:
- **Factory Pattern**: Para crear nodos desde JSON
- **Strategy Pattern**: Para diferentes executors
- **Dependency Injection**: Inyectar executors en nodes
- **Validation**: Pydantic + custom validators

**Inspiración**:
- **LangGraph**: State management, type safety
- **Airflow**: Operator abstraction, reusability
- **n8n**: Declarative (JSON) + programmatic (Python)
- **Pydantic**: Runtime validation, serialization

### Justificación

1. ✅ **Type-safe**: Pydantic valida en runtime + static type hints
2. ✅ **JSON-friendly**: Fácil serializar workflows desde JSON
3. ✅ **Extensible**: Fácil agregar nuevos node types
4. ✅ **Testeable**: Dependency injection permite mocking
5. ✅ **Clean**: Separación clara entre node types
6. ✅ **Performant**: Validación solo al crear, no en ejecución

### Trade-offs Aceptados

1. ⚠️ **Pydantic overhead**: ~ms por validación (insignificante vs ~500ms de Hetzner)
2. ⚠️ **More classes**: Más verboso que solo funciones (pero más mantenible)
3. ⚠️ **Learning curve**: Devs deben aprender Pydantic (pero es industry standard)

---

## 8. Comparación Final

| Aspecto | NOVA Design | LangGraph | Airflow | n8n |
|---------|-------------|-----------|---------|-----|
| **Node representation** | Pydantic BaseModel | Functions | Operator classes | TypeScript classes + JSON |
| **Validation** | Pydantic (runtime) | TypedDict (static) | Manual | TypeScript (static) |
| **Serialization** | JSON ↔ Pydantic | JSON ↔ dict | Python objects | JSON ↔ TypeScript |
| **Executor abstraction** | Strategy Pattern | Function composition | Hook Pattern | execute() method |
| **Type safety** | Runtime + Static | Static only | Minimal | Static (TypeScript) |
| **Extensibility** | Add node types | Add functions | Custom operators | Custom node types |

---

## 9. Roadmap de Implementación

### Phase 1 (MVP)

1. ✅ BaseNode (abstract)
2. ✅ StartNode, EndNode
3. ✅ ActionNode con StaticExecutor
4. ✅ DecisionNode
5. ✅ Factory pattern (create_node_from_dict)
6. ✅ Workflow validation
7. ✅ Unit tests

### Phase 2 (AI-Powered)

1. CachedExecutor implementation
2. AIExecutor implementation
3. Executor selection logic
4. Performance caching

### Phase 3 (Advanced)

1. ParallelNode (multiple concurrent actions)
2. LoopNode (iteration)
3. SubworkflowNode (nested workflows)
4. Conditional validation (context-aware)

---

## 10. Referencias

- Pydantic Validation Decorators: https://docs.pydantic.dev/latest/concepts/validators/
- LangGraph State Management: https://langchain-ai.github.io/langgraph/concepts/low_level/
- Airflow Operators: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/operators.html
- n8n Node Development: https://docs.n8n.io/integrations/creating-nodes/
- Factory Pattern in Python: https://refactoring.guru/design-patterns/factory-method/python/example
- Strategy Pattern with DI: https://www.mytechramblings.com/posts/dotnet-strategy-pattern-using-dependency-injection/
- Workflow Engine Principles (Temporal): https://temporal.io/blog/workflow-engine-principles
- Prefect Workflow Design Patterns: https://www.prefect.io/blog/workflow-design-patterns

---

## Conclusión

**Decisión Final**: Implementar nodos como **Pydantic BaseModels con Factory + Strategy patterns**.

**Razones**:
1. ✅ Type-safe (runtime + static)
2. ✅ JSON-friendly (workflows como JSON)
3. ✅ Extensible (fácil agregar node types)
4. ✅ Industry standard (Pydantic usado ampliamente)
5. ✅ Testeable (dependency injection)
6. ✅ Best practices from leaders (LangGraph, Airflow, n8n)

**Próximos Pasos**:
1. Implementar `/nova/src/core/nodes.py` con BaseNode hierarchy
2. Implementar `/nova/src/core/executors.py` con Strategy pattern
3. Testing exhaustivo (unit + integration)
4. Documentar API pública
