# Marito: Análisis de Costes y Competencia

**Fecha**: 2025-10-22
**Objetivo**: Determinar si Marito es viable económicamente y cómo se posiciona frente a competidores

---

## PARTE 1: ANÁLISIS DE COSTES

### 1.1 Costes de Marito (Operación)

#### **Infraestructura Base** (desarrollo/MVP)

```
OPCIÓN A: Desarrollo Local + Deploy Simple
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Desarrollo (tu máquina):
├─ Costo: €0
└─ Recursos: Tu laptop/PC

Deploy MVP (Railway/Render):
├─ Compute: €7-20/mes
├─ PostgreSQL: €7-15/mes
├─ Redis: €5-10/mes (Upstash free tier posible)
└─ Docker Registry: €0 (DockerHub free)

TOTAL MVP: €19-45/mes
```

#### **Costes Variables (por uso)**

```
LLM API Costs (CRÍTICO - el coste principal)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Escenario 1: Workflow con 5 pasos (ej: validar facturas)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SIN CACHÉ (primera vez):
    Razonador (planificar):
    - Prompt: ~1,000 tokens
    - Response: ~500 tokens
    - Costo (GPT-4): $0.015

    Code Generator × 5 pasos:
    - Cada paso: ~2,000 tokens input + 1,000 output
    - Costo por paso (Claude Sonnet): $0.012
    - Total 5 pasos: $0.060

    TOTAL POR WORKFLOW: ~$0.075 (€0.07)

CON CACHÉ 80% (después de 5-10 ejecuciones):
    Razonador: $0.015 (siempre necesario)
    Code Generator: $0.012 (solo 1 paso nuevo)
    4 pasos desde caché: $0

    TOTAL POR WORKFLOW: ~$0.027 (€0.025)

CON CACHÉ 95% (workflows maduros):
    Razonador: $0.015
    Code Generator: $0 (todo desde caché)

    TOTAL POR WORKFLOW: ~$0.015 (€0.014)
```

#### **Cálculo Real por Volumen**

```
CLIENTE TÍPICO: 1,000 workflows/mes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Mes 1 (sin caché):
    1,000 workflows × $0.075 = $75
    + Infra: $25
    TOTAL: $100/mes (€92/mes)

Mes 2-3 (caché creciendo):
    1,000 workflows × $0.040 = $40
    + Infra: $25
    TOTAL: $65/mes (€60/mes)

Mes 4+ (caché maduro 80-90%):
    1,000 workflows × $0.020 = $20
    + Infra: $25
    TOTAL: $45/mes (€41/mes)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COSTE ESTABILIZADO: ~€40-60/mes para 1,000 workflows/mes
```

---

### 1.2 Costes de Competidores

#### **n8n (Competidor Directo)**

```
n8n Cloud:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Starter: $20/mes
├─ 2,500 executions/mes
├─ Cada "step" = 1 execution
└─ Workflow de 5 pasos = 5 executions

Para 1,000 workflows × 5 pasos = 5,000 executions
→ Necesitas plan Pro: $50/mes (10,000 executions)

Si necesitas 10,000 workflows/mes:
→ $50/mes NO alcanza (solo 10k executions = 2k workflows)
→ Necesitas Enterprise ($200-500/mes estimado)

n8n Self-Hosted:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Software: Gratis (open-source)

Infraestructura:
├─ VPS/Cloud: $50-80/mes
├─ PostgreSQL managed: $25-80/mes
├─ Monitoring: $30-50/mes
├─ Backups: $20-30/mes
└─ SSL/Security: $10-20/mes

TOTAL Self-Hosted: $135-260/mes

PERO: Sin límite de executions
→ Puedes hacer 100,000 workflows/mes sin coste extra
```

#### **Make.com (ex-Integromat)**

```
Make Pricing:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Free: 1,000 operations/mes
Core: $9/mes → 10,000 operations
Pro: $16/mes → 10,000 operations (más features)
Teams: $29/mes → 10,000 operations

TRAMPA: "Operations" NO son workflows
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Cada acción = 1 operation:
- Leer email = 1 op
- Descargar PDF = 1 op
- Extraer datos = 1 op
- Validar = 1 op
- Guardar DB = 1 op

Workflow de 5 pasos = 5 operations

Para 1,000 workflows/mes:
→ 1,000 × 5 = 5,000 operations
→ Necesitas plan Core ($9/mes) ✓

Para 10,000 workflows/mes:
→ 10,000 × 5 = 50,000 operations
→ Necesitas $9/mes × 5 = $45/mes

ADVERTENCIA: Según reviews, Make consume operations
muy rápido → costes ocultos pueden ser 44-100x más
```

#### **Zapier**

```
Zapier Pricing (2025):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Free: 100 tasks/mes
Starter: $19.99/mes → 750 tasks
Pro: $49/mes → 2,000 tasks
Team: $69/mes → 50,000 tasks

Para 1,000 workflows × 5 pasos = 5,000 tasks
→ Necesitas plan Team: $69/mes

Para 10,000 workflows/mes = 50,000 tasks
→ $69/mes alcanza justo
→ Pero si necesitas más: $103/mes (100k tasks)

MÁS CARO que Make y n8n
```

---

### 1.3 Comparación de Costes REAL

```
CASO: Cliente con 1,000 workflows/mes (5 pasos cada uno)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌──────────────────┬──────────────┬─────────────┬──────────────┐
│   Plataforma     │  Mes 1       │  Mes 3      │  Mes 6+      │
├──────────────────┼──────────────┼─────────────┼──────────────┤
│ MARITO           │  €92         │  €60        │  €41         │
│ n8n Cloud        │  €46 ($50)   │  €46        │  €46         │
│ n8n Self-Hosted  │  €150-250    │  €150-250   │  €150-250    │
│ Make.com         │  €8 ($9)     │  €8         │  €8          │
│ Zapier           │  €64 ($69)   │  €64        │  €64         │
└──────────────────┴──────────────┴─────────────┴──────────────┘

CASO: Cliente con 10,000 workflows/mes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌──────────────────┬──────────────┬─────────────┬──────────────┐
│   Plataforma     │  Mes 1       │  Mes 3      │  Mes 6+      │
├──────────────────┼──────────────┼─────────────┼──────────────┤
│ MARITO           │  €750        │  €400       │  €200        │
│ n8n Cloud        │  €460+       │  €460+      │  €460+       │
│ n8n Self-Hosted  │  €150-250    │  €150-250   │  €150-250    │
│ Make.com         │  €41 ($45)   │  €41        │  €41         │
│ Zapier           │  €64 ($69)   │  €64        │  €64         │
└──────────────────┴──────────────┴─────────────┴──────────────┘
```

---

### 1.4 Análisis de Costes: ¿Es Marito Caro o Barato?

#### ✅ **MARITO ES MÁS BARATO QUE**:

```
1. Zapier (siempre)
   - Zapier: €64/mes (1k workflows)
   - Marito: €41/mes (maduro)
   - Ahorro: 36%

2. n8n Cloud (volúmenes altos)
   - n8n: €460+/mes (10k workflows)
   - Marito: €200/mes (maduro)
   - Ahorro: 57%

3. n8n Self-Hosted (volúmenes bajos)
   - n8n: €150-250/mes (infra fija)
   - Marito: €41/mes (1k workflows)
   - Ahorro: 73-84%
```

#### ⚠️ **MARITO ES MÁS CARO QUE**:

```
1. Make.com (SIEMPRE)
   - Make: €8/mes (1k workflows)
   - Marito: €41/mes (maduro)
   - Diferencia: 5x más caro

2. n8n Self-Hosted (volúmenes MUY altos)
   - n8n: €150-250/mes (sin límite workflows)
   - Marito: €750/mes (100k workflows sin caché)
   - Diferencia: 3-5x más caro
```

---

### 1.5 Factor Clave: CACHÉ

```
El caché es CRÍTICO para costes de Marito
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Workflow repetitivo (ej: facturas diarias):
    ↓
    Caché 90%+ después de 1-2 semanas
    ↓
    Coste LLM: ~€0.015 por workflow
    ↓
    COMPETITIVO con Make/n8n

Workflow muy variado (cada uno diferente):
    ↓
    Caché 20-30%
    ↓
    Coste LLM: ~€0.050 por workflow
    ↓
    MÁS CARO que Make/n8n

CONCLUSIÓN: Marito es económico para workflows
             REPETITIVOS, caro para workflows AD-HOC
```

---

## PARTE 2: COMPETIDORES

### 2.1 Competencia Directa (Automation Platforms)

```
CATEGORÍA A: No-Code Automation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Make.com (ex-Integromat)
   - Líder en Europa
   - Precio: €8-29/mes
   - Visual workflow builder
   - 1,000+ integraciones
   - ❌ NO genera código
   - ✅ Muy barato

2. n8n
   - Open-source
   - Precio: €0 (self-hosted) o €46+/mes (cloud)
   - Workflow automation
   - 400+ nodos
   - ❌ NO genera código (usa nodos pre-hechos)
   - ✅ Self-hosteable

3. Zapier
   - Líder USA
   - Precio: €64-103/mes (1k workflows)
   - 6,000+ apps
   - ❌ NO genera código
   - ❌ Caro

4. Pabbly Connect
   - Precio: €29.99/mes (unlimited tasks)
   - ❌ NO genera código
   - ✅ Flat-rate pricing

5. Integrately
   - Precio: €29.99/mes
   - 8M+ ready automations
   - ❌ NO genera código
   - ✅ Automation expert incluido
```

#### **Diferencia clave de Marito**:

```
Make/Zapier/n8n:
    Usuario configura workflow visualmente
    ↓
    Usa conectores pre-hechos
    ↓
    Si conector no existe → NO se puede hacer
    ↓
    ❌ Limitado a integraciones disponibles

MARITO:
    Usuario describe tarea en texto
    ↓
    Marito GENERA código Python
    ↓
    Si API existe → Marito la usa
    ↓
    ✅ CUALQUIER API/integración posible
```

---

### 2.2 Competencia Indirecta (AI Code Generation)

```
CATEGORÍA B: AI Code Assistants
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. GitHub Copilot
   - Precio: $10-19/mes por dev
   - Autocompletado de código
   - ❌ NO ejecuta código
   - ❌ NO orquesta workflows
   - Público: Developers

2. Cursor
   - Precio: $20/mes
   - AI-native IDE
   - ❌ NO ejecuta automáticamente
   - ❌ NO workflows
   - Público: Developers

3. Replit AI
   - Precio: $20/mes
   - Full-stack AI platform
   - ✅ Ejecuta código
   - ❌ NO workflows de negocio
   - Público: Developers

4. Amazon Q Developer
   - Precio: Free tier + enterprise
   - AWS-focused
   - ❌ Solo para AWS
   - Público: Cloud engineers

5. Continue (Open-source)
   - Precio: Gratis
   - IDE extension
   - ❌ NO ejecuta workflows
   - Público: Developers
```

#### **Diferencia clave de Marito**:

```
Copilot/Cursor/etc:
    Ayudan a DEVELOPERS a escribir código
    ↓
    Developer escribe, revisa, ejecuta manualmente
    ↓
    Público: Programadores

MARITO:
    Genera Y ejecuta código automáticamente
    ↓
    Usuario NO necesita saber programar
    ↓
    Público: No-technical users (empresas)
```

---

### 2.3 Competencia REAL (Closest Match)

```
CATEGORÍA C: AI Agents que generan código
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. MAISA AI ⭐⭐⭐ (COMPETIDOR MÁS CERCANO)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   - Precio: €50,000+ (enterprise)
   - Trabajadores digitales con KPU
   - ✅ Genera y ejecuta código
   - ✅ Chain-of-Work auditable
   - ✅ Anti-alucinación
   - Target: Enterprise (bancos, energía)

   VS MARITO:
   ├─ Maisa: €50k+/año
   ├─ Marito: €5-10k proyecto
   └─ Diferencia: 5-10x más barato

2. Lindy AI
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   - Precio: Free tier, Pro $5k tasks/mes
   - AI agents que automatizan acciones
   - ✅ AI-powered
   - ⚠️ Menos técnico que Marito
   - Target: SMB

3. Relevance AI
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   - Precio: $199-499/mes
   - AI agent builder
   - ✅ Workflows con AI
   - ❌ NO genera código custom
   - Target: Mid-market

4. Zapier Central (Beta 2025)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   - Precio: TBD (beta)
   - AI agents on Zapier platform
   - ⚠️ Todavía en beta
   - Target: Zapier users

5. OpenHands (Open-source)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   - Precio: Gratis (OSS)
   - AI coding assistant
   - ✅ Genera código
   - ❌ NO orquesta workflows de negocio
   - Target: Developers
```

---

### 2.4 Mapa de Posicionamiento

```
                    Alto Precio
                         │
                         │
              MAISA AI   │
                 ●       │
                         │
                         │         ● Zapier
                         │
────────────────────────┼────────────────────── Tech Skills Required
        MARITO ●        │      ● Make.com
                         │    ● n8n Cloud
      ● Lindy AI        │
                         │
   ● n8n Self-Hosted    │
                         │
                    Bajo Precio

Eje X: Tech Skills Required (izq = no-tech, der = developers)
Eje Y: Precio (abajo = barato, arriba = caro)
```

---

### 2.5 ¿Quién está haciendo lo mismo que Marito?

```
RESPUESTA: NADIE EXACTAMENTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Closest matches:

1. MAISA AI
   - Hace lo mismo (genera código, ejecuta, aprende)
   - PERO: Target enterprise (€50k+)
   - PERO: Plataforma cerrada
   - MARITO: Target SMB (€5-10k), código abierto cliente

2. n8n + AI nodes
   - Tiene nodos de AI (OpenAI, etc)
   - PERO: No genera código Python custom
   - PERO: Limitado a integraciones existentes
   - MARITO: Genera código para CUALQUIER API

3. Replit AI
   - Genera código, ejecuta
   - PERO: Target developers
   - PERO: No workflows de negocio
   - MARITO: Target no-technical, workflows empresariales

CONCLUSIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Marito está en un "sweet spot" NO cubierto:

    ✅ Genera código como Copilot/Replit
    ✅ Ejecuta workflows como n8n/Make
    ✅ Aprende como Maisa
    ✅ Precio SMB (no enterprise)
    ✅ Target no-technical users
```

---

## PARTE 3: VENTAJA COMPETITIVA DE MARITO

### 3.1 ¿Por qué elegir Marito sobre competidores?

```
VS Make.com/n8n/Zapier:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Make/n8n:
    Problema: "No hay integración para API X"
    Solución: Esperar a que la construyan o hacerlo custom
    Tiempo: Semanas/meses

MARITO:
    Problema: "No hay integración para API X"
    Solución: Marito genera código Python en minutos
    Tiempo: 5-10 minutos

VENTAJA: Flexibilidad infinita
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VS Maisa AI:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Maisa:
    Target: Enterprise (bancos, energía)
    Precio: €50,000+/año
    Time to market: 2-3 meses
    Onboarding: Complejo

MARITO:
    Target: SMB/Mid-market
    Precio: €5-10k proyecto
    Time to market: 2-4 semanas
    Onboarding: Simple

VENTAJA: Mismo concepto, precio accesible
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VS GitHub Copilot/Cursor:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Copilot:
    Target: Developers
    Usuario: Escribe código manualmente
    Ejecución: Manual
    Workflows: NO

MARITO:
    Target: No-technical users
    Usuario: Describe tarea en texto
    Ejecución: Automática
    Workflows: SÍ

VENTAJA: Automatización end-to-end sin programar
```

---

### 3.2 Casos donde Marito GANA

```
✅ Cliente necesita automatización custom
   - API que no está en Make/Zapier
   - Lógica de negocio específica
   - Integraciones propias

✅ Cliente quiere auditoría completa
   - Chain-of-Work para compliance
   - Trazabilidad de decisiones
   - Regulación estricta

✅ Cliente tiene workflows repetitivos
   - Mismo flujo cada día
   - Caché 90%+ → costes bajos
   - ROI alto

✅ Cliente es SMB/Mid-market
   - Presupuesto €5-15k (no €50k)
   - Necesita solución rápida
   - No tiene equipo técnico grande
```

### 3.3 Casos donde Marito PIERDE

```
❌ Cliente necesita workflows muy simples
   - "Cuando recibo email, guardar en Sheets"
   - Make.com: €8/mes
   - Marito: €41/mes (overkill)
   - RECOMENDACIÓN: Usa Make.com

❌ Cliente tiene volumen ENORME y muy variado
   - 100,000 workflows/mes todos diferentes
   - Caché 20% → Marito: €3,000/mes
   - n8n self-hosted: €250/mes (sin límite)
   - RECOMENDACIÓN: Usa n8n self-hosted

❌ Cliente tiene developers in-house
   - Pueden programar workflows custom
   - Costo: €0 (su tiempo)
   - Marito: €41+/mes
   - RECOMENDACIÓN: Programa internamente

❌ Cliente necesita UI visual drag-and-drop
   - No-technical user que prefiere UI
   - Marito: Configuración por JSON/texto
   - Make.com: Drag-and-drop visual
   - RECOMENDACIÓN: Usa Make.com
```

---

## PARTE 4: ESTRATEGIA DE PRICING PARA MARITO

### 4.1 Modelo de Negocio Propuesto

```
OPCIÓN 1: Modelo Proyecto (Track 1 - Agencia)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Cobrar por implementación:
    ├─ Setup inicial: €2,000-5,000
    │   └─ Configuración de workflow
    │   └─ Credenciales
    │   └─ Testing y ajustes
    │
    ├─ Mensualidad: €50-200/mes
    │   └─ Hosting + LLM costs
    │   └─ Mantenimiento
    │   └─ Soporte
    │
    └─ Adicionales: €500-1,500 por workflow nuevo

Ejemplo cliente factura:
    ├─ Setup: €3,000
    ├─ Mensual: €100/mes (incluye 1k workflows)
    └─ Total año 1: €4,200

VENTAJA: Ingresos predecibles, margen alto
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPCIÓN 2: Modelo SaaS (Track 2 - Producto)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Pricing por uso:
    ├─ Starter: €49/mes
    │   └─ 1,000 workflows/mes
    │   └─ 3 workflows configurados
    │   └─ Email support
    │
    ├─ Pro: €149/mes
    │   └─ 5,000 workflows/mes
    │   └─ 10 workflows configurados
    │   └─ Priority support
    │
    └─ Enterprise: Custom
        └─ Unlimited workflows
        └─ Dedicated instance
        └─ SLA garantizado

VENTAJA: Escalable, recurring revenue
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPCIÓN 3: Modelo Híbrido (RECOMENDADO)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Track 1 (primeros clientes):
    ├─ Cobrar por proyecto (€3-8k)
    ├─ Usar Marito internamente
    ├─ Aprender qué funciona
    └─ Construir library de workflows

Track 2 (después de 6-12 meses):
    ├─ Lanzar SaaS (€49-149/mes)
    ├─ Workflows pre-construidos
    ├─ Self-service onboarding
    └─ Escalar con producto
```

---

### 4.2 Cálculo de Margen

```
CLIENTE TÍPICO: €3,000 setup + €100/mes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Costos (mes 1):
    ├─ Tu tiempo (setup): 20 horas × €50/h = €1,000
    ├─ Infra: €25
    ├─ LLM (sin caché): €75
    └─ TOTAL COSTOS: €1,100

Ingresos (mes 1):
    ├─ Setup: €3,000
    ├─ Mensualidad: €100
    └─ TOTAL INGRESOS: €3,100

MARGEN MES 1: €2,000 (65%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Costos (mes 3+, caché maduro):
    ├─ Tu tiempo: 0 horas (automático)
    ├─ Infra: €25
    ├─ LLM (caché 80%): €25
    └─ TOTAL COSTOS: €50

Ingresos (mes 3+):
    └─ Mensualidad: €100

MARGEN MES 3+: €50 (50%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CON 10 CLIENTES (año 1):
    ├─ Setup: 10 × €3,000 = €30,000
    ├─ Mensualidades: 10 × €100 × 12 = €12,000
    ├─ INGRESOS TOTALES: €42,000
    │
    ├─ Costos setup: €11,000
    ├─ Costos operación: €6,000
    ├─ COSTOS TOTALES: €17,000
    │
    └─ BENEFICIO: €25,000 (60% margen)
```

---

## PARTE 5: CONCLUSIONES Y RECOMENDACIONES

### 5.1 ¿Es Marito Económicamente Viable?

```
✅ SÍ, PERO con condiciones
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VIABLE SI:
    ✅ Workflows repetitivos (caché alto)
    ✅ Target SMB/Mid-market (€5-15k budget)
    ✅ Casos custom (APIs no en Make/Zapier)
    ✅ Auditoría necesaria (compliance)

NO VIABLE SI:
    ❌ Workflows muy simples (mejor Make €8/mes)
    ❌ Volumen enorme variado (mejor n8n self-hosted)
    ❌ Cliente tiene developers (mejor custom code)
    ❌ Presupuesto muy bajo (< €1,000)
```

### 5.2 Posicionamiento vs Competencia

```
MARITO = "Maisa para SMBs"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Características:
    ✅ Genera código on-the-fly (como Maisa)
    ✅ Chain-of-Work auditable (como Maisa)
    ✅ Precio accesible (5-10x más barato que Maisa)
    ✅ Target SMB (vs Enterprise de Maisa)

Diferenciación:
    VS Make/Zapier/n8n:
        → Flexibilidad infinita (genera código custom)
        → Auditoría enterprise (Chain-of-Work)

    VS Maisa:
        → Mismo concepto, precio SMB
        → Time to market rápido (2-4 semanas vs 2-3 meses)

    VS Copilot/Cursor:
        → No-code para usuarios finales
        → Workflows automáticos end-to-end
```

### 5.3 Estrategia Recomendada

```
FASE 1 (Meses 1-6): Track 1 - Agencia
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Objetivo: Validar mercado + ingresos
    ├─ 5-10 clientes a €3-8k cada uno
    ├─ Usar Marito internamente
    ├─ Aprender qué workflows son más demandados
    └─ Construir library de código exitoso

Target:
    ├─ Empresas 10-100 empleados
    ├─ Procesos manuales repetitivos
    ├─ Presupuesto €5-15k
    └─ Necesitan custom (no hay en Make/Zapier)

FASE 2 (Meses 7-12): Producto + Agencia
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Objetivo: Escalar con SaaS
    ├─ Lanzar self-service (€49-149/mes)
    ├─ Workflows pre-construidos (basados en Track 1)
    ├─ Mantener agencia para casos custom
    └─ 50/50 ingresos (proyecto + SaaS)

FASE 3 (Año 2+): Producto Principal
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Objetivo: SaaS escalable
    ├─ 80% ingresos de SaaS
    ├─ 20% ingresos de enterprise custom
    ├─ 100+ clientes SaaS
    └─ ARR €100k+
```

### 5.4 Riesgos y Mitigación

```
RIESGO 1: Costes LLM muy altos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Escenario: Cliente con workflows muy variados
→ Caché bajo (20-30%)
→ Costes LLM altos (€0.05-0.07 por workflow)

Mitigación:
    ├─ Límite de workflows/mes en planes
    ├─ Cobrar extra por workflows muy variados
    ├─ Educar cliente sobre beneficio de workflows repetitivos
    └─ Ofrecer "design optimization" (consolidar workflows)

RIESGO 2: Make.com/n8n mejoran con AI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Escenario: Make añade generación de código con AI
→ Marito pierde ventaja competitiva

Mitigación:
    ├─ Construir moat con caché/aprendizaje
    ├─ Chain-of-Work como diferenciador (compliance)
    ├─ Velocidad de iteración (somos más ágiles)
    └─ Nicho SMB (ellos van a enterprise)

RIESGO 3: Maisa baja precios
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Escenario: Maisa lanza plan SMB a €10-20k
→ Compite directamente con Marito

Mitigación:
    ├─ Maisa es startup (tardará años en bajar mercado)
    ├─ Nosotros somos más ágiles (2 semanas vs 2 meses)
    ├─ Código abierto cliente (vs platform lock-in)
    └─ Target geográfico (España/LATAM vs global)
```

---

## RESUMEN EJECUTIVO FINAL

### Costes:
```
Marito (1,000 workflows/mes):
    Mes 1: €92
    Mes 6+: €41 (con caché maduro)

Competencia:
    Make.com: €8/mes (MÁS BARATO)
    n8n Cloud: €46/mes (similar)
    Zapier: €64/mes (MÁS CARO)
    Maisa: €4,000+/mes (MUY CARO)

CONCLUSIÓN: Marito es competitivo en precio
            para workflows REPETITIVOS
```

### Competidores:
```
Directos (automation):
    - Make.com, n8n, Zapier, Pabbly
    VENTAJA MARITO: Genera código custom

Similares (AI + automation):
    - Maisa AI (enterprise, €50k+)
    - Lindy AI (SMB, menos técnico)
    VENTAJA MARITO: Sweet spot precio/features

Indirectos (code generation):
    - Copilot, Cursor, Replit
    VENTAJA MARITO: Workflows end-to-end no-code

CONCLUSIÓN: Marito cubre nicho NO cubierto
            (AI code gen + automation + SMB pricing)
```

### Viabilidad:
```
✅ VIABLE económicamente
✅ NICHO claro (SMB custom automation)
✅ COMPETENCIA identificada
✅ DIFERENCIACIÓN clara
✅ MARGEN atractivo (50-65%)

⚠️ CONDICIÓN: Workflows repetitivos (caché alto)
⚠️ RIESGO: Competencia mejora con AI
```

---

**¿Procedemos con documento de arquitectura completo?**
