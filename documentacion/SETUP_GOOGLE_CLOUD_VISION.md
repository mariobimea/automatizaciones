# Guía: Configurar Google Cloud Vision API

**Tiempo estimado**: 15-20 minutos
**Costo**: $0 (incluye $300 de créditos gratis para nuevas cuentas)

---

## Paso 1: Crear Proyecto en Google Cloud Console

### 1.1 Acceder a Google Cloud Console

1. Ve a **https://console.cloud.google.com**
2. Inicia sesión con tu cuenta de Google (Gmail)

### 1.2 Crear Nuevo Proyecto

1. Haz clic en el **selector de proyecto** (arriba a la izquierda, junto a "Google Cloud")
2. Clic en **"NEW PROJECT"** (esquina superior derecha)
3. Configurar proyecto:
   - **Project name**: `nova-ocr` (o el nombre que prefieras)
   - **Organization**: Dejar en blanco (No organization)
   - **Location**: Dejar en blanco
4. Clic en **"CREATE"**

**Espera 10-20 segundos** mientras se crea el proyecto.

### 1.3 Verificar que estás en el proyecto correcto

- En la barra superior, verifica que dice **"nova-ocr"** (o el nombre que elegiste)
- Si no, usa el selector de proyecto para cambiarlo

---

## Paso 2: Habilitar Billing (Facturación)

Google Cloud requiere billing configurado (aunque no te cobrarán con los créditos gratis).

### 2.1 Configurar Billing Account

1. Ve a **Menu (☰)** → **Billing** → **"LINK A BILLING ACCOUNT"**
2. Si **NO tienes Billing Account**:
   - Clic en **"CREATE BILLING ACCOUNT"**
   - País: España
   - Tipo: Individual
   - Agregar tarjeta de crédito (NO te cobrarán, solo para verificación)
   - Aceptar términos y continuar
3. Si **YA tienes Billing Account**: Selecciónala de la lista

**Nota**: Google da **$300 USD gratis** por 90 días para nuevas cuentas. Vision API cuesta $1.50/1000 páginas, así que $300 = 200,000 páginas gratis.

---

## Paso 3: Habilitar Cloud Vision API

### 3.1 Activar la API

1. Ve a **Menu (☰)** → **APIs & Services** → **"Library"**
2. En el buscador, escribe: **"Cloud Vision API"**
3. Haz clic en **"Cloud Vision API"**
4. Clic en botón **"ENABLE"** (azul)

**Espera 10-20 segundos** mientras se habilita la API.

### 3.2 Verificar que está habilitada

- Deberías ver un mensaje: "API enabled"
- Arriba dice: **"Cloud Vision API"** con un check verde

---

## Paso 4: Crear Service Account (Cuenta de Servicio)

Este es el paso más importante - crea las credenciales para que NOVA pueda usar Vision API.

### 4.1 Ir a Service Accounts

1. Ve a **Menu (☰)** → **IAM & Admin** → **"Service Accounts"**
2. Clic en **"+ CREATE SERVICE ACCOUNT"** (arriba)

### 4.2 Configurar Service Account (Paso 1/3)

**Service account details**:
- **Service account name**: `nova-vision-api`
- **Service account ID**: Se auto-genera como `nova-vision-api@tu-proyecto.iam.gserviceaccount.com`
- **Description**: `Service account for NOVA workflow engine to use Cloud Vision API`

Clic en **"CREATE AND CONTINUE"**

### 4.3 Asignar Rol (Paso 2/3)

**Grant this service account access to project**:
1. En **"Select a role"**, busca: **"Cloud Vision"**
2. Selecciona: **"Cloud Vision API User"**
   - O alternativamente: **"Cloud Vision API Admin"** (si quieres más permisos)
3. Clic en **"CONTINUE"**

### 4.4 Saltar paso 3/3

**Grant users access to this service account** (opcional):
- Dejar vacío
- Clic en **"DONE"**

---

## Paso 5: Crear y Descargar JSON Key

### 5.1 Generar JSON Key

1. En la lista de **Service Accounts**, busca `nova-vision-api@...`
2. Haz clic en el **email** de la service account (link azul)
3. Ve a la pestaña **"KEYS"** (arriba)
4. Clic en **"ADD KEY"** → **"Create new key"**
5. Selecciona formato: **JSON** (recomendado)
6. Clic en **"CREATE"**

**Se descargará automáticamente un archivo JSON** como:
```
nova-ocr-a1b2c3d4e5f6.json
```

⚠️ **MUY IMPORTANTE**: Este archivo contiene credenciales secretas. NO lo subas a Git ni lo compartas.

### 5.2 Guardar el JSON en lugar seguro

```bash
# Mover a una carpeta segura (NO dentro del repo)
mv ~/Downloads/nova-ocr-*.json ~/credentials/gcp-vision-key.json

# O mejor aún, guardarlo en un gestor de contraseñas
```

---

## Paso 6: Configurar Credenciales en Railway

Ahora vamos a configurar las credenciales en Railway para que NOVA pueda usarlas.

### 6.1 Leer el contenido del JSON

```bash
# Abrir el archivo JSON y copiar TODO el contenido
cat ~/credentials/gcp-vision-key.json
```

**El JSON se verá así**:
```json
{
  "type": "service_account",
  "project_id": "nova-ocr",
  "private_key_id": "a1b2c3d4e5f6...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBg...\n-----END PRIVATE KEY-----\n",
  "client_email": "nova-vision-api@nova-ocr.iam.gserviceaccount.com",
  "client_id": "123456789012345678901",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

**Copia TODO el contenido** (desde `{` hasta `}`)

### 6.2 Agregar Variable de Entorno en Railway

1. Ve a **https://railway.app**
2. Selecciona tu proyecto **NOVA**
3. Selecciona el servicio **web** (FastAPI)
4. Ve a la pestaña **"Variables"**
5. Clic en **"+ New Variable"**
6. Configurar:
   - **Name**: `GCP_SERVICE_ACCOUNT_JSON`
   - **Value**: Pega TODO el contenido del JSON (asegúrate de copiar completo)
7. Clic en **"Add"**

**⚠️ IMPORTANTE**: Railway guardará el JSON como string. El código de NOVA lo parseará con `json.loads()`.

### 6.3 Verificar que se guardó correctamente

1. En Railway, la variable debería verse como:
   ```
   GCP_SERVICE_ACCOUNT_JSON = {"type":"service_account",...}
   ```
2. **NO** debería tener saltos de línea visibles (Railway los maneja internamente)

---

## Paso 7: Verificar la Configuración (Opcional)

### 7.1 Test local (en tu Mac)

Puedes probar las credenciales localmente antes de deployar:

```bash
# 1. Instalar google-cloud-vision
pip install google-cloud-vision

# 2. Exportar credenciales
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/credentials/gcp-vision-key.json"

# 3. Test rápido
python -c "
from google.cloud import vision

client = vision.ImageAnnotatorClient()
print('✅ Autenticación exitosa!')
print(f'Client: {client}')
"
```

**Si funciona**, deberías ver:
```
✅ Autenticación exitosa!
Client: <google.cloud.vision_v1.services.image_annotator.ImageAnnotatorClient object at 0x...>
```

### 7.2 Test con imagen de ejemplo

```python
# test_vision_api.py
from google.cloud import vision
import os

# Autenticar
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.expanduser('~/credentials/gcp-vision-key.json')

client = vision.ImageAnnotatorClient()

# Crear imagen de prueba con texto
from PIL import Image, ImageDraw, ImageFont
import io

# Crear imagen simple con texto
img = Image.new('RGB', (400, 100), color='white')
draw = ImageDraw.Draw(img)
draw.text((10, 30), "FACTURA 2024-001", fill='black')

# Convertir a bytes
img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='PNG')
img_bytes = img_byte_arr.getvalue()

# OCR con Vision API
image = vision.Image(content=img_bytes)
response = client.text_detection(image=image)

# Mostrar resultado
if response.text_annotations:
    text = response.text_annotations[0].description
    print(f"✅ OCR funcionó!")
    print(f"Texto detectado: {text}")
else:
    print("⚠️ No se detectó texto")

# Verificar errores
if response.error.message:
    print(f"❌ Error: {response.error.message}")
```

Ejecutar:
```bash
python test_vision_api.py
```

**Resultado esperado**:
```
✅ OCR funcionó!
Texto detectado: FACTURA 2024-001
```

---

## Paso 8: Monitorear Uso y Costos

### 8.1 Ver Uso de API

1. Ve a **Google Cloud Console** → **APIs & Services** → **"Dashboard"**
2. Selecciona **"Cloud Vision API"**
3. Verás gráficas de:
   - Requests per day
   - Errors
   - Latency

### 8.2 Ver Costos

1. Ve a **Menu (☰)** → **Billing** → **"Reports"**
2. Filtra por:
   - **Service**: Cloud Vision API
   - **Date range**: Last 30 days

**Costo estimado** (para referencia):
```
- Primeras 1,000 unidades/mes: GRATIS
- 1,001 - 5,000,000 unidades: $1.50 por 1,000
- 5,000,001+: $0.60 por 1,000

Ejemplos:
- 100 facturas/día × 30 días = 3,000 facturas/mes
  Costo: (3,000 - 1,000) × $1.50 / 1,000 = $3.00/mes

- 500 facturas/día × 30 días = 15,000 facturas/mes
  Costo: (15,000 - 1,000) × $1.50 / 1,000 = $21.00/mes
```

### 8.3 Configurar Alertas de Presupuesto (Recomendado)

1. Ve a **Menu (☰)** → **Billing** → **"Budgets & alerts"**
2. Clic en **"CREATE BUDGET"**
3. Configurar:
   - **Name**: Vision API Budget
   - **Projects**: nova-ocr
   - **Services**: Cloud Vision API
   - **Budget amount**: $20/mes (o lo que consideres apropiado)
4. Agregar alertas:
   - 50% del presupuesto ($10)
   - 90% del presupuesto ($18)
   - 100% del presupuesto ($20)
5. **Email alerts**: Agregar tu email
6. Clic en **"FINISH"**

**Recibirás emails** cuando el gasto alcance estos umbrales.

---

## Paso 9: Probar en NOVA (E2B Sandbox)

Una vez configurado Railway, el código generado por NOVA se verá así:

```python
# Código que el LLM generará automáticamente
import os
import json
from google.cloud import vision
from google.oauth2 import service_account

# Leer credenciales de variable de entorno
creds_json = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')

if creds_json:
    # Parsear JSON y crear credentials
    creds_dict = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    client = vision.ImageAnnotatorClient(credentials=credentials)
else:
    # Fallback a default credentials (desarrollo local)
    client = vision.ImageAnnotatorClient()

# Usar Vision API para OCR
import fitz  # PyMuPDF

doc = fitz.open(pdf_path)
page = doc[0]
pix = page.get_pixmap(dpi=300)
img_bytes = pix.tobytes("png")
doc.close()

# OCR
image = vision.Image(content=img_bytes)
response = client.document_text_detection(image=image)

if response.error.message:
    raise Exception(f"Vision API Error: {response.error.message}")

# Extraer texto
text = response.full_text_annotation.text
context['extracted_text'] = text
```

---

## Troubleshooting

### Error: "Could not find default credentials"

**Problema**: Variable de entorno no configurada o mal formateada

**Solución**:
1. Verificar que `GCP_SERVICE_ACCOUNT_JSON` existe en Railway
2. Verificar que el JSON está completo (desde `{` hasta `}`)
3. Verificar que NO tiene espacios extra al inicio/final

### Error: "403 Permission Denied"

**Problema**: Service account no tiene permisos

**Solución**:
1. Ve a **IAM & Admin** → **Service Accounts**
2. Verifica que `nova-vision-api` tiene rol **"Cloud Vision API User"**
3. Si no, edítala y agrega el rol

### Error: "API not enabled"

**Problema**: Vision API no está habilitada

**Solución**:
1. Ve a **APIs & Services** → **Library**
2. Busca "Cloud Vision API"
3. Clic en **"ENABLE"**

### Error: "Billing not enabled"

**Problema**: Proyecto no tiene billing configurado

**Solución**:
1. Ve a **Billing** → **"LINK A BILLING ACCOUNT"**
2. Selecciona o crea billing account
3. Agrega tarjeta de crédito (no te cobrarán con créditos gratis)

---

## Checklist Final

Antes de probar en NOVA, verifica:

- [  ] ✅ Proyecto creado en Google Cloud Console
- [  ] ✅ Billing habilitado (aunque sea con $300 gratis)
- [  ] ✅ Cloud Vision API habilitada
- [  ] ✅ Service Account creada con rol "Cloud Vision API User"
- [  ] ✅ JSON Key descargado y guardado de forma segura
- [  ] ✅ Variable `GCP_SERVICE_ACCOUNT_JSON` configurada en Railway
- [  ] ✅ (Opcional) Test local funcionando
- [  ] ✅ (Opcional) Alertas de presupuesto configuradas

---

## Próximos Pasos

Una vez completada la configuración:

1. **Build template E2B V3**:
   ```bash
   e2b template build --dockerfile e2b-v3-vision.Dockerfile --name "nova-engine-v3"
   ```

2. **Probar con workflow de facturas**:
   - Usar workflow existente
   - Cambiar `template_id` a `nova-engine-v3`
   - Verificar que funciona

3. **Comparar resultados**:
   - Precisión OCR
   - Tiempo de ejecución
   - Código generado por LLM

---

## Referencias

- **Google Cloud Console**: https://console.cloud.google.com
- **Vision API Docs**: https://cloud.google.com/vision/docs
- **Pricing**: https://cloud.google.com/vision/pricing
- **Service Account Setup**: https://cloud.google.com/iam/docs/service-accounts-create

---

**Última actualización**: 2025-01-17
**Autor**: Plan de migración NOVA
**Status**: Lista para usar
