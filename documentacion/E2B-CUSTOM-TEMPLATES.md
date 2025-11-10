# E2B Custom Templates - Guía Completa

**Fecha**: 2025-11-09
**Versión E2B**: v1.x (Build System 2.0)

---

## Índice

1. [¿Qué son los Custom Templates?](#qué-son-los-custom-templates)
2. [Dos Sistemas de Build](#dos-sistemas-de-build)
3. [Build System 2.0 (Recomendado)](#build-system-20-recomendado)
4. [Legacy System (Dockerfile-based)](#legacy-system-dockerfile-based)
5. [Comparación de Sistemas](#comparación-de-sistemas)
6. [Cómo Funcionan los Templates](#cómo-funcionan-los-templates)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## ¿Qué son los Custom Templates?

Un **Custom Template** en E2B es una **snapshot pre-configurada** de un entorno de ejecución que incluye:
- Sistema operativo base (Debian-based)
- Paquetes del sistema (apt packages)
- Librerías Python/Node/etc pre-instaladas
- Archivos de configuración
- Servicios que arrancan automáticamente

**Analogía**: Es como crear una imagen Docker personalizada, pero optimizada para micro VMs que arrancan en ~300ms.

### ¿Por qué usar Custom Templates?

**Sin template personalizado**:
```
Sandbox arranca → Instala PyMuPDF (~4s) → Instala pandas (~2s) → Ejecuta código
Total: ~6-7 segundos
```

**Con template personalizado**:
```
Sandbox arranca con PyMuPDF + pandas pre-instalados → Ejecuta código
Total: ~1.5 segundos
```

**Beneficios**:
- ⚡ Reduce cold start de 6s a 1.5s (75% más rápido)
- 💰 Ahorra dinero (E2B cobra por segundo de ejecución)
- 🔄 Consistencia garantizada (todos los sandboxes tienen mismas versiones)
- 🚀 Mejor UX (workflows responden más rápido)

---

## Dos Sistemas de Build

E2B tiene **dos formas** de crear custom templates:

### 1. Build System 2.0 (Actual - Recomendado)

**Características**:
- ✅ Templates como código Python/TypeScript
- ✅ Type hints y autocompletado
- ✅ Build automático al ejecutar script
- ✅ Fácil integración en CI/CD
- ✅ Dinámico (puedes generar templates programáticamente)

**Cuándo usarlo**: Proyectos nuevos, templates complejos, builds dinámicos

### 2. Legacy System (Dockerfile-based)

**Características**:
- ⚠️ Basado en `e2b.Dockerfile`
- ⚠️ Build manual con CLI `e2b template build`
- ⚠️ Menos flexible
- ✅ Familiar si vienes de Docker
- ✅ Reutiliza Dockerfiles existentes

**Cuándo usarlo**: Migración desde Docker, templates simples, familiaridad con Docker

---

## Build System 2.0 (Recomendado)

### Estructura de Archivos

```
/my-project/
├── template/
│   ├── template.py          # Define el template
│   ├── build_prod.py        # Build para producción
│   ├── build_dev.py         # Build para desarrollo (opcional)
│   ├── requirements.txt     # Dependencias Python
│   └── server/              # Archivos a copiar (opcional)
│       └── start.sh
```

### Ejemplo Completo: Template Python

**`template/template.py`**:
```python
from e2b import Template, wait_for_url

def make_template(
    packages: list[str] = None,
    set_user_workdir: bool = False
):
    """
    Crea template personalizado para workflows.

    Args:
        packages: Lista de paquetes pip adicionales
        set_user_workdir: Si True, usa /home/user como workdir
    """
    # Paquetes por defecto
    default_packages = [
        "PyMuPDF==1.24.0",
        "requests==2.31.0",
        "pandas==2.1.4",
        "pillow==10.1.0",
    ]

    # Combinar con paquetes adicionales
    all_packages = default_packages + (packages or [])

    # Build template
    template = (
        Template()
        # Base image (solo Debian-based)
        .from_image("python:3.12")

        # Usuario y directorio
        .set_user("root")
        .set_workdir("/")

        # Environment variables
        .set_envs({
            "PIP_DEFAULT_TIMEOUT": "100",
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            "PIP_NO_CACHE_DIR": "1",
        })

        # Paquetes del sistema
        .apt_install([
            "build-essential",
            "curl",
            "git",
            "jq",
        ])

        # Instalar Python packages
        .pip_install(all_packages)

        # Copiar archivos de configuración
        .copy("server/start.sh", ".jupyter/start-up.sh")
        .run_cmd("chmod +x .jupyter/start-up.sh")
    )

    # Usuario final
    if set_user_workdir:
        template = template.set_user("user").set_workdir("/home/user")

    # Comando de inicio (importante!)
    return template.set_start_cmd(
        ".jupyter/start-up.sh",
        wait_for_url("http://localhost:49999/health")
    )
```

**`template/build_prod.py`**:
```python
from dotenv import load_dotenv
from e2b import Template, default_build_logger
from template import make_template

load_dotenv()

# Build del template
Template.build(
    make_template(set_user_workdir=True),
    alias="my-workflow-engine",  # Nombre del template
    cpu_count=2,                  # CPUs (default: 2)
    memory_mb=2048,               # RAM en MB (default: 512)
    on_build_logs=default_build_logger(),  # Logs durante build
)
```

### Métodos del Template Builder

```python
Template()
    # Imagen base
    .from_image("python:3.12")           # Desde imagen Docker
    .from_dockerfile("./Dockerfile")     # Desde Dockerfile existente
    .from_template("code-interpreter")   # Desde template E2B existente

    # Usuario y directorio
    .set_user("root")                    # Cambiar usuario
    .set_workdir("/app")                 # Cambiar working directory

    # Environment variables
    .set_envs({"KEY": "value"})          # Múltiples vars

    # Paquetes del sistema (apt)
    .apt_install(["git", "curl"])        # Lista de packages
    .run_cmd("apt-get update")           # Comando arbitrario

    # Python packages
    .pip_install(["requests", "pandas"]) # Lista de packages
    .pip_install("--no-cache-dir -r requirements.txt")  # Desde archivo

    # Node.js packages
    .npm_install("express", g=True)      # Global install
    .npm_install("react")                # Local install

    # Archivos
    .copy("src/", "/app/")               # Copiar archivo/directorio
    .make_dir("/data")                   # Crear directorio

    # Comando de inicio
    .set_start_cmd(
        "python server.py",              # Comando a ejecutar
        wait_for_url("http://localhost:8000/health")  # Healthcheck
    )
```

### Ejecutar el Build

```bash
# Instalar dependencias
pip install e2b python-dotenv

# Build del template
cd template/
python build_prod.py
```

**Output esperado**:
```
Building template...
✓ Step 1/12: FROM python:3.12
✓ Step 2/12: USER root
✓ Step 3/12: WORKDIR /
✓ Step 4/12: ENV PIP_DEFAULT_TIMEOUT=100
...
✓ Template built successfully!

Template ID: wzqi57u2e8v2f90t6lh5
Alias: my-workflow-engine
```

### Usar el Template en tu App

```python
from e2b_code_interpreter import Sandbox

# Con alias
sandbox = Sandbox.create(template="my-workflow-engine")

# Con template ID
sandbox = Sandbox.create(template="wzqi57u2e8v2f90t6lh5")

# Ejecutar código
execution = sandbox.run_code("import pandas; print(pandas.__version__)")
print(execution.logs.stdout)  # "2.1.4"

sandbox.close()
```

---

## Legacy System (Dockerfile-based)

### Estructura de Archivos

```
/nova/
├── e2b.Dockerfile     # Template definition
├── e2b.toml           # Auto-generated config
└── .env               # E2B_TEMPLATE_ID
```

### Ejemplo: e2b.Dockerfile

```dockerfile
# NOVA Workflow Engine - E2B Sandbox Template
# Solo Debian-based images permitidos

FROM e2bdev/code-interpreter:latest

# Working directory
WORKDIR /home/user

# Paquetes del sistema
RUN apt-get update && \
    apt-get install -y gcc && \
    rm -rf /var/lib/apt/lists/*

# Python packages (pinned versions)
RUN pip install --no-cache-dir \
    PyMuPDF==1.24.0 \
    requests==2.31.0 \
    pandas==2.1.4 \
    pillow==10.1.0 \
    psycopg2-binary==2.9.10 \
    python-dotenv==1.0.0

# Verificar instalación
RUN python -c "import fitz; import requests; import pandas; import PIL; import psycopg2; import dotenv; print('✅ All packages installed')"

WORKDIR /home/user
```

### Build con CLI

```bash
# Inicializar template (crea e2b.Dockerfile)
e2b template init

# Build del template
e2b template build \
  --name "nova-workflow-fresh" \
  --cpu-count 2 \
  --memory-mb 2048 \
  -c "/root/.jupyter/start-up.sh"
```

**Parámetros importantes**:
- `--name`: Nombre del template (lowercase, alphanumeric, dashes, underscores)
- `--cpu-count`: CPUs (default: 2)
- `--memory-mb`: RAM en MB (default: 512, debe ser par)
- `-c` o `--cmd`: Comando de inicio (**OBLIGATORIO** para code-interpreter)
- `--dockerfile`: Path al Dockerfile (default: `./e2b.Dockerfile` o `./Dockerfile`)

**Output**:
```
Building template nova-workflow-fresh...
✓ Image built
✓ Pushing to E2B cloud...
✓ Template created

Template ID: wzqi57u2e8v2f90t6lh5
Name: nova-workflow-fresh
```

### e2b.toml (auto-generado)

```toml
template_id = "wzqi57u2e8v2f90t6lh5"
dockerfile = "e2b.Dockerfile"
start_cmd = "/root/.jupyter/start-up.sh"
cpu_count = 2
memory_mb = 2048
```

### Usar el Template

```python
from e2b_code_interpreter import Sandbox
import os

template_id = os.getenv("E2B_TEMPLATE_ID")  # wzqi57u2e8v2f90t6lh5

with Sandbox.create(template=template_id) as sbx:
    execution = sbx.run_code("import pandas; print(pandas.__version__)")
    print(execution.logs.stdout)
```

---

## Comparación de Sistemas

| Característica | Build System 2.0 | Legacy (Dockerfile) |
|----------------|------------------|---------------------|
| **Sintaxis** | Python/TS fluent API | Dockerfile |
| **Build** | Automático (script) | Manual (CLI) |
| **Type hints** | ✅ Sí | ❌ No |
| **Dinámico** | ✅ Sí (código) | ❌ No |
| **CI/CD** | ✅ Fácil | ⚠️ Requiere CLI |
| **Debugging** | ✅ Mejor | ⚠️ Limitado |
| **Familiaridad** | ⚠️ Nuevo | ✅ Docker conocido |
| **Futuro** | ✅ Soporte activo | ⚠️ Legacy |

**Recomendación**:
- **Proyectos nuevos**: Build System 2.0
- **Migración Docker**: Legacy Dockerfile
- **Templates simples**: Ambos funcionan
- **Templates dinámicos**: Build System 2.0 obligatorio

---

## Cómo Funcionan los Templates

### Proceso de Build (Ambos Sistemas)

```
1. E2B recibe definición del template
   ↓
2. Crea un contenedor Docker
   ↓
3. Ejecuta comandos de instalación
   ↓
4. Ejecuta start command (si existe)
   ↓
5. Espera readiness check (default: 20s, o hasta que URL responda)
   ↓
6. Toma snapshot del filesystem + procesos
   ↓
7. Convierte snapshot a micro VM image
   ↓
8. Almacena en E2B cloud
   ↓
9. Retorna template ID
```

### Proceso de Uso

```
1. Tu app llama: Sandbox.create(template="my-template")
   ↓
2. E2B carga micro VM desde template
   ↓
3. Arranca sandbox en ~300ms (ya tiene todo instalado!)
   ↓
4. Tu código ejecuta con packages pre-instalados
   ↓
5. Sandbox termina
```

### Template ID vs Alias

```python
# Template ID (nunca cambia)
Sandbox.create(template="wzqi57u2e8v2f90t6lh5")

# Alias (apunta al template ID)
Sandbox.create(template="my-workflow-engine")
```

**Importante**:
- El **template ID** es permanente y único
- El **alias** es un nombre legible que puedes cambiar
- Puedes tener múltiples aliases apuntando al mismo template
- Al rebuild, el template ID NO cambia (se actualiza in-place)

---

## Best Practices

### 1. Pin Package Versions

**❌ Malo**:
```python
.pip_install(["pandas", "requests"])
```

**✅ Bueno**:
```python
.pip_install([
    "pandas==2.1.4",
    "requests==2.31.0",
])
```

**Por qué**: Reproducibilidad. Si pandas 2.2.0 tiene un bug, todos tus sandboxes lo tendrán.

### 2. Minimize Template Size

**❌ Malo**:
```dockerfile
RUN pip install --no-cache-dir \
    pandas \
    numpy \
    scipy \
    scikit-learn \
    tensorflow \
    pytorch \
    transformers
```

**✅ Bueno**:
```dockerfile
# Solo lo que realmente necesitas
RUN pip install --no-cache-dir \
    pandas==2.1.4 \
    requests==2.31.0
```

**Por qué**:
- Reduce tiempo de build
- Reduce tamaño del snapshot
- Reduce cold start time
- Ahorra dinero (menos tiempo = menos costo)

### 3. Combina RUN Commands

**❌ Malo**:
```dockerfile
RUN apt-get update
RUN apt-get install -y git
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*
```

**✅ Bueno**:
```dockerfile
RUN apt-get update && \
    apt-get install -y git curl && \
    rm -rf /var/lib/apt/lists/*
```

**Por qué**: Reduce layers de Docker, hace build más rápido.

### 4. Use Start Command

**❌ Malo**:
```python
Template.build(
    make_template(),
    alias="my-template",
)
```

**✅ Bueno**:
```python
Template.build(
    make_template().set_start_cmd(
        "python server.py",
        wait_for_url("http://localhost:8000/health")
    ),
    alias="my-template",
)
```

**Por qué**:
- Garantiza que servicios estén listos antes de ejecutar código
- Evita race conditions
- Compatible con `e2b-code-interpreter`

### 5. Test After Build

**Siempre** verifica que el template funciona:

```python
# test_template.py
from e2b_code_interpreter import Sandbox

def test_packages():
    with Sandbox.create(template="my-template") as sbx:
        result = sbx.run_code("""
import pandas
import requests
print("✅ All packages available")
        """)

        assert "✅" in result.logs.stdout
        print("Template works!")

test_packages()
```

### 6. Use Template Alias in Production

**❌ Malo**:
```python
# Hardcoded template ID
sandbox = Sandbox.create(template="wzqi57u2e8v2f90t6lh5")
```

**✅ Bueno**:
```python
# Use alias
sandbox = Sandbox.create(template="my-workflow-engine")

# O desde env var
template = os.getenv("E2B_TEMPLATE_ID", "my-workflow-engine")
sandbox = Sandbox.create(template=template)
```

**Por qué**: Flexibilidad para cambiar templates sin redeployar código.

### 7. Document Your Template

Crea un `E2B_TEMPLATE.md` con:
- Lista de packages instalados
- Versiones
- Propósito de cada package
- Template ID
- Fecha de última actualización
- Instrucciones de rebuild

Ver [ejemplo en NOVA](../nova/E2B_TEMPLATE.md).

---

## Troubleshooting

### "Template build failed: Image size too large"

**Problema**: Docker build context > 4.3GB

**Solución**:
```dockerfile
# Agrega .dockerignore
node_modules/
.git/
*.log
__pycache__/
```

### "The sandbox is running but port is not open"

**Problema**: Start command no especificado o healthcheck falla

**Solución (Build System 2.0)**:
```python
.set_start_cmd(
    "python server.py",
    wait_for_url("http://localhost:8000/health", timeout=60)
)
```

**Solución (Legacy)**:
```bash
e2b template build --name "my-template" -c "/path/to/start.sh"
```

### "ImportError: No module named 'xyz'"

**Problema**: Package no está en el template

**Solución 1** (Rebuild template):
```python
.pip_install(["xyz==1.0.0"])
```

**Solución 2** (Install on-the-fly):
```python
sbx.run_code("pip install xyz")
sbx.run_code("import xyz; print(xyz.__version__)")
```

### "Template ID mismatch"

**Problema**: Template ID diferente entre local y Railway

**Solución**:
```bash
# Railway → Settings → Environment Variables
E2B_TEMPLATE_ID=wzqi57u2e8v2f90t6lh5

# IMPORTANTE: Agregar en AMBOS servicios
# - Web (API)
# - Worker (Celery)
```

### "401 Not Authorized when e2b template build"

**Problema**: No estás autenticado

**Solución**:
```bash
# Obtén API key de https://e2b.dev/dashboard
export E2B_API_KEY=e2b_your_key_here

# O agrega a .env
echo "E2B_API_KEY=e2b_your_key_here" >> .env
```

### Template tiene caching issues

**Síntoma**: Packages no aparecen después de rebuild

**Solución**: Crea template completamente nuevo con nuevo nombre

```bash
# Legacy
e2b template build --name "my-template-v2" -c "/root/.jupyter/start-up.sh"

# Build System 2.0
Template.build(
    make_template(),
    alias="my-workflow-engine-v2",  # Nuevo nombre
)
```

---

## Recursos Adicionales

### Documentación Oficial
- [E2B Docs](https://e2b.dev/docs)
- [Build System 2.0](https://e2b.dev/blog/introducing-build-system-2-0)
- [CLI Reference](https://e2b.dev/docs/sdk-reference/cli)

### Ejemplos de Templates
- [E2B Code Interpreter](https://github.com/e2b-dev/code-interpreter/tree/main/template)
- [E2B Cookbook](https://github.com/e2b-dev/e2b-cookbook)

### NOVA Templates
- [E2B Template Config](../nova/E2B_TEMPLATE.md)
- [e2b.Dockerfile](../nova/e2b.Dockerfile)
- [Test Script](../nova/test_template.py)

---

## Conclusión

**Para NOVA**:
- ✅ Usamos **Legacy System (Dockerfile)** porque:
  - Es más simple para template básico
  - Familiaridad con Docker
  - Fácil agregar/quitar packages

**Recomendación general**:
- Proyectos nuevos → **Build System 2.0**
- Migración Docker → **Legacy System**
- Templates dinámicos → **Build System 2.0**

**Next steps**:
1. ✅ Template creado (`nova-workflow-fresh`)
2. ✅ Packages pre-instalados (PyMuPDF, pandas, etc)
3. 🔄 Crear workflows que usen el template
4. 🔄 Monitorear performance y costos

---

*Última actualización: 2025-11-09*
