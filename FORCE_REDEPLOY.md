# 🚨 FORZAR REDEPLOY DE NOVA-RAG

Railway sigue usando código viejo (importa sentence_transformers).

## ✅ Verificado Localmente

El código local **SÍ tiene los cambios**:
- ✅ `vector_store.py` usa `from openai import OpenAI`
- ✅ `code_cache_service.py` usa `from openai import OpenAI`
- ✅ `requirements.txt` tiene `openai==1.54.5`
- ✅ Commits pusheados: `bf98563` y `3e8270c`

## 🔧 Soluciones

### **Opción 1: Forzar Redeploy desde Railway Dashboard**

1. Ir a https://railway.app
2. Seleccionar proyecto: **automatizaciones-production-92f8**
3. Ir a **Deployments**
4. Click en **Deploy** (botón arriba derecha)
5. Seleccionar branch: **main**
6. Click **Deploy Now**

---

### **Opción 2: Railway CLI (si tienes acceso)**

```bash
cd /Users/marioferrer/automatizaciones/nova-rag
railway login
railway link  # Selecciona el proyecto
railway up    # Fuerza redeploy
```

---

### **Opción 3: Trigger con Commit Vacío**

```bash
cd /Users/marioferrer/automatizaciones/nova-rag
git commit --allow-empty -m "chore: Force Railway redeploy"
git push origin main
```

Esto fuerza un nuevo commit → Railway debería detectarlo y redesplegar.

---

### **Opción 4: Verificar Branch de Deploy**

Railway podría estar desplegando desde otro branch (no `main`):

1. Railway Dashboard → Settings
2. Buscar: **Deploy Branch**
3. Verificar que sea: `main`
4. Si es otro branch, cambiar a `main` y guardar

---

## 📋 Checklist Post-Deploy

Después del redeploy, verificar:

```bash
# 1. Servicio arriba
curl https://automatizaciones-production-92f8.up.railway.app/health

# 2. No debe mostrar error de sentence_transformers
# Si sigue fallando, verificar logs en Railway Dashboard

# 3. Debe usar OpenAI embeddings
# Los logs deberían mostrar:
# "Using OpenAI embedding model: text-embedding-3-small"
```

---

## 🔍 Debug: Ver Logs en Railway

Si sigue fallando:

1. Railway Dashboard → Deployments
2. Click en el deployment activo
3. Ver **Build Logs** y **Deploy Logs**
4. Buscar errores o warnings

---

## ⚠️ IMPORTANTE

**ANTES** de que funcione, necesitas:
1. ✅ Configurar `OPENAI_API_KEY` en Railway Variables
2. ✅ Redeploy con código actualizado (este paso)
3. ✅ Verificar que inicie correctamente

Sin la API key, aunque redespliegue correctamente, seguirá fallando (pero con error diferente).

---

**¿Qué opción prefieres probar primero?**
