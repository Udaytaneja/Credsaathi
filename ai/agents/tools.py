"""Whitelisted read-only tools for Saakshi Assistant."""
from typing import Any, Dict, Optional

# Synthetic mock database for authorized user application contexts (Zero DB write access)
SYNTHETIC_USER_APPLICATIONS = {
    "APP_101": {
        "owner_user_id": "user_ramesh_01",
        "scheme_name": "PMEGP Manufacturing Scheme",
        "status": "UNDER_VERIFICATION",
        "submitted_date": "2026-09-28",
        "next_step": "Upload Income Proof & Bank Statement",
        "verified_metrics": {"validated_income": 450000.0, "loan_required": 500000.0}
    },
    "APP_102": {
        "owner_user_id": "user_sita_02",
        "scheme_name": "Stree Shakti Udyam Scheme",
        "status": "APPROVED_PRELIMINARY",
        "submitted_date": "2026-09-25",
        "next_step": "Visit Local Bank Branch for Document Signing",
        "verified_metrics": {"validated_income": 300000.0, "loan_required": 200000.0}
    }
}


class SaakshiTools:
    """Whitelisted read-only tools with strict tenant data scope enforcement."""

    def get_application_status(self, user_id: str, application_id: str) -> Optional[Dict[str, Any]]:
        """Fetches application status ONLY if user_id owns application_id."""
        app_data = SYNTHETIC_USER_APPLICATIONS.get(application_id)
        if not app_data:
            return None

        # Scope Check: Enforce user data isolation
        if app_data["owner_user_id"] != user_id:
            return None  # Unauthorized cross-tenant access attempt

        return {
            "application_id": application_id,
            "status": app_data["status"],
            "scheme_name": app_data["scheme_name"],
            "submitted_date": app_data["submitted_date"],
            "next_step": app_data["next_step"]
        }


saakshi_tools = SaakshiTools()
