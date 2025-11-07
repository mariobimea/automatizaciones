# Análisis Técnico: Sistema de Automatización de Facturas

## Resumen Ejecutivo

Sistema completo para automatizar la gestión de facturas recibidas por email, desde la extracción de datos hasta la validación y reenvío a cliente final (Fundación).

**Complejidad General**: Alta
**Tiempo Estimado**: 3-4.5 meses
**Equipo Recomendado**: 1-2 desarrolladores full-stack

---

## 1. Arquitectura del Sistema

```
┌─────────────────┐
│  Email Server   │
│  (IMAP/API)     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│   Email Reader Service      │
│   - Polling/Webhooks        │
│   - Download attachments    │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│   Document Processor        │
│   - OCR (scanned)           │
│   - PDF text extraction     │
│   - XML parsing             │
│   - AI extraction (ML)      │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│   Validation Engine         │
│   - Business rules          │
│   - NIF/CIF validation      │
│   - VAT calculations        │
│   - Duplicate detection     │
│   - Provider authorization  │
└────────┬────────────────────┘
         │
         ├─── OK ──────────────────┐
         │                         ▼
         │                 ┌───────────────┐
         │                 │   Database    │
         │                 │   + Storage   │
         │                 └───────┬───────┘
         │                         │
         │                         ▼
         │                 ┌───────────────┐
         │                 │   Web Panel   │
         │                 │   + API       │
         │                 └───────┬───────┘
         │                         │
         │                         ▼
         │                 ┌───────────────┐
         │                 │  Send to      │
         │                 │  Fundación    │
         │                 └───────────────┘
         │
         └─── KO ────────────────┐
                                 ▼
                         ┌───────────────┐
                         │  Notification │
                         │  Service      │
                         │  (Email)      │
                         └───────────────┘
```

---

## 2. Stack Tecnológico Recomendado

### Opción A: Python Full Stack (RECOMENDADA para MVP)

**Backend**:
- Framework: FastAPI (moderno, rápido, async) o Django (completo, admin panel)
- OCR: Tesseract (gratuito) + pytesseract
- OCR Premium: AWS Textract o Google Vision API (opcional)
- IA Extraction: OpenAI GPT-4 Vision o Anthropic Claude (para casos complejos)
- PDF: pdfplumber + PyPDF2
- XML: lxml
- Email: imaplib + email library
- Colas: Celery + Redis
- Testing: pytest

**Frontend**:
- React con TypeScript
- Tailwind CSS o Material-UI
- React Query para estado
- Visor PDF: react-pdf o pdf.js

**Base de Datos**:
- PostgreSQL (relacional, robusto)
- Redis (caché y colas)
- S3 o almacenamiento local para PDFs

**Infraestructura**:
- Docker + Docker Compose
- Nginx como reverse proxy
- Supervisor o systemd para servicios

### Opción B: Node.js Full Stack

Similar stack pero con Express/NestJS en backend. Menos recomendado por menor ecosistema de OCR/ML nativo.

### Opción C: Híbrida Low-Code

- n8n o Make.com para flujos de email y notificaciones
- Microservicios custom en Python para OCR y validación
- Supabase para backend/database
- React para frontend custom

---

## 3. Componentes Detallados

### 3.1 Email Reader Service

**Función**: Leer buzón y descargar facturas

**Tecnologías**:
- Python: `imaplib`, `email`
- Alternativa: Microsoft Graph API (si usan Office 365)
- Gmail API (si usan Gmail)

**Consideraciones**:
- Polling cada X minutos vs webhooks (si el proveedor lo permite)
- Manejo de múltiples adjuntos por email
- Filtrado por remitente, asunto, etc.
- Marcado de emails procesados
- Gestión de errores de conexión

### 3.2 Document Processor

**Función**: Extraer información de las facturas

**Flujo**:
1. Detectar tipo de archivo (PDF, XML, imagen)
2. Si es PDF:
   - Intentar extracción de texto nativo
   - Si falla o es imagen → OCR
3. Si es XML:
   - Parsing directo con estructura conocida
4. Si es imagen:
   - OCR directo

**Tecnologías OCR**:

| Solución | Coste | Precisión | Complejidad |
|----------|-------|-----------|-------------|
| Tesseract | Gratis | 70-85% | Media |
| AWS Textract | $1.50/1000 pág | 90-95% | Baja |
| Google Vision | $1.50/1000 pág | 90-95% | Baja |
| Azure Computer Vision | $1/1000 pág | 90-95% | Baja |
| GPT-4 Vision | ~$0.01-0.03/pág | 95-98% | Baja |

**Extracción Inteligente con IA**:
```python
# Ejemplo conceptual
prompt = """
Extrae de esta factura:
- Número de factura
- Proveedor y NIF
- Fecha
- Base imponible
- IVA
- Total
- Número de trabajo/referencia
"""
# Enviar imagen a GPT-4 Vision o Claude
# Obtener JSON estructurado
```

**Campos a Extraer**:
- Número de factura
- Proveedor (nombre completo)
- NIF/CIF del proveedor
- Fecha de emisión
- Base imponible
- % IVA
- Importe IVA
- Total factura
- Número de trabajo/proyecto/referencia
- Conceptos (líneas de factura)
- IBAN (si aplica)

### 3.3 Validation Engine

**Validaciones Esenciales**:

1. **Validación de NIF/CIF**:
```python
def validar_nif(nif):
    # Algoritmo oficial de validación
    # Verificar letra de control
    pass
```

2. **Validación de Cálculos**:
```python
def validar_importes(base, iva_porcentaje, iva_importe, total):
    iva_calculado = base * (iva_porcentaje / 100)
    total_calculado = base + iva_calculado

    tolerancia = 0.01  # 1 céntimo de margen
    return (
        abs(iva_importe - iva_calculado) <= tolerancia and
        abs(total - total_calculado) <= tolerancia
    )
```

3. **Validación de Proveedor Autorizado**:
```python
def validar_proveedor(nif):
    # Consultar tabla de proveedores autorizados
    return Proveedor.objects.filter(nif=nif, activo=True).exists()
```

4. **Validación de Número de Trabajo**:
```python
def validar_trabajo(numero_trabajo):
    # Verificar que existe el proyecto/trabajo
    return Trabajo.objects.filter(numero=numero_trabajo, activo=True).exists()
```

5. **Detección de Duplicados**:
```python
import hashlib

def detectar_duplicado(pdf_bytes, numero_factura, proveedor_nif):
    # Hash del archivo
    file_hash = hashlib.sha256(pdf_bytes).hexdigest()

    # Buscar por hash O por número+proveedor
    existe = Factura.objects.filter(
        Q(file_hash=file_hash) |
        Q(numero=numero_factura, proveedor__nif=proveedor_nif)
    ).exists()

    return existe
```

**Reglas de Negocio Configurables**:
```python
class ReglaValidacion:
    nombre: str
    tipo: str  # 'obligatorio', 'advertencia'
    funcion_validacion: callable
    mensaje_error: str
```

### 3.4 Base de Datos

**Modelo de Datos Principal**:

```sql
-- Tabla de proveedores
CREATE TABLE proveedores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    nif VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de trabajos/proyectos
CREATE TABLE trabajos (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(100) UNIQUE NOT NULL,
    nombre VARCHAR(255),
    cliente VARCHAR(255),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de facturas
CREATE TABLE facturas (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(100) NOT NULL,
    proveedor_id INTEGER REFERENCES proveedores(id),
    trabajo_id INTEGER REFERENCES trabajos(id),

    fecha_emision DATE,
    fecha_recepcion TIMESTAMP DEFAULT NOW(),

    base_imponible DECIMAL(10,2),
    iva_porcentaje DECIMAL(5,2),
    iva_importe DECIMAL(10,2),
    total DECIMAL(10,2),

    estado VARCHAR(20), -- 'pendiente', 'validada', 'rechazada', 'enviada'
    motivo_rechazo TEXT,

    archivo_pdf TEXT, -- ruta o URL
    archivo_original TEXT,
    file_hash VARCHAR(64),

    datos_extraidos JSONB, -- todos los campos extraídos

    email_id VARCHAR(255), -- ID del email original
    email_asunto TEXT,
    email_remitente VARCHAR(255),

    validado_por INTEGER REFERENCES usuarios(id),
    validado_en TIMESTAMP,

    enviado_fundacion BOOLEAN DEFAULT FALSE,
    enviado_fundacion_en TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de usuarios
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    nombre VARCHAR(255),
    rol VARCHAR(50), -- 'admin', 'revisor', 'consultor'
    centro VARCHAR(100), -- para filtrar por centro
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de logs/auditoría
CREATE TABLE auditoria (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER REFERENCES facturas(id),
    usuario_id INTEGER REFERENCES usuarios(id),
    accion VARCHAR(100), -- 'recibida', 'validada', 'rechazada', 'editada', 'enviada'
    detalles JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de notificaciones enviadas
CREATE TABLE notificaciones (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER REFERENCES facturas(id),
    tipo VARCHAR(50), -- 'error_proveedor', 'enviado_fundacion'
    destinatario VARCHAR(255),
    asunto TEXT,
    contenido TEXT,
    enviado BOOLEAN DEFAULT FALSE,
    enviado_en TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 3.5 Web Panel (Frontend)

**Páginas Principales**:

1. **Dashboard**:
   - Métricas: facturas recibidas hoy/semana/mes
   - Facturas pendientes de revisión
   - Tasa de validación automática
   - Errores más comunes

2. **Listado de Facturas**:
   - Tabla con filtros (estado, proveedor, fecha, trabajo)
   - Búsqueda por número, proveedor
   - Orden por fecha, importe
   - Paginación

3. **Detalle de Factura**:
   - Visualización del PDF
   - Campos extraídos (editables si necesario)
   - Histórico de cambios
   - Botones: Validar, Rechazar, Enviar a Fundación
   - Motivo de error si está KO

4. **Gestión de Proveedores**:
   - CRUD de proveedores autorizados
   - Alta/baja de proveedores

5. **Gestión de Trabajos**:
   - CRUD de trabajos/proyectos

6. **Usuarios y Permisos**:
   - Gestión de usuarios
   - Asignación de roles
   - Filtros por centro/cliente

**Control de Acceso**:
```javascript
// Ejemplo de filtrado por rol
if (usuario.rol === 'consultor') {
  facturas = facturas.filter(f => f.centro === usuario.centro);
} else if (usuario.rol === 'revisor') {
  facturas = facturas.filter(f =>
    f.centro === usuario.centro &&
    f.estado === 'pendiente'
  );
}
// admin ve todo
```

### 3.6 Notification Service

**Función**: Enviar emails automáticos a proveedores cuando hay errores

**Plantilla de Email**:
```
Asunto: Error en factura {numero_factura} - {proveedor}

Estimado proveedor,

Hemos recibido su factura número {numero_factura}, pero hemos detectado los siguientes errores que impiden su procesamiento:

{lista_errores}

Por favor, corrija estos errores y reenvíe la factura a {email_facturas}.

Gracias por su colaboración.

---
Este es un mensaje automático. Por favor, no responda a este email.
```

**Tipos de Errores Comunes**:
- NIF/CIF inválido o no autorizado
- Número de trabajo inexistente o inactivo
- Importes que no cuadran (IVA mal calculado)
- Factura duplicada
- Formato no reconocido
- Campos obligatorios faltantes

**Tecnologías**:
- SMTP (sendmail, Postfix)
- Servicios: SendGrid, AWS SES, Mailgun
- Cola de envío: Celery para no bloquear el proceso principal

### 3.7 Integración con Fundación

**Opción 1: Reenvío por Email**
```python
def enviar_a_fundacion(factura):
    msg = MIMEMultipart()
    msg['From'] = 'facturas@empresa.com'
    msg['To'] = 'facturas@fundacion.com'
    msg['Subject'] = f'Factura {factura.numero} - {factura.proveedor.nombre}'

    # Adjuntar PDF original
    with open(factura.archivo_pdf, 'rb') as f:
        attachment = MIMEApplication(f.read(), _subtype="pdf")
        attachment.add_header('Content-Disposition', 'attachment',
                            filename=f'{factura.numero}.pdf')
        msg.attach(attachment)

    # Enviar
    smtp.send_message(msg)

    # Registrar envío
    factura.enviado_fundacion = True
    factura.enviado_fundacion_en = datetime.now()
    factura.save()
```

**Opción 2: API de Fundación** (si existe):
```python
def enviar_a_fundacion_api(factura):
    data = {
        'numero': factura.numero,
        'proveedor': factura.proveedor.nif,
        'total': float(factura.total),
        'fecha': factura.fecha_emision.isoformat(),
        'pdf_url': factura.archivo_pdf_url
    }

    response = requests.post(
        'https://api.fundacion.com/facturas',
        json=data,
        headers={'Authorization': f'Bearer {API_KEY}'}
    )

    if response.status_code == 200:
        factura.enviado_fundacion = True
        factura.save()
```

---

## 4. Fases de Desarrollo

### FASE 1: MVP Funcional (6-8 semanas)

**Objetivos**:
- Sistema funcionando end-to-end con casos básicos
- Sin OCR complejo (solo PDFs con texto)

**Tareas**:
1. Setup de infraestructura (Docker, DB, servicios)
2. Email reader + descarga de adjuntos
3. Extracción de texto de PDFs nativos
4. Validaciones básicas (NIF, cálculos, duplicados)
5. Base de datos y modelos
6. API REST básica
7. Panel web con login y listado de facturas
8. Detalle de factura con visor PDF
9. Botones de validar/rechazar

**Entregables**:
- Sistema funcional para facturas en PDF con texto
- Panel web operativo
- Base de datos funcionando

### FASE 2: Automatización Completa (4-6 semanas)

**Objetivos**:
- OCR para facturas escaneadas
- Validaciones avanzadas
- Notificaciones automáticas

**Tareas**:
1. Integración de OCR (Tesseract o servicio cloud)
2. Mejora del motor de extracción con IA (opcional)
3. Motor de validación completo con reglas configurables
4. Sistema de notificaciones por email
5. Gestión de proveedores autorizados
6. Gestión de trabajos/proyectos
7. Sistema de roles y permisos multi-tenant
8. Mejoras en el panel (filtros, búsquedas, dashboard)

**Entregables**:
- OCR operativo
- Validaciones completas
- Emails automáticos funcionando
- Panel avanzado con gestión completa

### FASE 3: Integración y Optimización (3-4 semanas)

**Objetivos**:
- Integración con Fundación
- Histórico y auditoría
- Optimización de rendimiento
- Testing

**Tareas**:
1. Integración con sistema de Fundación (email o API)
2. Sistema de auditoría completo (logs de todas las acciones)
3. Dashboard con métricas y estadísticas
4. Optimización de procesamiento (colas, paralelización)
5. Testing exhaustivo (unit, integration, e2e)
6. Documentación técnica y de usuario
7. Deploy en producción

**Entregables**:
- Sistema completo en producción
- Documentación completa
- Tests automatizados

---

## 5. Puntos Críticos y Riesgos

### 🔴 CRÍTICOS

**1. Precisión del OCR/Extracción**
- **Problema**: Facturas con mala calidad pueden tener errores de extracción
- **Impacto**: Datos erróneos → validaciones incorrectas → rechazo innecesario
- **Mitigación**:
  - Combinar OCR tradicional con IA (GPT-4 Vision, Claude)
  - Validación cruzada: si OCR y texto nativo difieren, alertar
  - Permitir corrección manual fácil
  - Establecer umbral de confianza (si confianza < 80%, marcar para revisión manual)

**2. Variabilidad de Formatos**
- **Problema**: Cada proveedor tiene formato diferente de factura
- **Impacto**: Motor de extracción puede no encontrar todos los campos
- **Mitigación**:
  - Usar IA con prompts flexibles (GPT-4, Claude) en lugar de regex rígidas
  - Sistema de plantillas por proveedor como fallback
  - Aprendizaje incremental: mejorar extracción con feedback

**3. Seguridad y RGPD**
- **Problema**: Datos sensibles (NIFs, importes, documentos fiscales)
- **Impacto**: Incumplimiento legal, multas, pérdida de confianza
- **Mitigación**:
  - Encriptación de datos en reposo y en tránsito
  - Acceso basado en roles (RBAC)
  - Logs de auditoría de todos los accesos
  - Backups cifrados
  - Cumplimiento RGPD: derecho al olvido, portabilidad, etc.
  - Política de retención de datos

### 🟡 IMPORTANTES

**4. Detección de Duplicados**
- **Problema**: Proveedor reenvía factura corregida, se detecta como duplicado
- **Solución**:
  - Hash del archivo + comparación de campos clave
  - Permitir "reemplazar" versión anterior si el usuario lo indica
  - Marcar como "versión 2" en lugar de rechazar

**5. Volumen de Emails**
- **Problema**: Muchas facturas al día pueden saturar el sistema
- **Solución**:
  - Sistema de colas (Celery + Redis)
  - Procesamiento paralelo con workers
  - Monitorización de performance
  - Escalado horizontal si es necesario

**6. Disponibilidad del Buzón**
- **Problema**: Si el servidor de email cae, se pierden facturas
- **Solución**:
  - Sistema de reintentos con backoff exponencial
  - Alertas si el buzón no responde > X minutos
  - Backup de emails en otro sistema

---

## 6. Costes Estimados

### Desarrollo

**Opción 1: Freelancer/Agencia**
- Fase 1 (MVP): 6-8 semanas × €800-1500/semana = €4,800-12,000
- Fase 2 (Completo): 4-6 semanas × €800-1500/semana = €3,200-9,000
- Fase 3 (Optimización): 3-4 semanas × €800-1500/semana = €2,400-6,000
- **Total: €10,400-27,000**

**Opción 2: Desarrollador In-house**
- 3-4.5 meses a tiempo completo
- Salario según mercado local

### Infraestructura Mensual

**Opción Económica (VPS)**:
- VPS con 4GB RAM, 2 CPU: €20-40/mes (Hetzner, OVH, DigitalOcean)
- Dominio: €10/año
- Email SMTP: €5-10/mes (o gratis con IMAP)
- OCR Tesseract: gratis
- Backups: €5-10/mes
- **Total: €30-60/mes**

**Opción Cloud Escalable**:
- AWS EC2 t3.medium (2vCPU, 4GB): ~€30/mes
- RDS PostgreSQL db.t3.micro: ~€15/mes
- S3 para almacenamiento: ~€5/mes (100GB)
- AWS SES para emails: ~€0.10/1000 emails
- AWS Textract OCR: ~€1.50/1000 páginas
- Load Balancer + varios: ~€20/mes
- **Total: ~€70-100/mes + variable por uso**

**Opción Premium con IA**:
- Todo lo anterior +
- GPT-4 Vision para extracción: ~€0.01-0.03/factura
- Si procesan 1000 facturas/mes: +€10-30/mes
- **Total: €80-130/mes + variable**

### Costes por Volumen (estimaciones)

| Facturas/mes | OCR (Textract) | IA (GPT-4V) | Total aprox. |
|--------------|----------------|-------------|--------------|
| 100 | €0.15 | €1-3 | €1-3 |
| 500 | €0.75 | €5-15 | €5-15 |
| 1,000 | €1.50 | €10-30 | €10-30 |
| 5,000 | €7.50 | €50-150 | €50-150 |
| 10,000 | €15 | €100-300 | €100-300 |

---

## 7. Recomendaciones

### Para Empezar (MVP)

1. **Stack Python + FastAPI + PostgreSQL + React**
   - Rápido desarrollo
   - Buen ecosistema de librerías
   - Fácil de mantener

2. **OCR Gratuito (Tesseract) + IA (GPT-4 Vision) para casos complejos**
   - Tesseract para facturas claras (70-85% de los casos)
   - GPT-4 Vision solo para las que Tesseract falla
   - Coste controlado, buena precisión

3. **Despliegue en VPS económico**
   - Hetzner o DigitalOcean
   - Docker Compose para fácil gestión
   - Escalable más adelante si es necesario

4. **Priorizar validaciones esenciales**
   - NIF/CIF
   - Cálculos de IVA
   - Duplicados
   - Proveedor autorizado
   - Resto puede añadirse después

### Para Escalar

1. **Migrar a cloud (AWS/Azure/GCP)** cuando:
   - Volumen > 2000 facturas/mes
   - Se necesite alta disponibilidad
   - Múltiples usuarios concurrentes

2. **Implementar ML personalizado**:
   - Entrenar modelo propio con facturas históricas
   - Mayor precisión en formatos recurrentes
   - Menor coste a largo plazo

3. **API para integraciones**:
   - Fundación puede conectarse directamente
   - Otros sistemas internos pueden consultar
   - Webhooks para notificaciones en tiempo real

---

## 8. Próximos Pasos

1. **Validar requisitos con cliente**:
   - ¿Cuántas facturas/mes esperan?
   - ¿Cuántos proveedores diferentes?
   - ¿Cuántos usuarios del panel?
   - ¿Integración con Fundación por email o API?
   - ¿Ya tienen lista de proveedores autorizados?
   - ¿Formato de las facturas: mayoría escaneadas o digitales?

2. **Definir prioridades**:
   - ¿Qué validaciones son críticas vs opcionales?
   - ¿Qué nivel de automatización esperan? (¿90% automático?)
   - ¿Tolerancia a falsos positivos/negativos?

3. **Presupuesto y timeline**:
   - Confirmar presupuesto disponible
   - Fecha objetivo de lanzamiento
   - ¿MVP incremental o sistema completo?

4. **Setup inicial**:
   - Acceso al buzón de facturas (credenciales IMAP o API)
   - Muestras de facturas reales (para testing)
   - Definir reglas de validación específicas
   - Listado de proveedores autorizados

---

## 9. Alternativas y Opciones

### Opción Low-Code/No-Code

**Herramientas**:
- Zapier/Make.com para flujos de email
- DocuClipper o similar para OCR
- Airtable o Notion como base de datos
- Frontend con Retool o Softr

**Pros**:
- Desarrollo muy rápido (2-4 semanas)
- Bajo coste inicial
- Fácil de mantener sin programadores

**Contras**:
- Menos flexible
- Costes recurrentes más altos
- Limitaciones en lógica compleja
- Dependencia de servicios externos

### Solución Enterprise

**Alternativas comerciales**:
- Kofax Invoice Processing
- ABBYY FlexiCapture
- Basware Invoice Automation
- SAP Ariba

**Pros**:
- Solución probada y completa
- Soporte profesional
- Alta precisión

**Contras**:
- Muy caro (€10k-50k/año+)
- Menos personalizable
- Overkill para casos de uso mediano

---

## Conclusión

Es un proyecto **ambicioso pero totalmente viable** con las tecnologías actuales. La clave está en:

1. **Fase MVP rápida** (6-8 semanas) para validar el concepto
2. **Iteración incremental** añadiendo features según necesidad
3. **OCR híbrido** (Tesseract + IA) para balance coste/precisión
4. **Validaciones configurables** para adaptarse a cambios de reglas
5. **Panel web intuitivo** para revisión manual cuando sea necesario

**Riesgo principal**: Precisión del OCR en facturas escaneadas de baja calidad. Mitigable con IA y revisión manual.

**Coste estimado total**:
- Desarrollo: €10k-27k
- Mensual: €30-130 (según volumen y servicios)

**Timeline**: 3-4.5 meses para sistema completo.
