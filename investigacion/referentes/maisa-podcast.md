# Análisis Completo: Qué Hace Maisa (Basado en Podcast con el CTO)

He analizado el podcast completo con David Villalón, CTO y cofundador de Maisa. Aquí está TODO lo que hacen y cómo lo hacen.

---

## 1. QUÉ ES MAISA EN UNA FRASE

**Maisa es una plataforma que genera código Python ON-THE-FLY para automatizar procesos empresariales complejos, lo ejecuta en entornos controlados, y guarda TODO en un Chain-of-Work 100% auditable.**

---

## 2. EL PROBLEMA QUE RESUELVEN

### El mercado actual (RAG, Function Calls, Agentes tradicionales):

**Tiene 3 problemas fundamentales:**

1. **No es auditable**: No sabes REALMENTE qué hizo la IA
   - El "chain of thought" (cadena de pensamiento) NO es verdad
   - Hay un paper: "Chain of Thought is NOT Explainability"
   - Si el agente te dice "busqué en la BD", no sabes si realmente lo hizo o cómo

2. **No es determinista**: Mismo input ≠ mismo output
   - Si das los mismos datos 2 veces, obtienes resultados diferentes
   - No puedes confiar en que funcione igual siempre
   - Alucinaciones imprevisibles

3. **No escala a producción enterprise**:
   - Necesitas humanos revisando TODO el output
   - El humano tarda MÁS en revisar que en hacer la tarea manualmente
   - No hay ROI (retorno de inversión)
   - 95% de proyectos de IA en enterprise NO llegan a producción (MIT report)

### Por qué fallan las aproximaciones actuales:

```
APROXIMACIÓN 1: Workflows agénticos (n8n, Make, Open AI)
├─ Problema: Muy rígidos
├─ No se adaptan a casos inesperados
└─ Requieren programar cajitas con flechas (nadie sabe hacer eso)

APROXIMACIÓN 2: Agentes multi-herramienta (LangChain, CrewAI)
├─ Problema: No puedes crear lógica con function calls
├─ No puedes hacer loops, try/catch, lógica compleja
├─ El LLM decide qué tools usar (no determinista)
└─ La "explicación" del agente NO es verdad

APROXIMACIÓN 3: Code Interpreter como tool
├─ Problema: No controlas el entorno de ejecución
├─ Genera scripts enteros de golpe (sin contexto)
└─ No puedes auditar qué hizo realmente
```

---

## 3. LA SOLUCIÓN DE MAISA: KPU (Knowledge Processing Unit)

### Concepto core:

**En vez de que un LLM "piense" y use herramientas, el LLM GENERA CÓDIGO PYTHON que se ejecuta en un entorno controlado.**

### Cómo funciona (paso a paso):

```
PASO 1: Usuario define el trabajador digital
├─ Lenguaje natural: "Lee facturas, extrae NIF, valida en BD..."
├─ NO son workflows visuales
└─ NO es prompt engineering

PASO 2: Maisa Studio prepara el "cerebro" del trabajador
├─ Instrucciones (qué hacer)
├─ Variables de entrada (qué datos necesita)
├─ Know-how (conocimiento específico del negocio)
├─ Tools disponibles (APIs, BD, navegadores)
└─ TODO en lenguaje natural

PASO 3: El trabajador recibe datos y empieza a ejecutar
├─ El LLM NO ejecuta todo de golpe
├─ Va generando código PASO A PASO
├─ Cada paso: 2-3 líneas de código Python
└─ Ve el resultado → decide siguiente paso

PASO 4: Ejecución en entorno controlado
├─ Sandbox (ordenador virtual aislado)
├─ Con permisos controlados
├─ Con credenciales gestionadas
└─ Límites de recursos

PASO 5: Chain-of-Work (auditoría total)
├─ Se guarda CADA paso de código generado
├─ Se guarda el resultado de cada paso
├─ Se guarda qué knoh know-how usó
├─ Se guarda qué herramientas utilizó
└─ Se guarda qué datos procesó

PASO 6: Verificación (Checker)
├─ Otro agente (también KPU) revisa el código generado
├─ Verifica que siguió las instrucciones
├─ Verifica que el resultado tiene sentido
└─ Conservador: prefiere falsos negativos a falsos positivos

PASO 7: Segunda ejecución = DETERMINISTA
├─ Si los MISMOS datos vuelven a entrar
├─ Se ejecuta el MISMO código que funcionó
├─ Resultado 100% consistente
└─ Esto es lo que NO puede hacer ningún agente tradicional
```

---

## 4. DIFERENCIAS CLAVE CON OTRAS SOLUCIONES

### vs. n8n / Make / Open AI workflows:

| n8n/Make | Maisa |
|----------|-------|
| Cajitas con flechas | Lenguaje natural |
| Flujo predefinido rígido | Se adapta on-the-fly |
| Si cambia el formato → se rompe | Entiende el contexto |
| Requiere técnicos | Lo usa el business user |

### vs. Agentes con LangChain / Function Calls:

| LangChain | Maisa |
|-----------|-------|
| Function calls predefinidos | Genera código libre |
| No puedes hacer lógica (loops, try/catch) | Código Python completo |
| El LLM decide qué tools usar | El código decide qué hacer |
| No auditable (chain of thought falso) | 100% auditable (código real) |
| No determinista | Determinista en 2ª ejecución |

### vs. Code Interpreter (Claude Code, GPT Code Interpreter):

| Code Interpreter | Maisa |
|------------------|-------|
| Genera scripts enteros de golpe | Genera paso a paso (2-3 líneas) |
| No controlas el entorno | Entorno 100% controlado |
| No puedes combinar con tools externas | Integra todo (APIs, BD, navegadores) |
| No hay Chain-of-Work | Auditoría completa |

---

## 5. EJEMPLO REAL: PROCESAMIENTO DE FACTURAS

### Caso de uso del primer cliente (Enero 2024):

**Problema**:
- Banco recibe facturas en PDF por email
- Formatos MUY variables (escaners, PDFs, múltiples facturas en un email)
- RPA tradicional: 65% de éxito
- Necesitan: extraer datos, validar NIF, buscar proveedor, conciliar con BD, postear resultado

**Solución Maisa**:

1. Usuario define en lenguaje natural:
```
"Lee el email de facturas@proveedor.com,
descarga el PDF adjunto,
extrae NIF y importe,
busca el proveedor en la base de datos,
valida que está autorizado,
guarda en la tabla 'facturas' si todo OK,
si no, envía email de error"
```

2. Maisa Studio autoconfigura:
   - Detecta que necesita acceso a Gmail
   - Detecta que necesita OCR para leer PDF
   - Detecta que necesita acceso a BD de proveedores
   - Detecta que necesita enviar emails
   - Genera las instrucciones y know-how

3. Cuando llega una factura:
```python
# PASO 1 (código generado on-the-fly)
import gmail_api
email = gmail_api.buscar(remitente='facturas@proveedor.com', ultimo=True)
pdf_bytes = gmail_api.descargar_adjunto(email.id, tipo='pdf')

# PASO 2 (código generado on-the-fly)
import pdf_reader
texto = pdf_reader.extraer_texto(pdf_bytes)
nif = pdf_reader.extraer_campo(texto, campo='NIF')

# PASO 3 (código generado on-the-fly)
import database
proveedor = database.query("SELECT * FROM proveedores WHERE nif = ?", [nif])
if not proveedor:
    raise ValueError(f"Proveedor no autorizado: {nif}")

# PASO 4 (código generado on-the-fly)
factura_id = database.insert("facturas", {
    "nif": nif,
    "importe": importe,
    "email_id": email.id,
    "estado": "OK"
})
```

4. Chain-of-Work guarda TODO:
```json
{
  "pasos": [
    {
      "id": 1,
      "accion": "Buscar email",
      "codigo": "email = gmail_api.buscar(...)",
      "resultado": {"id": "email_123", "found": true},
      "duracion": "0.8s"
    },
    {
      "id": 2,
      "accion": "Extraer NIF",
      "codigo": "nif = pdf_reader.extraer_campo(...)",
      "resultado": {"nif": "B12345678"},
      "duracion": "1.2s"
    },
    ...
  ]
}
```

**Resultado**:
- De 65% éxito (RPA tradicional) → 98% éxito
- El 2% que falla, sabes EXACTAMENTE por qué
- 3000-4000 facturas/mes procesadas desde Enero 2024
- Cliente paga €600/mes (antes pagaba €15.000/año por RPA tradicional)

---

## 6. EJEMPLO DE USO: DEMO EN VIVO DEL PODCAST

### Caso: Gestión de Subpoenas (Requerimientos Legales)

**Tarea**:
- Un banco recibe un requerimiento legal (subpoena) pidiendo información de un cliente
- Hay que leer el PDF, buscar al cliente en la BD, buscar cuentas relacionadas, generar informe

**Proceso con Maisa Studio**:

1. **Definir en chat**:
```
Usuario: "Lee la subpoena PDF, busca por la información que se pide,
         busca otras posibles cuentas relacionadas,
         envía email con toda la información"
```

2. **Maisa Studio pregunta** (autoconfigura):
```
Studio: "¿Qué tipo de database utilizas?"
Usuario: "Un Google Sheet con los clientes"
Studio: "¿A qué email envío el resultado?"
Usuario: "david@ejemplo.com"
```

3. **Usuario ajusta** (opcional):
```
Studio: "Necesito: account number, email, phone number"
Usuario: "No tengo esos datos, están en la subpoena. Extr áelos del documento"
```

4. **Click en "RUN"** → El trabajador ejecuta:

```
CHAIN-OF-WORK GENERADO:

Paso 1: Identificar account number (1.2s)
├─ Código: Leer PDF y buscar patrón de account number
├─ Resultado: "89526" encontrado
└─ Know-how usado: "Account numbers son 5 dígitos"

Paso 2: Preparar acceso a base de datos (0.8s)
├─ Código: Conectar a Google Sheets
├─ Resultado: Conexión OK
└─ Herramienta: google_sheets_api

Paso 3: Buscar cliente (2.1s)
├─ Código: Query en Google Sheet por account number
├─ Resultado: Cliente "Peter Ford" encontrado
└─ Datos: email, address, phone

Paso 4: Buscar cuentas relacionadas (3.4s)
├─ Código: Loop buscando mismo email en otras cuentas
├─ Resultado: 2 cuentas adicionales encontradas
└─ Lógica: if email == cliente.email → añadir

Paso 5: Generar informe (1.5s)
├─ Código: Crear documento con todos los datos
├─ Resultado: Informe generado
└─ Formato: Email HTML

Paso 6: Enviar email (0.6s)
├─ Código: smtp.send(destinatario, informe)
├─ Resultado: Email enviado OK
└─ Timestamp: 2024-10-17 11:35
```

**Tiempo total**: 1 minuto 39 segundos

**¿Qué pasaría con un agente tradicional?**
- No sabrías si realmente buscó en todas las cuentas
- No sabrías por qué encontró 2 cuentas relacionadas
- Si falla, no sabrías en qué paso
- Si lo vuelves a ejecutar, podría dar resultados diferentes

**Con Maisa**:
- Ves TODO el código que ejecutó
- Ves CADA decisión que tomó
- Si falla, ves EXACTAMENTE dónde y por qué
- Si lo vuelves a ejecutar con los mismos datos → mismo resultado

---

## 7. MAISA STUDIO: LA INTERFAZ

### Componentes principales:

```
┌─────────────────────────────────────────────────────────┐
│                    MAISA STUDIO                         │
├────────────────────────┬────────────────────────────────┤
│                        │                                │
│  WORKER BUILDER        │    CEREBRO DEL TRABAJADOR      │
│  (Chat Izquierda)      │    (Panel Derecha)             │
│                        │                                │
│  - Ayuda a definir     │  - Instructions (qué hacer)    │
│    el proceso          │  - Input Variables (datos)     │
│  - Hace preguntas      │  - Know-how (conocimiento)     │
│  - Autoconfigura       │  - Tools (herramientas)        │
│  - Busca              │  - Output (resultado esperado) │
│    contradicciones     │                                │
│  - Optimiza            │                                │
│                        │                                │
└────────────────────────┴────────────────────────────────┘
```

### Funcionalidades clave:

1. **Onboarding con lenguaje natural**:
   - Usuario describe la tarea como si explicara a un junior
   - El chat va preguntando detalles
   - Se autoconfigura automáticamente

2. **Worker Builder (Asistente)**:
   - Te ayuda a traducir lenguaje de negocio a proceso
   - Busca contradicciones en tus instrucciones
   - Optimiza el proceso
   - Responde preguntas sobre la plataforma

3. **Integraciones** (350+ disponibles):
   - Se autoconfiguran hablando en el chat
   - Soporta MCP (Model Context Protocol)
   - APIs, navegadores, bases de datos
   - Ejemplo: "Necesito conectar con Supabase" → se autoconfigura

4. **Versiones**:
   - Sistema de control de versiones (como Git)
   - Puedes tener v1, v2, v3... del mismo trabajador
   - Deploy asíncrono (cambias versión sin afectar API)

5. **Control Tower** (después de deploy):
   - Generar tokens para compartir
   - On-premises o cloud
   - Gestión de permisos
   - Monitoreo de ejecuciones

---

## 8. TECNOLOGÍA: KPU (Knowledge Processing Unit)

### ¿Qué es una KPU?

**Es como una CPU, pero para IA:**

```
CPU (Computer):
├─ Ejecuta instrucciones de código (assembly)
├─ Paso a paso
├─ Determinista
└─ En un procesador físico

KPU (Maisa):
├─ Ejecuta "instrucciones" en lenguaje natural
├─ Genera código paso a paso (2-3 líneas)
├─ Determinista en 2ª ejecución
└─ En un "ordenador virtual" controlado
```

### Evolución de las KPUs de Maisa:

**KPU v1 (Marzo 2023)**:
- Primera versión
- No sabían muy bien para qué usarla
- Demostraba que funcionaba el concepto

**KPU v2 "Binchi" (Octubre 2023)**:
- Mismo performance que v1
- Usando Sonnet 3.5 (más barato que GPT-4)
- Fracción del coste

**KPU v3 (Próximamente)**:
- "Gordo gordo" (palabras de David)
- Trabajadores digitales que trabajan 200+ horas (vs 3 horas ahora)
- Profundidad de tareas mucho mayor
- **Autorecursión**: KPUs que se llaman a sí mismas
- Comparten entorno entre "hijos"
- Gestión de contexto virtual

### Características técnicas:

1. **Entorno controlado** (la innovación clave):
```python
entorno_trabajador = {
    "permisos": ["leer_db", "escribir_db", "enviar_email"],
    "credenciales": {
        "gmail": "...",
        "database": "...",
        # La IA NO puede acceder a estas credenciales
        # Pero SÍ puede usarlas a través del entorno
    },
    "recursos": {
        "memoria": "256MB",
        "timeout": "30s",
        "network": "limitada"
    },
    "herramientas": ["gmail_api", "pdf_reader", "database"],
    "codigo_cache": {
        # Código que ya funcionó para ciertos inputs
        "hash_abc123": "email = gmail_api.buscar(...)"
    }
}
```

2. **Generación de código incremental**:
```
NO HACE ESTO (mal):
├─ Generar script entero de 200 líneas
└─ Ejecutar todo de golpe

HACE ESTO (bien):
├─ Paso 1: Generar 2-3 líneas
├─ Ejecutar
├─ Ver resultado
├─ Paso 2: Generar siguiente 2-3 líneas basado en resultado anterior
├─ Ejecutar
├─ ...
└─ Paso N: Terminar cuando task completada
```

3. **Checker (Quality Assurance)**:
```python
# Después de cada ejecución
checker_result = otra_kpu.verificar(
    codigo_generado=chain_of_work,
    instrucciones=trabajador.instrucciones,
    know_how=trabajador.know_how,
    resultado=output_final
)

if checker_result == "NO_VALIDO":
    marcar_como_error()
    notificar_humano()
else:
    marcar_como_exito()
    cachear_codigo()  # Para siguiente vez
```

---

## 9. CHAIN-OF-WORK: LA CLAVE DE LA AUDITABILIDAD

### Qué se guarda en el Chain-of-Work:

```json
{
  "execution_id": "exec_abc123",
  "worker_id": "invoice_processor_v2",
  "timestamp": "2024-10-17T10:30:00Z",
  "input_data": {
    "email_id": "email_456"
  },
  "steps": [
    {
      "step_id": 1,
      "action": "Buscar email en Gmail",
      "code_generated": "email = gmail_api.buscar(remitente='facturas@proveedor.com')",
      "code_language": "python",
      "execution_time": "0.8s",
      "result": {
        "success": true,
        "data": {"id": "email_456", "subject": "Factura FRA-2024-001"}
      },
      "know_how_used": ["Gmail API requiere OAuth2", "Buscar últimos 10 emails"],
      "tools_used": ["gmail_api"]
    },
    {
      "step_id": 2,
      "action": "Descargar PDF adjunto",
      "code_generated": "pdf = gmail_api.descargar_adjunto(email.id, tipo='pdf')",
      "execution_time": "1.2s",
      "result": {
        "success": true,
        "data": {"size": "234KB", "type": "application/pdf"}
      }
    },
    {
      "step_id": 3,
      "action": "Extraer NIF del PDF",
      "code_generated": "texto = pdf_reader.extraer_texto(pdf)\nnif = regex.search(r'NIF:\\s*([A-Z0-9]+)', texto).group(1)",
      "execution_time": "2.1s",
      "result": {
        "success": true,
        "data": {"nif": "B12345678"}
      },
      "know_how_used": ["NIFs españoles formato: letra + 8 dígitos"]
    },
    ...
  ],
  "final_result": {
    "status": "SUCCESS",
    "factura_id": 1234,
    "total_time": "8.7s"
  },
  "checker_validation": {
    "valid": true,
    "confidence": 0.95,
    "notes": "Todas las instrucciones seguidas correctamente"
  }
}
```

### Por qué esto es revolucionario:

**Agente tradicional (LangChain)**:
```
Output:
"He procesado la factura correctamente.
Primero busqué el email, luego descargué el PDF,
extraje el NIF B12345678, validé en la BD..."

Problema: ¿Esto es VERDAD?
- No sabes si realmente hizo esos pasos
- "Chain of thought is NOT explainability" (paper)
- El LLM puede inventar la explicación
```

**Maisa con Chain-of-Work**:
```
Output:
- Código Python REAL que se ejecutó: [ver código]
- Resultado de CADA paso: [ver resultados]
- Tiempo de ejecución: 8.7s
- Tools usadas: gmail_api, pdf_reader, database

Ventaja: Es IMPOSIBLE mentir
- El código se ejecutó o no se ejecutó
- El resultado es el del código real
- Puedes REPRODUCIR la ejecución
- Puedes DEBUG el fallo exacto
```

---

## 10. CASOS DE USO REALES

### 1. Invoice Processing (Primer cliente, Enero 2024):
- **Tarea**: Procesar facturas variables de múltiples proveedores
- **Antes**: RPA con 65% éxito, €15.000/año
- **Después**: Maisa con 98% éxito, €600/mes
- **Volumen**: 3000-4000 facturas/mes
- **Estado**: En producción desde hace 10 meses

### 2. Subpoenas (Requerimientos legales):
- **Tarea**: Procesar requerimientos legales, buscar clientes, generar informes
- **Complejidad**: PDFs variables, búsquedas en BD, cuentas relacionadas
- **Tiempo**: ~2 minutos por subpoena
- **Estado**: Demo funcional

### 3. Trade Finance:
- **Tarea**: Leer múltiples documentos, consultar 3 BDs, hacer conciliación, generar documento, subir a BD
- **Complejidad**: Alta (mencionado como ejemplo complejo)
- **Estado**: En producción

### 4. Cierre Contable:
- **Tarea**: Proceso end-to-end de cierre contable
- **Complejidad**: Muy alta (documentos, conciliaciones, validaciones)
- **Estado**: En producción con cliente

---

## 11. NÚMEROS Y MÉTRICAS

### Clientes y facturación:

- **7 clientes** (casi todos bancos y financieras)
- **€4 millones de facturación anual** (con solo 7 clientes!)
- **Ticket promedio**: ~€500k/año por cliente
- **Primer cliente**: €600/mes (pequeño, caso especial)
- **Clientes enterprise**: €1-6 millones/año

### Equipo:

- **40 personas** (casi)
- **60 personas** esperadas para fin de año
- **Perfiles que buscan**:
  - UX/Producto
  - IA + Python (mezcla de aplicada + programación)
  - Forward Deploy Engineers / DevOps
  - Sales / Go-to-Market

### Funding:

- **Pre-seed**: €300-400k (Business Angels, Pablo Fernández)
- **Seed**: $5 millones USD (mitad de 2024, anunciado Diciembre 2024)
  - Liderada por: Peter Thiel's fund + Forge Point Capital
  - Acompañan: NFX + Village Global
  - Valoración: ~$20M pre-money
- **Serie A**: $25 millones USD (recientemente cerrada)
  - Liderada por: Peter Thiel + Forge Point Capital
  - Valoración: >$100M post-money

### Hitos técnicos:

- **Marzo 2023**: KPU v1 (primera versión)
- **Octubre 2023**: KPU v2 "Binchi" (mismo performance, más barato)
- **Enero 2024**: Primer cliente en producción
- **Octubre 2024**: 7 clientes, €4M facturación
- **Próximamente**: KPU v3 (autorecursión, 200+ horas de ejecución)

---

## 12. MERCADO OBJETIVO Y ESTRATEGIA

### Mercado principal: **Enterprise Regulado**

- **Banca y Servicios Financieros** (foco principal)
- **Telecomunicaciones** (a través de partners)
- **Energía** (a través de partners)
- **Seguros**

### Por qué este mercado:

1. **Valoran la auditabilidad** (crítico en regulado)
2. **Tienen presupuesto** (€1-6M/año sin problema)
3. **Tienen casos de uso claros** (RPA que no funciona)
4. **Necesitan determinismo** (compliance)
5. **Tienen procesos complejos** (no resueltos con RPA tradicional)

### Modelo de Go-to-Market:

```
ESTRATEGIA MULTI-CANAL:

1. DIRECTO ENTERPRISE
   ├─ Venta directa a bancos
   ├─ Proceso largo (meses)
   ├─ Ticket alto (€1-6M/año)
   └─ Foco en España, Europa, USA

2. PARTNERS (CONSULTORAS E INTEGRADORES)
   ├─ Ya tienen acceso al cliente
   ├─ Llevan Maisa a otros sectores
   ├─ Aceleran penetración
   └─ Land-and-expand

3. CLOUD (USUARIOS TÉCNICOS)
   ├─ Onboarding self-service
   ├─ Ticket bajo (€10-100/mes)
   ├─ Sirve para aprender
   └─ No requiere soporte 24/7

4. CLOUD PROVIDERS (AWS, Azure, GCP)
   ├─ Para hiperscalar
   ├─ En roadmap
   └─ Partnerships estratégicos
```

### Competencia:

**Según David: "No hay nadie haciendo lo que nosotros hacemos"**

Competidores indirectos:
- **RPA tradicional**: UiPath, Blue Prism, Power Automate
  - Problema: No se adaptan, 65% éxito
- **n8n, Zapier, Make**: Workflows agénticos
  - Problema: Muy rígidos, requieren cajitas con flechas
- **LangChain, CrewAI**: Frameworks de agentes
  - Problema: No deterministas, no auditables
- **Claude Code, GPT Code Interpreter**: Generación de código
  - Problema: No tienen el entorno controlado, no Chain-of-Work

Maisa está en un **océano azul**: son los únicos con generación de código + entorno controlado + Chain-of-Work + determinismo.

---

## 13. VENTAJAS COMPETITIVAS (MOATS)

### 1. **Tecnología (KPU)**:
- Patentable (probablemente)
- 2 años de desarrollo
- 3 versiones iteradas
- Próxima versión "gordo gordo"

### 2. **Know-how de producción**:
> "Somos los únicos que sabemos qué cuesta llevar a producción casos de uso de esta magnitud"

- 10 meses en producción (desde Enero 2024)
- 7 clientes funcionando
- 40,000 horas/año de trabajo humano reemplazado
- Todos los edge cases descubiertos y resueltos

### 3. **Acceso a enterprise**:
- Ya dentro de bancos TOP
- Proceso de entrada es LENTO (meses)
- Una vez dentro → land-and-expand
- Referencias de clientes existentes

### 4. **Equipo técnico único**:
- **Manuel Romero** (cofundador):
  - 500+ modelos en HuggingFace
  - 184 millones de descargas
  - Más descargas que Mistral (empresa)
  - Español con más modelos en HuggingFace
- **David Villalón** (cofundador CTO):
  - Visión de sistema operativo de IA
  - Experiencia en deeptech

### 5. **Agnosticismo de modelos**:
- Funciona con GPT-4, Claude, Gemini, modelos locales
- Clientes enterprise pueden elegir su modelo
- No dependen de OpenAI/Anthropic

---

## 14. VISIÓN DE FUTURO

### Sistema Operativo de IA (LLM OS):

> "No visualizo el GPT-50 AGI. Para mí AGI será un sistema, como Internet."

**Concepto**:
- No hay UN modelo que sea AGI
- AGI es el ECOSISTEMA de modelos + herramientas + entornos
- Como Internet: no nació en un día, fue evolucionando
- Ya estamos en AGI (parcialmente): TikTok, Gmail, todo usa IA

**Visión de Maisa**:
```
FUTURO (5-10 años):
├─ Los programas se construyen on-the-fly
├─ La UI se adapta al contexto del usuario
├─ Las BDs forman parte del contexto del modelo (trillones de tokens)
├─ Todo es dinámico y se adapta al entorno
├─ La interacción humano-tecnología cambia radicalmente
└─ Sistema operativo = entorno donde la IA opera y construye
```

**Analogía del micelio**:
- Hongos bajo el bosque
- Cada nodo NO es inteligente
- Pero el CONJUNTO se coordina
- Reparte nutrientes
- Avisa de incendios
- Sistema distribuido

**Cómo afecta hoy**:
- Tu opinión ya está influenciada por IA (TikTok, YouTube)
- Tus emails ya los escribe IA (parcialmente)
- El contenido que consumes ya lo elige IA
- AGI no será un evento, será gradual

### Roadmap técnico de Maisa:

**Corto plazo (6-12 meses)**:
- KPU v3 con autorecursión
- Trabajadores que trabajan 200+ horas
- Más integraciones (ya tienen 350+)
- Mejorar UX de Maisa Studio
- Escalabilidad (gestión de concurrencia y picos)

**Medio plazo (1-3 años)**:
- Convertirse en el referente de trabajadores digitales para enterprise regulado
- Partners con consultoras e integradores
- Presencia en España, Europa, USA
- Cloud self-service para startups
- Sistema de aprendizaje (HALP - Human-Augmented LLM Processing)

**Largo plazo (3-10 años)**:
- Sistema operativo de IA
- Trabajadores digitales que se auto-mejoran
- Ecosistema de trabajadores que colaboran
- Standard de la industria para auditabilidad

---

## 15. DESAFÍOS Y LIMITACIONES

### Desafíos técnicos:

1. **Escalabilidad de infraestructura**:
   - Gestionar 1000s de "ordenadores virtuales" concurrentes
   - Cada uno con credenciales, permisos, recursos
   - Picos de demanda
   - Costes de compute

2. **Integraciones complejas**:
   - Sistemas legacy (mainframes)
   - APIs sin documentación
   - Navegadores (Selenium)
   - Credenciales y tokens que expiran

3. **Límites actuales de los LLMs**:
   - Ventana de contexto (aunque creciendo)
   - Velocidad (aunque mejorando: 60 tokens/s → 500k tokens/s en el futuro)
   - Costes (GPT-4 es caro)
   - Alucinaciones (aunque resistente con código)

4. **Edge cases infinitos**:
   - El mundo real es caótico
   - Siempre hay casos que no esperabas
   - Necesitas aprender de cada error

### Desafíos de negocio:

1. **Venta enterprise es LENTA**:
   - Meses para entrar
   - Tienen que pasar por CISO (seguridad)
   - Compliance
   - Múltiples stakeholders

2. **Competencia con áreas internas**:
   - Equipos de IA del cliente se sienten amenazados
   - "Llevan 1 año invirtiendo en su solución"
   - Maisa llega y dice "está mal el approach"

3. **Educación del mercado**:
   - Es un paradigma nuevo
   - Difícil de explicar
   - "Me ha costado TODO el podcast explicarlo"

4. **Costes de soporte**:
   - Enterprise exige 24/7
   - Necesitas Forward Deploy Engineers
   - Cada cliente es único

5. **Presión del mercado**:
   - "Maratón de keniatas" (ritmo insostenible)
   - Todo cambia cada 3 meses
   - GPT-5, Claude 4, Gemini 2...

### Limitaciones actuales:

1. **No es para tiempo real**:
   - Procesa tareas en minutos, no segundos
   - No es un chatbot
   - Latencia: 1-3 minutos por tarea

2. **Primera ejecución no es determinista**:
   - Solo la segunda ejecución con mismos datos es 100% determinista
   - La primera vez, genera código nuevo

3. **No es 100% perfecto**:
   - 98% de éxito (vs 65% del RPA)
   - El 2% puede fallar
   - Pero SABES por qué falla

4. **Requiere definición clara**:
   - Si el negocio no sabe qué quiere, Maisa no lo puede hacer
   - Know-how tiene que estar bien definido
   - Garbage in, garbage out

---

## 16. CONCLUSIONES: QUÉ HACE MAISA (RESUMIDO)

### En una frase:
**Maisa permite crear trabajadores digitales que ejecutan procesos complejos generando código Python on-the-fly en entornos controlados, con auditabilidad total y determinismo en la segunda ejecución.**

### Los 3 pilares:

1. **KPU (Knowledge Processing Unit)**:
   - Genera código paso a paso
   - Ejecuta en entorno controlado
   - Se adapta a casos inesperados

2. **Chain-of-Work**:
   - Auditoría 100% de qué hizo
   - Código real ejecutado
   - Resultados verificables

3. **Determinismo**:
   - Mismos inputs → mismos outputs (2ª ejecución)
   - Crítico para enterprise regulado
   - Imposible con agentes tradicionales

### Diferenciadores clave:

| Característica | Maisa | Competencia |
|----------------|-------|-------------|
| Genera código | ✅ Sí, paso a paso | ❌ No (o scripts enteros) |
| Entorno controlado | ✅ Sí, 100% | ❌ No |
| Auditabilidad | ✅ Chain-of-Work | ❌ "Chain of thought" falso |
| Determinismo | ✅ 2ª ejecución | ❌ Nunca |
| Lenguaje natural | ✅ Sí | ⚠️ Parcial (workflows) |
| Lógica compleja | ✅ Código Python | ❌ Function calls limitados |
| Enterprise ready | ✅ Sí (en producción) | ❌ 95% no llega a prod |

### Por qué importa:

1. **Enterprise regulado** necesita auditabilidad → Maisa lo da
2. **RPA tradicional** falla en casos complejos → Maisa se adapta
3. **Agentes con LLMs** no son deterministas → Maisa sí (2ª vez)
4. **Workflows visuales** son rígidos → Maisa usa lenguaje natural

### El futuro según Maisa:

- AGI no será UN modelo, será un ECOSISTEMA
- Maisa quiere ser el "sistema operativo" donde operan los trabajadores digitales
- La próxima revolución es cómo INTERACTUAMOS con la tecnología
- Los programas se construirán on-the-fly, adaptándose al contexto
- Estamos en el 10% del mercado, queda el 90% por resolver

---

## 17. PARA TU PROYECTO

### ¿Deberías hacer algo como Maisa?

**Ventajas de replicar el approach**:
- ✅ Auditabilidad total (crítico para enterprise)
- ✅ Determinismo (crítico para regulado)
- ✅ Se adapta a casos inesperados
- ✅ Funciona en producción (demostrado)

**Desventajas / Dificultad**:
- ❌ Muy complejo de construir (2 años de Maisa)
- ❌ Requiere gestionar entornos controlados (infraestructura)
- ❌ Necesitas expertise en LLMs + infra + producto
- ❌ Competir con Maisa (ya levantaron $30M, tienen tracción)

### Recomendación:

**Para tu caso de facturas**:
- Usa el CONCEPTO de Maisa (generar código, ejecutar, auditar)
- Pero simplificado: no necesitas toda la plataforma
- MVP: LLM genera Python → ejecuta en Docker → guarda logs
- Escala: si funciona, construye más features

**Para competir con Maisa**:
- Difícil en enterprise (ya tienen ventaja)
- Oportunidad en **SMB** (€5-15k/año vs €500k de Maisa)
- Maisa no puede atender SMB (coste de soporte alto)
- Tu nicho: automatizaciones para SMB con la tecnología de Maisa

**Stack recomendado** (inspirado en Maisa):
```
Backend:
├─ FastAPI (API)
├─ GPT-4 (generar código)
├─ Docker (sandbox)
├─ PostgreSQL (Chain-of-Work)
└─ Celery + Redis (workers)

Frontend:
├─ React + Monaco editor
└─ Chat para definir trabajadores

Diferenciador:
├─ Precio SMB (€50-500/mes vs €50k+ de Maisa)
├─ Self-service total
└─ Templates para casos comunes
```

---

**RESUMEN FINAL**: Maisa ha creado una nueva categoría. No son RPA, no son agentes tradicionales. Son "trabajadores digitales" que generan código on-the-fly, lo ejecutan de forma controlada, y dan auditabilidad total. Perfecto para enterprise regulado. Tu oportunidad: mismo concepto para SMB.
