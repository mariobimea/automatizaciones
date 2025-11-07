# Generación de Código On-the-Fly: Investigación Completa

**Fecha**: 2025-10-21
**Objetivo**: Diseñar un sistema que genere y ejecute código Python dinámicamente usando LLMs

---

## RESUMEN EJECUTIVO

Un sistema de generación de código on-the-fly permite que agentes de IA:
1. **Reciban tareas** en lenguaje natural
2. **Generen código Python** paso a paso usando LLMs (GPT-4, Claude)
3. **Ejecuten código** de forma segura en sandboxes aislados
4. **Aprendan de ejecuciones exitosas** (determinismo/caché)
5. **Mantengan trazabilidad completa** (Chain-of-Work)

**Complejidad**: Alta
**Tiempo estimado MVP**: 2-3 meses
**Viabilidad**: Muy alta (múltiples implementaciones exitosas en producción)

---

## PARTE 1: ARQUITECTURA GENERAL

### 1.1 Componentes Clave

```
┌─────────────────────────────────────────────────────────────┐
│                    SISTEMA COMPLETO                          │
└─────────────────────────────────────────────────────────────┘

[1] INPUT LAYER
    │
    ├─ Usuario: "Genera facturas PDF desde Excel"
    │
    └─ Input Parser: Convierte lenguaje natural → task structure

[2] ORCHESTRATOR (Cerebro del sistema)
    │
    ├─ Task Analyzer: Analiza complejidad de la tarea
    ├─ Cache Lookup: ¿Ya existe código para esto?
    │   ├─ Hash exacto → Reutilizar código
    │   └─ Similitud semántica → Adaptar código existente
    │
    └─ Decision Engine:
        ├─ Usar Template (tareas simples repetitivas)
        ├─ Usar Código Cacheado (tarea idéntica anterior)
        └─ Generar Nuevo (LLM)

[3] CODE GENERATOR (LLM-based)
    │
    ├─ Prompt Engineering: Construye prompt contextual
    ├─ LLM API Call: GPT-4 / Claude Sonnet
    ├─ Code Validator: Valida sintaxis antes de ejecutar
    │   ├─ AST parsing (Abstract Syntax Tree)
    │   ├─ Security checks (no imports peligrosos)
    │   └─ Linting básico
    │
    └─ Step-by-Step Generation:
        ├─ Paso 1: Leer archivo Excel
        ├─ Paso 2: Procesar datos
        └─ Paso 3: Generar PDF

[4] SANDBOX EXECUTOR
    │
    ├─ Docker Container / Firecracker microVM
    ├─ Resource Limits: CPU, RAM, Timeout
    ├─ Network Isolation: Sin acceso red (o controlado)
    ├─ Filesystem: Read-only excepto /sandbox
    │
    └─ Execution Monitor:
        ├─ Captura stdout/stderr
        ├─ Detecta errores
        └─ Mide performance (tiempo, memoria)

[5] ERROR HANDLER & RETRY
    │
    ├─ Error Detector: Analiza traceback
    ├─ Self-Correction: LLM corrige código con error feedback
    ├─ Retry Mechanism: Máx 3 intentos con exponential backoff
    │
    └─ Escalation: Si falla 3x → Humano revisa

[6] CHAIN-OF-WORK LOGGER
    │
    ├─ Log cada paso de ejecución
    ├─ Guarda razonamiento del LLM
    ├─ Registra código generado + resultado
    │
    └─ Audit Trail completo en PostgreSQL

[7] LEARNING SYSTEM (Determinismo)
    │
    ├─ Success Detector: ¿Código funcionó?
    ├─ Code Cache: Guarda código exitoso
    ├─ Hash Generator: SHA-256 de input → código mapping
    │
    └─ Similarity Matcher:
        ├─ Embeddings de tarea (similitud semántica)
        └─ Encuentra código similar para adaptar
```

---

## PARTE 2: GENERACIÓN DE CÓDIGO CON LLM

### 2.1 Estrategias de Prompting (Estado del Arte 2025)

#### A. **Prompt Step-by-Step (Incremental Generation)**

**Concepto**: No generar todo el código de golpe, sino paso a paso.

**Ejemplo**:

```
PROMPT PARA GPT-4:

You are an expert Python developer. Generate code step-by-step for this task:

TASK: "Generate PDF invoices from Excel file"

Current step: Step 1 of 4 - Read Excel file
Input file path: /input/invoices.xlsx
Expected columns: id, client_name, amount, date

Requirements:
- Use pandas to read Excel
- Handle missing columns gracefully
- Return DataFrame

Generate ONLY the code for Step 1. Be concise.
```

**Ventajas**:
- ✅ LLM genera código más simple y correcto
- ✅ Fácil debug (sabes en qué paso falló)
- ✅ Puedes validar cada paso antes de continuar

**Desventajas**:
- ⚠️ Más llamadas a LLM (más caro)
- ⚠️ Orquestación más compleja

#### B. **Self-Planning Approach**

**Concepto**: LLM primero crea un plan, luego implementa cada parte.

```python
# Paso 1: Pedir plan
plan_prompt = """
Task: Generate PDF invoices from Excel

Create a high-level plan with steps needed to accomplish this.
Format: Numbered list of steps with clear objectives.
"""

plan_response = llm.invoke(plan_prompt)
# Output:
# 1. Read Excel with pandas
# 2. Validate data (check required columns)
# 3. For each row, generate PDF using reportlab
# 4. Save PDFs to /output folder

# Paso 2: Implementar cada paso del plan
for step in plan_response.steps:
    code = llm.invoke(f"Generate Python code for: {step}")
    execute_in_sandbox(code)
```

**Ventajas**:
- ✅ Estructura clara y lógica
- ✅ Fácil seguimiento para humanos (Chain-of-Work)
- ✅ Validación del plan antes de ejecutar

#### C. **Chain-of-Thought Prompting**

**Concepto**: Pedir al LLM que "piense en voz alta" antes de generar código.

```
PROMPT:

Task: Generate PDF invoices from Excel file at /input/invoices.xlsx

Before writing code, explain:
1. What libraries you'll use and why
2. What edge cases you need to handle
3. How you'll structure the code

Then generate the complete Python code.
```

**Ventajas**:
- ✅ Código más robusto (LLM considera edge cases)
- ✅ Transparencia (sabes el razonamiento)
- ✅ Útil para Chain-of-Work

#### D. **Few-Shot Prompting with Examples**

**Concepto**: Mostrar ejemplos de código exitoso previo.

```python
prompt = f"""
You are a Python code generator. Here are examples of good code:

EXAMPLE 1:
Task: Read CSV and filter rows
Code:
import pandas as pd
df = pd.read_csv('/input/data.csv')
filtered = df[df['amount'] > 100]
filtered.to_csv('/output/result.csv', index=False)

EXAMPLE 2:
Task: Generate simple PDF
Code:
from reportlab.pdfgen import canvas
pdf = canvas.Canvas('/output/report.pdf')
pdf.drawString(100, 750, "Hello World")
pdf.save()

NOW YOUR TASK:
{user_task}

Generate similar clean, working Python code.
"""
```

**Ventajas**:
- ✅ LLM aprende estilo y patrones
- ✅ Reduce errores comunes
- ✅ Código más consistente

---

### 2.2 Best Practices para Code Generation (2025)

#### ✅ **1. Especifica el runtime environment**

```python
prompt = f"""
Generate Python 3.11 code that will run in a Docker container with:
- pandas==2.0.0
- reportlab==4.0.0
- openpyxl==3.1.0

No external network access. Files in /input (read-only), output to /output.

Task: {task}
"""
```

**Por qué**: LLM sabe qué librerías puede usar y evita imports no disponibles.

#### ✅ **2. Pide código auto-contenido**

```python
prompt = f"""
Generate a SINGLE, self-contained Python script (no imports from custom modules).

Task: {task}

Requirements:
- All code in one file
- No external dependencies beyond stdlib and: pandas, reportlab
- Include error handling with try/except
"""
```

**Por qué**: Evita dependencias complejas difíciles de resolver en sandbox.

#### ✅ **3. Solicita logging explícito**

```python
prompt = f"""
Generate Python code with explicit logging:

- Log each major step with print() statements
- Log input parameters at start
- Log success/failure at end

Example:
print("STEP 1: Reading Excel file...")
df = pd.read_excel('/input/data.xlsx')
print(f"STEP 1 COMPLETE: Loaded {len(df)} rows")

Task: {task}
"""
```

**Por qué**: Facilita debugging y Chain-of-Work.

#### ✅ **4. Valida código antes de ejecutar**

```python
import ast

def validate_generated_code(code: str) -> dict:
    """Valida código Python antes de ejecutar"""

    # 1. Check syntax con AST
    try:
        ast.parse(code)
    except SyntaxError as e:
        return {"valid": False, "error": f"Syntax error: {e}"}

    # 2. Security checks
    dangerous_imports = ['os.system', 'subprocess', 'eval', 'exec', '__import__']
    for danger in dangerous_imports:
        if danger in code:
            return {"valid": False, "error": f"Dangerous function: {danger}"}

    # 3. Check for required patterns
    if '/input/' not in code and '/output/' not in code:
        return {"valid": False, "error": "Missing input/output paths"}

    return {"valid": True}

# Uso
code = llm.generate_code(task)
validation = validate_generated_code(code)

if not validation["valid"]:
    # Retry con feedback
    code = llm.generate_code(
        task,
        feedback=f"Previous code had error: {validation['error']}"
    )
```

#### ✅ **5. Implementa Self-Review**

```python
def generate_with_self_review(task: str) -> str:
    """LLM genera código y luego lo auto-revisa"""

    # Paso 1: Generar código
    code_v1 = llm.invoke(f"Generate Python code for: {task}")

    # Paso 2: LLM revisa su propio código
    review_prompt = f"""
    Review this Python code for the task: {task}

    Code:
    {code_v1}

    Check for:
    1. Syntax errors
    2. Logic errors
    3. Missing error handling
    4. Edge cases not handled

    If you find issues, provide corrected code. Otherwise, return APPROVED.
    """

    review = llm.invoke(review_prompt)

    if "APPROVED" in review:
        return code_v1
    else:
        return extract_code_from_review(review)
```

---

## PARTE 3: SANDBOX EXECUTION

### 3.1 Opciones de Sandbox

| Tecnología | Aislamiento | Startup Time | Complejidad | Coste | Recomendación |
|------------|-------------|--------------|-------------|-------|---------------|
| **Docker** | Bueno (kernel compartido) | ~1-2s | Media | Bajo | ✅ **MVP/SMB** |
| **Firecracker microVM** | Excelente (VM real) | ~200ms | Alta | Medio | ✅ **Producción/Scale** |
| **Kubernetes** | Bueno | ~3-5s | Muy alta | Alto | ⚠️ Solo enterprise |
| **Podman** | Bueno | ~1-2s | Media | Bajo | ✅ Alternativa Docker |

**Recomendación para tu caso**: Empieza con **Docker** (simple, probado), evoluciona a **Firecracker** si necesitas escalar.

---

### 3.2 Configuración Docker Sandbox (Producción-Ready)

#### A. **Dockerfile optimizado**

```dockerfile
# Dockerfile para Python sandbox
FROM python:3.11-slim

# Security: Non-root user
RUN useradd -m -u 1000 sandboxuser

# Install dependencies
RUN pip install --no-cache-dir \
    pandas==2.0.0 \
    openpyxl==3.1.0 \
    reportlab==4.0.0 \
    pypdf2==3.0.1 \
    requests==2.31.0 \
    beautifulsoup4==4.12.0

# Create directories
RUN mkdir -p /input /output /sandbox && \
    chown -R sandboxuser:sandboxuser /input /output /sandbox

# Set working directory
WORKDIR /sandbox

# Switch to non-root user
USER sandboxuser

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Default command
CMD ["python", "-u", "/sandbox/script.py"]
```

#### B. **Docker Compose con límites de recursos**

```yaml
# docker-compose.yml
version: '3.8'

services:
  python-sandbox:
    build: ./sandbox
    container_name: code-executor

    # Resource limits (CRÍTICO para seguridad)
    deploy:
      resources:
        limits:
          cpus: '0.5'        # Máx 50% de 1 CPU
          memory: 512M       # Máx 512MB RAM
        reservations:
          cpus: '0.25'
          memory: 256M

    # Security options
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETUID
      - SETGID

    # Network: disable by default
    network_mode: "none"

    # Filesystem
    volumes:
      - ./input:/input:ro          # Read-only
      - ./output:/output:rw        # Read-write
      - ./sandbox:/sandbox:rw

    # Read-only root filesystem
    read_only: true
    tmpfs:
      - /tmp:size=64M,mode=1777

    # PID limits
    pids_limit: 100

    # Restart policy
    restart: "no"
```

#### C. **Executor Python con timeout**

```python
import docker
import time
from typing import Dict, Any

class SandboxExecutor:
    def __init__(self):
        self.client = docker.from_env()
        self.image_name = "python-sandbox:latest"

    def execute_code(
        self,
        code: str,
        timeout: int = 30,
        input_files: Dict[str, bytes] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta código Python en sandbox Docker

        Args:
            code: Código Python a ejecutar
            timeout: Timeout en segundos (default 30s)
            input_files: Dict de {filename: content} para /input/

        Returns:
            Dict con stdout, stderr, exit_code, execution_time
        """

        # 1. Preparar archivos input
        if input_files:
            for filename, content in input_files.items():
                with open(f"./input/{filename}", "wb") as f:
                    f.write(content)

        # 2. Escribir código a ejecutar
        with open("./sandbox/script.py", "w") as f:
            f.write(code)

        # 3. Crear container
        container = self.client.containers.create(
            image=self.image_name,
            command=["python", "-u", "/sandbox/script.py"],
            detach=True,

            # Límites de recursos
            mem_limit="512m",
            cpu_quota=50000,  # 50% de 1 CPU
            pids_limit=100,

            # Network disabled
            network_disabled=True,

            # Volumes
            volumes={
                "./input": {"bind": "/input", "mode": "ro"},
                "./output": {"bind": "/output", "mode": "rw"},
                "./sandbox": {"bind": "/sandbox", "mode": "rw"}
            },

            # Security
            security_opt=["no-new-privileges"],
            cap_drop=["ALL"],
            read_only=True,
            tmpfs={"/tmp": "size=64M,mode=1777"}
        )

        # 4. Start container
        start_time = time.time()
        container.start()

        # 5. Wait with timeout
        try:
            exit_code = container.wait(timeout=timeout)["StatusCode"]
            execution_time = time.time() - start_time

            # 6. Obtener logs
            stdout = container.logs(stdout=True, stderr=False).decode('utf-8')
            stderr = container.logs(stdout=False, stderr=True).decode('utf-8')

            # 7. Cleanup
            container.remove(force=True)

            return {
                "success": exit_code == 0,
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "execution_time": execution_time,
                "timeout": False
            }

        except docker.errors.DockerException as e:
            # Timeout o error
            container.kill()
            container.remove(force=True)

            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "execution_time": timeout,
                "timeout": True
            }

# USO
executor = SandboxExecutor()

code = """
import pandas as pd

df = pd.read_excel('/input/data.xlsx')
print(f"Loaded {len(df)} rows")

df['total'] = df['quantity'] * df['price']
df.to_csv('/output/result.csv', index=False)
print("SUCCESS")
"""

result = executor.execute_code(
    code=code,
    timeout=30,
    input_files={"data.xlsx": excel_file_bytes}
)

if result["success"]:
    print("✅ Código ejecutado correctamente")
    print(result["stdout"])
else:
    print("❌ Error en ejecución")
    print(result["stderr"])
```

---

### 3.3 Security Best Practices (Docker Sandbox)

#### ✅ **1. User no root**
```dockerfile
USER sandboxuser  # NUNCA root
```

#### ✅ **2. Filesystem read-only**
```yaml
read_only: true
tmpfs:
  - /tmp:size=64M
```

#### ✅ **3. Network disabled por defecto**
```yaml
network_mode: "none"
```

Si necesitas red controlada:
```yaml
networks:
  sandbox_net:
    driver: bridge

# Firewall rules
iptables:
  - ALLOW https://api.openai.com
  - DENY all other
```

#### ✅ **4. Limits de recursos estrictos**
```yaml
mem_limit: 512M
cpu_quota: 50000  # 50% CPU
pids_limit: 100
ulimits:
  nofile: 1024
  nproc: 64
```

#### ✅ **5. Timeout SIEMPRE**
```python
# NUNCA ejecución sin timeout
container.wait(timeout=30)  # Máx 30 segundos
```

#### ✅ **6. AppArmor/SELinux profiles**
```yaml
security_opt:
  - apparmor=docker-default
  - no-new-privileges:true
```

---

## PARTE 4: DETERMINISMO Y CACHÉ

### 4.1 Sistema de Caché Basado en Hash

**Concepto**: Si input es idéntico → reusar código exitoso.

```python
import hashlib
import json
from typing import Dict, Any, Optional

class CodeCache:
    def __init__(self, db_connection):
        self.db = db_connection

    def generate_hash(self, task_input: Dict[str, Any]) -> str:
        """
        Genera hash SHA-256 del input de la tarea

        task_input = {
            "task_description": "Generate PDF invoices",
            "input_schema": {"columns": ["id", "name", "amount"]},
            "output_format": "pdf"
        }
        """
        # Serializar input de forma consistente
        serialized = json.dumps(task_input, sort_keys=True)

        # Hash SHA-256
        return hashlib.sha256(serialized.encode()).hexdigest()

    def get_cached_code(self, task_hash: str) -> Optional[str]:
        """Busca código exitoso para este hash exacto"""

        query = """
        SELECT code, success_count, last_used
        FROM code_cache
        WHERE task_hash = %s AND success = true
        ORDER BY success_count DESC
        LIMIT 1
        """

        result = self.db.execute(query, (task_hash,))

        if result:
            # Actualizar last_used
            self.db.execute(
                "UPDATE code_cache SET last_used = NOW() WHERE task_hash = %s",
                (task_hash,)
            )
            return result["code"]

        return None

    def save_successful_code(
        self,
        task_hash: str,
        code: str,
        task_description: str,
        execution_time: float
    ):
        """Guarda código que funcionó"""

        query = """
        INSERT INTO code_cache (
            task_hash, code, task_description,
            success, success_count, execution_time, created_at
        )
        VALUES (%s, %s, %s, true, 1, %s, NOW())
        ON CONFLICT (task_hash) DO UPDATE SET
            success_count = code_cache.success_count + 1,
            last_used = NOW(),
            execution_time = EXCLUDED.execution_time
        """

        self.db.execute(query, (task_hash, code, task_description, execution_time))

# SCHEMA PostgreSQL
"""
CREATE TABLE code_cache (
    id SERIAL PRIMARY KEY,
    task_hash VARCHAR(64) UNIQUE NOT NULL,
    code TEXT NOT NULL,
    task_description TEXT,
    success BOOLEAN DEFAULT true,
    success_count INTEGER DEFAULT 1,
    execution_time FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    last_used TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_task_hash ON code_cache(task_hash);
CREATE INDEX idx_success ON code_cache(success) WHERE success = true;
"""
```

---

### 4.2 Caché Semántico (Similarity Matching)

**Concepto**: Incluso si input NO es idéntico, buscar casos similares.

```python
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Tuple

class SemanticCodeCache:
    def __init__(self, db_connection):
        self.db = db_connection
        # Modelo para embeddings
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def get_embedding(self, text: str) -> List[float]:
        """Genera embedding vectorial del texto"""
        return self.model.encode(text).tolist()

    def find_similar_tasks(
        self,
        task_description: str,
        threshold: float = 0.85,
        top_k: int = 3
    ) -> List[Tuple[str, float, str]]:
        """
        Busca tareas similares usando similitud de coseno

        Returns:
            List de (code, similarity_score, original_description)
        """

        # 1. Embedding de la tarea nueva
        query_embedding = self.get_embedding(task_description)

        # 2. Buscar en DB (usando pgvector o similitud en Python)
        # Opción A: Si usas pgvector en PostgreSQL
        query = """
        SELECT code, task_description, embedding,
               1 - (embedding <=> %s::vector) as similarity
        FROM code_cache
        WHERE success = true
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        """

        results = self.db.execute(query, (query_embedding, query_embedding, top_k))

        # Filtrar por threshold
        similar = [
            (r["code"], r["similarity"], r["task_description"])
            for r in results
            if r["similarity"] >= threshold
        ]

        return similar

    def save_with_embedding(
        self,
        task_hash: str,
        code: str,
        task_description: str
    ):
        """Guarda código con embedding para búsqueda semántica"""

        embedding = self.get_embedding(task_description)

        query = """
        INSERT INTO code_cache (
            task_hash, code, task_description, embedding, success
        )
        VALUES (%s, %s, %s, %s, true)
        """

        self.db.execute(query, (task_hash, code, task_description, embedding))

# SCHEMA con pgvector
"""
-- Instalar pgvector extension
CREATE EXTENSION vector;

ALTER TABLE code_cache ADD COLUMN embedding vector(384);
CREATE INDEX ON code_cache USING ivfflat (embedding vector_cosine_ops);
"""
```

**Uso combinado**:

```python
def get_code_for_task(task_description: str, task_input: dict) -> str:
    """
    Sistema inteligente de caché:
    1. Buscar match exacto (hash)
    2. Si no, buscar similar (embeddings)
    3. Si no, generar nuevo con LLM
    """

    cache = CodeCache(db)
    semantic_cache = SemanticCodeCache(db)

    # 1. Hash exacto
    task_hash = cache.generate_hash(task_input)
    exact_match = cache.get_cached_code(task_hash)

    if exact_match:
        print("✅ Cache HIT (exact match)")
        return exact_match

    # 2. Similitud semántica
    similar = semantic_cache.find_similar_tasks(task_description, threshold=0.85)

    if similar:
        print(f"⚡ Cache HIT (similar task, score={similar[0][1]:.2f})")
        # Adaptar código similar con LLM
        adapted_code = llm.adapt_code(
            base_code=similar[0][0],
            new_task=task_description,
            original_task=similar[0][2]
        )
        return adapted_code

    # 3. Generar nuevo
    print("🆕 Cache MISS - Generating new code")
    new_code = llm.generate_code(task_description)

    # Guardar para futuro
    cache.save_successful_code(task_hash, new_code, task_description, 0)
    semantic_cache.save_with_embedding(task_hash, new_code, task_description)

    return new_code
```

---

## PARTE 5: ERROR HANDLING & SELF-CORRECTION

### 5.1 Sistema de Retry con Feedback

```python
from typing import Dict, Any, Optional

class SelfCorrectingExecutor:
    def __init__(self, llm, sandbox):
        self.llm = llm
        self.sandbox = sandbox
        self.max_retries = 3

    def execute_with_retry(
        self,
        task: str,
        initial_code: str
    ) -> Dict[str, Any]:
        """
        Ejecuta código con auto-corrección en caso de error
        """

        code = initial_code
        chain_of_work = []

        for attempt in range(1, self.max_retries + 1):
            print(f"Attempt {attempt}/{self.max_retries}")

            # Ejecutar en sandbox
            result = self.sandbox.execute_code(code, timeout=30)

            # Log paso
            chain_of_work.append({
                "attempt": attempt,
                "code": code,
                "stdout": result["stdout"],
                "stderr": result["stderr"],
                "success": result["success"]
            })

            # Si funciona, terminar
            if result["success"]:
                return {
                    "success": True,
                    "code": code,
                    "result": result,
                    "attempts": attempt,
                    "chain_of_work": chain_of_work
                }

            # Si falla, pedir corrección al LLM
            if attempt < self.max_retries:
                print(f"❌ Error detected. Asking LLM to fix...")

                correction_prompt = f"""
                The following Python code failed:

                ```python
                {code}
                ```

                Error output:
                {result["stderr"]}

                Task was: {task}

                Fix the code to handle this error. Return ONLY the corrected code.
                """

                code = self.llm.invoke(correction_prompt)
                print("🔧 LLM generated corrected code")

        # Si llegamos aquí, fallaron todos los intentos
        return {
            "success": False,
            "error": "Max retries exceeded",
            "chain_of_work": chain_of_work
        }

# USO
executor = SelfCorrectingExecutor(llm=gpt4, sandbox=docker_executor)

result = executor.execute_with_retry(
    task="Generate PDF from Excel",
    initial_code=generated_code
)

if result["success"]:
    print(f"✅ Success after {result['attempts']} attempts")
else:
    print("❌ Failed after all retries - escalate to human")
```

---

### 5.2 Error Classification & Smart Retry

```python
import re
from enum import Enum

class ErrorType(Enum):
    SYNTAX = "syntax"
    IMPORT = "import"
    FILE_NOT_FOUND = "file_not_found"
    TYPE_ERROR = "type_error"
    TIMEOUT = "timeout"
    MEMORY = "memory"
    UNKNOWN = "unknown"

class ErrorAnalyzer:
    def classify_error(self, stderr: str) -> ErrorType:
        """Clasifica tipo de error del traceback"""

        if "SyntaxError" in stderr:
            return ErrorType.SYNTAX
        elif "ModuleNotFoundError" in stderr or "ImportError" in stderr:
            return ErrorType.IMPORT
        elif "FileNotFoundError" in stderr or "No such file" in stderr:
            return ErrorType.FILE_NOT_FOUND
        elif "TypeError" in stderr:
            return ErrorType.TYPE_ERROR
        elif "timeout" in stderr.lower():
            return ErrorType.TIMEOUT
        elif "MemoryError" in stderr or "Out of memory" in stderr:
            return ErrorType.MEMORY
        else:
            return ErrorType.UNKNOWN

    def should_retry(self, error_type: ErrorType) -> bool:
        """Decide si vale la pena reintentar"""

        # Errores que SÍ se pueden corregir con LLM
        retryable = [
            ErrorType.SYNTAX,
            ErrorType.TYPE_ERROR,
            ErrorType.FILE_NOT_FOUND,
            ErrorType.UNKNOWN
        ]

        # Errores de recursos NO son corregibles con código
        non_retryable = [
            ErrorType.TIMEOUT,  # Necesita optimización manual
            ErrorType.MEMORY,   # Necesita más recursos
            ErrorType.IMPORT    # Librería no disponible
        ]

        return error_type in retryable

    def generate_fix_prompt(
        self,
        code: str,
        error_type: ErrorType,
        stderr: str
    ) -> str:
        """Genera prompt específico según tipo de error"""

        if error_type == ErrorType.SYNTAX:
            return f"""
            Fix the syntax error in this Python code:

            {code}

            Error: {stderr}

            Return corrected code only.
            """

        elif error_type == ErrorType.FILE_NOT_FOUND:
            return f"""
            This code is looking for a file that doesn't exist:

            {code}

            Error: {stderr}

            Available files are in /input/ directory.
            Fix the code to handle missing files gracefully.
            """

        elif error_type == ErrorType.TYPE_ERROR:
            return f"""
            Fix the type mismatch in this code:

            {code}

            Error: {stderr}

            Ensure proper type conversions and validations.
            """

        else:
            return f"""
            Debug and fix this code:

            {code}

            Error: {stderr}

            Provide corrected version.
            """

# Integración
class SmartRetryExecutor(SelfCorrectingExecutor):
    def __init__(self, llm, sandbox):
        super().__init__(llm, sandbox)
        self.error_analyzer = ErrorAnalyzer()

    def execute_with_smart_retry(self, task: str, code: str):
        """Retry inteligente según tipo de error"""

        for attempt in range(1, self.max_retries + 1):
            result = self.sandbox.execute_code(code)

            if result["success"]:
                return {"success": True, "code": code, "result": result}

            # Analizar error
            error_type = self.error_analyzer.classify_error(result["stderr"])

            if not self.error_analyzer.should_retry(error_type):
                return {
                    "success": False,
                    "error": f"Non-retryable error: {error_type.value}",
                    "suggestion": "Escalate to human or adjust resources"
                }

            # Generar fix específico
            fix_prompt = self.error_analyzer.generate_fix_prompt(
                code, error_type, result["stderr"]
            )

            code = self.llm.invoke(fix_prompt)

        return {"success": False, "error": "Max retries exceeded"}
```

---

## PARTE 6: CHAIN-OF-WORK (Trazabilidad Completa)

### 6.1 Schema de Base de Datos

```sql
-- PostgreSQL Schema para Chain-of-Work

-- 1. Tabla de trabajadores/agentes
CREATE TABLE workers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2. Tabla de ejecuciones (una por tarea)
CREATE TABLE executions (
    id SERIAL PRIMARY KEY,
    worker_id INTEGER REFERENCES workers(id),
    task_description TEXT NOT NULL,
    task_input JSONB,
    status VARCHAR(20) CHECK (status IN ('pending', 'running', 'success', 'failed')),
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    total_duration FLOAT,
    error_message TEXT
);

-- 3. Chain-of-Work steps
CREATE TABLE chain_of_work (
    id SERIAL PRIMARY KEY,
    execution_id INTEGER REFERENCES executions(id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    step_type VARCHAR(50) NOT NULL, -- 'plan', 'code_gen', 'execution', 'retry', 'validation'

    -- Qué pasó en este paso
    action TEXT NOT NULL,
    reasoning TEXT, -- Por qué el agente decidió esto

    -- Input/Output del paso
    input_data JSONB,
    output_data JSONB,

    -- Código generado (si aplica)
    code_generated TEXT,

    -- Resultado de ejecución (si aplica)
    stdout TEXT,
    stderr TEXT,
    exit_code INTEGER,

    -- Metadata
    llm_model VARCHAR(50),
    llm_tokens_used INTEGER,
    execution_time FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(execution_id, step_number)
);

CREATE INDEX idx_execution_id ON chain_of_work(execution_id);
CREATE INDEX idx_step_type ON chain_of_work(step_type);

-- 4. Código cacheado (ya visto antes)
CREATE TABLE code_cache (
    id SERIAL PRIMARY KEY,
    task_hash VARCHAR(64) UNIQUE NOT NULL,
    code TEXT NOT NULL,
    task_description TEXT,
    embedding vector(384), -- Para búsqueda semántica
    success BOOLEAN DEFAULT true,
    success_count INTEGER DEFAULT 1,
    execution_time FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    last_used TIMESTAMP DEFAULT NOW()
);
```

---

### 6.2 Logger de Chain-of-Work

```python
from typing import Optional, Dict, Any
import time

class ChainOfWorkLogger:
    def __init__(self, db_connection):
        self.db = db_connection
        self.current_execution_id: Optional[int] = None
        self.step_counter = 0

    def start_execution(
        self,
        worker_id: int,
        task_description: str,
        task_input: Dict[str, Any]
    ) -> int:
        """Inicia nueva ejecución"""

        query = """
        INSERT INTO executions (worker_id, task_description, task_input, status)
        VALUES (%s, %s, %s, 'running')
        RETURNING id
        """

        result = self.db.execute(
            query,
            (worker_id, task_description, json.dumps(task_input))
        )

        self.current_execution_id = result["id"]
        self.step_counter = 0

        return self.current_execution_id

    def log_step(
        self,
        step_type: str,
        action: str,
        reasoning: Optional[str] = None,
        code_generated: Optional[str] = None,
        stdout: Optional[str] = None,
        stderr: Optional[str] = None,
        exit_code: Optional[int] = None,
        input_data: Optional[Dict] = None,
        output_data: Optional[Dict] = None,
        llm_model: Optional[str] = None,
        llm_tokens: Optional[int] = None,
        execution_time: Optional[float] = None
    ):
        """Log un paso del Chain-of-Work"""

        self.step_counter += 1

        query = """
        INSERT INTO chain_of_work (
            execution_id, step_number, step_type, action, reasoning,
            input_data, output_data, code_generated,
            stdout, stderr, exit_code,
            llm_model, llm_tokens_used, execution_time
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        self.db.execute(query, (
            self.current_execution_id,
            self.step_counter,
            step_type,
            action,
            reasoning,
            json.dumps(input_data) if input_data else None,
            json.dumps(output_data) if output_data else None,
            code_generated,
            stdout,
            stderr,
            exit_code,
            llm_model,
            llm_tokens,
            execution_time
        ))

    def complete_execution(self, status: str, error_message: Optional[str] = None):
        """Marca ejecución como completada"""

        query = """
        UPDATE executions
        SET status = %s,
            completed_at = NOW(),
            total_duration = EXTRACT(EPOCH FROM (NOW() - created_at)),
            error_message = %s
        WHERE id = %s
        """

        self.db.execute(query, (status, error_message, self.current_execution_id))

# USO COMPLETO
def execute_task_with_full_logging(task: str):
    """Ejemplo completo de ejecución con logging"""

    logger = ChainOfWorkLogger(db)

    # 1. Iniciar ejecución
    execution_id = logger.start_execution(
        worker_id=1,
        task_description=task,
        task_input={"task": task}
    )

    try:
        # 2. Paso: Generar plan
        start = time.time()
        plan = llm.invoke(f"Create a plan for: {task}")

        logger.log_step(
            step_type="plan",
            action="Generated execution plan",
            reasoning="Breaking down task into steps for clarity",
            output_data={"plan": plan},
            llm_model="gpt-4",
            llm_tokens=150,
            execution_time=time.time() - start
        )

        # 3. Paso: Generar código
        start = time.time()
        code = llm.invoke(f"Generate Python code for: {task}")

        logger.log_step(
            step_type="code_generation",
            action="Generated Python code",
            reasoning="Implementing solution based on plan",
            code_generated=code,
            llm_model="gpt-4",
            llm_tokens=300,
            execution_time=time.time() - start
        )

        # 4. Paso: Ejecutar código
        start = time.time()
        result = sandbox.execute_code(code)

        logger.log_step(
            step_type="execution",
            action="Executed generated code in sandbox",
            reasoning="Running code in isolated Docker container",
            stdout=result["stdout"],
            stderr=result["stderr"],
            exit_code=result["exit_code"],
            execution_time=time.time() - start
        )

        if result["success"]:
            # 5. Paso: Validación
            logger.log_step(
                step_type="validation",
                action="Validated output",
                reasoning="Checking if output meets requirements",
                output_data={"validation": "passed"}
            )

            logger.complete_execution(status="success")

        else:
            # Retry con corrección
            logger.log_step(
                step_type="retry",
                action="Detected error, requesting fix from LLM",
                reasoning=f"Code failed with: {result['stderr'][:100]}",
                input_data={"error": result["stderr"]}
            )

            # ... más pasos de retry ...

    except Exception as e:
        logger.complete_execution(status="failed", error_message=str(e))
        raise
```

---

## PARTE 7: ARQUITECTURA COMPLETA DEL SISTEMA

### 7.1 Orquestador Principal

```python
from typing import Dict, Any, Optional
import hashlib
import json

class CodeGeneratorOrchestrator:
    """
    Orquestador principal que coordina todo el sistema
    """

    def __init__(
        self,
        llm_client,
        sandbox_executor,
        code_cache,
        semantic_cache,
        chain_logger,
        db_connection
    ):
        self.llm = llm_client
        self.sandbox = sandbox_executor
        self.cache = code_cache
        self.semantic = semantic_cache
        self.logger = chain_logger
        self.db = db_connection

    def execute_task(
        self,
        task_description: str,
        task_input: Dict[str, Any],
        worker_id: int = 1
    ) -> Dict[str, Any]:
        """
        Punto de entrada principal para ejecutar una tarea

        Flujo:
        1. Buscar en caché (hash exacto)
        2. Si no, buscar similar (embeddings)
        3. Si no, generar con LLM
        4. Ejecutar en sandbox
        5. Si falla, retry con auto-corrección
        6. Guardar resultado exitoso en caché
        7. Retornar Chain-of-Work completo
        """

        # Iniciar logging
        execution_id = self.logger.start_execution(
            worker_id=worker_id,
            task_description=task_description,
            task_input=task_input
        )

        try:
            # FASE 1: Búsqueda en caché
            code = self._get_code_from_cache_or_generate(
                task_description,
                task_input
            )

            # FASE 2: Ejecución con retry
            result = self._execute_with_retry(
                task_description=task_description,
                code=code,
                max_retries=3
            )

            # FASE 3: Guardar resultado exitoso
            if result["success"]:
                self._save_to_cache(task_description, task_input, code)
                self.logger.complete_execution(status="success")
            else:
                self.logger.complete_execution(
                    status="failed",
                    error_message=result.get("error")
                )

            # Retornar resultado + Chain-of-Work
            return {
                **result,
                "execution_id": execution_id,
                "chain_of_work": self._get_chain_of_work(execution_id)
            }

        except Exception as e:
            self.logger.complete_execution(status="failed", error_message=str(e))
            raise

    def _get_code_from_cache_or_generate(
        self,
        task_description: str,
        task_input: Dict[str, Any]
    ) -> str:
        """Intenta obtener código de caché o genera nuevo"""

        # 1. Hash exacto
        task_hash = self.cache.generate_hash(task_input)
        cached = self.cache.get_cached_code(task_hash)

        if cached:
            self.logger.log_step(
                step_type="cache_lookup",
                action="Found exact match in cache",
                reasoning=f"Hash {task_hash} matched previous execution",
                code_generated=cached
            )
            return cached

        # 2. Similitud semántica
        similar = self.semantic.find_similar_tasks(
            task_description,
            threshold=0.85,
            top_k=1
        )

        if similar:
            base_code = similar[0][0]
            similarity_score = similar[0][1]

            self.logger.log_step(
                step_type="cache_lookup",
                action=f"Found similar task (score={similarity_score:.2f})",
                reasoning="Adapting existing code to new task",
                input_data={"base_code": base_code}
            )

            # Adaptar código similar
            adapted = self._adapt_code(base_code, task_description)
            return adapted

        # 3. Generar desde cero
        self.logger.log_step(
            step_type="cache_lookup",
            action="No cache match found",
            reasoning="Generating new code with LLM"
        )

        return self._generate_new_code(task_description, task_input)

    def _generate_new_code(
        self,
        task_description: str,
        task_input: Dict[str, Any]
    ) -> str:
        """Genera código nuevo con LLM"""

        import time
        start = time.time()

        # Construir prompt
        prompt = f"""
        You are an expert Python developer. Generate clean, working Python code.

        TASK: {task_description}

        INPUT SPECIFICATION:
        {json.dumps(task_input, indent=2)}

        ENVIRONMENT:
        - Python 3.11
        - Available libraries: pandas, openpyxl, reportlab, requests
        - Input files in /input/ (read-only)
        - Output files to /output/
        - No network access

        REQUIREMENTS:
        - Single self-contained script
        - Include error handling
        - Log progress with print() statements
        - Handle edge cases gracefully

        Return ONLY the Python code, no explanations.
        """

        code = self.llm.invoke(prompt)

        self.logger.log_step(
            step_type="code_generation",
            action="Generated new code with LLM",
            reasoning="No cached code available",
            code_generated=code,
            llm_model="gpt-4",
            execution_time=time.time() - start
        )

        return code

    def _adapt_code(self, base_code: str, new_task: str) -> str:
        """Adapta código existente a nueva tarea"""

        prompt = f"""
        Adapt this working Python code to a new task:

        ORIGINAL CODE:
        {base_code}

        NEW TASK:
        {new_task}

        Modify the code to accomplish the new task while preserving the structure.
        Return ONLY the adapted code.
        """

        adapted = self.llm.invoke(prompt)

        self.logger.log_step(
            step_type="code_adaptation",
            action="Adapted similar code to new task",
            reasoning="Reusing proven patterns",
            code_generated=adapted,
            llm_model="gpt-4"
        )

        return adapted

    def _execute_with_retry(
        self,
        task_description: str,
        code: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Ejecuta código con retry automático"""

        for attempt in range(1, max_retries + 1):
            import time
            start = time.time()

            # Ejecutar
            result = self.sandbox.execute_code(code, timeout=30)

            self.logger.log_step(
                step_type="execution",
                action=f"Executed code (attempt {attempt})",
                reasoning="Running in Docker sandbox",
                stdout=result["stdout"],
                stderr=result["stderr"],
                exit_code=result.get("exit_code", -1),
                execution_time=time.time() - start
            )

            if result["success"]:
                return {
                    "success": True,
                    "code": code,
                    "result": result,
                    "attempts": attempt
                }

            # Si falla y quedan intentos, corregir
            if attempt < max_retries:
                self.logger.log_step(
                    step_type="retry",
                    action="Requesting code correction from LLM",
                    reasoning=f"Execution failed: {result['stderr'][:200]}"
                )

                code = self._fix_code(code, result["stderr"], task_description)

        return {
            "success": False,
            "error": "Max retries exceeded",
            "last_stderr": result["stderr"]
        }

    def _fix_code(self, code: str, error: str, task: str) -> str:
        """Pide al LLM que corrija código con error"""

        prompt = f"""
        Fix this Python code that failed:

        CODE:
        {code}

        ERROR:
        {error}

        TASK:
        {task}

        Return the corrected code only.
        """

        fixed = self.llm.invoke(prompt)

        self.logger.log_step(
            step_type="code_correction",
            action="LLM corrected code",
            reasoning="Auto-fixing execution errors",
            code_generated=fixed,
            llm_model="gpt-4"
        )

        return fixed

    def _save_to_cache(
        self,
        task_description: str,
        task_input: Dict[str, Any],
        code: str
    ):
        """Guarda código exitoso en caché"""

        task_hash = self.cache.generate_hash(task_input)

        self.cache.save_successful_code(
            task_hash=task_hash,
            code=code,
            task_description=task_description,
            execution_time=0
        )

        self.semantic.save_with_embedding(
            task_hash=task_hash,
            code=code,
            task_description=task_description
        )

        self.logger.log_step(
            step_type="caching",
            action="Saved successful code to cache",
            reasoning="Enable reuse for future similar tasks"
        )

    def _get_chain_of_work(self, execution_id: int) -> list:
        """Obtiene Chain-of-Work completo"""

        query = """
        SELECT * FROM chain_of_work
        WHERE execution_id = %s
        ORDER BY step_number
        """

        return self.db.execute_all(query, (execution_id,))

# ============================================
# USO DEL ORQUESTADOR
# ============================================

# Setup
from openai import OpenAI

llm = OpenAI(api_key="...")
sandbox = SandboxExecutor()
cache = CodeCache(db)
semantic = SemanticCodeCache(db)
logger = ChainOfWorkLogger(db)

orchestrator = CodeGeneratorOrchestrator(
    llm_client=llm,
    sandbox_executor=sandbox,
    code_cache=cache,
    semantic_cache=semantic,
    chain_logger=logger,
    db_connection=db
)

# Ejecutar tarea
result = orchestrator.execute_task(
    task_description="Generate PDF invoices from Excel file",
    task_input={
        "input_file": "/input/invoices.xlsx",
        "columns": ["id", "client_name", "amount", "date"],
        "output_format": "pdf"
    },
    worker_id=1
)

if result["success"]:
    print("✅ Task completed successfully")
    print(f"Attempts: {result['attempts']}")
    print(f"Execution ID: {result['execution_id']}")

    # Ver Chain-of-Work
    for step in result["chain_of_work"]:
        print(f"Step {step['step_number']}: {step['action']}")
else:
    print("❌ Task failed")
    print(result["error"])
```

---

## PARTE 8: STACK TECNOLÓGICO RECOMENDADO

### 8.1 Para MVP (2-3 meses)

```
BACKEND:
├─ Python 3.11
├─ FastAPI (API REST)
├─ PostgreSQL 15 (datos + Chain-of-Work)
├─ Docker (sandbox básico)
├─ OpenAI API (GPT-4 para code generation)
└─ Celery + Redis (tasks asíncronas)

FRONTEND (opcional para MVP):
├─ React + TypeScript
├─ shadcn/ui (componentes)
└─ TanStack Query (data fetching)

INFRA:
├─ Docker Compose (desarrollo local)
└─ Railway / Render (deploy MVP)
```

### 8.2 Para Producción (6+ meses)

```
BACKEND:
├─ Python 3.11
├─ FastAPI + Pydantic v2
├─ PostgreSQL 15 + pgvector (semantic search)
├─ Firecracker microVMs (sandbox de producción)
├─ LangChain / LangGraph (orchestration)
├─ Anthropic Claude + OpenAI GPT-4 (multi-model)
└─ Celery + Redis (async tasks)

OBSERVABILITY:
├─ MLflow Tracing (LLM observability)
├─ Sentry (error tracking)
├─ Datadog / Grafana (metrics)
└─ PostgreSQL (Chain-of-Work audit logs)

CACHING:
├─ Redis (hot cache)
├─ PostgreSQL (code cache + embeddings)
└─ Sentence Transformers (embeddings)

FRONTEND:
├─ Next.js 14 (React framework)
├─ TypeScript
├─ shadcn/ui + Tailwind
├─ TanStack Query
└─ Vercel (hosting)

INFRA:
├─ AWS / GCP (cloud)
├─ Terraform (IaC)
├─ Kubernetes (orchestration)
└─ E2B (sandbox as a service - alternativa)
```

---

## PARTE 9: ROADMAP DE IMPLEMENTACIÓN

### Mes 1: Core Runtime + Básico

**Semana 1-2: Sandbox funcional**
- [ ] Dockerfile optimizado con Python + librerías
- [ ] SandboxExecutor con límites de recursos
- [ ] Tests básicos de ejecución

**Semana 3-4: Generación básica**
- [ ] Integración con OpenAI API
- [ ] Prompt engineering inicial
- [ ] Validación de código (AST parsing)
- [ ] Ejecución de código generado

**Entregable**: Sistema que genera código simple y lo ejecuta.

---

### Mes 2: Caché + Retry

**Semana 1-2: Sistema de caché**
- [ ] PostgreSQL schema (code_cache)
- [ ] Hash-based cache (SHA-256)
- [ ] Guardar código exitoso
- [ ] Lookup antes de generar

**Semana 3-4: Error handling**
- [ ] Retry mechanism con exponential backoff
- [ ] Self-correction (LLM corrige errores)
- [ ] Error classification
- [ ] Smart retry logic

**Entregable**: Sistema que aprende de éxitos y corrige errores automáticamente.

---

### Mes 3: Chain-of-Work + Semántica

**Semana 1-2: Trazabilidad**
- [ ] Schema PostgreSQL completo (executions + chain_of_work)
- [ ] ChainOfWorkLogger
- [ ] Dashboard básico para ver auditoría

**Semana 3-4: Semantic cache**
- [ ] Embeddings con Sentence Transformers
- [ ] pgvector integration
- [ ] Similarity search
- [ ] Code adaptation

**Entregable**: Sistema completo con auditoría y búsqueda semántica.

---

### Mes 4+: Producción + Features Avanzadas

- [ ] Firecracker microVMs (opcional)
- [ ] Multi-step code generation (LangGraph)
- [ ] Multi-model support (Claude + GPT-4)
- [ ] MLflow tracing
- [ ] Dashboard web completo
- [ ] API pública
- [ ] Documentación

---

## PARTE 10: COSTOS ESTIMADOS

### 10.1 Costos de Desarrollo (MVP)

```
TU TIEMPO (2-3 meses):
- Full-time: €0 (tu trabajo)
- Opportunity cost: Variable

SERVICIOS:
- OpenAI API (GPT-4):
  * ~$0.03 por tarea (promedio)
  * 1000 tareas/mes = $30/mes
  * Con caché 80% = $6/mes

- PostgreSQL (Supabase free tier): €0
- Redis (Upstash free tier): €0
- Hosting (Railway/Render): €5-20/mes

TOTAL MVP: €10-25/mes
```

### 10.2 Costos de Producción (escala)

```
10,000 tareas/mes:
- LLM API (con 80% cache hit): ~$60/mes
- Database (PostgreSQL): ~$25/mes
- Compute (sandbox containers): ~$50/mes
- Redis: ~$10/mes
- Monitoring: ~$20/mes

TOTAL: ~$165/mes (€150/mes)

100,000 tareas/mes:
- LLM API: ~$600/mes
- Database: ~$100/mes
- Compute: ~$300/mes
- Redis: ~$30/mes
- Monitoring: ~$50/mes

TOTAL: ~$1,080/mes (€1,000/mes)
```

**Optimización con caché agresivo**: Puedes reducir costos LLM en 90% con buen sistema de caché.

---

## CONCLUSIONES Y RECOMENDACIONES

### ✅ Viabilidad: ALTA

El sistema es **100% viable** y está probado en producción por:
- Maisa (España, $30M funding)
- E2B (open-source, usado por Groq, Perplexity)
- Replit Agent
- OpenAI Code Interpreter

### 🎯 Recomendación: Enfoque Híbrido

**Track 1 (Corto plazo - 1-2 meses)**:
- Construye el core runtime (Docker + GPT-4 + PostgreSQL)
- Úsalo manualmente para clientes Track 1
- Guarda cada script exitoso en base de datos
- **Ingresos**: €5-15k por proyecto

**Track 2 (Largo plazo - 3-6 meses)**:
- Evoluciona el runtime a sistema inteligente
- Implementa caché determinístico
- Añade semantic search
- Implementa self-correction
- **Producto**: Plataforma escalable

### 📊 Diferenciación vs Competencia

| Feature | Tu Sistema | Maisa | Make.com | Código Manual |
|---------|-----------|-------|----------|---------------|
| Precio | €5-10k proyecto | €50k+ | €30-100/mes | €8-15k |
| Auditoría | ✅ Chain-of-Work | ✅ KPU | ⚠️ Básico | ✅ Custom |
| Flexibilidad | ✅✅✅ | ⚠️ | ⚠️ | ✅✅✅ |
| Time to market | 2-4 semanas | 2-3 meses | Días | 3-6 semanas |
| Aprendizaje | ✅ Determinismo | ✅ HALP | ❌ | ⚠️ Manual |

**Tu ventaja**: Precio SMB con features enterprise.

### 🚀 Próximos Pasos

1. **Decisión estratégica**: ¿Quieres construir esto como producto principal o complemento a Track 1?

2. **Si es producto principal**:
   - Empieza con Mes 1 del roadmap
   - Invierte 2-3 meses full-time
   - Busca 1-2 clientes beta para validar

3. **Si es complemento**:
   - Construye versión simplificada (sin semantic search)
   - Úsala internamente para Track 1
   - Evoluciona según necesidad

### 📚 Recursos para Profundizar

**Código open-source**:
- E2B Code Interpreter: https://github.com/e2b-dev/code-interpreter
- LLM Sandbox: https://github.com/vndee/llm-sandbox
- LangGraph Code Assistant: https://langchain-ai.github.io/langgraph/tutorials/code_assistant/

**Papers académicos**:
- AgentCoder (multi-agent code generation)
- Self-Organized Agents (LLM code generation at scale)
- RGD (Refinement and Guidance Debugging)

**Plataformas de referencia**:
- Maisa Studio: https://maisa.ai
- E2B: https://e2b.dev
- Modal Sandboxes: https://modal.com

---

## ¿Qué sigue?

**Mario, ahora que tienes toda esta investigación, ¿qué quieres hacer?**

**Opciones**:

A. **Diseñar la arquitectura completa** para tu caso específico
   - Definir casos de uso concretos (facturas, emails, etc.)
   - Elegir stack tecnológico
   - Diseñar database schema
   - Crear diagrama de componentes

B. **Empezar a construir el MVP** (core runtime)
   - Dockerizar sandbox
   - Integrar GPT-4
   - Primera ejecución exitosa
   - Base de datos básica

C. **Profundizar en un componente específico**
   - Prompting strategies
   - Sandbox security
   - Caché semántico
   - Chain-of-Work

D. **Hacer un prototipo rápido** (proof of concept)
   - Script Python que genere código simple
   - Ejecución en Docker
   - Sin caché, sin retry
   - Solo para validar concepto

**¿Qué prefieres?**
