# AWS Secrets Manager - Phase 2+

## 🎯 **Por Qué Migrar a AWS Secrets Manager**

Cuando NOVA escale a producción con múltiples clientes, considera migrar de PostgreSQL a AWS Secrets Manager para gestión de credenciales.

---

## ✅ **Ventajas sobre PostgreSQL**

### **Seguridad**
- ✅ **Encriptación automática** con AWS KMS
- ✅ **Rotación automática** de passwords
- ✅ **Auditoría completa** en CloudTrail (quién accedió a qué secret)
- ✅ **Permisos granulares** con IAM policies
- ✅ **No guardas secrets en tu BD** (separation of concerns)

### **Operacional**
- ✅ **Zero maintenance**: AWS gestiona todo
- ✅ **Alta disponibilidad**: multi-AZ automático
- ✅ **Integración nativa** con otros servicios AWS
- ✅ **Versionado**: historial de cambios de secrets

### **Compliance**
- ✅ **SOC 2, ISO 27001, HIPAA** compliant
- ✅ **GDPR-ready**: encriptación at-rest y in-transit
- ✅ **Auditoría**: logs de acceso completos

---

## 💰 **Costos**

- **$0.40** por secret por mes
- **$0.05** por 10,000 API calls
- **Ejemplo**: 10 clientes = ~$5-8/mes

**Comparado con:**
- PostgreSQL separada en Railway: ~$7/mes
- HashiCorp Vault self-hosted: ~$50-150/mes

---

## 🏗️ **Arquitectura Propuesta**

### **Current (Phase 1):**
```
NOVA → PostgreSQL → Credenciales en tablas
```

### **Future (Phase 2+):**
```
NOVA → AWS Secrets Manager → Credenciales encriptadas
```

---

## 📝 **Estructura de Secrets**

### **Opción A: Un secret por cliente (simple)**
```json
// Secret name: "nova/clients/idom"
{
  "client_name": "IDOM",
  "database": {
    "host": "shortline.proxy.rlwy.net",
    "port": 49057,
    "name": "railway",
    "user": "postgres",
    "password": "YMrLct..."
  },
  "email": {
    "user": "facturas@idom.com",
    "app_password": "xxxx-xxxx-xxxx-xxxx",
    "sender_whitelist": "proveedor@empresa.com"
  }
}
```

### **Opción B: Secrets separados por servicio (granular)**
```
nova/clients/idom/database
nova/clients/idom/email
nova/clients/idom/aws
```

---

## 🔧 **Código de Migración**

### **Configuración AWS SDK**
```python
# requirements.txt
boto3>=1.28.0
```

### **Helper Functions**
```python
# src/services/secrets_manager.py
import json
import boto3
from botocore.exceptions import ClientError

class SecretsManager:
    def __init__(self, region_name='us-east-1'):
        self.client = boto3.client('secretsmanager', region_name=region_name)

    def get_client_credentials(self, client_slug: str):
        """
        Get all credentials for a client from AWS Secrets Manager.

        Args:
            client_slug: Client identifier (e.g., "idom")

        Returns:
            Dict with database, email, and other credentials

        Raises:
            ClientError: If secret not found
        """
        secret_name = f"nova/clients/{client_slug}"

        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            secret = json.loads(response['SecretString'])
            return secret

        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                raise ValueError(f"Client '{client_slug}' not found in Secrets Manager")
            raise

    def get_database_credentials(self, client_slug: str):
        """Get only database credentials"""
        creds = self.get_client_credentials(client_slug)
        return creds['database']

    def get_email_credentials(self, client_slug: str):
        """Get only email credentials"""
        creds = self.get_client_credentials(client_slug)
        return creds['email']

    def create_client_credentials(self, client_slug: str, credentials: dict):
        """Create new secret for a client"""
        secret_name = f"nova/clients/{client_slug}"

        self.client.create_secret(
            Name=secret_name,
            Description=f"NOVA credentials for client {client_slug}",
            SecretString=json.dumps(credentials)
        )

    def update_client_credentials(self, client_slug: str, credentials: dict):
        """Update existing secret"""
        secret_name = f"nova/clients/{client_slug}"

        self.client.update_secret(
            SecretId=secret_name,
            SecretString=json.dumps(credentials)
        )

    def rotate_password(self, client_slug: str, service: str, new_password: str):
        """Rotate a specific password"""
        creds = self.get_client_credentials(client_slug)

        if service == 'database':
            creds['database']['password'] = new_password
        elif service == 'email':
            creds['email']['app_password'] = new_password

        self.update_client_credentials(client_slug, creds)
```

### **Uso en Workflows**
```python
# En ActionNode del workflow
from src.services.secrets_manager import SecretsManager

secrets = SecretsManager()

# Get database credentials
db_creds = secrets.get_database_credentials(context["client_slug"])
conn = psycopg2.connect(
    host=db_creds['host'],
    port=db_creds['port'],
    database=db_creds['name'],
    user=db_creds['user'],
    password=db_creds['password']
)

# Get email credentials
email_creds = secrets.get_email_credentials(context["client_slug"])
mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(email_creds['user'], email_creds['app_password'])
```

---

## 🔄 **Plan de Migración (Phase 1 → Phase 2)**

### **Paso 1: Dual Write (transición)**
```python
# Escribir en ambos lados durante transición
def save_credentials(client_slug, creds):
    # Write to PostgreSQL (old)
    db.save_to_client_credentials_table(client_slug, creds)

    # Write to AWS Secrets Manager (new)
    secrets.create_client_credentials(client_slug, creds)
```

### **Paso 2: Dual Read (validación)**
```python
# Leer de ambos lados y comparar
def get_credentials(client_slug):
    pg_creds = db.get_from_postgres(client_slug)
    aws_creds = secrets.get_from_aws(client_slug)

    # Log if different
    if pg_creds != aws_creds:
        logger.warning("Credentials mismatch!")

    return aws_creds  # Prefer AWS
```

### **Paso 3: Full Migration**
```python
# Migrar todos los clientes
def migrate_all_clients():
    clients = db.query("SELECT * FROM clients")

    for client in clients:
        db_creds = db.get_database_credentials(client.slug)
        email_creds = db.get_email_credentials(client.slug)

        # Create in AWS
        secrets.create_client_credentials(client.slug, {
            'database': db_creds,
            'email': email_creds
        })

        print(f"✅ Migrated {client.slug}")
```

### **Paso 4: Switch Over**
```python
# Update all helper functions to use AWS
# Remove PostgreSQL credential tables (keep clients table)
```

---

## 🔐 **IAM Policy Example**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:nova/clients/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:CreateSecret",
        "secretsmanager:UpdateSecret"
      ],
      "Resource": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:nova/clients/*",
      "Condition": {
        "StringEquals": {
          "secretsmanager:ResourceTag/Project": "NOVA"
        }
      }
    }
  ]
}
```

---

## 📊 **Decisión: ¿Cuándo Migrar?**

### **Mantén PostgreSQL si:**
- ✅ Tienes < 20 clientes
- ✅ Costo es prioridad ($0 vs $5-10/mes)
- ✅ No necesitas compliance estricto

### **Migra a AWS Secrets Manager si:**
- ✅ Tienes > 20 clientes
- ✅ Necesitas compliance (SOC 2, HIPAA)
- ✅ Quieres rotación automática de passwords
- ✅ Quieres separar credenciales de tu BD principal

---

## 🎯 **Timeline Recomendado**

- **Phase 1 (MVP)**: PostgreSQL (estamos aquí)
- **Phase 2 (5-10 clientes)**: Dual write (PostgreSQL + AWS)
- **Phase 3 (10-20 clientes)**: Migración completa a AWS
- **Phase 4 (20+ clientes)**: Solo AWS Secrets Manager

---

## 📚 **Referencias**

- AWS Secrets Manager Docs: https://docs.aws.amazon.com/secretsmanager/
- Boto3 Secrets Manager: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html
- Best Practices: https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html

---

**Última actualización**: 30 octubre 2025
**Estado**: Documentado para futuro (Phase 2+)
