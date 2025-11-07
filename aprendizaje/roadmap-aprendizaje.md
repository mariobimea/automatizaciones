# Roadmap de Aprendizaje: De 0 a Arquitecto de Software (con Claude Code)

## Tu Objetivo

**Aprender a diseñar y construir sistemas de software complejos usando Claude Code como tu copiloto técnico.**

No necesitas ser un experto programador, pero SÍ necesitas:
- Entender arquitectura de sistemas
- Saber comunicar ideas técnicas
- Tomar decisiones de diseño fundamentadas

---

## SEMANA 1: Fundamentos de Arquitectura

### Día 1: Arquitectura de Sistemas (2 horas)

**Lee**:
- [PLAN_ARQUITECTURA.md](PLAN_ARQUITECTURA.md) → Módulo 1 completo

**Ejercicio Práctico 1: Diagrama de Flujo**
```
Tarea: Dibuja (en papel o digital) el flujo completo de tu sistema Maisa:
- Las 5 piezas principales
- Cómo se conectan
- Qué datos fluyen entre ellas

Objetivo: Interiorizar la arquitectura visualmente.
```

**Ejercicio Práctico 2: Explica la Arquitectura**
```
Tarea: Abre Claude Code y explica la arquitectura de Maisa en tus propias palabras.
Usa el template de GUIA_COMUNICACION_CLAUDE.md

Objetivo: Practicar comunicación arquitectónica.
```

**Validación**: Si puedes explicar por qué cada pieza existe y qué pasaría si la eliminas, ¡lo entendiste! ✅

---

### Día 2: Bases de Datos y Chain-of-Work (2 horas)

**Lee**:
- [PLAN_ARQUITECTURA.md](PLAN_ARQUITECTURA.md) → Módulo 4 completo

**Ejercicio Práctico 3: Diseña el Schema**
```
Tarea: Abre Claude Code y pídele:

"Necesito diseñar el schema de base de datos para mi sistema de trabajadores digitales.

Debo guardar:
1. Trabajadores (id, nombre, descripción, herramientas)
2. Ejecuciones (id, trabajador_id, input, status, timestamps)
3. Chain-of-work (id, ejecucion_id, paso_numero, codigo, resultado)

¿Puedes crear el SQL CREATE TABLE con las relaciones apropiadas?"

Objetivo: Practicar cómo pedir implementaciones específicas.
```

**Ejercicio Práctico 4: Entiende las Relaciones**
```
Tarea: Dibuja el diagrama entidad-relación (ERD) de las 3 tablas.
Marca las foreign keys y las cardinalidades (1:N, N:M, etc.)

Objetivo: Entender cómo se relacionan los datos.
```

**Validación**: Explica qué pasa en la BD cuando ejecutas un trabajador 3 veces. Si puedes trazar todos los INSERTs, ¡lo entendiste! ✅

---

### Día 3: APIs y Endpoints (2 horas)

**Lee**:
- [PLAN_ARQUITECTURA.md](PLAN_ARQUITECTURA.md) → Módulo 6.1 (Diseño de la API)

**Ejercicio Práctico 5: Diseña tu API**
```
Tarea: En un documento, diseña los 5 endpoints principales:
1. Crear trabajador
2. Ejecutar trabajador
3. Ver ejecución
4. Ver chain-of-work
5. Listar trabajadores

Para cada uno especifica:
- Método HTTP (GET, POST, PUT, DELETE)
- Path (/trabajadores, /ejecuciones/{id}, etc.)
- Request body (si aplica)
- Response body
- Códigos de estado (200, 201, 404, 500, etc.)
```

**Ejercicio Práctico 6: Valida con Claude Code**
```
Tarea: Pídele a Claude Code que revise tu diseño:

"He diseñado esta API para mi sistema de trabajadores digitales:
[pega tu diseño]

¿Puedes darme feedback sobre:
1. ¿Los nombres de recursos siguen REST correctamente?
2. ¿Faltan endpoints críticos?
3. ¿Los códigos de estado son apropiados?
4. ¿Cómo manejo errores?"
```

**Validación**: Si Claude Code dice "tu diseño se ve bien" con comentarios menores, ¡lo lograste! ✅

---

### Día 4: Seguridad y Sandboxing (2 horas)

**Lee**:
- [PLAN_ARQUITECTURA.md](PLAN_ARQUITECTURA.md) → Módulo 3 completo

**Ejercicio Práctico 7: Entiende por qué Docker**
```
Tarea: Escribe en tus propias palabras:
1. ¿Por qué NO ejecutar el código directo en el servidor?
2. ¿Por qué NO es suficiente un virtualenv?
3. ¿Qué ofrece Docker que las otras opciones no?

Objetivo: Entender las capas de aislamiento.
```

**Ejercicio Práctico 8: Configura el Sandbox**
```
Tarea: Pídele a Claude Code:

"Necesito configurar Docker para ejecutar código Python de forma segura.

Restricciones:
- Máximo 256MB de RAM
- Máximo 30 segundos de ejecución
- Sin acceso a red
- Sistema de archivos read-only excepto /sandbox
- Capturar stdout y stderr

¿Puedes mostrarme:
1. El Dockerfile
2. El comando docker run con los flags correctos?"

Objetivo: Practicar cómo especificar restricciones de seguridad.
```

**Validación**: Lee la respuesta de Claude Code. ¿Entiendes para qué sirve cada flag de Docker? Si sí, ¡excelente! ✅

---

### Día 5: Generación de Código con LLMs (2 horas)

**Lee**:
- [PLAN_ARQUITECTURA.md](PLAN_ARQUITECTURA.md) → Módulo 2 completo

**Ejercicio Práctico 9: Entiende la Generación Incremental**
```
Tarea: Escribe el flujo paso a paso de cómo generarías código para "Extraer datos de una factura en PDF":

Paso 1: [qué código generar, qué resultado esperar]
Paso 2: [qué código generar, qué resultado esperar]
...

Objetivo: Entender por qué generamos código en pasos pequeños.
```

**Ejercicio Práctico 10: Diseña un Prompt**
```
Tarea: Diseña el prompt que le darías a GPT-4 para generar el Paso 3 de tu flujo anterior.

Incluye:
- Contexto (pasos previos, resultados)
- Herramientas disponibles
- Tarea actual
- Restricciones
- Formato de output esperado

Usa el template de PLAN_ARQUITECTURA.md → Módulo 2.2
```

**Validación**: Prueba tu prompt con Claude Code. ¿Genera código útil? Si sí, ¡entendiste prompt engineering! ✅

---

## SEMANA 2: Construcción del MVP

### Día 6-7: Construye el Schema de Base de Datos (4 horas)

**Proyecto**: Crea las 3 tablas principales en PostgreSQL

**Pasos**:
1. Instala PostgreSQL (o usa Docker)
2. Crea una base de datos `maisa_db`
3. Usa Claude Code para generar el SQL
4. Ejecuta el SQL
5. Inserta datos de prueba

**Pide a Claude Code**:
```
"Estoy construyendo Maisa, mi sistema de trabajadores digitales.

Necesito crear el schema de base de datos en PostgreSQL.

Tablas:
1. trabajadores (id, nombre, descripcion, herramientas, creado_en)
2. ejecuciones (id, trabajador_id, input_data, status, iniciado_en, terminado_en)
3. chain_of_work (id, ejecucion_id, paso_numero, codigo_generado, stdout, stderr, timestamp)

¿Puedes crear:
1. El SQL CREATE TABLE completo
2. Las foreign keys apropiadas
3. Índices para optimizar queries comunes
4. Script INSERT con datos de prueba (2 trabajadores, 3 ejecuciones)?

También necesito el código Python para conectarme a PostgreSQL."
```

**Validación**: Ejecuta queries de prueba. Si puedes hacer JOINs entre las tablas, ¡éxito! ✅

---

### Día 8-9: Construye la API Básica (4 horas)

**Proyecto**: Crea una API FastAPI con 3 endpoints básicos

**Endpoints**:
1. POST /trabajadores - Crear trabajador
2. GET /trabajadores - Listar trabajadores
3. GET /trabajadores/{id} - Ver trabajador específico

**Pide a Claude Code**:
```
"Necesito crear una API REST en FastAPI para mi sistema Maisa.

Por ahora, solo 3 endpoints:
1. POST /trabajadores
   → Body: {"nombre": str, "descripcion": str, "herramientas": list}
   → Response: {"trabajador_id": int}
   → Guarda en PostgreSQL

2. GET /trabajadores
   → Response: [{"id": int, "nombre": str, ...}, ...]
   → Lee de PostgreSQL

3. GET /trabajadores/{id}
   → Response: {"id": int, "nombre": str, ...}
   → Lee de PostgreSQL

¿Puedes crear:
1. La app FastAPI con estos endpoints
2. Los modelos Pydantic para request/response
3. La conexión a PostgreSQL (usa la configuración del día 6)
4. Manejo de errores básico (404 si no existe trabajador)?"
```

**Validación**: Usa `curl` o Postman para probar los endpoints. Si puedes crear y listar trabajadores, ¡funciona! ✅

---

### Día 10: Construye el Sandbox de Docker (2 horas)

**Proyecto**: Crea un contenedor Docker que ejecute código Python de forma segura

**Pide a Claude Code**:
```
"Necesito crear un sandbox en Docker para ejecutar código Python generado por IA.

Requisitos:
1. Dockerfile con Python 3.11
2. Librerías instaladas: requests, beautifulsoup4, pandas
3. Usuario sin privilegios (no root)
4. Límites: 256MB RAM, 30s timeout
5. Código Python para:
   - Ejecutar código en el contenedor
   - Capturar stdout/stderr
   - Manejar timeouts
   - Limpiar contenedores después de usar

¿Puedes implementar todo esto?"
```

**Validación**: Ejecuta código de prueba (ej: "print('hello')") y verifica que capturas el output. ✅

---

## SEMANA 3: Integración y Refinamiento

### Día 11-12: Construye el Orquestador Básico (4 horas)

**Proyecto**: Crea la clase que coordina generación + ejecución

**Pide a Claude Code**:
```
"Necesito crear el OrquestadorTrabajador que coordina todo.

Flujo simplificado (sin determinismo por ahora):
1. Recibe trabajador_id y input_data
2. Genera código paso a paso (simula esto con código hardcodeado por ahora)
3. Ejecuta cada paso en Docker (usa el sandbox del día 10)
4. Guarda cada paso en chain_of_work
5. Marca la ejecución como SUCCESS o FAILED

¿Puedes crear:
1. La clase OrquestadorTrabajador
2. El método async ejecutar(input_data)
3. Integración con PostgreSQL para guardar chain-of-work
4. Integración con el sandbox Docker?

Por ahora, usa código hardcodeado para los pasos (ej: paso 1 = 'print("hola")', paso 2 = 'x = 5', etc.)
Más adelante integraremos el LLM real."
```

**Validación**: Ejecuta un trabajador y verifica que se guardan todos los pasos en chain_of_work. ✅

---

### Día 13-14: Integra Generación de Código Real (4 horas)

**Proyecto**: Reemplaza el código hardcodeado con llamadas a GPT-4

**Pide a Claude Code**:
```
"Ahora quiero reemplazar los pasos hardcodeados por generación real con GPT-4.

Necesito:
1. Integrar OpenAI API (tengo API key)
2. Crear la clase GeneradorCodigo
3. Método generar_paso(contexto, paso_numero) que:
   - Construye el prompt con el contexto
   - Llama a GPT-4
   - Valida el código generado (sintaxis, blacklist de funciones peligrosas)
   - Devuelve el código

Contexto incluye:
- Descripción del trabajador
- Herramientas disponibles
- Resultados de pasos previos

¿Puedes implementarlo?"
```

**Validación**: Ejecuta un trabajador real con una tarea simple (ej: "calcula 5+3"). Si GPT-4 genera y ejecuta código, ¡éxito! ✅

---

### Día 15: Implementa Determinismo (2 horas)

**Proyecto**: Agrega caché para reusar código que funciona

**Pide a Claude Code**:
```
"Necesito agregar determinismo al orquestador.

Flujo:
1. Antes de generar código, calcular hash del input
2. Buscar en BD si existe ejecución exitosa con ese hash
3. Si existe → ejecutar chain_of_work cacheado
4. Si no existe → generar código nuevo
5. Si la ejecución es exitosa → guardar en caché

¿Puedes:
1. Agregar tabla cache_ejecuciones (input_hash, trabajador_id, chain_of_work)
2. Modificar OrquestadorTrabajador para usar el caché
3. Implementar lógica de invalidación de caché (si trabajador cambia)?"
```

**Validación**: Ejecuta un trabajador 2 veces con el mismo input. La 2ª vez debe ser más rápida y usar código cacheado. ✅

---

## SEMANA 4: Pulido y Producción

### Día 16-17: Agrega Manejo de Errores Robusto (4 horas)

**Proyecto**: Implementa reintentos, logging, y recuperación de errores

**Pide a Claude Code**:
```
"Necesito hacer el sistema robusto frente a errores.

Casos a manejar:
1. GPT-4 genera código con syntax error → reintentar hasta 3 veces
2. Código ejecutado en Docker timeout → marcar como FAILED, guardar error
3. PostgreSQL connection error → usar circuit breaker
4. Docker container crash → capturar error, limpiar recursos

¿Puedes:
1. Agregar lógica de reintentos en GeneradorCodigo
2. Agregar manejo de excepciones en OrquestadorTrabajador
3. Implementar logging estructurado (usa librería logging)
4. Crear tests unitarios para casos de error?"
```

**Validación**: Simula errores (ej: apaga PostgreSQL) y verifica que el sistema los maneja gracefully. ✅

---

### Día 18-19: Crea la CLI (4 horas)

**Proyecto**: Interfaz de línea de comandos para interactuar con el sistema

**Pide a Claude Code**:
```
"Necesito una CLI para usar Maisa fácilmente.

Comandos:
1. `maisa crear --nombre="..." --descripcion="..." --herramientas=[...]`
   → Crea trabajador, imprime trabajador_id

2. `maisa ejecutar <trabajador_id> --input='{"key": "value"}'`
   → Ejecuta trabajador, imprime ejecucion_id, muestra progreso en tiempo real

3. `maisa ver <ejecucion_id>`
   → Muestra chain-of-work formateado

4. `maisa listar`
   → Lista todos los trabajadores

¿Puedes crear la CLI usando Click o Typer?"
```

**Validación**: Usa la CLI para crear y ejecutar un trabajador. Si funciona end-to-end, ¡lo lograste! ✅

---

### Día 20: Documenta y Despliega (2 horas)

**Proyecto**: README, documentación, y deployment a producción

**Pide a Claude Code**:
```
"Necesito documentar Maisa para que otros (o yo en 6 meses) puedan usarlo.

Crea:
1. README.md con:
   - Qué es Maisa
   - Arquitectura (diagrama)
   - Setup (PostgreSQL, Docker, Python dependencies)
   - Ejemplos de uso
   - API docs

2. docker-compose.yml para levantar todo el stack:
   - PostgreSQL
   - API FastAPI
   - Sandbox Docker

3. Script de deploy para producción (ej: deploy a DigitalOcean o AWS)

¿Puedes crear estos artefactos?"
```

**Validación**: Sigue tu propio README desde cero en una máquina nueva. Si funciona, ¡documentación perfecta! ✅

---

## DESPUÉS DE LAS 4 SEMANAS

### Has Logrado:
- ✅ Entender arquitectura de sistemas complejos
- ✅ Comunicarte efectivamente con Claude Code
- ✅ Construir un sistema completo end-to-end
- ✅ Hacer decisiones arquitectónicas fundamentadas
- ✅ Debuggear y optimizar sistemas

### Próximos Pasos:

**Nivel Intermedio**:
- Agrega autenticación (OAuth, JWT)
- Implementa rate limiting
- Agrega métricas y observabilidad (Prometheus, Grafana)
- Crea una UI web (React + shadcn/ui)

**Nivel Avanzado**:
- Implementa ejecuciones asíncronas con Celery
- Agrega multi-tenancy (múltiples usuarios)
- Escala horizontalmente con Kubernetes
- Implementa CI/CD completo

---

## RECURSOS ADICIONALES

### Lecturas Recomendadas:
- "Designing Data-Intensive Applications" by Martin Kleppmann
- "Building Microservices" by Sam Newman
- "Clean Architecture" by Robert C. Martin

### Conceptos para Profundizar:
- REST API design patterns
- Database normalization vs denormalization
- Distributed systems concepts (CAP theorem, eventual consistency)
- Containerization and orchestration

### Comunidades:
- r/softwarearchitecture
- Software Engineering Stack Exchange
- HackerNews

---

## TU CHECKLIST

Después de cada día, pregúntate:
- [ ] ¿Entendí los conceptos teóricos?
- [ ] ¿Completé los ejercicios prácticos?
- [ ] ¿Puedo explicar lo aprendido en mis propias palabras?
- [ ] ¿Probé lo construido y funciona?

Si respondes SÍ a las 4, ¡avanza al siguiente día! Si no, repasa ese día.

---

¡Éxito en tu aprendizaje! 🚀
