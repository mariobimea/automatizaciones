# Migración de EasyOCR a Google Cloud Vision API

**Fecha**: 2025-01-17
**Razón**: Simplificar generación de código por LLM y mejorar precisión OCR
**Estado**: 🚧 EN PROGRESO

---

## Contexto

### Problema con EasyOCR

- ❌ **API compleja**: LLM genera código incorrecto frecuentemente
  - Requiere inicializar `Reader(['es', 'en'], gpu=False)`
  - Parsing manual de resultados `readtext()`
  - Manejo de coordenadas y confidencias
- ❌ **Template pesado**: 22.4 GB (con PyTorch + modelos pre-descargados)
- ❌ **Cold start lento**: 2-5 minutos para cargar modelos
- ❌ **Costo E2B alto**: $3.60-$9 por ejecución (template grande)
- ⚠️ **Precisión aceptable**: 83% promedio, 95% en campos críticos

### Solución: Google Cloud Vision API

- ✅ **API simple**: 1 función call → texto extraído
- ✅ **Template ligero**: ~1-2 GB (sin PyTorch ni modelos)
- ✅ **Cold start rápido**: <30 segundos
- ✅ **Costo E2B normal**: ~$0.10 por ejecución
- ✅ **Mejor precisión**: 98% promedio
- ✅ **Costo OCR bajo**: $1.50 / 1,000 páginas = $4.50/mes para 3,000 facturas

**Trade-off aceptado**: Costo de $4.50/mes en API externa vs template pesado y código difícil de generar

---

## Plan de Migración

### ✅ Fase 1: Documentación y Template

- [x] Crear documentación completa de Google Cloud Vision API
  - `/nova-rag/knowledge/official_docs/google_vision_ocr.md`
- [x] Crear nuevo template E2B V3 (sin EasyOCR)
  - `/nova/e2b-v3-vision.Dockerfile`
- [ ] Deprecar template V2 (con EasyOCR)
  - Mantener `e2b-v2.Dockerfile` por compatibilidad pero marcar como DEPRECATED

### 🚧 Fase 2: Configuración Google Cloud

- [ ] Crear proyecto en Google Cloud Console
- [ ] Habilitar Vision API
- [ ] Crear service account con rol "Cloud Vision API User"
- [ ] Descargar JSON credentials
- [ ] Configurar credenciales en Railway
  - Variable de entorno: `GCP_SERVICE_ACCOUNT_JSON`
  - Valor: Contenido del JSON (inline, no path)

### 🔜 Fase 3: Actualizar Código

- [ ] Actualizar `KnowledgeManager` para cargar docs de Vision API
  - Reemplazar `easyocr` → `google_vision` en integration dependencies
- [ ] Actualizar `CodeGenerator` prompts
  - Cambiar ejemplos de EasyOCR → Google Cloud Vision
- [ ] Actualizar `tools.py` description
  - Reemplazar "EasyOCR" → "Google Cloud Vision API"
- [ ] Marcar EasyOCR docs como DEPRECATED
  - Mover `/nova-rag/knowledge/official_docs/easyocr_official.md` → `_deprecated/`

### 🔜 Fase 4: Testing

- [ ] Build template V3 en E2B
  - `e2b template build --dockerfile e2b-v3-vision.Dockerfile --name "nova-engine-v3"`
- [ ] Probar workflow de invoice processing con Vision API
  - Usar `invoice_workflow_v5_multi_model.json`
  - Verificar que LLM genera código correcto
- [ ] Comparar tiempos de ejecución
  - V2 (EasyOCR): Cold start + OCR
  - V3 (Vision API): Cold start + API call
- [ ] Validar precisión OCR
  - Comparar campos extraídos: invoice_number, date, total, CIF

### 🔜 Fase 5: Deployment

- [ ] Actualizar workflow definitions para usar template V3
  - Cambiar `template_id` en workflows
- [ ] Deploy a producción (Railway)
- [ ] Monitorear costos Google Cloud Vision API
  - Configurar alertas de billing
  - Target: <$10/mes para MVP

### 🔜 Fase 6: Documentación Final

- [ ] Actualizar `/documentacion/ARQUITECTURA.md`
  - Cambiar sección OCR: EasyOCR → Google Cloud Vision
- [ ] Actualizar `/documentacion/futuro/OCR-MEJORAS.md`
  - Marcar "Modelo Híbrido" como implementado
  - Actualizar benchmarks con Vision API
- [ ] Actualizar `E2B_TEMPLATE_V2_OCR.md`
  - Marcar como DEPRECATED
  - Agregar link a nueva guía V3
- [ ] Crear `E2B_TEMPLATE_V3_VISION.md`
  - Guía de uso de template V3 con Vision API

---

## Cambios en Código

### Antes (EasyOCR)

```python
# Código que el LLM debe generar (COMPLEJO)
import easyocr
import fitz

# Inicializar EasyOCR
reader = easyocr.Reader(['es', 'en'], gpu=False)

# Abrir PDF
doc = fitz.open(pdf_path)
page = doc[0]
pix = page.get_pixmap(dpi=300)
img_bytes = pix.tobytes("png")

# OCR
results = reader.readtext(img_bytes, detail=1)

# Parsing manual
text = ' '.join([item[1] for item in results])
avg_confidence = sum([item[2] for item in results]) / len(results)

doc.close()
context['extracted_text'] = text
context['ocr_confidence'] = avg_confidence
```

### Después (Google Cloud Vision)

```python
# Código que el LLM debe generar (SIMPLE)
from google.cloud import vision
import fitz
import os
import json

# Inicializar Vision API
creds_json = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
if creds_json:
    from google.oauth2 import service_account
    creds_dict = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    client = vision.ImageAnnotatorClient(credentials=credentials)
else:
    client = vision.ImageAnnotatorClient()

# Abrir PDF
doc = fitz.open(pdf_path)
page = doc[0]
pix = page.get_pixmap(dpi=300)
img_bytes = pix.tobytes("png")
doc.close()

# OCR (1 línea)
image = vision.Image(content=img_bytes)
response = client.document_text_detection(image=image)

# Extraer texto (1 línea)
text = response.full_text_annotation.text

context['extracted_text'] = text
```

**Reducción**: ~15 líneas → ~10 líneas, y mucho más simple

---

## Configuración de Credenciales

### Opción 1: Service Account JSON inline (RECOMENDADO para E2B)

```bash
# En Railway, crear variable de entorno:
GCP_SERVICE_ACCOUNT_JSON='{
  "type": "service_account",
  "project_id": "tu-proyecto",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "vision-api@tu-proyecto.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}'
```

**En código generado**:
```python
import os
import json
from google.oauth2 import service_account
from google.cloud import vision

creds_json = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
creds_dict = json.loads(creds_json)
credentials = service_account.Credentials.from_service_account_info(creds_dict)
client = vision.ImageAnnotatorClient(credentials=credentials)
```

### Opción 2: File path (SOLO para desarrollo local)

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

```python
from google.cloud import vision

# Auto-usa GOOGLE_APPLICATION_CREDENTIALS
client = vision.ImageAnnotatorClient()
```

---

## Costos Estimados

### Antes (EasyOCR)

| Concepto | Costo |
|----------|-------|
| Template E2B (22.4 GB) | $3.60 - $9 por ejecución |
| OCR | $0 |
| **Total** | **$3.60 - $9 por workflow** |

**Para 100 facturas/día**: $360 - $900/mes 💀

### Después (Google Cloud Vision)

| Concepto | Costo |
|----------|-------|
| Template E2B (~1-2 GB) | ~$0.10 por ejecución |
| Vision API (3,000 páginas/mes) | $4.50/mes |
| **Total** | **~$0.10 por workflow + $4.50/mes fijo** |

**Para 100 facturas/día**: ~$30 + $4.50 = **$34.50/mes** ✅

**Ahorro**: ~$325 - $865/mes (92-96% reducción)

---

## Monitoreo de Costos

### Google Cloud Console

1. **Billing Reports**: Verificar costo mensual de Vision API
2. **Alertas de presupuesto**: Configurar alerta si > $20/mes
3. **Quota monitoring**: Verificar número de requests

### Railway

1. **Template size**: Verificar que V3 sea ~1-2 GB (vs 22.4 GB de V2)
2. **Execution time**: Cold start debería ser <30s (vs 2-5 min)
3. **Cost per execution**: Debería ser ~$0.10 (vs $3.60-$9)

---

## Rollback Plan

Si algo falla durante la migración:

1. **Mantener template V2 activo** hasta confirmar que V3 funciona
2. **Workflows pueden especificar template_id**
   - V2: `nova-engine-v2` (con EasyOCR)
   - V3: `nova-engine-v3` (con Vision API)
3. **Variable de feature flag** en Railway
   ```python
   USE_VISION_API = os.getenv('USE_VISION_API', 'true') == 'true'
   ```

---

## Métricas de Éxito

### Objetivos

- ✅ **Template size**: <2 GB (vs 22.4 GB)
- ✅ **Cold start**: <30s (vs 2-5 min)
- ✅ **OCR accuracy**: >95% en campos críticos (vs 95% con EasyOCR)
- ✅ **LLM success rate**: >90% de código generado correcto en primer intento
- ✅ **Cost**: <$50/mes para 3,000 facturas (vs $360-$900)

### KPIs a medir

1. **Template metrics**
   - Size: `docker images | grep nova-engine-v3`
   - Build time: `e2b template build` duration
2. **Execution metrics**
   - Cold start time (first execution)
   - OCR time (Vision API latency)
3. **Quality metrics**
   - OCR accuracy (compare extracted vs ground truth)
   - LLM code generation success rate
4. **Cost metrics**
   - E2B cost per execution
   - Vision API monthly cost

---

## Timeline

| Fase | Duración estimada | Status |
|------|-------------------|--------|
| **Fase 1**: Docs + Template | 1 hora | ✅ COMPLETADO |
| **Fase 2**: Google Cloud Setup | 30 minutos | 🔜 PENDIENTE |
| **Fase 3**: Actualizar código | 1 hora | 🔜 PENDIENTE |
| **Fase 4**: Testing | 1-2 horas | 🔜 PENDIENTE |
| **Fase 5**: Deployment | 30 minutos | 🔜 PENDIENTE |
| **Fase 6**: Docs finales | 1 hora | 🔜 PENDIENTE |

**Total**: ~5-6 horas

---

## Referencias

- **Docs Vision API**: `/nova-rag/knowledge/official_docs/google_vision_ocr.md`
- **Template V3**: `/nova/e2b-v3-vision.Dockerfile`
- **OCR Mejoras**: `/documentacion/futuro/OCR-MEJORAS.md`
- **Google Cloud Vision Pricing**: https://cloud.google.com/vision/pricing

---

**Última actualización**: 2025-01-17
**Responsable**: Mario Ferrer
**Estado**: En progreso (Fase 1 completada)
