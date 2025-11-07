# Entendiendo Desde Cero: Cómo Funcionan las Automatizaciones y Agentes con Código

Vamos a entender EXACTAMENTE cómo funciona todo, desde lo más básico hasta lo más avanzado.

---

## PARTE 1: AUTOMATIZACIONES ESTILO N8N CON CÓDIGO

### ¿Qué hace n8n por dentro?

n8n es básicamente un **gestor de trabajos** que:
1. Detecta eventos (triggers): "cada hora", "cuando llega un email", "cuando hay un archivo nuevo"
2. Ejecuta una secuencia de pasos (nodes)
3. Maneja errores y reintentos
4. Guarda el estado de cada ejecución
5. Te da una UI para ver qué pasó

### Replicar n8n con código: Los 5 componentes

```
┌─────────────────────────────────────────────┐
│         AUTOMATIZACIÓN CON CÓDIGO           │
├─────────────────────────────────────────────┤
│                                             │
│  1. TRIGGERS (¿Cuándo ejecutar?)           │
│     → APScheduler / Cron                    │
│                                             │
│  2. WORKERS (¿Qué ejecutar?)               │
│     → Celery / RQ                           │
│                                             │
│  3. QUEUE (¿Dónde encolar trabajos?)       │
│     → Redis / RabbitMQ                      │
│                                             │
│  4. DATABASE (¿Dónde guardar estado?)      │
│     → PostgreSQL                            │
│                                             │
│  5. MONITORING (¿Cómo ver qué pasa?)       │
│     → FastAPI + React                       │
│                                             │
└─────────────────────────────────────────────┘
```

---

## EJEMPLO COMPLETO: Sistema de Facturas (como en n8n)

Vamos a construir PASO A PASO el sistema de facturas, viendo exactamente qué hace cada parte.

### PASO 1: El Worker (El que hace el trabajo)

```python
# workers/procesar_factura.py
from celery import Celery
import imaplib
import email
from datetime import datetime
import psycopg2

# Configurar Celery (sistema de workers)
celery_app = Celery('facturas', broker='redis://localhost:6379/0')

@celery_app.task(bind=True, max_retries=3)
def procesar_factura_worker(self, email_id):
    """
    Este es el WORKER - el código que hace el trabajo real.
    Es como un "node" de n8n, pero en Python.
    """

    print(f"[WORKER] Procesando email {email_id}")

    try:
        # PASO 1: Conectar a Gmail
        print("[WORKER] Conectando a Gmail...")
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login('tu_email@gmail.com', 'tu_password')
        mail.select('INBOX')

        # PASO 2: Descargar el email
        print("[WORKER] Descargando email...")
        _, data = mail.fetch(email_id, '(RFC822)')
        email_message = email.message_from_bytes(data[0][1])

        # PASO 3: Extraer PDF adjunto
        print("[WORKER] Buscando PDF adjunto...")
        pdf_bytes = None
        for part in email_message.walk():
            if part.get_content_type() == 'application/pdf':
                pdf_bytes = part.get_payload(decode=True)
                break

        if not pdf_bytes:
            raise ValueError("No se encontró PDF en el email")

        # PASO 4: Extraer datos con OCR (simulado)
        print("[WORKER] Extrayendo datos con OCR...")
        datos_factura = extraer_datos_pdf(pdf_bytes)
        # Resultado: {"nif": "B12345678", "importe": 1500.00, "fecha": "2024-10-17"}

        # PASO 5: Validar NIF
        print("[WORKER] Validando NIF...")
        if not validar_nif(datos_factura['nif']):
            raise ValueError(f"NIF inválido: {datos_factura['nif']}")

        # PASO 6: Verificar que el proveedor está autorizado
        print("[WORKER] Verificando proveedor en base de datos...")
        conn = psycopg2.connect("dbname=facturas user=postgres")
        cur = conn.cursor()

        cur.execute(
            "SELECT id FROM proveedores WHERE nif = %s AND activo = true",
            (datos_factura['nif'],)
        )
        proveedor = cur.fetchone()

        if not proveedor:
            raise ValueError(f"Proveedor no autorizado: {datos_factura['nif']}")

        # PASO 7: Guardar factura en base de datos
        print("[WORKER] Guardando factura...")
        cur.execute("""
            INSERT INTO facturas (nif, importe, fecha, email_id, estado)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            datos_factura['nif'],
            datos_factura['importe'],
            datos_factura['fecha'],
            email_id,
            'PENDIENTE'
        ))
        factura_id = cur.fetchone()[0]
        conn.commit()

        # PASO 8: Enviar a la Fundación
        print("[WORKER] Enviando a la Fundación...")
        enviar_email_fundacion(datos_factura, factura_id)

        # PASO 9: Actualizar estado
        cur.execute(
            "UPDATE facturas SET estado = 'ENVIADA' WHERE id = %s",
            (factura_id,)
        )
        conn.commit()

        conn.close()

        print(f"[WORKER] ✅ Factura {factura_id} procesada correctamente")

        return {
            "status": "success",
            "factura_id": factura_id,
            "nif": datos_factura['nif'],
            "importe": datos_factura['importe']
        }

    except Exception as e:
        print(f"[WORKER] ❌ Error: {str(e)}")

        # Guardar el error en la base de datos
        try:
            conn = psycopg2.connect("dbname=facturas user=postgres")
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO errores_procesamiento (email_id, error, fecha)
                VALUES (%s, %s, %s)
            """, (email_id, str(e), datetime.now()))
            conn.commit()
            conn.close()
        except:
            pass

        # Reintentar hasta 3 veces (configurado en @celery_app.task)
        raise self.retry(exc=e, countdown=60)  # Reintentar en 60 segundos


# Funciones auxiliares
def extraer_datos_pdf(pdf_bytes):
    """Extrae datos del PDF con OCR"""
    # Aquí irías con Tesseract, AWS Textract, etc.
    # Por ahora simulamos
    return {
        "nif": "B12345678",
        "importe": 1500.00,
        "fecha": "2024-10-17"
    }

def validar_nif(nif):
    """Valida formato de NIF español"""
    import re
    return bool(re.match(r'^[A-Z]\d{8}$', nif))

def enviar_email_fundacion(datos, factura_id):
    """Envía email a la Fundación"""
    # Aquí irías con SMTP, SendGrid, etc.
    print(f"[EMAIL] Enviando factura {factura_id} a fundacion@ejemplo.com")
```

**¿Qué acabamos de hacer?**
- Hemos creado un WORKER que hace lo mismo que un workflow de n8n
- Cada `print()` es como ver los logs de n8n
- Los `try/except` manejan errores como lo hace n8n
- El `@celery_app.task(max_retries=3)` maneja reintentos automáticos

---

### PASO 2: El Trigger (¿Cuándo ejecutar el worker?)

```python
# triggers/email_trigger.py
from apscheduler.schedulers.background import BackgroundScheduler
import imaplib
from workers.procesar_factura import procesar_factura_worker

def revisar_emails_nuevos():
    """
    Este es el TRIGGER - revisa si hay emails nuevos cada 5 minutos.
    Es como el trigger "Email" de n8n.
    """

    print("[TRIGGER] Revisando emails nuevos...")

    # Conectar a Gmail
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login('tu_email@gmail.com', 'tu_password')
    mail.select('INBOX')

    # Buscar emails no leídos de proveedores
    _, message_numbers = mail.search(None, '(UNSEEN FROM "facturas@proveedor.com")')

    email_ids = message_numbers[0].split()

    if email_ids:
        print(f"[TRIGGER] Encontrados {len(email_ids)} emails nuevos")

        # Por cada email, encolar un worker
        for email_id in email_ids:
            print(f"[TRIGGER] Encolando worker para email {email_id}")

            # Esto encola el trabajo en Redis - NO lo ejecuta inmediatamente
            procesar_factura_worker.delay(email_id.decode())

            # delay() = "hazlo cuando haya un worker disponible"
            # apply_async() = más control (prioridad, countdown, etc)
    else:
        print("[TRIGGER] No hay emails nuevos")

    mail.close()
    mail.logout()


# Configurar el scheduler (como el cron de n8n)
scheduler = BackgroundScheduler()

# Ejecutar cada 5 minutos
scheduler.add_job(
    revisar_emails_nuevos,
    'interval',
    minutes=5,
    id='revisar_emails'
)

# Iniciar el scheduler
scheduler.start()

print("[TRIGGER] Scheduler iniciado - revisando emails cada 5 minutos")
```

**¿Qué hace esto?**
- Cada 5 minutos revisa si hay emails nuevos
- Si encuentra emails, encola un worker para cada uno
- Es exactamente como el trigger de n8n que revisa emails

---

### PASO 3: La Queue (Redis - donde se encolan los trabajos)

```python
# No necesitas escribir código para esto - Redis lo gestiona automáticamente

# Pero así es como funciona internamente:

"""
REDIS QUEUE (cola de trabajos)
==============================

Cuando haces: procesar_factura_worker.delay(email_id)

Redis guarda:
{
    "task_id": "abc-123-def-456",
    "task_name": "procesar_factura_worker",
    "args": ["email_123"],
    "kwargs": {},
    "status": "PENDING",
    "created_at": "2024-10-17T10:30:00"
}

Luego un worker lo toma:
{
    "task_id": "abc-123-def-456",
    "status": "STARTED",
    "started_at": "2024-10-17T10:30:05"
}

Si termina bien:
{
    "task_id": "abc-123-def-456",
    "status": "SUCCESS",
    "result": {"factura_id": 1234, "status": "success"},
    "completed_at": "2024-10-17T10:30:15"
}

Si falla:
{
    "task_id": "abc-123-def-456",
    "status": "FAILURE",
    "error": "NIF inválido: X12345678",
    "retry_count": 1,
    "next_retry": "2024-10-17T10:31:15"
}
"""
```

**¿Qué es Redis aquí?**
- Una base de datos en memoria ultra-rápida
- Guarda la cola de trabajos pendientes
- Guarda el estado de cada trabajo
- Es como la "execution queue" que ves en n8n

---

### PASO 4: La Base de Datos (PostgreSQL - donde guardas los datos)

```python
# database/schema.sql

-- Tabla de proveedores autorizados
CREATE TABLE proveedores (
    id SERIAL PRIMARY KEY,
    nif VARCHAR(9) UNIQUE NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de facturas procesadas
CREATE TABLE facturas (
    id SERIAL PRIMARY KEY,
    nif VARCHAR(9) NOT NULL,
    importe DECIMAL(10,2) NOT NULL,
    fecha DATE NOT NULL,
    email_id VARCHAR(255) NOT NULL,
    estado VARCHAR(50) NOT NULL, -- PENDIENTE, ENVIADA, ERROR
    pdf_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de errores (para saber qué falló)
CREATE TABLE errores_procesamiento (
    id SERIAL PRIMARY KEY,
    email_id VARCHAR(255) NOT NULL,
    error TEXT NOT NULL,
    fecha TIMESTAMP DEFAULT NOW(),
    resuelto BOOLEAN DEFAULT false
);

-- Tabla de ejecuciones (como el historial de n8n)
CREATE TABLE ejecuciones (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) UNIQUE NOT NULL,
    task_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL, -- PENDING, RUNNING, SUCCESS, FAILED
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER
);
```

**¿Para qué sirve cada tabla?**
- `proveedores`: Lista de quién puede enviarte facturas (lista blanca)
- `facturas`: Todas las facturas procesadas
- `errores_procesamiento`: Log de qué falló y por qué
- `ejecuciones`: Historial completo de cada ejecución (como n8n)

---

### PASO 5: El Monitoring (FastAPI + React - ver qué pasa)

```python
# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from datetime import datetime, timedelta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    return psycopg2.connect("dbname=facturas user=postgres")

@app.get("/api/dashboard")
def get_dashboard():
    """
    Dashboard con métricas principales
    Como la pantalla principal de n8n
    """
    conn = get_db()
    cur = conn.cursor()

    # Facturas procesadas hoy
    cur.execute("""
        SELECT COUNT(*) FROM facturas
        WHERE DATE(created_at) = CURRENT_DATE
    """)
    facturas_hoy = cur.fetchone()[0]

    # Facturas con error hoy
    cur.execute("""
        SELECT COUNT(*) FROM errores_procesamiento
        WHERE DATE(fecha) = CURRENT_DATE AND resuelto = false
    """)
    errores_hoy = cur.fetchone()[0]

    # Total facturado hoy
    cur.execute("""
        SELECT COALESCE(SUM(importe), 0) FROM facturas
        WHERE DATE(created_at) = CURRENT_DATE
    """)
    total_facturado_hoy = cur.fetchone()[0]

    # Últimas 10 ejecuciones
    cur.execute("""
        SELECT
            id, task_name, status, started_at, completed_at,
            duration_seconds, error_message
        FROM ejecuciones
        ORDER BY started_at DESC
        LIMIT 10
    """)
    ejecuciones = []
    for row in cur.fetchall():
        ejecuciones.append({
            "id": row[0],
            "task_name": row[1],
            "status": row[2],
            "started_at": row[3].isoformat() if row[3] else None,
            "completed_at": row[4].isoformat() if row[4] else None,
            "duration_seconds": row[5],
            "error_message": row[6]
        })

    conn.close()

    return {
        "facturas_hoy": facturas_hoy,
        "errores_hoy": errores_hoy,
        "total_facturado_hoy": float(total_facturado_hoy),
        "ultimas_ejecuciones": ejecuciones
    }

@app.get("/api/facturas")
def get_facturas(limit: int = 50, offset: int = 0):
    """
    Lista de facturas procesadas
    """
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            f.id, f.nif, f.importe, f.fecha, f.estado, f.created_at,
            p.nombre as proveedor_nombre
        FROM facturas f
        LEFT JOIN proveedores p ON f.nif = p.nif
        ORDER BY f.created_at DESC
        LIMIT %s OFFSET %s
    """, (limit, offset))

    facturas = []
    for row in cur.fetchall():
        facturas.append({
            "id": row[0],
            "nif": row[1],
            "importe": float(row[2]),
            "fecha": row[3].isoformat(),
            "estado": row[4],
            "created_at": row[5].isoformat(),
            "proveedor_nombre": row[6]
        })

    conn.close()

    return {"facturas": facturas}

@app.get("/api/errores")
def get_errores(solo_no_resueltos: bool = True):
    """
    Lista de errores
    Como la pestaña "Executions" de n8n filtrada por errores
    """
    conn = get_db()
    cur = conn.cursor()

    query = """
        SELECT id, email_id, error, fecha, resuelto
        FROM errores_procesamiento
    """
    if solo_no_resueltos:
        query += " WHERE resuelto = false"

    query += " ORDER BY fecha DESC LIMIT 50"

    cur.execute(query)

    errores = []
    for row in cur.fetchall():
        errores.append({
            "id": row[0],
            "email_id": row[1],
            "error": row[2],
            "fecha": row[3].isoformat(),
            "resuelto": row[4]
        })

    conn.close()

    return {"errores": errores}

@app.post("/api/errores/{error_id}/resolver")
def marcar_error_resuelto(error_id: int):
    """
    Marcar un error como resuelto
    """
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE errores_procesamiento SET resuelto = true WHERE id = %s",
        (error_id,)
    )
    conn.commit()
    conn.close()

    return {"status": "ok"}

@app.post("/api/workers/procesar-email/{email_id}")
def ejecutar_worker_manual(email_id: str):
    """
    Ejecutar worker manualmente
    Como darle a "Execute Workflow" en n8n
    """
    from workers.procesar_factura import procesar_factura_worker

    # Encolar el trabajo
    task = procesar_factura_worker.delay(email_id)

    return {
        "status": "enqueued",
        "task_id": task.id
    }
```

**¿Qué hace esta API?**
- `/api/dashboard`: Métricas principales (como n8n homepage)
- `/api/facturas`: Lista de facturas procesadas
- `/api/errores`: Qué ha fallado y por qué
- `/api/workers/procesar-email/{id}`: Ejecutar worker manualmente

---

### PASO 6: El Frontend (React - la UI)

```typescript
// frontend/src/Dashboard.tsx
import React, { useEffect, useState } from 'react';

interface DashboardData {
  facturas_hoy: number;
  errores_hoy: number;
  total_facturado_hoy: number;
  ultimas_ejecuciones: Array<{
    id: number;
    task_name: string;
    status: string;
    started_at: string;
    completed_at: string;
    duration_seconds: number;
    error_message: string | null;
  }>;
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    // Cargar datos cada 5 segundos
    const interval = setInterval(async () => {
      const response = await fetch('http://localhost:8000/api/dashboard');
      const json = await response.json();
      setData(json);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  if (!data) return <div>Cargando...</div>;

  return (
    <div className="dashboard">
      <h1>Dashboard de Facturas</h1>

      {/* Métricas principales */}
      <div className="metrics">
        <div className="metric">
          <h3>Facturas Hoy</h3>
          <p className="metric-value">{data.facturas_hoy}</p>
        </div>

        <div className="metric">
          <h3>Errores Hoy</h3>
          <p className="metric-value error">
            {data.errores_hoy}
          </p>
        </div>

        <div className="metric">
          <h3>Total Facturado Hoy</h3>
          <p className="metric-value">
            {data.total_facturado_hoy.toFixed(2)} €
          </p>
        </div>
      </div>

      {/* Últimas ejecuciones */}
      <div className="executions">
        <h2>Últimas Ejecuciones</h2>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Worker</th>
              <th>Estado</th>
              <th>Inicio</th>
              <th>Duración</th>
              <th>Error</th>
            </tr>
          </thead>
          <tbody>
            {data.ultimas_ejecuciones.map((ejecucion) => (
              <tr key={ejecucion.id}>
                <td>{ejecucion.id}</td>
                <td>{ejecucion.task_name}</td>
                <td>
                  <span className={`status ${ejecucion.status.toLowerCase()}`}>
                    {ejecucion.status}
                  </span>
                </td>
                <td>
                  {new Date(ejecucion.started_at).toLocaleString()}
                </td>
                <td>{ejecucion.duration_seconds}s</td>
                <td className="error-cell">
                  {ejecucion.error_message || '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

**¿Qué ves en esta UI?**
- Métricas en tiempo real (como n8n)
- Lista de ejecuciones (como "Executions" de n8n)
- Estado de cada ejecución (SUCCESS, FAILED, RUNNING)
- Errores visibles

---

## COMPARACIÓN VISUAL: n8n vs Tu Código

```
┌─────────────────────────────────────────────────────────────┐
│                          N8N                                │
├─────────────────────────────────────────────────────────────┤
│  [Email Trigger] → [PDF Extract] → [Validate] → [Database] │
│                                                             │
│  Todo visual, drag & drop                                   │
│  Ejecuta en servidores de n8n (o self-hosted)             │
│  Logs en su interfaz web                                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      TU CÓDIGO                              │
├─────────────────────────────────────────────────────────────┤
│  [APScheduler] → [Celery Worker] → [PostgreSQL]            │
│      ↓               ↓                                      │
│   Trigger         Lógica                                    │
│   (cuando)        (qué hacer)                               │
│                                                             │
│  Todo en Python, control total                             │
│  Ejecuta donde tú quieras (tu servidor, AWS, etc)          │
│  Logs en FastAPI + React                                    │
└─────────────────────────────────────────────────────────────┘
```

**¿Qué acabas de construir?**
- ✅ Un sistema completo de automatización (como n8n)
- ✅ Con triggers programados
- ✅ Con workers que procesan tareas
- ✅ Con gestión de errores y reintentos
- ✅ Con base de datos para persistir todo
- ✅ Con API y UI para monitorear

---

## SIGUIENTE PASO: Entender Agentes con Código

Ahora que ya sabes cómo hacer automatizaciones con código, ¿quieres que te explique cómo funcionan los **AGENTES con LangChain**?

La diferencia clave:
- **Automatización** (lo que acabamos de ver): Pasos fijos, siempre hace lo mismo
- **Agente**: El LLM DECIDE qué pasos hacer según la situación

¿Seguimos con agentes? 🤖
