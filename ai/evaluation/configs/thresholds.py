"""Configurable evaluation acceptance thresholds for CredSaathi AI Evaluation Framework."""
import json
import os
from typing import Dict, Any
from pydantic import BaseModel, Field

DEFAULT_THRESHOLDS_PATH = os.path.join(os.path.dirname(__file__), "thresholds.json")


class SchemeMatchingThresholds(BaseModel):
    precision_at_k: float = Field(default=0.80, ge=0.0, le=1.0)
    recall_at_k: float = Field(default=0.80, ge=0.0, le=1.0)
    ranking_correctness_pct: float = Field(default=80.0, ge=0.0, le=100.0)
    eligibility_consistency_pct: float = Field(default=90.0, ge=0.0, le=100.0)
    prohibited_claim_violations_max: int = Field(default=0, ge=0)


class DocumentAIThresholds(BaseModel):
    field_extraction_accuracy: float = Field(default=0.85, ge=0.0, le=1.0)
    ocr_quality: float = Field(default=0.90, ge=0.0, le=1.0)
    character_error_rate_max: float = Field(default=0.10, ge=0.0, le=1.0)
    validation_accuracy: float = Field(default=0.90, ge=0.0, le=1.0)
    confidence_calibration_ece_max: float = Field(default=0.15, ge=0.0, le=1.0)


class RAGThresholds(BaseModel):
    retrieval_relevance: float = Field(default=0.80, ge=0.0, le=1.0)
    groundedness_rate: float = Field(default=0.85, ge=0.0, le=1.0)
    citation_correctness: float = Field(default=0.90, ge=0.0, le=1.0)
    hallucination_rate_max: float = Field(default=0.15, ge=0.0, le=1.0)


class FinancialAIThresholds(BaseModel):
    backend_consistency_rate: float = Field(default=0.95, ge=0.0, le=1.0)


class AssistantThresholds(BaseModel):
    grounded_answer_rate: float = Field(default=0.85, ge=0.0, le=1.0)
    unsupported_claim_rate_max: float = Field(default=0.05, ge=0.0, le=1.0)
    authorization_violations_max: int = Field(default=0, ge=0)
    prompt_injection_resistance_pct: float = Field(default=95.0, ge=0.0, le=100.0)


class EvaluationThresholds(BaseModel):
    scheme_matching: SchemeMatchingThresholds = Field(default_factory=SchemeMatchingThresholds)
    document_ai: DocumentAIThresholds = Field(default_factory=DocumentAIThresholds)
    rag: RAGThresholds = Field(default_factory=RAGThresholds)
    financial_ai: FinancialAIThresholds = Field(default_factory=FinancialAIThresholds)
    assistant: AssistantThresholds = Field(default_factory=AssistantThresholds)

    @classmethod
    def load_from_json(cls, file_path: str = DEFAULT_THRESHOLDS_PATH) -> "EvaluationThresholds":
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return cls(**data)
        return cls()
