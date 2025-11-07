# Workflow de Procesamiento de Facturas

**Fecha creación**: 2025-10-30
**Estado**: Phase 1 - MVP
**Prioridad**: HIGH - Primer workflow de ejemplo

---

## 🎯 Objetivo

Crear un workflow realista que procese facturas recibidas por email, validándolas y aprobándolas/rechazándolas según reglas de negocio.

**Input**: Email con factura adjunta (PDF) - simulado con datos mock
**Output**: Factura validada y aprobada/rechazada + notificaciones enviadas

---

## 🔄 Flujo Completo del Workflow

```
START
  ↓
[1] EXTRACT_INVOICE_DATA (ActionNode)
  │   • Descarga PDF del email (mock)
  │   • Extrae información clave
  │   • Output: invoice_number, supplier, amount, date
  ↓
[2] VALIDATE_INVOICE (ActionNode)
  │   • Valida formato de datos
  │   • Verifica proveedor existe en sistema
  │   • Verifica fecha no es futura
  │   • Output: validation_status (valid/invalid), validation_errors
  ↓
[DECISION 1] ¿Es válida? (DecisionNode)
  │   • Condition: validation_status == "valid"
  │
  ├─ NO → [3] REJECT_INVOICE (ActionNode)
  │         • Marca como rechazada
  │         • Registra razón de rechazo
  │         • Envía email a finanzas (mock)
  │         • Output: rejection_reason, notification_sent
  │         → END
  │
  └─ YES → [DECISION 2] ¿Monto > 1000€? (DecisionNode)
             │   • Condition: amount > 1000
             │
             ├─ YES → [4] MANUAL_APPROVAL_REQUIRED (ActionNode)
             │         • Crea tarea para manager
             │         • Envía notificación a manager (mock)
             │         • Output: approval_task_id, manager_notified
             │         → END
             │
             └─ NO → [5] AUTO_APPROVE (ActionNode)
                       • Marca como aprobada automáticamente
                       • Registra en sistema contable (mock)
                       • Envía confirmación a proveedor (mock)
                       • Output: approved, registered_in_accounting
                       → END
```

---

## 📊 Nodos Detallados

### Nodo 1: EXTRACT_INVOICE_DATA
**Tipo**: ActionNode
**ID**: `extract_invoice_data`

**Input Context**:
```json
{
  "email_data": {
    "from": "proveedor@example.com",
    "subject": "Factura #INV-2024-001",
    "attachment": "factura.pdf",
    "received_date": "2024-10-30"
  }
}
```

**Código Python** (simulado):
```python
# Simular extracción de PDF
# En Phase 2: usar PyPDF2, pdfplumber, pytesseract

context['invoice_number'] = "INV-2024-001"
context['supplier'] = "Acme Corp"
context['amount'] = 850.50
context['invoice_date'] = "2024-10-28"
context['currency'] = "EUR"
context['extracted_at'] = "2024-10-30T10:00:00Z"
```

**Output Context**:
```json
{
  "invoice_number": "INV-2024-001",
  "supplier": "Acme Corp",
  "amount": 850.50,
  "invoice_date": "2024-10-28",
  "currency": "EUR",
  "extracted_at": "2024-10-30T10:00:00Z"
}
```

---

### Nodo 2: VALIDATE_INVOICE
**Tipo**: ActionNode
**ID**: `validate_invoice`

**Input Context**: Output del nodo anterior

**Código Python**:
```python
# Lista de proveedores válidos (mock - en Phase 2 sería DB query)
valid_suppliers = ["Acme Corp", "Tech Solutions", "Office Supplies Ltd"]

# Validaciones
errors = []

# 1. Validar supplier
if context.get('supplier') not in valid_suppliers:
    errors.append(f"Proveedor desconocido: {context.get('supplier')}")

# 2. Validar amount
if not context.get('amount') or context['amount'] <= 0:
    errors.append("Monto inválido o cero")

# 3. Validar fecha no es futura
from datetime import datetime
invoice_date = datetime.fromisoformat(context.get('invoice_date', ''))
if invoice_date > datetime.now():
    errors.append("Fecha de factura es futura")

# 4. Validar invoice_number existe
if not context.get('invoice_number'):
    errors.append("Número de factura faltante")

# Resultado
if errors:
    context['validation_status'] = "invalid"
    context['validation_errors'] = errors
else:
    context['validation_status'] = "valid"
    context['validation_errors'] = []
```

**Output Context**:
```json
{
  "validation_status": "valid",
  "validation_errors": []
}
```

---

### Nodo 3: IS_VALID (Decision)
**Tipo**: DecisionNode
**ID**: `is_valid_decision`

**Condition**:
```python
context.get('validation_status') == 'valid'
```

**Branches**:
- `true` → `amount_threshold_decision`
- `false` → `reject_invoice`

---

### Nodo 4: REJECT_INVOICE
**Tipo**: ActionNode
**ID**: `reject_invoice`

**Código Python**:
```python
# Marcar como rechazada
context['status'] = 'rejected'
context['rejection_reason'] = ', '.join(context.get('validation_errors', []))
context['rejected_at'] = datetime.now().isoformat()

# Simular envío de email a finanzas
context['notification_sent'] = True
context['notification_to'] = 'finanzas@empresa.com'
context['notification_message'] = f"Factura {context.get('invoice_number')} rechazada: {context['rejection_reason']}"
```

**Output Context**:
```json
{
  "status": "rejected",
  "rejection_reason": "Proveedor desconocido: Unknown Corp",
  "rejected_at": "2024-10-30T10:05:00Z",
  "notification_sent": true,
  "notification_to": "finanzas@empresa.com"
}
```

---

### Nodo 5: AMOUNT_THRESHOLD (Decision)
**Tipo**: DecisionNode
**ID**: `amount_threshold_decision`

**Condition**:
```python
context.get('amount', 0) > 1000
```

**Branches**:
- `true` → `manual_approval_required`
- `false` → `auto_approve`

---

### Nodo 6: MANUAL_APPROVAL_REQUIRED
**Tipo**: ActionNode
**ID**: `manual_approval_required`

**Código Python**:
```python
import uuid

# Crear tarea de aprobación
context['status'] = 'pending_approval'
context['approval_task_id'] = str(uuid.uuid4())
context['approval_required_at'] = datetime.now().isoformat()
context['assigned_to'] = 'manager@empresa.com'

# Simular notificación al manager
context['manager_notified'] = True
context['notification_message'] = f"Factura {context.get('invoice_number')} de {context.get('amount')} EUR requiere aprobación manual"
```

**Output Context**:
```json
{
  "status": "pending_approval",
  "approval_task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "approval_required_at": "2024-10-30T10:06:00Z",
  "assigned_to": "manager@empresa.com",
  "manager_notified": true
}
```

---

### Nodo 7: AUTO_APPROVE
**Tipo**: ActionNode
**ID**: `auto_approve`

**Código Python**:
```python
# Aprobar automáticamente
context['status'] = 'approved'
context['approved_at'] = datetime.now().isoformat()
context['approved_by'] = 'system_auto'

# Simular registro en sistema contable
context['registered_in_accounting'] = True
context['accounting_entry_id'] = f"ACC-{context.get('invoice_number')}"

# Simular envío de confirmación
context['confirmation_sent'] = True
context['confirmation_to'] = context.get('supplier', 'unknown')
context['confirmation_message'] = f"Factura {context.get('invoice_number')} aprobada y registrada"
```

**Output Context**:
```json
{
  "status": "approved",
  "approved_at": "2024-10-30T10:06:00Z",
  "approved_by": "system_auto",
  "registered_in_accounting": true,
  "accounting_entry_id": "ACC-INV-2024-001",
  "confirmation_sent": true,
  "confirmation_to": "Acme Corp"
}
```

---

## 🎨 Características del Workflow

### ✅ Elementos de Phase 1 (todos implementados)

1. **ActionNodes**: 5 nodos que ejecutan código Python
2. **DecisionNodes**: 2 decisiones condicionales con branching
3. **Context Management**: Estado compartido entre nodos
4. **Chain of Work**: Auditoría completa de ejecución
5. **E2B Executor**: Ejecución segura en sandbox

### 🔄 Caminos posibles

**Camino 1: Rechazo por validación**
```
START → Extract → Validate → [Invalid] → Reject → END
Resultado: Factura rechazada, finanzas notificadas
```

**Camino 2: Aprobación manual (monto alto)**
```
START → Extract → Validate → [Valid] → [Amount > 1000] → Manual Approval → END
Resultado: Tarea creada para manager
```

**Camino 3: Aprobación automática (monto bajo)**
```
START → Extract → Validate → [Valid] → [Amount ≤ 1000] → Auto Approve → END
Resultado: Factura aprobada y registrada automáticamente
```

---

## 🧪 Casos de Prueba

### Test 1: Factura válida de monto bajo (auto-aprobación)
```json
{
  "email_data": {
    "from": "acme@example.com",
    "subject": "Factura #INV-2024-001",
    "attachment": "factura.pdf"
  }
}
```
**Expected Path**: Extract → Validate → IsValid(true) → AmountThreshold(false) → AutoApprove → END
**Expected Result**: `status: "approved"`, `approved_by: "system_auto"`

---

### Test 2: Factura válida de monto alto (aprobación manual)
```json
{
  "email_data": {
    "from": "techsolutions@example.com",
    "subject": "Factura #INV-2024-002",
    "attachment": "factura_2500.pdf"
  }
}
```
**Mock amount**: 2500.00 EUR
**Expected Path**: Extract → Validate → IsValid(true) → AmountThreshold(true) → ManualApproval → END
**Expected Result**: `status: "pending_approval"`, `approval_task_id` exists

---

### Test 3: Factura con proveedor desconocido (rechazo)
```json
{
  "email_data": {
    "from": "unknown@example.com",
    "subject": "Factura #INV-2024-003",
    "attachment": "factura_invalid.pdf"
  }
}
```
**Mock supplier**: "Unknown Corp"
**Expected Path**: Extract → Validate → IsValid(false) → Reject → END
**Expected Result**: `status: "rejected"`, `rejection_reason` contains "Proveedor desconocido"

---

### Test 4: Factura con monto cero (rechazo)
```json
{
  "email_data": {
    "from": "acme@example.com",
    "subject": "Factura #INV-2024-004"
  }
}
```
**Mock amount**: 0.00 EUR
**Expected Path**: Extract → Validate → IsValid(false) → Reject → END
**Expected Result**: `status: "rejected"`, `rejection_reason` contains "Monto inválido"

---

## 📈 Chain of Work - Ejemplo

Para el **Test 1** (auto-aprobación), el Chain of Work registrará:

```json
[
  {
    "node_id": "extract_invoice_data",
    "node_type": "ActionNode",
    "code_executed": "# Simular extracción de PDF\ncontext['invoice_number'] = ...",
    "input_context": {"email_data": {...}},
    "output_context": {"invoice_number": "INV-2024-001", "amount": 850.50, ...},
    "execution_time": "2024-10-30T10:00:00Z",
    "duration_ms": 150,
    "status": "success"
  },
  {
    "node_id": "validate_invoice",
    "node_type": "ActionNode",
    "code_executed": "valid_suppliers = [...]\nerrors = []\n...",
    "input_context": {"invoice_number": "INV-2024-001", ...},
    "output_context": {"validation_status": "valid", "validation_errors": []},
    "execution_time": "2024-10-30T10:00:01Z",
    "duration_ms": 80,
    "status": "success"
  },
  {
    "node_id": "is_valid_decision",
    "node_type": "DecisionNode",
    "condition": "context.get('validation_status') == 'valid'",
    "condition_result": true,
    "next_node": "amount_threshold_decision",
    "execution_time": "2024-10-30T10:00:02Z",
    "duration_ms": 5
  },
  {
    "node_id": "amount_threshold_decision",
    "node_type": "DecisionNode",
    "condition": "context.get('amount', 0) > 1000",
    "condition_result": false,
    "next_node": "auto_approve",
    "execution_time": "2024-10-30T10:00:02Z",
    "duration_ms": 5
  },
  {
    "node_id": "auto_approve",
    "node_type": "ActionNode",
    "code_executed": "context['status'] = 'approved'\n...",
    "input_context": {"amount": 850.50, ...},
    "output_context": {"status": "approved", "approved_by": "system_auto", ...},
    "execution_time": "2024-10-30T10:00:03Z",
    "duration_ms": 120,
    "status": "success"
  }
]
```

**Resultado**: Auditoría completa de qué se ejecutó, qué decisiones se tomaron, y por qué.

---

## 🚀 Extensiones Futuras (Phase 2+)

### OCR Real
```python
# En extract_invoice_data
import pytesseract
from pdf2image import convert_from_bytes
import pdfplumber

# Extraer texto de PDF
with pdfplumber.open(pdf_bytes) as pdf:
    text = pdf.pages[0].extract_text()

# OCR para PDFs escaneados
images = convert_from_bytes(pdf_bytes)
ocr_text = pytesseract.image_to_string(images[0], lang='spa+eng')
```

### Email Real (IMAP)
```python
import imaplib
import email

# Conectar a IMAP
mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(user, password)
mail.select('inbox')

# Buscar emails con facturas
status, messages = mail.search(None, 'SUBJECT "Factura"')

# Descargar adjuntos
for msg_id in messages[0].split():
    _, msg_data = mail.fetch(msg_id, '(RFC822)')
    # Extraer PDF attachment
```

### Base de Datos de Proveedores
```python
# En validate_invoice
import psycopg2

# Query real a PostgreSQL
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()
cursor.execute("SELECT id FROM suppliers WHERE name = %s", (supplier,))
supplier_exists = cursor.fetchone() is not None
```

### Integración Contable
```python
# En auto_approve
import requests

# API de sistema contable (ej. Xero, QuickBooks)
response = requests.post(
    "https://api.xero.com/api.xro/2.0/Invoices",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "Type": "ACCPAY",
        "Contact": {"Name": supplier},
        "LineItems": [{"Description": invoice_number, "Amount": amount}]
    }
)
```

### Machine Learning (Phase 3)
```python
# Clasificación inteligente de facturas
from sklearn.ensemble import RandomForestClassifier

# Entrenar con facturas históricas
model.fit(X_train, y_train)

# Predecir categoría de gasto
category = model.predict([invoice_features])
context['expense_category'] = category
```

---

## 📋 Implementación - Checklist

- [ ] Crear JSON del workflow en `/nova/fixtures/invoice_processing_workflow.json`
- [ ] Implementar código Python para cada nodo
- [ ] Crear script de prueba `examples/run_invoice_workflow.py`
- [ ] Ejecutar los 4 casos de prueba
- [ ] Verificar Chain of Work se registra correctamente
- [ ] Validar que todos los caminos funcionan
- [ ] Documentar resultados y tiempos de ejecución

---

## 💡 Aprendizajes Clave

Este workflow demuestra:

1. **Branching condicional**: Decisiones basadas en datos extraídos
2. **Validación de negocio**: Reglas empresariales aplicadas
3. **Múltiples caminos**: 3 resultados posibles según input
4. **Auditoría completa**: Chain of Work registra todo
5. **Extensibilidad**: Fácil agregar integraciones reales en Phase 2

---

**Última actualización**: 2025-10-30
**Estado**: Diseñado, pendiente de implementación
**Próximo paso**: Crear JSON del workflow
