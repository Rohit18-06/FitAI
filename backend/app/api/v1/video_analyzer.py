"""
Exercise video analysis routes.
POST /api/v1/video/analyze       – upload video & receive biomechanical critique
GET  /api/v1/video/history       – list past video evaluations
GET  /api/v1/video/{analysis_id} – get single analysis record
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Path, Query, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.form_analysis import FormAnalysisResponse
from app.services.video_analyzer_service import VideoAnalyzerService

router = APIRouter(prefix="/video", tags=["Gemini Video Analyzer"])


class VideoAnalyzeRequest(BaseModel):
    """Payload for direct JSON analysis submission (e.g. mobile/test clients)."""
    exercise_name: str = Field(..., min_length=2, max_length=100, description="Exercise name e.g. 'Barbell Squat'")
    filename: Optional[str] = Field(default="workout_recording.mp4")
    video_base64: Optional[str] = Field(default=None, description="Optional base64 encoded video or frames")


@router.post(
    "/analyze",
    response_model=FormAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analyze workout video file via multipart upload",
)
async def analyze_video_upload(
    exercise_name: str = Form(..., description="Exercise to evaluate (squat, pushup, deadlift, etc.)"),
    file: Optional[UploadFile] = File(default=None, description="Recorded video file (mp4, webm, mov)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FormAnalysisResponse:
    """Upload exercise video file for multimodal AI biomechanical analysis."""
    video_bytes = b""
    filename = "live_camera_capture.mp4"
    if file:
        filename = file.filename or filename
        video_bytes = await file.read()

    return VideoAnalyzerService.analyze_exercise_video(
        db=db,
        user=current_user,
        exercise_name=exercise_name,
        video_bytes=video_bytes,
        filename=filename,
    )


@router.post(
    "/analyze-direct",
    response_model=FormAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analyze exercise with direct JSON payload",
)
def analyze_exercise_direct(
    data: VideoAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FormAnalysisResponse:
    """Analyze exercise movement with structured JSON payload."""
    import base64
    video_bytes = b""
    if data.video_base64:
        try:
            video_bytes = base64.b64decode(data.video_base64)
        except Exception:
            video_bytes = b""

    return VideoAnalyzerService.analyze_exercise_video(
        db=db,
        user=current_user,
        exercise_name=data.exercise_name,
        video_bytes=video_bytes,
        filename=data.filename or "video.mp4",
    )


@router.get(
    "/history",
    response_model=List[FormAnalysisResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve video analysis history",
)
def get_video_history(
    limit: int = Query(default=20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[FormAnalysisResponse]:
    """Retrieve the user's historical form critiques."""
    return VideoAnalyzerService.get_analysis_history(db, current_user, limit=limit)


@router.get(
    "/{analysis_id}",
    response_model=FormAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve single video analysis record",
)
def get_video_analysis(
    analysis_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FormAnalysisResponse:
    """Retrieve detailed assessment for a specific analysis ID."""
    return VideoAnalyzerService.get_analysis_by_id(db, current_user, analysis_id)
