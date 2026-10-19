from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import verify_password, create_access_token
from backend.app.core.roles import normalize_role
from backend.app.models.user import User
from backend.app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from backend.app.services.audit_service import AuditService
from backend.app.api.deps import get_current_user, get_required_user

router = APIRouter()


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User Login with Short-Lived Access Token",
    description="Authenticates user credentials and issues a signed, short-lived JWT access token (30 min)."
)
def login(
    req: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
) -> TokenResponse:
    user = db.query(User).filter(User.email == req.email.strip()).first()
    client_ip = request.client.host if request.client else None

    if not user or not verify_password(req.password, user.hashed_password):
        # Log security audit for failed attempt
        AuditService.log_event(
            db=db,
            organization_id=user.organization_id if user else "org-gem-meity",
            event_type="AUTH_LOGIN_FAILED",
            entity_type="User",
            entity_id=user.id if user else "UNKNOWN",
            actor_id=user.id if user else None,
            actor_role="ANONYMOUS",
            ip_address=client_ip,
            description=f"Failed login attempt for email '{req.email}'.",
            metadata={"email": req.email}
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated.",
        )

    token = create_access_token(
        subject=user.id,
        role=user.role,
        org_id=user.organization_id
    )

    # Log successful login
    AuditService.log_event(
        db=db,
        organization_id=user.organization_id,
        event_type="AUTH_LOGIN_SUCCESS",
        entity_type="User",
        entity_id=user.id,
        actor_id=user.id,
        actor_role=user.role,
        ip_address=client_ip,
        description=f"User '{user.full_name}' ({user.email}) logged in successfully with role '{user.role}'.",
        metadata={"role": user.role}
    )
    db.commit()

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in_seconds=1800,  # 30 minutes
        user_id=user.id,
        email=user.email,
        role=normalize_role(user.role).value,
        organization_id=user.organization_id,
        full_name=user.full_name
    )


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="OAuth2 Password Token Endpoint",
    description="OAuth2 standard compliant endpoint for Swagger UI authorization dialog."
)
def oauth2_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> TokenResponse:
    user = db.query(User).filter(User.email == form_data.username.strip()).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated.",
        )

    token = create_access_token(
        subject=user.id,
        role=user.role,
        org_id=user.organization_id
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in_seconds=1800,
        user_id=user.id,
        email=user.email,
        role=normalize_role(user.role).value,
        organization_id=user.organization_id,
        full_name=user.full_name
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User Profile",
    description="Returns the profile and role privileges of the currently authenticated user."
)
def get_me(current_user: User = Depends(get_required_user)) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=normalize_role(current_user.role).value,
        organization_id=current_user.organization_id,
        is_active=current_user.is_active
    )


@router.post(
    "/logout",
    summary="User Logout",
    description="Logs out the current session and registers an audit log event."
)
def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else None
    AuditService.log_event(
        db=db,
        organization_id=current_user.organization_id,
        event_type="AUTH_LOGOUT",
        entity_type="User",
        entity_id=current_user.id,
        actor_id=current_user.id,
        actor_role=current_user.role,
        ip_address=client_ip,
        description=f"User '{current_user.email}' logged out.",
    )
    db.commit()
    return {"message": "Session terminated successfully."}
