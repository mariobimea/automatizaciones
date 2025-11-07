# 🛡️ VALIDACIONES - Sistema de Prevención de Errores

**Fecha Creación**: 6 Noviembre 2025
**Estado**: 📝 Backlog (Future enhancements)
**Owner**: Mario Ferrer

---

## 📋 RESUMEN

Documento que recopila validaciones necesarias para prevenir errores comunes en la ejecución de workflows AI-powered.

---

## 🚨 VALIDACIONES PENDIENTES

### **1. Validación de Context antes de generación de código**

**Problema:**
- El LLM podría generar código asumiendo que ciertas keys existen en el context
- Si el context llega vacío o incompleto, el código generado podría:
  - Usar mock data inventado
  - Fallar en runtime con KeyError
  - Generar código genérico no adaptado a los datos reales

**Ejemplo:**
```python
# Node espera context['ocr_text'] para extraer importe
# Si ocr_text no existe o está vacío:
# - LLM podría asumir estructura y generar código genérico
# - LLM podría usar valores por defecto (mock data)
# - Código generado no ve el contenido real del PDF
```

**Solución propuesta:**
```python
# En CachedExecutor, antes de generar código:
def _validate_context(self, task: str, context: Dict) -> None:
    """Validate context has required data before generation"""

    # Detectar keys requeridas del task description
    required_keys = self._extract_required_keys(task)

    # Validar que existen en context
    for key in required_keys:
        if key not in context:
            raise ValueError(
                f"Task requires '{key}' in context but it's missing. "
                f"Cannot generate code without required data."
            )

        # Validar que no está vacío (para strings)
        if isinstance(context[key], str) and not context[key]:
            raise ValueError(
                f"Task requires '{key}' but it's empty in context."
            )

def _extract_required_keys(self, task: str) -> List[str]:
    """Extract required context keys from task description"""
    # Regex para encontrar context['key'] en el prompt
    import re
    matches = re.findall(r"context\['(\w+)'\]", task)
    return list(set(matches))
```

**Beneficios:**
- ✅ Fail fast si context incompleto
- ✅ Evita que LLM genere código con mock data
- ✅ Error message claro y accionable
- ✅ Previene retries innecesarios

**Implementación:**
- Fase: Phase 2
- Prioridad: Media
- Esfuerzo: 2-3 horas
- Ubicación: `/nova/src/core/executors.py` (CachedExecutor)

---

## 📊 TRACKING

| Validación | Estado | Prioridad | Fase |
|------------|--------|-----------|------|
| Context validation antes de generación | Pendiente | Media | Phase 2 |

---

**Última actualización**: 6 Noviembre 2025
**Autor**: Mario Ferrer + Claude Code
