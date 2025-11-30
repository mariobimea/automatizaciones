# Setup: OpenAI Embeddings para Semantic Cache

## 📋 Cambios Realizados

### 1. ✅ CodeCacheService modificado
- **Archivo**: `nova-rag/src/core/code_cache_service.py`
- **Cambios**:
  - Reemplazado `sentence-transformers` por `OpenAI`
  - Modelo: `text-embedding-3-small` (1536 dimensiones)
  - Embeddings generados vía API de OpenAI

### 2. ✅ Requirements.txt actualizado
- **Archivo**: `nova-rag/requirements.txt`
- **Cambios**:
  - Removido: `sentence-transformers==3.3.1`
  - Agregado: `openai==1.54.5`

---

## 🚀 Próximos Pasos (MANUAL)

### **Paso 1: Configurar OPENAI_API_KEY en Railway**

```bash
# Opción A: Vía Railway CLI
cd /Users/marioferrer/automatizaciones/nova-rag
railway login
railway link  # Selecciona el proyecto nova-rag
railway variables set OPENAI_API_KEY=sk-proj-...

# Opción B: Vía Railway Dashboard
# 1. Ir a https://railway.app
# 2. Seleccionar proyecto: automatizaciones-production-92f8
# 3. Variables → Add Variable
#    Name: OPENAI_API_KEY
#    Value: sk-proj-...
```

**⚠️ IMPORTANTE**: Necesitas tu OpenAI API key. Si no la tienes:
1. Ir a https://platform.openai.com/api-keys
2. Crear nueva API key
3. Copiar el valor (empieza con `sk-proj-...`)

---

### **Paso 2: Limpiar ChromaDB (Obligatorio)**

Los embeddings antiguos (384 dim) son incompatibles con los nuevos (1536 dim).

**Opción A: Limpiar vía API (recomendado)**:
```bash
curl -X POST "https://automatizaciones-production-92f8.up.railway.app/code/clear"
```

**Opción B: Limpiar localmente**:
```bash
# Eliminar vector DB local
rm -rf /Users/marioferrer/automatizaciones/nova-rag/knowledge/vector_db

# Recrear directorio
mkdir -p /Users/marioferrer/automatizaciones/nova-rag/knowledge/vector_db
```

---

### **Paso 3: Deploy a Railway**

```bash
cd /Users/marioferrer/automatizaciones/nova-rag

# Commit cambios
git add .
git commit -m "feat: Switch to OpenAI text-embedding-3-small for semantic cache

- Replace sentence-transformers with OpenAI embeddings
- Use text-embedding-3-small (1536 dimensions)
- Better semantic similarity for code matching
- Update requirements.txt: remove sentence-transformers, add openai"

# Push a Railway (autodeploy)
git push origin main
```

**⚠️ Verifica**:
- Railway hará autodeploy
- Espera ~2-3 minutos
- Verifica logs: `railway logs`

---

### **Paso 4: Verificar Funcionamiento**

```bash
# 1. Health check
curl https://automatizaciones-production-92f8.up.railway.app/health

# 2. Stats (debería mostrar 0 codes después de limpiar)
curl https://automatizaciones-production-92f8.up.railway.app/code/stats

# 3. Ejecutar un workflow para que guarde código nuevo
# Los próximos códigos se guardarán con embeddings de OpenAI
```

---

## 📊 Beneficios Esperados

### **Mejor Similitud Semántica**

OpenAI text-embedding-3-small es MUCHO mejor capturando similitud entre:

```python
# Antes (sentence-transformers): Score bajo
"extracted_text" vs "extracted_pdf_text"  # Score: ~0.65

# Después (OpenAI): Score alto esperado
"extracted_text" vs "extracted_pdf_text"  # Score esperado: ~0.92+
```

### **Dimensiones**

| Modelo | Dimensiones | Calidad | Costo/1M tokens |
|--------|-------------|---------|----------------|
| all-MiniLM-L6-v2 | 384 | Buena | Gratis (local) |
| text-embedding-3-small | 1536 | Excelente | $0.02 |

### **Costos**

```
Embedding promedio: ~50 tokens
Costo por embedding: $0.02 / 1M * 50 = $0.000001 (~$0.001/1000 embeddings)

100 códigos guardados/mes: ~$0.10
1000 búsquedas/mes: ~$1.00

Total esperado: ~$2-3/mes
```

---

## 🔍 Testing

### **Test Local (Opcional)**

```bash
# Instalar dependencias
cd /Users/marioferrer/automatizaciones/nova-rag
pip3 install -r requirements.txt

# Configurar env
export OPENAI_API_KEY=sk-proj-...

# Limpiar cache local
rm -rf knowledge/vector_db

# Ejecutar servicio
uvicorn src.api.main:app --reload --port 8001

# En otra terminal, probar
curl -X GET http://localhost:8001/health
curl -X GET http://localhost:8001/code/stats
```

---

## ⚠️ IMPORTANTE: Incompatibilidad de Embeddings

**NO puedes mezclar embeddings**:
- ❌ ChromaDB con 384-dim + 1536-dim → ERROR
- ✅ Debes limpiar TODA la colección antes del deploy

**Si olvidas limpiar**:
```
Error: Embedding dimension mismatch
Expected: 384, Got: 1536
```

**Solución**: Ejecutar `/code/clear` endpoint.

---

## 📝 Checklist

- [ ] Configurar `OPENAI_API_KEY` en Railway
- [ ] Limpiar ChromaDB (vía API o manual)
- [ ] Commit cambios a git
- [ ] Push a Railway (autodeploy)
- [ ] Verificar deployment exitoso
- [ ] Ejecutar workflow para probar cache
- [ ] Verificar mejores scores en semantic search

---

**Última actualización**: 2025-11-30
