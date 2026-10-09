import uuid
from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Validate Bearer JWT token and return authenticated User ORM model."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token payload.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID claim.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_uuid, User.deleted_at.is_(None)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account.",
        )

    return user


def require_role(allowed_roles: list[str]) -> Callable[[User], User]:
    """Dependency factory returning a role-checker dependency."""

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role_name = current_user.role.name.upper() if current_user.role else "APPLICANT"
        upper_allowed = [r.upper() for r in allowed_roles]

        if user_role_name not in upper_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{user_role_name}' is not authorized to access this resource.",
            )
        return current_user

    return role_checker


def verify_user_access(current_user: User, target_user_id: uuid.UUID) -> None:
    """Enforce user-level data isolation."""
    role_name = current_user.role.name.upper() if current_user.role else "APPLICANT"
    if role_name == "APPLICANT" and current_user.id != target_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only access your own data.",
        )


def verify_organization_access(current_user: User, target_org_id: uuid.UUID | None) -> None:
    """Enforce organization/tenant isolation."""
    role_name = current_user.role.name.upper() if current_user.role else "APPLICANT"
    if role_name in ("BANKER", "BANK_ADMIN"):
        if current_user.organization_id and current_user.organization_id != target_org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Resource belongs to another organization tenant.",
            )
