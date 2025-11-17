# Google Cloud Vision API - OCR Integration Guide

**Version**: 3.8.0 (latest as of 2025)
**Official Docs**: https://cloud.google.com/vision/docs/ocr
**Status**: ✅ PRODUCTION READY for NOVA workflows

---

## Overview

Google Cloud Vision API provides **high-accuracy OCR** (98%+ precision) optimized for document processing like invoices, receipts, and forms.

### Key Features

- **98% accuracy** on printed text (Spanish + English)
- **Simple API**: Single function call to extract text
- **Fast**: ~1 second per page
- **Cost-effective**: $1.50 per 1,000 pages
- **Scalable**: No template dependencies, external API

---

## Installation

```bash
pip install google-cloud-vision
```

**Version**: Install `google-cloud-vision>=3.8.0`

**Dependencies**: Only requires `google-cloud-vision` (lightweight, ~10 MB)

---

## Authentication

### Service Account Setup

1. **Create Service Account** in Google Cloud Console
2. **Download JSON key file** (e.g., `vision-service-account.json`)
3. **Set environment variable**:

```python
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/path/to/service-account.json'
```

**IMPORTANT for E2B Sandbox**:
- Service account JSON must be available in the sandbox environment
- Pass credentials via environment variable or inline JSON

```python
# Option 1: Environment variable (recommended)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/tmp/gcp-credentials.json'

# Option 2: Inline credentials (for E2B)
from google.oauth2 import service_account
import json

credentials = service_account.Credentials.from_service_account_info(
    json.loads(os.environ['GCP_SERVICE_ACCOUNT_JSON'])
)
client = vision.ImageAnnotatorClient(credentials=credentials)
```

---

## Basic Usage

### Extract Text from Image

```python
from google.cloud import vision

# Initialize client
client = vision.ImageAnnotatorClient()

# Read image file
with open('invoice.jpg', 'rb') as image_file:
    content = image_file.read()

# Create image object
image = vision.Image(content=content)

# Perform OCR
response = client.text_detection(image=image)

# Extract text
if response.text_annotations:
    full_text = response.text_annotations[0].description
    print(full_text)
else:
    print("No text detected")

# Check for errors
if response.error.message:
    raise Exception(f"Vision API Error: {response.error.message}")
```

---

## OCR Methods

### 1. `text_detection()` - For sparse text in images

**Use case**: Photos, signs, labels

```python
response = client.text_detection(image=image)
full_text = response.text_annotations[0].description
```

### 2. `document_text_detection()` - For dense documents ⭐ RECOMMENDED

**Use case**: Invoices, receipts, forms, contracts

```python
response = client.document_text_detection(image=image)
full_text = response.full_text_annotation.text
```

**Why use `document_text_detection` for invoices**:
- Preserves document structure (pages, blocks, paragraphs)
- Better handling of tables and multi-column layouts
- Provides confidence scores per word
- Supports language detection

---

## Extract Text from PDF

### Convert PDF page to image first

Google Cloud Vision **cannot process PDF bytes directly**. You must:

1. **Convert PDF to images** using PyMuPDF
2. **Run OCR on each image**

```python
import fitz  # PyMuPDF
from google.cloud import vision
import io

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using Google Cloud Vision OCR"""

    client = vision.ImageAnnotatorClient()
    doc = fitz.open(pdf_path)
    all_text = []

    for page_num in range(len(doc)):
        # Convert page to image
        page = doc[page_num]
        pix = page.get_pixmap(dpi=300)  # High DPI for better OCR
        img_bytes = pix.tobytes("png")

        # OCR on image
        image = vision.Image(content=img_bytes)
        response = client.document_text_detection(image=image)

        if response.full_text_annotation:
            all_text.append(response.full_text_annotation.text)

        # Check for errors
        if response.error.message:
            raise Exception(f"Vision API Error on page {page_num}: {response.error.message}")

    doc.close()
    return "\n\n--- PAGE BREAK ---\n\n".join(all_text)
```

**Performance tips**:
- Use `dpi=300` for high-quality text extraction
- For faster processing with lower accuracy, use `dpi=150`
- Process pages in parallel if needed (use `asyncio` or threads)

---

## Structured Data Extraction

### Get text with bounding boxes and confidence

```python
response = client.document_text_detection(image=image)

# Iterate through detected text blocks
for page in response.full_text_annotation.pages:
    for block in page.blocks:
        block_text = ""
        block_confidence = 0.0

        for paragraph in block.paragraphs:
            for word in paragraph.words:
                word_text = "".join([symbol.text for symbol in word.symbols])
                word_confidence = word.confidence

                block_text += word_text + " "
                block_confidence += word_confidence

        avg_confidence = block_confidence / len(block.paragraphs)
        print(f"Block: {block_text.strip()} (confidence: {avg_confidence:.2%})")
```

---

## Invoice Processing Example

### Complete workflow: PDF → OCR → Extract fields

```python
from google.cloud import vision
import fitz
import re

def process_invoice(pdf_path):
    """Extract invoice data using Google Cloud Vision OCR"""

    # 1. Initialize Vision API client
    client = vision.ImageAnnotatorClient()

    # 2. Convert PDF to image
    doc = fitz.open(pdf_path)
    page = doc[0]  # First page only
    pix = page.get_pixmap(dpi=300)
    img_bytes = pix.tobytes("png")
    doc.close()

    # 3. Run OCR
    image = vision.Image(content=img_bytes)
    response = client.document_text_detection(image=image)

    if response.error.message:
        raise Exception(f"Vision API Error: {response.error.message}")

    # 4. Extract full text
    full_text = response.full_text_annotation.text

    # 5. Parse invoice fields using regex
    invoice_data = {
        "invoice_number": extract_invoice_number(full_text),
        "date": extract_date(full_text),
        "total": extract_total(full_text),
        "supplier_cif": extract_cif(full_text),
        "raw_text": full_text
    }

    return invoice_data

def extract_invoice_number(text):
    """Extract invoice number from text"""
    patterns = [
        r'(?:Invoice|Factura|N[úu]mero)[:\s]*([A-Z0-9-]+)',
        r'(?:No\.|#)[:\s]*([A-Z0-9-]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

def extract_date(text):
    """Extract date from text"""
    patterns = [
        r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY
        r'\d{4}-\d{2}-\d{2}'   # YYYY-MM-DD
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None

def extract_total(text):
    """Extract total amount from text"""
    patterns = [
        r'(?:Total|TOTAL)[:\s]*([\d,.]+)\s*€?',
        r'(?:Total|TOTAL)[:\s]*€\s*([\d,.]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '.')
            return float(amount_str)
    return None

def extract_cif(text):
    """Extract Spanish CIF/NIF"""
    pattern = r'\b[A-Z]\d{8}\b|\b\d{8}[A-Z]\b'
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    return None
```

---

## Error Handling

### Handle common errors gracefully

```python
from google.api_core import exceptions

try:
    response = client.document_text_detection(image=image)

    # Check for API errors
    if response.error.message:
        raise Exception(f"Vision API Error: {response.error.message}")

    # Check if text was detected
    if not response.full_text_annotation:
        raise ValueError("No text detected in image")

    text = response.full_text_annotation.text

except exceptions.InvalidArgument as e:
    print(f"Invalid image format: {e}")

except exceptions.PermissionDenied as e:
    print(f"Authentication error: {e}")
    print("Check GOOGLE_APPLICATION_CREDENTIALS environment variable")

except exceptions.ResourceExhausted as e:
    print(f"API quota exceeded: {e}")

except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Performance Optimization

### Image quality matters

**DPI recommendations**:
- **300 DPI**: Best quality, recommended for invoices (default)
- **150 DPI**: Faster, acceptable for simple documents
- **72 DPI**: Very fast, only for clean printed text

```python
# High quality (slower, best OCR)
pix = page.get_pixmap(dpi=300)

# Balanced (faster, good OCR)
pix = page.get_pixmap(dpi=150)
```

### Batch processing

Process multiple images efficiently:

```python
async def process_batch(image_paths):
    """Process multiple images in parallel"""
    import asyncio

    async def process_one(path):
        client = vision.ImageAnnotatorClient()
        with open(path, 'rb') as f:
            image = vision.Image(content=f.read())
        response = await client.document_text_detection_async(image=image)
        return response.full_text_annotation.text

    tasks = [process_one(path) for path in image_paths]
    results = await asyncio.gather(*tasks)
    return results
```

---

## Cost Management

### Pricing (as of 2025)

- **First 1,000 units/month**: FREE
- **1,001 - 5,000,000 units**: $1.50 per 1,000 units
- **5,000,001+**: $0.60 per 1,000 units

**1 unit = 1 image OCR request**

### Cost estimation examples

| Scenario | Monthly pages | Cost |
|----------|---------------|------|
| MVP (100 invoices/day) | 3,000 | $4.50 |
| Small business (500/day) | 15,000 | $22.50 |
| Medium (2,000/day) | 60,000 | $90.00 |

**Optimization tips**:
- Check if PDF has text layer before OCR (use `has_text_layer()`)
- Cache OCR results in database
- Use lower DPI for simple documents

---

## Language Support

### Automatic language detection (recommended)

```python
# No language hints needed - Vision API auto-detects
response = client.document_text_detection(image=image)
```

### Explicit language hints (optional)

```python
from google.cloud import vision

image_context = vision.ImageContext(language_hints=['es', 'en'])
response = client.document_text_detection(image=image, image_context=image_context)
```

**Supported languages**: 50+ including Spanish, English, French, German, Italian, Portuguese, etc.

---

## Best Practices for NOVA Workflows

### 1. Always check PDF text layer first

```python
def should_use_ocr(pdf_path):
    """Check if PDF needs OCR (no text layer)"""
    doc = fitz.open(pdf_path)
    page = doc[0]
    text = page.get_text()
    doc.close()

    # If extractable text exists, don't use OCR
    return len(text.strip()) < 50  # Threshold for "empty"
```

### 2. Use `document_text_detection` for invoices

```python
# ✅ CORRECT - For structured documents
response = client.document_text_detection(image=image)

# ❌ WRONG - For invoices (use text_detection only for photos/signs)
response = client.text_detection(image=image)
```

### 3. Handle credentials in E2B sandbox

```python
import os
import json
from google.cloud import vision
from google.oauth2 import service_account

# Get credentials from environment variable
creds_json = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')

if creds_json:
    # Parse JSON credentials
    creds_dict = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    client = vision.ImageAnnotatorClient(credentials=credentials)
else:
    # Fallback to default credentials (uses GOOGLE_APPLICATION_CREDENTIALS)
    client = vision.ImageAnnotatorClient()
```

### 4. Validate extracted data

```python
def validate_invoice_data(data):
    """Validate OCR results before saving"""
    errors = []

    if not data.get('invoice_number'):
        errors.append("Missing invoice number")

    if not data.get('total') or data['total'] <= 0:
        errors.append("Invalid total amount")

    # Spanish CIF validation
    cif = data.get('supplier_cif', '')
    if not re.match(r'^[A-Z]\d{8}$|^\d{8}[A-Z]$', cif):
        errors.append("Invalid CIF format")

    return errors
```

---

## Common Issues & Solutions

### Issue 1: "Could not find default credentials"

**Error**: `google.auth.exceptions.DefaultCredentialsError`

**Solution**: Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

### Issue 2: "Permission denied"

**Error**: `403 Permission Denied`

**Solution**:
1. Enable Vision API in Google Cloud Console
2. Check service account has "Cloud Vision API User" role
3. Verify billing is enabled

### Issue 3: "No text detected" on valid invoice

**Possible causes**:
- Image resolution too low (use DPI 300)
- Image is corrupted
- Image is blank or nearly blank

**Solution**: Check image quality before sending to API

```python
from PIL import Image

img = Image.open('invoice.jpg')
print(f"Resolution: {img.size}")  # Should be at least 1000x1000 pixels
```

### Issue 4: Low confidence scores

**Solution**: Improve image quality
- Increase DPI when converting PDF to image
- Ensure good contrast (black text on white background)
- Remove noise/artifacts from scanned images

---

## Comparison with EasyOCR

| Aspect | Google Cloud Vision | EasyOCR |
|--------|---------------------|---------|
| **Accuracy** | 98% | 83% |
| **Speed** | ~1s per page | ~7s per page |
| **API Complexity** | Simple (1 function call) | Complex (Reader init, parsing) |
| **Dependencies** | 1 package (~10 MB) | Multiple packages (~850 MB) |
| **Cost** | $1.50 / 1,000 pages | Free |
| **Setup** | Service account JSON | Model downloads |
| **E2B Template Size** | Normal (~1-2 GB) | Large (~22 GB) |
| **Cold Start** | N/A (external API) | 2-5 minutes (model loading) |

**Verdict**: Google Cloud Vision is **significantly simpler** for LLM code generation and **more accurate** for invoice processing.

---

## References

- **Official Docs**: https://cloud.google.com/vision/docs/ocr
- **Python Client Library**: https://cloud.google.com/python/docs/reference/vision/latest
- **Pricing**: https://cloud.google.com/vision/pricing
- **Quickstart**: https://cloud.google.com/vision/docs/setup
- **Best Practices**: https://cloud.google.com/vision/docs/best-practices

---

**Last Updated**: 2025-01-17
**Status**: Production-ready for NOVA workflows
**Recommended for**: All invoice/receipt/document OCR tasks
