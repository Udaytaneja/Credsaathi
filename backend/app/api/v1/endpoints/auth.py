from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.applicant_profile import ApplicantProfile
from app.models.role import Role
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserSessionResponse

router = APIRouter()


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new applicant or banker user account",
)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    """Registers a new user, hashes password, assigns role, and returns access token + session."""
    normalized_email = body.email.lower().strip()

    # Check for existing user
    existing_user = db.query(User).filter(User.email == normalized_email, User.deleted_at.is_(None)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    # Get or create Role
    requested_role_name = body.role.upper().strip()
    if requested_role_name not in ("APPLICANT", "BANKER", "BANK_ADMIN", "CRED_SAATHI_ADMIN"):
        requested_role_name = "APPLICANT"

    role = db.query(Role).filter(Role.name == requested_role_name).first()
    if not role:
        role = Role(name=requested_role_name, description=f"{requested_role_name.title()} user role")
        db.add(role)
        db.flush()

    # Hash password
    hashed_pwd = hash_password(body.password)

    # Create User
    new_user = User(
        email=normalized_email,
        password_hash=hashed_pwd,
        full_name=body.name.strip(),
        role_id=role.id,
        organization_id=body.organization_id,
        is_active=True,
        is_verified=True,
    )
    db.add(new_user)
    db.flush()

    # Create default ApplicantProfile if APPLICANT
    if requested_role_name == "APPLICANT":
        profile = ApplicantProfile(user_id=new_user.id)
        db.add(profile)

    db.commit()
    db.refresh(new_user)

    # Create JWT Access Token
    access_token = create_access_token(
        subject=str(new_user.id),
        email=new_user.email,
        role=role.name,
        organization_id=str(new_user.organization_id) if new_user.organization_id else None,
    )

    org_name = new_user.organization.name if new_user.organization else None

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserSessionResponse(
            id=str(new_user.id),
            name=new_user.full_name,
            email=new_user.email,
            role=role.name,
            organization=org_name,
        ),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user credentials and issue JWT token",
)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """Authenticates user credentials securely and returns access token + session."""
    normalized_email = body.email.lower().strip()

    user = db.query(User).filter(User.email == normalized_email, User.deleted_at.is_(None)).first()

    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account.",
        )

    role_name = user.role.name if user.role else "APPLICANT"
    org_name = user.organization.name if user.organization else None

    access_token = create_access_token(
        subject=str(user.id),
        email=user.email,
        role=role_name,
        organization_id=str(user.organization_id) if user.organization_id else None,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserSessionResponse(
            id=str(user.id),
            name=user.full_name,
            email=user.email,
            role=role_name,
            organization=org_name,
        ),
    )
