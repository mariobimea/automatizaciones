# PDF OCR Workflow

## How to Extract Text from Scanned PDFs using OCR

When a PDF is scanned (images only, no text layer), you CANNOT use PyMuPDF's `get_text()` directly. You need to:

1. **Convert PDF pages to images** using PyMuPDF
2. **Apply OCR to each image** using Google Cloud Vision API

## Complete Working Example

```python
import fitz  # PyMuPDF
from google.cloud import vision
import base64
import io
import json
import os

# Step 1: Initialize Google Cloud Vision client
# Credentials are loaded from GCP_SERVICE_ACCOUNT_JSON environment variable
creds_json = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
if creds_json:
    from google.oauth2 import service_account
    creds_dict = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    client = vision.ImageAnnotatorClient(credentials=credentials)
else:
    # Fallback to default credentials (development)
    client = vision.ImageAnnotatorClient()

# Step 2: Decode PDF from base64
pdf_bytes = base64.b64decode(context['pdf_data'])
pdf_stream = io.BytesIO(pdf_bytes)

# Step 3: Open PDF with PyMuPDF
doc = fitz.open(stream=pdf_stream, filetype='pdf')

# Step 4: Process each page
all_text = []

for page_num in range(len(doc)):
    page = doc[page_num]

    # Convert page to image (PNG format)
    # Use higher DPI (300) for better OCR accuracy
    pix = page.get_pixmap(dpi=300)

    # Get image bytes in PNG format
    img_bytes = pix.tobytes("png")

    # Apply OCR using Google Cloud Vision
    image = vision.Image(content=img_bytes)
    response = client.document_text_detection(image=image)

    # Check for errors
    if response.error.message:
        raise Exception(f"Vision API Error: {response.error.message}")

    # Extract text from response
    if response.full_text_annotation:
        page_text = response.full_text_annotation.text
        all_text.append(page_text)

doc.close()

# Step 5: Join all extracted text
ocr_text = '\n\n'.join(all_text)

# Step 6: Return results
print(json.dumps({
    "status": "success",
    "context_updates": {
        "ocr_text": ocr_text,
        "extraction_method_used": "google_vision",
        "pages_processed": len(all_text)
    },
    "message": f"OCR extracted {len(ocr_text)} chars from {len(all_text)} pages"
}))
```

## Important Notes

### DO NOT do this (common mistake):
```python
# ❌ WRONG - Vision API cannot read PDF bytes directly
pdf_data = base64.b64decode(context['pdf_data'])
image = vision.Image(content=pdf_data)  # This will FAIL!
response = client.document_text_detection(image=image)
```

### DO this instead:
```python
# ✅ CORRECT - Convert PDF to image first, then OCR
import fitz
doc = fitz.open(stream=io.BytesIO(pdf_bytes), filetype='pdf')
pix = doc[0].get_pixmap(dpi=300)  # Page to image
img_bytes = pix.tobytes("png")     # Image as PNG bytes

# Now OCR the image
image = vision.Image(content=img_bytes)
response = client.document_text_detection(image=image)
text = response.full_text_annotation.text
```

## When to Use OCR vs PyMuPDF Text Extraction

### Use PyMuPDF `get_text()` when:
- PDF has a text layer (digital PDF, searchable)
- Faster and more accurate than OCR
- context['recommended_extraction_method'] == 'pymupdf'

### Use Google Cloud Vision OCR when:
- PDF is scanned (no text layer)
- PDF contains images of text
- context['recommended_extraction_method'] == 'ocr'
- Better accuracy than other OCR solutions (98% vs 83% with EasyOCR)

## Performance Tips

1. **DPI setting**: Higher DPI = better accuracy but slower
   - 150 DPI: Fast but lower quality
   - 300 DPI: Good balance (recommended)
   - 600 DPI: Maximum quality but very slow

2. **Batch processing**: Process multiple pages in parallel if needed

3. **Cost optimization**:
   - First 1,000 pages/month: FREE
   - Additional pages: $1.50 per 1,000 pages
   - Example: 3,000 invoices/month = $3.00/month

## Error Handling

```python
try:
    # OCR workflow here
    all_text = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(dpi=300)
        img_bytes = pix.tobytes("png")

        image = vision.Image(content=img_bytes)
        response = client.document_text_detection(image=image)

        # Check for errors
        if response.error.message:
            raise Exception(f"Vision API Error on page {page_num + 1}: {response.error.message}")

        if response.full_text_annotation:
            all_text.append(response.full_text_annotation.text)

    ocr_text = '\n\n'.join(all_text)

except Exception as e:
    # Fallback: return empty text on error
    print(json.dumps({
        "status": "error",
        "context_updates": {"ocr_text": "", "ocr_error": str(e)},
        "message": f"OCR failed: {str(e)}"
    }))
```

## Authentication

Google Cloud Vision requires authentication via service account:

```python
import os
import json
from google.oauth2 import service_account
from google.cloud import vision

# Option 1: From environment variable (recommended for E2B)
creds_json = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
if creds_json:
    creds_dict = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    client = vision.ImageAnnotatorClient(credentials=credentials)
else:
    # Option 2: Default credentials (development)
    client = vision.ImageAnnotatorClient()
```

The `GCP_SERVICE_ACCOUNT_JSON` environment variable should contain the full JSON content of the service account key.

## Example Context Usage

```python
# Context should have:
# - pdf_data: base64 encoded PDF (NO prefix like "data:application/pdf;base64,")
# - recommended_extraction_method: 'ocr' or 'pymupdf'

recommended_method = context.get('recommended_extraction_method', 'pymupdf')

if recommended_method == 'ocr':
    # Use Google Cloud Vision OCR workflow above
    pass
elif recommended_method == 'pymupdf':
    # Use PyMuPDF get_text() instead (faster for digital PDFs)
    doc = fitz.open(stream=pdf_stream, filetype='pdf')
    text = ''
    for page in doc:
        text += page.get_text()
    doc.close()
```

## Comparison with EasyOCR (deprecated)

Google Cloud Vision is recommended over EasyOCR for:
- ✅ Simpler API (1 function call vs complex initialization)
- ✅ Better accuracy (98% vs 83%)
- ✅ No heavy dependencies (no PyTorch needed)
- ✅ Lighter E2B template (1.2GB vs 22.4GB)
- ✅ Faster cold start (<30s vs 2-5min)
- ⚠️ Small cost ($1.50/1000 pages after first 1,000 free)
