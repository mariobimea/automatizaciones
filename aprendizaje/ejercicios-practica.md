# Ejercicios de Práctica: Comunicación con Claude Code

Este documento contiene ejercicios prácticos para que AHORA MISMO practiques comunicarte conmigo (Claude Code).

**Instrucciones**: Lee cada ejercicio, escribe tu respuesta, y luego pégala en el chat. Te daré feedback inmediato.

---

## EJERCICIO 1: Describe un Sistema Simple

**Contexto**: Imagina que quieres construir un sistema que:
- Lea emails de Gmail
- Extraiga los PDFs adjuntos
- Guarde los PDFs en una carpeta local

**Tu tarea**: Escribe una descripción arquitectónica de este sistema para Claude Code.

Incluye:
1. Las 3-4 piezas principales del sistema
2. Cómo se conectan
3. Qué datos fluyen entre ellas
4. Restricciones o decisiones importantes

**Template**:
```
Quiero construir un sistema que [DESCRIPCIÓN GENERAL].

ARQUITECTURA:

PIEZA 1: [Nombre]
- Responsabilidad: [qué hace]
- Input: [qué recibe]
- Output: [qué produce]

PIEZA 2: [Nombre]
...

FLUJO:
[Describe el flujo de datos paso a paso]

DECISIONES ARQUITECTÓNICAS:
- [Por qué elegiste esta estructura]
- [Qué alternativas consideraste]
```

**Cuando termines**: Pega tu descripción en el chat y yo te daré feedback. ✅

---

## EJERCICIO 2: Pide una Implementación Específica

**Contexto**: Tienes una API FastAPI. Necesitas agregar un endpoint que:
- Reciba un `email_id` (string)
- Descargue ese email de Gmail
- Devuelva el subject y el body del email

**Tu tarea**: Escríbeme un mensaje pidiendo que implemente este endpoint.

Incluye:
1. Contexto de tu proyecto
2. Qué debe hacer el endpoint
3. Especificaciones técnicas (método HTTP, path, request/response)
4. Restricciones o consideraciones

**Template**:
```
Estoy construyendo [PROYECTO].

Necesito agregar un endpoint a mi API FastAPI que [DESCRIPCIÓN].

ESPECIFICACIÓN:
- Método: [GET/POST/etc]
- Path: [/emails/{id} o similar]
- Request: [qué parámetros recibe]
- Response: [qué devuelve]
- Códigos de estado: [200, 404, etc]

CONTEXTO:
- [Cómo se integra con el resto de tu sistema]
- [Restricciones de seguridad/performance]

¿Puedes implementar este endpoint?
```

**Cuando termines**: Pégalo en el chat y yo implementaré el código. ✅

---

## EJERCICIO 3: Debuggea un Problema

**Contexto**: Este código está fallando:

```python
import requests

def descargar_pdf(url):
    response = requests.get(url)
    pdf_data = response.content
    return pdf_data
```

Error:
```
Traceback (most recent call last):
  File "main.py", line 5, in <module>
    pdf = descargar_pdf("https://example.com/factura.pdf")
  File "main.py", line 3, in descargar_pdf
    response = requests.get(url)
requests.exceptions.ConnectionError: Max retries exceeded
```

**Tu tarea**: Escríbeme un mensaje pidiendo ayuda para debuggear.

Incluye:
1. Qué esperabas que pasara
2. Qué está pasando
3. El código relevante
4. El error completo
5. Pregunta específica

**Template**:
```
Tengo un bug en [COMPONENTE/FUNCIÓN].

QUÉ ESPERABA:
[Comportamiento esperado]

QUÉ ESTÁ PASANDO:
[Comportamiento actual]

CÓDIGO:
[código relevante]

ERROR:
[traceback completo]

CONTEXTO:
[información adicional útil]

PREGUNTA:
[pregunta específica sobre el problema]
```

**Cuando termines**: Pégalo en el chat y yo te ayudaré a debuggear. ✅

---

## EJERCICIO 4: Solicita Revisión Arquitectónica

**Contexto**: Has diseñado esta arquitectura:

```
Usuario → CLI → API → Base de Datos
```

La CLI llama directamente a la API, y la API lee/escribe en la base de datos.

**Tu tarea**: Pídeme que revise esta arquitectura y te dé feedback.

Incluye:
1. Diagrama o descripción de tu arquitectura
2. Flujo de datos
3. Preguntas específicas que tienes
4. Preocupaciones o dudas

**Template**:
```
He diseñado esta arquitectura para [PROYECTO]:

DIAGRAMA:
[ASCII art o descripción]

FLUJO:
[Describe el flujo completo]

COMPONENTES:
[Lista cada pieza y su responsabilidad]

PREGUNTAS:
1. [¿Falta algo crítico?]
2. [¿Esta arquitectura escala?]
3. [¿Hay mejores alternativas?]
4. [pregunta específica tuya]

¿Puedes revisar y darme feedback?
```

**Cuando termines**: Pégalo en el chat y yo revisaré tu arquitectura. ✅

---

## EJERCICIO 5: Optimiza Código

**Contexto**: Este código funciona pero es muy lento:

```python
def procesar_facturas(facturas):
    resultados = []
    for factura in facturas:
        # Conecta a BD por cada factura
        conn = conectar_bd()
        datos = extraer_datos(factura)
        guardar_en_bd(conn, datos)
        conn.close()
        resultados.append(datos)
    return resultados
```

Para 1000 facturas, tarda 45 segundos.

**Tu tarea**: Pídeme que optimice este código.

Incluye:
1. El problema (lentitud)
2. Métricas actuales
3. Objetivo deseado
4. El código
5. Tu análisis del cuello de botella

**Template**:
```
Tengo un problema de performance en [FUNCIÓN/COMPONENTE].

PROBLEMA:
[Descripción del problema]

MÉTRICAS:
- Tiempo actual: [X segundos]
- Tiempo deseado: [Y segundos]
- Tamaño de datos: [N items]

CÓDIGO:
[código relevante]

ANÁLISIS:
[Tu hipótesis de por qué es lento]

PREGUNTA:
¿Cómo puedo optimizar esto?
```

**Cuando termines**: Pégalo en el chat y yo optimizaré el código. ✅

---

## EJERCICIO 6: Diseña una API desde Cero

**Contexto**: Estás construyendo un sistema de gestión de tareas (TODO app).

Funcionalidades:
- Crear tarea
- Listar tareas
- Marcar tarea como completada
- Eliminar tarea

**Tu tarea**: Diseña la API REST completa.

Para cada endpoint especifica:
- Método HTTP
- Path
- Request body (si aplica)
- Response body
- Códigos de estado

**Template**:
```
Necesito diseñar una API REST para [PROYECTO].

ENDPOINTS:

1. [NOMBRE DEL ENDPOINT]
   - Método: [GET/POST/etc]
   - Path: [/recursos]
   - Request: [body o params]
   - Response: [estructura JSON]
   - Códigos: [200, 201, 404, etc]
   - Descripción: [qué hace]

2. [ENDPOINT 2]
...

PREGUNTAS:
1. ¿Los nombres siguen REST correctamente?
2. ¿Faltan endpoints importantes?
3. ¿Los códigos de estado son apropiados?

¿Puedes revisar mi diseño?
```

**Cuando termines**: Pégalo en el chat y yo revisaré tu API. ✅

---

## EJERCICIO 7: Implementa Seguridad

**Contexto**: Tienes una API que ejecuta código Python generado por IA.

Riesgos:
- El código podría intentar borrar archivos
- El código podría hacer requests a URLs maliciosas
- El código podría consumir toda la RAM

**Tu tarea**: Pídeme que diseñe la estrategia de seguridad.

Incluye:
1. El riesgo que quieres mitigar
2. Restricciones que quieres imponer
3. Preguntas sobre implementación

**Template**:
```
Necesito implementar seguridad para [COMPONENTE].

CONTEXTO:
[Qué hace el componente y por qué es riesgoso]

RIESGOS:
1. [Riesgo 1]
2. [Riesgo 2]
3. [Riesgo 3]

RESTRICCIONES DESEADAS:
1. [Restricción 1]
2. [Restricción 2]
3. [Restricción 3]

PREGUNTAS:
1. ¿Cómo implemento estas restricciones?
2. ¿Qué tecnologías usar? (Docker, sandboxing, etc)
3. ¿Cómo valido que el código es seguro ANTES de ejecutarlo?

¿Puedes diseñar la estrategia de seguridad?
```

**Cuando termines**: Pégalo en el chat y yo diseñaré la estrategia. ✅

---

## EJERCICIO 8: Integra Múltiples Servicios

**Contexto**: Necesitas construir un pipeline que:
1. Escuche un webhook de Stripe (pago recibido)
2. Cree un registro en PostgreSQL
3. Envíe un email de confirmación con SendGrid
4. Actualice un Google Sheet con las ventas del día

**Tu tarea**: Pídeme que diseñe e implemente esta integración.

Incluye:
1. El flujo completo
2. Los servicios involucrados
3. Cómo deben comunicarse
4. Manejo de errores

**Template**:
```
Necesito construir un pipeline que integre múltiples servicios.

FLUJO:
1. [Paso 1: trigger]
2. [Paso 2: acción]
3. [Paso 3: acción]
...

SERVICIOS INVOLUCRADOS:
- [Servicio 1: qué hace]
- [Servicio 2: qué hace]
- [Servicio 3: qué hace]

ARQUITECTURA:
[Describe cómo se conectan]

PREGUNTAS:
1. ¿Cómo manejo errores si SendGrid falla?
2. ¿Debo usar colas (RabbitMQ, Redis)?
3. ¿Cómo hago esto idempotente? (si se ejecuta 2 veces, no duplica datos)

¿Puedes diseñar e implementar este pipeline?
```

**Cuando termines**: Pégalo en el chat y yo implementaré la integración. ✅

---

## EJERCICIO 9: Escala un Sistema

**Contexto**: Tu sistema Maisa funciona bien para 1 usuario, pero ahora tienes 100 usuarios concurrentes.

Problemas:
- PostgreSQL se satura (demasiados queries)
- Docker no puede crear más contenedores (límite del OS)
- GPT-4 rate limits (demasiadas llamadas/minuto)

**Tu tarea**: Pídeme que diseñe la estrategia de escalabilidad.

Incluye:
1. Los cuellos de botella actuales
2. La carga esperada (usuarios, requests/segundo)
3. Restricciones de presupuesto/infraestructura

**Template**:
```
Mi sistema funciona bien en desarrollo, pero necesito escalarlo a producción.

ARQUITECTURA ACTUAL:
[Diagrama simple]

PROBLEMAS:
1. [Cuello de botella 1 + métricas]
2. [Cuello de botella 2 + métricas]
3. [Cuello de botella 3 + métricas]

CARGA ESPERADA:
- [X usuarios concurrentes]
- [Y requests/segundo]
- [Z trabajadores ejecutándose simultáneamente]

RESTRICCIONES:
- Presupuesto: [cantidad/mes]
- Infraestructura: [cloud provider, constraints]

PREGUNTA:
¿Cómo escalo este sistema? ¿Qué tecnologías uso (Kubernetes, Redis, load balancers, etc)?
```

**Cuando termines**: Pégalo en el chat y yo diseñaré la estrategia de escalabilidad. ✅

---

## EJERCICIO 10: Crea Tests

**Contexto**: Tienes esta función:

```python
def validar_nif(nif: str) -> bool:
    """Valida que un NIF español sea correcto"""
    if len(nif) != 9:
        return False
    letras = "TRWAGMYFPDXBNJZSQVHLCKE"
    numero = int(nif[:-1])
    letra = nif[-1].upper()
    return letras[numero % 23] == letra
```

**Tu tarea**: Pídeme que cree tests unitarios completos.

Incluye:
1. Qué debe testear (casos válidos, inválidos, edge cases)
2. Framework de testing preferido (pytest, unittest)
3. Nivel de cobertura deseado

**Template**:
```
Necesito crear tests unitarios para esta función:

CÓDIGO:
[la función]

CASOS A TESTEAR:
1. [Caso válido: NIF correcto]
2. [Caso inválido: NIF incorrecto]
3. [Edge case: NIF vacío]
4. [Edge case: NIF con formato raro]
...

FRAMEWORK:
[pytest, unittest, otro]

OBJETIVO:
- Cobertura: [90%, 100%]
- Incluir tests parametrizados
- Incluir docstrings

¿Puedes crear los tests?
```

**Cuando termines**: Pégalo en el chat y yo crearé los tests. ✅

---

## CHECKLIST DE CALIDAD

Antes de enviarme cualquier mensaje, revisa:

- [ ] ¿Proporcioné contexto suficiente?
- [ ] ¿Fui específico con nombres, tipos, restricciones?
- [ ] ¿Expliqué el "por qué", no solo el "qué"?
- [ ] ¿Incluí ejemplos concretos si es aplicable?
- [ ] ¿Hice preguntas específicas?
- [ ] ¿El mensaje está bien estructurado (no es un párrafo gigante)?

---

## SIGUIENTE PASO

**Ahora mismo**: Elige el ejercicio 1, 2 o 3 (los más simples) y complétalo.

Cuando lo tengas listo, pégalo en el chat y yo te daré feedback inmediato y específico.

¡A practicar! 🚀
