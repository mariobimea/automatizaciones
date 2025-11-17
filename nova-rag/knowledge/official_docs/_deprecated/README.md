# Deprecated Documentation

This folder contains documentation for integrations that have been **deprecated** and are no longer actively used in NOVA workflows.

## Deprecated Integrations

### EasyOCR (`easyocr_official.md`)

**Deprecated**: 2025-01-17
**Replaced by**: Google Cloud Vision API ([google_vision_ocr.md](../google_vision_ocr.md))

**Reason for deprecation**:
- Complex API made LLM code generation difficult
- Heavy template dependencies (PyTorch ~850 MB)
- E2B template size: 22.4 GB (caused $3.60-$9 per execution)
- Cold start time: 2-5 minutes
- Lower accuracy: 83% average (vs 98% with Google Vision)

**Migration**: See `/documentacion/MIGRACION_VISION_API.md` for full migration guide

---

## Why Keep Deprecated Docs?

These docs are kept for:
1. **Reference**: Understanding past implementation decisions
2. **Rollback**: If needed to revert to previous solution
3. **Learning**: Comparing different approaches
4. **Future**: May become relevant again (e.g., if switching to self-hosted OCR at high volume)

---

**Note**: RAG system should NOT load docs from `_deprecated/` folder unless explicitly requested.
