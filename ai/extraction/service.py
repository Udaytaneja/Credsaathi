"""Document AI Orchestrator Service."""
from ai.extraction.classifiers.classifier import classifier
from ai.extraction.confidence.scorer import confidence_scorer
from ai.extraction.extractors.extractor import extractor
from ai.extraction.loaders.loader import document_loader
from ai.extraction.normalizers.normalizer import normalizer
from ai.extraction.ocr.engine import ocr_engine
from ai.extraction.schemas import DocumentExtractionRequest, DocumentExtractionResponseData, ProcessingMetadata, SupportedDocumentType
from ai.extraction.validators.validator import validator


class DocumentAIService:
    """Orchestrates Document AI pipeline: Load -> OCR -> Classify -> Extract -> Normalize -> Validate -> Score -> Guard."""

    async def process_document(self, req: DocumentExtractionRequest) -> DocumentExtractionResponseData:
        # 1. Load & Validate File
        raw_bytes = b""
        mime_type = "application/pdf"
        file_size = 0

        if req.file_bytes_base64:
            raw_bytes, mime_type = document_loader.validate_and_load(req.file_name, req.file_bytes_base64)
            file_size = len(raw_bytes)

        # 2. OCR Text Extraction
        ocr_text, ocr_confidence = ocr_engine.extract_text(
            raw_bytes=raw_bytes,
            mime_type=mime_type,
            text_override=req.file_text_override
        )

        # 3. Classify Document Type
        classified_type = classifier.classify(ocr_text, hint_type=req.document_type)

        # 4. Extract Structured Fields
        raw_fields = await extractor.extract_fields(ocr_text, classified_type.value)

        # 5. Normalize Fields
        normalized_fields = normalizer.normalize(raw_fields)

        # 6. Validate Mandatory Schemas
        val_warnings, missing_mandatory = validator.validate(classified_type.value, normalized_fields)

        # 7. Calculate Field Confidence & Human Review Flag
        field_conf, review_req, conf_warnings = confidence_scorer.calculate_confidence(
            ocr_doc_confidence=ocr_confidence,
            fields=normalized_fields,
            missing_mandatory=missing_mandatory
        )

        all_warnings = list(dict.fromkeys(val_warnings + conf_warnings))

        proc_meta = ProcessingMetadata(
            ocr_engine=ocr_engine.engine_name,
            model_version="1.0.0",
            file_size_bytes=file_size,
            file_type=mime_type
        )

        return DocumentExtractionResponseData(
            document_type=classified_type.value,
            fields=normalized_fields,
            field_confidence=field_conf,
            warnings=all_warnings,
            review_required=review_req,
            processing_metadata=proc_meta
        )


document_ai_service = DocumentAIService()
