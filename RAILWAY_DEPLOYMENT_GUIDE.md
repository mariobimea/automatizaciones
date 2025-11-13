# Railway Multi-Service Deployment Guide

Guía para deployar NOVA como un sistema multi-servicio en Railway.

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│              Railway Project: NOVA                           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │  nova-api    │      │ nova-worker  │      │ nova-rag  │ │
│  │  (Main API)  │─────▶│  (Celery)    │◀────▶│ (RAG)     │ │
│  │              │      │              │      │           │ │
│  │ Port: $PORT  │      │ No port      │      │ Port: 8001│ │
│  └──────────────┘      └──────────────┘      └───────────┘ │
│         │                      │                    │       │
│         ▼                      ▼                    ▼       │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │ PostgreSQL   │      │    Redis     │      │  Volume   │ │
│  │              │      │              │      │ (optional)│ │
│  └──────────────┘      └──────────────┘      └───────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Pre-requisitos

1. Cuenta de Railway con plan Pro (para multi-servicio)
2. GitHub repo con:
   - `/nova` (main API + workers)
   - `/nova-rag` (RAG microservice)

---

## 🚀 Deployment Steps

### Step 1: Crear Proyecto Railway

```bash
# En la raíz del repo
cd /Users/marioferrer/automatizaciones

# Crear proyecto Railway
railway init

# Nombrar proyecto: "nova-production"
```

---

### Step 2: Agregar PostgreSQL y Redis

**En Railway Dashboard:**

1. Click **"New" → "Database" → "PostgreSQL"**
2. Click **"New" → "Database" → "Redis"**

Railway automáticamente creará las variables:
- `DATABASE_URL` (PostgreSQL)
- `REDIS_URL` (Redis)

---

### Step 3: Deployar `nova-rag` (RAG Service)

**En Railway Dashboard:**

1. Click **"New" → "GitHub Repo"**
2. Seleccionar repo: `automatizaciones`
3. **Root Directory**: `/nova-rag`
4. **Service Name**: `nova-rag`

**Environment Variables:**

```bash
# Ninguna variable requerida (opcional)
CHROMA_DB_PATH=/tmp/chroma_db  # Default path
```

**Verificar Deploy:**

```bash
# Una vez deployed, la URL será:
# https://nova-rag-production-xxxx.up.railway.app

# Test health check
curl https://nova-rag-production-xxxx.up.railway.app/health
```

---

### Step 4: Deployar `nova-api` (Main API)

**En Railway Dashboard:**

1. Click **"New" → "GitHub Repo"**
2. Seleccionar repo: `automatizaciones`
3. **Root Directory**: `/nova`
4. **Service Name**: `nova-api`

**Environment Variables:**

```bash
# Database (auto-created)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis (auto-created)
REDIS_URL=${{Redis.REDIS_URL}}

# RAG Service (⭐ IMPORTANTE)
RAG_SERVICE_URL=https://nova-rag-production-xxxx.up.railway.app

# E2B API Key
E2B_API_KEY=e2b_xxxxxxxxxxxxx

# OpenAI API Key
OPENAI_API_KEY=sk-xxxxxxxxxxxxx

# Environment
ENVIRONMENT=production
```

**⚠️ IMPORTANTE**: Reemplazar `nova-rag-production-xxxx` con la URL real de `nova-rag`.

**Verificar Deploy:**

```bash
# Test health check
curl https://nova-api-production-xxxx.up.railway.app/health
```

---

### Step 5: Deployar `nova-worker` (Celery Workers)

**En Railway Dashboard:**

1. Click **"New" → "GitHub Repo"**
2. Seleccionar repo: `automatizaciones`
3. **Root Directory**: `/nova`
4. **Service Name**: `nova-worker`

**Environment Variables:**

```bash
# Database (auto-created)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis (auto-created)
REDIS_URL=${{Redis.REDIS_URL}}

# RAG Service
RAG_SERVICE_URL=${{nova-rag.RAILWAY_PUBLIC_DOMAIN}}

# E2B API Key
E2B_API_KEY=e2b_xxxxxxxxxxxxx

# OpenAI API Key
OPENAI_API_KEY=sk-xxxxxxxxxxxxx

# Environment
ENVIRONMENT=production
```

**Custom Start Command:**

En Railway Settings → Deploy → **Custom Start Command**:

```bash
celery -A src.workers.celery_app worker --loglevel=info --concurrency=2
```

**Disable Web Service:**

En Railway Settings → Deploy → **Service Type**: `Worker`

---

### Step 6: Conectar Servicios

**Internal URLs** (para comunicación entre servicios):

Railway provee URLs internas automáticamente:

```bash
# nova-rag internal URL (usado por nova-api y nova-worker)
RAG_SERVICE_URL=http://nova-rag.railway.internal:8001

# O usar la URL pública (funciona igual):
RAG_SERVICE_URL=https://nova-rag-production-xxxx.up.railway.app
```

**⚠️ Mejor práctica**: Usar URL pública (más confiable en Railway).

---

## 🔧 Configuración de Variables de Entorno

### Tabla de Variables por Servicio

| Variable | nova-api | nova-worker | nova-rag | Notas |
|----------|----------|-------------|----------|-------|
| `DATABASE_URL` | ✅ | ✅ | ❌ | Auto-injected by Railway |
| `REDIS_URL` | ✅ | ✅ | ❌ | Auto-injected by Railway |
| `RAG_SERVICE_URL` | ✅ | ✅ | ❌ | URL de nova-rag |
| `E2B_API_KEY` | ✅ | ✅ | ❌ | Para sandbox |
| `OPENAI_API_KEY` | ✅ | ✅ | ❌ | Para AI code gen |
| `ENVIRONMENT` | ✅ | ✅ | ✅ | "production" |
| `PORT` | Auto | ❌ | Auto | Railway asigna automáticamente |

---

## ✅ Verificación Post-Deploy

### 1. Check RAG Service

```bash
# Health check
curl https://nova-rag-production-xxxx.up.railway.app/health

# Expected response:
{
  "status": "healthy",
  "vector_store_ready": true,
  "documents_loaded": 1234
}

# Stats
curl https://nova-rag-production-xxxx.up.railway.app/rag/stats

# Expected response:
{
  "total_documents": 1234,
  "sources": ["pymupdf", "easyocr", "requests"],
  "topics": ["official", "tutorial"],
  "status": "ready"
}
```

### 2. Check Main API

```bash
# Health check
curl https://nova-api-production-xxxx.up.railway.app/health

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}

# List workflows
curl https://nova-api-production-xxxx.up.railway.app/workflows
```

### 3. Test End-to-End Workflow

```bash
# Submit workflow
curl -X POST https://nova-api-production-xxxx.up.railway.app/workflows/execute \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "invoice_workflow",
    "context": {...}
  }'

# Expected response:
{
  "task_id": "abc-123-def-456",
  "status": "queued"
}

# Check task status
curl https://nova-api-production-xxxx.up.railway.app/tasks/abc-123-def-456
```

---

## 📊 Monitoreo

### Railway Logs

**Ver logs en tiempo real:**

1. Dashboard → Service → **"Logs"** tab
2. Filtrar por servicio:
   - `nova-api`: API requests
   - `nova-worker`: Workflow executions
   - `nova-rag`: RAG queries

**Logs importantes a monitorear:**

```
# nova-api
✅ "Workflow queued: task_id=abc-123"
✅ "RAG client initialized with base_url: https://..."

# nova-worker
✅ "Executing workflow: workflow_id=invoice_workflow"
✅ "RAG query successful: 5 results for 'extract PDF text'"

# nova-rag
✅ "Vector store loaded with 1234 documents"
✅ "RAG query: 5 results for 'extract PDF text'"
```

---

## 💰 Costos Estimados

| Servicio | Recursos | Costo Mensual |
|----------|----------|---------------|
| `nova-api` | 1 vCPU, 512MB RAM | ~$5 |
| `nova-worker` | 1 vCPU, 512MB RAM | ~$5 |
| `nova-rag` | 1 vCPU, 1GB RAM | ~$7 |
| PostgreSQL | 1GB storage | $5 |
| Redis | 256MB RAM | $5 |
| **Total** | | **~$27/month** |

**Optimización**:
- Compartir `nova-api` + `nova-worker` en un solo servicio: **~$22/month**
- Usar Railway volume para persistir vector store: **+$1/GB**

---

## 🔄 Re-Deploy & Updates

### Update Code (Auto-Deploy)

Railway re-deploya automáticamente en cada push a GitHub:

```bash
# Local
git add .
git commit -m "Update workflow logic"
git push origin main

# Railway auto-deploya
```

### Update RAG Docs (Manual Reload)

Si actualizas documentación sin re-deployar:

```bash
# Trigger reload endpoint
curl -X POST https://nova-rag-production-xxxx.up.railway.app/rag/reload

# Response:
{
  "message": "Documentation reload started in background",
  "documents_loaded": 0
}
```

---

## 🐛 Troubleshooting

### Error: RAG Service Unavailable

**Síntoma**:
```
ERROR: RAG service unavailable at http://nova-rag:8001
```

**Solución**:
1. Verificar que `nova-rag` está deployed y healthy
2. Verificar `RAG_SERVICE_URL` en `nova-api` y `nova-worker`
3. Usar URL pública en vez de interna:
   ```bash
   RAG_SERVICE_URL=https://nova-rag-production-xxxx.up.railway.app
   ```

---

### Error: Vector Store Not Ready

**Síntoma**:
```
503 Service Unavailable: Vector store not ready yet
```

**Solución**:
1. Esperar 1-2 minutos después del deploy (carga inicial)
2. Verificar logs de `nova-rag`:
   ```
   Loading documentation into vector store...
   ✓ Loaded 1234 chunks
   ```

---

### Error: Slow Deploys

**Síntoma**:
- Deploy de `nova-api` tarda >5 minutos

**Solución**:
- ✅ Verificar que `chromadb` y `sentence-transformers` NO están en `/nova/requirements.txt`
- ✅ Solo deben estar en `/nova-rag/requirements.txt`

---

## 📚 Referencias

- [Railway Docs - Multi-Service Projects](https://docs.railway.app/develop/services)
- [Railway Docs - Environment Variables](https://docs.railway.app/develop/variables)
- [NOVA Architecture](./documentacion/ARQUITECTURA.md)
- [NOVA RAG Service README](./nova-rag/README.md)

---

**Last Updated**: 2025-11-13
