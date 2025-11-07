# OCR Solutions Comparison for NOVA

**Date**: 2025-11-07
**Purpose**: Evaluate OCR options to handle scanned invoices with no text layer
**Context**: PyMuPDF (fitz) can't extract text from scanned PDFs - need real OCR capability

---

## Problem Statement

NOVA currently uses PyMuPDF for PDF text extraction, which only works with PDFs that have a text layer. When processing scanned invoices (like Amazon receipts), `page.get_text()` returns empty string because there's no extractable text - just an image.

**We need**: OCR capability to extract text from scanned/image-based PDFs.

---

## Options Evaluated

| Option | Type | Cost | Accuracy | Integration |
|--------|------|------|----------|-------------|
| **Tesseract OCR** | Local/Open-source | Free | 89-94% (clean), 65-80% (difficult) | Docker install |
| **Google Cloud Vision** | API | $1.50/1K images (after 1K free) | 95%+ | HTTP API |
| **AWS Textract** | API | $0.01/page (invoices) | 95%+ | HTTP API |
| **Azure Document Intelligence** | API | Pay-per-page | 95%+ | HTTP API |

---

## 1. Tesseract OCR (Local)

### Overview
Open-source OCR engine that runs locally in Docker container.

### Pricing
- **Cost**: $0 (completely free)
- **No API limits**
- **No per-page charges**

### Accuracy
- **Clean scans**: 89-94% accuracy
- **Difficult documents**: 65-80% accuracy
- **Scanned invoices**: Adequate but lower than cloud solutions
- **Line order issues**: Sometimes swaps lines or drops faded characters on skewed scans

### Language Support
- Supports 100+ languages including Spanish
- Strong performance on mainstream Latin languages (English, Spanish, French, German)

### Integration Complexity
**Docker Installation** (Medium complexity):
```dockerfile
FROM python:3.11-slim

# Install Tesseract OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \  # Spanish language pack
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install pytesseract Pillow pdf2image

COPY app.py /app/
CMD ["python", "/app/app.py"]
```

**Python Usage**:
```python
import pytesseract
from PIL import Image
import pdf2image

# Convert PDF to images
pages = pdf2image.convert_from_bytes(pdf_data)

# Extract text from first page
text = pytesseract.image_to_string(pages[0], lang='spa')
```

### Pros
✅ **Zero cost** - completely free
✅ **No API limits** - process unlimited documents
✅ **Data privacy** - all processing happens locally in Hetzner VM
✅ **No external dependencies** - works offline
✅ **Spanish language support** built-in
✅ **Version 5.x** is mature and stable

### Cons
❌ **Lower accuracy** than cloud solutions (especially on difficult scans)
❌ **Requires Docker image update** - adds ~200MB to image size
❌ **Line order issues** on skewed/rotated documents
❌ **No invoice-specific optimization** - generic OCR

### Cost Analysis (Monthly)
- **0 invoices/month**: $0
- **1,000 invoices/month**: $0
- **10,000 invoices/month**: $0
- **100,000 invoices/month**: $0

**Winner for cost**: Unlimited processing at zero cost.

---

## 2. Google Cloud Vision API

### Overview
Cloud-based OCR service with DOCUMENT_TEXT_DETECTION optimized for dense text.

### Pricing
- **Free tier**: First 1,000 units/month free
- **1,001 - 5M units**: $1.50 per 1,000 units
- **5M+ units**: $0.60 per 1,000 units
- **Note**: Each page = 1 unit

### Accuracy
- **Industry-leading** for OCR tasks
- Optimized for dense text and documents
- Returns confidence scores for each detection
- Handles skewed, rotated, and poor-quality scans well

### Language Support
- Supports 50+ languages including Spanish
- Multi-language detection in same document

### Integration Complexity
**Low complexity** - HTTP REST API:
```python
from google.cloud import vision
import io

client = vision.ImageAnnotatorClient()

# Process PDF page as image
image = vision.Image(content=pdf_page_bytes)
response = client.document_text_detection(image=image)

text = response.full_text_annotation.text
```

### Pros
✅ **High accuracy** (95%+) even on difficult scans
✅ **Generous free tier** (1,000 pages/month)
✅ **Simple REST API** - easy integration
✅ **Confidence scores** for quality control
✅ **Document-optimized** - preserves layout, paragraphs, blocks
✅ **Handles rotation/skew** automatically

### Cons
❌ **Costs money** after free tier
❌ **External API dependency** - requires internet from Hetzner VM
❌ **Privacy concern** - documents sent to Google servers
❌ **Authentication complexity** - need Google Cloud credentials
❌ **Latency** - network round-trip time (~200-500ms per page)

### Cost Analysis (Monthly)
- **100 invoices/month**: $0 (within free tier)
- **1,000 invoices/month**: $0 (within free tier)
- **5,000 invoices/month**: $6.00
- **10,000 invoices/month**: $13.50
- **100,000 invoices/month**: $148.50

---

## 3. AWS Textract (Analyze Expense API)

### Overview
AWS service specifically designed for invoice and receipt processing.

### Pricing
- **Free tier**: 100 pages/month for first 3 months (new customers only)
- **Cost**: $0.01 per page (first 1M pages)
- **Volume discount**: $0.008 per page (beyond 1M)

### Accuracy
- **Invoice-specific optimization** - trained specifically for invoices/receipts
- Returns structured data (line items, totals, dates, vendor info)
- High accuracy for key-value pairs and tables
- Confidence scores included

### Language Support
- English only (officially documented)
- May handle Spanish but not officially supported

### Integration Complexity
**Low complexity** - AWS SDK:
```python
import boto3

client = boto3.client('textract')

response = client.analyze_expense(
    Document={'Bytes': pdf_data}
)

# Extract structured invoice data
for expense_doc in response['ExpenseDocuments']:
    for field in expense_doc['SummaryFields']:
        print(f"{field['Type']['Text']}: {field['ValueDetection']['Text']}")
```

### Pros
✅ **Invoice-specific** - extracts structured data (line items, totals, taxes)
✅ **High accuracy** for invoice processing
✅ **Returns structured JSON** - not just text
✅ **Confidence scores** for validation
✅ **Mature AWS service** with good documentation

### Cons
❌ **Most expensive option** ($0.01/page = $10 per 1,000 invoices)
❌ **Limited free tier** (only 100 pages/month for 3 months)
❌ **English only** - Spanish support not documented
❌ **AWS credentials required**
❌ **Privacy concern** - documents sent to AWS
❌ **Latency** - network round-trip time

### Cost Analysis (Monthly)
- **100 invoices/month**: $1.00 (or free during 3-month trial)
- **1,000 invoices/month**: $10.00
- **5,000 invoices/month**: $50.00
- **10,000 invoices/month**: $100.00
- **100,000 invoices/month**: $1,000.00

**Most expensive option** - 6.7x more expensive than Google Cloud Vision.

---

## 4. Azure Computer Vision / Document Intelligence

### Overview
Microsoft's OCR service with document-specific features.

### Pricing
- **Pay-per-transaction** model
- Pricing varies by region and features used
- **Exact pricing not transparent** - need to contact Microsoft or use calculator
- Estimated similar to Google Cloud Vision (~$1-2 per 1,000 pages)

### Accuracy
- High accuracy comparable to Google/AWS
- Document Intelligence optimized for invoices and forms
- Returns structured data with confidence scores

### Language Support
- Supports 100+ languages including Spanish
- Prebuilt models for receipts and invoices

### Integration Complexity
**Low-Medium complexity** - HTTP REST API:
```python
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

client = DocumentIntelligenceClient(endpoint, AzureKeyCredential(key))

poller = client.begin_analyze_document(
    "prebuilt-invoice",
    document=pdf_bytes
)
result = poller.result()
```

### Pros
✅ **High accuracy** (95%+)
✅ **Invoice-specific models** available
✅ **Structured extraction** - line items, totals, dates
✅ **Spanish language support**
✅ **Prebuilt invoice model** reduces configuration

### Cons
❌ **Pricing not transparent** - harder to estimate costs
❌ **External API dependency**
❌ **Privacy concern** - documents sent to Microsoft
❌ **Azure credentials required**
❌ **Less popular than Google/AWS** - smaller community

### Cost Analysis (Monthly)
**Estimated** (similar to Google Cloud Vision):
- **1,000 invoices/month**: ~$1.50
- **10,000 invoices/month**: ~$15.00
- **100,000 invoices/month**: ~$150.00

---

## Comparison Matrix

### By Cost (10,000 invoices/month)

| Solution | Monthly Cost | Annual Cost |
|----------|-------------|-------------|
| **Tesseract** | **$0** | **$0** |
| Google Cloud Vision | $13.50 | $162 |
| Azure Document Intelligence | ~$15 (est) | ~$180 |
| AWS Textract | $100 | $1,200 |

### By Accuracy (for scanned invoices)

| Solution | Accuracy | Invoice-Specific |
|----------|----------|------------------|
| **Google Cloud Vision** | **95%+** | Generic OCR |
| **AWS Textract** | **95%+** | ✅ **Yes - Invoice optimized** |
| Azure Document Intelligence | 95%+ | ✅ Yes - Invoice models |
| Tesseract | 65-80% | ❌ No |

### By Integration Complexity

| Solution | Complexity | Setup Time |
|----------|-----------|------------|
| **Tesseract** | Medium (Docker) | **30 min** |
| **Google Cloud Vision** | **Low (REST API)** | **15 min** |
| AWS Textract | Low (AWS SDK) | 20 min |
| Azure Document Intelligence | Medium (Azure SDK) | 25 min |

### By Privacy / Data Security

| Solution | Data Location | Privacy |
|----------|--------------|---------|
| **Tesseract** | **Local (Hetzner VM)** | ✅ **Best - No external data transfer** |
| Google Cloud Vision | Google servers (EU/US) | ⚠️ External processing |
| AWS Textract | AWS servers (US) | ⚠️ External processing |
| Azure Document Intelligence | Azure servers (EU/US) | ⚠️ External processing |

---

## Recommendation

### **Winner: Tesseract OCR** 🏆

**Why Tesseract wins for NOVA**:

1. **Zero Cost**
   - Completely free, no API limits
   - $0 vs $162/year (Google) vs $1,200/year (AWS)
   - Budget-friendly for MVP phase

2. **Data Privacy**
   - All processing happens locally in Hetzner VM
   - No external API calls exposing invoice data
   - GDPR-friendly (no data leaves EU)

3. **No External Dependencies**
   - Works offline
   - No API keys, authentication, or credentials needed
   - No network latency

4. **Good Enough Accuracy for MVP**
   - 65-80% accuracy on difficult scans is acceptable for Phase 1
   - Spanish language support included
   - Can upgrade to cloud OCR in Phase 2 if accuracy becomes critical

5. **Simple Integration**
   - Add 3 lines to Dockerfile
   - Install pytesseract via pip
   - Done - no authentication setup

6. **Scalable**
   - Unlimited processing capacity (only limited by VM resources)
   - Can process 100, 1,000, or 100,000 invoices at same $0 cost

### **When to Consider Alternatives**

**Use Google Cloud Vision if**:
- Accuracy becomes critical (need 95%+ instead of 65-80%)
- You're processing < 5,000 invoices/month (only ~$6/month)
- You need confidence scores for quality validation
- Handling very poor quality scans (skewed, rotated, faded)

**Use AWS Textract if**:
- You need structured invoice extraction (line items, totals, taxes)
- English-only invoices
- Budget allows $100+/month for OCR
- Already using AWS infrastructure

**Avoid Azure** unless:
- Already committed to Azure ecosystem
- Need specific Azure integrations

---

## Implementation Plan

### Phase 1: Tesseract OCR (Immediate - MVP)

**Week 1**:
1. ✅ Update Hetzner Docker image with Tesseract
2. ✅ Install pytesseract + pdf2image dependencies
3. ✅ Create `/knowledge/integrations/ocr.md` with usage docs
4. ✅ Add OCR detection to KnowledgeManager
5. ✅ Test with Amazon invoice PDF

**Dockerfile Changes**:
```dockerfile
FROM python:3.11-slim

# Install Tesseract OCR + Spanish
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    poppler-utils \  # For pdf2image
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install \
    pytesseract \
    pdf2image \
    Pillow \
    ... (existing dependencies)
```

**Expected Results**:
- Successfully extract text from scanned Amazon invoice
- Process 10+ test invoices with 70-80% accuracy
- Zero cost for unlimited processing

### Phase 2: Cloud OCR (Optional - If Accuracy Critical)

**Only implement if**:
- Tesseract accuracy < 70% in production
- Processing high-value invoices requiring 95%+ accuracy
- Customer complaints about extraction errors

**Recommendation**: Google Cloud Vision
- Best price/performance ratio
- Generous free tier (1,000/month)
- Only $13.50/month for 10,000 invoices

**Implementation**:
- Add Google Cloud credentials to Railway environment
- Create fallback: Try Tesseract first → If low confidence, use Google Cloud Vision
- Hybrid approach minimizes cost while maintaining high accuracy

---

## Cost Projections (3 Scenarios)

### Scenario 1: Low Volume (100 invoices/month)

| Solution | Cost/Month | Cost/Year |
|----------|-----------|-----------|
| Tesseract | **$0** | **$0** |
| Google Cloud Vision | $0 (free tier) | $0 |
| AWS Textract | $1 | $12 |

**Winner**: Tesseract or Google (both free)

### Scenario 2: Medium Volume (5,000 invoices/month)

| Solution | Cost/Month | Cost/Year |
|----------|-----------|-----------|
| Tesseract | **$0** | **$0** |
| Google Cloud Vision | $6 | $72 |
| AWS Textract | $50 | $600 |

**Winner**: Tesseract (saves $72-600/year)

### Scenario 3: High Volume (50,000 invoices/month)

| Solution | Cost/Month | Cost/Year |
|----------|-----------|-----------|
| Tesseract | **$0** | **$0** |
| Google Cloud Vision | $73.50 | $882 |
| AWS Textract | $500 | $6,000 |

**Winner**: Tesseract (saves $882-6,000/year)

---

## Technical Risks & Mitigations

### Risk 1: Tesseract Accuracy Too Low
**Probability**: Medium
**Impact**: High (incorrect invoice amounts)

**Mitigation**:
- Implement confidence threshold validation
- Flag low-confidence extractions for manual review
- Add fallback to Google Cloud Vision for flagged cases
- Test with real invoice samples before production

### Risk 2: Docker Image Size Increase
**Probability**: High
**Impact**: Low (slower deployments)

**Mitigation**:
- Tesseract adds ~200MB to image size
- Acceptable for Hetzner VM (not serverless)
- Use multi-stage Docker builds to minimize size
- Layer caching speeds up rebuilds

### Risk 3: Spanish Language Accuracy
**Probability**: Low
**Impact**: Medium

**Mitigation**:
- Tesseract has strong Spanish support (tested in benchmarks)
- Install `tesseract-ocr-spa` language pack
- Test with 10+ Spanish invoices before production
- Can fine-tune Tesseract with custom training data if needed

---

## Decision

**Choose Tesseract OCR** for NOVA Phase 1 (MVP).

**Reasons**:
1. Zero cost → More budget for other features
2. Data privacy → No external API calls
3. No external dependencies → Simpler architecture
4. Good enough accuracy → 65-80% acceptable for MVP
5. Easy to upgrade → Can add cloud OCR later if needed

**Next Steps**:
1. Update Hetzner Docker image with Tesseract
2. Create OCR knowledge base documentation
3. Test with 10+ real invoice samples
4. Deploy to production
5. Monitor accuracy metrics
6. Upgrade to cloud OCR only if accuracy < 70% in production

---

**Last Updated**: 2025-11-07
**Decision Made By**: Mario Ferrer
**Status**: Ready to implement
