# Plan de Arquitectura: Tu Sistema de Trabajadores Digitales

Este plan te enseña **arquitectura de sistemas**, no programación. Al final entenderás PERFECTAMENTE cómo construir tu Maisa, y Claude Code escribirá el código.

---

## ESTRUCTURA DEL CURSO

**Tiempo total**: 8-10 horas (distribuidas en 1 semana)
**Formato**: Explicaciones + Diagramas + Ejemplos prácticos
**Resultado**: Sabrás exactamente qué construir y por qué

---

## MÓDULO 1: Arquitectura General del Sistema (2 horas)

### Objetivos:
- Entender las 5 piezas principales y cómo se conectan
- Ver el flujo completo end-to-end
- Comprender por qué cada pieza es necesaria

### Contenido:

#### 1.1 Visión de Alto Nivel (30 min)
```
Usuario dice: "Crea trabajador que procese facturas"
    ↓
[GENERADOR DE CÓDIGO] - GPT-4 genera Python paso a paso
    ↓
[SANDBOX] - Docker ejecuta el código de forma segura
    ↓
[CHAIN-OF-WORK] - PostgreSQL guarda TODO lo que pasó
    ↓
[API] - FastAPI expone todo como servicio
    ↓
[CLI/UI] - Interfaz para crear y gestionar trabajadores
```

**Por qué esta arquitectura**:
- Separación de responsabilidades
- Cada pieza hace UNA cosa bien
- Fácil de debuggear
- Fácil de escalar

#### 1.2 Las 5 Piezas Fundamentales (1 hora)

**PIEZA 1: El Generador de Código**
```
Input: "Lee email, extrae PDF, valida NIF"
Output: Código Python ejecutable

Responsabilidad:
- Recibir descripción en lenguaje natural
- Generar código Python paso a paso (no todo de golpe)
- Validar que el código es seguro
- Incluir manejo de errores
```

**PIEZA 2: El Sandbox (Docker)**
```
Input: Código Python generado
Output: Resultado de la ejecución

Responsabilidad:
- Ejecutar código de forma AISLADA
- Limitar recursos (CPU, memoria, tiempo)
- Capturar output y errores
- NO permitir acceso a cosas peligrosas
```

**PIEZA 3: Chain-of-Work (PostgreSQL)**
```
Input: Cada paso de ejecución
Output: Historial completo auditable

Responsabilidad:
- Guardar TODO: código, resultado, tiempo, errores
- Permitir reproducir ejecuciones
- Dar trazabilidad completa
- Base para el determinismo
```

**PIEZA 4: La API (FastAPI)**
```
Input: Requests HTTP
Output: Responses JSON

Responsabilidad:
- Endpoint para crear trabajadores
- Endpoint para ejecutar trabajadores
- Endpoint para ver Chain-of-Work
- Endpoint para gestionar trabajadores
```

**PIEZA 5: La Interfaz (CLI o UI)**
```
Input: Comandos del usuario
Output: Llamadas a la API

Responsabilidad:
- Permitir crear trabajadores fácilmente
- Mostrar resultados de ejecuciones
- Visualizar Chain-of-Work
- Gestionar trabajadores existentes
```

#### 1.3 Flujo Completo End-to-End (30 min)

**Escenario**: Usuario quiere crear un trabajador que procese facturas

```
PASO 1: Usuario describe el trabajador
├─ CLI: "python crear_trabajador.py"
├─ Input: "Procesa facturas: lee email, extrae NIF, valida"
└─ API recibe: POST /trabajadores/crear

PASO 2: Generador de Código trabaja
├─ LLM analiza la descripción
├─ Identifica herramientas necesarias (gmail, pdf_reader, database)
├─ Genera "esqueleto" del trabajador
└─ Guarda en BD: trabajador_123

PASO 3: Usuario ejecuta el trabajador
├─ CLI: "python ejecutar_trabajador.py 123 --email_id=456"
├─ API recibe: POST /trabajadores/123/ejecutar
└─ Orquestador toma el control

PASO 4: Orquestador genera código paso a paso
├─ Paso 1: Genera código "buscar email"
├─ Ejecuta en Docker → resultado OK
├─ Guarda en Chain-of-Work
├─ Paso 2: Genera código "descargar PDF"
├─ Ejecuta en Docker → resultado OK
├─ Guarda en Chain-of-Work
├─ ... (continúa hasta terminar)
└─ Resultado final: SUCCESS

PASO 5: Chain-of-Work completo disponible
├─ API: GET /ejecuciones/789/chain-of-work
└─ Usuario ve TODO lo que pasó
```

**Preguntas que responderemos**:
- ¿Por qué no generar todo el código de golpe?
- ¿Por qué Docker y no ejecutar directo?
- ¿Por qué guardar cada paso?
- ¿Por qué separar generación de ejecución?

---

## MÓDULO 2: El Generador de Código (1.5 horas)

### Objetivos:
- Entender cómo pedirle al LLM que genere código
- Aprender a hacerlo paso a paso (incremental)
- Saber qué validaciones hacer
- Comprender cómo se adapta a casos inesperados

### Contenido:

#### 2.1 Estrategia de Generación (30 min)

**Por qué NO generar todo de golpe**:
```
❌ MAL: Generar 200 líneas de código
Problemas:
- No conoce el contexto completo
- Asume muchas cosas
- Si falla en el paso 5, pasos 1-4 desperdiciados
- No puede adaptarse sobre la marcha

✅ BIEN: Generar 2-3 líneas por vez
Ventajas:
- Ve resultado del paso anterior
- Se adapta según lo que encuentra
- Si falla, solo regenera ese paso
- Puede tomar decisiones en tiempo real
```

**Ejemplo concreto**:
```
Tarea: "Procesa la factura del email"

GENERACIÓN INCREMENTAL:

Paso 1: Generar código para buscar email
→ Código: email = gmail_api.buscar(...)
→ Ejecutar en Docker
→ Resultado: email encontrado ✓

Paso 2: Generar código para descargar PDF (conoce el email del paso 1)
→ Código: pdf = gmail_api.descargar_adjunto(email.id)
→ Ejecutar en Docker
→ Resultado: PDF descargado ✓

Paso 3: Generar código para extraer datos (conoce el PDF del paso 2)
→ Código: texto = pdf_reader.extraer(pdf)
          nif = regex.search(r'NIF: ([A-Z0-9]+)', texto)
→ Ejecutar en Docker
→ Resultado: NIF extraído ✓

... y así sucesivamente
```

#### 2.2 Prompting para Generación de Código (40 min)

**Anatomía de un buen prompt**:

```python
PROMPT_TEMPLATE = """
Eres un generador de código Python experto.

CONTEXTO:
- Estamos en el paso {paso_numero} de {total_pasos}
- Objetivo final: {objetivo_trabajador}
- Resultados de pasos anteriores: {resultados_previos}

HERRAMIENTAS DISPONIBLES:
{lista_herramientas_con_documentacion}

TAREA ACTUAL:
{descripcion_paso_actual}

RESTRICCIONES:
- Genera SOLO 2-5 líneas de código
- Usa SOLO las herramientas disponibles
- NO uses imports externos (ya están disponibles)
- Incluye manejo de errores básico

FORMATO DE OUTPUT:
```python
# Código aquí
```

GENERA EL CÓDIGO:
"""
```

**Ejemplo real**:
```
CONTEXTO:
- Estamos en el paso 2 de 5
- Objetivo: Extraer datos de factura y validar
- Paso anterior: Email encontrado (id: email_123)

HERRAMIENTAS:
- gmail_api.descargar_adjunto(email_id, tipo='pdf') → bytes

TAREA ACTUAL:
Descargar el PDF adjunto del email

CÓDIGO GENERADO:
```python
pdf_bytes = gmail_api.descargar_adjunto('email_123', tipo='pdf')
if not pdf_bytes:
    raise ValueError("No se encontró PDF en el email")
```
```

#### 2.3 Validación y Seguridad (20 min)

**Qué validar ANTES de ejecutar**:

```python
# 1. Sintaxis válida
try:
    compile(codigo_generado, '<string>', 'exec')
except SyntaxError:
    # Pedir al LLM que regenere

# 2. No contiene cosas peligrosas
BLACKLIST = ['os.system', 'subprocess', 'eval', 'exec', '__import__']
for peligro in BLACKLIST:
    if peligro in codigo_generado:
        # Rechazar y pedir regeneración

# 3. Solo usa herramientas permitidas
herramientas_usadas = extraer_llamadas_funciones(codigo_generado)
for herramienta in herramientas_usadas:
    if herramienta not in HERRAMIENTAS_PERMITIDAS:
        # Rechazar
```

**Por qué esto es crítico**:
- Ejecutas código generado por IA
- Puede intentar hacer cosas maliciosas (sin querer)
- Necesitas múltiples capas de seguridad

---

## MÓDULO 3: Ejecución en Sandbox (1.5 horas)

### Objetivos:
- Entender por qué Docker es necesario
- Aprender a configurar un sandbox seguro
- Saber capturar resultados y errores
- Gestionar recursos y timeouts

### Contenido:

#### 3.1 Por Qué Docker (20 min)

**Alternativas y por qué NO funcionan**:

```
❌ Ejecutar directo en el servidor:
Problemas:
- Código malicioso puede leer archivos del sistema
- Puede borrar cosas
- Puede abrir conexiones
- Un error puede tumbar todo el servidor

❌ Usar virtualenv/venv:
Problemas:
- Solo aísla librerías Python
- NO aísla sistema de archivos
- NO aísla red
- NO aísla procesos

✅ Docker:
Ventajas:
- Aislamiento COMPLETO
- Límites de recursos (CPU, RAM)
- Si explota, solo afecta al contenedor
- Fácil de limpiar y recrear
```

**Analogía**:
- Ejecutar directo = Dejar entrar a un desconocido a tu casa
- Docker = Darle una habitación separada con llave

#### 3.2 Configuración del Sandbox (40 min)

**Dockerfile para el sandbox**:

```dockerfile
FROM python:3.11-slim

# Instalar herramientas básicas
RUN pip install --no-cache-dir \
    requests \
    beautifulsoup4 \
    pandas

# Crear usuario sin privilegios
RUN useradd -m -u 1000 sandbox
USER sandbox

# Directorio de trabajo
WORKDIR /sandbox

# Comando por defecto
CMD ["python", "-u", "script.py"]
```

**Por qué cada línea**:
- `python:3.11-slim`: Imagen base pequeña y rápida
- `pip install`: Librerías que los trabajadores pueden usar
- `useradd`: NO ejecutar como root (seguridad)
- `WORKDIR`: Aislar archivos
- `-u`: Output sin buffer (para capturar en tiempo real)

**Ejecutar código con límites**:

```python
import docker

client = docker.from_env()

# Ejecutar con límites estrictos
container = client.containers.run(
    image='sandbox:latest',
    command=f'python -c "{codigo_generado}"',

    # LÍMITES DE RECURSOS
    mem_limit='256m',        # Máximo 256MB RAM
    cpu_quota=50000,         # 50% de 1 CPU

    # TIMEOUTS
    detach=True,             # Ejecutar en background

    # SEGURIDAD
    network_disabled=True,   # Sin acceso a internet (opcional)
    read_only=True,          # Sistema de archivos read-only

    # CAPTURA DE OUTPUT
    stdout=True,
    stderr=True,

    # AUTO-LIMPIEZA
    remove=True              # Borrar contenedor al terminar
)

# Esperar resultado con timeout
try:
    resultado = container.wait(timeout=30)  # 30 segundos máximo
    logs = container.logs()
except docker.errors.ContainerError as e:
    # El código falló
    error = e.stderr.decode('utf-8')
```

**Decisiones arquitectónicas**:
- ¿Cuánta RAM dar? (trade-off: seguridad vs funcionalidad)
- ¿Permitir acceso a red? (depende del caso de uso)
- ¿Timeout? (facturas = 30s, cierres contables = 5 min)

#### 3.3 Captura de Resultados (30 min)

**Qué capturar**:

```python
resultado_ejecucion = {
    # OUTPUT DEL CÓDIGO
    "stdout": "Factura procesada: NIF B12345678, Importe 1500€",
    "stderr": "",

    # MÉTRICAS
    "duracion_segundos": 2.3,
    "memoria_usada_mb": 45,
    "cpu_percent": 23,

    # ESTADO
    "exit_code": 0,  # 0 = éxito, >0 = error
    "success": True,

    # VARIABLES EXTRAÍDAS (si las hay)
    "variables": {
        "nif": "B12345678",
        "importe": 1500.00
    }
}
```

**Cómo extraer variables del código**:

```python
# El código puede devolver resultados así:
codigo_generado = """
nif = extraer_nif(pdf)
importe = extraer_importe(pdf)

# Devolver resultado en formato JSON
import json
print(json.dumps({"nif": nif, "importe": importe}))
"""

# Tú capturas el stdout y parseas el JSON
output = ejecutar_en_docker(codigo_generado)
resultado = json.loads(output)
# → {"nif": "B12345678", "importe": 1500.00}
```

---

## MÓDULO 4: Chain-of-Work (1 hora)

### Objetivos:
- Entender qué guardar y por qué
- Diseñar el schema de base de datos
- Hacer que todo sea reproducible
- Dar auditabilidad 100%

### Contenido:

#### 4.1 Qué Guardar (20 min)

**La regla de oro**: Guarda TODO lo que necesitas para:
1. Entender qué pasó
2. Reproducir la ejecución
3. Debuggear errores
4. Cumplir con auditorías

**Esquema de datos**:

```sql
-- Tabla de trabajadores
CREATE TABLE trabajadores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255),
    descripcion TEXT,
    herramientas JSONB,  -- ["gmail", "pdf_reader", ...]
    creado_en TIMESTAMP DEFAULT NOW()
);

-- Tabla de ejecuciones
CREATE TABLE ejecuciones (
    id SERIAL PRIMARY KEY,
    trabajador_id INTEGER REFERENCES trabajadores(id),
    input_data JSONB,    -- {"email_id": "123"}
    status VARCHAR(50),  -- RUNNING, SUCCESS, FAILED
    iniciado_en TIMESTAMP,
    terminado_en TIMESTAMP,
    duracion_segundos DECIMAL
);

-- Tabla de pasos (Chain-of-Work)
CREATE TABLE chain_of_work (
    id SERIAL PRIMARY KEY,
    ejecucion_id INTEGER REFERENCES ejecuciones(id),
    paso_numero INTEGER,

    -- QUÉ SE GENERÓ
    codigo_generado TEXT,
    prompt_usado TEXT,

    -- QUÉ PASÓ
    stdout TEXT,
    stderr TEXT,
    exit_code INTEGER,

    -- MÉTRICAS
    duracion_segundos DECIMAL,
    memoria_mb INTEGER,

    -- CONTEXTO
    variables_entrada JSONB,
    variables_salida JSONB,

    timestamp TIMESTAMP DEFAULT NOW()
);
```

#### 4.2 Ejemplo de Chain-of-Work Real (20 min)

**Ejecución**: Procesar factura del email_123

```json
{
  "ejecucion_id": 456,
  "trabajador": "Procesador de Facturas",
  "input": {"email_id": "email_123"},
  "status": "SUCCESS",
  "duracion_total": "8.7s",

  "chain_of_work": [
    {
      "paso": 1,
      "descripcion": "Buscar email en Gmail",
      "codigo": "email = gmail_api.buscar(id='email_123')",
      "resultado": {"id": "email_123", "found": true},
      "duracion": "0.8s",
      "timestamp": "2025-01-15T10:30:00Z"
    },
    {
      "paso": 2,
      "descripcion": "Descargar PDF adjunto",
      "codigo": "pdf = gmail_api.descargar_adjunto(email.id)",
      "resultado": {"size_kb": 234, "type": "pdf"},
      "duracion": "1.2s",
      "timestamp": "2025-01-15T10:30:01Z"
    },
    {
      "paso": 3,
      "descripcion": "Extraer NIF del PDF",
      "codigo": "texto = pdf_reader.extraer(pdf)\nnif = regex.search(r'NIF: ([A-Z0-9]+)', texto).group(1)",
      "resultado": {"nif": "B12345678"},
      "duracion": "2.1s",
      "timestamp": "2025-01-15T10:30:02Z"
    },
    {
      "paso": 4,
      "descripcion": "Validar NIF en base de datos",
      "codigo": "proveedor = db.query('SELECT * FROM proveedores WHERE nif = ?', [nif])",
      "resultado": {"found": true, "proveedor_id": 789, "activo": true},
      "duracion": "0.4s",
      "timestamp": "2025-01-15T10:30:04Z"
    },
    {
      "paso": 5,
      "descripcion": "Guardar factura",
      "codigo": "factura_id = db.insert('facturas', {'nif': nif, 'importe': 1500})",
      "resultado": {"factura_id": 1234},
      "duracion": "0.3s",
      "timestamp": "2025-01-15T10:30:05Z"
    }
  ]
}
```

**Con esto puedes**:
- Ver EXACTAMENTE qué hizo en cada paso
- Reproducir el paso 3 si falla
- Auditar para compliance
- Explicar a un cliente qué pasó

#### 4.3 Visualización del Chain-of-Work (20 min)

**En la CLI**:
```
$ python ver_ejecucion.py 456

EJECUCIÓN #456 - Procesador de Facturas
Status: ✅ SUCCESS
Duración: 8.7s
Input: email_id=email_123

CHAIN-OF-WORK:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Paso 1 (0.8s) - Buscar email en Gmail
  Código:
    email = gmail_api.buscar(id='email_123')
  Resultado:
    ✅ Email encontrado

Paso 2 (1.2s) - Descargar PDF adjunto
  Código:
    pdf = gmail_api.descargar_adjunto(email.id)
  Resultado:
    ✅ PDF descargado (234 KB)

Paso 3 (2.1s) - Extraer NIF del PDF
  Código:
    texto = pdf_reader.extraer(pdf)
    nif = regex.search(r'NIF: ([A-Z0-9]+)', texto).group(1)
  Resultado:
    ✅ NIF extraído: B12345678

... etc
```

---

## MÓDULO 5: Determinismo (45 min)

### Objetivos:
- Entender cómo hacer la segunda ejecución determinista
- Aprender a cachear código que funciona
- Saber cuándo regenerar vs reusar código

### Contenido:

#### 5.1 El Concepto de Determinismo (15 min)

**Problema con agentes tradicionales**:
```
Input: "Procesa factura email_123"

Ejecución 1:
- Llama a tool_A
- Luego tool_B
- Resultado: NIF extraído ✓

Ejecución 2 (MISMO input):
- Llama a tool_B primero
- Luego tool_C (diferente!)
- Resultado: NIF NO extraído ✗

❌ NO determinista
```

**Solución con código generado**:
```
Input: "Procesa factura email_123"

Ejecución 1:
- Genera código X
- Ejecuta código X
- Funciona ✓
- Guarda código X asociado al hash del input

Ejecución 2 (MISMO input):
- Detecta: "Ya tengo código para este input"
- Ejecuta MISMO código X
- Mismo resultado ✓

✅ Determinista
```

#### 5.2 Implementación del Caché (20 min)

**Esquema**:

```python
import hashlib
import json

def calcular_hash_input(input_data, trabajador_id):
    """
    Calcula un hash único del input
    """
    # Serializar input de forma consistente
    input_str = json.dumps(input_data, sort_keys=True)

    # Incluir el trabajador_id (versión del trabajador)
    combined = f"{trabajador_id}:{input_str}"

    # Hash
    return hashlib.sha256(combined.encode()).hexdigest()


def ejecutar_trabajador(trabajador_id, input_data):
    """
    Ejecuta un trabajador con determinismo
    """
    # Calcular hash del input
    input_hash = calcular_hash_input(input_data, trabajador_id)

    # Buscar si ya tenemos código para este input
    codigo_cacheado = db.query("""
        SELECT chain_of_work
        FROM ejecuciones_exitosas
        WHERE trabajador_id = ? AND input_hash = ?
    """, [trabajador_id, input_hash])

    if codigo_cacheado:
        # REUSAR código que ya funcionó
        print("✅ Usando código cacheado (determinista)")
        resultado = ejecutar_chain_of_work(codigo_cacheado)
    else:
        # GENERAR código nuevo
        print("🆕 Generando código nuevo...")
        resultado = generar_y_ejecutar(trabajador_id, input_data)

        if resultado.success:
            # Guardar para futuras ejecuciones
            db.insert("ejecuciones_exitosas", {
                "trabajador_id": trabajador_id,
                "input_hash": input_hash,
                "chain_of_work": resultado.chain_of_work
            })

    return resultado
```

#### 5.3 Cuándo Invalidar el Caché (10 min)

**Casos donde NO debes reusar código**:

1. **El trabajador cambió**:
```python
# Usuario modifica instrucciones del trabajador
# → Incrementar versión → nuevo trabajador_id
# → No hay caché para el nuevo trabajador_id
```

2. **Los datos son "similares" pero no idénticos**:
```python
Input 1: {"email_id": "email_123"}
Input 2: {"email_id": "email_456"}
# → Hashes diferentes → código diferente (correcto)
```

3. **Las herramientas disponibles cambiaron**:
```python
# Actualizaste gmail_api v1 → v2
# → Marca todos los cachés como "stale"
# → Regenerar código
```

---

## MÓDULO 6: API y Orquestación (1.5 horas)

### Objetivos:
- Diseñar los endpoints de la API
- Entender cómo orquestar todas las piezas
- Gestionar estados y errores
- Hacer que sea escalable

### Contenido:

#### 6.1 Diseño de la API (30 min)

**Endpoints principales**:

```python
# FastAPI
from fastapi import FastAPI

app = FastAPI()

# 1. CREAR TRABAJADOR
@app.post("/trabajadores")
def crear_trabajador(data: dict):
    """
    Input: {
        "nombre": "Procesador de Facturas",
        "descripcion": "Lee emails, extrae datos...",
        "herramientas": ["gmail", "pdf_reader", "database"]
    }
    Output: {
        "trabajador_id": 123
    }
    """

# 2. EJECUTAR TRABAJADOR
@app.post("/trabajadores/{id}/ejecutar")
def ejecutar_trabajador(id: int, input_data: dict):
    """
    Input: {"email_id": "email_123"}
    Output: {
        "ejecucion_id": 456,
        "status": "RUNNING"
    }
    """

# 3. VER ESTADO DE EJECUCIÓN
@app.get("/ejecuciones/{id}")
def ver_ejecucion(id: int):
    """
    Output: {
        "status": "SUCCESS",
        "resultado": {...},
        "duracion": "8.7s"
    }
    """

# 4. VER CHAIN-OF-WORK
@app.get("/ejecuciones/{id}/chain-of-work")
def ver_chain_of_work(id: int):
    """
    Output: [
        {"paso": 1, "codigo": "...", "resultado": "..."},
        {"paso": 2, "codigo": "...", "resultado": "..."},
        ...
    ]
    """

# 5. LISTAR TRABAJADORES
@app.get("/trabajadores")
def listar_trabajadores():
    """
    Output: [
        {"id": 123, "nombre": "Procesador Facturas"},
        {"id": 124, "nombre": "Validador NIFs"},
        ...
    ]
    """
```

#### 6.2 El Orquestador (40 min)

**El cerebro del sistema**:

```python
class OrquestadorTrabajador:
    """
    Coordina todas las piezas:
    - Generación de código
    - Ejecución en sandbox
    - Chain-of-Work
    - Determinismo
    """

    def __init__(self, trabajador_id):
        self.trabajador = db.get_trabajador(trabajador_id)
        self.generador = GeneradorCodigo()
        self.sandbox = SandboxDocker()
        self.chain = []

    async def ejecutar(self, input_data):
        """
        Ejecuta el trabajador completo
        """
        # 1. Verificar si hay código cacheado
        input_hash = calcular_hash(input_data)
        codigo_cache = self.buscar_cache(input_hash)

        if codigo_cache:
            return await self.ejecutar_determinista(codigo_cache)

        # 2. Ejecutar paso a paso generando código
        return await self.ejecutar_generativo(input_data)

    async def ejecutar_generativo(self, input_data):
        """
        Genera y ejecuta código paso a paso
        """
        contexto = {
            "trabajador": self.trabajador,
            "input": input_data,
            "resultados_previos": []
        }

        paso_numero = 1
        max_pasos = 20  # Límite de seguridad

        while paso_numero <= max_pasos:
            # Generar código para este paso
            codigo = await self.generador.generar_paso(
                contexto=contexto,
                paso_numero=paso_numero
            )

            # Validar código
            if not self.validar_codigo(codigo):
                raise ValueError("Código no válido generado")

            # Ejecutar en sandbox
            resultado = await self.sandbox.ejecutar(codigo)

            # Guardar en chain-of-work
            self.chain.append({
                "paso": paso_numero,
                "codigo": codigo,
                "resultado": resultado
            })

            # Actualizar contexto para siguiente paso
            contexto["resultados_previos"].append(resultado)

            # ¿Ya terminamos?
            if self.tarea_completada(resultado):
                break

            paso_numero += 1

        # Guardar chain-of-work completo
        return self.guardar_resultado()

    async def ejecutar_determinista(self, codigo_cache):
        """
        Ejecuta código ya conocido (2ª ejecución)
        """
        for paso in codigo_cache:
            resultado = await self.sandbox.ejecutar(paso["codigo"])
            self.chain.append({
                "paso": paso["paso"],
                "codigo": paso["codigo"],
                "resultado": resultado,
                "cache": True  # Marcar que vino de caché
            })

        return self.guardar_resultado()
```

#### 6.3 Manejo de Errores (20 min)

**Estrategia de recuperación**:

```python
async def ejecutar_paso_con_retry(self, codigo, max_reintentos=3):
    """
    Ejecuta un paso con auto-corrección
    """
    for intento in range(max_reintentos):
        try:
            # Ejecutar código
            resultado = await self.sandbox.ejecutar(codigo)

            if resultado.success:
                return resultado

            # Si falla, pedir al LLM que corrija
            codigo_corregido = await self.generador.corregir_codigo(
                codigo_original=codigo,
                error=resultado.error,
                intento=intento
            )

            codigo = codigo_corregido

        except Exception as e:
            if intento == max_reintentos - 1:
                # Último intento, fallar
                raise

            # Esperar antes de reintentar
            await asyncio.sleep(2 ** intento)

    raise RuntimeError("No se pudo ejecutar el paso después de reintentos")
```

---

## MÓDULO FINAL: Juntando Todo (30 min)

### Arquitectura Completa Integrada

```
┌─────────────────────────────────────────────────────────────┐
│                        USUARIO                              │
│                          │                                  │
│                          ▼                                  │
│              ┌───────────────────────┐                      │
│              │   CLI / UI (Futuro)   │                      │
│              └───────────┬───────────┘                      │
│                          │                                  │
│                          ▼                                  │
│              ┌───────────────────────┐                      │
│              │    FastAPI (API)      │                      │
│              └───────────┬───────────┘                      │
│                          │                                  │
│                          ▼                                  │
│       ┌──────────────────────────────────────┐             │
│       │     ORQUESTADOR TRABAJADOR           │             │
│       │                                       │             │
│       │  1. Verifica caché (determinismo)    │             │
│       │  2. Si no hay → genera código        │             │
│       │  3. Ejecuta en sandbox               │             │
│       │  4. Guarda chain-of-work             │             │
│       └────┬─────────────────────────┬───────┘             │
│            │                         │                      │
│            ▼                         ▼                      │
│  ┌─────────────────┐      ┌──────────────────┐            │
│  │ GENERADOR       │      │ SANDBOX          │            │
│  │ CÓDIGO          │      │ (Docker)         │            │
│  │                 │      │                  │            │
│  │ - GPT-4 genera  │      │ - Ejecuta código │            │
│  │ - Paso a paso   │      │ - Límites        │            │
│  │ - Valida        │      │ - Captura output │            │
│  └─────────────────┘      └──────────────────┘            │
│            │                         │                      │
│            └──────────┬──────────────┘                      │
│                       ▼                                     │
│            ┌──────────────────────┐                        │
│            │   PostgreSQL         │                        │
│            │                      │                        │
│            │ - Trabajadores       │                        │
│            │ - Ejecuciones        │                        │
│            │ - Chain-of-Work      │                        │
│            │ - Caché              │                        │
│            └──────────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### Flujo Completo End-to-End

```
1. USUARIO crea trabajador
   → CLI: python crear_trabajador.py
   → API: POST /trabajadores
   → DB: INSERT INTO trabajadores

2. USUARIO ejecuta trabajador
   → CLI: python ejecutar.py 123 --input='{"email_id":"456"}'
   → API: POST /trabajadores/123/ejecutar

3. ORQUESTADOR toma control
   → Busca caché
   → Si no hay: inicia generación

4. GENERADOR produce código paso a paso
   → Paso 1: "buscar email" → genera código
   → Paso 2: "descargar PDF" → genera código
   → ...

5. SANDBOX ejecuta cada paso
   → Docker run con límites
   → Captura resultado
   → Devuelve al orquestador

6. CHAIN-OF-WORK se va guardando
   → INSERT INTO chain_of_work por cada paso

7. RESULTADO final
   → UPDATE ejecuciones SET status='SUCCESS'
   → Si éxito: guardar en caché
   → Devolver a usuario

8. USUARIO ve resultado
   → CLI muestra: ✅ SUCCESS
   → Puede ver chain-of-work completo
```

---

## SIGUIENTE PASO

Ahora que entiendes la **ARQUITECTURA COMPLETA**:

### ¿Qué sigue?

1. **Revisar dudas** de cualquier módulo
2. **Empezar a construir** con Claude Code
3. **Decidir qué construir primero** (MVP)

¿Por dónde quieres empezar? 🚀
