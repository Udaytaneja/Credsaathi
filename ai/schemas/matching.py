"""Pydantic schemas for CredSaathi Scheme Matching AI."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class ApplicantContext(BaseModel):
    """Applicant profile context passed from core backend."""
    applicant_id: Optional[str] = Field(default=None, description="Optional anonymous applicant ID")
    category: Optional[str] = Field(default=None, description="Category e.g. General, OBC, SC, ST, Women, Student")
    state: Optional[str] = Field(default=None, description="State of residence")
    income_annual: Optional[float] = Field(default=None, ge=0.0, description="Annual income in INR")
    occupation: Optional[str] = Field(default=None, description="Occupation / profession")
    age: Optional[int] = Field(default=None, ge=0, le=120, description="Age in years")
    gender: Optional[str] = Field(default=None, description="Gender identity")
    purpose: Optional[str] = Field(default=None, description="Purpose for loan or scheme e.g. Higher Education, Business Expansion")
    additional_attributes: Dict[str, Any] = Field(default_factory=dict, description="Additional verified backend profile key-values")


class CandidateScheme(BaseModel):
    """Candidate scheme entity deterministically pre-filtered by Kashvi's backend."""
    scheme_id: str = Field(..., description="Unique scheme identifier from backend database")
    scheme_name: str = Field(..., description="Official scheme name")
    category: str = Field(default="General", description="Target scheme category")
    description: str = Field(..., description="Summary description of scheme benefits")
    eligibility_criteria: List[str] = Field(default_factory=list, description="Backend eligibility rules/criteria text")
    required_documents: List[str] = Field(default_factory=list, description="List of required supporting documents")
    backend_eligibility_status: str = Field(default="ELIGIBLE", description="Backend deterministic status: ELIGIBLE, PARTIAL, NEEDS_INFO")
    source_reference: str = Field(default="Official Portal", description="Verified source reference")
    last_verified: str = Field(default="2026-10-01", description="ISO date when scheme rules were verified")


class SchemeMatchRequest(BaseModel):
    """Request payload for scheme semantic matching and ranking."""
    applicant_context: ApplicantContext = Field(..., description="Applicant profile context")
    candidate_schemes: List[CandidateScheme] = Field(..., min_length=1, description="Backend-filtered candidate scheme list")
    language: str = Field(default="en", description="Output explanation language ('en', 'hi', 'hinglish')")

    @field_validator("candidate_schemes")
    @classmethod
    def validate_candidate_schemes_not_empty(cls, v: List[CandidateScheme]) -> List[CandidateScheme]:
        if not v:
            raise ValueError("Candidate schemes list cannot be empty.")
        return v


class SchemeMatchResult(BaseModel):
    """Result item representing a matched, ranked, and explained scheme."""
    scheme_id: str = Field(..., description="Scheme unique ID")
    scheme_name: str = Field(..., description="Official scheme name")
    relevance_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Semantic match relevance score (0.0 - 1.0). NOTE: This is NOT an approval probability, credit score, or guaranteed eligibility."
    )
    eligibility_status: str = Field(..., description="Deterministic backend eligibility status passed through")
    match_reasons: List[str] = Field(default_factory=list, description="Grounded key reasons why applicant matches scheme requirements")
    missing_information: List[str] = Field(default_factory=list, description="Missing applicant attributes or documents required for complete application")
    source_reference: str = Field(..., description="Source portal/document reference")
    last_verified: str = Field(..., description="Last verification date of scheme rules")
    explanation: str = Field(..., description="Plain-language explanation of semantic fit")


class SchemeMatchResponseData(BaseModel):
    """Container for list of ranked scheme matches."""
    matches: List[SchemeMatchResult] = Field(..., description="List of ranked and explained scheme matches")
    disclaimer: str = Field(
        default="Relevance scores indicate semantic matching compatibility based on provided data. Relevance scores are NOT loan approval probabilities, credit scores, or guaranteed eligibility approvals.",
        description="Mandatory financial safety disclaimer"
    )
