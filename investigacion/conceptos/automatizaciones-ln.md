# Automatizaciones con Código: Lo que REALMENTE Necesitas

Vamos a ir al grano. Ya entiendes QUÉ es una automatización. Ahora vamos a ver QUÉ NECESITAS INSTALAR Y CONFIGURAR para que funcione.

---

## LA PREGUNTA CLAVE: ¿Qué necesito para hacer automatizaciones con código?

### Respuesta corta:
1. **Python** (el lenguaje)
2. **Celery** (para ejecutar trabajos en segundo plano)
3. **Redis** (para la cola de trabajos)
4. **PostgreSQL** (para guardar datos)
5. **FastAPI** (para la API)
6. **React** (opcional, para la UI)

---

## DESGLOSE PIEZA POR PIEZA

### 1. CELERY - El motor que ejecuta trabajos

**¿Qué es Celery?**
Celery es una librería de Python que te permite ejecutar código "en segundo plano" sin bloquear tu aplicación.

**¿Por qué lo necesitas?**
Porque si procesas una factura directamente en tu API, el usuario tiene que esperar 10-20 segundos hasta que termine. Con Celery:
- Recibes la petición
- La encolas (0.1 segundos)
- Respondes "OK, lo estoy procesando"
- Celery lo procesa en segundo plano

**Instalación:**
```bash
pip install celery
```

**Configuración básica:**
```python
# celery_config.py
from celery import Celery

# Crear la app de Celery
app = Celery(
    'mi_sistema',
    broker='redis://localhost:6379/0',    # Dónde está la cola
    backend='redis://localhost:6379/0'     # Dónde guarda resultados
)

# Configuración
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Madrid',
    enable_utc=True,
)
```

**Definir un trabajo (task):**
```python
# tasks/procesar_factura.py
from celery_config import app

@app.task
def procesar_factura(email_id):
    """
    Este es un "trabajo" que Celery puede ejecutar en segundo plano
    """
    print(f"Procesando factura del email {email_id}")

    # Aquí va tu lógica
    # - Descargar email
    # - Extraer PDF
    # - Validar datos
    # - Guardar en DB

    return {"status": "ok", "factura_id": 123}
```

**Ejecutar el trabajo:**
```python
# Desde tu API o cualquier código Python
from tasks.procesar_factura import procesar_factura

# Opción 1: Ejecutar AHORA (bloqueante)
resultado = procesar_factura(email_id="email_123")

# Opción 2: Encolar y ejecutar cuando haya un worker disponible (recomendado)
resultado = procesar_factura.delay("email_123")
# → Esto devuelve inmediatamente, no espera

# Opción 3: Ejecutar después de 60 segundos
resultado = procesar_factura.apply_async(
    args=["email_123"],
    countdown=60
)
```

**Arrancar los workers de Celery:**
```bash
# En una terminal separada
celery -A celery_config worker --loglevel=info

# Esto arranca un "worker" que está esperando trabajos en la cola
# Puedes arrancar múltiples workers para procesar más trabajos en paralelo
```

**¿Qué pasa cuando arrancas un worker?**
```
[2024-10-17 10:30:00] Celery worker starting...
[2024-10-17 10:30:01] Connected to redis://localhost:6379/0
[2024-10-17 10:30:01] Ready to receive tasks

# Cuando llegas un trabajo
[2024-10-17 10:30:15] Received task: procesar_factura[abc-123-def]
[2024-10-17 10:30:15] Procesando factura del email email_123
[2024-10-17 10:30:25] Task procesar_factura[abc-123-def] succeeded: {"status": "ok"}
```

---

### 2. REDIS - La cola de trabajos

**¿Qué es Redis?**
Una base de datos en memoria ultra-rápida. Celery la usa para:
- Guardar la cola de trabajos pendientes
- Guardar los resultados de trabajos completados
- Coordinar múltiples workers

**¿Por qué lo necesitas?**
Sin Redis, Celery no puede funcionar. Es donde vive la "cola" de trabajos.

**Instalación (macOS):**
```bash
brew install redis
```

**Instalación (Ubuntu/Debian):**
```bash
sudo apt-get install redis-server
```

**Instalación (Docker):**
```bash
docker run -d -p 6379:6379 redis:alpine
```

**Arrancar Redis:**
```bash
# macOS/Linux
redis-server

# O en segundo plano
redis-server --daemonize yes
```

**Comprobar que funciona:**
```bash
redis-cli ping
# Respuesta: PONG
```

**¿Qué hace Redis internamente?**
```
REDIS (corriendo en localhost:6379)
====================================

Cola de trabajos pendientes:
┌─────────────────────────────────────┐
│ celery:                             │
│   - procesar_factura (email_123)    │
│   - procesar_factura (email_456)    │
│   - procesar_factura (email_789)    │
└─────────────────────────────────────┘

Resultados de trabajos completados:
┌─────────────────────────────────────┐
│ celery-task-meta-abc-123-def:       │
│   {"status": "ok", "factura_id": 1} │
└─────────────────────────────────────┘

Workers activos:
┌─────────────────────────────────────┐
│ celery@mario-macbook: IDLE          │
│ celery@server-2: BUSY               │
└─────────────────────────────────────┘
```

**Ver qué hay en la cola (comando útil):**
```bash
# Ver cuántos trabajos pendientes
redis-cli llen celery

# Ver trabajos activos
celery -A celery_config inspect active

# Ver workers conectados
celery -A celery_config inspect stats
```

---

### 3. APSCHEDULER - El programador de tareas (cron)

**¿Qué es APScheduler?**
Una librería que ejecuta código en momentos específicos:
- "Cada 5 minutos"
- "Todos los días a las 9:00"
- "Cada lunes a las 8:00"

Es como el `cron` de Linux pero en Python.

**¿Por qué lo necesitas?**
Para los **triggers**: "Revisa emails nuevos cada 5 minutos"

**Instalación:**
```bash
pip install apscheduler
```

**Configuración:**
```python
# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from tasks.procesar_factura import procesar_factura

# Crear el scheduler
scheduler = BackgroundScheduler()

def revisar_emails():
    """
    Esta función se ejecuta cada 5 minutos
    """
    print("Revisando emails nuevos...")

    # Aquí irías a Gmail y buscarías emails nuevos
    # Por cada email nuevo, encolas un worker
    emails_nuevos = ["email_123", "email_456"]

    for email_id in emails_nuevos:
        procesar_factura.delay(email_id)
        print(f"Encolado worker para {email_id}")

# Programar: ejecutar cada 5 minutos
scheduler.add_job(
    revisar_emails,
    'interval',
    minutes=5,
    id='revisar_emails'
)

# Iniciar el scheduler
scheduler.start()
print("Scheduler iniciado")

# Mantener el script corriendo
import time
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    scheduler.shutdown()
```

**Arrancar el scheduler:**
```bash
python scheduler.py

# Output:
Scheduler iniciado
Revisando emails nuevos...
Encolado worker para email_123
Encolado worker para email_456
# (espera 5 minutos)
Revisando emails nuevos...
Encolado worker para email_789
```

**Opciones de programación:**

```python
# Cada X minutos
scheduler.add_job(mi_funcion, 'interval', minutes=5)

# Cada X horas
scheduler.add_job(mi_funcion, 'interval', hours=2)

# Cada día a las 9:00
scheduler.add_job(mi_funcion, 'cron', hour=9, minute=0)

# Cada lunes a las 8:30
scheduler.add_job(mi_funcion, 'cron', day_of_week='mon', hour=8, minute=30)

# De lunes a viernes a las 9:00
scheduler.add_job(mi_funcion, 'cron', day_of_week='mon-fri', hour=9, minute=0)

# Cada 30 segundos
scheduler.add_job(mi_funcion, 'interval', seconds=30)
```

---

### 4. POSTGRESQL - La base de datos

**¿Qué es PostgreSQL?**
Una base de datos relacional donde guardas todos tus datos:
- Facturas procesadas
- Proveedores autorizados
- Historial de ejecuciones
- Errores

**¿Por qué lo necesitas?**
Porque necesitas persistir datos. Redis solo guarda cosas temporalmente.

**Instalación (macOS):**
```bash
brew install postgresql
brew services start postgresql
```

**Instalación (Ubuntu/Debian):**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Instalación (Docker):**
```bash
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=mipassword \
  -e POSTGRES_DB=facturas \
  -p 5432:5432 \
  postgres:15-alpine
```

**Crear la base de datos:**
```bash
# Conectar a PostgreSQL
psql -U postgres

# Crear base de datos
CREATE DATABASE facturas;

# Conectar a la base de datos
\c facturas

# Crear tabla de facturas
CREATE TABLE facturas (
    id SERIAL PRIMARY KEY,
    nif VARCHAR(9) NOT NULL,
    importe DECIMAL(10,2) NOT NULL,
    fecha DATE NOT NULL,
    email_id VARCHAR(255) NOT NULL,
    estado VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

# Crear tabla de proveedores
CREATE TABLE proveedores (
    id SERIAL PRIMARY KEY,
    nif VARCHAR(9) UNIQUE NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    activo BOOLEAN DEFAULT true
);

# Salir
\q
```

**Conectar desde Python:**
```bash
pip install psycopg2-binary
```

```python
import psycopg2

# Conectar
conn = psycopg2.connect(
    dbname="facturas",
    user="postgres",
    password="mipassword",
    host="localhost",
    port="5432"
)

# Crear cursor
cur = conn.cursor()

# Insertar factura
cur.execute("""
    INSERT INTO facturas (nif, importe, fecha, email_id, estado)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id
""", ("B12345678", 1500.00, "2024-10-17", "email_123", "PENDIENTE"))

factura_id = cur.fetchone()[0]
print(f"Factura guardada con ID: {factura_id}")

# Commit
conn.commit()

# Cerrar
cur.close()
conn.close()
```

**Comandos útiles de PostgreSQL:**
```bash
# Ver todas las bases de datos
psql -U postgres -c "\l"

# Ver todas las tablas
psql -U postgres -d facturas -c "\dt"

# Ver datos de una tabla
psql -U postgres -d facturas -c "SELECT * FROM facturas LIMIT 10"

# Backup
pg_dump -U postgres facturas > backup.sql

# Restore
psql -U postgres facturas < backup.sql
```

---

### 5. FASTAPI - La API REST

**¿Qué es FastAPI?**
Un framework para crear APIs REST en Python. Es como Express.js pero en Python.

**¿Por qué lo necesitas?**
Para que tu frontend (React) pueda:
- Ver el dashboard
- Listar facturas
- Ver errores
- Ejecutar workers manualmente

**Instalación:**
```bash
pip install fastapi uvicorn
```

**Crear API básica:**
```python
# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2

app = FastAPI()

# Permitir CORS (para que React pueda llamar a la API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    return psycopg2.connect(
        dbname="facturas",
        user="postgres",
        password="mipassword",
        host="localhost"
    )

@app.get("/")
def root():
    return {"message": "API de Facturas"}

@app.get("/api/facturas")
def get_facturas():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, nif, importe, fecha, estado
        FROM facturas
        ORDER BY created_at DESC
        LIMIT 50
    """)

    facturas = []
    for row in cur.fetchall():
        facturas.append({
            "id": row[0],
            "nif": row[1],
            "importe": float(row[2]),
            "fecha": str(row[3]),
            "estado": row[4]
        })

    conn.close()
    return {"facturas": facturas}

@app.post("/api/procesar-factura/{email_id}")
def procesar_factura_manual(email_id: str):
    from tasks.procesar_factura import procesar_factura

    # Encolar el trabajo
    task = procesar_factura.delay(email_id)

    return {
        "status": "enqueued",
        "task_id": task.id
    }
```

**Arrancar la API:**
```bash
uvicorn api.main:app --reload --port 8000

# Output:
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Probar la API:**
```bash
# Ver facturas
curl http://localhost:8000/api/facturas

# Procesar factura manualmente
curl -X POST http://localhost:8000/api/procesar-factura/email_123
```

---

### 6. REACT (Opcional) - La interfaz web

**¿Qué es React?**
Una librería de JavaScript para crear interfaces de usuario.

**¿Por qué lo necesitas?**
Para tener un panel visual como n8n donde veas:
- Dashboard con métricas
- Lista de facturas
- Historial de ejecuciones
- Errores

**Instalación:**
```bash
npx create-react-app frontend
cd frontend
npm start
```

**Conectar con tu API:**
```typescript
// frontend/src/App.tsx
import React, { useEffect, useState } from 'react';

function App() {
  const [facturas, setFacturas] = useState([]);

  useEffect(() => {
    // Llamar a la API
    fetch('http://localhost:8000/api/facturas')
      .then(res => res.json())
      .then(data => setFacturas(data.facturas));
  }, []);

  return (
    <div>
      <h1>Facturas</h1>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>NIF</th>
            <th>Importe</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          {facturas.map((f: any) => (
            <tr key={f.id}>
              <td>{f.id}</td>
              <td>{f.nif}</td>
              <td>{f.importe} €</td>
              <td>{f.estado}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
```

---

## RESUMEN: ¿QUÉ NECESITO INSTALAR?

### Instalaciones necesarias:

```bash
# 1. Redis (la cola)
brew install redis
redis-server

# 2. PostgreSQL (la base de datos)
brew install postgresql
brew services start postgresql

# 3. Librerías Python
pip install celery redis psycopg2-binary apscheduler fastapi uvicorn

# 4. (Opcional) React para UI
npx create-react-app frontend
```

### Arrancar todo:

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Worker de Celery
celery -A celery_config worker --loglevel=info

# Terminal 3: Scheduler (triggers)
python scheduler.py

# Terminal 4: API
uvicorn api.main:app --reload

# Terminal 5 (opcional): Frontend React
cd frontend && npm start
```

---

## ESTRUCTURA DE ARCHIVOS FINAL

```
mi-sistema-facturas/
├── celery_config.py          # Configuración de Celery
├── scheduler.py               # Triggers (APScheduler)
├── tasks/
│   └── procesar_factura.py    # Workers (lógica de negocio)
├── api/
│   └── main.py                # FastAPI (endpoints)
├── database/
│   └── schema.sql             # Estructura de PostgreSQL
├── frontend/                  # React (opcional)
│   ├── src/
│   │   └── App.tsx
│   └── package.json
└── requirements.txt           # Dependencias Python
```

**requirements.txt:**
```
celery==5.3.4
redis==5.0.1
psycopg2-binary==2.9.9
apscheduler==3.10.4
fastapi==0.104.1
uvicorn==0.24.0
```

---

## LA PREGUNTA DEL MILLÓN: ¿Es complicado?

**Respuesta honesta**: La PRIMERA vez que lo montas, sí, es un poco lioso porque tienes que:
1. Instalar Redis
2. Instalar PostgreSQL
3. Configurar Celery
4. Arrancar todo en terminales separadas

**PERO**: Una vez que lo tienes montado (1-2 horas), añadir NUEVOS workers es trivial:

```python
# Nuevo worker: enviar email de bienvenida
@app.task
def enviar_email_bienvenida(user_id):
    user = get_user_from_db(user_id)
    send_email(user.email, "Bienvenido!")
    return {"status": "ok"}

# Usarlo
enviar_email_bienvenida.delay(123)
```

**Eso es todo**. No necesitas tocar nada más.

---

## SIGUIENTE PASO: AGENTES

Ya sabes qué necesitas para hacer automatizaciones con código. Ahora falta entender **AGENTES con LangChain**.

¿Quieres que te explique qué necesitas instalar y configurar para usar agentes con LLMs? 🤖
