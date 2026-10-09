import uuid
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.scheme import Scheme
from app.models.user import User
from app.schemas.application import ALLOWED_STATUS_TRANSITIONS, ApplicationCreate


class ApplicationService:
    """
    Service handling backend application creation, retrieval, ownership authorization,
    and status state machine transitions.
    """

    @staticmethod
    def list_applications(db: Session, current_user: User) -> list[Application]:
        role_name = current_user.role.name.upper() if current_user.role else "APPLICANT"

        query = db.query(Application).filter(Application.deleted_at.is_(None))

        if role_name == "APPLICANT":
            query = query.filter(Application.user_id == current_user.id)
        elif role_name in ("BANKER", "BANK_ADMIN"):
            if current_user.organization_id:
                query = query.filter(Application.organization_id == current_user.organization_id)

        return query.order_by(Application.created_at.desc()).all()

    @staticmethod
    def create_application(db: Session, current_user: User, data: ApplicationCreate) -> Application:
        # Verify scheme exists
        scheme = db.query(Scheme).filter(Scheme.id == data.scheme_id, Scheme.deleted_at.is_(None)).first()
        if not scheme:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scheme with ID '{data.scheme_id}' does not exist.",
            )

        # Generate unique application number
        app_number = f"APP-{datetime.now(timezone.utc).year}-{uuid.uuid4().hex[:8].upper()}"

        org_id = data.organization_id or current_user.organization_id

        new_app = Application(
            application_number=app_number,
            user_id=current_user.id,
            scheme_id=data.scheme_id,
            organization_id=org_id,
            requested_amount=data.requested_amount,
            status="DRAFT",
            readiness_score=None,
        )

        db.add(new_app)
        db.commit()
        db.refresh(new_app)
        return new_app

    @staticmethod
    def get_application_by_id(db: Session, current_user: User, application_id: uuid.UUID) -> Application:
        app = (
            db.query(Application)
            .filter(Application.id == application_id, Application.deleted_at.is_(None))
            .first()
        )

        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application with ID '{application_id}' not found.",
            )

        # Enforce authorization rules
        role_name = current_user.role.name.upper() if current_user.role else "APPLICANT"

        if role_name == "APPLICANT" and app.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You do not own this application.",
            )

        if role_name in ("BANKER", "BANK_ADMIN"):
            if current_user.organization_id and app.organization_id and app.organization_id != current_user.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied. Application belongs to a different organization.",
                )

        return app

    @classmethod
    def update_application_status(
        cls, db: Session, current_user: User, application_id: uuid.UUID, new_status: str
    ) -> Application:
        app = cls.get_application_by_id(db, current_user, application_id)
        current_status = app.status.upper()
        target_status = new_status.upper().strip()

        if current_status == target_status:
            return app

        # Validate status state machine transition
        allowed_next = ALLOWED_STATUS_TRANSITIONS.get(current_status, set())
        if target_status not in allowed_next:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status transition from '{current_status}' to '{target_status}'.",
            )

        # Role authorization for specific transitions
        role_name = current_user.role.name.upper() if current_user.role else "APPLICANT"
        if role_name == "APPLICANT":
            if target_status not in ("SUBMITTED", "CLOSED"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Applicants are not permitted to set status to '{target_status}'.",
                )

        # Audit status change & timestamp
        app.status = target_status
        if target_status == "SUBMITTED" and app.submitted_at is None:
            app.submitted_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(app)
        return app
