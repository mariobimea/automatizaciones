# 🤔 Decisiones Técnicas y Alternativas

**Proyecto**: NOVA
**Propósito**: Documentar el razonamiento detrás de decisiones técnicas clave

---

## 🚀 Deployment: Railway + Hetzner

### Decisión Final
- **Railway**: FastAPI + Celery + PostgreSQL + Redis (~$10-15/mes)
- **Hetzner VM**: Docker sandbox CPX21 (~€6/mes)
- **Total**: ~$15-20/mes

### Alternativas Consideradas

#### 1. Railway + E2B Cloud Sandboxes
**Pros**:
- ✅ Servicio managed, no gestionar VM
- ✅ Firecracker microVMs (muy seguro)
- ✅ SDK Python maduro
- ✅ Inicio rápido (~150ms)

**Contras**:
- ❌ **Costo**: ~$126/mes para 1000 ejecuciones/día de 30s
- ❌ Vendor lock-in
- ❌ Overkill para MVP

**Por qué NO**: Demasiado caro para MVP. E2B está pensado para producción a escala.

#### 2. Modal.com (Serverless Python)
**Pros**:
- ✅ Python-native, muy fácil de usar
- ✅ Sandboxing incluido
- ✅ Free tier: $30/mes créditos
- ✅ Costo bajo (~$20/mes estimado)

**Contras**:
- ❌ **Alto vendor lock-in**: Código muy específico de Modal
- ❌ Menos control sobre infraestructura
- ❌ No compatible con Railway fácilmente

**Por qué NO**: Preferimos mantener flexibilidad y control. Quitar Modal después sería complicado.

#### 3. Render.com
**Pros**:
- ✅ Similar a Railway, buena DX
- ✅ PostgreSQL + Redis incluidos

**Contras**:
- ❌ Más caro (~$115/mes para mismo setup)
- ❌ Tampoco soporta Docker-in-Docker
- ❌ Peor documentación que Railway

**Por qué NO**: Railway tiene mejor DX y es más barato.

#### 4. Fly.io
**Pros**:
- ✅ Máxima flexibilidad
- ✅ Soporta múltiples regiones
- ✅ Pricing competitivo

**Contras**:
- ❌ Más técnico, curva de aprendizaje
- ❌ Configuración más compleja
- ❌ Tampoco soporta Docker-in-Docker nativamente

**Por qué NO**: Preferimos Railway por velocidad de desarrollo.

#### 5. Local + Docker Compose
**Pros**:
- ✅ **Gratis** ($0/mes)
- ✅ Docker-in-Docker funciona sin problemas
- ✅ Control total

**Contras**:
- ❌ No uptime 24/7
- ❌ Necesita ngrok para demos (~$8/mes)
- ❌ No escalable

**Por qué NO (para producción)**: Perfecto para desarrollo, pero queremos MVP en cloud desde día 1.

#### 6. AWS EC2 (t3.medium)
**Pros**:
- ✅ Auto-scaling disponible
- ✅ Ecosystem completo (Lambda, ECS, Fargate, etc.)
- ✅ Múltiples regiones globales
- ✅ 99.99% SLA

**Contras**:
- ❌ **Costo**: ~$40-50/mes (instancia + EBS + tráfico)
- ❌ Reserved Instances: ~$20/mes (aún 3-4x más caro que Hetzner)
- ❌ **Complejidad**: VPC, Security Groups, IAM, subnets
- ❌ Curva de aprendizaje mayor
- ❌ Overkill para MVP con poco tráfico

**Por qué NO**: Para Phase 1 con tráfico limitado, pagar 3-4x más por features que no usamos no tiene sentido. Auto-scaling solo vale la pena con >10,000 ejecuciones/mes.

**Cuándo reconsiderar AWS**:
- Tráfico > 10,000 ejecuciones/mes requiere auto-scaling
- Necesidad de múltiples regiones (clientes en Asia/América)
- Compliance específico (HIPAA, PCI-DSS)
- Integración con ecosystem AWS (Step Functions, EventBridge, etc.)

### Por qué Hetzner

**Razones**:
1. **Costo**: €6/mes vs $126/mes (E2B) vs $40-50/mes (AWS)
2. **Suficientemente potente**: CPX21 (3 vCPU, 4GB RAM) cubre Phase 1 y Phase 2
3. **Control total**: Configuramos Docker como queramos
4. **Simplicidad**: VM tradicional, SSH directo, sin complejidad de AWS
5. **Fácil migración**: Si después queremos E2B/AWS, solo cambiamos el cliente HTTP
6. **Aprendizaje**: Entendemos cómo funciona el sandbox

**Trade-off aceptado**:
- Gestionar una VM manualmente (pero es simple con Docker)
- Sin auto-scaling nativo (escalar verticalmente es suficiente para MVP)
- Vendor lock-in ligero (mitigado por API HTTP agnóstica)

---

## 📊 Arquitectura: Grafos vs Workflows Lineales

### Decisión Final
**Grafos con decisiones desde día 1**

### Alternativas Consideradas

#### 1. Empezar con Workflows Lineales
**Ejemplo**:
```
Start → Extract → Validate → Process → End
```

**Pros**:
- ✅ Más simple de implementar inicialmente
- ✅ Menos código boilerplate

**Contras**:
- ❌ **Requiere refactoring completo** para agregar decisiones
- ❌ No representa casos reales (siempre hay if/else)
- ❌ Limitado para workflows complejos

**Por qué NO**: Refactorizar después toma más tiempo que hacerlo bien desde el inicio.

#### 2. If/Else en Código Hardcodeado
**Ejemplo**:
```python
def process_invoice(data):
    if validate(data):
        if data.amount > 1000:
            manual_approval(data)
        else:
            auto_approve(data)
    else:
        reject(data)
```

**Pros**:
- ✅ Fácil de escribir inicialmente
- ✅ Familiar para desarrolladores

**Contras**:
- ❌ **No escalable**: Cada workflow es código custom
- ❌ Difícil de visualizar
- ❌ No se puede editar sin redesplegar
- ❌ No hay "grafo" explícito para auditoría

**Por qué NO**: Queremos workflows editables y visualizables.

### Por qué Grafos

**Razones**:
1. **Flexibilidad**: Soporta cualquier flujo (lineal, condicional, loops)
2. **Visualización**: El grafo ES el workflow, fácil de entender
3. **Editable**: Se puede modificar el grafo sin código
4. **Auditoría**: Chain of Work muestra path exacto seguido
5. **Inspiración Maisa**: Análisis de Maisa sugiere que usan grafos adaptativos

**Trade-off aceptado**: Más código boilerplate inicial, pero arquitectura preparada para el futuro.

---

## 🤖 Executors: StaticExecutor vs AI desde Día 1

### Decisión Final
**Phase 1**: Solo StaticExecutor (código hardcodeado)
**Phase 2**: CachedExecutor + AIExecutor (IA)

### Alternativa Considerada

#### Integrar IA desde Día 1
**Pros**:
- ✅ MVP más "wow factor"
- ✅ Validar hipótesis de auto-generación antes

**Contras**:
- ❌ **Complejidad**: Mucho más código y lógica
- ❌ **Costos**: LLM calls desde día 1
- ❌ **Riesgo**: Si IA no funciona bien, todo el MVP falla
- ❌ **Tiempo**: 2 semanas no es suficiente para hacerlo bien

**Por qué NO**: Queremos validar que la arquitectura de grafos funciona ANTES de agregar IA.

### Por qué Fases Separadas

**Razones**:
1. **Validación incremental**: Primero probar grafos, luego IA
2. **Debugging más fácil**: Si algo falla, sabemos qué componente es
3. **Menos variables**: MVP falla solo si Graph Engine falla, no por IA
4. **Arquitectura prepared**: Executors son intercambiables

**Trade-off aceptado**: MVP menos "sexy" inicialmente, pero más sólido.

---

## 🗄️ Base de Datos: PostgreSQL vs Alternativas

### Decisión Final
**PostgreSQL** en Railway

### Alternativas Consideradas

#### 1. MongoDB
**Pros**:
- ✅ Flexible schema (workflows como JSON)
- ✅ Queries fáciles para documentos

**Contras**:
- ❌ Menos robusto para transacciones
- ❌ No hay JSONB con índices como PostgreSQL
- ❌ Menos familiar para equipo

**Por qué NO**: PostgreSQL tiene JSONB que da misma flexibilidad + robustez.

#### 2. SQLite
**Pros**:
- ✅ Súper simple, sin servidor
- ✅ Archivo único

**Contras**:
- ❌ No escalable
- ❌ Concurrencia limitada
- ❌ Railway no lo soporta nativamente

**Por qué NO**: Queremos algo que escale sin cambiar después.

### Por qué PostgreSQL

**Razones**:
1. **JSONB nativo**: Workflows como JSON + índices eficientes
2. **Robusto**: Transacciones ACID
3. **Escalable**: Soporta alta concurrencia
4. **Railway native**: Incluido en Railway, fácil setup
5. **Ecosystem**: Alembic, SQLAlchemy bien maduros

**Trade-off aceptado**: Ninguno, PostgreSQL es la mejor opción para este caso.

---

## 🔧 Framework: FastAPI vs Alternativas

### Decisión Final
**FastAPI** + Uvicorn

### Alternativas Consideradas

#### 1. Flask
**Pros**:
- ✅ Más simple, menos boilerplate
- ✅ Más maduro, más recursos

**Contras**:
- ❌ No async nativo
- ❌ No auto-docs
- ❌ Menos moderno

**Por qué NO**: FastAPI es async nativo, crítico para Celery y sandbox HTTP calls.

#### 2. Django + DRF
**Pros**:
- ✅ Batteries included (admin, ORM, etc.)
- ✅ Muy maduro

**Contras**:
- ❌ **Overkill** para API REST simple
- ❌ Más lento que FastAPI
- ❌ Menos flexible

**Por qué NO**: No necesitamos 90% de features de Django.

### Por qué FastAPI

**Razones**:
1. **Async nativo**: Perfecto para I/O bound (HTTP calls a sandbox)
2. **Auto-docs**: OpenAPI gratis
3. **Pydantic**: Validación de datos automática
4. **Performance**: Casi tan rápido como Go/Node
5. **DX**: Type hints + autocomplete

**Trade-off aceptado**: Ninguno, FastAPI es perfecto para este caso.

---

## 📝 Resumen de Trade-offs Aceptados

| Decisión | Trade-off | Mitigación |
|----------|-----------|------------|
| Hetzner VM | Gestionar servidor | Docker simplifica, scripts de setup |
| Grafos día 1 | Más código inicial | Arquitectura preparada para futuro |
| Phase 1 sin IA | MVP menos impresionante | Validación más sólida de arquitectura |
| Monolito Railway | No microservicios aún | Código modular, fácil separar después |

---

*Última actualización: 2025-10-27*
