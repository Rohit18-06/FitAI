"""
Auth routes: register, login, and /me profile.

POST /api/v1/auth/register  – create account
POST /api/v1/auth/login     – obtain JWT
GET  /api/v1/auth/me        – get current user profile (protected)
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=LoginResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    responses={
        201: {"description": "Account created, token returned"},
        400: {"description": "Email or username already taken"},
    },
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
) -> LoginResponse:
    """
    Register a new user and return an access token immediately so the
    client does not need a separate login call.
    """
    user = AuthService.register_user(db, data)
    # Issue a token right away (same as a login)
    from app.core.security import create_access_token
    token = create_access_token({"sub": str(user.id)})
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Login and obtain a JWT access token",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials"},
        403: {"description": "Account inactive"},
    },
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
) -> LoginResponse:
    """Authenticate with email + password and receive a bearer token."""
    return AuthService.login_user(db, data)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the authenticated user's profile",
    responses={
        200: {"description": "Profile returned"},
        401: {"description": "Unauthorized"},
    },
)
def get_me(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """Return the profile of the currently authenticated user."""
    return UserResponse.model_validate(current_user)
