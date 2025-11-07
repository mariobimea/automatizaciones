# Mejoras E2B - Custom Templates

## Estado Actual (2025-10-30)

### ✅ Lo que funciona

**E2B Base Template - Producción Ready**
- SDK version: `e2b-code-interpreter==2.2.1`
- Template: Base template (sin custom configuration)
- Tests: **4/4 passing** (arithmetic, network access, error handling, context preservation)
- Network access: ✅ Confirmado (puede usar IMAP, SMTP, APIs externas)
- Startup time: ~2-3 segundos
- Costo: ~$0.06-0.09 por ejecución (2-3s)

**Código actualizado correctamente**:
- Usa `Sandbox.create()` (API sync de v2.x)
- Usa `with` context manager para cleanup automático
- Wrapped en `run_in_executor()` para mantener interface async del GraphEngine
- Compatible con Phase 1 MVP

### ⚠️ Custom Template - Pendiente de Resolver

**Objetivo**: Pre-instalar librerías de invoice processing para reducir startup time y costo

**Template creado**:
- Template ID: `j0hjup33shzpbnumir2w`
- Template Name: `nova-invoice`
- Build status: `uploaded` ✅
- Dockerfile: Creado correctamente con todas las dependencias
- Build completado exitosamente

**Librerías que debería tener**:
```dockerfile
# Sistema
tesseract-ocr (English + Spanish)
poppler-utils
libjpeg-dev, libpng-dev, libtiff-dev

# Python packages
PyPDF2==3.0.1
pdfplumber==0.10.3
pytesseract==0.3.10
pdf2image==1.16.3
Pillow==10.1.0
psycopg2-binary==2.9.9
email-validator==2.1.0
python-magic==0.4.27
requests==2.32.5
python-dateutil==2.8.2
```

**Problema actual**:
- Template se construyó y subió exitosamente a E2B
- Al crear sandbox con el template, **las librerías NO están disponibles**
- Test result: 1/9 librerías OK (solo PIL que viene pre-instalada)
- Error típico: `ModuleNotFoundError: No module named 'pytesseract'`

**Lo que se intentó**:
1. ✅ Crear template con `e2b template create` (deprecated v1)
2. ✅ Actualizar a build system v2 con `template_id` en `e2b.toml`
3. ✅ Rebuild con `e2b template build` (exitoso)
4. ✅ Docker push completado exitosamente
5. ✅ E2B confirmó build exitoso
6. ❌ Pero al usar el template, las librerías no están presentes

**Ubicación del template**:
```
/nova/e2b-templates/nova-invoice/
├── Dockerfile
└── e2b.toml
```

---

## 🔧 Posibles Causas y Soluciones

### Hipótesis 1: Template no está "activado"
**Causa**: El template se subió pero E2B no lo marcó como "ready" para uso
**Solución**:
- Verificar en dashboard de E2B: https://e2b.dev/dashboard
- Comprobar status del template con `e2b template list`
- Esperar propagación (puede tardar 5-10 minutos después del build)

### Hipótesis 2: Template ID vs Template Name
**Causa**: Estamos pasando template ID en vez de template name (o viceversa)
**Solución**:
```python
# Probar ambas opciones
Sandbox.create(template="nova-invoice")  # Por nombre
Sandbox.create(template="j0hjup33shzpbnumir2w")  # Por ID
```

### Hipótesis 3: Base image incorrecta
**Causa**: El Dockerfile usa `FROM e2bdev/code-interpreter:latest` que puede sobreescribir nuestras instalaciones
**Solución**:
- Cambiar a base image más estable
- Verificar que las capas del Dockerfile no se sobreescriban
- Considerar usar Python base image (`python:3.11-slim`) + instalar E2B runtime manualmente

### Hipótesis 4: Build cache issues
**Causa**: E2B está usando una versión cacheada anterior del template
**Solución**:
```bash
# Force rebuild sin cache
e2b template build --no-cache

# O crear nuevo template con nombre diferente
e2b template create nova-invoice-v2
```

### Hipótesis 5: Limitación de E2B free tier
**Causa**: Los custom templates con muchas librerías pueden requerir plan de pago
**Solución**:
- Verificar límites del free tier en documentación
- Contactar soporte de E2B si es necesario
- Por ahora usar base template + install on-demand

---

## 📋 Plan de Acción para Resolver

### Paso 1: Diagnóstico completo
```bash
# 1. Verificar estado actual del template
e2b template list

# 2. Obtener detalles del template
e2b template inspect j0hjup33shzpbnumir2w

# 3. Ver logs de build (si hay comando)
e2b template logs j0hjup33shzpbnumir2w
```

### Paso 2: Probar template name vs ID
```python
# En test_custom_template.py, probar ambas variantes
executor_by_name = E2BExecutor(api_key=api_key, template="nova-invoice")
executor_by_id = E2BExecutor(api_key=api_key, template="j0hjup33shzpbnumir2w")
```

### Paso 3: Rebuild desde cero
```bash
# 1. Eliminar template actual
e2b template delete j0hjup33shzpbnumir2w

# 2. Crear nuevo template desde cero
e2b template init nova-invoice-v2

# 3. Copiar Dockerfile optimizado
# 4. Build con verbose output
e2b template build --verbose

# 5. Esperar 10 minutos para propagación
# 6. Re-test
```

### Paso 4: Si todo falla, alternativas
1. **On-demand installation**: Usar base template + instalar librerías en primer nodo del workflow
2. **Pre-warm strategy**: Cachear sandboxes con librerías ya instaladas
3. **Hybrid approach**: Custom template solo para librerías pesadas (tesseract), resto on-demand

---

## 💰 Análisis de Costo - Custom vs Base

### Escenario actual (Base Template)
```
Startup: 2-3s
Execution: Variable (ej. 10s para invoice processing)
Total: 12-13s por workflow
Costo: ~$0.36-0.39 por ejecución

Con $100 credits: ~256-278 executions
```

### Escenario ideal (Custom Template funcionando)
```
Startup: 1-2s (pre-installed libs)
Execution: Variable (ej. 10s)
Total: 11-12s por workflow
Costo: ~$0.33-0.36 por ejecución

Con $100 credits: ~278-303 executions
Ahorro: ~8-9% en costo
```

### Escenario on-demand (Base + install libs en workflow)
```
Startup: 2-3s
First-time install: +15-20s (install all libs)
Execution: 10s
Total primera vez: 27-33s
Total siguientes: 12-13s (libs ya instaladas en contexto)

Problema: Cada sandbox nuevo = reinstalar libs
No viable para producción
```

**Conclusión**: El custom template valdría la pena SI funciona, pero **no es bloqueante** para MVP. Base template funciona perfectamente.

---

## ✅ Decisión para MVP (Phase 1)

**Usar Base Template** por las siguientes razones:

1. ✅ **Funciona perfectamente ahora** (4/4 tests passing)
2. ✅ **Network access confirmado** (requisito crítico para invoices)
3. ✅ **Costo aceptable** (~$0.36/ejecución = ~250 executions con free tier)
4. ✅ **No bloquea desarrollo** del workflow de facturas
5. ✅ **Podemos optimizar después** cuando tengamos workflows funcionando

**Custom template** queda como:
- 🔧 **Tech debt / mejora futura**
- 📊 **Optimización de costo** (no crítica)
- 🎯 **Priority: LOW** (solo si afecta presupuesto en producción)

---

## 📚 Referencias

**Documentación E2B**:
- Quickstart: https://e2b.dev/docs/quickstart
- Custom templates: https://e2b.dev/docs/guide/custom-sandbox
- SDK Python v2: https://github.com/e2b-dev/code-interpreter

**Archivos del proyecto**:
- Template config: `/nova/e2b-templates/nova-invoice/e2b.toml`
- Dockerfile: `/nova/e2b-templates/nova-invoice/Dockerfile`
- E2BExecutor: `/nova/src/core/executors.py`
- Tests: `/nova/examples/test_e2b_executor.py`, `/nova/examples/test_custom_template.py`

**API Key** (guardada en entorno local):
```bash
export E2B_API_KEY=e2b_a58171ddb2be1e03333222f77fa4bd1273e6f699
```

---

## 🎯 Criterio de Éxito

El custom template estará funcionando cuando:

1. ✅ Template build exitoso (YA LOGRADO)
2. ❌ Sandbox creado con template tiene todas las librerías disponibles
3. ❌ Test `test_custom_template.py` pasa 2/2 tests
4. ❌ Startup time < 2 segundos
5. ❌ Costo por ejecución < $0.35

**Última actualización**: 2025-10-30
**Estado**: PENDIENTE - No bloqueante para MVP
**Prioridad**: LOW
**Estimación**: 2-4 horas de debugging cuando sea prioritario
