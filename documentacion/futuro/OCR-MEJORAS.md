# Mejoras de OCR para Phase 2+

**Estado actual (Phase 1)**: EasyOCR con **83% confianza promedio**
- ✅ Campos críticos (importes, CIF, totales): **95-99%**
- ⚠️ Fechas y referencias: **70-80%**
- ✅ Suficiente para MVP

---

## Opciones de Mejora de Precisión

### **Opción 1: Google Cloud Vision API** 🌟 RECOMENDADA
**Precisión**: 97-98%

**Pros**:
- Máxima precisión en facturas (98%)
- API RESTful simple de integrar
- Maneja múltiples idiomas y handwriting
- Infraestructura de Google (99.9% uptime)

**Contras**:
- **Costo**: $1.50 por 1,000 páginas
- Dependencia externa (requiere internet)
- Límites de rate (1,800 requests/min)

**Cuándo usarla**:
- Facturas críticas (importes altos)
- Cuando EasyOCR tiene confianza < 80%
- Documentos complejos con handwriting

**Implementación**:
```python
from google.cloud import vision

def ocr_google(image_path):
    client = vision.ImageAnnotatorClient()
    with open(image_path, 'rb') as f:
        image = vision.Image(content=f.read())
    response = client.text_detection(image=image)
    return response.text_annotations[0].description
```

**Costo estimado**:
- 100 facturas/día = 3,000 facturas/mes
- Costo: 3,000 / 1,000 × $1.50 = **$4.50/mes**

---

### **Opción 2: Tesseract OCR** 🔧 SELF-HOSTED
**Precisión**: 92-95%

**Pros**:
- **Gratis** y open source
- Self-hosted (sin costos recurrentes)
- Muy maduro (usado por Google)
- Alta precisión en texto impreso

**Contras**:
- Requiere dependencias del sistema (libtesseract)
- Más lento que EasyOCR (~2-3s por página)
- Template más pesado (+200MB)

**Cuándo usarla**:
- Si quieres evitar costos de APIs
- Facturas con texto impreso claro
- Necesitas 95% de precisión sin pagar

**Implementación**:
```python
import pytesseract

def ocr_tesseract(image_path):
    text = pytesseract.image_to_string(image_path, lang='spa+eng')
    data = pytesseract.image_to_data(image_path, output_type=pytesseract.Output.DICT)
    confidences = [int(c) for c in data['conf'] if c != '-1']
    avg_confidence = sum(confidences) / len(confidences)
    return text, avg_confidence
```

**Cambios necesarios en template**:
```dockerfile
# Añadir a e2b-simple.Dockerfile
RUN apt-get install -y tesseract-ocr tesseract-ocr-spa
RUN pip install pytesseract
```

---

### **Opción 3: Modelo Híbrido** 🎯 ÓPTIMO COST/PERFORMANCE
**Precisión**: 95%+ en promedio

**Estrategia**:
1. **EasyOCR primero** (gratis, rápido)
2. **Si confianza < 80%** → Google Cloud Vision API
3. **Validación posterior** con regex y reglas de negocio

**Pros**:
- Minimiza costos de API (solo casos complejos)
- Mejor relación costo/precisión
- Fallback robusto

**Contras**:
- Lógica más compleja
- Requiere configurar ambas soluciones

**Implementación**:
```python
def ocr_hybrid(image_path, threshold=0.80):
    # Intentar primero con EasyOCR (gratis)
    results = reader.readtext(image_path, detail=1)
    avg_conf = sum(conf for (_, _, conf) in results) / len(results)

    if avg_conf >= threshold:
        # Suficiente confianza, usar EasyOCR
        return extract_invoice_data(results), "easyocr"
    else:
        # Baja confianza, usar Google Vision API
        text = ocr_google(image_path)
        return extract_invoice_data_from_text(text), "google"
```

**Costo estimado**:
- Si 20% de facturas van a Google API
- 3,000 facturas/mes × 20% = 600 facturas/mes
- Costo: 600 / 1,000 × $1.50 = **$0.90/mes** 💰

---

## Validación Posterior (Aplicar en cualquier opción)

Independientemente del engine OCR, agregar validación de negocio:

### **Validación de Campos Críticos**

```python
import re

def validate_invoice_data(data):
    """Validar y corregir datos extraídos"""

    # Validar CIF/NIF español
    cif_pattern = r'^[A-Z]\d{8}$|^\d{8}[A-Z]$'
    if not re.match(cif_pattern, data.get('cif', '')):
        data['validation_errors'].append('CIF inválido')

    # Validar formato de fecha
    date_pattern = r'\d{2}/\d{2}/\d{4}'
    if not re.match(date_pattern, data.get('fecha', '')):
        data['validation_errors'].append('Fecha inválida')

    # Validar importes (deben ser números)
    try:
        total = float(data.get('total', '').replace(',', '.').replace('EUR', '').strip())
        data['total'] = total
    except ValueError:
        data['validation_errors'].append('Total inválido')

    # Calcular IVA esperado
    subtotal = data.get('subtotal', 0)
    iva_esperado = subtotal * 0.21
    iva_detectado = data.get('iva', 0)

    if abs(iva_esperado - iva_detectado) > 0.50:  # Tolerancia 50 cents
        data['validation_warnings'].append('IVA no coincide con cálculo')

    return data
```

---

## Roadmap de Implementación

### **Phase 1 (MVP)** ✅ COMPLETADO
- [x] EasyOCR básico funcionando
- [x] Template E2B con OCR
- [x] Extracción de campos clave
- **Resultado**: 83% confianza promedio, 95%+ en campos críticos

### **Phase 2 (Mejora de Precisión)**
- [ ] Implementar validación de campos con regex
- [ ] Calcular y verificar IVA automáticamente
- [ ] Detectar anomalías en importes

### **Phase 3 (Modelo Híbrido)**
- [ ] Configurar Google Cloud Vision API
- [ ] Implementar estrategia de fallback (EasyOCR → Google)
- [ ] Métricas de costo y precisión

### **Phase 4 (Optimización)**
- [ ] Analizar facturas que fallan más
- [ ] Fine-tuning de thresholds de confianza
- [ ] A/B testing entre engines

---

## Benchmark de Referencia

| Engine | Confianza Promedio | Campos Críticos | Costo/1000 | Velocidad |
|--------|-------------------|-----------------|------------|-----------|
| **EasyOCR** | 83% | 95% | $0 | 7s |
| **Tesseract** | 92% | 95% | $0 | 2-3s |
| **Google Cloud Vision** | 98% | 99% | $1.50 | 1s |
| **Modelo Híbrido** | 95% | 98% | $0.30* | 5s avg |

*Asumiendo 20% de facturas van a Google API

---

## Decisión Recomendada

**Para Phase 2**: Implementar **Modelo Híbrido**

**Razones**:
1. ✅ Mejor balance costo/precisión (95% por $0.30/1000)
2. ✅ Fallback robusto para casos complejos
3. ✅ Escalable (si crece el volumen, seguirá siendo barato)
4. ✅ No requiere cambios en template (API externa)

**Criterio de fallback sugerido**:
- Si `confianza_promedio < 75%` → Google API
- Si `campos_críticos_detectados < 5/7` → Google API
- Si `importe > 5,000 EUR` → Google API (facturas críticas)

**Resultado esperado**:
- 95% de precisión promedio
- $0.30 por 1,000 facturas
- 99% de campos críticos detectados

---

**Última actualización**: 2025-01-10
**Próxima revisión**: Después de procesar 1,000 facturas reales en Phase 1
