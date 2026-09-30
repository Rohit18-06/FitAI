"""User-related Pydantic schemas."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema with common fields."""
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    age: Optional[int] = Field(None, ge=13, le=120)
    gender: Optional[str] = None
    height_cm: Optional[float] = Field(None, gt=0)
    weight_kg: Optional[float] = Field(None, gt=0)
    fitness_goal: Optional[str] = None
    experience_level: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=255)


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    age: Optional[int] = Field(None, ge=13, le=120)
    gender: Optional[str] = None
    height_cm: Optional[float] = Field(None, gt=0)
    weight_kg: Optional[float] = Field(None, gt=0)
    fitness_goal: Optional[str] = None
    experience_level: Optional[str] = None


class UserResponse(UserBase):
    """Response schema for user data (excludes password)."""
    id: int = Field(..., description="User ID")
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True


class CurrentUser(UserResponse):
    """Schema for currently authenticated user."""
    pass
