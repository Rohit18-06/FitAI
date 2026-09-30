"""Database models for FitAI application."""

from app.models.user import User
from app.models.bmi import BMIRecord
from app.models.calorie import CalorieRecord
from app.models.workout import WorkoutRecord
from app.models.water import WaterRecord
from app.models.step import StepRecord
from app.models.diet_plan import DietPlan
from app.models.workout_plan import WorkoutPlan
from app.models.form_analysis import FormAnalysisRecord
from app.models.health_insight import HealthInsight
from app.models.coach_conversation import CoachConversation
from app.models.wearable_device import WearableDevice
from app.models.sleep_record import SleepRecord
from app.models.heart_rate_record import HeartRateRecord
from app.models.personal_record import PersonalRecord
from app.models.notification import Notification
from app.models.social import (
    Friendship,
    Follow,
    ActivityFeed,
    Challenge,
    ChallengeParticipant,
    UserLevel,
    Badge,
    UserBadge,
    Team,
    TeamMember,
)
from app.models.training import (
    TrainingProgram,
    ProgramWeek,
    ProgramDay,
    ExerciseProgression,
    RecoveryAssessment,
    WeeklyReport,
    GoalTracking,
    BodyMeasurement,
    ProgressPhoto,
    InjuryRiskAssessment,
)
from app.models.vision_trainer import (
    TrainerSession,
    PoseAnalysisLog,
    MovementLibraryItem,
    TrainerAdaptivePlan,
)

__all__ = [
    "User",
    "BMIRecord",
    "CalorieRecord",
    "WorkoutRecord",
    "WaterRecord",
    "StepRecord",
    "DietPlan",
    "WorkoutPlan",
    "FormAnalysisRecord",
    "HealthInsight",
    "CoachConversation",
    "WearableDevice",
    "SleepRecord",
    "HeartRateRecord",
    "PersonalRecord",
    "Notification",
    "Friendship",
    "Follow",
    "ActivityFeed",
    "Challenge",
    "ChallengeParticipant",
    "UserLevel",
    "Badge",
    "UserBadge",
    "Team",
    "TeamMember",
    # Phase 8
    "TrainingProgram",
    "ProgramWeek",
    "ProgramDay",
    "ExerciseProgression",
    "RecoveryAssessment",
    "WeeklyReport",
    "GoalTracking",
    "BodyMeasurement",
    "ProgressPhoto",
    "InjuryRiskAssessment",
    # Phase 9
    "TrainerSession",
    "PoseAnalysisLog",
    "MovementLibraryItem",
    "TrainerAdaptivePlan",
]

