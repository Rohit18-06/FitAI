"""User service for user profile management."""

from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserUpdate, UserResponse
from fastapi import HTTPException, status


class UserService:
    """Service for user-related operations."""

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """
        Get user by ID.
        
        Args:
            db: Database session.
            user_id: The user ID.
            
        Returns:
            The User object.
            
        Raises:
            HTTPException: If user not found.
        """
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        return user

    @staticmethod
    def update_user_profile(
        db: Session,
        user_id: int,
        update_data: UserUpdate,
    ) -> User:
        """
        Update user profile information.
        
        Args:
            db: Database session.
            user_id: The user ID to update.
            update_data: User update data.
            
        Returns:
            Updated User object.
        """
        user = UserService.get_user_by_id(db, user_id)
        
        # Update only provided fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> None:
        """
        Delete a user account.
        
        Args:
            db: Database session.
            user_id: The user ID to delete.
        """
        user = UserService.get_user_by_id(db, user_id)
        db.delete(user)
        db.commit()
