# Marito: Tool Documentation System

## Concepto

Marito necesita **documentación clara** sobre cómo hacer cada cosa (leer email, extraer PDF, conectar a DB, etc.).

Esta documentación se usa como **contexto en los prompts** para que GPT-4 genere código correcto.

---

## Estructura del Tool Catalog

```
/marito/tools/
    ├── email/
    │   ├── outlook_imap.md
    │   ├── gmail_imap.md
    │   └── send_email_smtp.md
    │
    ├── pdf/
    │   ├── extract_text_pdf.md
    │   ├── extract_with_ocr.md
    │   └── generate_pdf.md
    │
    ├── database/
    │   ├── postgresql.md
    │   ├── mysql.md
    │   └── sqlite.md
    │
    ├── files/
    │   ├── read_excel.md
    │   ├── write_csv.md
    │   └── manipulate_json.md
    │
    └── http/
        ├── make_request.md
        └── parse_html.md
```

---

## Ejemplo: outlook_imap.md

```markdown
# Tool: Read Emails from Outlook via IMAP

## Description
Connect to Outlook/Office365 via IMAP protocol and fetch emails based on criteria.

## Required Credentials
- `outlook_email`: Email address (string)
- `outlook_password`: Password or app-specific password (string)

## Python Implementation

### Libraries Required
```python
import imaplib
import email
from email.header import decode_header
import os
```

### Code Template

```python
def read_outlook_emails(
    email_address: str,
    password: str,
    mailbox: str = "INBOX",
    search_criteria: str = "UNSEEN",
    max_emails: int = 50
) -> list:
    """
    Connect to Outlook via IMAP and fetch emails

    Args:
        email_address: Outlook email address
        password: Outlook password or app-specific password
        mailbox: Mailbox to read from (default: INBOX)
        search_criteria: IMAP search criteria (default: UNSEEN for unread)
        max_emails: Maximum number of emails to fetch

    Returns:
        List of email dictionaries with structure:
        {
            "id": str,
            "from": str,
            "to": str,
            "subject": str,
            "date": str,
            "body": str,
            "attachments": [
                {
                    "filename": str,
                    "content_type": str,
                    "data": bytes
                }
            ]
        }
    """

    # IMAP settings for Outlook/Office365
    IMAP_SERVER = "outlook.office365.com"
    IMAP_PORT = 993

    emails = []

    try:
        # Connect to IMAP server
        print("Connecting to Outlook IMAP server...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)

        # Login
        print("Logging in...")
        mail.login(email_address, password)

        # Select mailbox
        mail.select(mailbox)

        # Search emails
        print(f"Searching for emails: {search_criteria}")
        status, messages = mail.search(None, search_criteria)

        if status != "OK":
            raise Exception(f"Search failed: {status}")

        # Get email IDs
        email_ids = messages[0].split()

        # Limit to max_emails
        email_ids = email_ids[-max_emails:]

        print(f"Found {len(email_ids)} emails")

        # Fetch each email
        for email_id in email_ids:
            status, msg_data = mail.fetch(email_id, "(RFC822)")

            if status != "OK":
                print(f"Failed to fetch email {email_id}")
                continue

            # Parse email
            msg = email.message_from_bytes(msg_data[0][1])

            # Extract headers
            subject = decode_header(msg["Subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()

            from_ = msg.get("From")
            to_ = msg.get("To")
            date_ = msg.get("Date")

            # Extract body
            body = ""
            attachments = []

            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    # Get email body
                    if "attachment" not in content_disposition:
                        if content_type == "text/plain":
                            body = part.get_payload(decode=True).decode()

                    # Get attachments
                    else:
                        filename = part.get_filename()
                        if filename:
                            attachments.append({
                                "filename": filename,
                                "content_type": content_type,
                                "data": part.get_payload(decode=True)
                            })
            else:
                body = msg.get_payload(decode=True).decode()

            emails.append({
                "id": email_id.decode(),
                "from": from_,
                "to": to_,
                "subject": subject,
                "date": date_,
                "body": body,
                "attachments": attachments
            })

        # Logout
        mail.logout()

        print(f"Successfully fetched {len(emails)} emails")
        return emails

    except Exception as e:
        print(f"Error reading Outlook emails: {e}")
        raise

# Example usage
if __name__ == "__main__":
    emails = read_outlook_emails(
        email_address="your-email@outlook.com",
        password="your-password",
        search_criteria="UNSEEN",  # Only unread emails
        max_emails=10
    )

    for email in emails:
        print(f"Subject: {email['subject']}")
        print(f"From: {email['from']}")
        print(f"Attachments: {len(email['attachments'])}")
```

## Common Search Criteria

```python
# Unread emails
search_criteria = "UNSEEN"

# Emails from specific sender
search_criteria = 'FROM "sender@example.com"'

# Emails with specific subject
search_criteria = 'SUBJECT "Invoice"'

# Emails since specific date
search_criteria = '(SINCE "01-Jan-2025")'

# Emails with attachments (complex)
search_criteria = 'HEADER Content-Type "application/pdf"'

# Combine multiple criteria
search_criteria = '(UNSEEN FROM "sender@example.com")'
```

## Error Handling

Common errors and solutions:

1. **Authentication Error**: Use app-specific password if 2FA enabled
2. **Timeout**: Increase socket timeout with `socket.setdefaulttimeout(60)`
3. **Connection Error**: Check firewall allows port 993

## Security Notes

- Never hardcode credentials
- Use environment variables or secure credential store
- For production, use OAuth2 instead of password authentication

## Example Prompt for GPT-4

When Marito needs to read Outlook emails, it includes this documentation in the prompt:

```
You need to generate Python code to read emails from Outlook.

TOOL DOCUMENTATION:
[Include full content of outlook_imap.md here]

TASK SPECIFIC REQUIREMENTS:
- Read unread emails from last 24 hours
- Filter emails with PDF attachments only
- Return list of emails with attachment data

Generate production-ready Python code using the template above.
Adapt it to the specific requirements.
```

## Testing

To test this tool documentation:

```bash
# Install dependencies
pip install email imaplib

# Run test
python test_outlook_imap.py
```

Expected output:
```
Connecting to Outlook IMAP server...
Logging in...
Searching for emails: UNSEEN
Found 5 emails
Successfully fetched 5 emails
```
```

---

## Ejemplo: extract_text_pdf.md

```markdown
# Tool: Extract Text from PDF

## Description
Extract text from PDF files. Handles both text-based PDFs and scanned PDFs (with OCR).

## Required Libraries
```python
import pypdf
import io
from pdf2image import convert_from_bytes
import pytesseract
```

## Installation
```bash
pip install pypdf pdf2image pytesseract
# For OCR support:
apt-get install tesseract-ocr tesseract-ocr-spa  # Linux
brew install tesseract tesseract-lang  # macOS
```

## Code Template

```python
def extract_pdf_text(pdf_bytes: bytes, use_ocr_fallback: bool = True) -> dict:
    """
    Extract text from PDF (handles both text and scanned PDFs)

    Args:
        pdf_bytes: PDF file content as bytes
        use_ocr_fallback: If True, use OCR when text extraction fails

    Returns:
        {
            "text": str,
            "method": "text" | "ocr",
            "pages": int,
            "success": bool
        }
    """

    result = {
        "text": "",
        "method": None,
        "pages": 0,
        "success": False
    }

    try:
        # STEP 1: Try extracting text directly
        print("Attempting text extraction...")
        pdf_reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))

        result["pages"] = len(pdf_reader.pages)

        text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            text += page_text
            print(f"Page {page_num + 1}: {len(page_text)} characters")

        # Check if we got meaningful text
        if text.strip() and len(text.strip()) > 50:
            result["text"] = text
            result["method"] = "text"
            result["success"] = True
            print(f"✓ Text extraction successful: {len(text)} characters")
            return result

        # STEP 2: Fallback to OCR if text extraction failed
        if use_ocr_fallback:
            print("Text extraction insufficient. Trying OCR...")

            # Convert PDF to images
            images = convert_from_bytes(pdf_bytes, dpi=300)

            ocr_text = ""
            for i, image in enumerate(images):
                print(f"OCR processing page {i + 1}/{len(images)}...")
                page_text = pytesseract.image_to_string(image, lang='spa+eng')
                ocr_text += page_text + "\n"

            if ocr_text.strip():
                result["text"] = ocr_text
                result["method"] = "ocr"
                result["success"] = True
                print(f"✓ OCR successful: {len(ocr_text)} characters")
                return result

        # If we reach here, both methods failed
        result["success"] = False
        print("✗ Both text extraction and OCR failed")
        return result

    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        result["success"] = False
        return result

# Example usage
if __name__ == "__main__":
    with open("invoice.pdf", "rb") as f:
        pdf_bytes = f.read()

    result = extract_pdf_text(pdf_bytes)

    if result["success"]:
        print(f"Extraction method: {result['method']}")
        print(f"Pages: {result['pages']}")
        print(f"Text preview: {result['text'][:200]}...")
    else:
        print("Failed to extract text from PDF")
```

## Advanced: Extract Structured Data

```python
import re

def extract_invoice_data(pdf_text: str) -> dict:
    """
    Parse invoice-specific fields from extracted text
    """

    data = {}

    # NIF/CIF (Spanish tax ID)
    nif_pattern = r'\b[A-Z]\d{8}\b|\b\d{8}[A-Z]\b'
    nif_match = re.search(nif_pattern, pdf_text)
    data["nif"] = nif_match.group(0) if nif_match else None

    # Invoice number
    inv_patterns = [
        r'(?:Factura|Invoice|Nº)\s*:?\s*([A-Z0-9\-/]+)',
        r'Nº\s*Factura\s*:?\s*([A-Z0-9\-/]+)'
    ]
    for pattern in inv_patterns:
        match = re.search(pattern, pdf_text, re.IGNORECASE)
        if match:
            data["invoice_number"] = match.group(1)
            break

    # Date (DD/MM/YYYY or DD-MM-YYYY)
    date_pattern = r'\b(\d{2}[/-]\d{2}[/-]\d{4})\b'
    date_match = re.search(date_pattern, pdf_text)
    data["date"] = date_match.group(1) if date_match else None

    # Amounts (base, IVA, total)
    amount_pattern = r'(\d{1,10}[.,]\d{2})'

    base_match = re.search(r'Base\s*:?\s*' + amount_pattern, pdf_text, re.IGNORECASE)
    data["base"] = float(base_match.group(1).replace(',', '.')) if base_match else None

    iva_match = re.search(r'IVA\s*:?\s*' + amount_pattern, pdf_text, re.IGNORECASE)
    data["vat"] = float(iva_match.group(1).replace(',', '.')) if iva_match else None

    total_match = re.search(r'Total\s*:?\s*' + amount_pattern, pdf_text, re.IGNORECASE)
    data["total"] = float(total_match.group(1).replace(',', '.')) if total_match else None

    return data
```

## Testing

```python
# Test with text-based PDF
pdf_bytes = open("text_invoice.pdf", "rb").read()
result = extract_pdf_text(pdf_bytes)
assert result["method"] == "text"
assert result["success"] == True

# Test with scanned PDF
pdf_bytes = open("scanned_invoice.pdf", "rb").read()
result = extract_pdf_text(pdf_bytes)
assert result["method"] == "ocr"
assert result["success"] == True
```

## Performance Notes

- Text extraction: ~100ms per page
- OCR: ~2-5 seconds per page (depends on image quality and DPI)
- Higher DPI = better OCR accuracy but slower processing
- Recommended DPI: 300 for invoices, 200 for general documents

## Common Issues

1. **Empty text despite visible text in PDF**: PDF might be using custom fonts. Try OCR.
2. **OCR produces gibberish**: Increase DPI to 400-600 or improve image preprocessing
3. **Tesseract not found**: Install tesseract-ocr system package
```

---

## Cómo Marito Usa Esta Documentación

```python
class CodeGenerator:
    def __init__(self, tools_catalog_path: str):
        self.tools_catalog = self.load_tools_catalog(tools_catalog_path)

    def load_tools_catalog(self, path: str) -> dict:
        """Load all tool documentation"""
        tools = {}

        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.md'):
                    tool_name = file.replace('.md', '')
                    file_path = os.path.join(root, file)

                    with open(file_path, 'r') as f:
                        tools[tool_name] = f.read()

        return tools

    def find_relevant_tools(self, step_description: str) -> list:
        """
        Encuentra qué herramientas son relevantes para un paso
        """

        # Usar LLM para matchear descripción con tools
        prompt = f"""
        Given this task: "{step_description}"

        Available tools:
        {', '.join(self.tools_catalog.keys())}

        Which tools are needed? Return as JSON array.
        Example: ["outlook_imap", "extract_text_pdf", "postgresql"]
        """

        response = gpt4.invoke(prompt)
        needed_tools = json.loads(response)

        return needed_tools

    def generate_code_with_tools(self, step: dict) -> str:
        """
        Genera código usando las tool docs como referencia
        """

        # 1. Encontrar tools relevantes
        needed_tools = self.find_relevant_tools(step["description"])

        # 2. Cargar documentación de esos tools
        tool_docs = ""
        for tool_name in needed_tools:
            if tool_name in self.tools_catalog:
                tool_docs += f"\n\n### TOOL: {tool_name}\n"
                tool_docs += self.tools_catalog[tool_name]

        # 3. Generar código con contexto de tools
        prompt = f"""
        You are generating Python code for this task:

        TASK: {step["description"]}

        INPUT: {step["input_from"]}
        OUTPUT: {step["output_to"]}

        AVAILABLE TOOL DOCUMENTATION:
        {tool_docs}

        INSTRUCTIONS:
        1. Use the tool templates provided above as reference
        2. Adapt them to the specific task requirements
        3. Combine multiple tools if needed
        4. Include error handling
        5. Return production-ready code

        Generate the complete Python code.
        """

        code = gpt4.invoke(prompt)

        return code

# USO
generator = CodeGenerator(tools_catalog_path="/marito/tools/")

# Para step "read_emails":
code = generator.generate_code_with_tools({
    "description": "Read unread Outlook emails with PDF attachments",
    "input_from": "credentials",
    "output_to": "email_list"
})

# GPT-4 genera código basado en outlook_imap.md template
```

---

## Por Qué Esto Funciona

### ✅ Ventajas del Tool Documentation System

1. **Código más consistente**: GPT-4 sigue templates probados
2. **Menos errores**: Documentación incluye error handling
3. **Reutilización**: Mismas tools para diferentes flujos
4. **Actualizable**: Cambias la doc, mejoran todas las generaciones futuras
5. **Explicable**: Puedes ver qué template usó Marito

### 📚 Qué Tools Necesitas Documentar (MVP)

**Email**:
- `outlook_imap.md` - Leer emails de Outlook
- `gmail_imap.md` - Leer emails de Gmail
- `send_email_smtp.md` - Enviar emails

**PDF**:
- `extract_text_pdf.md` - Extraer texto de PDF
- `generate_pdf_reportlab.md` - Generar PDFs

**Database**:
- `postgresql.md` - CRUD en PostgreSQL
- `sqlite.md` - CRUD en SQLite

**Files**:
- `read_excel.md` - Leer Excel (pandas/openpyxl)
- `write_csv.md` - Escribir CSV

**HTTP**:
- `make_http_request.md` - Hacer requests HTTP
- `parse_html.md` - Parsear HTML (BeautifulSoup)

**Total: ~12-15 tools documentados** cubren 80% de casos de uso.

---

## Siguiente Paso

¿Quieres que escribamos 3-5 tool docs completos como ejemplos?

O prefieres que veamos **cómo el orquestador decide qué tools usar para cada paso**?
```
