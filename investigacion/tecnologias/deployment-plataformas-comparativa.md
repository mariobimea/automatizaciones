# Comparativa de Plataformas de Deployment para NOVA MVP

**Fecha**: 2025-10-23
**Contexto**: Análisis exhaustivo de opciones de deployment para proyecto NOVA (plataforma de agentes AI)
**Presupuesto objetivo**: $10-20/mes para MVP, escalable a $50-100/mes
**Timeline**: 2 semanas para MVP funcional

---

## Contexto del Proyecto NOVA

### Stack Técnico Requerido
- **Backend**: FastAPI (Python)
- **Databases**: PostgreSQL + Redis
- **Workers**: Celery (procesamiento asíncrono)
- **Sandboxing**: Ejecución de código Python no confiable (generado por LLM)
- **Docker**: NO disponible Docker-in-Docker en Railway

### Requisitos Críticos
1. **Seguridad**: Ejecutar código LLM-generated de forma aislada
2. **Escalabilidad**: Arrancar con MVP, crecer según demanda
3. **Costo**: Presupuesto inicial muy limitado ($10-20/mes)
4. **Rapidez**: Deploy funcional en 2 semanas
5. **Simplicidad**: Minimizar ops overhead

---

## 🏆 Análisis Comparativo de Plataformas

### 1. Railway.app ⭐ MEJOR PARA MVP RÁPIDO

#### Overview
Railway es una PaaS moderna con énfasis en developer experience. Usa Nixpacks para builds automáticos y soporta deployment directo desde GitHub.

#### Capacidades Técnicas

**✅ Soportado:**
- PostgreSQL nativo (managed database)
- Redis nativo (managed)
- Celery workers (deploy como service separado)
- FastAPI / Python apps
- Templates one-click para Django+Celery+Redis+PostgreSQL
- Auto-scaling básico
- Environment variables con referencias entre servicios
- Private networking entre servicios

**❌ NO Soportado:**
- **Docker-in-Docker (DinD)** - Limitación crítica
- Privileged containers
- Nested containerization
- GPU access
- Advanced networking (VPNs, etc)

#### Pricing (2024)

**Plan Hobby: $5/mes**
- Incluye $5 de créditos de uso
- Si uso total ≤ $5 → solo pagas $5
- Si uso > $5 → pagas $5 + delta

**Plan Pro: $20/mes**
- Incluye $20 de créditos
- Mejor para producción

**Cálculo de costos por recursos:**
```
CPU: $20/vCPU/mes ($0.027/hora)
RAM: $10/GB/mes ($0.014/hora)
Network egress: $0.10/GB
Storage: Incluido en databases
```

**Ejemplo real de costos:**
- Small worker + Rails server + Postgres: ~$12/mes
- API básica + PostgreSQL + Redis: ~$3-8/mes (dentro del Hobby plan)

#### Arquitectura en Railway

```
┌─────────────────────────────────────────┐
│         Railway Project (NOVA)          │
├─────────────────────────────────────────┤
│                                         │
│  Service 1: FastAPI (public)            │
│    - Expuesto en HTTPS                  │
│    - Variables: DATABASE_URL, REDIS_URL │
│                                         │
│  Service 2: Celery Worker (private)     │
│    - NO expuesto                        │
│    - Conecta vía internal network       │
│                                         │
│  Service 3: PostgreSQL (private)        │
│    - Managed database                   │
│    - Backups automáticos                │
│                                         │
│  Service 4: Redis (private)             │
│    - Managed cache/queue                │
│                                         │
└─────────────────────────────────────────┘
```

#### Pros para NOVA
- ✅ **Setup ultra-rápido**: Templates preconstruidos Django+Celery+Redis+PostgreSQL
- ✅ **PostgreSQL y Redis managed**: Sin configuración manual
- ✅ **Celery support nativo**: Ejemplos y templates disponibles
- ✅ **Costo predecible**: Usage-based, ideal para tráfico variable
- ✅ **Developer experience**: Deploy con git push, zero config
- ✅ **Private networking**: Redis y PostgreSQL no expuestos públicamente
- ✅ **Variables de referencia**: `${{Postgres.DATABASE_URL}}` entre servicios

#### Contras para NOVA
- ❌ **NO Docker-in-Docker**: Sandboxing debe ser externo
- ❌ **Vendor lock-in moderado**: Nixpacks es Railway-specific
- ❌ **Costos pueden escalar**: Si uso crece, puede superar Fly.io
- ❌ **Menos control**: No acceso a sistema de archivos, networking limitado

#### Solución para Sandboxing
Como Railway **NO soporta DinD**, opciones:
1. **E2B Cloud** (recomendado) - API externa para sandboxing
2. **AWS Lambda** - Función serverless para ejecutar código
3. **Modal.com** - Python sandboxes managed
4. **VM separada** - DigitalOcean/Hetzner con Docker

#### Costo Total Estimado (MVP)
```
Railway Hobby:           $5/mes
E2B Free Tier:          $0 (hasta $100 créditos)
───────────────────────────────
Total MVP:              $5/mes ✅

Con uso real (~1k ejecuciones/día):
Railway:                $10-15/mes (algunos overages)
E2B:                    ~$126/mes (30s promedio * 30k ejecuciones)
───────────────────────────────
Total producción ligera: $136-141/mes ⚠️
```

#### Veredicto Railway
**MEJOR para MVP rápido** si combinamos con E2B para sandboxing. Developer experience excelente, costo inicial mínimo, pero costos de sandboxing pueden ser altos.

---

### 2. Render.com - ALTERNATIVA ESTABLE

#### Overview
Render es un competidor de Heroku con pricing más predecible. Ofrece servicios managed similares a Railway pero con un modelo de pricing más tradicional.

#### Capacidades Técnicas

**✅ Soportado:**
- PostgreSQL managed
- Redis managed
- Web services (FastAPI)
- Background workers (Celery)
- Docker containers custom
- Cron jobs
- Private services

**❌ NO Soportado:**
- Docker-in-Docker
- GPU workloads
- Advanced networking

#### Pricing (2024)

**Free Tier:**
- Web services: Spin down after 15 min inactivity
- PostgreSQL: 90 días, luego se borra
- Redis: 90 días, luego se borra
- NO apto para producción

**Paid Tiers:**
- **Starter**: $7/mes por service (25 horas/mes)
- **Standard**: $25/mes por service
- **PostgreSQL**: $7-$95/mes (según specs)
- **Redis**: $10-$250/mes (según specs)

**Ejemplo de stack completo:**
```
FastAPI (Starter):       $7/mes
Celery Worker (Starter): $7/mes
PostgreSQL (Starter):    $7/mes
Redis (Starter):         $10/mes
──────────────────────────────
Total:                   $31/mes
```

#### Pros para NOVA
- ✅ **Pricing predecible**: Fixed cost por service
- ✅ **Stack completo soportado**: PostgreSQL, Redis, Celery
- ✅ **Estabilidad**: Empresa madura, menos outages que Railway
- ✅ **Docker support**: Dockerfile custom si necesitas
- ✅ **Blueprint YAML**: Infrastructure as code
- ✅ **Health checks y auto-restart**

#### Contras para NOVA
- ❌ **Costo base más alto**: ~$31/mes mínimo vs $5 Railway
- ❌ **Menos flexible**: Fixed pricing sin usage-based
- ❌ **Developer experience**: Menos pulido que Railway
- ❌ **NO Docker-in-Docker**: Mismo problema que Railway
- ❌ **Free tier limitado**: No apto para testing prolongado

#### Veredicto Render
**MEJOR para producción estable** con tráfico constante. Más caro que Railway para MVP, pero costs más predecibles. Requiere E2B para sandboxing.

---

### 3. Fly.io - MÁXIMA FLEXIBILIDAD

#### Overview
Fly.io ejecuta apps en Firecracker microVMs con foco en edge computing y distribución global. CLI-first approach.

#### Capacidades Técnicas

**✅ Soportado:**
- Full Docker support (Dockerfile required)
- PostgreSQL via fly-postgres
- Redis via Upstash integration
- Multi-region deployment
- Kubernetes-like architecture
- SSH access to VMs
- GPU instances (limitado)

**❌ NO Soportado:**
- Docker-in-Docker (por seguridad)
- Native managed databases (solo Postgres HA clusters)
- One-click templates (más manual)

#### Pricing (2024)

**Pay-as-you-go (nuevo modelo Oct 2024):**
```
Machines (shared CPU):
- 256MB RAM: ~$2/mes (24/7)
- 1GB RAM: ~$6/mes (24/7)

Machines (dedicated):
- 1 vCPU + 2GB: ~$20/mes

Storage:
- $0.15/GB/mes

PostgreSQL:
- Single node: ~$2/mes
- HA cluster: ~$82-164/mes

Redis (Upstash):
- Pay-as-you-go: desde $0
- Fixed plans: $10-50/mes
```

**Free Allowance:**
- $5/mes de créditos gratuitos
- 3 shared VMs (256MB)
- 160GB bandwidth

#### Arquitectura en Fly.io

```
┌──────────────────────────────────────┐
│     Fly.io Organization (NOVA)       │
├──────────────────────────────────────┤
│                                      │
│  App: nova-api                       │
│    - Dockerfile custom               │
│    - 1 machine, 1GB RAM              │
│    - Public HTTPS                    │
│                                      │
│  App: nova-worker                    │
│    - Celery worker                   │
│    - 1 machine, 512MB                │
│    - Private                         │
│                                      │
│  App: nova-postgres                  │
│    - fly-postgres template           │
│    - Single node (MVP)               │
│                                      │
│  Redis: Upstash integration          │
│    - External managed service        │
│                                      │
└──────────────────────────────────────┘
```

#### Pros para NOVA
- ✅ **Full Docker support**: Mayor control sobre runtime
- ✅ **Firecracker VMs**: Mejor aislamiento que containers
- ✅ **SSH access**: Debug directo en VMs
- ✅ **Scaling granular**: Auto-start/stop por request
- ✅ **Global edge**: Deployment cerca de usuarios
- ✅ **CLI poderoso**: flyctl con muchas features

#### Contras para NOVA
- ❌ **Setup más complejo**: Dockerfiles requeridos, más manual
- ❌ **NO DinD**: Mismo problema de sandboxing
- ❌ **Curva de aprendizaje**: Más técnico que Railway
- ❌ **Databases menos managed**: PostgreSQL requiere más config
- ❌ **Documentación fragmentada**: Menos ejemplos prehechos
- ❌ **Regional pricing**: Costos varían por región

#### Costo Total Estimado (MVP)
```
API (1GB, shared):      $6/mes
Worker (512MB, shared): $4/mes
PostgreSQL (single):    $2/mes
Redis (Upstash basic):  $10/mes
──────────────────────────────
Total:                  $22/mes

Dentro de free tier podría ser ~$17/mes ✅
```

#### Veredicto Fly.io
**MEJOR para control total y edge deployment**. Más técnico pero más flexible. Requiere E2B para sandboxing al igual que Railway.

---

### 4. Modal.com - ESPECIALISTA EN PYTHON SERVERLESS

#### Overview
Modal es una plataforma serverless diseñada específicamente para workloads de ML/AI en Python. **Incluye sandboxing nativo con gVisor**.

#### Capacidades Técnicas

**✅ Soportado:**
- **Python sandboxes nativos** con `@app.function()` decorator
- GPU support (H100, A100, etc)
- Container-based execution
- Auto-scaling instantáneo
- Secrets management
- Scheduled functions
- Web endpoints
- gVisor runtime para isolation

**❌ NO Soportado:**
- Databases managed (necesitas external)
- Redis managed (necesitas external)
- Long-running services tradicionales
- Non-Python workloads (muy limitado)

#### Pricing (2024)

**Free Tier:**
- $30/mes en créditos gratuitos (PERPETUO)
- Suficiente para MVPs pequeños

**Pay-as-you-go:**
```
CPU:
- $0.00003/second (shared)
- ~$0.11/hora para 1 CPU

GPU (ejemplos):
- T4: $0.00060/second (~$2.16/hora)
- A100: $0.00450/second (~$16.20/hora)

Pricing reciente 2024:
- 15-30% reducción en CPUs y GPUs top
```

**Ejemplo de uso real:**
- Whisper Large (5 min audio, T4, 30s): $0.00438
- 1000 ejecuciones/día (30s cada una): ~$4.20/día = $126/mes

#### Arquitectura en Modal

```
┌─────────────────────────────────────┐
│       Modal.com (NOVA)              │
├─────────────────────────────────────┤
│                                     │
│  @app.function() - execute_code     │
│    - Sandbox con gVisor             │
│    - Timeout configurable           │
│    - Memoria configurable           │
│    - Auto-scaling                   │
│                                     │
│  @app.function() - generate_plan    │
│    - LLM API calls                  │
│                                     │
└─────────────────────────────────────┘

External (Railway/Render):
- PostgreSQL (estado, chain-of-work)
- Redis (queue, cache)
- API Gateway
```

#### Pros para NOVA
- ✅ **Sandboxing NATIVO**: gVisor built-in, NO necesita E2B
- ✅ **Python-first**: Perfecto para nuestro stack
- ✅ **$30/mes gratis perpetuo**: Suficiente para testing
- ✅ **Cold start <1s**: Muy rápido
- ✅ **Developer experience**: `@app.function()` es trivial
- ✅ **Auto-scaling ilimitado**: De 0 a 1000 workers
- ✅ **GPU support**: Si el futuro necesitamos ML

#### Contras para NOVA
- ❌ **NO tiene databases**: PostgreSQL y Redis externos
- ❌ **Vendor lock-in fuerte**: Código muy Modal-specific
- ❌ **Costos pueden explotar**: $126/mes solo en sandboxing
- ❌ **No long-running**: No apto para API 24/7 tradicional
- ❌ **Solo funciona para Python**: No Node.js ni otros lenguajes

#### Arquitectura Híbrida Modal + Railway

**Opción A: Modal SOLO para sandboxing**
```
Railway:
- FastAPI API (public)
- PostgreSQL
- Redis
- Celery coordinator

Modal:
- execute_code() function
- API endpoint que Railway llama
```

**Costos combinados:**
```
Railway (API + DBs):    $10/mes
Modal (sandboxing):     $126/mes (1k ejecuciones/día)
───────────────────────────────
Total:                  $136/mes
```

**Opción B: Modal para TODO el processing**
```
Modal:
- API endpoints
- Code execution
- LLM generation

External:
- PostgreSQL (Supabase Free: $0)
- Redis (Upstash Free: $0)
```

**Costos:**
```
Modal:                  $126/mes (dentro de free tier si <$30 uso)
Supabase Free:          $0
Upstash Free:           $0
───────────────────────────────
Total:                  $0-126/mes ✅
```

#### Veredicto Modal
**MEJOR solución técnica para sandboxing Python**. Si usamos Modal SOLO para execution + databases gratis externos, podríamos tener MVP casi gratis. Sin embargo, vendor lock-in es muy alto.

---

### 5. Desarrollo Local + ngrok - MVP ULTRA-RÁPIDO

#### Overview
Desarrollar localmente con Docker Compose y exponer vía ngrok/localtunnel para testing externo.

#### Capacidades Técnicas

**✅ Soportado:**
- **Docker-in-Docker NATIVO**: Control total sobre sandboxing
- PostgreSQL local
- Redis local
- Celery workers
- FastAPI
- gVisor, Firecracker, o Docker simple

**❌ NO Soportado:**
- Uptime 24/7 (tu laptop debe estar encendida)
- Escalabilidad
- Alta disponibilidad

#### Pricing

**Gratis total:**
- ngrok Free: 1 static domain, 1 agent online
- LocalTunnel: Gratis, menos estable
- Infraestructura: Tu laptop

**ngrok Plus ($8/mes):**
- 3 agents
- Custom domains
- Mejor para demos profesionales

#### Arquitectura

```
┌─────────────────────────────────┐
│     Tu Laptop (Docker Compose)  │
├─────────────────────────────────┤
│                                 │
│  Container: FastAPI             │
│    - Port 8000                  │
│                                 │
│  Container: Celery Worker       │
│                                 │
│  Container: PostgreSQL          │
│    - Port 5432                  │
│                                 │
│  Container: Redis               │
│    - Port 6379                  │
│                                 │
│  Container: Sandbox Executor    │
│    - Docker-in-Docker aquí! ✅  │
│    - gVisor runtime             │
│                                 │
└─────────────────────────────────┘
          ↓
     ngrok tunnel
          ↓
https://nova-demo.ngrok.io (público)
```

#### Pros para NOVA
- ✅ **GRATIS TOTAL**: $0 para MVP completo
- ✅ **Docker-in-Docker funciona**: Control total sobre sandboxing
- ✅ **Desarrollo = producción**: Mismo ambiente
- ✅ **Debugging fácil**: Logs locales, no remote
- ✅ **Iteración rápida**: Sin deploys, cambios instantáneos
- ✅ **Sin vendor lock-in**: Portabilidad total

#### Contras para NOVA
- ❌ **No uptime garantizado**: Laptop debe estar on
- ❌ **No escalabilidad**: Recursos locales limitados
- ❌ **IP dinámica**: ngrok URLs cambian (salvo paid plan)
- ❌ **Demo-only**: No apto para usuarios reales
- ❌ **Sin monitoring**: Necesitas configurar todo manualmente

#### Uso Recomendado
- ✅ **Semana 1-2 del MVP**: Desarrollo y testing
- ✅ **Demos a investors/usuarios**: Con ngrok paid ($8/mes)
- ✅ **Validación de concepto**: Antes de cloud deployment
- ❌ **Producción real**: Migrar a Railway/Modal después

#### Veredicto Local + ngrok
**MEJOR para arrancar el MVP**. Permite validar el concepto con $0 de costo, implementar Docker-in-Docker sin restricciones, y migrar después a cloud cuando haya tracción.

---

## 📊 Tabla Comparativa Definitiva

| Criterio | Railway | Render | Fly.io | Modal | Local+ngrok |
|----------|---------|--------|--------|-------|-------------|
| **Setup Time** | 1 hora | 2 horas | 4 horas | 2 horas | 30 min |
| **Docker-in-Docker** | ❌ No | ❌ No | ❌ No | ⚠️ gVisor | ✅ Sí |
| **PostgreSQL** | ✅ Managed | ✅ Managed | ⚠️ Semi-managed | ❌ Externo | ✅ Local |
| **Redis** | ✅ Managed | ✅ Managed | ⚠️ Upstash | ❌ Externo | ✅ Local |
| **Celery Workers** | ✅ Sí | ✅ Sí | ✅ Sí | ⚠️ Funciones | ✅ Sí |
| **Sandboxing Solution** | E2B | E2B | E2B | Nativo | Docker |
| **Costo MVP (mes 1)** | $5 | $31 | $17 | $0-30 | $0 |
| **Costo Producción** | $136 | $157 | $138 | $126 | N/A |
| **Developer Experience** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Vendor Lock-in** | Medio | Bajo | Bajo | Alto | Ninguno |
| **Escalabilidad** | Buena | Buena | Excelente | Excelente | Ninguna |
| **Uptime 24/7** | ✅ Sí | ✅ Sí | ✅ Sí | ✅ Sí | ❌ No |

---

## 🎯 Recomendaciones por Caso de Uso

### Para MVP en 2 semanas (tu caso)

**OPCIÓN RECOMENDADA: Híbrido en 2 fases**

#### FASE 1: Semanas 1-2 (Desarrollo)
**Stack: Local + ngrok**
- Docker Compose local con todo el stack
- Docker-in-Docker para sandboxing
- Validar concepto con facturas reales
- Demos a usuarios early con ngrok
- **Costo: $0**

#### FASE 2: Post-validación (Deployment)
**Stack: Railway + E2B**
- Railway para API, PostgreSQL, Redis, Celery
- E2B para sandboxing (reemplaza Docker-in-Docker)
- Deploy en 1 día desde código local
- **Costo inicial: $5-15/mes**
- **Costo con uso real: $136-141/mes**

### ¿Por qué esta estrategia?

1. **Time-to-market óptimo**: Empiezas codificando en minutos
2. **Zero friction**: Sin batallas con cloud providers
3. **Validación real**: Docker-in-Docker funciona local
4. **Path to production claro**: Railway + E2B está probado
5. **Costo inicial $0**: No gastas hasta validar

---

## 🚨 Análisis Crítico: Sandboxing

### El Problema Central
**Railway, Render y Fly.io NO soportan Docker-in-Docker por seguridad.**

Esto significa que tu arquitectura MVP con Docker sandboxing **NO puede deployarse directamente en estas plataformas**.

### Soluciones Viables

#### Opción A: E2B Cloud Sandboxes ⭐ RECOMENDADO
- ✅ **Seguridad enterprise**: Firecracker microVMs
- ✅ **Rápido**: ~150ms cold start
- ✅ **Compatible con Railway/Render/Fly**: API externa
- ❌ **Costo**: ~$126/mes con 1k ejecuciones/día (30s cada una)
- ❌ **Vendor lock-in**: Cambiar después requiere refactor

```python
# Implementación E2B
from e2b import Sandbox

async def execute_code(code: str):
    sandbox = await Sandbox.create(template="python")
    result = await sandbox.run_code(code)
    await sandbox.close()
    return result
```

#### Opción B: Modal.com para Sandboxing
- ✅ **Sandboxing nativo**: gVisor incluido
- ✅ **$30/mes gratis perpetuo**
- ✅ **Python-first**
- ❌ **Vendor lock-in extremo**: @app.function() muy específico
- ❌ **Arquitectura híbrida**: Railway para DBs + Modal para exec

```python
# Implementación Modal
import modal
app = modal.App("nova")

@app.function()
async def execute_code(code: str):
    # Ejecuta en sandbox gVisor automáticamente
    exec(code)
```

#### Opción C: AWS Lambda para Execution
- ✅ **Seguro**: Lambda isolation nativo
- ✅ **Escalable**: Auto-scaling infinito
- ❌ **Complejidad**: Deployment separado en AWS
- ❌ **Cold starts**: 1-3 segundos
- ❌ **15 min limit**: No apto para tareas largas

#### Opción D: VM Dedicada (Post-MVP)
- ✅ **Control total**: Docker, gVisor, Firecracker
- ✅ **Costo fijo**: ~$5-10/mes (Hetzner, DigitalOcean)
- ❌ **Ops overhead**: Gestión manual de servidor
- ❌ **Tiempo setup**: 1-2 días adicionales

### Comparativa de Sandboxing

| Solución | Seguridad | Costo (1k/día) | Setup Time | Lock-in |
|----------|-----------|----------------|------------|---------|
| E2B | ⭐⭐⭐⭐⭐ | $126/mes | 1 día | Medio |
| Modal | ⭐⭐⭐⭐ | $126/mes | 1 día | Alto |
| AWS Lambda | ⭐⭐⭐⭐ | $50/mes | 3 días | Medio |
| VM Dedicada | ⭐⭐⭐ | $10/mes | 5 días | Bajo |
| Local Docker | ⭐⭐⭐ | $0 | 0 días | Ninguno |

---

## 💰 Análisis de Costos Realista

### Escenario MVP (100 ejecuciones/día, 20s promedio)

```
=== OPCIÓN 1: Railway + E2B ===
Railway Hobby:              $5/mes
E2B (60k segundos/mes):     $8.40/mes
─────────────────────────────────
TOTAL:                      $13.40/mes ✅

=== OPCIÓN 2: Modal + Databases Externas ===
Modal (60k segundos):       ~$2/mes (dentro de $30 free)
Supabase PostgreSQL:        $0/mes (free tier)
Upstash Redis:              $0/mes (free tier)
─────────────────────────────────
TOTAL:                      $0/mes 🎉

=== OPCIÓN 3: Local + ngrok ===
Todo local:                 $0/mes
ngrok (opcional):           $0-8/mes
─────────────────────────────────
TOTAL:                      $0-8/mes ✅
```

### Escenario Tracción Inicial (1,000 ejecuciones/día)

```
=== OPCIÓN 1: Railway + E2B ===
Railway (overages):         $15/mes
E2B (600k seg/mes):         $84/mes
─────────────────────────────────
TOTAL:                      $99/mes ⚠️

=== OPCIÓN 2: Modal + Databases Externas ===
Modal (600k seg):           $20/mes (sobre free tier)
Supabase:                   $0/mes (aún en free)
Upstash:                    $0/mes (aún en free)
─────────────────────────────────
TOTAL:                      $20/mes ✅

=== OPCIÓN 3: Fly.io + E2B ===
Fly.io (API + DBs):         $22/mes
E2B:                        $84/mes
─────────────────────────────────
TOTAL:                      $106/mes ⚠️
```

### Escenario Crecimiento (5,000 ejecuciones/día)

```
=== OPCIÓN 1: Railway + E2B ===
Railway:                    $30/mes
E2B (3M seg/mes):           $420/mes 🚨
─────────────────────────────────
TOTAL:                      $450/mes 💸

=== OPCIÓN 2: Modal Completo ===
Modal (3M seg):             $100/mes
Databases externas:         $25/mes (paid tiers)
─────────────────────────────────
TOTAL:                      $125/mes ✅

=== OPCIÓN 3: VM Dedicada ===
Railway (sin sandboxing):   $20/mes
Hetzner CPX21:              $10/mes
(Docker + gVisor propio)
─────────────────────────────────
TOTAL:                      $30/mes ⭐
```

### Breaking Points

| Ejecuciones/día | Railway+E2B | Modal | Fly+E2B | VM Dedicada |
|-----------------|-------------|-------|---------|-------------|
| 100 | $13 ✅ | $0 🎉 | $20 | $30 |
| 1,000 | $99 | $20 ✅ | $106 | $30 ✅ |
| 5,000 | $450 🚨 | $125 | $456 🚨 | $30 ⭐ |
| 10,000 | $900 💸 | $250 | $912 💸 | $50 ⭐ |

**Conclusión de costos**: Modal es más barato hasta ~5k ejecuciones/día. Después, VM dedicada se vuelve necesaria.

---

## 🏗️ Arquitectura Recomendada: 3 Fases

### FASE 1: MVP Local (Semanas 1-2) 💚 START HERE

**Objetivo**: Validar concepto, código funcional, demos

**Stack:**
```yaml
# docker-compose.yml
services:
  api:
    build: ./api
    ports: ["8000:8000"]
    depends_on: [postgres, redis]

  worker:
    build: ./api
    command: celery -A nova worker
    depends_on: [redis, postgres]

  sandbox:
    image: python:3.11-slim
    privileged: true  # Para DinD
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock

  postgres:
    image: postgres:15
    volumes: [pgdata:/var/lib/postgresql/data]

  redis:
    image: redis:7-alpine
```

**Exposición pública:**
```bash
# Desarrollo
uvicorn main:app --reload

# Demos externos
ngrok http 8000
# → https://nova-xyz.ngrok.io
```

**Pros de esta fase:**
- ✅ $0 de costo
- ✅ Docker-in-Docker funciona perfectamente
- ✅ Iteración ultra-rápida
- ✅ Testing real con facturas
- ✅ Demos a early users

**Cuándo salir**: Cuando necesites uptime 24/7 o tengas >10 usuarios concurrentes

### FASE 2: Cloud Deployment (Semana 3-4) 🟡 SCALING

**Objetivo**: Uptime 24/7, usuarios reales, estabilidad

**Opción A: Railway + E2B (más simple)**

```
Railway Project:
├── api (FastAPI)
│   └── Llama E2B API para sandboxing
├── worker (Celery)
├── postgres (managed)
└── redis (managed)

E2B:
└── Sandboxes on-demand
```

**Setup:**
```bash
# 1. Push a Railway
railway login
railway init
railway up

# 2. Configurar E2B
pip install e2b
export E2B_API_KEY=xxx

# 3. Cambiar sandbox executor
# De: DockerSandbox()
# A: E2BSandbox()
```

**Costo**: $13/mes (100 exec/día) → $99/mes (1k exec/día)

**Opción B: Modal + Databases Externas (más barato)**

```
Modal:
├── @app.function() execute_code  # Sandbox nativo
├── @app.function() generate_plan
└── @app.web_endpoint() api

Supabase: PostgreSQL (free tier)
Upstash: Redis (free tier)
```

**Setup:**
```bash
# 1. Deploy a Modal
modal deploy nova.py

# 2. Conectar DBs externas
export DATABASE_URL=postgresql://supabase...
export REDIS_URL=redis://upstash...
```

**Costo**: $0/mes (MVP) → $20/mes (1k exec/día)

**Cuándo salir**: Cuando costos de E2B superen $200/mes o necesites features custom

### FASE 3: Self-Hosted Sandboxing (Mes 3+) 🔴 OPTIMIZATION

**Objetivo**: Control total, costos optimizados, features custom

**Stack:**
```
Railway/Render:
├── API (FastAPI)
├── Worker (Celery)
├── PostgreSQL
└── Redis
    ↓
    Calls via private network
    ↓
Hetzner CPX21 VM:
├── Docker daemon
├── gVisor runtime
├── Sandbox API (FastAPI)
└── Resource monitoring
```

**Implementación:**
```python
# sandbox_vm.py (en Hetzner)
from fastapi import FastAPI
import docker

app = FastAPI()
client = docker.from_env()

@app.post("/execute")
async def execute(code: str):
    container = client.containers.run(
        "python:3.11-slim",
        f"python -c '{code}'",
        mem_limit="512m",
        cpu_period=100000,
        cpu_quota=100000,  # 1 CPU
        network_disabled=True,
        runtime="runsc",  # gVisor
        remove=True
    )
    return {"output": container.logs()}
```

**Setup VM:**
```bash
# En Hetzner CPX21 (€5.83/mes)
apt update && apt install docker.io

# Instalar gVisor
wget https://storage.googleapis.com/gvisor/releases/runsc
chmod +x runsc
mv runsc /usr/local/bin/

# Configurar Docker con gVisor
cat >> /etc/docker/daemon.json <<EOF
{
  "runtimes": {
    "runsc": {
      "path": "/usr/local/bin/runsc"
    }
  }
}
EOF

systemctl restart docker

# Deploy sandbox API
docker run -d -p 8080:8080 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  nova-sandbox:latest
```

**Costo**: $30-50/mes independiente del volumen (hasta límite de VM)

**Cuándo implementar**:
- Costos de E2B/Modal > $200/mes
- Necesitas timeouts custom >60s
- Compliance requiere control de infraestructura
- Quieres features específicos (GPU, networking custom)

---

## 🎓 Lecciones de las Búsquedas

### 1. Docker-in-Docker es un Deal-Breaker Universal
**Todas las PaaS modernas lo prohíben por seguridad:**
- Railway: Explícitamente no soportado, sin planes de agregarlo
- Render: No soportado
- Fly.io: Firecracker VMs impiden DinD
- Heroku: No soportado

**Razón**: Compartir el Docker socket del host es un riesgo de seguridad masivo. Cualquier escape del container compromete el host entero.

**Alternativas reales**:
- E2B: Firecracker microVMs (hardware-level isolation)
- Modal: gVisor (userspace kernel)
- AWS Lambda: Lambda isolation
- VM dedicada: Tu propio Docker daemon

### 2. "Sandboxing" tiene Muchas Definiciones

| Tecnología | Nivel de Aislamiento | Performance | Seguridad |
|------------|---------------------|-------------|-----------|
| Docker básico | Namespace isolation | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Docker + gVisor | Userspace kernel | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Firecracker | Hardware microVM | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Full VM | Complete isolation | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| WASM | Language-level | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

Para código LLM-generated, **mínimo recomendado: gVisor o Firecracker**.

### 3. El Costo Real Está en el Sandboxing, No en la Infra

**Costos comparados (1k ejecuciones/día):**
```
Railway API + DBs:     $15/mes  (15% del total)
E2B Sandboxing:        $84/mes  (85% del total)
─────────────────────────────────
Total:                 $99/mes
```

El cuello de botella económico es **el sandboxing seguro**, no databases ni APIs.

### 4. Modal es el Secreto Mejor Guardado para Python

Modal tiene **sandboxing Python nativo con gVisor** y $30/mes gratis perpetuo. Para workloads exclusivamente Python, es imbatible en costo y developer experience.

**Limitación**: Vendor lock-in extremo. Tu código queda atado a `@app.function()`.

### 5. Local Development es Subestimado

El 90% de los tutoriales saltan directo a cloud deployment. Pero:
- Docker Compose local = $0
- ngrok para demos = $0-8/mes
- Validación completa del concepto
- Migración posterior toma 1 día

**No hay razón para deployar en la nube hasta tener product-market fit.**

---

## 🚀 Decision Framework

### Usa este flowchart para decidir:

```
¿Necesitas uptime 24/7 YA?
│
├─ NO → Local + ngrok ($0/mes)
│       └─ Valida concepto, luego migra
│
└─ SÍ → ¿Cuántas ejecuciones/día?
        │
        ├─ <100 → Modal + DBs gratis ($0/mes)
        │          ⚠️ Alto vendor lock-in
        │
        ├─ 100-1000 → Railway + E2B ($13-99/mes)
        │              ✅ Balance simplicidad/costo
        │
        ├─ 1000-5000 → Modal completo ($20-125/mes)
        │               ✅ Más barato, pero lock-in
        │
        └─ >5000 → VM dedicada + Railway ($30-50/mes)
                    ⚠️ Más complejo, pero escalable
```

### Red Flags para Cada Opción

**Railway:**
- 🚨 Si necesitas Docker-in-Docker nativo
- 🚨 Si costos de E2B superan $200/mes
- 🚨 Si necesitas control total del runtime

**Render:**
- 🚨 Si presupuesto <$30/mes
- 🚨 Si necesitas usage-based pricing
- 🚨 Si workload es muy variable

**Fly.io:**
- 🚨 Si no estás cómodo con CLI tools
- 🚨 Si necesitas templates one-click
- 🚨 Si equipo no es técnico

**Modal:**
- 🚨 Si necesitas non-Python runtimes
- 🚨 Si portabilidad es crítica
- 🚨 Si necesitas long-running processes

**Local:**
- 🚨 Si necesitas uptime 24/7
- 🚨 Si tienes >10 usuarios concurrentes
- 🚨 Si laptop no puede estar siempre encendida

---

## 📝 Recomendación Final para NOVA MVP

### Stack Recomendado: Enfoque de 3 Fases

#### FASE 1 (Semanas 1-2): 🟢 START HERE
**Local + Docker Compose + ngrok**
- **Costo**: $0/mes
- **Objetivo**: Validar concepto, desarrollar features, demos early
- **Sandboxing**: Docker-in-Docker local (después migrar a E2B)
- **Timeline**: 2 semanas para MVP funcional

```bash
# Setup inicial
docker-compose up -d
uvicorn main:app --reload

# Demos externos
ngrok http 8000 --domain=nova-demo.ngrok.io
```

#### FASE 2 (Semana 3): 🟡 CLOUD DEPLOYMENT
**Railway + E2B**
- **Costo**: $13/mes (100 exec/día) → $99/mes (1k exec/día)
- **Objetivo**: Uptime 24/7, primeros usuarios reales
- **Migration time**: 1 día desde local
- **Sandboxing**: Cambiar de Docker a E2B API

```python
# Cambio mínimo en código
# Before:
sandbox = DockerSandbox()

# After:
sandbox = E2BSandbox(api_key=os.getenv("E2B_API_KEY"))
```

#### FASE 3 (Mes 2-3): 🔴 OPTIMIZATION
**Railway + VM Dedicada (Hetzner)**
- **Costo**: $30-50/mes (hasta 20k exec/día)
- **Objetivo**: Control total, costos optimizados
- **Cuándo**: Cuando E2B cueste >$200/mes
- **Sandboxing**: Docker + gVisor en VM propia

### Por qué este approach

✅ **Cero fricción inicial**: Empiezas codificando inmediatamente
✅ **Validación real**: Docker-in-Docker funciona local sin hacks
✅ **Costo mínimo**: $0 hasta tener tracción
✅ **Path claro a producción**: Railway + E2B es deployment de 1 día
✅ **Escalabilidad**: Ruta de migración a VM propia cuando justifique
✅ **Portabilidad**: Docker Compose funciona en cualquier cloud después

---

## 📚 Referencias y Recursos

### Documentación Oficial
- [Railway Docs](https://docs.railway.com/)
- [Render Docs](https://render.com/docs)
- [Fly.io Docs](https://fly.io/docs/)
- [Modal Docs](https://modal.com/docs)
- [E2B Docs](https://e2b.dev/docs)

### Ejemplos de Stack Completo
- [Railway Django+Celery+Redis Template](https://railway.com/template/NBR_V3)
- [Render FastAPI Deployment](https://docs.render.com/deploy-fastapi)
- [Fly.io Python Guide](https://fly.io/docs/languages-and-frameworks/python/)
- [Modal Safe Code Execution Example](https://modal.com/docs/examples/safe_code_execution)

### Sandboxing Deep Dives
- [Firecracker vs gVisor vs Kata Containers](https://fly.io/blog/sandboxing-and-workload-isolation/)
- [Running Untrusted Code Safely (AWS Blog)](https://aws.amazon.com/blogs/compute/sandboxing-with-aws-lambda/)
- [E2B Architecture](https://e2b.dev/docs/architecture)
- [Modal Sandbox Implementation](https://modal.com/docs/guide/sandbox)

### Pricing Calculators
- [Railway Pricing Calculator](https://railway.com/pricing)
- [Fly.io Pricing Calculator](https://fly.io/calculator)
- [Modal Pricing](https://modal.com/pricing)
- [E2B Pricing](https://e2b.dev/pricing)

### Community Discussions
- [Railway Help Station - Docker-in-Docker](https://station.railway.com/feedback/docker-in-docker-d07c4730)
- [Fly.io Forum - Sandboxing](https://community.fly.io/t/on-demand-docker-container-spinup-for-safe-user-code-execution/11361)
- [HN: E2B Discussion](https://news.ycombinator.com/item?id=40159630)

---

## ✅ Next Steps Inmediatos

1. **Esta Semana**: Setup Docker Compose local con todo el stack
2. **Próxima Semana**: Implementar workflow de facturas con Docker sandboxing
3. **Semana 3**: Si validado, deploy a Railway + cambiar a E2B
4. **Mes 2+**: Monitor costos, considerar VM propia si >$200/mes

---

**Última actualización**: 2025-10-23
**Autor**: Análisis para Mario Ferrer / Proyecto NOVA
**Status**: ✅ Listo para decisión
