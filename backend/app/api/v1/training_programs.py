"""Phase 8: AI Training Programs API."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.training import (
    TrainingProgramCreate, TrainingProgramResponse,
    ProgramDayResponse, ProgramWeekResponse, ProgramDayExercise,
    CompleteDayRequest,
)
from app.services.training_ai_service import TrainingProgramService

router = APIRouter(prefix="/training-programs", tags=["Training Programs"])


@router.post("", response_model=TrainingProgramResponse, status_code=status.HTTP_201_CREATED)
def generate_program(
    data: TrainingProgramCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Generate a new AI training program."""
    program = TrainingProgramService.generate_program(
        db, user.id, data.fitness_goal, data.fitness_level,
        data.duration_weeks, data.days_per_week,
    )
    return _serialize_program(program)


@router.get("", response_model=list[TrainingProgramResponse])
def list_programs(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    programs = TrainingProgramService.list_programs(db, user.id)
    return [_serialize_program(p) for p in programs]


@router.get("/active", response_model=TrainingProgramResponse | None)
def get_active_program(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    program = TrainingProgramService.get_active_program(db, user.id)
    if not program:
        return None
    return _serialize_program(program)


@router.post("/complete-day")
def complete_day(
    data: CompleteDayRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    day = TrainingProgramService.complete_day(db, user.id, data.day_id)
    if not day:
        raise HTTPException(status_code=404, detail="Day not found")
    return {"success": True, "day_id": day.id, "completed": True}


def _serialize_program(p) -> dict:
    weeks = []
    for w in (p.weeks or []):
        days = []
        for d in (w.days or []):
            exercises = []
            for ex in (d.exercises_json or []):
                exercises.append(ProgramDayExercise(
                    name=ex.get("name", ""), sets=ex.get("sets", 3),
                    reps=str(ex.get("reps", "10")), rest_seconds=ex.get("rest_seconds", 60),
                    notes=ex.get("notes"),
                ))
            days.append(ProgramDayResponse(
                id=d.id, day_number=d.day_number, day_name=d.day_name,
                focus=d.focus, exercises=exercises,
                warmup=d.warmup_json or [], cooldown=d.cooldown_json or [],
                estimated_duration_min=d.estimated_duration_min,
                completed=d.completed, completed_at=d.completed_at,
            ))
        weeks.append(ProgramWeekResponse(
            id=w.id, week_number=w.week_number, theme=w.theme,
            intensity_pct=w.intensity_pct, volume_modifier=w.volume_modifier,
            notes=w.notes, days=days,
        ))
    return TrainingProgramResponse(
        id=p.id, user_id=p.user_id, title=p.title, description=p.description,
        fitness_goal=p.fitness_goal, fitness_level=p.fitness_level,
        duration_weeks=p.duration_weeks, days_per_week=p.days_per_week,
        is_active=p.is_active, ai_notes=p.ai_notes, weeks=weeks,
        created_at=p.created_at, updated_at=p.updated_at,
    )
