"""
Phase 7 – Challenges API endpoints.
Covers Community Challenges, Enrollment, and Progress Tracking.
"""

from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.social import (
    ChallengeCreate,
    ChallengeResponse,
    ChallengeParticipantResponse,
)
from app.services.social_service import ChallengeService

router = APIRouter(prefix="/challenges", tags=["Challenges"])


@router.post(
    "",
    response_model=ChallengeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new community challenge",
)
def create_challenge(
    data: ChallengeCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> ChallengeResponse:
    challenge = ChallengeService.create(db, current_user, data)
    ch_dict = ChallengeService.get_by_id(db, challenge.id, current_user)
    return ChallengeResponse(**ch_dict)


@router.get(
    "",
    response_model=List[ChallengeResponse],
    summary="List all community challenges",
)
def list_challenges(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[ChallengeResponse]:
    challenges = ChallengeService.get_all(db, current_user)
    return [ChallengeResponse(**c) for c in challenges]


@router.get(
    "/my",
    response_model=List[ChallengeResponse],
    summary="List challenges currently joined by user",
)
def get_my_challenges(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[ChallengeResponse]:
    challenges = ChallengeService.get_my(db, current_user)
    return [ChallengeResponse(**c) for c in challenges]


@router.get(
    "/{challenge_id}",
    response_model=ChallengeResponse,
    summary="Get challenge by ID",
)
def get_challenge(
    challenge_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> ChallengeResponse:
    try:
        ch = ChallengeService.get_by_id(db, challenge_id, current_user)
        return ChallengeResponse(**ch)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/{challenge_id}/join",
    response_model=ChallengeParticipantResponse,
    summary="Join a community challenge",
)
def join_challenge(
    challenge_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> ChallengeParticipantResponse:
    try:
        part = ChallengeService.join(db, current_user, challenge_id)
        return ChallengeParticipantResponse(
            id=part.id,
            challenge_id=part.challenge_id,
            user_id=part.user_id,
            username=current_user.username,
            progress=part.progress,
            completed=part.completed,
            joined_at=part.joined_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/{challenge_id}/leave",
    summary="Leave a community challenge",
)
def leave_challenge(
    challenge_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict:
    try:
        ChallengeService.leave(db, current_user, challenge_id)
        return {"success": True, "message": "Left challenge"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
