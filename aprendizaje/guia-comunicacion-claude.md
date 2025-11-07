# Guía: Cómo Comunicarte con Claude Code para Construir Software

## ¿Por qué esta guía?

Entender arquitectura es el 50%. El otro 50% es **saber comunicar tus ideas arquitectónicas a Claude Code** de forma efectiva.

Esta guía te enseña **cómo hablar con una IA de ingeniería de software**.

---

## PARTE 1: Principios de Comunicación Efectiva

### 1.1 Sé Específico, No Vago

#### ❌ MALO:
```
"Necesito una API"
```

#### ✅ BUENO:
```
"Necesito una API REST en FastAPI con estos endpoints:
1. POST /trabajadores - Crear un trabajador digital
2. POST /trabajadores/{id}/ejecutar - Ejecutar un trabajador
3. GET /ejecuciones/{id} - Ver estado de una ejecución

La API debe conectarse a PostgreSQL y manejar errores con códigos HTTP apropiados."
```

**Por qué**: Claude Code necesita contexto para tomar decisiones arquitectónicas correctas.

---

### 1.2 Proporciona Contexto Arquitectónico

#### ❌ MALO:
```
"Crea una función que procese facturas"
```

#### ✅ BUENO:
```
"Estoy construyendo un sistema de trabajadores digitales. Necesito una función que:
- Sea llamada desde el orquestador principal
- Reciba un email_id como input
- Descargue el PDF de Gmail usando la API de Google
- Extraiga el NIF y el importe
- Devuelva un diccionario con los datos extraídos

Contexto: Esta función será ejecutada dentro de un contenedor Docker con límites de memoria (256MB) y timeout de 30 segundos."
```

**Por qué**: Claude Code necesita entender DÓNDE encaja esta pieza en el sistema completo.

---

### 1.3 Explica el "Por Qué", No Solo el "Qué"

#### ❌ MALO:
```
"Agrega un campo 'input_hash' a la tabla ejecuciones"
```

#### ✅ BUENO:
```
"Necesito agregar un campo 'input_hash' a la tabla ejecuciones para implementar determinismo.

Objetivo: Cuando un usuario ejecute un trabajador con el mismo input dos veces, quiero reusar el código que ya funcionó en vez de regenerarlo.

El campo input_hash será un SHA256 del input serializado más el trabajador_id."
```

**Por qué**: Claude Code puede sugerir mejores alternativas si entiende tu objetivo.

---

## PARTE 2: Patrones de Conversación Efectivos

### 2.1 Patrón: "Arquitectura → Implementación"

**Paso 1: Describe la arquitectura**
```
"Quiero construir un sistema de trabajadores digitales con esta arquitectura:

1. Generador de código (GPT-4) que genera Python paso a paso
2. Sandbox (Docker) que ejecuta el código de forma segura
3. Base de datos (PostgreSQL) que guarda cada paso (Chain-of-Work)
4. API (FastAPI) que expone todo como servicio
5. CLI que permite crear y ejecutar trabajadores

Las piezas se comunican así:
CLI → API → Orquestador → Generador + Sandbox → PostgreSQL
"
```

**Paso 2: Pide implementación incremental**
```
"Empecemos por lo más básico: la estructura de base de datos.

Necesito estas 3 tablas:
1. trabajadores (id, nombre, descripcion, herramientas)
2. ejecuciones (id, trabajador_id, input_data, status, timestamps)
3. chain_of_work (id, ejecucion_id, paso_numero, codigo_generado, resultado)

¿Puedes crear el schema SQL con las relaciones apropiadas?"
```

**Resultado**: Claude Code tiene el contexto completo pero empieza por una pieza pequeña.

---

### 2.2 Patrón: "Problema → Restricciones → Solución"

#### Ejemplo 1: Seguridad en Sandbox

```
PROBLEMA:
"Voy a ejecutar código Python generado por GPT-4. Este código puede ser peligroso."

RESTRICCIONES:
"- No puede acceder al sistema de archivos fuera de /sandbox
- No puede hacer llamadas de red arbitrarias
- Máximo 256MB de RAM
- Máximo 30 segundos de ejecución
- No puede ejecutar comandos del sistema (os.system, subprocess)"

SOLUCIÓN DESEADA:
"¿Cómo configuro Docker para garantizar estas restricciones? Muéstrame:
1. El Dockerfile
2. El comando docker run con los flags correctos
3. Cómo capturar stdout/stderr"
```

**Resultado**: Claude Code genera una solución que cumple TODAS tus restricciones.

---

### 2.3 Patrón: "Ejemplo Concreto → Generalización"

#### ❌ MALO (muy abstracto):
```
"Crea un sistema de caché para hacer las ejecuciones deterministas"
```

#### ✅ BUENO (ejemplo concreto primero):
```
"Necesito implementar determinismo. Déjame darte un ejemplo concreto:

EJEMPLO:
1. Usuario ejecuta trabajador #123 con input {"email_id": "email_456"}
2. El sistema genera código y lo ejecuta → SUCCESS
3. Usuario ejecuta trabajador #123 con input {"email_id": "email_456"} (MISMO input)
4. El sistema debe detectar que ya tiene código para ese input
5. Ejecuta el MISMO código sin regenerarlo

IMPLEMENTACIÓN:
Para detectar "mismo input", necesito:
- Calcular un hash del input (JSON serializado + trabajador_id)
- Buscar en BD si existe una ejecución exitosa con ese hash
- Si existe, reusar el chain_of_work guardado
- Si no existe, generar nuevo código

¿Puedes implementar esta lógica en el orquestador?"
```

**Resultado**: Claude Code entiende perfectamente qué construir.

---

## PARTE 3: Cómo Describir Componentes Complejos

### 3.1 El Orquestador

**Estructura de la descripción**:

```
"Necesito crear la clase OrquestadorTrabajador. Te explico qué hace:

RESPONSABILIDAD:
Coordina la ejecución completa de un trabajador digital.

FLUJO:
1. Recibe un trabajador_id y un input_data
2. Verifica si hay código cacheado para este input (determinismo)
3. Si hay caché → ejecuta código cacheado
4. Si no hay caché → genera código paso a paso
5. Por cada paso:
   - Llama al GeneradorCodigo para generar código
   - Valida que el código es seguro
   - Ejecuta en SandboxDocker
   - Guarda resultado en chain_of_work
   - Actualiza contexto para el siguiente paso
6. Cuando termina, guarda todo en BD y devuelve resultado

MANEJO DE ERRORES:
- Si un paso falla, reintenta hasta 3 veces
- Si falla después de 3 intentos, marca la ejecución como FAILED
- Guarda los errores en chain_of_work para debugging

INTERFAZ:
```python
class OrquestadorTrabajador:
    async def ejecutar(self, input_data: dict) -> ResultadoEjecucion:
        pass
```

¿Puedes implementar esta clase?"
```

---

### 3.2 El Generador de Código

```
"Necesito crear el GeneradorCodigo que usa GPT-4 para generar Python.

RESPONSABILIDAD:
Generar código Python ejecutable paso a paso.

CONTEXTO QUE RECIBE:
- Descripción del trabajador (qué hace)
- Lista de herramientas disponibles (gmail_api, pdf_reader, etc.)
- Resultados de pasos anteriores
- Paso actual que debe generar

PROMPT ENGINEERING:
El prompt al LLM debe incluir:
1. Objetivo del trabajador
2. Herramientas disponibles (con documentación)
3. Contexto de pasos previos
4. Restricciones (solo 2-5 líneas de código, no imports externos)
5. Formato de output esperado

VALIDACIÓN:
Antes de devolver el código, valida:
- Sintaxis correcta (compile())
- No contiene llamadas peligrosas (os.system, eval, etc.)
- Solo usa herramientas permitidas

INTERFAZ:
```python
class GeneradorCodigo:
    async def generar_paso(self, contexto: dict, paso_numero: int) -> str:
        """
        Returns: Código Python válido como string
        """
        pass
```

¿Puedes implementarlo?"
```

---

## PARTE 4: Depuración y Refinamiento

### 4.1 Cómo Pedir Ayuda con Bugs

#### ❌ MALO:
```
"No funciona"
```

#### ✅ BUENO:
```
"El orquestador está fallando. Te doy contexto:

QUÉ ESPERABA:
Que ejecutara los 5 pasos y devolviera SUCCESS.

QUÉ ESTÁ PASANDO:
Falla en el paso 3 con error: 'NoneType' object has no attribute 'group'

CÓDIGO RELEVANTE:
[pega el código del paso que falla]

CHAIN-OF-WORK:
Paso 1: ✅ Email encontrado
Paso 2: ✅ PDF descargado
Paso 3: ❌ Error al extraer NIF

LOGS:
[pega los logs]

PREGUNTA:
¿Por qué el regex no está encontrando el NIF? ¿El problema es el regex o la forma en que extraemos el texto del PDF?"
```

---

### 4.2 Cómo Pedir Optimizaciones

```
"El sistema funciona pero es lento. Te doy métricas:

PROBLEMA:
Procesar una factura tarda 45 segundos. Queremos bajarlo a <10s.

ANÁLISIS:
He medido cada paso:
- Paso 1 (buscar email): 0.5s ✅
- Paso 2 (descargar PDF): 1.2s ✅
- Paso 3 (extraer texto del PDF): 38s ❌ (CUELLO DE BOTELLA)
- Paso 4 (guardar en BD): 0.3s ✅

CÓDIGO DEL PASO LENTO:
[pega código del paso 3]

PREGUNTA:
¿Cómo puedo optimizar la extracción de texto del PDF? ¿Es problema de la librería pdf_reader o de cómo la estoy usando?"
```

---

## PARTE 5: Patrones Avanzados

### 5.1 Diseño de APIs

```
"Necesito diseñar los endpoints de la API. Dame feedback arquitectónico.

PROPUESTA INICIAL:

POST /trabajadores
→ Crea un trabajador
→ Body: {"nombre": "...", "descripcion": "...", "herramientas": [...]}
→ Response: {"trabajador_id": 123}

POST /trabajadores/{id}/ejecutar
→ Ejecuta un trabajador
→ Body: {"input_data": {...}}
→ Response: {"ejecucion_id": 456, "status": "RUNNING"}

GET /ejecuciones/{id}
→ Ver estado de ejecución
→ Response: {"status": "SUCCESS", "resultado": {...}, "duracion": "8.7s"}

GET /ejecuciones/{id}/chain-of-work
→ Ver chain-of-work completo
→ Response: [{"paso": 1, "codigo": "...", "resultado": "..."}, ...]

GET /trabajadores
→ Listar todos los trabajadores
→ Response: [{"id": 123, "nombre": "..."}, ...]

PREGUNTAS:
1. ¿Falta algún endpoint crítico?
2. ¿Los nombres de recursos siguen REST correctamente?
3. ¿Debería agregar paginación en GET /trabajadores?
4. ¿Los códigos de estado HTTP son apropiados?
5. ¿Necesito autenticación/autorización desde el principio?"
```

---

### 5.2 Solicitar Revisión de Arquitectura

```
"He diseñado esta arquitectura. ¿Puedes revisarla y darme feedback?

ARQUITECTURA PROPUESTA:

┌─────────┐
│   CLI   │
└────┬────┘
     │
     ▼
┌─────────┐
│   API   │
└────┬────┘
     │
     ▼
┌──────────────┐
│ Orquestador  │
└──┬────────┬──┘
   │        │
   ▼        ▼
┌──────┐ ┌──────┐
│ LLM  │ │Docker│
└──────┘ └──────┘
   │        │
   └────┬───┘
        ▼
   ┌─────────┐
   │PostgreSQL│
   └──────────┘

FLUJO:
1. CLI envía request a API
2. API llama al Orquestador
3. Orquestador genera código con LLM
4. Orquestador ejecuta código en Docker
5. Cada paso se guarda en PostgreSQL
6. Resultado se devuelve a CLI

PREOCUPACIONES:
1. ¿Es un problema que cada llamada al LLM sea síncrona? ¿Debería usar colas (Celery, RabbitMQ)?
2. ¿Docker puede manejar múltiples ejecuciones concurrentes?
3. ¿PostgreSQL será un cuello de botella si guardo cada paso?
4. ¿Falta alguna pieza crítica?
5. ¿Esta arquitectura escala a 100 ejecuciones concurrentes?"
```

---

## PARTE 6: Ejercicios Prácticos

### Ejercicio 1: Describe un Componente Completo

**Tarea**: Escribe una descripción completa del componente "SandboxDocker" siguiendo este template:

```
COMPONENTE: SandboxDocker

RESPONSABILIDAD:
[¿Qué hace este componente?]

INPUTS:
[¿Qué recibe?]

OUTPUTS:
[¿Qué devuelve?]

RESTRICCIONES:
[¿Qué limitaciones debe cumplir?]

INTERFAZ:
[¿Qué métodos públicos expone?]

MANEJO DE ERRORES:
[¿Qué puede salir mal y cómo se maneja?]
```

---

### Ejercicio 2: Depura un Problema

**Escenario**: El chain-of-work no se está guardando correctamente en PostgreSQL.

Escribe un mensaje a Claude Code que incluya:
1. Qué esperabas que pasara
2. Qué está pasando realmente
3. Código relevante
4. Logs de error
5. Pregunta específica

---

### Ejercicio 3: Solicita una Optimización

**Escenario**: El sistema tarda mucho en ejecutar trabajadores.

Escribe un mensaje que incluya:
1. Métricas actuales (tiempos por paso)
2. Objetivo deseado
3. Análisis de dónde está el cuello de botella
4. Pregunta sobre cómo optimizar

---

## PARTE 7: Checklist de Comunicación Efectiva

Antes de enviar un mensaje a Claude Code, verifica:

- [ ] ¿Proporcioné contexto arquitectónico?
- [ ] ¿Expliqué el "por qué", no solo el "qué"?
- [ ] ¿Fui específico con nombres, tipos de datos, restricciones?
- [ ] ¿Incluí un ejemplo concreto si es aplicable?
- [ ] ¿Especifiqué cómo se integra con el resto del sistema?
- [ ] ¿Mencioné restricciones de seguridad/performance si aplican?
- [ ] ¿Pedí feedback si no estoy 100% seguro del diseño?

---

## PARTE 8: Frases Útiles

### Para Empezar Proyectos
```
"Estoy construyendo [PROYECTO]. La arquitectura es [DESCRIPCIÓN]. Quiero empezar por [COMPONENTE] porque [RAZÓN]."
```

### Para Pedir Implementación
```
"Necesito implementar [COMPONENTE]. Su responsabilidad es [DESCRIPCIÓN]. Debe integrarse con [OTROS COMPONENTES]. ¿Puedes crear [INTERFAZ]?"
```

### Para Depurar
```
"Tengo un bug en [COMPONENTE]. Esperaba [COMPORTAMIENTO], pero está [COMPORTAMIENTO ACTUAL]. Aquí está el código relevante: [CÓDIGO]. Los logs muestran: [LOGS]. ¿Qué está mal?"
```

### Para Optimizar
```
"[COMPONENTE] es lento. Tarda [TIEMPO ACTUAL], quiero bajarlo a [TIEMPO OBJETIVO]. He medido: [MÉTRICAS]. ¿Cómo puedo optimizarlo?"
```

### Para Pedir Review
```
"He diseñado [ARQUITECTURA/COMPONENTE]. ¿Puedes revisar y darme feedback sobre: [ASPECTOS ESPECÍFICOS]?"
```

---

## RESUMEN

La clave para trabajar efectivamente con Claude Code es:

1. **Contexto**: Explica DÓNDE encaja cada pieza
2. **Por qué**: No solo QUÉ hacer, sino POR QUÉ
3. **Especificidad**: Nombres concretos, tipos de datos, restricciones
4. **Ejemplos**: Usa casos concretos para ilustrar comportamiento
5. **Iteración**: Empieza simple, pide feedback, refina

Con estos principios, Claude Code será tu copiloto perfecto para construir software complejo. 🚀
