"""
Authentication request and response schemas.
Pydantic v2 syntax throughout.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, model_validator
import re


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class RegisterRequest(BaseModel):
    """Payload for POST /auth/register."""

    email: EmailStr = Field(..., description="User e-mail address")
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username (3-50 chars, alphanumeric + underscore)",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (min 8 characters)",
    )

    @model_validator(mode="after")
    def username_valid(self) -> "RegisterRequest":
        if not re.match(r"^[a-zA-Z0-9_]+$", self.username):
            raise ValueError("username must be alphanumeric and may contain underscores")
        return self

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "john@example.com",
                "username": "john_doe",
                "password": "SecureP@ss123",
            }
        }
    }


class LoginRequest(BaseModel):
    """Payload for POST /auth/login."""

    email: EmailStr = Field(..., description="Registered e-mail address")
    password: str = Field(..., description="Account password")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "john@example.com",
                "password": "SecureP@ss123",
            }
        }
    }


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class Token(BaseModel):
    """JWT token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }
    }


class UserResponse(BaseModel):
    """Public user profile returned in responses."""

    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    """Combined token + user profile returned on successful login / register."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
