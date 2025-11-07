# n8n vs Código Custom con Claude Code
## Análisis Completo para Sistema de Automatización de Facturas

---

## RESUMEN EJECUTIVO

**Mi Recomendación Directa**: **CÓDIGO CUSTOM con Claude Code** para este proyecto específico.

**¿Por qué?**: n8n es EXCELENTE para automatizaciones simples, pero este proyecto tiene 3 requisitos que lo hacen inadecuado:
1. **Panel web custom con usuarios y permisos multi-tenant** (n8n no lo soporta nativamente)
2. **Lógica de validación compleja y personalizada** (terminarás escribiendo mucho código custom de todos modos)
3. **Base de datos relacional con múltiples tablas relacionadas** (n8n se vuelve muy complejo)

**PERO**: n8n puede ser útil para proyectos más simples en el futuro. Sigue leyendo para entender exactamente cuándo usar cada uno.

---

## PARTE 1: ¿Qué PUEDE hacer n8n en este proyecto?

### ✅ LO QUE N8N HACE MUY BIEN

n8n tiene **templates reales y funcionales** para procesamiento de facturas con IA:

1. **Lectura de Emails con Facturas**
   - ✅ IMAP/Gmail trigger funcionando
   - ✅ Descarga de adjuntos PDF
   - ✅ Polling automático cada X minutos
   - **Funciona perfectamente**

2. **OCR y Extracción de Datos**
   - ✅ OCR.space integration (gratis hasta 25k requests/mes)
   - ✅ Mistral OCR support (nuevo en 2025)
   - ✅ GPT-4 Vision integration para extracción inteligente
   - ✅ LlamaParse support
   - **Templates listos para usar**: Hay 106 workflows de invoice processing en la comunidad

3. **Almacenamiento Básico**
   - ✅ PostgreSQL node con soporte de transacciones
   - ✅ Google Sheets (muy fácil para prototipos)
   - ✅ Airtable
   - **Suficiente para almacenar datos extraídos**

4. **Notificaciones por Email**
   - ✅ SMTP/Gmail/SendGrid nodes
   - ✅ Plantillas de email
   - ✅ Envío automático
   - **Perfecto para notificar a proveedores**

### Ejemplo Real de Workflow en n8n (disponible ya):

```
Gmail Trigger
  ↓
Filter (solo emails con "factura")
  ↓
Download PDF Attachment
  ↓
Mistral OCR / GPT-4 Vision
  ↓
Code Node (validar NIF, calcular IVA)
  ↓
IF (válida?)
  ├─ SI → PostgreSQL Insert → Send Email to Fundación
  └─ NO → Send Email to Proveedor (error)
```

**Tiempo de desarrollo**: 2-3 días para un MVP básico
**Coste**: Gratis (self-hosted) o €20/mes (n8n Cloud)

---

## PARTE 2: ¿Qué NO PUEDE hacer n8n (o se vuelve muy complejo)?

### ❌ LIMITACIONES CRÍTICAS PARA TU PROYECTO

#### 1. **Panel Web de Usuario (CRÍTICO para tu proyecto)**

**Lo que necesitas**:
- Panel web donde usuarios loguean
- Ver facturas solo de su centro/cliente
- Visor de PDF integrado
- Editar campos extraídos
- Botones: Validar, Rechazar, Enviar a Fundación
- Dashboard con métricas
- Gestión de proveedores y trabajos

**Lo que n8n ofrece**:
- ❌ **NO tiene frontend para usuarios finales**
- ❌ La interfaz de n8n es solo para administradores del workflow
- ❌ NO puedes crear un panel personalizado dentro de n8n

**Opciones con n8n**:
1. **Form Trigger** (limitado): Solo formularios simples, no panel completo
2. **Chat Trigger** (limitado): Solo chat, no dashboard
3. **Webhook + Frontend Separado**: Tendrías que construir el frontend en código de todos modos

**Conclusión**: Si necesitas un panel web, **tendrás que programar el frontend sí o sí**, entonces pierdes gran parte de la ventaja de n8n.

#### 2. **Multi-Tenant y Permisos Complejos**

**Lo que necesitas**:
- Usuario A solo ve facturas de Centro X
- Usuario B ve facturas de todos los centros pero no puede editarlas
- Admin ve todo y puede editar

**Lo que n8n ofrece**:
- ❌ **NO tiene sistema multi-tenant nativo**
- ❌ Los roles en n8n (Admin, Editor, Viewer) son para gestionar workflows, NO para usuarios finales
- ❌ NO puedes filtrar datos por usuario en el frontend (porque no hay frontend)

**Workaround**:
- Crear workflows que reciban user_id por webhook
- Filtrar en PostgreSQL basado en ese user_id
- **PERO** sigue necesitando frontend custom para login y gestión

**Conclusión**: Multi-tenancy es un **dolor de cabeza** en n8n. Es más fácil en código.

#### 3. **Base de Datos Relacional Compleja**

**Lo que necesitas**:
```sql
facturas
  ├─ proveedor_id → proveedores
  ├─ trabajo_id → trabajos
  ├─ validado_por → usuarios
  └─ auditoria[] → logs de cambios

auditoria
  ├─ factura_id
  ├─ usuario_id
  └─ acción (validada, rechazada, editada, enviada)
```

**Lo que n8n hace bien**:
- ✅ INSERT, UPDATE, DELETE básicos
- ✅ Transacciones

**Lo que se vuelve complejo**:
- ❌ JOINs complejos entre múltiples tablas
- ❌ Queries dinámicos basados en múltiples condiciones
- ❌ Mantener consistencia referencial
- ❌ Migraciones de base de datos

**En código**:
```python
# Simple ORM query
facturas = Factura.objects.filter(
    proveedor__nif=nif,
    trabajo__activo=True,
    estado='pendiente'
).select_related('proveedor', 'trabajo')
```

**En n8n**:
- Múltiples nodos PostgreSQL
- Mucho código JavaScript custom
- Difícil de mantener y debuggear

**Conclusión**: Para bases de datos complejas, **código con ORM es mucho más limpio**.

#### 4. **Lógica de Validación Compleja**

**Lo que necesitas**:
- Validar NIF/CIF con algoritmo oficial
- Validar cálculos de IVA con tolerancias
- Detección de duplicados (hash + campos clave)
- Validación contra proveedores autorizados
- Validación de número de trabajo
- Reglas configurables por cliente

**En n8n**:
- ✅ Puedes hacer esto con **Code Node** (JavaScript)
- ⚠️ PERO vas a escribir MUCHO código JavaScript

**Ejemplo Code Node en n8n**:
```javascript
// Validar NIF
function validarNIF(nif) {
  const nieRegex = /^[XYZ]\d{7}[A-Z]$/;
  const nifRegex = /^\d{8}[A-Z]$/;
  // ... más código ...
  return true;
}

// Validar IVA
function validarIVA(base, iva_pct, iva_amt, total) {
  const calculado = base * (iva_pct / 100);
  return Math.abs(iva_amt - calculado) <= 0.01;
}

// Detectar duplicados - necesitas llamar a PostgreSQL
// ... más nodos ...
```

**En código (Python)**:
```python
# validators.py - reutilizable, testeado, mantenible
def validar_nif(nif: str) -> bool:
    # ...

def validar_iva(factura: Factura) -> ValidationResult:
    # ...

def detectar_duplicado(factura: Factura) -> bool:
    # ...
```

**Conclusión**: Si vas a escribir mucho código custom de validación, **¿para qué usar n8n?** Pierdes las ventajas.

#### 5. **Testing y Debugging**

**En n8n**:
- ⚠️ Testear workflows es manual (ejecutar y ver qué pasa)
- ⚠️ NO hay unit tests para Code Nodes
- ⚠️ Debugging es ver los datos entre nodos
- ⚠️ Si algo falla, es difícil saber dónde exactamente

**En código**:
```python
# tests/test_validators.py
def test_validar_nif_correcto():
    assert validar_nif("12345678Z") == True

def test_validar_nif_incorrecto():
    assert validar_nif("12345678A") == False

def test_validar_iva_con_tolerancia():
    factura = Factura(base=100, iva_pct=21, iva_amt=21, total=121)
    assert validar_iva(factura).is_valid == True
```

**Conclusión**: Para proyectos complejos que necesitan fiabilidad, **tests automatizados son cruciales**.

#### 6. **Escalabilidad y Performance**

**Limitaciones de n8n** (documentadas):
- ⚠️ Workflows complejos pueden exceder límites de memoria → crash
- ⚠️ Base de datos de n8n crece rápido (executions, logs)
- ⚠️ Para > 5000-10000 ejecuciones/día → necesitas PostgreSQL + Queue mode
- ⚠️ Code Nodes de Python son más lentos (usa Pyodide/WebAssembly)

**En código**:
- ✅ Control total sobre performance
- ✅ Puedes optimizar queries específicos
- ✅ Colas de trabajo (Celery) configurables
- ✅ Escalado horizontal simple

**Conclusión**: Si esperas crecer a > 1000 facturas/mes, **código custom escala mejor**.

---

## PARTE 3: Comparativa Directa por Componente

| Componente | n8n | Código Custom | Ganador |
|------------|-----|---------------|---------|
| **Lectura de emails** | ✅ Excelente (IMAP/Gmail node) | ✅ Excelente (imaplib, Graph API) | **EMPATE** |
| **OCR básico** | ✅ Muy bueno (OCR.space, Mistral) | ✅ Muy bueno (Tesseract, Textract) | **EMPATE** |
| **Extracción IA** | ✅ Excelente (GPT-4, Claude integrado) | ✅ Excelente (API directo) | **EMPATE** |
| **Validaciones simples** | ✅ Bueno (Code Node) | ✅ Excelente (Python limpio) | **Código** |
| **Validaciones complejas** | ⚠️ Posible pero tedioso | ✅ Excelente | **Código** |
| **Base de datos simple** | ✅ Bueno (PostgreSQL node) | ✅ Excelente (ORM) | **Código** |
| **Base de datos compleja** | ❌ Se vuelve caótico | ✅ Excelente | **CÓDIGO** |
| **Panel web usuario** | ❌ NO existe | ✅ Frontend custom | **CÓDIGO** |
| **Multi-tenant** | ❌ Muy difícil | ✅ Estándar | **CÓDIGO** |
| **Autenticación usuarios** | ❌ Solo admin workflows | ✅ JWT, OAuth, etc. | **CÓDIGO** |
| **Dashboard/métricas** | ❌ NO tiene | ✅ Frontend custom | **CÓDIGO** |
| **Envío emails** | ✅ Excelente (SMTP nodes) | ✅ Excelente (SMTP libs) | **EMPATE** |
| **Testing** | ❌ Manual | ✅ Automatizado | **CÓDIGO** |
| **Debugging** | ⚠️ Visual pero limitado | ✅ Completo (logs, debugger) | **Código** |
| **Escalabilidad** | ⚠️ Límites documentados | ✅ Control total | **Código** |
| **Mantenimiento** | ⚠️ Workflows grandes = caos | ✅ Código organizado | **Código** |
| **Velocidad desarrollo inicial** | ✅ 2-3 días MVP | ⚠️ 2-3 semanas MVP | **n8n** |
| **Velocidad desarrollo completo** | ⚠️ 4-6 semanas | ✅ 3-4 meses | **Código** (pero más robusto) |

**Score Final**:
- **n8n gana**: Desarrollo inicial rápido, email/OCR simple
- **Código gana**: Panel web, multi-tenant, DB compleja, testing, escalabilidad

**Para TU proyecto**: **Código custom es CLARAMENTE mejor** (necesitas 7 cosas que n8n no hace bien).

---

## PARTE 4: ¿Cuándo SÍ usar n8n? (Casos de uso ideales)

### ✅ Proyectos PERFECTOS para n8n:

#### 1. **Sincronización de Datos Simple**
```
Ejemplo: Cada vez que entra un lead en HubSpot, crear registro en Google Sheets y enviar notificación a Slack.

n8n: 10 minutos de setup
Código: 2-3 horas
```

#### 2. **Automatizaciones de Marketing**
```
Ejemplo: Leer respuestas de Typeform, segmentar por respuestas, enviar emails personalizados por SendGrid, actualizar CRM.

n8n: 30 minutos
Código: 1 día
```

#### 3. **Monitoreo y Alertas**
```
Ejemplo: Cada hora, revisar API de Stripe para pagos fallidos, enviar alertas por Telegram y crear ticket en Jira.

n8n: 20 minutos
Código: 3-4 horas
```

#### 4. **Procesamiento de Facturas SIMPLE (sin panel web)**
```
Ejemplo: Email → OCR → Google Sheets → Email a contable

n8n: 1-2 horas (con template)
Código: 1-2 días
```

#### 5. **Integraciones SaaS a SaaS**
```
Ejemplo: Slack → Notion → Trello → Discord → Airtable

n8n: Minutos (nodos pre-hechos)
Código: Días (múltiples APIs)
```

### ❌ Proyectos NO recomendados para n8n:

1. **Aplicaciones web con UI para usuarios finales** ← TU PROYECTO
2. **Sistemas multi-tenant con permisos complejos** ← TU PROYECTO
3. **Bases de datos relacionales con muchas tablas** ← TU PROYECTO
4. **Lógica de negocio muy compleja** ← TU PROYECTO (validaciones)
5. **Sistemas que requieren testing exhaustivo** ← TU PROYECTO (financiero)

---

## PARTE 5: Desarrollo con Claude Code

### ¿Por qué Claude Code cambia el juego?

**Antes** (sin Claude Code):
- Código custom = semanas de desarrollo
- n8n = días
- → n8n ganaba en velocidad

**Ahora** (con Claude Code):
- Código custom con Claude = **días de desarrollo, no semanas**
- Claude genera código completo, tests, documentación
- Claude conoce best practices
- → La ventaja de velocidad de n8n se reduce MUCHO

### Ejemplo Real: Crear el Sistema Completo

**Con n8n** (sin panel web, solo workflows):
- Día 1: Setup n8n, email trigger, OCR
- Día 2: Validaciones en Code Nodes
- Día 3: PostgreSQL storage
- Día 4: Email notifications
- **Total**: 4 días para workflows
- **PERO**: Falta el panel web (necesitas código de todos modos)

**Con Claude Code**:
- Día 1: Setup proyecto, modelos DB, email reader
- Día 2: OCR + extracción con IA
- Día 3: Motor de validación
- Día 4: API REST completo
- Día 5-7: Frontend (React) con visor PDF, tablas, filtros
- Día 8: Sistema de usuarios y permisos
- Día 9: Notificaciones email
- Día 10: Tests + deploy
- **Total**: 10 días para sistema COMPLETO con panel web

**Diferencia**: 4 días (n8n sin panel) vs 10 días (código con panel completo)
→ **6 días extra para tener un sistema 5x más potente y mantenible**

### Ventajas de Código con Claude Code:

1. **Velocidad de desarrollo mejorada**:
   - Claude genera código completo en segundos
   - Explica decisiones arquitectónicas
   - Debugging asistido

2. **Calidad del código**:
   - Best practices incluidas
   - Tests generados automáticamente
   - Código limpio y documentado

3. **Flexibilidad total**:
   - Cambios fáciles de implementar
   - Agregar features nuevas rápido
   - Refactoring asistido

4. **Aprendizaje continuo**:
   - Claude explica el código que genera
   - Aprendes mientras desarrollas
   - Mejoras tus skills de programación

---

## PARTE 6: Enfoque Híbrido (¿Lo Mejor de Ambos Mundos?)

### Opción: n8n para Workflows + Código para Panel Web

**Arquitectura**:
```
n8n (workflows):
  - Lectura de emails
  - OCR + extracción IA
  - Validaciones automáticas
  - Notificaciones
  ↓ (guarda en PostgreSQL)

Backend Custom (FastAPI):
  - API REST
  - Autenticación JWT
  - Lógica de negocio compleja
  - Permisos multi-tenant
  ↓

Frontend (React):
  - Panel de usuario
  - Visor PDF
  - Dashboard
  - Gestión
```

**Comunicación**:
- n8n escribe facturas en PostgreSQL
- Backend lee/actualiza PostgreSQL
- Frontend consume API del backend
- n8n puede exponer webhooks para triggers desde frontend

### Pros del Híbrido:
- ✅ Desarrollo rápido de workflows (n8n)
- ✅ Panel profesional (código)
- ✅ Combina ventajas de ambos

### Contras del Híbrido:
- ⚠️ **Dos sistemas que mantener** (n8n + código)
- ⚠️ **Dos deployments** (n8n server + backend + frontend)
- ⚠️ Complejidad aumentada
- ⚠️ Debugging más difícil (¿dónde está el error?)
- ⚠️ **Costes**: n8n Cloud ($20-100/mes) + servidor código

### ¿Vale la pena el híbrido?

**Para tu proyecto específico**: **NO lo recomiendo**.

**Razones**:
1. El backend tiene que replicar gran parte de la lógica de n8n de todos modos (validaciones, reglas de negocio)
2. Mantener sincronizado n8n y backend es complejo
3. Para cuando construyas el backend + frontend, agregar el email reader y OCR es trivial
4. Con Claude Code, el desarrollo full-stack es rápido

**Cuándo SÍ usar híbrido**:
- Ya tienes n8n con workflows funcionando
- Solo necesitas agregar un panel simple
- El equipo conoce muy bien n8n
- No tienes tiempo para migrar todo

---

## PARTE 7: Análisis de Costes

### Costes Totales de Propiedad (TCO) - 1 año

#### Opción A: Solo n8n (sin panel web completo)

**Desarrollo**:
- Setup workflows: 4-5 días × €150/día = €600-750
- **PERO**: Sin panel web profesional

**Infraestructura mensual**:
- n8n Cloud Starter: €20/mes × 12 = €240/año
- OCR.space comercial (si > 25k/mes): €20/mes × 12 = €240/año
- Total: **€480/año**

**O self-hosted**:
- VPS (2GB): €10/mes × 12 = €120/año
- PostgreSQL: incluido
- Total: **€120/año**

**Total primer año**: €600-750 (dev) + €120-480 (infra) = **€720-1,230**

**Limitaciones**:
- ❌ No hay panel web profesional
- ❌ No multi-tenant
- ❌ Difícil de escalar

#### Opción B: Código Custom Full-Stack con Claude Code

**Desarrollo**:
- Backend + Frontend + Tests: 10-12 días × €150/día = €1,500-1,800
- (Con Claude Code, puedes hacerlo tú mismo en 2-3 semanas)

**Infraestructura mensual**:
- VPS (4GB): €30/mes × 12 = €360/año
- PostgreSQL: incluido en VPS
- OCR Tesseract: gratis
- GPT-4 Vision (1000 facturas/mes): ~€10/mes × 12 = €120/año
- Backups: €5/mes × 12 = €60/año
- Total: **€540/año**

**Total primer año**: €1,500-1,800 (dev) + €540 (infra) = **€2,040-2,340**

**Ventajas**:
- ✅ Sistema completo profesional
- ✅ Panel web robusto
- ✅ Multi-tenant
- ✅ Escalable
- ✅ Mantenible largo plazo

#### Opción C: Híbrido (n8n + Código)

**Desarrollo**:
- Workflows n8n: 3 días × €150 = €450
- Backend + Frontend: 8 días × €150 = €1,200
- Total: **€1,650**

**Infraestructura mensual**:
- n8n Cloud: €20/mes × 12 = €240/año
- VPS para backend/frontend: €30/mes × 12 = €360/año
- OCR + IA: €10/mes × 12 = €120/año
- Total: **€720/año**

**Total primer año**: €1,650 (dev) + €720 (infra) = **€2,370**

**Problema**: Más caro que full código, más complejo de mantener.

### Comparativa de Costes

| Opción | Desarrollo | Infra Año 1 | Total Año 1 | Panel Web | Escalable |
|--------|------------|-------------|-------------|-----------|-----------|
| n8n solo | €600-750 | €120-480 | €720-1,230 | ❌ | ⚠️ |
| Código full | €1,500-1,800 | €540 | €2,040-2,340 | ✅ | ✅ |
| Híbrido | €1,650 | €720 | €2,370 | ✅ | ⚠️ |

**Si vas a hacer tú con Claude Code**:
- Código full: €540 (solo infra)
- n8n: €120-480 (infra, sin panel)
- → **Diferencia**: €60-420/año, pero con sistema 10x más potente

---

## PARTE 8: Recomendación Final Personalizada

### Para TU proyecto específico de facturas:

## 🎯 RECOMENDACIÓN: **CÓDIGO CUSTOM con Claude Code**

### Razones definitivas:

1. **Necesitas panel web profesional** (n8n no lo tiene)
2. **Multi-tenant es requisito** (n8n no lo soporta bien)
3. **Base de datos relacional compleja** (código es mucho más limpio)
4. **Sistema financiero = necesita tests** (n8n no tiene tests automatizados)
5. **Con Claude Code, desarrollo es rápido** (10-12 días vs semanas antes)
6. **Escalabilidad futura** (código escala mejor)
7. **Mantenibilidad** (código bien estructurado > workflows gigantes)

### Plan de Acción Recomendado:

#### Fase 1: MVP en 2 semanas con Claude Code

**Semana 1**:
- Setup proyecto (FastAPI + React + PostgreSQL)
- Modelos de base de datos
- Email reader (IMAP)
- OCR básico (Tesseract)
- Extracción con GPT-4 Vision
- Validaciones esenciales

**Semana 2**:
- API REST completa
- Frontend básico (login, listado, detalle)
- Sistema de notificaciones
- Tests básicos
- Deploy en VPS

**Resultado**: Sistema funcional end-to-end

#### Fase 2: Completar (2-3 semanas)

**Semana 3**:
- Motor de validación completo
- Sistema de permisos multi-tenant
- Dashboard con métricas
- Visor PDF integrado

**Semana 4**:
- Gestión de proveedores y trabajos
- Histórico y auditoría
- Optimización de performance
- Tests exhaustivos

**Resultado**: Sistema profesional completo

#### Fase 3: Escalado (si necesario)

- Migrar a AWS/Azure si el volumen crece
- Agregar ML personalizado
- Integraciones adicionales

### Tu Perfil:

- ✅ Conoces n8n → Sabes cuándo es útil
- ✅ Tienes Claude Code → Desarrollo de código es rápido
- ✅ Proyecto complejo → Necesitas código
- ✅ Cliente necesita profesionalismo → Panel web necesario

**Conclusión**: Aprovecha tu conocimiento de n8n para proyectos simples futuros, pero para ESTE proyecto, **código custom con Claude Code es la opción correcta**.

---

## PARTE 9: Cuándo Reconsiderar n8n en el Futuro

### Proyectos donde n8n será tu mejor amigo:

1. **Automatización de Lead Generation**
   - Scraping web → Google Sheets → CRM → Email
   - n8n: 1 hora
   - Código: 1 día

2. **Integración de SaaS**
   - Slack + Notion + Trello + Asana + etc.
   - n8n: Minutos (nodos pre-hechos)
   - Código: Días (múltiples APIs)

3. **Procesamiento de Datos Simple**
   - CSV → Transform → API → Database
   - n8n: 30 minutos
   - Código: 2-3 horas

4. **Monitoreo y Alertas**
   - Check API every X minutes → Alert if down
   - n8n: 10 minutos
   - Código: 1 hora

5. **Social Media Automation**
   - Post to Twitter + LinkedIn + Facebook from one source
   - n8n: 15 minutos
   - Código: 2-3 horas

### Regla práctica:

**Usa n8n si**:
- ✅ Es una automatización, NO una aplicación
- ✅ No necesitas UI para usuarios finales
- ✅ Conectar servicios SaaS existentes
- ✅ Lógica simple o mediana
- ✅ No necesitas tests exhaustivos
- ✅ Quieres prototipo rápido

**Usa código si**:
- ✅ Necesitas aplicación web con UI
- ✅ Multi-tenant / permisos complejos
- ✅ Base de datos relacional compleja
- ✅ Lógica de negocio compleja
- ✅ Necesitas tests automatizados
- ✅ Escalabilidad crítica
- ✅ Tienes Claude Code (desarrollo rápido)

---

## PARTE 10: Caso de Estudio - Tu Decisión en Números

### Escenario: Empiezas con n8n, luego necesitas migrar

**Timeline**:
- Semana 1-2: Desarrollo workflows en n8n (€1,000)
- Semana 3: Cliente pide panel web (cambio de requisitos)
- Semana 4-5: Intentas hacerlo con n8n + webhooks (€1,500)
- Semana 6: Te das cuenta que necesitas código custom (€1,000 perdidos)
- Semana 7-10: Desarrollas todo en código desde cero (€3,000)
- **Total**: €5,500 + 10 semanas

### Escenario: Empiezas con Código desde el inicio

**Timeline**:
- Semana 1-2: MVP funcional con Claude Code (€1,500)
- Semana 3-4: Sistema completo (€1,500)
- Cliente feliz, sistema escalable
- **Total**: €3,000 + 4 semanas

**Ahorro**: €2,500 + 6 semanas

### Lección:

> "Elige la herramienta según los requisitos FINALES, no los iniciales."

Para este proyecto, los requisitos finales incluyen panel web → código desde el inicio.

---

## CONCLUSIÓN FINAL

### Para Sistema de Automatización de Facturas:

**✅ CÓDIGO CUSTOM con Claude Code**

**Por qué**:
1. Panel web es requisito → n8n no lo tiene
2. Multi-tenant es requisito → n8n no lo soporta
3. Base de datos compleja → código es más limpio
4. Sistema financiero → tests necesarios
5. Con Claude Code → desarrollo rápido (2-4 semanas)
6. Inversión: ~€3,000 o 2-4 semanas tu tiempo
7. Resultado: Sistema profesional, escalable, mantenible

**✅ n8n para FUTUROS proyectos simples**:
- Integraciones SaaS
- Automatizaciones sin UI
- Prototipos rápidos
- Monitoreo y alertas

### Tu Ventaja:

Conoces n8n + tienes Claude Code = **Stack perfecto para automatizaciones**

- Proyectos simples → n8n (horas)
- Proyectos complejos → código con Claude (días)
- Combinas velocidad de n8n con poder de código custom

---

## BONUS: Checklist de Decisión

Usa esta checklist para CUALQUIER proyecto futuro:

```
¿Necesitas panel web para usuarios finales?
├─ SÍ → Código custom
└─ NO → n8n puede funcionar

¿Necesitas multi-tenant / permisos complejos?
├─ SÍ → Código custom
└─ NO → n8n puede funcionar

¿Base de datos con > 5 tablas relacionadas?
├─ SÍ → Código custom
└─ NO → n8n puede funcionar

¿Lógica de negocio muy compleja?
├─ SÍ → Código custom
└─ NO → n8n puede funcionar

¿Necesitas tests automatizados extensivos?
├─ SÍ → Código custom
└─ NO → n8n puede funcionar

¿Es crítica la escalabilidad?
├─ SÍ → Código custom
└─ NO → n8n puede funcionar

Si respondiste SÍ a ≥ 2 preguntas → **Código custom**
Si todas son NO → **n8n es perfecto**
```

**Tu proyecto**: 6 SÍes → **Definitivamente código custom** ✅

---

¿Listo para empezar con el código? Puedo ayudarte a:
1. Setup del proyecto inicial
2. Arquitectura detallada
3. Generación de código con Claude
4. Plan de desarrollo semana a semana
