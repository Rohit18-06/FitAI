"""
Phase 7 – Social Profile API endpoint.
Public athlete profile display with stats, badges, followers, and activity.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.social import PublicProfileResponse
from app.services.social_service import SocialProfileService

router = APIRouter(prefix="/profile", tags=["Social Profile"])


@router.get(
    "/{username}",
    response_model=PublicProfileResponse,
    summary="Get public athlete profile by username",
)
def get_public_profile(
    username: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> PublicProfileResponse:
    try:
        profile_data = SocialProfileService.get_public_profile(db, username, current_user)
        return PublicProfileResponse(**profile_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
