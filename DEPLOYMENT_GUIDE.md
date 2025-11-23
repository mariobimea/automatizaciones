# 🚀 Guía de Deployment en Railway

Esta guía te explica cómo deployar NOVA con el nuevo Semantic Code Cache en Railway.

---

## 📋 Estructura de Servicios

Necesitas deployar **2 servicios separados** en Railway:

```
Railway Project: NOVA
│
├── Servicio 1: nova-rag (Microservicio)
│   ├── Puerto: 8001
│   ├── Función: Vector store + Semantic Code Cache
│   └── URL: https://nova-rag-production.up.railway.app
│
└── Servicio 2: nova (Backend principal)
    ├── Puerto: 8000
    ├── Función: API + Workers + GraphEngine
    ├── Conecta a: nova-rag, PostgreSQL, Redis
    └── URL: https://nova-production.up.railway.app
```

---

## 🔧 Paso 1: Deployar NOVA-RAG

### 1.1 Crear Servicio en Railway

1. Ve a Railway: https://railway.app
2. Abre tu proyecto NOVA (o crea uno nuevo)
3. Click en **"New Service"** → **"GitHub Repo"**
4. Selecciona: `marioferrer/automatizaciones` (o tu repo)
5. Railway detectará que es un monorepo

### 1.2 Configurar Root Directory

**IMPORTANTE**: Railway debe apuntar a `nova-rag/` como root directory

En Railway:
1. Click en el servicio recién creado
2. Ve a **Settings** → **Service Settings**
3. En **Root Directory**, pon: `nova-rag`
4. Click **Save**

### 1.3 Variables de Entorno

En Railway, ve a **Variables** y agrega:

```bash
# No necesita variables adicionales
# ChromaDB se almacena en /knowledge/vector_db (persistente)
```

### 1.4 Verificar Build

Railway debería:
1. Detectar `requirements.txt` en `nova-rag/`
2. Instalar dependencias
3. Ejecutar: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`

**Verificar**:
```bash
# Una vez deployado, visita:
https://[tu-servicio-rag].up.railway.app/health

# Deberías ver:
{
  "status": "healthy",
  "vector_store_ready": true,
  "documents_loaded": 42  # O el número de docs cargados
}
```

### 1.5 Verificar Semantic Code Cache

```bash
# Visita:
https://[tu-servicio-rag].up.railway.app/code/stats

# Deberías ver:
{
  "total_codes": 0,  # Inicialmente vacío
  "actions": [],
  "avg_success_count": 0
}
```

✅ **NOVA-RAG deployado correctamente**

---

## 🔧 Paso 2: Deployar NOVA (Backend)

### 2.1 Crear Servicio en Railway

1. En el mismo proyecto Railway
2. Click en **"New Service"** → **"GitHub Repo"**
3. Selecciona el mismo repo
4. Railway detectará el monorepo

### 2.2 Configurar Root Directory

En Railway:
1. Click en el servicio NOVA
2. Ve a **Settings** → **Service Settings**
3. En **Root Directory**, pon: `nova`
4. Click **Save**

### 2.3 Variables de Entorno

**IMPORTANTE**: Agrega estas variables en Railway:

```bash
# === NOVA-RAG Connection ===
RAG_SERVICE_URL=https://[tu-servicio-rag].up.railway.app
# ⬆️ CRÍTICO: Apunta a tu servicio nova-rag deployado

# === Database (PostgreSQL de Railway) ===
DATABASE_URL=${{Postgres.DATABASE_URL}}  # Auto-inyectado

# === Redis (de Railway) ===
REDIS_URL=${{Redis.REDIS_URL}}  # Auto-inyectado

# === OpenAI ===
OPENAI_API_KEY=sk-...  # Tu API key

# === E2B Sandbox ===
E2B_API_KEY=e2b_...  # Tu E2B key
E2B_TEMPLATE_ID=tu-template-id

# === Semantic Cache (Opcional) ===
SEMANTIC_CACHE_ENABLED=true
SEMANTIC_CACHE_THRESHOLD=0.85
```

### 2.4 Agregar PostgreSQL y Redis

Si no los tienes:

**PostgreSQL**:
1. Click **"New Service"** → **"Database"** → **"PostgreSQL"**
2. Railway lo conectará automáticamente

**Redis**:
1. Click **"New Service"** → **"Database"** → **"Redis"**
2. Railway lo conectará automáticamente

### 2.5 Verificar Build

Railway debería:
1. Detectar `requirements.txt` en `nova/`
2. Instalar dependencias
3. Ejecutar migración: `./scripts/migrate.sh`
4. Ejecutar: `uvicorn src.api.main:app ...`

**Verificar**:
```bash
# Visita:
https://[tu-servicio-nova].up.railway.app/health

# Deberías ver:
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "rag_service": "connected"  # ✅ Conectado a nova-rag
}
```

✅ **NOVA deployado correctamente**

---

## 🔍 Paso 3: Verificar Integración

### 3.1 Test de Semantic Cache

Ejecuta un workflow que genere código:

```bash
POST https://[tu-servicio-nova].up.railway.app/workflows/{workflow_id}/execute
{
  "context": {
    "pdf_data": "JVBERi0...",
    "task": "Extract text from PDF"
  }
}
```

### 3.2 Ver Logs en Railway

**En NOVA**:
```
🚀 CachedExecutor executing...
🔍 Searching semantic code cache...
🔍 No semantic cache matches above threshold 0.85
🤖 Generating code with AI
✓ Code saved to semantic cache
```

**En NOVA-RAG**:
```
POST /code/save - 200 OK
✓ Code saved: code_1234...
```

### 3.3 Segunda Ejecución (Cache Hit)

Ejecuta el mismo workflow otra vez:

**Logs en NOVA**:
```
🔍 Searching semantic code cache...
🎯 Semantic cache HIT! Score: 0.956
✅ Semantic cached code validated successfully!
💰 Saved ~$0.003 with semantic cache
```

✅ **Semantic Cache funcionando correctamente**

---

## 📊 Paso 4: Monitorear Cache

### Ver Stats de Semantic Cache

```bash
# Stats de códigos cacheados
curl https://[tu-servicio-rag].up.railway.app/code/stats

{
  "total_codes": 15,
  "actions": ["extract_pdf", "query_db", "ocr_image"],
  "avg_success_count": 2.3
}
```

### Ver Logs en Railway

**Buscar en logs**:
- `🎯 Semantic cache HIT!` - Reutilización exitosa
- `✓ Code saved to semantic cache` - Código guardado
- `💰 Saved ~$0.003` - Ahorro de costos

---

## 🐛 Troubleshooting

### Error: "Code cache service not initialized"

**Causa**: NOVA-RAG no se inició correctamente

**Solución**:
1. Ve a logs de nova-rag en Railway
2. Busca: `✓ Code cache service initialized`
3. Si no aparece, redeploy el servicio

### Error: "RAG service unavailable"

**Causa**: Variable `RAG_SERVICE_URL` mal configurada en NOVA

**Solución**:
1. Ve a Variables en servicio NOVA
2. Verifica `RAG_SERVICE_URL` apunta a: `https://[nova-rag].up.railway.app`
3. **NO incluyas** `/code/search` en la URL base

### Error: "Semantic cache search failed"

**Causa**: Timeout o conexión perdida

**Solución**:
- El sistema hace **fallback automático a generación IA**
- No afecta la ejecución del workflow
- Revisa logs de nova-rag para errores

### ChromaDB no persiste datos

**Causa**: Railway reinicia el contenedor

**Solución**:
- Railway persiste `/knowledge/vector_db` automáticamente
- Si persiste el problema, verifica que el path sea correcto en `code_cache_service.py`

---

## 📈 Métricas Esperadas

Después de **50 ejecuciones** con workflows similares:

| Métrica | Valor Esperado |
|---------|----------------|
| Exact Cache Hit | 20-30% |
| **Semantic Cache Hit** | **40-50%** |
| AI Generation | 20-30% |
| **Total Cache Hit** | **60-80%** |
| Ahorro de Costos | ~$0.15-0.25 |
| Speedup Promedio | 10-40x |

---

## 🔐 Seguridad en Production

### ✅ Datos que se guardan en Semantic Cache

- Tipos de datos (`str`, `base64_large`, etc.)
- Estructura (schema compacto)
- Flags booleanos (`has_db_password: true`)

### ❌ Datos que NO se guardan

- Contraseñas o API keys
- Contenido de archivos
- Datos específicos de clientes
- Valores reales de credenciales

---

## 📝 Checklist de Deployment

### NOVA-RAG
- [ ] Servicio creado en Railway
- [ ] Root directory: `nova-rag`
- [ ] Build exitoso
- [ ] `/health` retorna `200 OK`
- [ ] `/code/stats` retorna stats
- [ ] Logs muestran: `✓ Code cache service initialized`

### NOVA
- [ ] Servicio creado en Railway
- [ ] Root directory: `nova`
- [ ] Variables de entorno configuradas
- [ ] `RAG_SERVICE_URL` apunta a nova-rag
- [ ] PostgreSQL conectado
- [ ] Redis conectado
- [ ] Build exitoso
- [ ] `/health` retorna `200 OK`
- [ ] Logs muestran: `✓ Semantic Code Cache client initialized`

### Integración
- [ ] Ejecutar workflow genera código
- [ ] Logs muestran: `✓ Code saved to semantic cache`
- [ ] Segunda ejecución muestra: `🎯 Semantic cache HIT!`
- [ ] `/code/stats` muestra códigos guardados

---

## 🆘 Soporte

Si algo falla:
1. Revisa logs en Railway (ambos servicios)
2. Verifica variables de entorno
3. Confirma que ChromaDB se inicializó correctamente
4. El semantic cache **no es crítico** - el sistema funciona sin él

---

**Última actualización**: 2025-11-23
