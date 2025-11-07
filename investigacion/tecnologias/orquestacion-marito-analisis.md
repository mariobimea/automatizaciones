# Orquestación de Marito: LangGraph vs Custom vs Maisa KPU

**Fecha**: 2025-10-22
**Decisión Crítica**: ¿Cómo orquestar los flujos de Marito?

---

## RESUMEN EJECUTIVO

Hay **3 opciones** para orquestar Marito:

| Opción | Complejidad | Control | Time to Market | Estabilidad | Recomendación |
|--------|-------------|---------|----------------|-------------|---------------|
| **LangGraph** | Media | Medio-Alto | Rápido (2-3 semanas) | ⚠️ Inestable | ⚠️ Con precaución |
| **Custom** | Alta | Total | Lento (6-8 semanas) | ✅ Total | ✅ **Recomendado** |
| **Maisa-style KPU** | Muy Alta | Total | Muy lento (3+ meses) | ✅ Total | ⚠️ Solo si enterprise |

**Mi recomendación final**: **Custom orchestrator** (estilo simple, inspirado en principios de Maisa KPU).

**Por qué**: Control total, estabilidad, no depender de frameworks que cambian cada semana, y es más simple de lo que parece.

---

## PARTE 1: ¿CÓMO FUNCIONA LANGGRAPH?

### 1.1 Arquitectura de LangGraph

LangGraph es un **framework de orquestación** basado en grafos que estructura workflows como **nodos** (agentes/funciones) conectados por **edges** (flujo de datos).

```python
# Ejemplo simplificado de LangGraph

from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

# 1. Definir el STATE (compartido entre todos los nodos)
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    task_description: str
    current_step: int
    generated_code: str
    execution_result: dict
    errors: list

# 2. Crear el grafo
workflow = StateGraph(AgentState)

# 3. Definir NODOS (funciones que procesan el state)
def analyze_task(state: AgentState) -> AgentState:
    """Analiza la tarea del usuario"""
    task = state["task_description"]

    # Llamar a LLM
    analysis = llm.invoke(f"Analyze this task and break it into steps: {task}")

    # Actualizar state
    state["messages"].append({"role": "system", "content": analysis})
    state["current_step"] = 1

    return state

def generate_code(state: AgentState) -> AgentState:
    """Genera código para el paso actual"""

    # Construir prompt con contexto del state
    prompt = f"""
    Task: {state['task_description']}
    Current step: {state['current_step']}

    Generate Python code for this step.
    """

    code = llm.invoke(prompt)
    state["generated_code"] = code

    return state

def execute_code(state: AgentState) -> AgentState:
    """Ejecuta el código generado"""

    code = state["generated_code"]

    # Ejecutar en sandbox
    result = sandbox.execute(code)

    state["execution_result"] = result

    if not result["success"]:
        state["errors"].append(result["error"])

    return state

def should_retry(state: AgentState) -> str:
    """Decide si reintentar o continuar"""

    if state["execution_result"]["success"]:
        return "continue"
    elif len(state["errors"]) < 3:
        return "retry"
    else:
        return "fail"

# 4. Añadir nodos al grafo
workflow.add_node("analyze", analyze_task)
workflow.add_node("generate", generate_code)
workflow.add_node("execute", execute_code)

# 5. Definir EDGES (flujo)
workflow.set_entry_point("analyze")
workflow.add_edge("analyze", "generate")
workflow.add_edge("generate", "execute")

# 6. Conditional edges (decisiones)
workflow.add_conditional_edges(
    "execute",
    should_retry,
    {
        "continue": END,
        "retry": "generate",  # Volver a generar código
        "fail": END
    }
)

# 7. Compilar el grafo
app = workflow.compile()

# 8. Ejecutar
initial_state = {
    "messages": [],
    "task_description": "Read emails from Outlook and extract PDF data",
    "current_step": 0,
    "generated_code": "",
    "execution_result": {},
    "errors": []
}

result = app.invoke(initial_state)
```

### 1.2 Ventajas de LangGraph

#### ✅ **1. State Management automático**

```python
# El STATE se pasa automáticamente entre nodos
# No necesitas gestionar manualmente el estado

workflow.add_edge("step1", "step2")
# LangGraph pasa el state de step1 a step2 automáticamente
```

#### ✅ **2. Conditional branching visual**

```python
# Decisiones complejas fáciles de visualizar
workflow.add_conditional_edges(
    "validate",
    lambda state: "save" if state["valid"] else "reject",
    {
        "save": "save_to_db",
        "reject": "send_email"
    }
)
```

#### ✅ **3. Checkpointing (persistencia de estado)**

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# Guardar estado en cada paso
memory = SqliteSaver.from_conn_string(":memory:")

app = workflow.compile(checkpointer=memory)

# Si falla, puedes reanudar desde el último checkpoint
result = app.invoke(initial_state, config={"thread_id": "123"})
```

#### ✅ **4. Human-in-the-loop**

```python
from langgraph.prebuilt import create_react_agent

# Pausar ejecución para aprobación humana
app = workflow.compile(
    checkpointer=memory,
    interrupt_before=["execute"]  # Pausa antes de ejecutar código
)

# Usuario aprueba el código generado
result = app.invoke(initial_state)
# Sistema pausa aquí

# Usuario revisa y aprueba
app.update_state(config, {"approved": True})

# Continúa ejecución
result = app.invoke(None, config)
```

#### ✅ **5. Visualización del grafo**

```python
from IPython.display import Image

# Ver el grafo visualmente
Image(app.get_graph().draw_mermaid_png())
```

### 1.3 Desventajas de LangGraph

#### ❌ **1. Inestabilidad (PROBLEMA GRAVE)**

**De la investigación**:
> "LangGraph sits on top of LangChain, a library that changes week to week, with new releases renaming classes, moving modules, or deprecating methods with little warning"

**Traducción**: Tu código puede romperse cada vez que actualizan.

**Ejemplo real**:
```python
# Código de hace 3 meses (funcionaba)
from langchain.agents import AgentExecutor

# Hoy (deprecated, código roto)
# TypeError: 'AgentExecutor' has been removed

# Ahora es:
from langgraph.prebuilt import create_react_agent
```

#### ❌ **2. Abstracción excesiva**

**De la investigación**:
> "Developers having to dig through five layers of abstraction just to customize an agent's behavior"

**Problema**: Cuando algo no funciona, es **difícil debuggear**.

```python
# Quieres controlar EXACTAMENTE qué se envía al LLM

# Con LangGraph (abstracción opaca):
result = agent.invoke(input)
# ¿Qué prompt se envió exactamente? No lo sabes sin debuggear profundo

# Con Custom (control total):
prompt = f"Generate code for: {task}"
print(f"SENDING TO LLM: {prompt}")  # Sabes exactamente qué pasa
result = llm.invoke(prompt)
```

#### ❌ **3. Curva de aprendizaje**

**De la investigación**:
> "LangGraph allows more custom control over workflow design, which means it is less abstracted and developers need to learn more to use it effectively"

Necesitas aprender:
- StateGraph API
- Conditional edges syntax
- Checkpointing system
- Message passing protocols
- LangChain compatibility

**Tiempo**: 1-2 semanas solo para entender bien LangGraph.

#### ❌ **4. Overhead de performance**

```python
# LangGraph añade overhead en cada paso:
# - Serialización de state
# - Checkpointing a DB
# - Graph traversal
# - Message passing

# Para Marito (que ejecuta muchos pasos rápido):
# Overhead = 50-100ms por nodo
# 10 nodos = 500-1000ms extra
```

---

## PARTE 2: ¿CÓMO FUNCIONA MAISA KPU?

### 2.1 Arquitectura del KPU (Knowledge Processing Unit)

Maisa creó un **sistema operativo** donde la IA es el núcleo.

**Componentes principales**:

```
┌─────────────────────────────────────────────────────┐
│                    MAISA KPU                         │
└─────────────────────────────────────────────────────┘

[1] REASONING ENGINE (Cerebro)
    │
    ├─ LLM/VLM (GPT-4, Claude, etc.)
    ├─ Step-by-step planning
    ├─ Orchestrates commands
    └─ ONLY reasons, NO data processing

[2] VIRTUAL CONTEXT WINDOW (Memoria)
    │
    ├─ Manages information flow
    ├─ Reasoning goes IN to LLM
    ├─ Data stays OUT of LLM
    └─ Maximizes token efficiency

[3] EXECUTION ENGINE (Manos)
    │
    ├─ Receives commands from Reasoning Engine
    ├─ Executes actual operations (code, API calls, DB)
    ├─ Returns results as feedback
    └─ NO hallucination risk (deterministic)
```

### 2.2 Principio Clave: Separación Reasoning ↔ Execution

**El problema que Maisa resuelve**:

```
❌ LLM tradicional (todo mezclado):
User: "Process these 1000 invoices"
LLM context:
    - Reasoning (cómo hacerlo)
    - Data (los 1000 invoices)
    - Code (el script Python)

→ Context window explota (200k tokens)
→ LLM se confunde (hallucina)
→ Caro ($50 por ejecución)
```

**Solución Maisa KPU**:

```
✅ Maisa KPU (separado):

REASONING ENGINE (LLM):
    Context: ONLY reasoning
    "Step 1: Connect to email
     Step 2: For each invoice, execute process_invoice()
     Step 3: Save results"

    → 500 tokens
    → $0.01 por ejecución

EXECUTION ENGINE (Deterministic):
    - Ejecuta process_invoice() 1000 veces
    - Procesa datos reales
    - No usa LLM
```

**Resultado**:
- 40x más barato que RAG
- Sin hallucinations en ejecución
- Context window libre para reasoning

### 2.3 Cómo funciona el flujo en Maisa

```python
# Pseudocódigo de cómo funciona Maisa KPU

class MaisaKPU:
    def __init__(self):
        self.reasoning_engine = ReasoningEngine(llm=GPT4)
        self.execution_engine = ExecutionEngine()
        self.virtual_context = VirtualContextWindow()

    def execute_task(self, task: str):
        """
        Ejecuta una tarea usando arquitectura KPU
        """

        # 1. REASONING: Planificar
        plan = self.reasoning_engine.plan(task)

        # plan = [
        #     {"command": "connect_email", "args": {...}},
        #     {"command": "for_each_pdf", "action": "extract_data"},
        #     {"command": "validate", "criteria": [...]},
        #     {"command": "save_to_db", "table": "invoices"}
        # ]

        # 2. EXECUTION: Ejecutar cada comando
        for step in plan:
            # Ejecución DETERMINISTA (sin LLM)
            result = self.execution_engine.execute(step["command"], step["args"])

            # 3. FEEDBACK al Reasoning Engine
            feedback = self.virtual_context.process_feedback(result)

            # 4. REASONING: Re-planificar si es necesario
            if not result["success"]:
                correction = self.reasoning_engine.replan(
                    original_plan=plan,
                    failed_step=step,
                    error=result["error"]
                )

                # Ejecutar corrección
                result = self.execution_engine.execute(correction)

        return final_result

# CLAVE: LLM solo razona, NUNCA ejecuta
```

### 2.4 Ventajas del enfoque Maisa

#### ✅ **1. Eficiencia de tokens**

```
Tarea: Procesar 100 facturas

❌ Sin KPU:
- Context: Reasoning + 100 facturas de datos
- Tokens: 50,000
- Costo: $0.50

✅ Con KPU:
- Context: Solo reasoning
- Tokens: 500
- Costo: $0.005
```

**100x más barato** en casos con mucha data.

#### ✅ **2. Anti-hallucination**

```python
# REASONING (LLM puede alucinar aquí, pero no importa):
plan = "Step 1: Calculate total = base * 1.21"

# EXECUTION (código determinista, NO puede alucinar):
def calculate_total(base):
    return base * 1.21  # Matemática exacta, no LLM
```

**Resultado**: Errores lógicos posibles, pero no hallucinations.

#### ✅ **3. Model-agnostic**

```python
# Cambiar de GPT-4 a Claude es trivial
reasoning_engine = ReasoningEngine(llm=Claude)

# La execution_engine no cambia (es determinista)
```

#### ✅ **4. Escalabilidad**

```python
# Procesar 10,000 items:

# REASONING (una sola vez):
plan = reasoning_engine.plan("Process all invoices")

# EXECUTION (paralelizable):
with ThreadPoolExecutor() as executor:
    results = executor.map(execution_engine.execute, items)

# LLM se usa 1 vez, no 10,000 veces
```

### 2.5 Desventajas del enfoque Maisa

#### ❌ **1. Complejidad de implementación**

Necesitas construir:
- Reasoning Engine (wrapper sobre LLM)
- Execution Engine (runtime para comandos)
- Virtual Context Window (gestión de memoria)
- Sistema de comandos completo

**Tiempo**: 3-6 meses para implementación robusta.

#### ❌ **2. No es open-source**

El KPU de Maisa es **propietario**. No puedes ver el código.

Solo sabes los **principios**, no la **implementación**.

#### ❌ **3. Requiere definir "lenguaje de comandos"**

```python
# Maisa tiene un DSL interno para comandos
# Tú tendrías que crear el tuyo

commands = {
    "connect_email": EmailConnector,
    "extract_pdf": PDFExtractor,
    "validate": Validator,
    "save_db": DatabaseWriter
}

# Cada comando necesita:
# - Interfaz clara
# - Error handling
# - Logs
# - Tests
```

**Overhead**: Crear abstracción para cada operación.

---

## PARTE 3: ORQUESTADOR CUSTOM

### 3.1 Cómo sería un orquestador custom para Marito

**Concepto**: Implementación **simple** que toma lo mejor de LangGraph (state management) y Maisa (separación reasoning/execution).

```python
# orquestador_marito.py

from typing import Dict, Any, List, Optional
import json

class MaritoOrchestrator:
    """
    Orquestador custom para Marito

    Principios:
    - Simple y entendible
    - Control total del flujo
    - Separación reasoning (LLM) y execution (sandbox)
    - State management explícito
    """

    def __init__(
        self,
        llm_client,
        sandbox_executor,
        code_cache,
        chain_logger,
        tools_catalog
    ):
        self.llm = llm_client
        self.sandbox = sandbox_executor
        self.cache = code_cache
        self.logger = chain_logger
        self.tools = tools_catalog

        # State global (simple dict)
        self.state = {}

    def execute_workflow(self, workflow_config: dict) -> dict:
        """
        Ejecuta un workflow completo

        Args:
            workflow_config: {
                "id": int,
                "description": str,
                "steps": [...],
                "credentials": {...}
            }

        Returns:
            {
                "success": bool,
                "results": {...},
                "chain_of_work": [...]
            }
        """

        # 1. Inicializar state
        self.state = {
            "workflow_id": workflow_config["id"],
            "current_step": 0,
            "steps_total": len(workflow_config["steps"]),
            "results": {},
            "errors": [],
            "credentials": workflow_config["credentials"]
        }

        # 2. Iniciar logging
        execution_id = self.logger.start_execution(
            worker_id=workflow_config["id"],
            task_description=workflow_config["description"],
            task_input=workflow_config
        )

        try:
            # 3. Ejecutar cada paso
            for step_index, step in enumerate(workflow_config["steps"]):
                self.state["current_step"] = step_index + 1

                # Ejecutar step
                result = self._execute_step(step)

                # Guardar resultado
                self.state["results"][step["step_id"]] = result

                # Si falla, decidir si continuar o parar
                if not result["success"]:
                    if step.get("critical", True):
                        # Step crítico falló → parar workflow
                        raise Exception(f"Critical step {step['step_id']} failed: {result['error']}")
                    else:
                        # Step no crítico → log warning y continuar
                        self.logger.log_step(
                            step_type="warning",
                            action=f"Step {step['step_id']} failed but not critical",
                            reasoning="Continuing workflow"
                        )

            # 4. Workflow completado
            self.logger.complete_execution(status="success")

            return {
                "success": True,
                "execution_id": execution_id,
                "results": self.state["results"],
                "chain_of_work": self.logger.get_chain(execution_id)
            }

        except Exception as e:
            # Workflow falló
            self.logger.complete_execution(status="failed", error_message=str(e))

            return {
                "success": False,
                "execution_id": execution_id,
                "error": str(e),
                "results": self.state["results"],
                "chain_of_work": self.logger.get_chain(execution_id)
            }

    def _execute_step(self, step: dict) -> dict:
        """
        Ejecuta un solo paso del workflow

        Flujo:
        1. Buscar en caché
        2. Si no existe, generar código (LLM)
        3. Ejecutar código (sandbox)
        4. Validar resultado
        5. Si falla, retry con corrección
        6. Guardar en caché si exitoso
        """

        # 1. Buscar en caché
        cached_code = self._get_code_from_cache(step)

        if cached_code:
            code = cached_code
        else:
            # 2. Generar código nuevo
            code = self._generate_code(step)

        # 3. Ejecutar con retry
        for attempt in range(1, 4):  # Max 3 intentos
            result = self._execute_code(step, code)

            if result["success"]:
                # 4. Guardar en caché
                self._save_to_cache(step, code)
                return result

            if attempt < 3:
                # 5. Corregir código
                code = self._fix_code(step, code, result["error"])

        # Falló después de 3 intentos
        return {
            "success": False,
            "error": "Max retries exceeded",
            "attempts": 3
        }

    def _generate_code(self, step: dict) -> str:
        """
        Genera código usando LLM + tool documentation
        """

        # Encontrar tools relevantes
        relevant_tools = self._find_tools_for_step(step)

        # Construir contexto de tools
        tools_context = ""
        for tool_name in relevant_tools:
            tools_context += self.tools.get_documentation(tool_name)

        # Prompt con contexto
        prompt = f"""
        Generate Python code for this step:

        STEP: {step['description']}
        INPUT: {step.get('input_from', 'previous step output')}
        OUTPUT: {step.get('output_to', 'next step')}

        AVAILABLE TOOLS:
        {tools_context}

        CREDENTIALS (inject as needed):
        {json.dumps(self.state['credentials'], indent=2)}

        PREVIOUS STEP RESULTS:
        {json.dumps(self.state['results'], indent=2)}

        Generate production-ready Python code.
        Include error handling and logging.
        """

        code = self.llm.invoke(prompt)

        self.logger.log_step(
            step_type="code_generation",
            action=f"Generated code for {step['step_id']}",
            code_generated=code,
            llm_model="gpt-4"
        )

        return code

    def _execute_code(self, step: dict, code: str) -> dict:
        """
        Ejecuta código en sandbox
        """

        result = self.sandbox.execute_code(
            code=code,
            timeout=step.get("timeout", 60)
        )

        self.logger.log_step(
            step_type="execution",
            action=f"Executed {step['step_id']}",
            stdout=result["stdout"],
            stderr=result["stderr"],
            exit_code=result.get("exit_code", -1)
        )

        return result

    # ... más métodos helper ...

# USO
orchestrator = MaritoOrchestrator(
    llm_client=openai_client,
    sandbox_executor=docker_sandbox,
    code_cache=cache_system,
    chain_logger=logger,
    tools_catalog=tools
)

# Ejecutar workflow
result = orchestrator.execute_workflow(workflow_config)
```

### 3.2 Ventajas del Custom Orchestrator

#### ✅ **1. Control total**

```python
# Sabes EXACTAMENTE qué pasa en cada línea
# No hay "magia" de frameworks
# Fácil de debuggear
```

#### ✅ **2. Estabilidad**

```python
# TÚ controlas las dependencias
# No se rompe cuando LangChain actualiza
# Código tuyo, actualizas cuando quieras
```

#### ✅ **3. Simplicidad**

```python
# ~500 líneas de código Python claro
# vs 5000 líneas de LangGraph abstracciones
```

#### ✅ **4. Performance**

```python
# Sin overhead de framework
# Sin serialización innecesaria
# Solo el código que necesitas
```

#### ✅ **5. Adaptable**

```python
# Añadir features es trivial
# Cambiar flujo es cambiar código Python normal
# No necesitas aprender DSL de framework
```

### 3.3 Desventajas del Custom Orchestrator

#### ❌ **1. Tienes que construirlo tú**

```python
# LangGraph: 2 semanas aprender + 1 semana implementar = 3 semanas
# Custom: 0 semanas aprender + 4-6 semanas implementar = 4-6 semanas

# Diferencia: 1-3 semanas más
```

#### ❌ **2. No hay tooling listo**

```python
# LangGraph tiene:
# - Visualización de grafos
# - Debugging tools
# - LangSmith integration

# Custom:
# - Builds your own logging
# - Build your own visualization
# - Build your own monitoring
```

#### ❌ **3. No hay community support**

```python
# LangGraph: Stack Overflow, Discord, docs extensas
# Custom: Solo tú y ChatGPT
```

---

## PARTE 4: COMPARACIÓN FINAL

### 4.1 Tabla Comparativa

| Aspecto | LangGraph | Maisa KPU | Custom |
|---------|-----------|-----------|--------|
| **Time to MVP** | ⚡ 3 semanas | 🐢 6+ meses | ⚡ 4-6 semanas |
| **Complejidad inicial** | 🟡 Media | 🔴 Muy alta | 🟢 Baja-Media |
| **Control** | 🟡 Medio | 🟢 Total | 🟢 Total |
| **Estabilidad** | 🔴 Baja (cambia mucho) | 🟢 Alta | 🟢 Alta |
| **Performance** | 🟡 Overhead moderado | 🟢 Optimizado | 🟢 Optimizado |
| **Debuggeability** | 🟡 Difícil (abstracciones) | 🟢 Claro | 🟢 Muy claro |
| **Learning curve** | 🔴 Alta | 🔴 Muy alta | 🟢 Baja |
| **Vendor lock-in** | 🔴 LangChain ecosystem | ⚪ Propietario | 🟢 Ninguno |
| **Escalabilidad** | 🟢 Buena | 🟢 Excelente | 🟢 Buena |
| **Community** | 🟢 Grande | ⚪ Privado | 🔴 Solo tú |
| **Costo desarrollo** | 💰 Medio | 💰💰💰 Alto | 💰💰 Medio-Alto |
| **Costo operación** | 💰💰 Overhead | 💰 Optimizado | 💰 Optimizado |

### 4.2 Casos de Uso Ideales

#### **Usar LangGraph si**:
- ✅ Necesitas MVP en 2-3 semanas
- ✅ No te importa depender de LangChain
- ✅ Valoras tooling (visualización, debugging) sobre estabilidad
- ✅ Tu equipo ya conoce LangChain/LangGraph
- ✅ Es un prototipo o proyecto temporal

#### **Usar enfoque Maisa KPU si**:
- ✅ Construyes producto enterprise de larga duración
- ✅ Procesarás MUCHA data (miles de items por workflow)
- ✅ Eficiencia de tokens es crítica (costos LLM altos)
- ✅ Tienes equipo grande (3-5 devs) y 6+ meses
- ✅ Necesitas máxima performance y anti-hallucination

#### **Usar Custom Orchestrator si**:
- ✅ Quieres control total y estabilidad
- ✅ Tiempo de desarrollo 4-6 semanas es aceptable
- ✅ Prefieres simplicidad sobre features avanzadas
- ✅ No quieres vendor lock-in
- ✅ Es un producto que mantendrás años

---

## PARTE 5: MI RECOMENDACIÓN PARA MARITO

### Opción Recomendada: **Custom Orchestrator Híbrido**

**Arquitectura**:
- Custom orchestrator (control total)
- Inspirado en principios de Maisa KPU (separación reasoning/execution)
- Sin usar LangGraph (evitar dependencias inestables)
- Código simple y mantenible

### Por qué esta opción

#### 1. **Control y estabilidad**
```python
# Tú decides cuando actualizar
# No te rompe código cada semana
# Entiendes 100% del sistema
```

#### 2. **Simplicidad suficiente**
```python
# No necesitas todo el KPU de Maisa
# Solo los principios:
# - LLM para reasoning
# - Sandbox para execution
# - State management simple
```

#### 3. **Time to market razonable**
```python
# 4-6 semanas vs 3 semanas de LangGraph
# Diferencia: 1-3 semanas
# PERO: código tuyo, estable, sin sorpresas futuras
```

#### 4. **Escalable**
```python
# Empieza simple
# Añade features cuando necesites:
#   - Checkpointing → añadir después
#   - Human-in-the-loop → añadir después
#   - Visualización → añadir después
```

### Arquitectura Concreta para Marito

```python
# marito/
#   orchestrator.py         # ~500 líneas (núcleo)
#   state_manager.py        # ~200 líneas (gestión de state)
#   code_generator.py       # ~300 líneas (LLM wrapper)
#   sandbox_executor.py     # ~400 líneas (Docker execution)
#   cache_system.py         # ~300 líneas (hash + semantic cache)
#   chain_logger.py         # ~200 líneas (auditoría)
#   tools_catalog.py        # ~200 líneas (tool documentation)
#
# TOTAL: ~2100 líneas de código Python claro
# vs LangGraph: ~5000+ líneas de abstracciones opacas
```

### Roadmap de implementación

**Semana 1-2**: Core básico
```python
- Orchestrator simple (ejecución secuencial)
- LLM integration (OpenAI)
- Sandbox básico (Docker)
- State management (dict simple)
```

**Semana 3-4**: Caché y retry
```python
- Hash-based cache
- Retry con auto-corrección
- Chain-of-work logging
```

**Semana 5-6**: Tools y polish
```python
- Tool documentation catalog
- Semantic cache (embeddings)
- Error handling robusto
```

**Semana 7+**: Features avanzadas (opcional)
```python
- Checkpointing a PostgreSQL
- Human-in-the-loop
- Dashboard web
```

---

## CONCLUSIÓN

### ❌ **NO usar LangGraph** para Marito

**Razones**:
1. Inestabilidad (código se rompe con actualizaciones)
2. Abstracciones dificultan debugging
3. Vendor lock-in a LangChain ecosystem
4. Overhead de performance innecesario

### ❌ **NO replicar Maisa KPU completo**

**Razones**:
1. Complejidad excesiva para MVP
2. 6+ meses de desarrollo
3. Sobre-engineering para caso de uso inicial

### ✅ **SÍ usar Custom Orchestrator**

**Razones**:
1. Control total del código
2. Estabilidad garantizada
3. Simplicidad y mantenibilidad
4. Escalable cuando lo necesites
5. 4-6 semanas de desarrollo razonable

**Inspiración**:
- State management de LangGraph (pero implementado simple)
- Separación reasoning/execution de Maisa KPU
- Código Python vanilla sin frameworks pesados

---

## SIGUIENTE PASO

¿Quieres que diseñemos la arquitectura concreta del Custom Orchestrator?

Incluiría:
- Código skeleton completo (~2000 líneas)
- Database schema
- API contracts entre componentes
- Ejemplo end-to-end del caso de facturas

**¿Procedemos con el diseño detallado?**
