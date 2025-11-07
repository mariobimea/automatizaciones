# OCR Propio (Servidor Dedicado)

## ¿Qué es?

Montar tu propio servidor OCR con EasyOCR en un servidor Hetzner en lugar de usar APIs comerciales (Google Vision, AWS Textract) o ejecutar OCR dentro de E2B sandbox.

## ¿Por qué?

**Problema actual**:
- E2B con OCR pre-instalado: Template de 22.4 GB, cold start de 2-5 minutos
- Costo por ejecución: $3.60-$9 (inviable)

**Solución**: Servidor dedicado con OCR siempre activo.

## ¿Cuándo tiene sentido?

**Punto de equilibrio**: ~30,000 facturas/mes

- Google Vision: 30,000 × $0.0015 = **$45/mes**
- Servidor Hetzner: **€6/mes fijo** (sin límite de uso)

**Recomendación**: Usar Google Vision hasta llegar a este volumen.

## Arquitectura Básica

```
┌─────────────────┐
│  NOVA (Railway) │
│   E2B Sandbox   │──┐
└─────────────────┘  │
                     │ HTTP POST /ocr
                     ▼
              ┌──────────────────┐
              │ Hetzner CPX21    │
              │ FastAPI + EasyOCR│
              │ €6/mes           │
              └──────────────────┘
```

### Servidor OCR (Hetzner CPX21)

**Stack**:
- FastAPI para API REST
- EasyOCR con modelos ES+EN pre-cargados
- Systemd para auto-restart
- Nginx como reverse proxy (opcional)

**Setup básico**:
```bash
# En Hetzner CPX21 (3 vCPU, 4GB RAM)
pip install fastapi uvicorn easyocr
```

```python
# server.py
from fastapi import FastAPI, UploadFile
import easyocr

app = FastAPI()
reader = easyocr.Reader(['es', 'en'], gpu=False)  # Cargar 1 vez al arrancar

@app.post("/ocr")
async def extract_text(file: UploadFile):
    bytes = await file.read()
    results = reader.readtext(bytes, detail=0)
    return {"text": " ".join(results)}
```

### Cliente (NOVA Workflow)

```python
# En E2B sandbox (sin EasyOCR instalado)
import requests

response = requests.post(
    "https://tu-servidor.com/ocr",
    files={"file": pdf_bytes}
)
text = response.json()["text"]
context['extracted_text'] = text
```

## Costos

| Opción | Setup | Costo/factura | Costo 100k facturas/mes |
|--------|-------|---------------|-------------------------|
| **E2B con OCR** | 0 min | $3.60-$9 | $360k-$900k 💀 |
| **Google Vision** | 10 min | $0.0015 | $150 ✅ |
| **Servidor propio** | 2-3 horas | €0 (flat) | €6 ✅ |

## Ventajas

- ✅ **Costo fijo**: €6/mes sin importar volumen
- ✅ **Control total**: Optimizar modelos, fine-tuning
- ✅ **Sin límites de API**: Sin rate limits
- ✅ **Privacidad**: Datos no salen de tu infraestructura
- ✅ **Latencia predecible**: Sin cold starts

## Desventajas

- ❌ **Mantenimiento**: Updates, monitoring, backups
- ❌ **Escalabilidad**: 1 servidor = límite de throughput
- ❌ **Disponibilidad**: Si cae el servidor, OCR no funciona
- ❌ **Tiempo de setup**: Requiere configuración inicial

## Cuándo implementar

1. **Inmediato**: Usa Google Cloud Vision API ($0.0015/factura)
2. **Al llegar a 30k facturas/mes**: Considera servidor propio
3. **Al llegar a 100k facturas/mes**: Servidor propio es obligatorio (ahorro significativo)

## Referencias Técnicas

**Documentación completa de EasyOCR**: https://github.com/JaidedAI/EasyOCR

Para patrones de uso detallados, ver la versión archivada de la documentación EasyOCR que estaba en `knowledge/integrations/ocr.md` (eliminada al migrar a Google Vision).

---

**Status**: Documentación para implementación futura
**Prioridad**: Baja (solo cuando se alcance volumen crítico)
**Última actualización**: 2025-11-07
