"""User profile endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services import UserService
from app.schemas import UserUpdate
from app.utils import format_response
from app.api.dependencies import get_current_active_user
from app.models import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
)
def get_user_profile(
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """
    Get the currently authenticated user's profile.
    
    Args:
        current_user: The authenticated user (injected by dependency).
        
    Returns:
        User profile data.
    """
    return format_response(
        success=True,
        message="User profile retrieved",
        data={
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "age": current_user.age,
            "gender": current_user.gender,
            "height_cm": current_user.height_cm,
            "weight_kg": current_user.weight_kg,
            "fitness_goal": current_user.fitness_goal.value if current_user.fitness_goal else None,
            "experience_level": current_user.experience_level.value if current_user.experience_level else None,
            "is_active": current_user.is_active,
            "created_at": current_user.created_at,
            "updated_at": current_user.updated_at,
        },
    )


@router.put(
    "/me",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Update user profile",
)
def update_user_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Update the currently authenticated user's profile.
    
    Args:
        update_data: User profile update data.
        current_user: The authenticated user (injected by dependency).
        db: Database session.
        
    Returns:
        Updated user profile data.
    """
    updated_user = UserService.update_user_profile(db, current_user.id, update_data)
    
    return format_response(
        success=True,
        message="User profile updated successfully",
        data={
            "id": updated_user.id,
            "name": updated_user.name,
            "email": updated_user.email,
            "age": updated_user.age,
            "gender": updated_user.gender,
            "height_cm": updated_user.height_cm,
            "weight_kg": updated_user.weight_kg,
            "fitness_goal": updated_user.fitness_goal.value if updated_user.fitness_goal else None,
            "experience_level": updated_user.experience_level.value if updated_user.experience_level else None,
            "is_active": updated_user.is_active,
            "updated_at": updated_user.updated_at,
        },
    )


@router.get(
    "/{user_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get user by ID",
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """
    Get user profile by ID (requires authentication).
    
    Args:
        user_id: The user ID to retrieve.
        db: Database session.
        current_user: The authenticated user (injected by dependency).
        
    Returns:
        User profile data.
    """
    user = UserService.get_user_by_id(db, user_id)
    
    return format_response(
        success=True,
        message="User profile retrieved",
        data={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "age": user.age,
            "gender": user.gender,
            "height_cm": user.height_cm,
            "weight_kg": user.weight_kg,
            "fitness_goal": user.fitness_goal.value if user.fitness_goal else None,
            "experience_level": user.experience_level.value if user.experience_level else None,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        },
    )
