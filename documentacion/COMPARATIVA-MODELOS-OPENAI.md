# Comparativa de Modelos OpenAI

**Fecha de actualización**: 2025-11-13

---

## Tabla Comparativa General

| Modelo | Tipo | Reasoning | Speed | Input Size | Output Size | Conocimiento Hasta |
|--------|------|-----------|-------|------------|-------------|-------------------|
| **GPT-5** | Flagship | ●●●● | ⚡⚡⚡ | 📝+🖼️+📊 | 📝+🖼️ | Sep 30, 2024 |
| **GPT-4.1** | Smart | ●●●● | ⚡⚡⚡ | 📝+🖼️+📊 | 📝+🖼️ | Jun 01, 2024 |
| **GPT-5-Codex** | Coding | ●●●● | ⚡⚡⚡ | 📝+🖼️ | 📝 | Sep 30, 2024 |
| **GPT-4.1 mini** | Fast | ●●● | ⚡⚡⚡⚡ | 📝+📊 | 📝+🖼️ | Jun 01, 2024 |
| **4o mini** | Budget | ●● | ⚡⚡⚡⚡ | 📝+🖼️ | 📝+🖼️ | Oct 01, 2023 |
| **GPT-5-mini** | Balanced | ●●● | ⚡⚡⚡⚡ | 📝+🖼️ | 📝+🖼️ | May 31, 2024 |

**Leyenda**:
- ● = Capacidad de razonamiento
- ⚡ = Velocidad
- 📝 = Texto
- 🖼️ = Imágenes
- 📊 = Documentos estructurados

---

## Modelos Principales (Flagship)

### GPT-5
**Mejor para**: Coding y tareas agentic multi-dominio

**Características**:
- Reasoning: ●●●● (Máximo)
- Speed: ⚡⚡⚡ (Rápido)
- Input: Texto + Imágenes + Documentos
- Output: Texto + Imágenes
- Reasoning Tokens: ✅ Disponible

**Contexto**:
- Window: 400,000 tokens
- Max Output: 128,000 tokens
- Knowledge Cutoff: Sep 30, 2024

**Precios (por 1M tokens)**:
- Input: $1.25
- Cached Input: $0.13
- Output: $10.00

**Endpoints disponibles**:
- ✅ `/v1/chat/completions`
- ✅ `/v1/responses`
- ⭕ `/v1/assistants` (coming soon)
- ⭕ `/v1/batch` (coming soon)
- ⭕ `/v1/fine-tuning` (coming soon)

**Supported Features**:
- ✅ Streaming
- ✅ Function calling
- ✅ Structured outputs
- ⭕ Fine-tuning (coming soon)
- ⭕ Distillation (coming soon)
- ⭕ Predicted outputs (coming soon)
- ✅ Image input

**Rate Limits (TPM)**:
- Free: -
- Tier 1: 500,000
- Tier 2: 1,000,000
- Tier 3: 2,000,000
- Tier 4: 4,000,000

---

### GPT-4.1
**Mejor para**: Non-reasoning tasks (smartest model)

**Características**:
- Reasoning: ●●●● (Máximo)
- Speed: ⚡⚡⚡ (Rápido)
- Input: Texto + Imágenes + Documentos
- Output: Texto + Imágenes
- Reasoning Tokens: ⭕ No disponible

**Contexto**:
- Window: 1,047,576 tokens
- Max Output: 32,768 tokens
- Knowledge Cutoff: Jun 01, 2024

**Precios (por 1M tokens)**:
- Input: $2.00
- Cached Input: $0.50
- Output: $8.00

**Endpoints disponibles**:
- ✅ `/v1/chat/completions`
- ✅ `/v1/responses`
- ✅ `/v1/assistants`
- ✅ `/v1/batch`
- ✅ `/v1/fine-tuning`

**Supported Features**:
- ✅ Streaming
- ✅ Function calling
- ✅ Structured outputs
- ✅ Fine-tuning
- ✅ Distillation
- ✅ Predicted outputs
- ✅ Image input

**Rate Limits (TPM)**:
- Free: -
- Tier 1: 30,000
- Tier 2: 450,000
- Tier 3: 800,000

---

### GPT-5-Codex
**Mejor para**: Agentic coding en Codex

**Características**:
- Reasoning: ●●●● (Máximo)
- Speed: ⚡⚡⚡ (Rápido)
- Input: Texto + Imágenes
- Output: Texto
- Reasoning Tokens: ✅ Disponible

**Contexto**:
- Window: 400,000 tokens
- Max Output: 128,000 tokens
- Knowledge Cutoff: Sep 30, 2024

**Precios (por 1M tokens)**:
- Input: $1.25
- Cached Input: $0.13
- Output: $10.00

**Endpoints disponibles**:
- ✅ `/v1/chat/completions`
- ✅ `/v1/responses`
- ⭕ `/v1/assistants` (coming soon)
- ⭕ `/v1/batch` (coming soon)
- ✅ `/v1/fine-tuning`

**Supported Features**:
- ✅ Streaming
- ✅ Function calling
- ✅ Structured outputs
- ⭕ Fine-tuning (available, pero coming soon mejoras)
- ⭕ Distillation (coming soon)
- ⭕ Predicted outputs (coming soon)
- ✅ Image input

**Rate Limits (TPM)**:
- Free: -
- Tier 1: 500,000
- Tier 2: 1,000,000
- Tier 3: 2,000,000
- Tier 4: 4,000,000

---

## Modelos Mini (Optimizados)

### GPT-4.1 mini
**Mejor para**: Versión más rápida de GPT-4.1

**Características**:
- Intelligence: ●●● (Alto)
- Speed: ⚡⚡⚡⚡ (Muy rápido)
- Input: Texto + Documentos
- Output: Texto + Imágenes
- Reasoning Tokens: ⭕ No disponible

**Contexto**:
- Window: 1,047,576 tokens
- Max Output: 32,768 tokens
- Knowledge Cutoff: Jun 01, 2024

**Precios (por 1M tokens)**:
- Input: $0.40
- Cached Input: $0.10
- Output: $1.60

**Endpoints disponibles**:
- ✅ `/v1/chat/completions`
- ✅ `/v1/responses`
- ✅ `/v1/assistants`
- ✅ `/v1/batch`
- ✅ `/v1/fine-tuning`

**Supported Features**:
- ✅ Streaming
- ✅ Function calling
- ✅ Structured outputs
- ✅ Fine-tuning
- ✅ Distillation
- ✅ Predicted outputs
- ✅ Image input

**Rate Limits (TPM)**:
- Free: 40,000
- Tier 1: 200,000
- Tier 2: 2,000,000
- Tier 3: 4,000,000
- Tier 4: 10,000,000
- Tier 5: 150,000,000

---

### 4o mini
**Mejor para**: Tareas focused a bajo costo

**Características**:
- Intelligence: ●● (Medio)
- Speed: ⚡⚡⚡⚡ (Muy rápido)
- Input: Texto + Imágenes
- Output: Texto + Imágenes
- Reasoning Tokens: ⭕ No disponible

**Contexto**:
- Window: 128,000 tokens
- Max Output: 16,384 tokens
- Knowledge Cutoff: Oct 01, 2023

**Precios (por 1M tokens)**:
- Input: $0.15
- Cached Input: $0.08
- Output: $0.60

**Endpoints disponibles**:
- ✅ `/v1/chat/completions`
- ✅ `/v1/responses`
- ✅ `/v1/assistants`
- ✅ `/v1/batch`
- ✅ `/v1/fine-tuning`

**Supported Features**:
- ✅ Streaming
- ✅ Function calling
- ✅ Structured outputs
- ✅ Fine-tuning
- ✅ Distillation
- ✅ Predicted outputs
- ✅ Image input

**Rate Limits (TPM)**:
- Free: 40,000
- Tier 1: 200,000
- Tier 2: 2,000,000
- Tier 3: 4,000,000
- Tier 4: 10,000,000
- Tier 5: 150,000,000

---

### GPT-5-mini
**Mejor para**: Tareas well-defined con mejor costo-eficiencia

**Características**:
- Reasoning: ●●● (Alto)
- Speed: ⚡⚡⚡⚡ (Muy rápido)
- Input: Texto + Imágenes
- Output: Texto + Imágenes
- Reasoning Tokens: ✅ Disponible

**Contexto**:
- Window: 400,000 tokens
- Max Output: 128,000 tokens
- Knowledge Cutoff: May 31, 2024

**Precios (por 1M tokens)**:
- Input: $0.25
- Cached Input: $0.03
- Output: $2.00

**Endpoints disponibles**:
- ✅ `/v1/chat/completions`
- ✅ `/v1/responses`
- ✅ `/v1/assistants`
- ✅ `/v1/batch`
- ⭕ `/v1/fine-tuning` (coming soon)

**Supported Features**:
- ✅ Streaming
- ✅ Function calling
- ✅ Structured outputs
- ⭕ Fine-tuning (coming soon)
- ⭕ Distillation (coming soon)
- ⭕ Predicted outputs (coming soon)
- ✅ Image input

**Rate Limits (TPM)**:
- Free: -
- Tier 1: 500,000
- Tier 2: 2,000,000
- Tier 3: 4,000,000
- Tier 4: 10,000,000
- Tier 5: 100,000,000

---

## Análisis de Costos

### Comparativa de Precios (Input por 1M tokens)

| Modelo | Input | Cached Input | Output | Ratio Output/Input |
|--------|-------|--------------|--------|-------------------|
| **4o mini** | $0.15 | $0.08 | $0.60 | 4x |
| **GPT-5-mini** | $0.25 | $0.03 | $2.00 | 8x |
| **GPT-4.1 mini** | $0.40 | $0.10 | $1.60 | 4x |
| **GPT-5** | $1.25 | $0.13 | $10.00 | 8x |
| **GPT-5-Codex** | $1.25 | $0.13 | $10.00 | 8x |
| **GPT-4.1** | $2.00 | $0.50 | $8.00 | 4x |

### Escenarios de Uso y Costos

#### Escenario 1: Workflow simple (100K tokens input, 10K tokens output)
```
4o mini:       $0.015 + $0.006 = $0.021
GPT-5-mini:    $0.025 + $0.020 = $0.045  (2.1x más caro)
GPT-4.1 mini:  $0.040 + $0.016 = $0.056  (2.7x más caro)
GPT-5:         $0.125 + $0.100 = $0.225  (10.7x más caro)
GPT-4.1:       $0.200 + $0.080 = $0.280  (13.3x más caro)
```

#### Escenario 2: Workflow con caché (100K tokens cached, 10K tokens output)
```
4o mini:       $0.008 + $0.006 = $0.014
GPT-5-mini:    $0.003 + $0.020 = $0.023  (1.6x más caro)
GPT-4.1 mini:  $0.010 + $0.016 = $0.026  (1.9x más caro)
GPT-5:         $0.013 + $0.100 = $0.113  (8.1x más caro)
GPT-4.1:       $0.050 + $0.080 = $0.130  (9.3x más caro)
```

#### Escenario 3: Code generation (50K tokens input, 20K tokens output)
```
4o mini:       $0.008 + $0.012 = $0.020
GPT-5-mini:    $0.013 + $0.040 = $0.053  (2.7x más caro)
GPT-4.1 mini:  $0.020 + $0.032 = $0.052  (2.6x más caro)
GPT-5-Codex:   $0.063 + $0.200 = $0.263  (13.2x más caro)
GPT-5:         $0.063 + $0.200 = $0.263  (13.2x más caro)
```

---

## Recomendaciones para NOVA

### Phase 1 (MVP - Current)

**Para StaticExecutor** (ejecución de código hardcoded):
- **Recomendado**: `4o mini`
- **Razón**: No necesitamos reasoning avanzado, solo parsing y validación
- **Costo estimado**: ~$0.02 por workflow (100 workflows = $2/mes)

**Para validaciones y decisiones simples**:
- **Recomendado**: `GPT-5-mini`
- **Razón**: Balance entre reasoning y costo, con caché muy barato ($0.03/1M)
- **Costo estimado**: ~$0.045 por workflow con decisiones

**Para debugging y análisis de errores**:
- **Recomendado**: `GPT-4.1 mini`
- **Razón**: Más inteligente que 4o mini, pero más barato que flagship
- **Costo estimado**: ~$0.056 por análisis

### Phase 2 (AI-Powered)

**Para CachedExecutor** (generación con caché):
- **Primera generación**: `GPT-5-Codex` ($0.263 por generación)
- **Lecturas de caché**: `GPT-5-Codex` cached ($0.013 input + $0.200 output = $0.213)
- **Ahorro con caché**: ~19% después de la primera vez

**Para AIExecutor** (generación always fresh):
- **Recomendado**: `GPT-5-Codex` o `GPT-5`
- **Razón**: Máxima calidad de código, reasoning avanzado
- **Costo estimado**: ~$0.263 por generación

**Para self-learning y análisis de patrones**:
- **Recomendado**: `GPT-5`
- **Razón**: Mejor reasoning, puede analizar patrones complejos
- **Costo estimado**: Variable según complejidad

### Proyección de Costos NOVA

#### Escenario Conservador (100 workflows/día)
```
Phase 1 (StaticExecutor con 4o mini):
- Input: 100 workflows × 100K tokens × $0.15/1M = $1.50/día
- Output: 100 workflows × 10K tokens × $0.60/1M = $0.60/día
- Total: $2.10/día = ~$63/mes
```

#### Escenario Moderado (500 workflows/día)
```
Phase 1 (StaticExecutor con 4o mini):
- Total: $10.50/día = ~$315/mes

Phase 2 (mix CachedExecutor 70% + AIExecutor 30%):
- CachedExecutor: 350 workflows × $0.213 = $74.55/día
- AIExecutor: 150 workflows × $0.263 = $39.45/día
- Total: $114/día = ~$3,420/mes
```

#### Escenario Agresivo (2000 workflows/día)
```
Phase 1: $42/día = ~$1,260/mes
Phase 2: $456/día = ~$13,680/mes
```

### Optimizaciones de Costo

1. **Usar caché agresivamente**:
   - Cached input es 50-90% más barato
   - Implementar caché de workflows repetitivos

2. **Escalar modelos según complejidad**:
   - Simple validations: `4o mini`
   - Medium logic: `GPT-5-mini`
   - Complex reasoning: `GPT-5` o `GPT-5-Codex`

3. **Batch processing**:
   - Usar `/v1/batch` para workflows no-urgentes
   - Reducción de costos (no especificado en docs, pero típicamente 50% off)

4. **Fine-tuning** (Phase 2):
   - Para workflows muy repetitivos
   - Modelos custom más baratos a largo plazo

---

## Features Comparison

### Reasoning Tokens
**Disponible en**:
- ✅ GPT-5
- ✅ GPT-5-Codex
- ✅ GPT-5-mini
- ❌ GPT-4.1
- ❌ GPT-4.1 mini
- ❌ 4o mini

**Implicación para NOVA**: Reasoning tokens ayudan en decisiones complejas, pero no crítico para Phase 1.

### Fine-tuning
**Disponible en**:
- ✅ GPT-4.1
- ✅ GPT-4.1 mini
- ✅ 4o mini
- ⭕ GPT-5-Codex (coming soon)
- ⭕ GPT-5-mini (coming soon)
- ❌ GPT-5

**Implicación para NOVA**: Útil para Phase 2, cuando tengamos workflows específicos repetitivos.

### Context Window
**Más grande**:
1. GPT-4.1 / GPT-4.1 mini: 1,047,576 tokens (1M+)
2. GPT-5 / GPT-5-Codex / GPT-5-mini: 400,000 tokens
3. 4o mini: 128,000 tokens

**Implicación para NOVA**: 400K es más que suficiente para workflows complejos.

---

## Decision Matrix

| Use Case | Recommended Model | Alternative | Reasoning |
|----------|------------------|-------------|-----------|
| **Simple validation** | 4o mini | GPT-5-mini | Costo mínimo, suficiente inteligencia |
| **Decision logic** | GPT-5-mini | GPT-4.1 mini | Balance costo/reasoning con caché barato |
| **Code generation** | GPT-5-Codex | GPT-5 | Optimizado para código |
| **Error analysis** | GPT-4.1 mini | GPT-5-mini | Más inteligente sin costo flagship |
| **Complex reasoning** | GPT-5 | GPT-4.1 | Máximo reasoning + features recientes |
| **High-volume batch** | 4o mini | GPT-5-mini | Costo crítico en alto volumen |

---

## Conclusiones

### Para Phase 1 (MVP):
**Recomendación principal**: `4o mini`
- Costo-efectivo (~$63/mes para 100 workflows/día)
- Suficiente para StaticExecutor y validaciones simples
- Rate limits generosos (40K TPM en tier free)

### Para Phase 2 (AI-Powered):
**Recomendación principal**: `GPT-5-Codex` con caché agresivo
- Mejor calidad de código generado
- Reasoning tokens para lógica compleja
- Caché reduce costo en workflows repetitivos (~19% ahorro)

**Modelo backup**: `GPT-5-mini`
- Para decisiones y validaciones que necesiten reasoning
- Muy barato con caché ($0.03/1M tokens cached)

### Trade-offs Clave:
1. **Costo vs. Calidad**: 4o mini es 13x más barato que GPT-5, pero con menos reasoning
2. **Caché**: Fundamental para reducir costos en Phase 2 (hasta 90% ahorro en input)
3. **Rate Limits**: Modelos flagship tienen más límites iniciales, escalar con tiers

---

**Próximos Pasos**:
1. Implementar Phase 1 con `4o mini` para validar arquitectura
2. Medir métricas reales de tokens/workflow
3. Evaluar upgrade a `GPT-5-mini` cuando implementemos decisiones complejas
4. Preparar infraestructura de caché para Phase 2
