# Resumen Ejecutivo: Estrategia de Deployment para NOVA

**Fecha**: 2025-10-23
**Para**: Mario Ferrer
**De**: Análisis de Deployment Platforms

---

## TL;DR - Recomendación

**NO deployar a cloud todavía. Empezar 100% local.**

**Stack recomendado para las próximas 2 semanas:**
- Docker Compose local con todo el stack
- Docker-in-Docker para sandboxing (funciona sin restricciones)
- ngrok para demos externos (gratis o $8/mes)
- **Costo total: $0**

**Después de validar el MVP (Semana 3):**
- Migrar a Railway + E2B en 1 día
- Costo: $13-99/mes según uso

---

## El Problema que Descubrimos

### Railway, Render y Fly.io NO soportan Docker-in-Docker

Tu arquitectura inicial con Docker para sandboxing **no puede deployarse directamente** en ninguna PaaS moderna por razones de seguridad.

**Opciones reales:**
1. ✅ **E2B Cloud**: Sandboxing externo con Firecracker microVMs (~$126/mes con 1k ejecuciones/día)
2. ✅ **Modal.com**: Python serverless con gVisor nativo ($30/mes gratis)
3. ✅ **VM Dedicada**: Hetzner/DigitalOcean con tu propio Docker ($5-10/mes)
4. ✅ **Local Development**: Docker-in-Docker funciona perfecto ($0)

---

## Por Qué Empezar Local (No Cloud)

### Ventajas de Local + Docker Compose

1. **Empiezas YA**: Sin configurar cloud providers, zero friction
2. **$0 de costo**: No gastas hasta validar el concepto
3. **Docker-in-Docker funciona**: Sin workarounds complicados
4. **Iteración ultra-rápida**: Cambios instantáneos, no deploys
5. **Demos viables**: ngrok te da HTTPS público para mostrar a usuarios
6. **Mismo código**: Docker Compose local = producción después

### Desventajas (todas manejables)

- ❌ Tu laptop debe estar encendida para demos
  - ✅ **Solución**: ngrok + laptop encendida solo para demos puntuales
- ❌ No uptime 24/7
  - ✅ **Solución**: No necesitas uptime hasta tener usuarios reales (Semana 3+)

---

## Comparativa de Plataformas (Cuando Migres)

### Railway.app ⭐ RECOMENDADO

**Pros:**
- Setup ultra-rápido (1 hora)
- Templates preconstruidos Django+Celery+Redis+PostgreSQL
- PostgreSQL y Redis managed
- Developer experience excelente
- $5/mes para empezar

**Contras:**
- NO soporta Docker-in-Docker
- Requiere E2B para sandboxing (~$84/mes con 1k exec/día)

**Costo total con 1k ejecuciones/día**: $99/mes

### Render.com

**Pros:**
- Muy estable
- Pricing predecible

**Contras:**
- Más caro ($31/mes mínimo)
- Menos features que Railway
- También necesita E2B

**Costo total**: $115/mes

### Fly.io

**Pros:**
- Máxima flexibilidad
- Firecracker VMs
- Pricing granular

**Contras:**
- Más técnico (CLI-heavy)
- Setup más complejo (4 horas)
- También necesita E2B

**Costo total**: $106/mes

### Modal.com (Alternativa Interesante)

**Pros:**
- **Sandboxing NATIVO** (gVisor incluido)
- $30/mes gratis perpetuo
- Python-first
- Developer experience excelente

**Contras:**
- No tiene databases (necesitas externos)
- Vendor lock-in muy alto
- Solo funciona bien para Python

**Costo total con DBs externos**: $20/mes (mucho más barato)

---

## Estrategia Recomendada: 3 Fases

### FASE 1 (Semanas 1-2): Local Development 🟢 AHORA

**Stack:**
```yaml
# docker-compose.yml
services:
  api:          # FastAPI
  worker:       # Celery
  postgres:     # PostgreSQL
  redis:        # Redis
  sandbox:      # Docker-in-Docker ✅
```

**Deployment:**
```bash
docker-compose up -d
ngrok http 8000  # Para demos
```

**Costo:** $0/mes

**Objetivo:** MVP funcional que procese facturas

---

### FASE 2 (Semana 3+): Railway + E2B 🟡 DESPUÉS

**Cuándo migrar:**
- Necesitas uptime 24/7
- 10+ usuarios quieren acceso
- Demos constantes a clientes

**Setup:**
```bash
railway login
railway init
railway up
# Cambiar DockerSandbox → E2BSandbox
```

**Migration time:** 1 día

**Costo:**
- 100 exec/día: $13/mes
- 1k exec/día: $99/mes
- 5k exec/día: $450/mes 🚨

---

### FASE 3 (Mes 2+): VM Dedicada 🔴 OPTIMIZACIÓN

**Cuándo migrar:**
- Costos de E2B superan $200/mes
- Necesitas control total
- >5k ejecuciones/día

**Setup:**
- Railway para API + databases
- Hetzner CPX21 (€5.83/mes) para sandboxing
- Docker + gVisor en VM propia

**Costo fijo:** $30-50/mes independiente del volumen

---

## Análisis de Costos Real

### Escenario MVP (100 ejecuciones/día)

| Opción | Costo |
|--------|-------|
| Local + ngrok | $0-8/mes ⭐ |
| Railway + E2B | $13/mes |
| Modal + DBs externos | $0/mes 🎉 |

**Recomendación:** Empezar local por $0

### Escenario Tracción (1,000 ejecuciones/día)

| Opción | Costo |
|--------|-------|
| Railway + E2B | $99/mes |
| Modal completo | $20/mes ⭐ |
| Fly.io + E2B | $106/mes |

**Recomendación:** Modal si aceptas vendor lock-in, Railway si no

### Escenario Crecimiento (5,000 ejecuciones/día)

| Opción | Costo |
|--------|-------|
| Railway + E2B | $450/mes 💸 |
| Modal completo | $125/mes |
| **VM Dedicada** | **$30/mes ⭐** |

**Recomendación:** Migrar a VM propia a este volumen

---

## Lo que Más Importa Saber

### 1. El Cuello de Botella es el Sandboxing, No la Infra

El 85% del costo es el sandboxing seguro (E2B), no las APIs ni databases.

**Ejemplo con 1k ejecuciones/día:**
```
Railway (API + DBs):   $15/mes  (15%)
E2B (sandboxing):      $84/mes  (85%)
──────────────────────────────
Total:                 $99/mes
```

### 2. Modal es el Secreto Mejor Guardado

Modal tiene sandboxing Python nativo (gVisor) + $30/mes gratis perpetuo. Es la opción más barata técnicamente, pero con vendor lock-in extremo.

Si estás OK con lock-in y 100% Python: **Modal puede ser $0-20/mes en vez de $99/mes**.

### 3. No Hay Razón para Deployar Cloud Día 1

El 90% de los tutoriales te dicen "deploy a Heroku/Railway inmediatamente". Pero:
- Docker Compose local es gratis
- Mismo código que en producción
- ngrok te da HTTPS público
- Validas el concepto sin gastar

**Deploy a cloud cuando NECESITES uptime 24/7, no antes.**

### 4. La Migración Local → Cloud es Trivial

Si usas Docker Compose bien, migrar a Railway/Render/Fly toma **1 día**, no semanas.

```bash
# Literalmente esto:
railway login
railway init
railway up
```

### 5. Railway NO Soporta DinD (Pero Eso Está OK)

Railway explícitamente dice "no Docker-in-Docker por seguridad". Pero hay soluciones probadas:
- E2B (lo usan Fortune 500)
- Modal (sandboxing nativo)
- VM separada (máximo control)

Tu arquitectura sigue siendo viable, solo cambia la implementación del sandbox.

---

## Decisión Recomendada

### Para las Próximas 2 Semanas

**Stack: Docker Compose Local + ngrok**

```bash
# Hoy
git clone <repo>
docker-compose up -d

# Mañana
# Implementar MVP hardcoded

# Próxima semana
# Integrar GPT-4

# Semana 2
# Testing con facturas reales

# Demos externos (cuando necesites)
ngrok http 8000
```

**Costo:** $0

**Objetivo:** MVP funcional con 10+ facturas procesadas

### Después de Validar (Semana 3)

**Stack: Railway + E2B**

**Cuándo:**
- Necesitas uptime 24/7
- 10+ usuarios quieren acceso constante
- Inversores piden ver producto en la nube

**Migration:**
```bash
railway login
railway init
# Cambiar DockerSandbox → E2BSandbox
railway up
```

**Migration time:** 1 día

**Costo inicial:** $13/mes → crece con uso

---

## Red Flags a Evitar

### ❌ NO hagas esto

1. **NO deploys a cloud en Día 1**: Es fricción innecesaria
2. **NO asumas que Railway = Docker-in-Docker**: No funciona
3. **NO ignores los costos de sandboxing**: Son el 85% del total
4. **NO te cases con una plataforma**: Portabilidad es clave

### ✅ SÍ haz esto

1. **SÍ empieza local**: Valida concepto gratis
2. **SÍ usa abstracción para sandbox**: `SandboxExecutor` interface
3. **SÍ monitorea costos**: E2B puede escalar rápido
4. **SÍ ten plan de migración**: Local → Railway → VM

---

## Preguntas Frecuentes

### ¿Por qué no usar Railway desde día 1?

Porque:
1. No necesitas uptime 24/7 para desarrollar
2. Railway no soporta DinD (necesitas E2B = $84+/mes extra)
3. Local es más rápido para iterar
4. Puedes migrar en 1 día cuando esté listo

### ¿E2B es caro?

Depende:
- 100 exec/día (30s): $8/mes ✅
- 1k exec/día (30s): $84/mes ⚠️
- 5k exec/día (30s): $420/mes 🚨

A partir de 5k/día, VM propia es más barato.

### ¿Modal vs Railway?

**Modal** si:
- Aceptas vendor lock-in
- Solo necesitas Python
- Quieres el costo más bajo

**Railway** si:
- Quieres portabilidad
- Necesitas control total
- Tienes presupuesto para E2B

### ¿Cuándo usar VM dedicada?

Cuando:
- Costos de E2B > $200/mes
- Necesitas features custom
- Compliance requiere control de infra
- >5k ejecuciones/día

---

## Documentación Completa

Este es un resumen. Para el análisis completo:

- **Comparativa Detallada**: [deployment-plataformas-comparativa.md](deployment-plataformas-comparativa.md)
- **ADR de Deployment**: [../proyecto/DECISIONES/004-deployment-strategy.md](../../proyecto/DECISIONES/004-deployment-strategy.md)
- **ADR de Sandboxing**: [../proyecto/DECISIONES/002-sandboxing.md](../../proyecto/DECISIONES/002-sandboxing.md)

---

## Próximos Pasos (Esta Semana)

1. **Hoy**: Crear `docker-compose.yml` con todos los servicios
2. **Mañana**: Setup sandbox executor con Docker
3. **Esta semana**: Implementar workflow de facturas hardcoded
4. **Próxima semana**: Integrar GPT-4 para generación dinámica

**NO te preocupes por cloud deployment todavía. Foco en MVP funcional local.**

---

**Última actualización**: 2025-10-23
