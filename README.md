# Automatizaciones - Investigación y Desarrollo

Repositorio de investigación y desarrollo para crear una plataforma de **trabajadores digitales** que generen y ejecuten su propio código de forma autónoma.

## 🎯 Objetivo del Proyecto

Crear un sistema que permita:
- Describir tareas en lenguaje natural
- Generar código Python automáticamente para ejecutar esas tareas
- Ejecutar el código de forma segura en sandboxes aislados
- Mantener trazabilidad completa de cada ejecución (Chain-of-Work)
- Reducir errores mediante determinismo y aprendizaje

**Inspiración**: [Maisa](https://maisa.ai) - Startup española de trabajadores digitales con IA

---

## 📁 Estructura del Repositorio

```
/investigacion          # Research sobre IA, agentes, y mercado
  /referentes          # Análisis de Maisa, Make, y otros competidores
  /tecnologias         # Evaluación de LangGraph, n8n, etc.
  /conceptos           # Fundamentos: agentes vs automatizaciones
  negocio.md           # Modelo de negocio y estrategia

/proyecto              # Definición del proyecto específico
  ARQUITECTURA.md      # Arquitectura técnica del sistema
  vision.md            # Visión y concepto del producto
  roadmap.md           # Plan de desarrollo

/aprendizaje           # Recursos de arquitectura de software
  plan-arquitectura.md # Curso de arquitectura de sistemas
  guia-comunicacion-claude.md  # Cómo trabajar con Claude Code
  ejercicios-practica.md       # Ejercicios prácticos
```

---

## 🔍 Estado Actual

**Fase**: Investigación y diseño (Semana 1)

**Próximos pasos**:
1. Finalizar investigación de tecnologías (LangGraph vs custom)
2. Definir arquitectura detallada del MVP
3. Decidir stack tecnológico definitivo
4. Comenzar implementación del prototipo

---

## 🚀 Concepto Central

**Trabajador Digital** = Agente que se programa a sí mismo

```
Usuario: "Crea un trabajador que procese facturas"
  ↓
Sistema genera código Python paso a paso (LLM)
  ↓
Ejecuta código en sandbox seguro (Docker)
  ↓
Guarda cada paso en base de datos (Chain-of-Work)
  ↓
Si falla → Analiza error → Regenera código → Reintenta
  ↓
Aprende para futuras ejecuciones (Determinismo)
```

---

## 🛠️ Stack Tecnológico (En evaluación)

**Candidatos**:
- **Backend**: Python + FastAPI
- **Base de datos**: PostgreSQL
- **Sandbox**: Docker
- **LLM**: GPT-4 / Claude
- **Orquestación**: ¿LangGraph? ¿Custom?
- **Frontend**: React + shadcn/ui (futuro)

---

## 📚 Documentación Clave

### Para Entender el Proyecto
1. [proyecto/ARQUITECTURA.md](proyecto/ARQUITECTURA.md) - Diseño técnico completo
2. [proyecto/vision.md](proyecto/vision.md) - Qué problema resuelve
3. [investigacion/referentes/maisa.md](investigacion/referentes/maisa.md) - Análisis del referente principal

### Para Investigación
- [investigacion/conceptos/agentes-vs-automatizaciones.md](investigacion/conceptos/agentes-vs-automatizaciones.md)
- [investigacion/tecnologias/langgraph.md](investigacion/tecnologias/langgraph.md)
- [investigacion/negocio.md](investigacion/negocio.md)

### Para Aprender Arquitectura
- [aprendizaje/guia-comunicacion-claude.md](aprendizaje/guia-comunicacion-claude.md)
- [aprendizaje/plan-arquitectura.md](aprendizaje/plan-arquitectura.md)

---

## 🤖 Trabajando con Claude Code

Este proyecto usa Claude Code como copiloto técnico. Ver [CLAUDE.md](CLAUDE.md) para instrucciones completas.

**Principios clave**:
- Proporcionar contexto arquitectónico en cada request
- Explicar el "por qué", no solo el "qué"
- Usar ejemplos concretos
- Pedir feedback en decisiones de diseño

---

## 📊 Competencia Analizada

| Empresa | Enfoque | Diferenciación |
|---------|---------|----------------|
| **Maisa** | No-code, anti-alucinaciones | Referente principal |
| **Make** | Visual automation | Muy limitado para código |
| **n8n** | Low-code workflows | Bueno para APIs, malo para lógica compleja |

**Nuestra diferenciación**:
- Open-source
- Código generado visible y editable
- Pricing accesible para SMBs
- Máxima transparencia (Chain-of-Work)

---

## 📝 Notas

- Este repo es **solo investigación y documentación** por ahora
- El código de implementación podría ir en repo separado (TBD)
- Fase de investigación: ~1 semana
- Diseño arquitectónico: ~1 semana
- Implementación MVP: ~4 semanas

---

## 🔗 Referencias

- [Maisa AI](https://maisa.ai)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- Transcripts de podcasts en [investigacion/referentes/](investigacion/referentes/)

---

Última actualización: 2025-10-21
