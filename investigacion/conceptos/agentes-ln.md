# Agentes con LangChain: Lo que REALMENTE Necesitas

Ahora vamos con los AGENTES. Te voy a explicar qué necesitas instalar, cómo funcionan, y en qué se diferencian de las automatizaciones.

---

## LA DIFERENCIA FUNDAMENTAL

### Automatización (lo que ya sabes):
```python
# SIEMPRE hace lo mismo - pasos fijos
def procesar_factura(email_id):
    pdf = descargar_pdf(email_id)
    datos = extraer_datos(pdf)
    if validar_nif(datos.nif):
        guardar_en_db(datos)
    else:
        enviar_error()
```
→ Código determinista: si A entonces B, siempre igual.

### Agente (lo nuevo):
```python
# El LLM DECIDE qué hacer según la situación
agent = create_agent(
    llm=ChatOpenAI(model="gpt-4"),
    tools=[descargar_pdf, extraer_datos, validar_nif, buscar_proveedor, enviar_email],
    prompt="Analiza la factura y decide si aprobarla, rechazarla o pedir más info"
)

resultado = agent.invoke({"email_id": "email_123"})

# El agente podría decidir:
# - Llamar a descargar_pdf()
# - Luego llamar a extraer_datos()
# - Luego llamar a buscar_proveedor() para investigar
# - Si encuentra algo sospechoso, llamar a enviar_email()
# - O si todo OK, aprobar directamente
```
→ El LLM decide en cada momento qué herramienta usar y por qué.

---

## ¿QUÉ NECESITAS INSTALAR?

### 1. OpenAI API (o cualquier LLM)

**¿Qué es?**
El "cerebro" del agente. Es el LLM (GPT-4, Claude, etc.) que toma decisiones.

**Instalación:**
```bash
pip install openai
```

**Configuración:**
```python
import openai
import os

# Configurar tu API key
os.environ["OPENAI_API_KEY"] = "sk-..."

# O directamente en el código
openai.api_key = "sk-..."
```

**Obtener API key:**
1. Ir a https://platform.openai.com/
2. Crear cuenta
3. Ir a API Keys
4. Crear nueva key
5. Copiar la key (empieza con `sk-...`)

**Costes (importantes):**
- GPT-4 Turbo: $0.01 por 1K tokens de input, $0.03 por 1K tokens de output
- GPT-3.5 Turbo: $0.0005 por 1K tokens de input, $0.0015 por 1K tokens de output

**¿Cuánto cuesta una ejecución de agente?**
- Agente simple (GPT-4): ~5K tokens = ~$0.02 por ejecución
- Agente complejo (GPT-4): ~20K tokens = ~$0.08 por ejecución
- Agente simple (GPT-3.5): ~5K tokens = ~$0.003 por ejecución

**Ejemplo: 1000 facturas/mes procesadas con agente:**
- Con GPT-4: ~$20-80/mes
- Con GPT-3.5: ~$3-10/mes

---

### 2. LangChain - El framework de agentes

**¿Qué es LangChain?**
Una librería de Python que facilita crear agentes que usan LLMs. Te da:
- Componentes pre-hechos para agentes
- Sistema de "tools" (herramientas que el agente puede usar)
- Manejo de memoria y contexto
- Integración con múltiples LLMs

**Instalación:**
```bash
pip install langchain langchain-openai
```

**Componentes principales:**

```python
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate

# 1. El LLM (el cerebro)
llm = ChatOpenAI(model="gpt-4", temperature=0)

# 2. Las herramientas (tools) que el agente puede usar
tools = [
    Tool(
        name="buscar_proveedor",
        func=buscar_proveedor_en_db,
        description="Busca un proveedor en la base de datos por NIF. Input: NIF (string)."
    ),
    Tool(
        name="validar_nif",
        func=validar_nif,
        description="Valida si un NIF español es válido. Input: NIF (string). Output: True/False."
    ),
    Tool(
        name="calcular_riesgo",
        func=calcular_score_riesgo,
        description="Calcula el score de riesgo de una factura. Input: dict con nif, importe, fecha. Output: score 0-100."
    )
]

# 3. El prompt (las instrucciones para el agente)
prompt = ChatPromptTemplate.from_messages([
    ("system", """Eres un experto validador de facturas.

    Tu trabajo es analizar facturas y decidir si:
    - APROBAR: La factura es válida y puede procesarse
    - RECHAZAR: La factura tiene problemas graves
    - REVISAR: Necesita revisión humana

    Usa las herramientas disponibles para investigar.
    Explica tu razonamiento.
    """),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# 4. Crear el agente
agent = create_openai_functions_agent(llm, tools, prompt)

# 5. Crear el ejecutor (wrapper que ejecuta el agente)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 6. Usar el agente
resultado = agent_executor.invoke({
    "input": "Valida esta factura: NIF B12345678, Importe 4500€"
})

print(resultado["output"])
```

---

## CÓMO FUNCIONA UN AGENTE INTERNAMENTE

Vamos a ver paso a paso qué pasa cuando ejecutas un agente.

### Ejemplo: Validar una factura

```python
# Tu código
resultado = agent_executor.invoke({
    "input": "Valida esta factura: NIF B12345678, Importe 4500€"
})
```

### Lo que pasa internamente (paso a paso):

**PASO 1: El agente recibe la pregunta**
```
Input: "Valida esta factura: NIF B12345678, Importe 4500€"
```

**PASO 2: El LLM analiza y decide qué herramienta usar**
```
GPT-4 piensa:
"Necesito validar la factura. Primero debo:
1. Validar que el NIF es correcto
2. Buscar si el proveedor existe en la base de datos
3. Calcular el score de riesgo
4. Decidir si aprobar, rechazar o revisar"

GPT-4 decide: "Voy a usar la herramienta 'validar_nif' primero"
```

**PASO 3: El agente ejecuta la herramienta**
```python
# LangChain llama a la función
resultado_tool = validar_nif("B12345678")
# Resultado: True
```

**PASO 4: El LLM recibe el resultado y decide siguiente paso**
```
GPT-4 recibe: "validar_nif devolvió True"

GPT-4 piensa:
"El NIF es válido. Ahora necesito buscar si el proveedor existe."

GPT-4 decide: "Voy a usar la herramienta 'buscar_proveedor'"
```

**PASO 5: El agente ejecuta la segunda herramienta**
```python
# LangChain llama a la función
resultado_tool = buscar_proveedor_en_db("B12345678")
# Resultado: {"id": 123, "nombre": "ACME SL", "activo": True, "facturas_previas": 15}
```

**PASO 6: El LLM recibe el resultado y decide siguiente paso**
```
GPT-4 recibe: "Proveedor encontrado: ACME SL, activo, 15 facturas previas"

GPT-4 piensa:
"El proveedor existe y está activo. Tiene historial (15 facturas).
El importe es 4500€, que no es sospechoso.
Ahora voy a calcular el score de riesgo para estar seguro."

GPT-4 decide: "Voy a usar la herramienta 'calcular_riesgo'"
```

**PASO 7: El agente ejecuta la tercera herramienta**
```python
# LangChain llama a la función
resultado_tool = calcular_score_riesgo({
    "nif": "B12345678",
    "importe": 4500,
    "fecha": "2024-10-17"
})
# Resultado: {"score": 15, "nivel": "bajo"}
```

**PASO 8: El LLM toma la decisión final**
```
GPT-4 recibe: "Score de riesgo: 15 (bajo)"

GPT-4 piensa:
"Todos los checks pasaron:
✅ NIF válido
✅ Proveedor autorizado y activo
✅ Historial de 15 facturas previas
✅ Score de riesgo bajo (15/100)
✅ Importe normal (4500€)

DECISIÓN: APROBAR"

GPT-4 genera: "APROBAR - La factura es válida. El proveedor ACME SL (NIF B12345678)
está autorizado, tiene historial de 15 facturas previas, y el score de riesgo es
bajo (15/100). El importe de 4500€ está dentro de lo normal."
```

**PASO 9: Devuelves el resultado**
```python
resultado["output"]
# → "APROBAR - La factura es válida. El proveedor ACME SL..."
```

---

## LOGS REALES DE UN AGENTE (con verbose=True)

Cuando ejecutas un agente con `verbose=True`, ves TODO lo que hace:

```
> Entering new AgentExecutor chain...

Invoking: `validar_nif` with `{'nif': 'B12345678'}`

True

Invoking: `buscar_proveedor` with `{'nif': 'B12345678'}`

{"id": 123, "nombre": "ACME SL", "activo": true, "facturas_previas": 15}

Invoking: `calcular_riesgo` with `{'nif': 'B12345678', 'importe': 4500, 'fecha': '2024-10-17'}`

{"score": 15, "nivel": "bajo"}

> Finished chain.

APROBAR - La factura es válida. El proveedor ACME SL (NIF B12345678) está autorizado,
tiene historial de 15 facturas previas, y el score de riesgo es bajo (15/100).
```

**¿Ves la diferencia?**
- El agente NO tiene un código fijo que dice "primero validar, luego buscar, luego calcular"
- El LLM DECIDE en cada momento qué herramienta usar
- Podría decidir usar herramientas diferentes según la situación

---

## EJEMPLO COMPLETO: Agente Validador de Facturas

Vamos a construir un agente completo paso a paso.

### Paso 1: Instalar dependencias

```bash
pip install langchain langchain-openai psycopg2-binary
```

### Paso 2: Crear las herramientas (tools)

```python
# tools/factura_tools.py
import psycopg2
import re
from datetime import datetime, timedelta

def get_db():
    return psycopg2.connect("dbname=facturas user=postgres")

def validar_nif_tool(nif: str) -> bool:
    """
    Valida si un NIF español es válido.
    Input: NIF (string) ej: "B12345678"
    Output: True si es válido, False si no.
    """
    return bool(re.match(r'^[A-Z]\d{8}$', nif))

def buscar_proveedor_tool(nif: str) -> dict:
    """
    Busca un proveedor en la base de datos por NIF.
    Input: NIF (string)
    Output: Dict con datos del proveedor o None si no existe.
    """
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, nombre, activo,
               (SELECT COUNT(*) FROM facturas WHERE facturas.nif = proveedores.nif) as total_facturas
        FROM proveedores
        WHERE nif = %s
    """, (nif,))

    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "nombre": row[1],
        "activo": row[2],
        "facturas_previas": row[3]
    }

def calcular_riesgo_tool(nif: str, importe: float, fecha: str) -> dict:
    """
    Calcula el score de riesgo de una factura.
    Input: NIF (string), importe (float), fecha (string YYYY-MM-DD)
    Output: Dict con score (0-100) y nivel (bajo/medio/alto)
    """
    conn = get_db()
    cur = conn.cursor()

    score = 0
    razones = []

    # 1. Proveedor nuevo? +30 puntos de riesgo
    cur.execute("SELECT COUNT(*) FROM facturas WHERE nif = %s", (nif,))
    facturas_previas = cur.fetchone()[0]

    if facturas_previas == 0:
        score += 30
        razones.append("Proveedor sin historial")

    # 2. Importe alto? +20 puntos si > 5000€
    if importe > 5000:
        score += 20
        razones.append(f"Importe alto: {importe}€")

    # 3. Importe muy diferente al promedio? +15 puntos
    cur.execute("""
        SELECT AVG(importe) FROM facturas
        WHERE nif = %s AND created_at > NOW() - INTERVAL '6 months'
    """, (nif,))

    promedio = cur.fetchone()[0]
    if promedio and abs(importe - promedio) > promedio * 0.5:
        score += 15
        razones.append(f"Importe muy diferente al promedio ({promedio:.2f}€)")

    # 4. Fecha futura? +25 puntos
    if datetime.strptime(fecha, "%Y-%m-%d") > datetime.now():
        score += 25
        razones.append("Fecha en el futuro")

    conn.close()

    # Determinar nivel
    if score < 30:
        nivel = "bajo"
    elif score < 60:
        nivel = "medio"
    else:
        nivel = "alto"

    return {
        "score": score,
        "nivel": nivel,
        "razones": razones
    }

def buscar_facturas_duplicadas_tool(nif: str, importe: float, fecha: str) -> list:
    """
    Busca facturas duplicadas (mismo NIF, importe similar, fecha cercana).
    Input: NIF, importe, fecha
    Output: Lista de facturas similares
    """
    conn = get_db()
    cur = conn.cursor()

    # Buscar facturas con mismo NIF, importe +/-5%, fecha +/-7 días
    cur.execute("""
        SELECT id, importe, fecha, estado
        FROM facturas
        WHERE nif = %s
          AND importe BETWEEN %s AND %s
          AND fecha BETWEEN %s AND %s
    """, (
        nif,
        importe * 0.95,
        importe * 1.05,
        (datetime.strptime(fecha, "%Y-%m-%d") - timedelta(days=7)).strftime("%Y-%m-%d"),
        (datetime.strptime(fecha, "%Y-%m-%d") + timedelta(days=7)).strftime("%Y-%m-%d")
    ))

    duplicadas = []
    for row in cur.fetchall():
        duplicadas.append({
            "id": row[0],
            "importe": float(row[1]),
            "fecha": str(row[2]),
            "estado": row[3]
        })

    conn.close()
    return duplicadas
```

### Paso 3: Crear el agente

```python
# agents/validador_facturas.py
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate
from tools.factura_tools import (
    validar_nif_tool,
    buscar_proveedor_tool,
    calcular_riesgo_tool,
    buscar_facturas_duplicadas_tool
)

# Definir las herramientas con descripciones claras
tools = [
    Tool(
        name="validar_nif",
        func=validar_nif_tool,
        description="Valida si un NIF español es válido. Input: NIF (string). Output: True/False."
    ),
    Tool(
        name="buscar_proveedor",
        func=buscar_proveedor_tool,
        description="Busca un proveedor en la base de datos por NIF. Input: NIF (string). Output: dict con datos del proveedor o None."
    ),
    Tool(
        name="calcular_riesgo",
        func=calcular_riesgo_tool,
        description="Calcula el score de riesgo de una factura. Input: nif (string), importe (float), fecha (string YYYY-MM-DD). Output: dict con score y nivel."
    ),
    Tool(
        name="buscar_duplicadas",
        func=buscar_facturas_duplicadas_tool,
        description="Busca facturas duplicadas. Input: nif, importe, fecha. Output: lista de facturas similares."
    )
]

# Crear el LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Crear el prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", """Eres un experto validador de facturas de una empresa española.

Tu trabajo es analizar facturas y decidir una de estas tres acciones:
1. APROBAR - La factura es válida y puede procesarse automáticamente
2. RECHAZAR - La factura tiene problemas graves y debe rechazarse
3. REVISAR - La factura necesita revisión humana

REGLAS:
- Si el NIF es inválido → RECHAZAR
- Si el proveedor no existe o está inactivo → RECHAZAR
- Si hay facturas duplicadas → RECHAZAR
- Si el score de riesgo es alto (>60) → REVISAR
- Si el score de riesgo es medio (30-60) y el importe > 3000€ → REVISAR
- Si todo está OK y riesgo bajo → APROBAR

Usa las herramientas disponibles para investigar.
Siempre explica tu razonamiento con los datos obtenidos.
"""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# Crear el agente
agent = create_openai_functions_agent(llm, tools, prompt)

# Crear el ejecutor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,  # Ver los pasos del agente
    max_iterations=10  # Máximo 10 llamadas a herramientas
)

def validar_factura(nif: str, importe: float, fecha: str) -> dict:
    """
    Valida una factura usando el agente
    """
    resultado = agent_executor.invoke({
        "input": f"Valida esta factura: NIF {nif}, Importe {importe}€, Fecha {fecha}"
    })

    return {
        "decision": resultado["output"],
        "raw_output": resultado
    }
```

### Paso 4: Usar el agente

```python
# main.py
from agents.validador_facturas import validar_factura

# Caso 1: Factura normal de proveedor conocido
resultado = validar_factura(
    nif="B12345678",
    importe=1500.00,
    fecha="2024-10-17"
)

print(resultado["decision"])
# Output:
# APROBAR - La factura es válida. El proveedor ACME SL está autorizado,
# tiene historial de 15 facturas previas, y el score de riesgo es bajo (10/100).

# Caso 2: Factura de proveedor nuevo con importe alto
resultado = validar_factura(
    nif="B99999999",
    importe=8500.00,
    fecha="2024-10-17"
)

print(resultado["decision"])
# Output:
# REVISAR - El proveedor no tiene historial previo y el importe es alto (8500€).
# Score de riesgo: 50/100 (medio). Requiere revisión humana antes de aprobar.

# Caso 3: NIF inválido
resultado = validar_factura(
    nif="INVALID123",
    importe=1500.00,
    fecha="2024-10-17"
)

print(resultado["decision"])
# Output:
# RECHAZAR - El NIF INVALID123 no es válido. No puede procesarse.
```

---

## INTEGRAR EL AGENTE CON CELERY

Ahora puedes usar el agente dentro de tus workers de Celery:

```python
# tasks/procesar_factura.py
from celery import Celery
from agents.validador_facturas import validar_factura
import psycopg2

celery_app = Celery('facturas', broker='redis://localhost:6379/0')

@celery_app.task
def procesar_factura_con_agente(email_id):
    """
    Worker que usa el agente para decidir si aprobar la factura
    """

    # 1. Descargar y extraer datos (como antes)
    pdf = descargar_pdf(email_id)
    datos = extraer_datos_pdf(pdf)

    # 2. Usar el AGENTE para decidir
    decision_agente = validar_factura(
        nif=datos['nif'],
        importe=datos['importe'],
        fecha=datos['fecha']
    )

    # 3. Actuar según la decisión del agente
    if "APROBAR" in decision_agente['decision']:
        # Guardar y procesar automáticamente
        guardar_factura(datos, estado='APROBADA')
        enviar_a_fundacion(datos)

    elif "RECHAZAR" in decision_agente['decision']:
        # Rechazar y notificar
        guardar_factura(datos, estado='RECHAZADA')
        enviar_email_rechazo(datos, razon=decision_agente['decision'])

    elif "REVISAR" in decision_agente['decision']:
        # Marcar para revisión humana
        guardar_factura(datos, estado='PENDIENTE_REVISION')
        notificar_revisor_humano(datos, razon=decision_agente['decision'])

    return {
        "status": "processed",
        "decision": decision_agente['decision']
    }
```

---

## VENTAJAS DE USAR AGENTES

### 1. Adaptabilidad
```python
# Caso especial: proveedor nuevo pero recomendado
# El agente puede investigar más a fondo automáticamente

# Caso especial: importe alto pero con descuento aplicado
# El agente puede razonar sobre el contexto
```

### 2. Transparencia
```python
# Sabes EXACTAMENTE por qué el agente tomó una decisión
print(resultado["decision"])
# "REVISAR - El proveedor no tiene historial (score +30),
# el importe es 2x el promedio (score +15),
# total: 45/100 (medio). Requiere revisión."
```

### 3. Flexibilidad
```python
# Puedes añadir nuevas herramientas sin cambiar el agente
tools.append(Tool(
    name="verificar_sanciones",
    func=buscar_en_lista_sanciones,
    description="Verifica si el proveedor está en lista de sanciones"
))

# El agente automáticamente sabrá usarla si es relevante
```

---

## DESVENTAJAS DE USAR AGENTES

### 1. Coste
- Cada ejecución cuesta ~$0.02-0.08 (GPT-4) o ~$0.003-0.01 (GPT-3.5)
- 1000 facturas/mes = $20-80/mes con GPT-4

### 2. Latencia
- Una automatización: ~1-2 segundos
- Un agente: ~5-15 segundos (depende de cuántas herramientas use)

### 3. No determinismo
- El agente podría tomar decisiones ligeramente diferentes en casos edge
- Para casos críticos, mejor combinar: agente decide + humano revisa

---

## CUÁNDO USAR AGENTES vs AUTOMATIZACIONES

### USA AUTOMATIZACIÓN (sin agente) cuando:
- ✅ El proceso es siempre igual
- ✅ Las reglas son claras y fijas
- ✅ No necesitas razonamiento complejo
- ✅ Quieres máxima velocidad y mínimo coste

**Ejemplo**: Procesar facturas de un formato siempre igual

### USA AGENTE cuando:
- ✅ Necesitas tomar decisiones contextuales
- ✅ Las reglas son complejas o cambian
- ✅ Necesitas razonamiento sobre múltiples factores
- ✅ Puedes tolerar ~5-10 segundos de latencia extra

**Ejemplo**: Decidir si aprobar, rechazar o revisar facturas

### USA HÍBRIDO (automatización + agente):
- ✅ Automatización para los pasos fijos (descargar, extraer, validar formato)
- ✅ Agente para la decisión final (aprobar/rechazar/revisar)

**Ejemplo**: Tu sistema de facturas ideal

---

## RESUMEN: ¿QUÉ NECESITO PARA AGENTES?

### Instalaciones:
```bash
pip install langchain langchain-openai openai
```

### API Key de OpenAI:
```bash
export OPENAI_API_KEY="sk-..."
```

### Código básico:
```python
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.tools import Tool

# 1. Crear herramientas
tools = [Tool(name="mi_tool", func=mi_funcion, description="...")]

# 2. Crear LLM
llm = ChatOpenAI(model="gpt-4")

# 3. Crear agente
agent = create_openai_functions_agent(llm, tools, prompt)

# 4. Ejecutar
agent_executor = AgentExecutor(agent=agent, tools=tools)
resultado = agent_executor.invoke({"input": "..."})
```

### Costes:
- Desarrollo: $0 (solo API credits)
- Producción: ~$20-80/mes por 1000 ejecuciones (GPT-4)

---

## SIGUIENTE PASO: TU SISTEMA MAISA

Ya sabes:
- ✅ Cómo hacer automatizaciones con código (Celery + Redis + PostgreSQL)
- ✅ Cómo hacer agentes con LangChain (GPT-4 + herramientas)

Ahora falta la **ÚLTIMA PIEZA**: Tu sistema "Maisa" que genera código on-the-fly.

**La diferencia clave**:
- Agente con LangChain: El LLM decide qué HERRAMIENTAS usar
- Tu Maisa: El LLM GENERA CÓDIGO PYTHON y lo ejecuta en un sandbox

¿Quieres que te explique cómo funciona la generación de código on-the-fly? 🔥
