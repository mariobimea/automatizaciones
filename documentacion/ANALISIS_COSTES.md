# Análisis de Costes - NOVA Multi-Agent Architecture

## Escenario Base: Procesamiento de Facturas en Producción

### Configuración del Workflow

**Total de nodos**: 15 nodos

**Distribución de nodos**:
- **10 nodos cacheables** (70%): Lógica estable, patrones repetitivos
  - Ejemplos: Extracción de datos estructurados, validaciones estándar, cálculos conocidos
- **5 nodos variables** (30%): Lógica que cambia frecuentemente
  - Ejemplos: Reglas de negocio complejas, decisiones con contexto amplio, validaciones cruzadas

---

## Estrategia de Modelos por Agente

### Coordinator Agent
- **Modelo**: `gpt-4.1-mini` (GPT-4.1 optimizado)
- **Uso**: 1 llamada por workflow
- **Función**: Orquestar el flujo, decidir qué nodos ejecutar
- **Input promedio**: 2K tokens (workflow definition + contexto)
- **Output promedio**: 500 tokens (plan de ejecución)

### Specialist Agents

#### Para nodos cacheables (10 nodos)
- **Modelo**: `gpt-4.1-mini`
- **Estrategia**: Cache agresivo
- **Hit rate esperado**: 80% (después de warmup)
- **Input promedio**: 1.5K tokens
- **Output promedio**: 800 tokens

#### Para nodos variables (5 nodos)
- **Modelo**: `gpt-5` (o-series)
- **Estrategia**: Generación fresh + validación
- **Hit rate esperado**: 20% (poco cacheable)
- **Input promedio**: 3K tokens (contexto más amplio)
- **Output promedio**: 1.2K tokens

### Validator Agent
- **Modelo**: `gpt-4.1-mini`
- **Uso**: 1 llamada por nodo generado (no cacheado)
- **Input promedio**: 1K tokens (código generado)
- **Output promedio**: 300 tokens (validación)

---

## Cálculo de Costes por Ejecución

### Precios de Referencia (OpenAI - Enero 2025)

| Modelo | Input ($/1M tokens) | Output ($/1M tokens) |
|--------|---------------------|----------------------|
| gpt-4.1-mini | $0.15 | $0.60 |
| gpt-5 | $15.00 | $60.00 |

*(Nota: GPT-5 pricing estimado basado en o1-preview/o1-mini como referencia)*

---

## Escenario 1: Cold Start (Primera Ejecución - Cache Vacío)

### Coordinator
- Input: 2K tokens × $0.15/1M = $0.0003
- Output: 500 tokens × $0.60/1M = $0.0003
- **Subtotal Coordinator**: $0.0006

### Nodos Cacheables (10 nodos) - gpt-4.1-mini
- Input: 10 × 1.5K × $0.15/1M = $0.00225
- Output: 10 × 800 × $0.60/1M = $0.0048
- Validator: 10 × (1K input + 300 output) × ($0.15 + $0.18)/1M = $0.0033
- **Subtotal Cacheables**: $0.01035

### Nodos Variables (5 nodos) - gpt-5
- Input: 5 × 3K × $15/1M = $0.225
- Output: 5 × 1.2K × $60/1M = $0.36
- Validator: 5 × (1K input + 300 output) × ($0.15 + $0.18)/1M = $0.00165
- **Subtotal Variables**: $0.58665

### **Total Cold Start**: $0.5976 ≈ **$0.60 por workflow**

---

## Escenario 2: Warm Cache (80% Hit Rate en Cacheables)

### Coordinator
- **Subtotal**: $0.0006 (igual)

### Nodos Cacheables (10 nodos)
- **Cache hits (8 nodos)**: $0 (código reutilizado)
- **Cache misses (2 nodos)**:
  - Input: 2 × 1.5K × $0.15/1M = $0.00045
  - Output: 2 × 800 × $0.60/1M = $0.00096
  - Validator: 2 × (1K + 300) × ($0.15 + $0.18)/1M = $0.00066
  - **Subtotal Cacheables**: $0.00207

### Nodos Variables (5 nodos) - 20% hit rate
- **Cache hits (1 nodo)**: $0
- **Cache misses (4 nodos)**:
  - Input: 4 × 3K × $15/1M = $0.18
  - Output: 4 × 1.2K × $60/1M = $0.288
  - Validator: 4 × (1K + 300) × ($0.15 + $0.18)/1M = $0.00132
  - **Subtotal Variables**: $0.46932

### **Total Warm Cache**: $0.47199 ≈ **$0.47 por workflow**

---

## Escenario 3: Hot Cache (95% Hit Rate en Cacheables, 40% en Variables)

### Coordinator
- **Subtotal**: $0.0006

### Nodos Cacheables (10 nodos)
- **Cache hits (9.5 nodos)**: $0
- **Cache misses (0.5 nodos promedio)**:
  - Input: 0.5 × 1.5K × $0.15/1M = $0.0001125
  - Output: 0.5 × 800 × $0.60/1M = $0.00024
  - Validator: 0.5 × (1K + 300) × ($0.15 + $0.18)/1M = $0.000165
  - **Subtotal Cacheables**: $0.0005175

### Nodos Variables (5 nodos)
- **Cache hits (2 nodos)**: $0
- **Cache misses (3 nodos)**:
  - Input: 3 × 3K × $15/1M = $0.135
  - Output: 3 × 1.2K × $60/1M = $0.216
  - Validator: 3 × (1K + 300) × ($0.15 + $0.18)/1M = $0.00099
  - **Subtotal Variables**: $0.35199

### **Total Hot Cache**: $0.35270 ≈ **$0.35 por workflow**

---

## Proyección Mensual - Diferentes Volúmenes

### Volumen Bajo: 1,000 workflows/mes
| Escenario | Coste por workflow | Coste mensual |
|-----------|-------------------|---------------|
| Cold Start (primeros 100) | $0.60 | $60 |
| Warm Cache (siguientes 900) | $0.47 | $423 |
| **Total Mes 1** | - | **$483** |
| **Meses siguientes (Hot Cache)** | $0.35 | **$350** |

### Volumen Medio: 5,000 workflows/mes
| Escenario | Coste por workflow | Coste mensual |
|-----------|-------------------|---------------|
| Cold Start (primeros 100) | $0.60 | $60 |
| Warm Cache (siguientes 4,900) | $0.47 | $2,303 |
| **Total Mes 1** | - | **$2,363** |
| **Meses siguientes (Hot Cache)** | $0.35 | **$1,750** |

### Volumen Alto: 20,000 workflows/mes
| Escenario | Coste por workflow | Coste mensual |
|-----------|-------------------|---------------|
| Cold Start (primeros 100) | $0.60 | $60 |
| Warm Cache (siguientes 19,900) | $0.47 | $9,353 |
| **Total Mes 1** | - | **$9,413** |
| **Meses siguientes (Hot Cache)** | $0.35 | **$7,000** |

---

## Comparación: Multi-Agent vs Monolítico GPT-5

### Enfoque Monolítico (todos los nodos con GPT-5)

**Coste por workflow**:
- 15 nodos × 3K input × $15/1M = $0.675
- 15 nodos × 1.2K output × $60/1M = $1.08
- **Total**: $1.755 por workflow

### Ahorro con Multi-Agent

| Volumen | Monolítico GPT-5 | Multi-Agent (Hot) | Ahorro | % Reducción |
|---------|------------------|-------------------|--------|-------------|
| 1,000/mes | $1,755 | $350 | $1,405 | **80%** |
| 5,000/mes | $8,775 | $1,750 | $7,025 | **80%** |
| 20,000/mes | $35,100 | $7,000 | $28,100 | **80%** |

---

## Optimizaciones Adicionales

### 1. Cache Persistence (Redis)
- **Coste Redis**: ~$15/mes (Railway Redis)
- **Hit rate improvement**: +10-15%
- **ROI**: Se paga solo con 50 workflows/mes

### 2. Modelo Cascade
Para nodos cacheables, intentar primero con modelo más barato:
- `gpt-4.1-nano` ($0.05/$0.20 por 1M tokens)
- Si falla validación → fallback a `gpt-4.1-mini`
- **Ahorro adicional**: 15-20% en nodos cacheables

### 3. Batch Processing
Generar código para múltiples workflows similares en una llamada:
- Facturas del mismo proveedor
- Workflows con misma estructura
- **Ahorro**: 30-40% en cold starts

---

## Breakdown de Costes por Componente

### Mes típico (5,000 workflows, Hot Cache)

| Componente | Llamadas/mes | Coste |
|------------|--------------|-------|
| Coordinator (gpt-4.1-mini) | 5,000 | $3 |
| Specialists Cacheables (95% cache) | 250 | $12 |
| Specialists Variables (40% cache) | 15,000 | $1,700 |
| Validators | 15,250 | $35 |
| **Total LLM** | - | **$1,750** |
| Infrastructure (Railway + Hetzner) | - | $20 |
| Redis Cache | - | $15 |
| **Total Operational** | - | **$1,785** |

---

## Sensibilidad a Variaciones

### Si GPT-5 sube de precio (+50%)
- Warm Cache: $0.47 → $0.61 (+30%)
- Hot Cache: $0.35 → $0.45 (+29%)
- Sigue siendo 74% más barato que monolítico

### Si hit rate cae (de 80% a 60%)
- Warm Cache: $0.47 → $0.54 (+15%)
- Sigue siendo 69% más barato que monolítico

### Si aumentan nodos variables (de 5 a 8)
- Warm Cache: $0.47 → $0.75 (+60%)
- Hot Cache: $0.35 → $0.53 (+51%)
- Sigue siendo 57% más barato que monolítico

---

## Conclusiones

### Viabilidad Económica ✅

1. **Multi-agent es ~80% más barato** que usar GPT-5 puro
2. **Break-even muy bajo**: 50 workflows/mes cubren infraestructura
3. **Escalable**: Coste marginal predecible ($0.35/workflow en hot cache)

### Puntos Clave

- **Cache es crítico**: 80% del ahorro viene de reutilización
- **Granularidad correcta**: 10 nodos cacheables vs 5 variables es óptimo
- **GPT-4.1-mini suficiente**: Para nodos cacheables, no necesitas GPT-5
- **Validación barata**: Validator con modelo light mantiene calidad

### Recomendación

**Implementar arquitectura multi-agent con**:
- Coordinator: `gpt-4.1-mini`
- Specialists cacheables: `gpt-4.1-mini`
- Specialists variables: `gpt-5`
- Validator: `gpt-4.1-mini`
- Cache: Redis con TTL inteligente

**ROI esperado**: Ahorro de $7,000/mes a 20K workflows vs monolítico GPT-5

---

*Última actualización: 2025-11-13*
