# Agentes IA + Automatizaciones: El Futuro de los Trabajadores Digitales
## Guía Completa para Crear Agentes Inteligentes con Código

---

## RESUMEN EJECUTIVO

**La Diferencia Clave**:
- **Automatización tradicional**: "Si X entonces Y" (reglas fijas)
- **Agente IA**: "Analiza X y decide qué hacer" (inteligencia adaptativa)

**¿Cuándo usar cada uno?**:
- **Automatización**: Procesos predecibles (90% de casos)
- **Agentes IA**: Procesos que requieren decisiones inteligentes (10% de casos, pero de ALTO valor)

**La Magia**: **Combinar ambos** = Trabajadores digitales que piensan + ejecutan

---

## PARTE 1: ¿Qué es un Agente IA Realmente?

### Automatización Tradicional vs Agente IA

```
AUTOMATIZACIÓN TRADICIONAL (Como n8n, Celery):
┌──────────────────────────────────────┐
│ Email llega con factura              │
│   ↓                                  │
│ Descarga PDF (siempre)               │
│   ↓                                  │
│ Extrae datos con OCR (siempre)      │
│   ↓                                  │
│ IF total > 1000:                     │
│   → Enviar a gerente                 │
│ ELSE:                                │
│   → Aprobar automático               │
└──────────────────────────────────────┘
Lógica: FIJA (if/else)
```

```
AGENTE IA (Con LangChain, CrewAI, AutoGen):
┌────────────────────────────────────────────┐
│ Email llega con factura                    │
│   ↓                                        │
│ AGENTE ANALIZA:                            │
│ "Esta factura dice 'urgente' en asunto,   │
│  el proveedor es nuevo,                    │
│  el importe es inusual,                    │
│  hay un concepto que no reconozco"         │
│   ↓                                        │
│ AGENTE DECIDE:                             │
│ "Voy a buscar en la base de datos si      │
│  este proveedor está autorizado,           │
│  revisar facturas previas similares,       │
│  y contactar al equipo de compras          │
│  para validar el concepto desconocido"     │
│   ↓                                        │
│ AGENTE EJECUTA:                            │
│ 1. Query a base de datos                  │
│ 2. Busca facturas similares                │
│ 3. Envía email al equipo                  │
│ 4. Espera respuesta                        │
│ 5. Decide siguiente paso                   │
└────────────────────────────────────────────┘
Lógica: ADAPTATIVA (IA decide)
```

### La Diferencia en Código

**Automatización Tradicional**:
```python
@app.task
def process_invoice(pdf_data):
    # Lógica FIJA
    data = extract_data(pdf_data)

    if data['total'] > 1000:
        send_to_manager(data)
    else:
        auto_approve(data)
```

**Agente IA**:
```python
from langchain.agents import create_react_agent
from langchain.tools import Tool

# HERRAMIENTAS que el agente puede usar
tools = [
    Tool(
        name="search_provider",
        func=lambda nif: db.query(f"SELECT * FROM providers WHERE nif='{nif}'"),
        description="Busca información de un proveedor por NIF"
    ),
    Tool(
        name="search_similar_invoices",
        func=lambda concept: db.query(f"SELECT * FROM invoices WHERE concept LIKE '%{concept}%'"),
        description="Busca facturas con conceptos similares"
    ),
    Tool(
        name="send_email",
        func=lambda to, msg: email.send(to, msg),
        description="Envía un email al equipo"
    ),
    Tool(
        name="approve_invoice",
        func=lambda invoice_id: db.update(invoice_id, status='approved'),
        description="Aprueba una factura"
    )
]

# AGENTE que usa las herramientas
agent = create_react_agent(
    llm=ChatOpenAI(model="gpt-4"),
    tools=tools,
    prompt="""Eres un asistente de facturación.

    Cuando recibes una factura:
    1. Analiza si el proveedor está autorizado
    2. Revisa si hay facturas similares previas
    3. Si algo es inusual, consulta al equipo
    4. Decide si aprobar o rechazar

    Piensa paso a paso y usa las herramientas disponibles."""
)

# EJECUTAR
result = agent.invoke({
    "input": f"Procesa esta factura: {invoice_data}"
})

# El agente DECIDE qué hacer:
# - "Voy a buscar primero al proveedor..."
# - "Hmm, no está en la BD, voy a buscar facturas similares..."
# - "Encontré una factura similar del año pasado, voy a aprobar"
# O:
# - "No encuentro nada, voy a enviar email al equipo..."
```

### Características de un Agente IA

1. **Autonomía**: Decide qué pasos seguir
2. **Razonamiento**: "Piensa" antes de actuar
3. **Herramientas**: Usa múltiples funciones según necesidad
4. **Memoria**: Recuerda contexto previo
5. **Adaptabilidad**: Se ajusta a situaciones nuevas

---

## PARTE 2: Frameworks de Agentes IA (2025)

### Comparativa de Frameworks

| Framework | Dificultad | Mejor Para | Puntos Fuertes |
|-----------|------------|------------|----------------|
| **LangChain** | Media | Agentes con RAG, workflows complejos | Ecosistema enorme, muchas integraciones |
| **LangGraph** | Alta | Workflows con estados complejos | Control total del flujo, debugging |
| **CrewAI** | Baja | Multi-agentes con roles | Muy fácil de usar, colaboración |
| **AutoGen** | Media | Conversaciones multi-agente | Agentes que "hablan" entre sí |
| **LlamaIndex** | Media | Agentes con documentos/datos | RAG especializado |

### 1. LangChain (El Más Popular)

**Cuándo usar**: Agente simple que usa herramientas

**Ejemplo Real - Agente de Soporte al Cliente**:
```python
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.tools import Tool

# HERRAMIENTAS
def get_order_status(order_id: str) -> str:
    """Obtiene el estado de un pedido"""
    return db.query(f"SELECT status FROM orders WHERE id={order_id}")

def cancel_order(order_id: str) -> str:
    """Cancela un pedido"""
    return db.update(f"UPDATE orders SET status='cancelled' WHERE id={order_id}")

def search_faq(question: str) -> str:
    """Busca en la base de conocimiento"""
    # RAG sobre documentación
    return vector_db.similarity_search(question)

tools = [
    Tool(name="get_order_status", func=get_order_status, description="..."),
    Tool(name="cancel_order", func=cancel_order, description="..."),
    Tool(name="search_faq", func=search_faq, description="...")
]

# AGENTE
llm = ChatOpenAI(model="gpt-4", temperature=0)
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# USO
customer_message = "Hola, mi pedido #12345 no ha llegado, ¿puedo cancelarlo?"

response = agent_executor.invoke({"input": customer_message})

# El agente decide:
# 1. "Primero voy a revisar el estado del pedido #12345"
# 2. "El pedido está en tránsito, voy a explicar al cliente"
# 3. "Pero mencionó cancelación, voy a buscar política de cancelación"
# 4. "Pedidos en tránsito no se pueden cancelar, voy a explicar opciones"
```

**Salida del Agente** (reasoning visible):
```
> Entering new AgentExecutor chain...

Thought: Primero necesito revisar el estado del pedido.

Action: get_order_status
Action Input: "12345"
Observation: {"status": "in_transit", "estimated_delivery": "2025-01-17"}

Thought: El pedido está en tránsito. Voy a buscar la política de cancelación.

Action: search_faq
Action Input: "cancelar pedido en tránsito"
Observation: "Pedidos en tránsito no pueden cancelarse, pero puedes rechazar el paquete al recibirlo"

Thought: Ya tengo suficiente información para responder.

Final Answer: Hola! Tu pedido #12345 está actualmente en tránsito y llegará mañana (17 de enero).
Los pedidos en tránsito no se pueden cancelar desde el sistema, pero puedes rechazar el paquete
cuando llegue y te haremos el reembolso completo. ¿Te parece bien esta opción?
```

### 2. CrewAI (El Más Fácil para Multi-Agentes)

**Cuándo usar**: Varios agentes colaborando (como un equipo)

**Ejemplo Real - Análisis de Facturas Multi-Agente**:
```python
from crewai import Agent, Task, Crew

# AGENTE 1: Extractor
extractor = Agent(
    role='Extractor de Datos',
    goal='Extraer todos los datos relevantes de la factura',
    backstory='Experto en OCR y extracción de documentos',
    tools=[ocr_tool, pdf_parser_tool],
    verbose=True
)

# AGENTE 2: Validador
validator = Agent(
    role='Validador de Facturas',
    goal='Validar que todos los datos sean correctos y cumplan reglas de negocio',
    backstory='Auditor con 10 años de experiencia en facturación',
    tools=[nif_validator_tool, calculation_validator_tool, db_lookup_tool],
    verbose=True
)

# AGENTE 3: Decisor
approver = Agent(
    role='Aprobador de Facturas',
    goal='Decidir si aprobar o rechazar la factura basado en análisis',
    backstory='Manager de finanzas que toma decisiones basadas en datos',
    tools=[email_tool, db_update_tool],
    verbose=True
)

# TAREAS
extract_task = Task(
    description='Extrae todos los datos de la factura PDF: {invoice_pdf}',
    agent=extractor,
    expected_output='Objeto JSON con: número, proveedor, NIF, conceptos, total, IVA'
)

validate_task = Task(
    description='Valida los datos extraídos: {extracted_data}. Verifica NIF, cálculos, proveedor autorizado.',
    agent=validator,
    expected_output='Informe de validación con OK/ERROR y razones',
    context=[extract_task]  # Depende de extract_task
)

approve_task = Task(
    description='Basado en el informe de validación, decide aprobar o rechazar.',
    agent=approver,
    expected_output='Decisión final: APROBADA/RECHAZADA con justificación',
    context=[extract_task, validate_task]  # Depende de ambas
)

# CREW (Equipo)
invoice_crew = Crew(
    agents=[extractor, validator, approver],
    tasks=[extract_task, validate_task, approve_task],
    verbose=True
)

# EJECUTAR
result = invoice_crew.kickoff(inputs={'invoice_pdf': pdf_data})
```

**Salida del Crew** (colaboración visible):
```
[Extractor] Analizando PDF...
[Extractor] Encontré: Factura #F-2025-001, Proveedor: Acme Corp, NIF: B12345678, Total: 1,245.50€

[Validator] Revisando datos del Extractor...
[Validator] ✓ NIF válido
[Validator] ✓ Cálculos correctos
[Validator] ✓ Proveedor autorizado en sistema
[Validator] ⚠️ Monto superior a límite de aprobación automática (€1,000)

[Approver] Revisando informe del Validator...
[Approver] Todos los datos son correctos, pero monto > €1,000.
[Approver] DECISIÓN: Enviar a gerente para aprobación manual.
[Approver] Email enviado a gerente@empresa.com
```

### 3. LangGraph (El Más Potente)

**Cuándo usar**: Workflows complejos con múltiples estados y branches

**Ejemplo Real - Onboarding de Cliente**:
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated

# ESTADO
class OnboardingState(TypedDict):
    customer_email: str
    data_collected: dict
    documents_verified: bool
    account_created: bool
    welcome_sent: bool
    errors: list

# NODOS (cada uno puede ser un agente o función)
def collect_customer_data(state: OnboardingState):
    """Agente que pregunta datos al cliente"""
    agent = create_agent_with_tools([email_tool, form_tool])
    result = agent.invoke(f"Solicita datos de onboarding a {state['customer_email']}")
    return {"data_collected": result}

def verify_documents(state: OnboardingState):
    """Agente que verifica documentos con IA"""
    agent = create_agent_with_tools([ocr_tool, validation_tool])
    result = agent.invoke(f"Verifica documentos: {state['data_collected']['documents']}")
    return {"documents_verified": result['valid']}

def create_account(state: OnboardingState):
    """Automatización que crea cuenta"""
    if state['documents_verified']:
        account = db.create_account(state['data_collected'])
        return {"account_created": True}
    else:
        return {"account_created": False, "errors": ["Documentos inválidos"]}

def send_welcome(state: OnboardingState):
    """Agente que personaliza y envía bienvenida"""
    agent = create_agent_with_tools([email_tool, template_tool])
    agent.invoke(f"Envía email de bienvenida personalizado a {state['customer_email']}")
    return {"welcome_sent": True}

def handle_errors(state: OnboardingState):
    """Agente que maneja errores y notifica"""
    agent = create_agent_with_tools([email_tool, slack_tool])
    agent.invoke(f"Notifica errores: {state['errors']}")
    return state

# GRAFO
workflow = StateGraph(OnboardingState)

# Agregar nodos
workflow.add_node("collect_data", collect_customer_data)
workflow.add_node("verify_docs", verify_documents)
workflow.add_node("create_account", create_account)
workflow.add_node("send_welcome", send_welcome)
workflow.add_node("handle_errors", handle_errors)

# Definir flujo
workflow.set_entry_point("collect_data")
workflow.add_edge("collect_data", "verify_docs")

# CONDITIONAL: Si docs OK → crear cuenta, sino → error
workflow.add_conditional_edges(
    "verify_docs",
    lambda state: "create_account" if state['documents_verified'] else "handle_errors"
)

workflow.add_edge("create_account", "send_welcome")
workflow.add_edge("send_welcome", END)
workflow.add_edge("handle_errors", END)

# COMPILAR
app = workflow.compile()

# EJECUTAR
result = app.invoke({
    "customer_email": "nuevo@cliente.com",
    "data_collected": {},
    "documents_verified": False,
    "account_created": False,
    "welcome_sent": False,
    "errors": []
})
```

**Ventaja de LangGraph**: Puedes ver y controlar EXACTAMENTE el flujo, con estados persistentes.

---

## PARTE 3: Patrones de Agentes + Automatizaciones

### Patrón 1: "Agente Decide, Automatización Ejecuta"

```python
# AGENTE: Analiza y decide
agent_decision = agent.invoke({
    "input": f"Analiza esta factura y decide si necesita aprobación manual: {invoice_data}"
})

# AUTOMATIZACIÓN: Ejecuta la decisión
if agent_decision['needs_manual_approval']:
    # Workflow automático
    send_to_manager.delay(invoice_data)
    create_approval_task.delay(invoice_data)
    notify_team.delay(invoice_data)
else:
    # Workflow automático
    auto_approve.delay(invoice_data)
    update_accounting.delay(invoice_data)
    send_confirmation.delay(invoice_data)
```

**Ejemplo Real**: Sistema de Facturas Inteligente

```python
from langchain.agents import create_react_agent
from celery import Celery

# AGENTE: Analiza factura
invoice_analyzer = create_react_agent(
    llm=ChatOpenAI(model="gpt-4"),
    tools=[
        search_provider_tool,
        search_similar_invoices_tool,
        calculate_risk_score_tool
    ],
    prompt="""Analiza facturas y decide si necesitan revisión manual.

    Factores a considerar:
    - Proveedor nuevo o no autorizado
    - Monto inusualmente alto o bajo
    - Conceptos desconocidos
    - Patrones sospechosos

    Da un score de riesgo (0-100) y recomendación."""
)

# WORKERS DE AUTOMATIZACIÓN
celery_app = Celery('workers', broker='redis://localhost')

@celery_app.task
def process_invoice_with_agent(invoice_data):
    # 1. AGENTE decide
    analysis = invoice_analyzer.invoke({
        "input": f"Analiza: {invoice_data}"
    })

    risk_score = analysis['risk_score']

    # 2. AUTOMATIZACIÓN ejecuta según decisión
    if risk_score > 70:
        # Alto riesgo → workflow manual
        send_to_fraud_team.delay(invoice_data, analysis)
        create_investigation_ticket.delay(invoice_data)
        hold_payment.delay(invoice_data)
    elif risk_score > 30:
        # Riesgo medio → aprobación manager
        send_to_manager.delay(invoice_data, analysis)
        create_approval_task.delay(invoice_data)
    else:
        # Bajo riesgo → automático
        auto_approve.delay(invoice_data)
        schedule_payment.delay(invoice_data)
        update_accounting.delay(invoice_data)
        send_confirmation_email.delay(invoice_data)
```

### Patrón 2: "Multi-Agente Colaborativo"

```python
# CREW de agentes especializados
from crewai import Agent, Task, Crew

# Agente 1: Investigador
researcher = Agent(
    role='Investigador de Mercado',
    goal='Investigar competencia y tendencias',
    tools=[web_search_tool, scraping_tool, analysis_tool]
)

# Agente 2: Escritor
writer = Agent(
    role='Redactor de Contenido',
    goal='Crear contenido optimizado SEO',
    tools=[seo_tool, grammar_tool, template_tool]
)

# Agente 3: Editor
editor = Agent(
    role='Editor Jefe',
    goal='Revisar y mejorar contenido',
    tools=[quality_check_tool, plagiarism_tool]
)

# TAREAS
research_task = Task(
    description='Investiga sobre: {topic}',
    agent=researcher
)

write_task = Task(
    description='Escribe artículo basado en investigación',
    agent=writer,
    context=[research_task]
)

edit_task = Task(
    description='Edita y mejora el artículo',
    agent=editor,
    context=[write_task]
)

# CREW
content_crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, write_task, edit_task]
)

# EJECUTAR
article = content_crew.kickoff(inputs={'topic': 'IA en automatización empresarial'})

# AUTOMATIZACIÓN: Publicar resultado
publish_to_blog.delay(article)
schedule_social_posts.delay(article)
notify_subscribers.delay(article)
```

### Patrón 3: "Agente con Memoria + Contexto"

```python
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor

# MEMORIA persistente
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# AGENTE con memoria
customer_support_agent = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,  # ← MEMORIA
    verbose=True
)

# CONVERSACIÓN 1
response1 = customer_support_agent.invoke({
    "input": "Hola, mi pedido #12345 no llegó"
})
# Agente recuerda: cliente tiene problema con pedido #12345

# CONVERSACIÓN 2 (días después)
response2 = customer_support_agent.invoke({
    "input": "Hola, soy yo otra vez"
})
# Agente recuerda: "Ah sí, el cliente del pedido #12345. Déjame revisar estado actual..."
```

---

## PARTE 4: Casos de Uso Reales - Cuándo Usar Qué

### Caso 1: Procesamiento de Facturas

**Opción A: Solo Automatización** (n8n o Celery)
```
✅ SI:
- Todas las facturas tienen mismo formato
- Reglas de validación son claras y fijas
- No necesitas adaptar lógica según contexto

Workflow:
Email → OCR → Validar NIF → Calcular IVA → IF total > 1000 → Manager ELSE → Auto-aprobar
```

**Opción B: Agente IA + Automatización** (Recomendado)
```
✅ SI:
- Facturas vienen en múltiples formatos
- Proveedores nuevos aparecen
- Necesitas detectar anomalías
- Requieres decisiones contextuales

Workflow:
Email → AGENTE analiza contexto → Decide riesgo → Automatización ejecuta flujo apropiado
```

**Código Híbrido**:
```python
@celery_app.task
def intelligent_invoice_processing(invoice_pdf):
    # 1. Automatización: OCR (siempre igual)
    extracted_data = ocr_service.extract(invoice_pdf)

    # 2. AGENTE: Análisis inteligente
    agent_analysis = invoice_agent.invoke({
        "input": f"""Analiza esta factura:

        Proveedor: {extracted_data['provider']}
        Total: {extracted_data['total']}
        Conceptos: {extracted_data['items']}

        Compara con histórico y detecta anomalías."""
    })

    # 3. Automatización: Ejecuta según análisis
    if agent_analysis['anomaly_detected']:
        # Workflow de revisión manual
        fraud_investigation_workflow.delay(invoice_pdf, agent_analysis)
    elif agent_analysis['risk_score'] > 50:
        # Workflow de aprobación manager
        manager_approval_workflow.delay(invoice_pdf, agent_analysis)
    else:
        # Workflow automático
        auto_approval_workflow.delay(invoice_pdf)
```

### Caso 2: Soporte al Cliente

**Solo Automatización** (Chatbot con reglas):
```python
def chatbot_rules(user_message):
    if "pedido" in user_message.lower():
        return "Para consultar tu pedido, visita: ..."
    elif "cancelar" in user_message.lower():
        return "Para cancelar, haz click en: ..."
    else:
        return "No entiendo, contacta a soporte@..."
```

**Agente IA** (Inteligente):
```python
support_agent = create_agent_with_tools([
    get_order_tool,
    cancel_order_tool,
    search_kb_tool,
    create_ticket_tool
])

# El agente ENTIENDE intención y contexto
response = support_agent.invoke({
    "input": "Mi paquete llegó roto y necesito un reembolso urgente"
})

# Agente decide:
# 1. Buscar política de devoluciones
# 2. Verificar si pedido es elegible
# 3. Iniciar proceso de reembolso
# 4. Crear ticket de prioridad alta
# 5. Responder con pasos siguientes
```

### Caso 3: Generación de Reportes

**Solo Automatización** (Reporte fijo):
```python
@celery_app.task
def generate_monthly_report():
    # Siempre igual
    sales = db.query("SELECT SUM(total) FROM sales WHERE month=...")
    customers = db.query("SELECT COUNT(*) FROM customers WHERE...")

    report = f"""
    Ventas: {sales}
    Clientes: {customers}
    """

    send_email(report)
```

**Agente IA** (Reporte inteligente):
```python
report_agent = create_agent_with_tools([
    query_database_tool,
    analyze_trends_tool,
    generate_insights_tool,
    create_visualization_tool
])

response = report_agent.invoke({
    "input": """Genera reporte mensual de ventas.

    Incluye:
    - Comparación con mes anterior
    - Tendencias detectadas
    - Productos top
    - Recomendaciones basadas en datos
    """
})

# Agente genera reporte PERSONALIZADO con insights reales
```

---

## PARTE 5: Stack Completo - Agentes + Automatizaciones

### Arquitectura Recomendada

```
┌─────────────────────────────────────────────────────┐
│                  CAPA DE AGENTES IA                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│  LangChain Agents (Decisiones inteligentes)        │
│  ├─ Invoice Analyzer Agent                         │
│  ├─ Customer Support Agent                         │
│  ├─ Content Generator Agent                        │
│  └─ Fraud Detection Agent                          │
│                                                     │
│         ↓ (Decisiones) ↓                           │
│                                                     │
├─────────────────────────────────────────────────────┤
│            CAPA DE AUTOMATIZACIÓN                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Celery Workers (Ejecución de tareas)              │
│  ├─ Email Workflows                                │
│  ├─ Database Operations                            │
│  ├─ File Processing                                │
│  ├─ API Integrations                               │
│  └─ Notifications                                  │
│                                                     │
│         ↓ (Almacenamiento) ↓                       │
│                                                     │
├─────────────────────────────────────────────────────┤
│                 CAPA DE DATOS                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  PostgreSQL (Datos estructurados)                  │
│  Qdrant/Pinecone (Vectores para RAG)              │
│  Redis (Cola + Cache)                              │
│  S3 (Archivos)                                     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Setup Completo en Código

**requirements.txt**:
```
# Agentes IA
langchain==0.1.0
langchain-openai==0.0.5
langgraph==0.0.20
crewai==0.1.0

# Automatización
celery==5.3.4
redis==5.0.1
fastapi==0.109.0
sqlalchemy==2.0.25

# RAG & Vectores
chromadb==0.4.22
sentence-transformers==2.3.1

# Utilidades
python-dotenv==1.0.0
pydantic==2.5.3
```

**Proyecto Estructura**:
```
intelligent-automation/
├── agents/
│   ├── invoice_agent.py        # Agente de facturas
│   ├── support_agent.py        # Agente de soporte
│   └── tools/
│       ├── database_tools.py
│       ├── email_tools.py
│       └── rag_tools.py
├── workers/
│   ├── invoice_workers.py      # Workers Celery
│   ├── email_workers.py
│   └── notification_workers.py
├── api/
│   ├── main.py                 # FastAPI
│   └── routes/
│       ├── invoices.py
│       └── agents.py
├── database/
│   ├── models.py
│   └── vector_store.py
├── docker-compose.yml
└── .env
```

### Código Completo: Sistema Inteligente de Facturas

**agents/invoice_agent.py**:
```python
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from database import db
from services import ocr_service

# HERRAMIENTAS para el agente
def search_provider(nif: str) -> str:
    """Busca proveedor en base de datos"""
    provider = db.query(f"SELECT * FROM providers WHERE nif='{nif}'")
    if provider:
        return f"Proveedor encontrado: {provider.name}, Autorizado: {provider.authorized}, Facturas previas: {provider.invoice_count}"
    return "Proveedor NO encontrado en sistema"

def search_similar_invoices(concept: str, amount: float) -> str:
    """Busca facturas similares"""
    invoices = db.query(f"""
        SELECT * FROM invoices
        WHERE concept LIKE '%{concept}%'
        AND amount BETWEEN {amount*0.8} AND {amount*1.2}
        ORDER BY created_at DESC LIMIT 5
    """)
    return f"Encontradas {len(invoices)} facturas similares en últimos 6 meses"

def calculate_risk_score(invoice_data: dict) -> dict:
    """Calcula score de riesgo basado en múltiples factores"""
    score = 0
    factors = []

    # Proveedor nuevo
    if not db.provider_exists(invoice_data['nif']):
        score += 30
        factors.append("Proveedor nuevo (+30)")

    # Monto inusual
    avg_amount = db.get_avg_invoice_amount()
    if invoice_data['total'] > avg_amount * 2:
        score += 25
        factors.append(f"Monto 2x superior al promedio (+25)")

    # Conceptos desconocidos
    known_concepts = db.get_all_concepts()
    if invoice_data['concept'] not in known_concepts:
        score += 20
        factors.append("Concepto no reconocido (+20)")

    return {
        "score": score,
        "level": "high" if score > 50 else "medium" if score > 25 else "low",
        "factors": factors
    }

# TOOLS
tools = [
    Tool(
        name="search_provider",
        func=search_provider,
        description="Busca información de un proveedor por NIF. Útil para verificar si está autorizado."
    ),
    Tool(
        name="search_similar_invoices",
        func=search_similar_invoices,
        description="Busca facturas con conceptos y montos similares. Útil para detectar patrones."
    ),
    Tool(
        name="calculate_risk_score",
        func=calculate_risk_score,
        description="Calcula score de riesgo (0-100) basado en múltiples factores."
    )
]

# PROMPT
prompt = ChatPromptTemplate.from_messages([
    ("system", """Eres un asistente experto en análisis de facturas.

Tu trabajo es:
1. Analizar facturas recibidas
2. Verificar proveedores
3. Detectar anomalías o riesgos
4. Dar una recomendación clara: APROBAR, REVISAR_MANUAL, o RECHAZAR

Piensa paso a paso y usa las herramientas disponibles para tomar la mejor decisión.

Factores a considerar:
- ¿El proveedor está autorizado?
- ¿El monto es razonable?
- ¿Hay facturas similares previas?
- ¿Los conceptos son reconocidos?

Devuelve tu análisis en este formato JSON:
{{
    "decision": "APROBAR|REVISAR_MANUAL|RECHAZAR",
    "risk_score": 0-100,
    "reasoning": "Explicación detallada",
    "next_steps": ["acción 1", "acción 2"]
}}"""),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

# AGENTE
llm = ChatOpenAI(model="gpt-4", temperature=0)
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def analyze_invoice(invoice_data: dict) -> dict:
    """Función principal para analizar factura con agente"""

    response = agent_executor.invoke({
        "input": f"""Analiza esta factura:

        Número: {invoice_data['numero']}
        Proveedor: {invoice_data['proveedor']}
        NIF: {invoice_data['nif']}
        Concepto: {invoice_data['concepto']}
        Base: {invoice_data['base']}€
        IVA: {invoice_data['iva']}€
        Total: {invoice_data['total']}€
        """
    })

    return response['output']
```

**workers/invoice_workers.py**:
```python
from celery import Celery
from agents.invoice_agent import analyze_invoice
from services import email_service, db_service

app = Celery('invoice_workers', broker='redis://localhost:6379')

@app.task
def process_invoice_intelligent(pdf_data, sender):
    """
    Worker que combina Agente IA + Automatización
    """

    # PASO 1: Automatización - OCR (siempre igual)
    print("📄 Extrayendo datos con OCR...")
    extracted_data = ocr_service.extract(pdf_data)

    # PASO 2: Agente IA - Análisis inteligente
    print("🤖 Analizando con IA...")
    agent_analysis = analyze_invoice(extracted_data)

    print(f"Decisión del agente: {agent_analysis['decision']}")
    print(f"Risk score: {agent_analysis['risk_score']}")
    print(f"Reasoning: {agent_analysis['reasoning']}")

    # PASO 3: Automatización - Ejecutar según decisión del agente
    if agent_analysis['decision'] == 'APROBAR':
        # Workflow automático de aprobación
        auto_approve_workflow.delay(extracted_data)

    elif agent_analysis['decision'] == 'REVISAR_MANUAL':
        # Workflow de revisión manual
        manual_review_workflow.delay(extracted_data, agent_analysis)

    else:  # RECHAZAR
        # Workflow de rechazo
        reject_workflow.delay(extracted_data, agent_analysis)

@app.task
def auto_approve_workflow(invoice_data):
    """Workflow automático aprobación"""
    db_service.save_invoice(invoice_data, status='APPROVED')
    db_service.schedule_payment(invoice_data)
    email_service.send_confirmation(invoice_data)
    email_service.send_to_fundacion(invoice_data)
    print("✅ Factura aprobada automáticamente")

@app.task
def manual_review_workflow(invoice_data, analysis):
    """Workflow revisión manual"""
    db_service.save_invoice(invoice_data, status='PENDING_REVIEW')
    ticket_id = db_service.create_review_ticket(invoice_data, analysis)
    email_service.notify_manager(invoice_data, analysis, ticket_id)
    print(f"⚠️ Factura enviada a revisión manual (Ticket #{ticket_id})")

@app.task
def reject_workflow(invoice_data, analysis):
    """Workflow rechazo"""
    db_service.save_invoice(invoice_data, status='REJECTED')
    email_service.notify_provider_rejection(
        invoice_data['sender'],
        analysis['reasoning']
    )
    print("❌ Factura rechazada")
```

**api/main.py**:
```python
from fastapi import FastAPI, File, UploadFile
from workers.invoice_workers import process_invoice_intelligent

app = FastAPI()

@app.post("/process-invoice")
async def process_invoice(file: UploadFile):
    """Endpoint para procesar factura con agente inteligente"""

    pdf_data = await file.read()

    # Enviar a cola para procesamiento asíncrono
    task = process_invoice_intelligent.delay(pdf_data, "webhook")

    return {
        "status": "queued",
        "task_id": task.id,
        "message": "Invoice sent to intelligent processing"
    }

@app.get("/task/{task_id}")
def get_task_status(task_id: str):
    """Ver estado de tarea"""
    from celery.result import AsyncResult

    result = AsyncResult(task_id)

    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None
    }
```

---

## PARTE 6: Comparativa Final & Recomendaciones

### Cuándo Usar Cada Approach

| Escenario | Solo Automatización | Agentes IA | Híbrido (Recomendado) |
|-----------|---------------------|------------|----------------------|
| **Proceso 100% predecible** | ✅ Ideal | ❌ Overkill | ⚠️ Opcional |
| **Necesita decisiones contextuales** | ❌ No puede | ✅ Perfecto | ✅ Perfecto |
| **Múltiples formatos de entrada** | ⚠️ Difícil | ✅ Excelente | ✅ Excelente |
| **Detección de anomalías** | ❌ No puede | ✅ Excelente | ✅ Excelente |
| **Alta precisión requerida** | ✅ Buena | ⚠️ Depende LLM | ✅ Mejor |
| **Bajo costo** | ✅ Muy bajo | ❌ Caro (API LLM) | ⚠️ Medio |
| **Explicabilidad** | ✅ Total | ⚠️ Limitada | ✅ Buena |

### Costes Comparados

**Solo Automatización** (Celery):
- Desarrollo: €3k
- Infra: €30/mes
- Por ejecución: €0.001
- **Total año 1**: €3,360

**Solo Agentes IA** (LangChain):
- Desarrollo: €5k
- Infra: €50/mes
- Por ejecución: €0.02 (llamadas LLM)
- 1000 facturas/mes = €20/mes LLM
- **Total año 1**: €5,840

**Híbrido** (Recomendado):
- Desarrollo: €4k
- Infra: €40/mes
- Por ejecución: €0.005 (solo agente cuando necesario)
- 1000 facturas/mes, 20% necesita agente = €4/mes LLM
- **Total año 1**: €4,528

**ROI**: Híbrido es solo 15% más caro que automatización pura, pero con capacidades 10x mejores.

### Tu Plan de Acción Recomendado

#### FASE 1: Empezar con Automatización Pura (Semana 1-2)

```python
# Sistema básico Celery
@app.task
def process_invoice_basic(pdf_data):
    data = ocr_extract(pdf_data)
    if validate_simple(data):
        approve(data)
    else:
        reject(data)
```

**Resultado**: Sistema funcionando rápido

#### FASE 2: Agregar Agente para Casos Complejos (Semana 3-4)

```python
@app.task
def process_invoice_smart(pdf_data):
    data = ocr_extract(pdf_data)

    # Automatización simple primero
    simple_validation = validate_simple(data)

    if simple_validation.passed:
        approve(data)
    elif simple_validation.clearly_invalid:
        reject(data)
    else:
        # ⭐ AGENTE solo para casos complejos
        agent_decision = invoice_agent.analyze(data)
        execute_decision(agent_decision)
```

**Resultado**: 80% automatización pura (rápido/barato), 20% con agente (inteligente)

#### FASE 3: Multi-Agentes (Mes 2-3)

```python
# CrewAI para procesos complejos
invoice_crew = Crew(
    agents=[extractor_agent, validator_agent, approver_agent],
    tasks=[extract_task, validate_task, approve_task]
)
```

**Resultado**: Sistema enterprise-grade

---

## CONCLUSIÓN FINAL

### Para Tu Sistema de Facturas:

**Recomendación**: **Híbrido - Automatización + Agente IA**

```python
# ARQUITECTURA PERFECTA para facturas

# 80% de casos: Automatización pura (rápido, barato)
if factura_es_simple(data):
    workflow_automatico(data)

# 20% de casos: Agente IA (inteligente, adaptable)
else:
    decision_agente = invoice_agent.analyze(data)
    workflow_segun_agente(decision_agente)
```

**Beneficios**:
1. ✅ Rápido y económico para casos simples
2. ✅ Inteligente para casos complejos
3. ✅ Escalable (no todos necesitan agente)
4. ✅ ROI alto (pagas LLM solo cuando necesitas)
5. ✅ Diferenciación (competencia usa solo automatización)

### Stack Final Recomendado:

```
AGENTES:
- LangChain (agente simple con tools)
- CrewAI (si necesitas multi-agente después)

AUTOMATIZACIÓN:
- Celery + Redis (workers)
- FastAPI (API)
- PostgreSQL (datos)

DESARROLLO:
- Claude Code (genera todo en días)
- Docker Compose
- Pytest

DEPLOY:
- VPS €40/mes
- O Railway/Render
```

### Próximos Pasos:

¿Quiero que te genere el **código completo** del sistema de facturas híbrido?

Incluiría:
1. ✅ Agente IA de análisis de facturas (LangChain)
2. ✅ Workers de automatización (Celery)
3. ✅ API REST (FastAPI)
4. ✅ Setup completo Docker
5. ✅ Panel web React (básico)
6. ✅ Tests unitarios

**Todo listo para** `docker-compose up` **y empezar a trabajar**.

¿Empezamos?
