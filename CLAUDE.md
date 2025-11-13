# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

---

## Quick Context

**Repository Type**: Research & Development for AI workflow engine
**User**: Mario Ferrer (Spanish-speaking, technical founder)
**Current Phase**: 🟢 **READY TO CODE** - Starting implementation
**Project Name**: **NOVA** (Neural Orchestration & Validation Agent)
**Primary Goal**: Build a workflow execution engine based on directed graphs with conditional logic

---

## What This Repo Is

Mario's workspace for building **NOVA** - a workflow execution engine:

### Phase 1 (MVP - Current)
1. Execute workflows as directed graphs with conditional logic
2. Workflows with ActionNodes (execute code) and DecisionNodes (conditional branching)
3. Execute code safely in Docker sandbox (Hetzner VM)
4. Complete traceability with Chain-of-Work
5. Hardcoded Python code in workflow definitions (StaticExecutor)

### Phase 2 (Future)
- AI-powered code generation (CachedExecutor, AIExecutor)
- Self-learning from successful execution paths
- Deterministic behavior over time

**Think**: Graph-based workflow engine preparing for self-programming capabilities.

---

## Repository Structure

```
/automatizaciones/
│
├── /investigacion/              # 📚 RESEARCH (completed, reference only)
│   ├── /referentes/            # Maisa, n8n, Make analysis
│   ├── /tecnologias/           # Tech evaluations
│   └── /conceptos/             # Theoretical fundamentals
│
├── /documentacion/              # 📖 NOVA DOCUMENTATION
│   ├── ARQUITECTURA.md         # ⭐ How NOVA works
│   ├── PLAN-FASES.md          # ⭐⭐ Implementation plan (5 phases)
│   ├── ALTERNATIVAS.md         # Technical decisions & reasoning
│   └── /futuro/
│       └── BACKLOG.md          # Future ideas (Phase 2+)
│
├── /nova/                       # 💻 THE PROJECT (code to deploy)
│   ├── /src/
│   │   ├── /api/               # FastAPI endpoints
│   │   ├── /core/              # Graph Engine, Executors, Nodes
│   │   ├── /models/            # SQLAlchemy models
│   │   └── /workers/           # Celery tasks
│   ├── /database/              # SQL schemas, Alembic migrations
│   ├── /fixtures/              # Example workflows
│   ├── /tests/                 # Tests
│   ├── README.md               # Quick start
│   ├── requirements.txt
│   ├── Dockerfile
│   └── Procfile                # Railway deployment
│
├── /aprendizaje/               # Learning resources
│
└── CLAUDE.md                   # 👈 This file
```

---

## Current Status

**Phase**: Ready to start coding
**Timeline**: 2 weeks for MVP

**Completed**:
- ✅ Research phase (Maisa, tech stacks, deployment options)
- ✅ Architecture designed (graph-based workflows)
- ✅ Tech stack decided (FastAPI + Celery + PostgreSQL + Hetzner)
- ✅ Implementation plan documented (5 phases)
- ✅ Documentation structured and clean

**Next Steps**:
1. Setup Hetzner VM for Docker sandbox
2. Create Railway project (PostgreSQL + Redis)
3. Implement Graph Engine core
4. Build StaticExecutor
5. Create Invoice Processing workflow (example)

---

## Key Architectural Concepts

Refer to [/documentacion/ARQUITECTURA.md](documentacion/ARQUITECTURA.md) for full details.

### Graph-Based Workflows
Workflows are directed graphs with nodes and edges:
- **ActionNode**: Executes Python code via an Executor
- **DecisionNode**: Conditional branching based on context
- **Start/End**: Control flow markers
- **Edges**: Connections between nodes

**Example**:
```
Start → Extract → Validate → [Decision: Valid?]
                              ├─ Yes → [Amount > 1000?]
                              │        ├─ Yes → Manual Approval
                              │        └─ No → Auto Approve
                              └─ No → Reject
```

### Executors (Execution Strategies)
- **StaticExecutor** (Phase 1): Executes hardcoded Python from workflow definitions
- **CachedExecutor** (Phase 2): Cache successful code or generate with AI
- **AIExecutor** (Phase 2): Always generate fresh code with LLM

### Chain of Work
Complete audit trail of execution:
- Code executed at each node
- Input context and output results
- Execution time and status
- Decisions taken and path followed

### Sandbox (Hetzner VM)
External Docker sandbox for secure code execution:
- **Why external**: Railway doesn't support Docker-in-Docker
- **Location**: Hetzner CPX21 VM (~€6/month)
- **Security**: Resource limits, network disabled, isolated containers
- **API**: HTTP endpoint for code execution

---

## Tech Stack

**Application (Railway)**:
- Backend: FastAPI + Python 3.11
- Workers: Celery + Redis
- Database: PostgreSQL
- Deployment: Railway monolith (~$10-15/month)

**Sandbox (Hetzner)**:
- VM: Hetzner CPX21 (3 vCPU, 4GB RAM)
- Runtime: Docker containers
- Cost: ~€6/month

**Total Cost**: ~$15-20/month for MVP

---

## How Claude Code Should Help

### During Implementation Phase

**Primary tasks**:
1. **Write code** according to [/documentacion/PLAN-FASES.md](documentacion/PLAN-FASES.md)
2. **Follow architecture** from [/documentacion/ARQUITECTURA.md](documentacion/ARQUITECTURA.md)
3. **Create tests** for all components
4. **Debug issues** that arise during development
5. **Optimize** when performance issues appear

**Code location**: All code goes in `/nova/src/`

**Example request**:
```
"Implementa el GraphEngine que ejecuta workflows.
Debe:
- Parsear workflow definitions (JSON)
- Validar estructura del grafo
- Ejecutar nodos secuencialmente
- Gestionar contexto entre nodos
- Registrar en Chain of Work

Código en: /nova/src/core/graph_engine.py"
```

### When Researching Solutions

**Use**:
- `/investigacion/` for competitor analysis (Maisa, n8n)
- `/documentacion/ALTERNATIVAS.md` for technical decisions already made
- `/documentacion/futuro/BACKLOG.md` for future ideas (don't implement in Phase 1)

---

## Communication Style & Language

**Language**: Mario speaks Spanish, but tech terms stay in English
- Responses can be in Spanish or English (follow Mario's lead)
- Code comments in English
- Technical terms: "graph", "executor", "chain-of-work" (not translated)

**Tone**:
- **Technical partner**, not just code generator
- **Challenge assumptions** if there are issues
- **Explain trade-offs**: "Option A is faster but..."
- **Ask clarifying questions** instead of guessing

**Principles**:
- Explain **WHY**, not just **WHAT**
- Provide **concrete examples**
- Suggest **better alternatives** when appropriate
- **Validate understanding**: "¿Tiene sentido esto?"

---

## Key Files to Reference

**⭐⭐ Most Important - Check These First**:
1. [/documentacion/PLAN-FASES.md](documentacion/PLAN-FASES.md) - **Implementation plan (5 phases)**
2. [/documentacion/ARQUITECTURA.md](documentacion/ARQUITECTURA.md) - **How NOVA works**

**When discussing architecture**:
- Start with ARQUITECTURA.md for components and flow
- Check PLAN-FASES.md for implementation steps

**When questioning decisions**:
- Check [/documentacion/ALTERNATIVAS.md](documentacion/ALTERNATIVAS.md) for reasoning

**When implementing**:
- Follow structure in `/nova/README.md`
- Add code to `/nova/src/`
- Database schemas in `/nova/database/`

**For research**:
- Competitors: `/investigacion/referentes/`
- Tech comparisons: `/investigacion/tecnologias/`

---

## Common Workflows

### Workflow: "Implement X component"

```
User: "Implementa el StaticExecutor"

Response:
1. Read /documentacion/ARQUITECTURA.md for StaticExecutor specs
2. Read /documentacion/PLAN-FASES.md for implementation checklist
3. Ask clarifying questions about edge cases
4. Show proposed interface/API design
5. Implement with full error handling
6. Suggest tests to validate functionality
```

### Workflow: "Why did we choose X?"

```
User: "¿Por qué Hetzner en vez de E2B?"

Response:
1. Check /documentacion/ALTERNATIVAS.md
2. Explain reasoning: "Hetzner (~€6/mes) vs E2B (~$126/mes)..."
3. Show trade-offs accepted
4. Ask: "¿Quieres reconsiderar esta decisión?"
```

### Workflow: "Add new feature"

```
User: "Quiero agregar loops a los workflows"

Response:
1. Check /documentacion/futuro/BACKLOG.md (might be there already)
2. Explain impact on current architecture
3. Suggest: "Esto es Phase 2. ¿Agregamos al backlog o implementamos ahora?"
4. If now: design how loops fit into graph architecture
```

---

## Decision Documentation

When making new architectural decisions during development:

1. **Small decisions**: Add to relevant code comments
2. **Medium decisions**: Update `/documentacion/ALTERNATIVAS.md`
3. **Major decisions**: Create new section in ALTERNATIVAS.md with:
   - Context & problem
   - Options considered
   - Decision made & reasoning
   - Trade-offs accepted

**NO ADRs (Architecture Decision Records)**: Keep it simple, use ALTERNATIVAS.md

---

## Recent Architectural Decisions

### RAG System Architecture (2025-11-13)

**Decision**: Removed local RAG/vector store from `/nova`, use only remote `nova-rag` service

**Problem**:
- Local ChromaDB vector store was duplicated (same docs in nova + nova-rag)
- Vector store rebuild on every deploy → slow startup (30-60s)
- Unnecessary memory consumption
- Maintenance overhead (keep 2 systems in sync)

**Options Considered**:
1. **Keep both** (local + remote RAG)
   - ❌ Complexity, duplication, inconsistency risk
2. **Remove local RAG** (selected)
   - ✅ Single source of truth
   - ✅ Fast startup (<5s)
   - ✅ Less memory, simpler code
   - ⚠️ Hard dependency on nova-rag service

**Implementation**:
- Removed `/nova/src/core/ai/vector_store.py`
- Removed `/nova/src/core/ai/document_loader.py`
- Simplified `KnowledgeManager` to ONLY use `RAGClient`
- Updated `tools.py` to use RAGClient
- Added `/knowledge` to `.gitignore` (docs managed by nova-rag)

**Trade-offs Accepted**:
- ⚠️ Hard dependency: If nova-rag is down, CachedExecutor cannot generate code
- ✅ Mitigation: Circuit breaker in RAGClient, clear error messages
- ✅ Development: Run nova-rag locally (simple: `cd nova-rag && uvicorn src.main:app`)

**Benefits Realized**:
- ✅ Startup time: 30-60s → <5s
- ✅ Memory usage: ~500MB → ~200MB (no ChromaDB)
- ✅ Code simplicity: -300 lines of unused code
- ✅ Single source of truth: All docs managed by nova-rag

---

## Example Interaction Patterns

### Good Pattern ✅

```
Mario: "Implementa el GraphEngine"

Claude: "Perfecto. Antes de implementar, confirmo el diseño:

GraphEngine debe:
1. Cargar workflow definition desde PostgreSQL
2. Validar estructura del grafo (¿detecto ciclos?)
3. Ejecutar nodos en orden topológico
4. Usar ExecutorInterface para ejecutar cada nodo
5. Gestionar contexto con ContextManager

¿Es correcto? ¿Algún edge case que deba considerar?"

[Mario confirma o ajusta]

Claude: [Implementa con código completo y comentarios]
```

### Bad Pattern ❌

```
Mario: "Implementa el GraphEngine"

Claude: [Código sin preguntar ni confirmar diseño]
```

---

## Development Commands

```bash
# Working directory
cd /Users/marioferrer/automatizaciones/nova

# Run API locally
uvicorn src.api.main:app --reload

# Run tests
pytest

# Linter
ruff check src/

# Format
black src/
```

---

## Summary

**Your role**: Technical partner helping Mario build NOVA

**Current focus**: Implementation Phase 1 (MVP)

**Key value-adds**:
1. Implement clean, well-documented code
2. Follow architecture from `/documentacion/`
3. Explain trade-offs clearly
4. Challenge assumptions constructively
5. Write tests for everything

**Remember**: Mario is building a real product. Quality matters. Ask questions. Suggest better approaches when you see them.

---

Last updated: 2025-10-27
