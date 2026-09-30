"""
Authentication service: user registration, login, and lookup.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import LoginResponse, RegisterRequest, LoginRequest, UserResponse

logger = logging.getLogger(__name__)


class AuthService:
    """Handles all authentication-related business logic."""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @staticmethod
    def register_user(db: Session, data: RegisterRequest) -> User:
        """
        Create a new user account.

        Raises
        ------
        HTTPException 400
            If e-mail or username is already taken.
        """
        if AuthService.get_user_by_email(db, data.email, raise_if_missing=False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists",
            )
        if AuthService._get_user_by_username(db, data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username is already taken",
            )

        user = User(
            email=data.email,
            username=data.username,
            hashed_password=hash_password(data.password),
            is_active=True,
        )
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
        except Exception as exc:
            db.rollback()
            logger.exception("Error during user registration")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not complete registration",
            ) from exc

        logger.info("Registered new user id=%s email=%s", user.id, user.email)
        return user

    @staticmethod
    def login_user(db: Session, data: LoginRequest) -> LoginResponse:
        """
        Authenticate a user and return an access token.

        Raises
        ------
        HTTPException 401
            If credentials are invalid or the account is inactive.
        """
        user = AuthService.get_user_by_email(db, data.email, raise_if_missing=False)

        # Use a constant-time-safe comparison path: always call verify_password
        # even for a non-existent user to prevent timing attacks.
        dummy_hash = "$2b$12$KIXkJ3zQzQ3zQ3zQ3zQ3zOq7Q3zQ3zQ3zQ3zQ3zQ3zQ3zQ3zQ3zQ"  # noqa
        password_ok = verify_password(
            data.password,
            user.hashed_password if user else dummy_hash,
        )

        if not user or not password_ok:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        token = create_access_token({"sub": str(user.id)})
        logger.info("User id=%s logged in", user.id)

        return LoginResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    @staticmethod
    def get_user_by_email(
        db: Session,
        email: str,
        raise_if_missing: bool = True,
    ) -> Optional[User]:
        """
        Look up a user by e-mail address.

        Parameters
        ----------
        raise_if_missing:
            When True (default), raises HTTP 404 if the user is not found.
            Set to False to return None instead.
        """
        user: Optional[User] = (
            db.query(User).filter(User.email == email).first()
        )
        if user is None and raise_if_missing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """
        Look up a user by primary key.

        Raises
        ------
        HTTPException 404
            If the user does not exist.
        """
        user: Optional[User] = db.get(User, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_user_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_from_token(db: Session, token: str) -> User:
        """
        Decode a raw JWT string and return the matching User.
        Used by the dependencies module.
        """
        from app.core.security import verify_token

        payload = verify_token(token)
        try:
            user_id = int(payload["sub"])
        except (KeyError, ValueError, TypeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc
        return AuthService.get_user_by_id(db, user_id)
