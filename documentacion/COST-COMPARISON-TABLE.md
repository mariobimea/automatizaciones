# 📊 Quick Cost Comparison: GPT-4o-mini vs Sonnet 4.5

**Fecha**: 20 Noviembre 2025

---

## 💵 Pricing per Million Tokens

| Model | Input | Output | Notes |
|-------|-------|--------|-------|
| **GPT-4o-mini** | $0.15 | $0.60 | Current (Phase 2) |
| **Sonnet 4.5** | $3.00 | $15.00 | **20x más caro** |
| Sonnet 4.5 (cache write) | $3.75 | $15.00 | Primera vez |
| Sonnet 4.5 (cache read) | $0.30 | $15.00 | **90% off input** |
| Sonnet 4.5 (batch) | $1.50 | $7.50 | 50% off, async |

---

## 💰 Monthly Cost by Scenario

### Scenario Matrix

| Workflows/Day | Nodes | GPT-4o-mini | Sonnet (std) | Sonnet (cache 70%) | Multiplier |
|---------------|-------|-------------|--------------|-------------------|------------|
| 10 | 2 | **$0.86** | $18.00 | $10.01 | 11.6x |
| 50 | 3 | **$8.10** | $168.75 | $78.30 | 9.7x |
| 100 | 4 | **$12.96** | $540.00 | $225.72 | 17.4x |
| 3 (dev) | 2 | **$0.23** | $4.73 | N/A | 20.8x |

**Assumptions**:
- Input: 8K-12K tokens (prompt + context + RAG docs)
- Output: 400-600 tokens (generated code)
- Cache hit rate: 70-85% (workflows repetitivos)

---

## 📈 Cost per Workflow Execution

### Light Workflow (2 CachedExecutor nodes, 8K input, 400 output)

| Model | Cost/Node | Cost/Workflow | vs GPT-4o-mini |
|-------|-----------|---------------|----------------|
| GPT-4o-mini | $0.00144 | **$0.00288** | baseline |
| Sonnet 4.5 (std) | $0.03000 | $0.06000 | +**2,083%** |
| Sonnet 4.5 (cache 70%) | $0.01668 | $0.03336 | +**1,058%** |

### Medium Workflow (3 nodes, 10K input, 500 output)

| Model | Cost/Node | Cost/Workflow | vs GPT-4o-mini |
|-------|-----------|---------------|----------------|
| GPT-4o-mini | $0.00180 | **$0.00540** | baseline |
| Sonnet 4.5 (std) | $0.03750 | $0.11250 | +**1,983%** |
| Sonnet 4.5 (cache 80%) | $0.01740 | $0.05220 | +**867%** |

### Heavy Workflow (4 nodes, 12K input, 600 output)

| Model | Cost/Node | Cost/Workflow | vs GPT-4o-mini |
|-------|-----------|---------------|----------------|
| GPT-4o-mini (batch) | $0.00108 | **$0.00432** | baseline |
| Sonnet 4.5 (std) | $0.04500 | $0.18000 | +**4,067%** |
| Sonnet 4.5 (cache 85%) | $0.01881 | $0.07524 | +**1,642%** |
| Sonnet 4.5 (batch) | $0.02250 | $0.09000 | +**1,983%** |

---

## 🎯 Break-Even Analysis

### ¿Cuándo vale la pena Sonnet 4.5?

**Escenario 1**: Quality Improvement
```
Asumiendo:
- Sonnet reduce error rate: 10% → 3% (7% improvement)
- 7% menos errores = 2h/mes menos debugging
- Hourly rate: $50/h

Savings: $100/mes
Extra cost (light usage): $10/mes
Net benefit: +$90/mes ✅

ROI: 10x
```

**Escenario 2**: Time to Market
```
Asumiendo:
- Sonnet genera código correcto en 1er intento (vs 2-3 con GPT-4o-mini)
- Latency reduction: 60s → 30s por workflow
- 50 workflows/día = 25min/día savings = 12.5h/mes

Savings: $625/mes (at $50/h)
Extra cost (medium usage): $70/mes
Net benefit: +$555/mes ✅

ROI: 8.9x
```

**Escenario 3**: Enterprise Trust
```
Asumiendo:
- Workflows críticos (legal, compliance) con Sonnet
- Reduces liability risk, mejora customer confidence
- Value: Prevents 1 mistake/year that costs $10K

Savings: $833/mes (amortizado)
Extra cost: $80-200/mes
Net benefit: +$633/mes ✅

ROI: 4-10x
```

---

## 🚦 Decision Matrix

### Use Sonnet 4.5 ✅ When:

| Condition | Threshold | Why |
|-----------|-----------|-----|
| **Business Value** | High | Legal, compliance, financial workflows |
| **Complexity** | High | Multi-step reasoning, error handling |
| **Volume** | <50/day | Cost impact manageable (<$100/mes) |
| **Repetitiveness** | High | Cache hit rate >70% achievable |
| **Error Cost** | High | Manual fixes cost >$50/h |

### Use GPT-4o-mini ✅ When:

| Condition | Threshold | Why |
|-----------|-----------|-----|
| **Business Value** | Low | Commodity workflows, low impact |
| **Complexity** | Low | Simple data transformations |
| **Volume** | >100/day | Cost scales quickly (>$200/mes) |
| **Repetitiveness** | Low | Cache won't help |
| **Error Cost** | Low | Easy to retry/fix |

---

## 💡 Cost Optimization Strategies

### Strategy 1: Hybrid Approach (Best ROI)

```
Light workflows:      GPT-4o-mini     ($0.003/workflow)
Critical workflows:   Sonnet 4.5      ($0.033/workflow with cache)

Example mix (50 workflows/day):
- 40 light (80%):     $3.60/mes
- 10 critical (20%):  $9.90/mes
─────────────────────────────────
TOTAL:                $13.50/mes

vs All Sonnet 4.5:    $78.30/mes
Savings:              $64.80/mes (83% reduction) ✅
```

### Strategy 2: Aggressive Caching (Highest Impact)

```
Cache hit rate impact on monthly cost (50 workflows/day):

No cache (0%):        $168.75/mes
Cache 50%:            $117.45/mes  (-30%)
Cache 70%:            $78.30/mes   (-54%) ✅
Cache 85%:            $56.70/mes   (-66%)
```

**Action**: Implement prompt caching + semantic cache ASAP
**Target**: 70%+ cache hit rate
**ROI**: 50-66% cost reduction

### Strategy 3: Batch API (Moderate Impact)

```
Workflows async (50 workflows/day, 4 nodes):

Standard API:         $168.75/mes
Batch API:            $84.38/mes   (-50%) ✅
```

**Action**: Use batch for non-critical workflows (reports, analytics)
**Limitation**: 24h max latency (not suitable for real-time)
**ROI**: 50% cost reduction en workflows async

---

## 📊 Token Usage Breakdown

### Typical ActionNode with CachedExecutor

```
INPUT TOKENS (~9,000 total):
├─ System prompt:           1,500 tokens  ┐
├─ RAG documentation:       4,000 tokens  │ Cacheable (90% savings)
├─ Task description:          500 tokens  ┘
├─ Current context (JSON):  2,000 tokens
└─ Error history (retry):   1,000 tokens

OUTPUT TOKENS (~400 total):
├─ Generated Python code:     300 tokens
├─ Context updates:            50 tokens
└─ Error handling:             50 tokens
```

**Optimization opportunity**:
- Cache system prompt + RAG docs (5,500 tokens)
- If cache hit (70% probability): Save $0.01665/node
- If cache miss: Pay $0.03000/node
- **Average**: $0.01668/node (44% savings) ✅

---

## 🎬 Quick Start Guide

### Step 1: Calculate Your Costs

```bash
cd /home/user/automatizaciones/nova
python tools/cost_calculator.py

# Edit scenarios with your expected usage
```

### Step 2: Track Costs in Production

```python
# Already implemented in CachedExecutor
ai_metadata = {
    "model": "sonnet-4.5",
    "tokens_input": 8000,
    "tokens_output": 400,
    "cost_usd": 0.030,  # Auto-calculated
    "cache_hit": True,
}
```

### Step 3: Monitor Dashboard

```sql
-- Daily costs
SELECT
    DATE(created_at) as date,
    COUNT(*) as workflows,
    SUM((ai_metadata->>'tokens_input')::int) as input_tokens,
    SUM((ai_metadata->>'tokens_output')::int) as output_tokens,
    SUM((ai_metadata->>'cost_usd')::float) as cost_usd
FROM chain_of_work
WHERE ai_metadata IS NOT NULL
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Cost per workflow type
SELECT
    w.name,
    COUNT(*) as executions,
    AVG((c.ai_metadata->>'cost_usd')::float) as avg_cost,
    SUM((c.ai_metadata->>'cost_usd')::float) as total_cost
FROM chain_of_work c
JOIN executions e ON c.execution_id = e.id
JOIN workflows w ON e.workflow_id = w.id
WHERE c.ai_metadata IS NOT NULL
GROUP BY w.name
ORDER BY total_cost DESC;
```

---

## 🔮 Future Pricing Trends

### Expected Changes (2025-2026)

1. **Sonnet 4.5 price drop**: -20-30% en 12 meses (historical trend)
   - Current: $3/$15 per 1M
   - Expected: $2-2.50/$10-12 per 1M

2. **Haiku 4 launch**: Cheaper alternative (~$0.50/$2.50 per 1M)
   - 3-5x más barato que Sonnet
   - Suficiente para workflows simples

3. **Prompt caching improvements**: Cache TTL más largo (5min → 30min)
   - Mayor cache hit rate
   - Menos cache writes

**Recomendación**: Re-evaluar costos quarterly

---

## 📝 Summary

### TL;DR

| Metric | Value |
|--------|-------|
| **Sonnet 4.5 cost multiplier** | **20x** vs GPT-4o-mini |
| **With prompt caching** | **10-12x** vs GPT-4o-mini |
| **Break-even volume** | <50 workflows/day |
| **Required cache hit rate** | >70% |
| **Best strategy** | Hybrid (GPT for light, Sonnet for critical) |
| **Expected monthly cost** | $10-150 (50-100 workflows/día) |

### Decision Flowchart

```
Start
  │
  ├─ Volume <10 workflows/day?
  │   └─ YES → Use Sonnet 4.5 (cost negligible) ✅
  │
  ├─ Critical workflows (legal/compliance)?
  │   └─ YES → Use Sonnet 4.5 with caching ✅
  │
  ├─ Can implement prompt caching (70%+ hit rate)?
  │   └─ YES → Consider Sonnet 4.5 ⚠️
  │   └─ NO → Stay with GPT-4o-mini ✅
  │
  └─ Budget <$100/month?
      └─ YES → Use GPT-4o-mini ✅
      └─ NO → Hybrid approach ✅
```

---

**Última actualización**: 20 Noviembre 2025
**Herramienta**: `/nova/tools/cost_calculator.py`
**Documentación completa**: `/documentacion/COST-ANALYSIS-SONNET-4-5.md`
