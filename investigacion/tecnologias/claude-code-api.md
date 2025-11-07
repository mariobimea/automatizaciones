# Claude Code: Uso Remoto y Vía API

**Fecha**: 2025-10-21
**Investigador**: Mario Ferrer
**Pregunta**: ¿Se puede usar Claude Code de manera remota vía API?

---

## Resumen Ejecutivo

**Respuesta corta**: **Sí, pero NO directamente**. Claude Code no expone una API HTTP nativa, pero ofrece múltiples formas de uso programático:

1. ✅ **Headless Mode (CLI)**: Modo no-interactivo con JSON I/O
2. ✅ **MCP Servers**: Protocolo para conectar herramientas remotas
3. ✅ **Proxy Solutions**: Wrappers de terceros que exponen APIs
4. ❌ **API HTTP Nativa**: No existe oficialmente

**Implicación para tu plataforma**: Puedes usar Claude Code como motor de ejecución, pero necesitarás:
- Orquestarlo vía CLI (headless mode)
- O construir un wrapper API personalizado
- O usar la Claude API directamente + implementar las capacidades de agente tú mismo

---

## 1. Headless Mode (Modo Programático)

### ¿Qué es?

Claude Code tiene un **modo headless** (`-p` flag) que permite ejecutarlo sin interfaz interactiva, perfecto para automatización.

### Capacidades

```bash
# Modo simple (texto)
claude -p "Analiza este código y sugiere mejoras"

# Modo JSON (para parsing programático)
claude -p "Fix the tests" --output-format stream-json

# Multi-turn conversations
echo '{"role":"user","content":"Analyze this code"}' | claude -p --output-format stream-json --resume session-123
```

### JSON Output Format

```json
{
  "type": "result",
  "subtype": "success",
  "total_cost_usd": 0.003,
  "result": "The analysis shows...",
  "session_id": "abc123"
}
```

### Casos de Uso

- **SRE Incident Response**: Scripts que llaman a Claude Code para diagnosticar errores
- **Security Reviews**: Análisis automatizado de PRs
- **Legal Document Analysis**: Procesamiento multi-turn de documentos largos

### Limitaciones

- ❌ No es una API HTTP (es CLI)
- ❌ Necesitas tener Claude Code instalado localmente
- ❌ Requiere autenticación previa (login manual)
- ❌ No soporta concurrencia nativa (cada llamada = nuevo proceso)

---

## 2. MCP (Model Context Protocol)

### ¿Qué es?

Protocolo open-source para conectar Claude Code con herramientas y fuentes de datos externas.

### Arquitectura

```
Tu App → Claude Code → MCP Server (HTTP/SSE/stdio) → External Service
                                   ↓
                              [Supabase, GitHub, Sentry, Custom Tools]
```

### Uso Remoto

```bash
# Agregar un MCP server remoto vía HTTP
claude mcp add --transport http myserver https://api.ejemplo.com/mcp

# Usar en conversación
claude -p "Busca datos usando @myserver:users/123"
```

### Autenticación

- Soporta OAuth 2.0 para servicios cloud
- Tokens guardados y auto-renovados
- Enterprise: control centralizado de servidores permitidos

### ¿Esto resuelve tu necesidad?

**Parcialmente**. MCP te permite:
- ✅ Conectar Claude Code a **tus servicios** remotos
- ✅ Extender capacidades con herramientas custom
- ❌ Pero NO convierte Claude Code en un servicio HTTP al que puedas llamar

**Es al revés**: Claude Code llama a tus APIs, no tú a Claude Code.

---

## 3. Soluciones Proxy

### Claude Code Proxy (Terceros)

Proyecto open-source: [fuergaosi233/claude-code-proxy](https://github.com/fuergaosi233/claude-code-proxy)

**Qué hace**:
- Wrapper Python que expone OpenAI-compatible API
- Traduce requests de Claude API a otros LLMs (OpenAI, Azure, Ollama)
- Permite rutear Claude Code a modelos alternativos

**Uso**:
```bash
# 1. Levantar el proxy
python proxy.py  # Escucha en localhost:8082

# 2. Configurar Claude Code para usar el proxy
ANTHROPIC_BASE_URL=http://localhost:8082 claude -p "Task"
```

**Arquitectura**:
```
Claude Code CLI → Proxy Server (localhost:8082) → OpenAI API
                                                 → Azure OpenAI
                                                 → Ollama local
```

### Limitaciones

- ❌ Solo traduce **requests salientes** de Claude Code
- ❌ No convierte Claude Code en un servicio al que llamar
- ✅ Útil si quieres usar Claude Code pero con otros LLMs

---

## 4. Claude Code Analytics API

### Qué es

API oficial de Anthropic para **telemetría** de uso de Claude Code en organizaciones.

### Endpoint

```
GET /v1/organizations/usage_report/claude_code
Authorization: Bearer sk-ant-admin-...
```

### Response

```json
{
  "daily_metrics": [
    {
      "date": "2025-10-21",
      "total_sessions": 142,
      "total_cost_usd": 23.45,
      "active_users": 12
    }
  ]
}
```

### ¿Sirve para tu caso?

❌ **No**. Esta API solo reporta métricas de uso, no permite **ejecutar** Claude Code remotamente.

---

## 5. Comparación: Claude Code vs Claude API

| Característica | Claude Code | Claude API |
|---|---|---|
| **Interfaz** | CLI + VSCode Extension | HTTP REST API |
| **Acceso Remoto** | Solo vía headless CLI | ✅ Nativo HTTP |
| **Agentes/Tools** | Built-in (subagents, skills, MCP) | ❌ Debes implementar |
| **Sandbox Docker** | Built-in | ❌ Debes implementar |
| **File System Access** | ✅ Directo | ❌ Vía prompts/herramientas |
| **Multi-turn Context** | ✅ Automático | ✅ Vía API |
| **Costo** | Pro/Max subscription (~$20-40/mes) | Pay-per-token (~$3-15 per 1M tokens) |
| **Concurrencia** | ❌ Limitada (procesos CLI) | ✅ Ilimitada (API calls) |
| **Customización** | Plugins, Skills, Subagents | Total (implementas tú) |

---

## Arquitecturas Posibles para Tu Plataforma

### Opción A: Claude Code como Motor (Wrapper API)

**Arquitectura**:
```
Tu API REST
    ↓
Orquestador (Python/Node)
    ↓
Claude Code CLI (headless mode)
    ↓
Docker Sandbox (ejecuta código generado)
```

**Implementación**:
```python
import subprocess
import json

def ejecutar_trabajador(tarea: str) -> dict:
    cmd = [
        "claude", "-p", tarea,
        "--output-format", "stream-json",
        "--allowedTools", "Bash,Read,Write"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

# API endpoint
@app.post("/trabajadores/ejecutar")
def ejecutar(tarea: str):
    resultado = ejecutar_trabajador(tarea)
    return {"chain_of_work": resultado}
```

**Pros**:
- ✅ Usas todas las capacidades de Claude Code (subagents, skills, sandbox)
- ✅ No tienes que implementar orquestación de herramientas
- ✅ Chain-of-work automático (logs de cada step)

**Contras**:
- ❌ Requiere instalación de Claude Code en cada worker
- ❌ Autenticación compleja (cada worker necesita login)
- ❌ Escalabilidad limitada (procesos CLI, no threads)
- ❌ Dependes de cliente propietario de Anthropic

---

### Opción B: Claude API + LangGraph (Custom Implementation)

**Arquitectura**:
```
Tu API REST
    ↓
LangGraph Orchestrator
    ↓
Claude API (Anthropic)
    ↓
Custom Sandbox (Docker Python SDK)
```

**Implementación**:
```python
from anthropic import Anthropic
from langgraph import Graph

client = Anthropic(api_key="sk-ant-...")

def generar_codigo(tarea: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4",
        messages=[{"role": "user", "content": f"Generate Python code for: {tarea}"}]
    )
    return response.content[0].text

def ejecutar_en_sandbox(codigo: str) -> dict:
    # Tu implementación de Docker sandbox
    pass

# LangGraph workflow
graph = Graph()
graph.add_node("generar", generar_codigo)
graph.add_node("ejecutar", ejecutar_en_sandbox)
graph.add_edge("generar", "ejecutar")
```

**Pros**:
- ✅ Control total sobre arquitectura
- ✅ Escalabilidad ilimitada (HTTP API)
- ✅ Multi-tenancy fácil (API keys por usuario)
- ✅ Costos transparentes (pay-per-token)

**Contras**:
- ❌ Debes implementar orquestación de herramientas
- ❌ Debes implementar sandbox (seguridad crítica)
- ❌ Debes implementar Chain-of-Work tracking
- ❌ Más código custom = más mantenimiento

---

### Opción C: Híbrido (Claude API + MCP para Herramientas)

**Arquitectura**:
```
Tu API REST
    ↓
Claude API (Anthropic)
    ↓
MCP Server (custom) ← Tus herramientas custom
    ↓
[Sandbox, DB, External APIs]
```

**Concepto**:
- Usas Claude API para generación de código
- Implementas tus herramientas como MCP server
- Claude API las invoca vía function calling

**Pros**:
- ✅ API nativa de Anthropic (escalable)
- ✅ Estándar open-source (MCP) para herramientas
- ✅ Reusabilidad de herramientas

**Contras**:
- ❌ MCP aún no está disponible en Claude API (solo en Claude Code por ahora)
- ❌ Necesitarías esperar a que Anthropic lo soporte o hacerlo manualmente

---

## Recomendación para Tu Caso

### Situación Actual

Estás construyendo una plataforma donde:
1. Usuarios dan tareas en lenguaje natural
2. Agentes generan código Python step-by-step
3. Ejecutan código en sandbox Docker
4. Guardan Chain-of-Work en PostgreSQL
5. Aprenden de éxitos/fracasos (determinismo)

### Mi Recomendación: **Opción B (Claude API + Custom)**

**Por qué**:

1. **Control total**: Necesitas customizar cada paso (generación, ejecución, learning)
2. **Escalabilidad**: Una plataforma de "trabajadores digitales" necesita escalar (API > CLI)
3. **Multi-tenancy**: Cada usuario tendrá sus propios trabajadores (API keys separados)
4. **Transparencia de costos**: Pay-per-token te permite pasar costos a usuarios
5. **Independencia**: No dependes de un cliente CLI propietario

**Arquitectura Sugerida**:

```
[Frontend/API Gateway]
        ↓
[Orquestador de Trabajadores] (FastAPI/Node)
        ↓
    ┌───┴────┐
    ↓        ↓
[LLM Service]  [Sandbox Service]
    ↓              ↓
Claude API    Docker Engine
    ↓              ↓
[Chain-of-Work DB] (PostgreSQL)
```

**Componentes a implementar**:

1. **LLM Service**: Wrapper de Claude API
   - Genera código step-by-step
   - Maneja conversación multi-turn
   - Implementa anti-alucinación (validación)

2. **Sandbox Service**: Docker Python SDK
   - Crea containers on-demand
   - Resource limits (CPU, memory, timeout)
   - Network isolation
   - Captura stdout/stderr

3. **Chain-of-Work Tracker**: PostgreSQL + ORM
   - Guarda cada step
   - Input hash para determinismo
   - Métricas de éxito/error

4. **Determinism Engine**: Caché de código exitoso
   - Hash de input → lookup código
   - Si existe y fue exitoso → reusar
   - Si no → generar nuevo

**Ventajas sobre usar Claude Code**:

| Aspecto | Claude Code (Opción A) | Claude API (Opción B) |
|---|---|---|
| Escalabilidad | ❌ Limitada (CLI) | ✅ Ilimitada (HTTP) |
| Multi-tenancy | ❌ Complejo | ✅ Trivial (API keys) |
| Customización | ⚠️ Limitada a plugins | ✅ Total |
| Costo | ~$40/mes fijo | Variable (pay-per-use) |
| Deploy | ❌ Complejo (instalar CLI) | ✅ Simple (solo código) |
| Control | ⚠️ Caja negra | ✅ Full visibility |

---

## Alternativa: Esperar a Claude Code Web API

**Contexto**: En Octubre 2025, Anthropic lanzó **Claude Code Web** (versión browser).

**Posibilidad futura**: Si Anthropic expone una API para Claude Code Web, podría cambiar todo.

**Estrategia**: Monitorear roadmap de Anthropic para futuras APIs de Claude Code.

**Mientras tanto**: Implementar con Claude API te da:
1. Solución inmediata
2. Control total
3. Si en el futuro lanzan API de Claude Code, puedes migrar

---

## Próximos Pasos

### 1. Decisión Inmediata

¿Qué priorizar?

- **Time-to-market**: Opción A (usar Claude Code vía CLI)
- **Escalabilidad**: Opción B (implementar con Claude API)
- **Exploración**: Prototipar ambas en paralelo

### 2. Prototipo Rápido (Esta Semana)

**Objetivo**: Validar viabilidad técnica

**Tareas**:
- [ ] Crear script Python que llame Claude Code en headless mode
- [ ] Parsear JSON output
- [ ] Ejecutar código generado en Docker
- [ ] Guardar Chain-of-Work en JSON local

**Tiempo estimado**: 2-3 horas

### 3. Investigación Adicional

- [ ] Investigar LangGraph docs (viste que lo mencionaste)
- [ ] Revisar Maisa architecture (¿usan Claude Code o API?)
- [ ] Benchmarking: Claude Code vs Claude API (latencia, costo)

---

## Conclusión

**Tu pregunta**: ¿Puedo usar Claude Code remotamente vía API?

**Respuesta técnica**:
- Claude Code **no tiene API HTTP nativa**
- Pero tiene **headless mode** (CLI programático)
- Y soporta **MCP servers** (herramientas remotas)

**Respuesta práctica para tu plataforma**:
- **No uses Claude Code como backend**
- **Usa Claude API + implementación custom**
- Claude Code es excelente como **cliente interactivo**, pero no como **servicio backend**

**Razón**: Necesitas control, escalabilidad y multi-tenancy que solo una API HTTP te da.

---

## Referencias

- [Claude Code Headless Mode Docs](https://docs.claude.com/en/docs/claude-code/sdk/sdk-headless)
- [MCP Protocol Docs](https://docs.claude.com/en/docs/claude-code/mcp)
- [Claude Code Analytics API](https://docs.claude.com/en/api/claude-code-analytics-api)
- [Claude API Platform](https://www.claude.com/platform/api)
- [Claude Code Proxy (Third-party)](https://github.com/fuergaosi233/claude-code-proxy)

---

**Última actualización**: 2025-10-21
**Siguiente revisión**: Cuando Anthropic lance nuevas features de API
