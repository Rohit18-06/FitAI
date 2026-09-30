"""
Security utilities: password hashing and JWT token management.

Functions
---------
hash_password        – bcrypt hash a plain-text password
verify_password      – compare plain-text against a stored hash
create_access_token  – mint a signed JWT
verify_token         – decode and validate a JWT; return payload dict
get_current_user     – FastAPI dependency: resolves bearer token → User ORM object
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

logger = logging.getLogger(__name__)
import bcrypt

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

_bearer_scheme = HTTPBearer()


def hash_password(plain: str) -> str:
    """Return the bcrypt hash of *plain*."""
    pwd_bytes = plain.encode("utf-8")[:72]
    return bcrypt.hashpw(pwd_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches the stored *hashed* password."""
    try:
        pwd_bytes = plain.encode("utf-8")[:72]
        return bcrypt.checkpw(pwd_bytes, hashed.encode("utf-8"))
    except Exception as exc:
        logger.warning("Password verification failed with error: %s", exc)
        return False


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create and return a signed JWT access token.

    Parameters
    ----------
    data:
        Arbitrary claims to embed in the payload.  The ``"sub"`` key should
        hold the user's ID as a string.
    expires_delta:
        Override the default expiry (ACCESS_TOKEN_EXPIRE_MINUTES from config).
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str) -> dict:
    """
    Decode and validate a JWT.

    Returns the decoded payload dict.

    Raises
    ------
    HTTPException 401
        If the token is invalid, expired, or missing the ``"sub"`` claim.
    """
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as exc:
        logger.warning("JWT decode error: %s", exc)
        raise credentials_exc

    if payload.get("sub") is None:
        raise credentials_exc

    return payload


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
):
    """
    FastAPI dependency that extracts the bearer token, verifies it, and
    returns the corresponding User ORM object.

    Raises HTTP 401 if the token is invalid or the user no longer exists.
    Raises HTTP 403 if the user account is inactive.
    """
    # Import here to avoid circular imports at module level
    from app.models.user import User

    payload = verify_token(credentials.credentials)

    try:
        user_id = int(payload["sub"])
    except (KeyError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user: Optional[User] = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    return user
