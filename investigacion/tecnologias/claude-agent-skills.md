# Claude Code: Agent Skills y Subagents

**Investigado**: 2025-10-21
**Fuente**: Documentación oficial de Anthropic

---

## 🎯 Resumen Ejecutivo

Claude Code tiene dos mecanismos potentes para extender sus capacidades:

1. **Skills**: Capacidades modulares que Claude invoca automáticamente cuando las necesita
2. **Subagents**: Agentes especializados con su propio contexto y configuración

**Por qué es relevante para tu proyecto**: Puedes crear Skills y Subagents personalizados para trabajar específicamente con tu arquitectura de trabajadores digitales.

---

## PARTE 1: Agent Skills

### ¿Qué son los Skills?

**Definición**: Capacidades modulares que extienden lo que Claude puede hacer, organizadas en carpetas con instrucciones, scripts y recursos.

**Características clave**:
- **Model-invoked**: Claude decide autónomamente cuándo usarlos (basado en la descripción)
- **Modulares**: Cada skill hace UNA cosa específica
- **Portables**: Funcionan igual en Claude apps, Claude Code, y API
- **Componibles**: Los skills se apilan/combinan automáticamente

### Cómo funcionan

```
Usuario hace request
    ↓
Claude lee las descripciones de todos los skills disponibles
    ↓
Claude decide qué skills son relevantes
    ↓
Claude carga SOLO esos skills (progressive disclosure)
    ↓
Claude ejecuta usando las instrucciones del skill
```

**Progressive Disclosure** = Carga información solo cuando la necesita (como un manual con índice, capítulos, y apéndice)

### Estructura de un Skill

```
my-skill/
├── SKILL.md              # ⭐ Archivo principal (obligatorio)
├── reference.md          # Documentación de referencia
├── scripts/
│   └── helper.py         # Scripts ejecutables
└── templates/
    └── template.txt      # Plantillas reutilizables
```

### Formato del SKILL.md

```yaml
---
name: Your Skill Name
description: Brief description of what this Skill does and when to use it
allowed-tools: [Bash, Read, Write]  # Opcional: limita qué tools puede usar
---

# Instrucciones Detalladas

Paso a paso de cómo usar este skill.

## Ejemplo

[Ejemplos concretos de uso]

## Referencias

[Links a documentación externa si aplica]
```

**Clave**: La `description` es CRÍTICA. Claude la usa para decidir si activar el skill.

### Tipos de Skills

1. **Personal Skills**: `~/.claude/skills/`
   - Disponibles en TODOS tus proyectos
   - Ejemplo: "Usa mi estilo de commits"

2. **Project Skills**: `.claude/skills/`
   - Solo para ese proyecto específico
   - Ejemplo: "Conoce la arquitectura de Maisa"

3. **Plugin Skills**: Vienen con plugins instalados
   - Ejemplo: Skills de shadcn/ui, Supabase, etc.

### Mejores Prácticas

✅ **SÍ hacer**:
- Descripciones específicas y claras
- Un skill = una capacidad
- Incluir ejemplos concretos
- Versionar los skills con tu código

❌ **NO hacer**:
- Skills demasiado generales
- Descripciones vagas
- Duplicar funcionalidad entre skills

---

## PARTE 2: Subagents

### ¿Qué son los Subagents?

**Definición**: Agentes especializados con su propio contexto, prompt del sistema, y conjunto de herramientas.

**Diferencia con Skills**:
- **Skills**: Instrucciones que Claude sigue
- **Subagents**: Instancias separadas de Claude con personalidad/configuración específica

### Beneficios de los Subagents

1. **Contexto Preservado**: No contaminan la conversación principal
2. **Expertise Especializado**: Prompt del sistema optimizado para tarea específica
3. **Reutilizables**: Úsalos en múltiples proyectos
4. **Permisos Flexibles**: Control granular de qué tools pueden usar

### Subagents Pre-configurados

Claude Code incluye varios subagents listos para usar:

| Subagent | Propósito | Cuándo usarlo |
|----------|-----------|---------------|
| **code-reviewer** | Revisa calidad, seguridad, best practices | Después de escribir código significativo |
| **test-runner** | Ejecuta tests, arregla failures | Desarrollo con TDD |
| **debugger** | Root cause analysis de bugs | Cuando algo falla |
| **data-scientist** | SQL queries, análisis de datos | Trabajar con bases de datos |

### Cómo se usan

**Automático**:
```
Tú: "Revisa el código que acabas de escribir"
Claude: [Delega automáticamente al code-reviewer subagent]
```

**Explícito**:
```
Tú: /code-reviewer
Claude: [Lanza el code-reviewer subagent manualmente]
```

### Crear tus propios Subagents

**Ubicación**: `.claude/agents/` en tu proyecto

**Estructura**:
```markdown
---
name: my-subagent
description: When and why to use this subagent
model: claude-sonnet-4-5-20250929
tools: [Bash, Read, Write, Grep]
---

# System Prompt

You are a specialized agent that...

[Instrucciones detalladas de comportamiento]
```

---

## PARTE 3: Cómo te pueden servir para TU proyecto

### Para Investigación (Fase actual)

#### Skill: "Maisa Architecture Analyzer"

**Propósito**: Claude conoce en profundidad la arquitectura de Maisa

```yaml
---
name: Maisa Architecture Analyzer
description: Use this skill when the user asks about Maisa's architecture, HALP system, Chain-of-Work, or how Maisa implements anti-hallucination. Also use when comparing our project to Maisa.
---

# Maisa Knowledge Base

## Core Architecture
[Copiar info clave de investigacion/referentes/maisa.md]

## HALP System (Anti-hallucination)
[Detalles del sistema HALP]

## Chain-of-Work Implementation
[Cómo lo hace Maisa]

## Cuando el usuario pregunta
- Siempre referencia los docs en investigacion/referentes/
- Compara con su proyecto en proyecto/ARQUITECTURA.md
- Sugiere adaptaciones específicas
```

#### Subagent: "Tech Stack Researcher"

**Propósito**: Investiga y compara tecnologías

```markdown
---
name: tech-stack-researcher
description: Specialized in researching and comparing technologies (LangGraph, n8n, Docker, etc.) for Mario's digital workers platform
model: claude-sonnet-4-5-20250929
tools: [WebSearch, WebFetch, Read, Write]
---

You are a technical researcher specializing in AI/automation stack decisions.

When researching a technology:
1. Check investigacion/tecnologias/ for existing notes
2. Search for latest 2025 documentation
3. Create comparison tables
4. Highlight trade-offs for Mario's specific use case
5. Recommend next steps

Always consider:
- Mario is building a Maisa-like platform
- Stack needs: LLM integration, Docker sandboxing, PostgreSQL
- Trade-off: Development speed vs control
```

### Para Diseño de Arquitectura (Próxima fase)

#### Skill: "Chain-of-Work Schema Designer"

```yaml
---
name: Chain-of-Work Schema Designer
description: Use when designing PostgreSQL schemas for Chain-of-Work, execution traces, or worker storage. Knows Mario's architecture patterns.
allowed-tools: [Read, Write]
---

# Database Design Patterns

## Chain-of-Work Schema
Reference: proyecto/ARQUITECTURA.md

Tables structure:
- trabajadores
- ejecuciones
- chain_of_work

When designing schemas:
1. Always include timestamps
2. Use JSONB for flexible metadata
3. Index by input_hash for determinism
4. Foreign keys with ON DELETE CASCADE
5. Include status enums (PENDING, RUNNING, SUCCESS, FAILED)
```

#### Subagent: "Architecture Critic"

```markdown
---
name: architecture-critic
description: Reviews architectural decisions for Mario's digital workers platform, challenges assumptions, suggests alternatives
model: claude-sonnet-4-5-20250929
tools: [Read]
---

You are a senior software architect reviewing Mario's system design.

Your role:
- Challenge assumptions constructively
- Point out scalability issues
- Suggest simpler alternatives
- Reference proyecto/ARQUITECTURA.md as source of truth
- Consider trade-offs: cost, complexity, maintainability

Focus areas:
- Docker sandbox security
- LLM integration patterns
- Chain-of-Work storage efficiency
- Determinism implementation
```

### Para Implementación (Fase futura)

#### Skill: "Maisa API Pattern"

```yaml
---
name: Maisa API Pattern
description: Use when implementing FastAPI endpoints for workers, executions, or chain-of-work. Follows Mario's project conventions.
allowed-tools: [Read, Write, Edit]
---

# API Implementation Patterns

## Standard Endpoint Structure

```python
@router.post("/trabajadores")
async def create_worker(
    worker: WorkerCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new digital worker

    Stores in PostgreSQL, returns worker_id
    """
    # Implementation follows proyecto/ARQUITECTURA.md
```

## Error Handling
Always return appropriate HTTP codes:
- 200: Success
- 201: Created
- 400: Bad Request (validation)
- 404: Not Found
- 500: Internal Server Error

## Response Format
```json
{
  "data": {...},
  "chain_of_work_id": "optional-uuid",
  "timestamp": "ISO-8601"
}
```
```

#### Subagent: "Docker Sandbox Expert"

```markdown
---
name: docker-sandbox-expert
description: Specialized in Docker sandbox configuration for executing LLM-generated code safely
model: claude-sonnet-4-5-20250929
tools: [Bash, Read, Write]
---

You are a Docker security expert specializing in sandbox environments.

Your expertise:
- Docker resource limits (--memory, --cpus, --pids-limit)
- Network isolation (--network=none or custom)
- Filesystem restrictions (read-only, tmpfs)
- User permissions (run as non-root)
- Capturing stdout/stderr from containers

When implementing sandboxes for Mario:
1. Security first - assume LLM-generated code is hostile
2. Resource limits must be enforced at OS level
3. Clean up containers after execution
4. Log everything for Chain-of-Work
5. Handle timeouts gracefully

Reference Mario's architecture in proyecto/ARQUITECTURA.md
```

---

## PARTE 4: Implementación Práctica

### Paso 1: Crear tu primer Skill (AHORA)

**Objetivo**: Skill que conoce tu arquitectura

```bash
# Crear estructura
mkdir -p .claude/skills/maisa-project-knowledge
cd .claude/skills/maisa-project-knowledge
```

**Archivo `SKILL.md`**:

```yaml
---
name: Maisa Project Knowledge
description: Use this skill when the user asks about the architecture of their digital workers platform, asks for design decisions, or needs to understand how components integrate. Also use when implementing features that need to follow established patterns.
---

# Project Architecture

## Core Concept
User describes task → LLM generates Python code step-by-step → Execute in Docker sandbox → Store in Chain-of-Work → Learn via determinism

## Key Components

### 1. Code Generator
- LLM: GPT-4 or Claude
- Generates code incrementally (not all at once)
- Validates syntax before execution
- Reference: proyecto/ARQUITECTURA.md

### 2. Docker Sandbox
- Isolated execution environment
- Resource limits: 256MB RAM, 30s timeout
- Network restrictions
- Read-only filesystem except /sandbox

### 3. Chain-of-Work
- PostgreSQL storage
- Every step recorded: code, result, error, timestamp
- Enables debugging and determinism

### 4. Determinism
- Hash input → Check cache → Reuse successful code
- Reduces LLM calls and errors

## When helping with this project

1. Always check proyecto/ARQUITECTURA.md first
2. Suggest implementations that fit this architecture
3. Explain how new features integrate with existing components
4. Reference investigacion/ docs when comparing to competitors
5. Ask clarifying questions about which component is being worked on

## Key Files
- proyecto/ARQUITECTURA.md - Main architecture doc
- investigacion/referentes/maisa.md - Competitive analysis
- aprendizaje/guia-comunicacion-claude.md - How to communicate effectively
```

### Paso 2: Crear tu primer Subagent (Próximamente)

Cuando empieces a escribir código, crea:

```bash
mkdir -p .claude/agents
```

**Archivo `.claude/agents/code-gen-reviewer.md`**:

```markdown
---
name: code-gen-reviewer
description: Reviews LLM-generated code for safety, efficiency, and correctness before sandbox execution
model: claude-sonnet-4-5-20250929
tools: [Read]
---

You are a code reviewer specialized in validating LLM-generated Python code.

Your checklist:
1. **Security**: No os.system, eval, exec, subprocess without approval
2. **Syntax**: Valid Python (use compile() to check)
3. **Imports**: Only allowed libraries (requests, beautifulsoup4, pandas)
4. **Resource usage**: No infinite loops, no massive memory allocations
5. **Error handling**: Proper try/except blocks

When reviewing code:
- Explain WHAT is unsafe and WHY
- Suggest safer alternatives
- Reference proyecto/ARQUITECTURA.md for allowed patterns
- Approve or reject with clear reasoning

Format response:
```
✅ APPROVED / ❌ REJECTED

Issues found:
1. [Issue description]
2. [Issue description]

Suggested fixes:
[Fixed code]
```
```

---

## PARTE 5: Casos de Uso Específicos para Ti

### Caso 1: Investigación de Competidores

**Skill que crearías**: `competitor-analyzer.md`

**Qué haría**:
- Conoce Maisa, Make, n8n en profundidad
- Compara features automáticamente
- Identifica gaps en el mercado
- Sugiere diferenciación

### Caso 2: Diseño de Schemas

**Subagent que crearías**: `db-schema-designer`

**Qué haría**:
- Diseña tablas PostgreSQL
- Optimiza índices
- Considera escalabilidad
- Genera migrations

### Caso 3: Validación de Código LLM

**Skill que crearías**: `llm-code-validator.md`

**Qué haría**:
- Valida sintaxis Python
- Detecta código peligroso
- Verifica imports permitidos
- Sugiere mejoras

### Caso 4: Generación de Prompts

**Subagent que crearías**: `prompt-engineer`

**Qué haría**:
- Diseña prompts para GPT-4
- Optimiza para generación de código
- Incluye ejemplos efectivos
- Maneja context management

---

## PARTE 6: Ventajas Específicas para tu Proyecto

### 1. **Consistencia Arquitectónica**

Con Skills:
```
Tú: "Implementa el endpoint POST /trabajadores"

Claude: [Usa "Maisa API Pattern" skill]
         [Genera código siguiendo proyecto/ARQUITECTURA.md]
         [Incluye Chain-of-Work logging automáticamente]
         [Usa los mismos patrones de error handling]
```

Sin Skills:
```
Tú: "Implementa el endpoint POST /trabajadores"

Claude: [Genera código genérico]
         [Tienes que explicar patrones cada vez]
         [Posibles inconsistencias]
```

### 2. **Conocimiento del Dominio**

Con Subagent especializado:
```
Tú: "¿Cómo implementar determinismo?"

Claude: [Delega a "maisa-architecture-expert"]
         [Responde basado en investigacion/referentes/maisa.md]
         [Compara con proyecto/ARQUITECTURA.md]
         [Sugiere implementación específica para tu stack]
```

### 3. **Validación Automática**

Con Subagent de seguridad:
```
GPT-4 genera: import os; os.system('rm -rf /')

Claude: [code-gen-reviewer subagent activa]
         [❌ REJECTED - Dangerous system call]
         [Sugiere alternativa segura]
```

### 4. **Iteración Rápida**

Con Skills de proyecto:
- No repites contexto en cada conversación
- Claude "conoce" tu arquitectura permanentemente
- Cambios en SKILL.md se propagan a todas las conversaciones

---

## PARTE 7: Próximos Pasos Recomendados

### Fase 1: Investigación (AHORA)

1. **Crea el skill**: `maisa-project-knowledge.md`
   - Contiene tu arquitectura actual
   - Referencias a docs de investigacion/
   - Patrones de comunicación

2. **Pruébalo**:
   - Pregúntame sobre arquitectura
   - Pídeme comparar con Maisa
   - Valida que respondo con el contexto correcto

### Fase 2: Diseño (Próxima semana)

3. **Crea subagent**: `architecture-critic`
   - Revisa tus decisiones de diseño
   - Desafía suposiciones
   - Sugiere alternativas

4. **Crea skill**: `db-schema-designer.md`
   - Patrones de schemas PostgreSQL
   - Best practices para Chain-of-Work
   - Indexing strategies

### Fase 3: Implementación (Semanas 3-6)

5. **Crea subagent**: `code-gen-validator`
   - Valida código LLM antes de ejecutar
   - Detecta vulnerabilidades
   - Sugiere mejoras

6. **Crea skill**: `docker-sandbox-patterns.md`
   - Configuraciones Docker seguras
   - Resource limiting
   - Output capturing

---

## PARTE 8: Librerías Oficiales y Comunitarias de Skills

### 📦 Repositorio Oficial: anthropics/skills

**URL**: https://github.com/anthropics/skills

**Instalación en Claude Code**:
```
/plugin marketplace add anthropics/skills
```

#### Skills Incluidos (Oficiales)

**Creative & Design**:
- `algorithmic-art` - Crear arte generativo con p5.js usando randomness seeded, flow fields, particle systems
- `canvas-design` - Diseñar arte visual en formatos .png y .pdf usando filosofías de diseño
- `slack-gif-creator` - Crear GIFs animados optimizados para límites de tamaño de Slack
- `theme-factory` - Aplicar 10 temas profesionales pre-configurados a artifacts

**Development & Technical**:
- `artifacts-builder` - Construir artifacts HTML complejos usando React, Tailwind CSS, y shadcn/ui
- `mcp-builder` - Guía para crear servidores MCP de alta calidad para integrar APIs externas
- `webapp-testing` - Testear aplicaciones web locales usando Playwright para UI verification

**Enterprise & Communication**:
- `brand-guidelines` - Aplicar colores y tipografía oficial de Anthropic
- `internal-comms` - Escribir comunicaciones internas (status reports, newsletters, FAQs)

**Meta Skills**:
- `skill-creator` - Guía para crear skills efectivos
- `template-skill` - Template básico para nuevos skills

**Document Skills** (en `document-skills/`):
- `docx` - Crear/editar Word documents con tracked changes, comments, formateo
- `pdf` - Toolkit completo de manipulación de PDFs (extraer texto/tablas, crear, merge/split, forms)
- `pptx` - Crear/editar PowerPoint con layouts, templates, charts, generación automática
- `xlsx` - Crear/editar Excel con fórmulas, formateo, análisis de datos, visualización

**Nota**: Los document skills son snapshots point-in-time y no se mantienen activamente (son ejemplos de referencia).

---

### 🌟 Repositorio Comunitario: obra/superpowers

**URL**: https://github.com/obra/superpowers

**Instalación**:
```
/plugin marketplace add obra/superpowers-marketplace
```

**Qué es**: Core skills library enfocada en workflows de ingeniería sistemática.

**Diferenciador principal**: Enforce enfoques sistemáticos sobre problem-solving ad-hoc.

#### Principios Filosóficos

- **Test-Driven Development**: Write tests first, always
- **Complexity reduction**: Simplifica antes de optimizar
- **Evidence over claims**: Datos sobre suposiciones
- **Domain over implementation**: Entiende el problema antes de codificar

#### Skills Incluidos

**Testing**:
- Test-driven development workflows
- Async testing patterns
- Coverage analysis

**Debugging**:
- Systematic root cause analysis
- Evidence-based debugging
- Reproduction steps generation

**Collaboration**:
- `/superpowers:brainstorm` - Brainstorming estructurado
- `/superpowers:write-plan` - Planificación de tareas
- `/superpowers:execute-plan` - Ejecución de planes
- Code review workflows

**Development**:
- Git workflows avanzados
- Branch management
- Commit message standards

**Meta Skills**:
- Skill creation guide
- Sharing workflows

**Características únicas**:
- Activación automática por contexto
- Slash commands específicos
- 20+ skills integrados

---

### 🎨 Repositorios Comunitarios Destacados

#### 1. travisvn/awesome-claude-skills

**URL**: https://github.com/travisvn/awesome-claude-skills

**Qué es**: Lista curada de awesome Claude Skills, recursos y tools.

**Skills destacados listados**:
- `ios-simulator-skill` - Build y testing de apps iOS
- `ffuf-web-fuzzing` - Guía de penetration testing
- `playwright-skill` - Browser automation avanzada
- `claude-d3js-skill` - Visualizaciones de datos con D3.js
- `claude-scientific-skills` - Librerías de scientific computing (NumPy, SciPy, pandas)

**Herramientas**:
- **Skill Seekers**: Convierte sitios web de documentación en Claude Skills automáticamente

**Útil para**: Descubrir skills comunitarios organizados por categoría.

---

#### 2. abubakarsiddik31/claude-skills-collection

**URL**: https://github.com/abubakarsiddik31/claude-skills-collection

**Qué es**: Colección curada de skills oficiales y comunitarios.

**Categorías**:
- Productivity
- Creativity
- Coding
- Data analysis
- Communication

---

#### 3. simonw/claude-skills

**URL**: https://github.com/simonw/claude-skills

**Qué es**: Contenidos de `/mnt/skills` en el code interpreter environment de Claude.

**Útil para**: Ver qué skills vienen pre-incluidos con Claude.

---

### 📊 Comparativa: Oficial vs Comunitario

| Aspecto | anthropics/skills | obra/superpowers | Comunidad |
|---------|-------------------|------------------|-----------|
| **Mantenimiento** | Oficial Anthropic | Jesse Vincent | Variado |
| **Enfoque** | Ejemplos diversos | Engineering workflows | Específico por skill |
| **Calidad** | Alta (verificado) | Alta (opinionado) | Variable |
| **Documentación** | Excelente | Muy buena | Depende |
| **Casos de uso** | General purpose | Software development | Nicho específico |
| **Actualización** | Activa | Activa | Variable |

---

### 🛠️ Cómo Instalar Skills

#### En Claude Code

**Desde marketplace**:
```bash
/plugin marketplace add anthropics/skills
/plugin marketplace add obra/superpowers-marketplace
```

**Desde GitHub custom**:
```bash
/plugin add https://github.com/usuario/mi-skill-repo
```

#### En Claude.ai

- Disponible para planes: Pro, Max, Team, Enterprise
- Instalar desde plugins en configuración

#### Vía Claude API

```python
# Upload custom skill
import anthropic

client = anthropic.Anthropic(api_key="...")

# Skills se especifican en la configuración del agente
```

---

### 💡 Skills Relevantes para TU Proyecto

De los repositorios existentes, estos te servirían ahora:

#### Instalar AHORA:

1. **anthropics/skills → `mcp-builder`**
   - **Por qué**: Si decides usar MCP servers para integrar servicios
   - **Uso**: Crear MCP servers para Gmail, PDF processing, etc.

2. **anthropics/skills → `webapp-testing`**
   - **Por qué**: Cuando tengas tu API FastAPI funcionando
   - **Uso**: Tests automatizados de endpoints

3. **obra/superpowers → Test-driven development**
   - **Por qué**: TDD es crítico para tu proyecto (código LLM debe ser testeable)
   - **Uso**: Escribir tests antes de implementar features

#### Instalar en FASE DE DISEÑO:

4. **anthropics/skills → `artifacts-builder`**
   - **Por qué**: Si construyes un frontend con React
   - **Uso**: Diseñar UI para gestionar trabajadores digitales

5. **obra/superpowers → Brainstorm/Planning**
   - **Por qué**: Planificar arquitectura sistemáticamente
   - **Uso**: `/superpowers:brainstorm` para decisiones de diseño

#### Considerar para FUTURO:

6. **Community → `playwright-skill`**
   - **Por qué**: Testing avanzado de UI
   - **Uso**: E2E tests de la plataforma completa

7. **Community → `claude-scientific-skills`**
   - **Por qué**: Si trabajadores digitales procesan datos científicos
   - **Uso**: Análisis de datos con pandas/NumPy

---

### 🎯 Acción Inmediata Recomendada

**Instala ahora**:
```bash
/plugin marketplace add anthropics/skills
```

**Explora los skills oficiales**:
1. Navega a `~/.claude/plugins/anthropics-skills/skills/`
2. Lee `template-skill/SKILL.md` para entender estructura
3. Lee `skill-creator/SKILL.md` para aprender a crear tus propios skills

**Crea tu primer custom skill** basándote en los templates oficiales.

---

## PARTE 9: Recursos y Referencias

### Documentación Oficial
- [Skills Documentation](https://docs.claude.com/en/docs/claude-code/skills)
- [Subagents Documentation](https://docs.claude.com/en/docs/claude-code/sub-agents)
- [Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk)
- [What are Skills?](https://support.claude.com/en/articles/12512176-what-are-skills)
- [Creating Custom Skills](https://support.claude.com/en/articles/12512198-creating-custom-skills)

### Repositorios Oficiales
- [anthropics/skills](https://github.com/anthropics/skills) - Repositorio oficial de skills
- [anthropics/claude-cookbooks](https://github.com/anthropics/claude-cookbooks) - Notebooks y recetas

### Artículos Clave
- [Simon Willison: Claude Skills are awesome](https://simonwillison.net/2025/Oct/16/claude-skills/)
- [Anthropic: Equipping agents for the real world](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Anthropic Skills Blog Post](https://www.anthropic.com/news/skills)

### Repositorios Comunitarios
- [obra/superpowers](https://github.com/obra/superpowers) - Core skills library
- [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) - Lista curada
- [abubakarsiddik31/claude-skills-collection](https://github.com/abubakarsiddik31/claude-skills-collection) - Colección comunitaria
- [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) - Commands y workflows

---

## PARTE 10: Template para tus Skills

```yaml
---
name: [Nombre descriptivo]
description: Use this skill when [situación específica]. Also use when [otra situación]. Context: [dominio del skill].
allowed-tools: [Bash, Read, Write, Grep, Edit]  # Opcional
---

# [Título del Skill]

## Propósito
[Qué resuelve este skill]

## Cuándo usar
- [Caso de uso 1]
- [Caso de uso 2]

## Cómo usar

### Paso 1: [Nombre del paso]
[Instrucciones detalladas]

```[lenguaje]
[Ejemplo de código]
```

### Paso 2: [Nombre del paso]
[Instrucciones detalladas]

## Referencias
- [Link a proyecto/ARQUITECTURA.md relevante]
- [Link a investigacion/ relevante]

## Ejemplos

### Ejemplo 1: [Nombre]
```
Usuario: [Request]
Skill responde: [Output esperado]
```

## Notas
- [Consideración especial 1]
- [Consideración especial 2]
```

---

## Conclusión

**Skills y Subagents son PERFECTOS para tu proyecto** porque:

1. ✅ **Mantienen contexto arquitectónico** sin repetirlo cada vez
2. ✅ **Validan código LLM** antes de ejecutar (crítico para tu caso)
3. ✅ **Especializan tareas** (investigación, diseño, implementación)
4. ✅ **Escalan con tu proyecto** (agregar skills conforme creces)
5. ✅ **Portable** (funcionan igual en Claude Code, API, apps)

**Siguiente acción**: Crear el primer skill `maisa-project-knowledge.md` para que yo (Claude) conozca permanentemente tu arquitectura.

¿Quieres que lo creemos juntos ahora?
