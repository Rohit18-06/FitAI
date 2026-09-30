"""
Phase 7 – Teams & Communities API endpoints.
Covers Community Clubs, Teams, and Memberships.
"""

from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.social import (
    TeamCreate,
    TeamResponse,
    TeamMemberResponse,
)
from app.services.social_service import TeamService

router = APIRouter(prefix="/teams", tags=["Teams & Communities"])


@router.post(
    "",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new athletic team",
)
def create_team(
    data: TeamCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> TeamResponse:
    try:
        team = TeamService.create(db, current_user, data)
        team_data = TeamService.get_by_id(db, team.id, current_user)
        return TeamResponse(**team_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "",
    response_model=List[TeamResponse],
    summary="List all community teams",
)
def list_teams(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[TeamResponse]:
    teams = TeamService.get_all(db, current_user)
    return [TeamResponse(**t) for t in teams]


@router.get(
    "/{team_id}",
    response_model=TeamResponse,
    summary="Get team by ID with roster",
)
def get_team(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> TeamResponse:
    try:
        t = TeamService.get_by_id(db, team_id, current_user)
        return TeamResponse(**t)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/{team_id}/join",
    response_model=TeamMemberResponse,
    summary="Join an athletic team",
)
def join_team(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> TeamMemberResponse:
    try:
        mem = TeamService.join(db, current_user, team_id)
        return TeamMemberResponse(
            id=mem.id,
            team_id=mem.team_id,
            user_id=mem.user_id,
            username=current_user.username,
            role=mem.role,
            joined_at=mem.joined_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/{team_id}/leave",
    summary="Leave an athletic team",
)
def leave_team(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict:
    try:
        TeamService.leave(db, current_user, team_id)
        return {"success": True, "message": "Left team"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
