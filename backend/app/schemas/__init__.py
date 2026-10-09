from app.schemas.applicant_profile import (
    ApplicantProfileCreate,
    ApplicantProfileResponse,
    ApplicantProfileUpdate,
)
from app.schemas.application import ApplicationCreate, ApplicationResponse
from app.schemas.document import DocumentCreate, DocumentResponse
from app.schemas.financial_profile import FinancialProfileCreate, FinancialProfileResponse
from app.schemas.loan_requirement import LoanRequirementCreate, LoanRequirementResponse
from app.schemas.scheme import SchemeCreate, SchemeResponse

__all__ = [
    "ApplicantProfileCreate",
    "ApplicantProfileResponse",
    "ApplicantProfileUpdate",
    "ApplicationCreate",
    "ApplicationResponse",
    "DocumentCreate",
    "DocumentResponse",
    "FinancialProfileCreate",
    "FinancialProfileResponse",
    "LoanRequirementCreate",
    "LoanRequirementResponse",
    "SchemeCreate",
    "SchemeResponse",
]
