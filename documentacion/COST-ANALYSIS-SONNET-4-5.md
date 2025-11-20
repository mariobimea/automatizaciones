# 💰 NOVA Cost Analysis: Claude Sonnet 4.5 vs GPT-4o-mini

**Fecha**: 20 Noviembre 2025
**Estado**: ✅ Análisis completo
**Objetivo**: Evaluar viabilidad económica de usar Claude Sonnet 4.5 en workflows de NOVA

---

## 📊 Executive Summary

| Escenario | GPT-4o-mini | Sonnet 4.5 (standard) | Sonnet 4.5 (con cache 70%+) | Multiplier |
|-----------|-------------|----------------------|------------------------------|------------|
| **Light Usage** (10 workflows/day) | $0.86/mes | $18.00/mes | $10.01/mes | **11.6x** |
| **Medium Usage** (50 workflows/day) | $8.10/mes | $168.75/mes | $78.30/mes | **9.7x** |
| **Heavy Usage** (100 workflows/day) | $12.96/mes | $540.00/mes | $225.72/mes | **17.4x** |
| **Dev/Testing** (3 workflows/day) | $0.23/mes | $4.73/mes | N/A | **20.8x** |

### Key Findings

1. ⚠️ **Sonnet 4.5 cuesta ~20x más que GPT-4o-mini** (API estándar)
2. ✅ **Prompt caching reduce costos 44-58%** (crítico para viabilidad)
3. ✅ **Para uso light (<50 workflows/day), diferencia es manejable** ($10-80/mes)
4. ⚠️ **Para uso enterprise (>100 workflows/day), costos escalan rápidamente** ($200-500/mes)
5. 🎯 **Cache hit rate >70% es OBLIGATORIO** para hacer Sonnet viable

---

## 💵 Pricing Models (Noviembre 2025)

### Claude Sonnet 4.5

| API Type | Input (per 1M tokens) | Output (per 1M tokens) | Discount |
|----------|----------------------|------------------------|----------|
| Standard | $3.00 | $15.00 | - |
| Prompt Caching (write) | $3.75 | $15.00 | - |
| Prompt Caching (read) | $0.30 | $15.00 | **90% off input** |
| Batch API | $1.50 | $7.50 | **50% off** |

**Extended Context** (>200K tokens): $6.00 input / $22.50 output

### GPT-4o-mini (Current)

| API Type | Input (per 1M tokens) | Output (per 1M tokens) | Discount |
|----------|----------------------|------------------------|----------|
| Standard | $0.15 | $0.60 | - |
| Batch API | $0.075 | $0.30 | **50% off** |

---

## 🔬 Detailed Scenario Analysis

### Escenario 1: Light Usage - Invoice Processing

**Perfil**: Pequeña empresa procesando ~10 facturas/día

**Parámetros**:
- Workflows/día: **10**
- CachedExecutor nodes/workflow: **2** (e.g., `extract_pdf`, `find_amount`)
- Avg input tokens: **8,000** (prompt + context + RAG docs)
- Avg output tokens: **400** (código Python generado)
- Prompt caching: **SÍ** (70% hit rate)

**Costos**:
```
GPT-4o-mini:              $0.86/mes   (baseline)
Sonnet 4.5 (standard):    $18.00/mes  (20.8x más caro)
Sonnet 4.5 (con cache):   $10.01/mes  (11.6x más caro)
```

**Análisis**:
- ✅ **Diferencia manejable**: $10/mes es asumible para pequeñas empresas
- ✅ **Calidad >> Costo**: Si Sonnet mejora significativamente code quality, vale la pena
- 🎯 **ROI positivo**: Si 1 error menos al mes ahorra >$10 en tiempo, break-even

**Recomendación**: ✅ **VIABLE** - Prueba Sonnet 4.5 con prompt caching

---

### Escenario 2: Medium Usage - Multi-tenant SaaS

**Perfil**: SaaS con 10 clientes, ~5 workflows/día cada uno

**Parámetros**:
- Workflows/día: **50**
- CachedExecutor nodes/workflow: **3**
- Avg input tokens: **10,000**
- Avg output tokens: **500**
- Prompt caching: **SÍ** (80% hit rate, workflows repetitivos)

**Costos**:
```
GPT-4o-mini:              $8.10/mes   (baseline)
Sonnet 4.5 (standard):    $168.75/mes (20.8x más caro)
Sonnet 4.5 (con cache):   $78.30/mes  (9.7x más caro)
```

**Análisis**:
- ⚠️ **Impacto moderado**: $78/mes adicionales (~$1,000/año)
- ✅ **Escalable con revenue**: Si cobras $50/mes/cliente → $500/mes ingreso
- 🎯 **Cache hit rate crítico**: 80% hit rate reduce costo de $169 → $78 (53% savings)

**Recomendación**: ⚠️ **VIABLE CON CONDICIONES**
- Implementar **semantic cache** desde día 1
- Monitorear cache hit rate (target: >80%)
- Considerar pricing tier para clientes premium

---

### Escenario 3: Heavy Usage - Enterprise

**Perfil**: Uso enterprise con 100+ workflows/día, data pipelines complejos

**Parámetros**:
- Workflows/día: **100**
- CachedExecutor nodes/workflow: **4**
- Avg input tokens: **12,000**
- Avg output tokens: **600**
- Prompt caching: **SÍ** (85% hit rate, workflows estandarizados)
- Batch API: **SÍ** (workflows no-críticos)

**Costos**:
```
GPT-4o-mini (batch):      $12.96/mes  (baseline)
Sonnet 4.5 (standard):    $540.00/mes (41.7x más caro)
Sonnet 4.5 (con cache):   $225.72/mes (17.4x más caro)
Sonnet 4.5 (batch):       $270.00/mes (20.8x más caro)
```

**Análisis**:
- ⚠️ **Alto impacto**: $225-500/mes ($2,700-6,000/año)
- ⚠️ **Escalabilidad limitada**: Costos crecen linealmente con workflows
- ✅ **Cache es game-changer**: 85% hit rate reduce de $540 → $226 (58% savings)
- 🎯 **Batch API útil**: Para workflows async (e.g., reportes nocturnos)

**Recomendación**: ⚠️ **REQUIERE ESTRATEGIA HÍBRIDA**
- **Fase 1**: Usar GPT-4o-mini para workflows estándar
- **Fase 2**: Sonnet 4.5 solo para workflows críticos (ej: compliance, legal)
- **Optimización**: Implementar semantic cache + batch API
- **Target**: Cache hit rate >85% para viabilidad económica

---

### Escenario 4: Development/Testing

**Perfil**: Testing y desarrollo, pocos workflows, sin optimizaciones

**Parámetros**:
- Workflows/día: **3**
- CachedExecutor nodes/workflow: **2**
- Avg input tokens: **7,000**
- Avg output tokens: **350**
- Prompt caching: **NO** (prompts cambian constantemente)

**Costos**:
```
GPT-4o-mini:              $0.23/mes   (baseline)
Sonnet 4.5 (standard):    $4.73/mes   (20.8x más caro)
```

**Análisis**:
- ✅ **Despreciable**: $4.73/mes es irrelevante para dev/testing
- ✅ **Sin necesidad de optimización**: Bajo volumen no justifica complejidad

**Recomendación**: ✅ **USAR SONNET 4.5 SIN RESTRICCIONES** - Costo negligible

---

## 🎯 Strategic Recommendations

### Fase 1: MVP y Validación (Primeros 3 meses)

**Modelo**: GPT-4o-mini
**Razón**: Validar product-market fit sin overhead de costos
**Costo esperado**: $10-50/mes

**Acciones**:
- ✅ Lanzar con GPT-4o-mini (ya implementado)
- ✅ Instrumentar logging de token usage por workflow
- ✅ Identificar workflows con mayor valor (candidates para Sonnet)
- ✅ Medir quality metrics (success rate, retry rate, manual interventions)

---

### Fase 2: Upgrade Selectivo (Mes 4-6)

**Modelo**: Híbrido (GPT-4o-mini + Sonnet 4.5)
**Estrategia**: Sonnet solo para workflows críticos

**Criterios para usar Sonnet 4.5**:
1. ✅ **High business impact**: Legal documents, compliance, financial
2. ✅ **Complex logic**: Multi-step reasoning, error handling complejo
3. ✅ **Low volume**: <10 workflows/día (costo controlado)
4. ✅ **Repetitive**: Prompts similares → cache hit rate >70%

**Acciones**:
- ✅ Implementar `executor_strategy` en workflow definition:
  ```json
  {
    "id": "legal_review",
    "executor": "cached",
    "model": "sonnet-4.5",  // Override default
    "prompt": "Review contract for legal compliance..."
  }
  ```
- ✅ Monitorear cost per workflow (añadir a Chain of Work)
- ✅ A/B testing: GPT-4o-mini vs Sonnet 4.5 en workflows piloto

---

### Fase 3: Optimización Agresiva (Mes 7+)

**Modelo**: Sonnet 4.5 (optimizado)
**Estrategia**: Cache semántico + Batch API + Code reuse

**Implementaciones**:

#### 1. Semantic Cache (Phase 3 roadmap)
```python
# Hash-based cache (Phase 3)
cache_key = hash(prompt + context_summary)
if code := cache.get(cache_key):
    return code  # Evita llamada a LLM (100% savings)

# Semantic cache con embeddings
similar_prompts = vector_store.similarity_search(prompt, k=1)
if similarity > 0.95:
    return cached_code  # Reusa código similar
```

**Impacto esperado**: 70-85% cache hit rate → 50-60% cost reduction

#### 2. Batch API para Workflows Non-Critical
```python
# Workflows async (e.g., reportes nocturnos, batch processing)
if workflow.priority == "low":
    executor = CachedExecutor(model="sonnet-4.5", use_batch=True)
    # 50% discount en costos
```

**Impacto esperado**: 50% cost reduction en workflows async

#### 3. Code Repository (Learning System)
```python
# Guardar código exitoso para reuso
successful_codes = chain_of_work.filter(status="success", attempts=1)
for code in successful_codes:
    code_repo.store(
        task_type=code.node_id,
        code=code.code_executed,
        success_rate=1.0
    )

# Reuso en workflows futuros (zero LLM cost)
if existing_code := code_repo.get(task_type, similarity=0.9):
    return existing_code
```

**Impacto esperado**: 30-50% workflows no requieren LLM calls

---

## 📈 Token Usage Estimates

### Breakdown Típico de Tokens (por ActionNode)

**Input Tokens** (~8,000-12,000 total):
```
Base system prompt:        1,500 tokens
Task description:            500 tokens
Current context (JSON):    2,000 tokens
RAG documentation:         4,000 tokens (KnowledgeManager)
Error history (retry):     1,000 tokens (if applicable)
─────────────────────────────────────
TOTAL INPUT:              ~9,000 tokens
```

**Output Tokens** (~350-600):
```
Generated Python code:       300 tokens
Context updates:              50 tokens
Error handling:               50 tokens
─────────────────────────────────────
TOTAL OUTPUT:               ~400 tokens
```

### Cómo Reducir Token Usage

**Input Optimization**:
1. ✅ **RAG doc filtering**: Solo docs relevantes (no todo knowledge/)
2. ✅ **Context pruning**: Remover campos irrelevantes del contexto
3. ✅ **Compressed prompts**: Usar bullet points, no prosa
4. ✅ **Prompt caching**: Cache system prompt + RAG docs (90% savings)

**Output Optimization**:
1. ✅ **Code templates**: Prompts que generen código conciso
2. ✅ **No comments**: Generar código sin docstrings (agregar después)
3. ✅ **Limit retries**: Max 2-3 intentos (no más)

**Impacto estimado**: 20-30% token reduction

---

## 💡 Cost Optimization Strategies

### Strategy 1: Smart Model Selection (Implement Today)

```python
# src/core/executors.py
def select_model(node: ActionNode, context: dict) -> str:
    """
    Select optimal model based on task complexity and business value.
    """
    # High-value workflows → Sonnet 4.5
    if context.get("workflow_type") in ["legal", "compliance", "financial"]:
        return "sonnet-4.5"

    # Complex reasoning → Sonnet 4.5
    if node.estimated_complexity > 0.8:
        return "sonnet-4.5"

    # Standard workflows → GPT-4o-mini
    return "gpt-4o-mini"
```

**Impacto**: 70% workflows con GPT-4o-mini → 80% cost savings

---

### Strategy 2: Aggressive Prompt Caching (Implement Phase 3)

```python
# src/core/ai/client.py
def generate_code(prompt: str, context: dict) -> str:
    """
    Generate code with aggressive prompt caching.
    """
    # Cache static parts (system prompt + RAG docs)
    cached_prefix = build_system_prompt() + load_rag_docs()

    # Dynamic part (task + context)
    dynamic_suffix = f"Task: {prompt}\nContext: {context}"

    # Anthropic caches prefixes automatically if marked
    response = anthropic.messages.create(
        model="claude-sonnet-4-5-20250929",
        messages=[
            {"role": "user", "content": cached_prefix + dynamic_suffix}
        ],
        system=[
            {
                "type": "text",
                "text": cached_prefix,
                "cache_control": {"type": "ephemeral"}  # Cache this part
            }
        ]
    )
```

**Impacto**: 70-85% input tokens cached → 44-58% cost reduction

---

### Strategy 3: Semantic Cache (Phase 3)

```python
# src/core/cache/semantic_cache.py
from sentence_transformers import SentenceTransformer

class SemanticCodeCache:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vector_store = ChromaDB()

    async def get_similar_code(self, prompt: str, threshold: float = 0.92):
        """
        Find previously generated code for similar prompts.
        """
        prompt_embedding = self.model.encode(prompt)
        results = self.vector_store.similarity_search(
            embedding=prompt_embedding,
            threshold=threshold
        )

        if results:
            # Return cached code (zero LLM cost)
            return results[0]["code"]

        return None

    async def store_code(self, prompt: str, code: str, success: bool):
        """
        Store successful code generation for reuse.
        """
        if success:
            prompt_embedding = self.model.encode(prompt)
            self.vector_store.add(
                embedding=prompt_embedding,
                metadata={"prompt": prompt, "code": code}
            )
```

**Impacto**: 40-60% prompts similares → 100% cost savings (no LLM call)

---

## 📊 ROI Analysis

### Cuándo Vale la Pena Sonnet 4.5?

**Calidad de Código**:
- Si Sonnet 4.5 reduce error rate de 10% → 3% (7% improvement)
- Si 7% menos errores ahorra 2h/mes de debugging
- Si tu hourly rate es $50/h → **$100/mes savings**
- Costo adicional Sonnet: **$10-80/mes**
- **ROI positivo** si ahorras >2h/mes

**Time to Market**:
- Si Sonnet 4.5 genera código correcto en 1er intento (vs 2-3 con GPT-4o-mini)
- Reduces latency de workflows: 60s → 30s
- Para 50 workflows/día → **25min/día savings** → 12.5h/mes
- Si tu hourly rate es $50/h → **$625/mes savings**
- Costo adicional Sonnet: **$70/mes**
- **ROI: 8.9x**

**Customer Trust**:
- Workflows críticos (legal, compliance) con Sonnet 4.5
- Reduces liability risk y mejora customer confidence
- Valor intangible pero **muy alto** para enterprise clients

---

## 🎬 Action Plan

### Immediate (Esta Semana)

1. ✅ **Run cost calculator** con tus números reales:
   ```bash
   cd /nova
   python tools/cost_calculator.py
   # Edita scenarios con tu uso esperado
   ```

2. ✅ **Add cost tracking** a Chain of Work:
   ```python
   # ai_metadata ya incluye tokens/cost
   chain_of_work.ai_metadata = {
       "model": "sonnet-4.5",
       "tokens_input": 8000,
       "tokens_output": 400,
       "cost_usd": 0.030  # Calculate based on pricing
   }
   ```

3. ✅ **Dashboard de costos** (query PostgreSQL):
   ```sql
   SELECT
       DATE(created_at) as date,
       SUM((ai_metadata->>'tokens_input')::int) as total_input_tokens,
       SUM((ai_metadata->>'tokens_output')::int) as total_output_tokens,
       SUM((ai_metadata->>'cost_usd')::float) as daily_cost
   FROM chain_of_work
   WHERE ai_metadata IS NOT NULL
   GROUP BY DATE(created_at)
   ORDER BY date DESC;
   ```

---

### Short-term (Próximas 2 Semanas)

1. ✅ **Implement model selection**:
   ```python
   # Añadir campo opcional en workflow definition
   {
     "id": "critical_task",
     "executor": "cached",
     "model": "sonnet-4.5",  // Override default (gpt-4o-mini)
     "prompt": "..."
   }
   ```

2. ✅ **A/B testing**:
   - 10% workflows con Sonnet 4.5
   - Comparar: success rate, retry rate, execution time, cost
   - Decide si vale la pena el upgrade

---

### Medium-term (Próximos 2 Meses)

1. ✅ **Implement prompt caching** (Anthropic API):
   - Ver [docs de Anthropic](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
   - Cache system prompts + RAG docs
   - Target: 70%+ cache hit rate

2. ✅ **Build semantic cache** (Phase 3):
   - Vector store para prompts similares
   - Reuso de código exitoso
   - Target: 50%+ workflows cacheable

---

## 🔮 Future Considerations

### Alternative Models

**Claude Haiku 4** (si se lanza):
- Pricing esperado: ~$0.50/$2.50 per 1M tokens
- 3-5x más barato que Sonnet
- Suficiente para workflows simples

**Open-source alternatives**:
- Llama 3.3 70B (via Groq/Together)
- Pricing: ~$0.50/$0.80 per 1M tokens
- Self-hosted: $0 (pero infrastructure costs)

---

## 📝 Conclusiones

### ✅ Sonnet 4.5 es VIABLE si:
1. Implementas **prompt caching** (mandatory)
2. Cache hit rate >70% (monitorear constantemente)
3. Uso <50 workflows/día O workflows de alto valor
4. Quality improvement justifica 10-20x cost increase

### ⚠️ Sonnet 4.5 es RIESGOSO si:
1. Alto volumen (>100 workflows/día) sin optimizaciones
2. Workflows commodity (low business value)
3. Budget constraints estrictos (<$100/mes)
4. No tienes semantic cache implementado

### 🎯 Estrategia Recomendada:

**PHASE 1 (Ahora)**: GPT-4o-mini para todo
**PHASE 2 (Mes 2-3)**: Sonnet 4.5 para workflows críticos (hybrid approach)
**PHASE 3 (Mes 4-6)**: Sonnet 4.5 con prompt caching + semantic cache

**Target final**: $50-150/mes con Sonnet 4.5 para 50-100 workflows/día

---

## 📚 Referencias

- [Anthropic Pricing (Nov 2025)](https://www.anthropic.com/pricing)
- [Prompt Caching Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
- [NOVA Architecture](/documentacion/ARQUITECTURA.md)
- [Phase 3 Roadmap](/documentacion/futuro/BACKLOG.md)

---

**Última actualización**: 20 Noviembre 2025
**Próxima revisión**: Cuando Anthropic actualice pricing (quarterly)
