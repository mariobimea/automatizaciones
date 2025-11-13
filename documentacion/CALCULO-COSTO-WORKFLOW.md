# Cálculo de Costo: Workflow de 15 Nodos con AI

**Escenario**: Generar código para un workflow completo usando GPT-5/GPT-5-Codex

---

## Asunciones Base

### Estructura de un Workflow de 15 Nodos

Ejemplo realista (Invoice Processing):
```
1. Start
2. ExtractInvoiceData (ActionNode - code generation)
3. ValidateFormat (ActionNode - code generation)
4. CheckDuplicate (ActionNode - code generation)
5. Decision: IsValid? (DecisionNode - logic generation)
6. ExtractLineItems (ActionNode - code generation)
7. CalculateTotals (ActionNode - code generation)
8. Decision: Amount > $1000? (DecisionNode - logic generation)
9. CheckBudgetCompliance (ActionNode - code generation)
10. Decision: IsCompliant? (DecisionNode - logic generation)
11. GetApprovalRequired (ActionNode - code generation)
12. SendNotification (ActionNode - code generation)
13. UpdateDatabase (ActionNode - code generation)
14. GenerateReport (ActionNode - code generation)
15. End
```

**Breakdown**:
- ActionNodes: 11 nodos (73%)
- DecisionNodes: 3 nodos (20%)
- Start/End: 2 nodos (7%)

---

## Estimación de Tokens por Nodo

### ActionNode (Code Generation)

**Input tokens por ActionNode**:
```
- System prompt (executor instructions): 500 tokens
- Node definition (name, description, inputs, outputs): 200 tokens
- Context from workflow: 300 tokens
- Previous nodes context (for dependencies): 400 tokens
- Chain-of-Work history: 200 tokens
- Examples/templates: 300 tokens
---
Total INPUT: ~1,900 tokens por ActionNode
```

**Output tokens por ActionNode**:
```
- Generated Python code: 300-800 tokens (avg 500 tokens)
- Explanation/comments: 100 tokens
- Error handling code: 100 tokens
- Return statement structure: 50 tokens
---
Total OUTPUT: ~750 tokens por ActionNode
```

### DecisionNode (Logic Generation)

**Input tokens por DecisionNode**:
```
- System prompt: 400 tokens
- Node definition: 150 tokens
- Context: 250 tokens
- Available context variables: 200 tokens
- Condition examples: 200 tokens
---
Total INPUT: ~1,200 tokens por DecisionNode
```

**Output tokens por DecisionNode**:
```
- Condition logic (Python expression): 100 tokens
- Explanation: 100 tokens
---
Total OUTPUT: ~200 tokens por DecisionNode
```

### Start/End Nodes
- No requieren generación de código
- Solo metadata estructural

---

## Cálculo por Workflow Completo

### Tokens Totales (15 nodos)

**Input Tokens**:
```
ActionNodes:     11 × 1,900 = 20,900 tokens
DecisionNodes:    3 × 1,200 =  3,600 tokens
Overhead (workflow parsing, validation): 1,500 tokens
---
TOTAL INPUT: 26,000 tokens
```

**Output Tokens**:
```
ActionNodes:     11 × 750 = 8,250 tokens
DecisionNodes:    3 × 200 =   600 tokens
Workflow summary/metadata:      150 tokens
---
TOTAL OUTPUT: 9,000 tokens
```

**Total Tokens**: 26,000 (input) + 9,000 (output) = **35,000 tokens**

---

## Costos por Modelo

### GPT-5 (Flagship)
```
Input:  26,000 tokens × $1.25/1M = $0.0325
Output:  9,000 tokens × $10.00/1M = $0.0900
---
TOTAL: $0.1225 por workflow (~12.3 centavos)
```

### GPT-5-Codex (Optimizado para código)
```
Input:  26,000 tokens × $1.25/1M = $0.0325
Output:  9,000 tokens × $10.00/1M = $0.0900
---
TOTAL: $0.1225 por workflow (~12.3 centavos)
```
*Mismo precio que GPT-5, pero optimizado para código*

### GPT-5-mini (Balance)
```
Input:  26,000 tokens × $0.25/1M = $0.0065
Output:  9,000 tokens × $2.00/1M = $0.0180
---
TOTAL: $0.0245 por workflow (~2.5 centavos)
```
**5x más barato que GPT-5**

### GPT-4.1 (Smart)
```
Input:  26,000 tokens × $2.00/1M = $0.0520
Output:  9,000 tokens × $8.00/1M = $0.0720
---
TOTAL: $0.1240 por workflow (~12.4 centavos)
```
*Similar a GPT-5, sin reasoning tokens*

### GPT-4.1 mini (Fast)
```
Input:  26,000 tokens × $0.40/1M = $0.0104
Output:  9,000 tokens × $1.60/1M = $0.0144
---
TOTAL: $0.0248 por workflow (~2.5 centavos)
```
**5x más barato que GPT-5**

### 4o mini (Budget)
```
Input:  26,000 tokens × $0.15/1M = $0.0039
Output:  9,000 tokens × $0.60/1M = $0.0054
---
TOTAL: $0.0093 por workflow (~0.9 centavos)
```
**13x más barato que GPT-5**

---

## Comparativa de Costos

| Modelo | Costo/Workflow | Relativo a GPT-5 | Calidad Esperada |
|--------|---------------|------------------|------------------|
| **4o mini** | $0.0093 | 1x (baseline) | ⭐⭐ Básica |
| **GPT-5-mini** | $0.0245 | 2.6x | ⭐⭐⭐ Buena |
| **GPT-4.1 mini** | $0.0248 | 2.7x | ⭐⭐⭐ Buena |
| **GPT-5-Codex** | $0.1225 | 13.2x | ⭐⭐⭐⭐⭐ Excelente |
| **GPT-5** | $0.1225 | 13.2x | ⭐⭐⭐⭐⭐ Excelente |
| **GPT-4.1** | $0.1240 | 13.3x | ⭐⭐⭐⭐ Muy buena |

---

## Proyecciones de Volumen

### Scenario 1: Desarrollo/Testing (10 workflows/día)
```
4o mini:       $0.093/día  = $2.79/mes
GPT-5-mini:    $0.245/día  = $7.35/mes
GPT-4.1 mini:  $0.248/día  = $7.44/mes
GPT-5-Codex:   $1.225/día  = $36.75/mes
GPT-5:         $1.225/día  = $36.75/mes
```

### Scenario 2: Producción Light (100 workflows/día)
```
4o mini:       $0.93/día   = $27.90/mes
GPT-5-mini:    $2.45/día   = $73.50/mes
GPT-4.1 mini:  $2.48/día   = $74.40/mes
GPT-5-Codex:   $12.25/día  = $367.50/mes
GPT-5:         $12.25/día  = $367.50/mes
```

### Scenario 3: Producción Medium (500 workflows/día)
```
4o mini:       $4.65/día   = $139.50/mes
GPT-5-mini:    $12.25/día  = $367.50/mes
GPT-4.1 mini:  $12.40/día  = $372.00/mes
GPT-5-Codex:   $61.25/día  = $1,837.50/mes
GPT-5:         $61.25/día  = $1,837.50/mes
```

### Scenario 4: Producción High (2000 workflows/día)
```
4o mini:       $18.60/día  = $558.00/mes
GPT-5-mini:    $49.00/día  = $1,470.00/mes
GPT-4.1 mini:  $49.60/día  = $1,488.00/mes
GPT-5-Codex:   $245.00/día = $7,350.00/mes
GPT-5:         $245.00/día = $7,350.00/mes
```

---

## Optimizaciones con Caché (Phase 2)

### CachedExecutor Strategy

Cuando un workflow similar ya existe, podemos cachear:
- System prompts (siempre iguales)
- Examples/templates (siempre iguales)
- Workflow structure (si es template reutilizable)

**Estimación de caché**:
- Cacheable: ~40% del input (10,400 tokens)
- Non-cacheable: ~60% del input (15,600 tokens)

### Costos con Caché (70% workflows use cached)

#### GPT-5-Codex con Caché
**Primera generación** (30% workflows):
```
Input:  26,000 × $1.25/1M = $0.0325
Output:  9,000 × $10.00/1M = $0.0900
Total: $0.1225
```

**Con caché** (70% workflows):
```
Cached input:     10,400 × $0.13/1M = $0.0014
Non-cached input: 15,600 × $1.25/1M = $0.0195
Output:            9,000 × $10.00/1M = $0.0900
Total: $0.1109
```

**Promedio ponderado**:
```
(30% × $0.1225) + (70% × $0.1109) = $0.1144
Ahorro: 6.6% vs. sin caché
```

#### GPT-5-mini con Caché
**Primera generación** (30%):
```
Total: $0.0245
```

**Con caché** (70%):
```
Cached input:     10,400 × $0.03/1M = $0.0003
Non-cached input: 15,600 × $0.25/1M = $0.0039
Output:            9,000 × $2.00/1M = $0.0180
Total: $0.0222
```

**Promedio ponderado**:
```
(30% × $0.0245) + (70% × $0.0222) = $0.0229
Ahorro: 6.5% vs. sin caché
```

**Nota**: El ahorro con caché es relativamente bajo (~6-7%) porque la mayoría del costo está en el output, no el input.

---

## Estrategia Híbrida (Recomendada)

### Usar diferentes modelos según complejidad del nodo

**Nodos Simples** (40% de ActionNodes):
- Operaciones CRUD básicas
- Validaciones simples
- Transformaciones directas
- **Modelo**: `4o mini` ($0.0093 por nodo)

**Nodos Medium** (40% de ActionNodes):
- Lógica de negocio estándar
- Parsing/extraction con reglas
- Cálculos con validaciones
- **Modelo**: `GPT-5-mini` ($0.0245 por nodo)

**Nodos Complejos** (20% de ActionNodes):
- Algoritmos custom
- Integrations complejas
- Error handling avanzado
- **Modelo**: `GPT-5-Codex` ($0.1225 por nodo)

**DecisionNodes** (siempre lógica simple):
- **Modelo**: `GPT-5-mini` ($0.0082 por nodo)

### Cálculo Workflow Híbrido (15 nodos)

```
ActionNodes simples:    4 × $0.0093  = $0.0372  (4o mini)
ActionNodes medium:     5 × $0.0245  = $0.1225  (GPT-5-mini)
ActionNodes complejos:  2 × $0.1225  = $0.2450  (GPT-5-Codex)
DecisionNodes:          3 × $0.0082  = $0.0246  (GPT-5-mini)
---
TOTAL: $0.4293 por workflow (~43 centavos)
```

**Wait, esto es MÁS caro porque estoy calculando mal...**

Déjame recalcular correctamente:

---

## Recalculo Correcto: Costo por Nodo Individual

### GPT-5-Codex por ActionNode
```
Input:  1,900 tokens × $1.25/1M = $0.002375
Output:   750 tokens × $10.00/1M = $0.007500
---
TOTAL: $0.009875 por ActionNode (~1 centavo)
```

### GPT-5-mini por ActionNode
```
Input:  1,900 tokens × $0.25/1M = $0.000475
Output:   750 tokens × $2.00/1M = $0.001500
---
TOTAL: $0.001975 por ActionNode (~0.2 centavos)
```

### 4o mini por ActionNode
```
Input:  1,900 tokens × $0.15/1M = $0.000285
Output:   750 tokens × $0.60/1M = $0.000450
---
TOTAL: $0.000735 por ActionNode (~0.07 centavos)
```

### GPT-5-mini por DecisionNode
```
Input:  1,200 tokens × $0.25/1M = $0.000300
Output:   200 tokens × $2.00/1M = $0.000400
---
TOTAL: $0.000700 por DecisionNode (~0.07 centavos)
```

### Workflow Híbrido Corregido (15 nodos)

```
ActionNodes simples:    4 × $0.000735 = $0.00294  (4o mini)
ActionNodes medium:     5 × $0.001975 = $0.00988  (GPT-5-mini)
ActionNodes complejos:  2 × $0.009875 = $0.01975  (GPT-5-Codex)
DecisionNodes:          3 × $0.000700 = $0.00210  (GPT-5-mini)
---
TOTAL: $0.03467 por workflow (~3.5 centavos)
```

**Ahorro vs. GPT-5-Codex puro**: $0.1225 - $0.03467 = **$0.0878 (72% ahorro)**

---

## Conclusión Final

### Costo por Workflow de 15 Nodos (Generation)

| Estrategia | Costo/Workflow | Proyección (500 workflows/día) |
|-----------|---------------|-------------------------------|
| **Solo 4o mini** | $0.0093 | $139.50/mes |
| **Solo GPT-5-mini** | $0.0245 | $367.50/mes |
| **Solo GPT-5-Codex** | $0.1225 | $1,837.50/mes |
| **Híbrida Smart** | $0.0347 | $520.50/mes |

### Recomendación para NOVA Phase 2

**Estrategia Híbrida Smart**:
1. Clasificar complejidad de cada nodo (simple/medium/complex)
2. Usar `4o mini` para nodos simples (CRUD, validations)
3. Usar `GPT-5-mini` para nodos medium (business logic)
4. Usar `GPT-5-Codex` para nodos complejos (algorithms, integrations)
5. **Resultado**: ~$0.03-0.04 por workflow (~3.5 centavos)

**Proyección realista**:
- 500 workflows/día × $0.0347 = **$17.35/día = $520.50/mes**
- 2000 workflows/día × $0.0347 = **$69.40/día = $2,082/mes**

**vs. Solo GPT-5-Codex**:
- 500 workflows/día: $1,837.50/mes (**3.5x más caro**)
- 2000 workflows/día: $7,350/mes (**3.5x más caro**)

---

## Próximos Pasos

1. **Phase 1**: Validar estimaciones de tokens con workflows reales
2. **Phase 2**: Implementar clasificador de complejidad de nodos
3. **Phase 2**: A/B test entre modelos para validar calidad
4. **Phase 2**: Monitorear métricas: tokens/nodo, éxito/fallo, tiempo
5. **Optimización**: Ajustar estrategia híbrida según datos reales
