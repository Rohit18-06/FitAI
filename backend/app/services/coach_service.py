"""
AI Fitness Coach service for FitAI.
Aggregates the user's complete physiological history and telemetry,
builds high-fidelity context for Gemini AI, and provides an intelligent
rule-based sports science fallback engine for 100% uptime.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.core.config import settings
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
from app.schemas.coach import (
    CoachChatResponse,
    CoachConversationItem,
    ConversationHistoryResponse,
    CoachSidebarStats,
)
from app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class CoachService:
    """Manages personalized AI coaching dialogues and telemetry aggregation."""

    # -------------------------------------------------------------------------
    # 1. Telemetry Collector
    # -------------------------------------------------------------------------
    @classmethod
    def collect_user_data(cls, db: Session, user: User) -> Dict[str, Any]:
        """
        Aggregate complete multi-domain telemetry for the given user.
        Gathers BMI history, calorie intake, workouts, hydration, steps,
        active plans, video analyses, and clinical insights.
        """
        now = _utcnow()
        today_start = datetime(now.year, now.month, now.day)
        seven_days_ago = now - timedelta(days=7)

        # 1. BMI & Body Mass
        latest_bmi = (
            db.query(BMIRecord)
            .filter(BMIRecord.user_id == user.id)
            .order_by(desc(BMIRecord.created_at))
            .first()
        )
        recent_bmis = (
            db.query(BMIRecord)
            .filter(BMIRecord.user_id == user.id)
            .order_by(desc(BMIRecord.created_at))
            .limit(5)
            .all()
        )

        # 2. Calories
        today_calories = (
            db.query(func.coalesce(func.sum(CalorieRecord.calories), 0.0))
            .filter(CalorieRecord.user_id == user.id, CalorieRecord.created_at >= today_start)
            .scalar()
        )
        recent_calories = (
            db.query(CalorieRecord)
            .filter(CalorieRecord.user_id == user.id, CalorieRecord.created_at >= seven_days_ago)
            .order_by(desc(CalorieRecord.created_at))
            .all()
        )
        avg_7d_calories = (
            sum(c.calories for c in recent_calories) / 7.0 if recent_calories else float(today_calories)
        )

        # 3. Water
        today_water = (
            db.query(func.coalesce(func.sum(WaterRecord.liters), 0.0))
            .filter(WaterRecord.user_id == user.id, WaterRecord.created_at >= today_start)
            .scalar()
        )
        recent_water = (
            db.query(WaterRecord)
            .filter(WaterRecord.user_id == user.id, WaterRecord.created_at >= seven_days_ago)
            .all()
        )
        avg_7d_water = sum(w.liters for w in recent_water) / 7.0 if recent_water else float(today_water)

        # 4. Steps
        today_steps = (
            db.query(func.coalesce(func.sum(StepRecord.steps), 0))
            .filter(StepRecord.user_id == user.id, StepRecord.created_at >= today_start)
            .scalar()
        )
        recent_steps = (
            db.query(StepRecord)
            .filter(StepRecord.user_id == user.id, StepRecord.created_at >= seven_days_ago)
            .all()
        )
        avg_7d_steps = sum(s.steps for s in recent_steps) / 7.0 if recent_steps else float(today_steps)

        # 5. Workouts
        today_workout_mins = (
            db.query(func.coalesce(func.sum(WorkoutRecord.duration_minutes), 0))
            .filter(WorkoutRecord.user_id == user.id, WorkoutRecord.created_at >= today_start)
            .scalar()
        )
        recent_workouts = (
            db.query(WorkoutRecord)
            .filter(WorkoutRecord.user_id == user.id, WorkoutRecord.created_at >= seven_days_ago)
            .order_by(desc(WorkoutRecord.created_at))
            .all()
        )
        total_7d_workout_mins = sum(w.duration_minutes for w in recent_workouts)
        workout_types = list({w.workout_type for w in recent_workouts})

        # 6. Active Plans
        active_diet = (
            db.query(DietPlan)
            .filter(DietPlan.user_id == user.id, DietPlan.is_active == True)
            .order_by(desc(DietPlan.created_at))
            .first()
        )
        active_workout = (
            db.query(WorkoutPlan)
            .filter(WorkoutPlan.user_id == user.id, WorkoutPlan.is_active == True)
            .order_by(desc(WorkoutPlan.created_at))
            .first()
        )

        # 7. Video Analysis
        latest_video = (
            db.query(FormAnalysisRecord)
            .filter(FormAnalysisRecord.user_id == user.id)
            .order_by(desc(FormAnalysisRecord.created_at))
            .first()
        )

        # 8. Health Insights
        recent_insights = (
            db.query(HealthInsight)
            .filter(HealthInsight.user_id == user.id)
            .order_by(desc(HealthInsight.created_at))
            .limit(4)
            .all()
        )

        return {
            "username": user.username,
            "email": user.email,
            "latest_bmi": latest_bmi,
            "recent_bmis": recent_bmis,
            "today_calories": float(today_calories),
            "avg_7d_calories": round(float(avg_7d_calories), 1),
            "today_water": round(float(today_water), 2),
            "avg_7d_water": round(float(avg_7d_water), 2),
            "today_steps": int(today_steps),
            "avg_7d_steps": int(avg_7d_steps),
            "today_workout_mins": int(today_workout_mins),
            "total_7d_workout_mins": int(total_7d_workout_mins),
            "workout_count_7d": len(recent_workouts),
            "workout_types": workout_types,
            "active_diet": active_diet,
            "active_workout": active_workout,
            "latest_video": latest_video,
            "recent_insights": recent_insights,
        }

    # -------------------------------------------------------------------------
    # 2. Context Builder & Prompt Generator
    # -------------------------------------------------------------------------
    @classmethod
    def build_ai_context(cls, data: Dict[str, Any]) -> str:
        """Construct structured clinical/athletic context for the LLM."""
        bmi = data.get("latest_bmi")
        diet = data.get("active_diet")
        w_plan = data.get("active_workout")
        video = data.get("latest_video")
        insights = data.get("recent_insights", [])

        bmi_str = (
            f"Weight: {bmi.weight_kg} kg, Height: {bmi.height_cm} cm, BMI: {bmi.bmi:.1f} ({bmi.category})"
            if bmi
            else "No BMI record logged yet (baseline ~70.0 kg assumed)"
        )

        diet_str = (
            f"Plan: '{diet.title}', Goal: {diet.fitness_goal}, Target Calories: {diet.target_calories} kcal, "
            f"Protein: {diet.target_protein_g}g, Carbs: {diet.target_carbs_g}g, Fats: {diet.target_fats_g}g"
            if diet
            else "No formal AI diet plan active"
        )

        workout_plan_str = (
            f"Plan: '{w_plan.title}', Level: {w_plan.fitness_level}, Goal: {w_plan.fitness_goal}, "
            f"Frequency: {w_plan.days_per_week} days/week, Gear: {w_plan.equipment}"
            if w_plan
            else "No formal AI workout plan active"
        )

        video_str = (
            f"Exercise: {video.exercise_name}, Form Score: {video.form_score}/100, Reps: {video.rep_count}, "
            f"Injury Risk: {video.injury_risk_level.upper()}, Posture Critique: '{video.posture_summary}'"
            if video
            else "No computer vision form analyses recorded yet"
        )

        insights_summary = (
            "; ".join(f"[{i.priority.upper()}] {i.title}: {i.content[:80]}..." for i in insights)
            if insights
            else "No active telemetry warning alerts"
        )

        context = f"""
================ USER ATHLETE TELEMETRY PROFILE ================
Athlete Name: {data['username']}

[1. BODY COMPOSITION & BMI]
- Current Status: {bmi_str}
- 5-Day Trend: {', '.join(f'{b.bmi:.1f}' for b in data['recent_bmis']) if data['recent_bmis'] else 'N/A'}

[2. NUTRITION & ENERGY EXPENDITURE]
- Today's Consumed: {data['today_calories']:.0f} kcal
- 7-Day Daily Average: {data['avg_7d_calories']:.0f} kcal/day
- Active Diet Plan: {diet_str}

[3. PHYSICAL TRAINING & EXERCISE]
- Today's Training: {data['today_workout_mins']} minutes
- Past 7 Days Volume: {data['workout_count_7d']} sessions, {data['total_7d_workout_mins']} total minutes
- Logged Disciplines: {', '.join(data['workout_types']) if data['workout_types'] else 'None recently'}
- Active Workout Plan: {workout_plan_str}

[4. HYDRATION & RECOVERY]
- Today's Water: {data['today_water']:.2f} Liters (Guideline: 3.00L)
- 7-Day Average: {data['avg_7d_water']:.2f} Liters/day

[5. DAILY AMBULATORY ACTIVITY (NEAT)]
- Today's Step Count: {data['today_steps']:,} steps (Target: 10,000 steps)
- 7-Day Average: {data['avg_7d_steps']:,} steps/day

[6. COMPUTER VISION BIOMECHANICS]
- Most Recent Assessment: {video_str}

[7. CLINICAL HEALTH INSIGHTS]
- Recent Signals: {insights_summary}
================================================================
"""
        return context.strip()

    @classmethod
    def generate_coach_prompt(cls, user_message: str, context: str) -> str:
        """Compose the comprehensive prompt for Gemini."""
        return f"""You are FitAI's Elite Personal Fitness Coach and Sports Science Specialist.
You combine Olympic-level coaching precision with clinical empathy and actionable clarity.

CRITICAL INSTRUCTIONS:
1. Ground your answer STICTLY in the user's verified telemetry profile below.
2. Cross-reference related physiological systems (e.g. caloric intake vs step volume vs workout frequency).
3. If data is lacking in an area, politely mention what should be logged for higher precision.
4. Structure your response clearly using GitHub Markdown:
   - 📊 **Telemetry Analysis**: Direct breakdown of what their numbers show regarding their question.
   - 💡 **Specific Recommendations**: Tactical biomechanical, dietary, or recovery advice.
   - ⚡ **Action Steps**: Concrete, numbered micro-steps to execute today/this week.
   - ⚠️ **Key Precautions**: Any red flags (e.g. high calorie surplus, dehydration, poor squat depth).

{context}

USER QUESTION:
"{user_message}"

Deliver your response now in an inspiring, authoritative, and direct tone:"""

    # -------------------------------------------------------------------------
    # 3. Gemini Execution
    # -------------------------------------------------------------------------
    @classmethod
    def call_gemini_coach(cls, prompt: str) -> Optional[Tuple[str, int]]:
        """Invoke Gemini 2.5 Flash via google-genai SDK. Returns (response_text, tokens_used)."""
        client = GeminiService.get_client()
        if not client:
            return None

        try:
            from google.genai import types

            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.35,
                    max_output_tokens=1200,
                ),
            )
            if response and response.text and response.text.strip():
                usage = getattr(response, "usage_metadata", None)
                total_tokens = getattr(usage, "total_token_count", 0) if usage else 380
                return response.text.strip(), total_tokens
        except Exception as exc:
            logger.warning("Gemini Coach API call failed: %s. Using expert fallback engine.", exc)

        return None

    # -------------------------------------------------------------------------
    # 4. Intelligent Rule-Based Fallback Reasoning Engine
    # -------------------------------------------------------------------------
    @classmethod
    def fallback_reasoning_engine(cls, user_message: str, data: Dict[str, Any]) -> Tuple[str, List[str]]:
        """
        Expert physiological reasoning engine that analyzes exact telemetry
        when Gemini API is unreachable or rate-limited. NEVER FAILS.
        """
        msg_lower = user_message.lower()
        sources: List[str] = []

        bmi = data.get("latest_bmi")
        diet = data.get("active_diet")
        cal_today = data.get("today_calories", 0.0)
        cal_avg = data.get("avg_7d_calories", 2000.0)
        target_cals = diet.target_calories if diet else 2200.0
        water_today = data.get("today_water", 0.0)
        water_avg = data.get("avg_7d_water", 2.0)
        steps_today = data.get("today_steps", 0)
        steps_avg = data.get("avg_7d_steps", 6000)
        w_mins_7d = data.get("total_7d_workout_mins", 0)
        w_count_7d = data.get("workout_count_7d", 0)
        video = data.get("latest_video")

        # -------------------------------------------------------------
        # Scenario A: Weight Loss / Fat Loss / "Why am I not losing weight"
        # -------------------------------------------------------------
        if any(w in msg_lower for w in ["weight", "fat", "lose", "losing", "deficit", "scale"]):
            sources = ["bmi", "calories", "steps", "workouts"]
            cal_diff = cal_avg - target_cals
            surplus_text = (
                f"Your 7-day average intake is **{cal_avg:.0f} kcal**, which is **{abs(cal_diff):.0f} kcal above** your target ({target_cals:.0f} kcal)."
                if cal_diff > 50
                else f"Your average daily intake (**{cal_avg:.0f} kcal**) is close to your target ({target_cals:.0f} kcal), indicating energy balance maintenance."
            )
            step_text = (
                f"Daily ambulatory steps average **{steps_avg:,}**, below the metabolic threshold of 10,000 steps."
                if steps_avg < 8000
                else f"Your step activity (**{steps_avg:,} avg**) provides solid non-exercise activity thermogenesis (NEAT)."
            )

            response = f"""### 📊 Telemetry Analysis: Energy Balance & Body Mass Dynamics
Examining your telemetry logs:
- **Caloric Balance**: {surplus_text}
- **NEAT Movement**: {step_text}
- **Training Frequency**: Logged **{w_count_7d} sessions ({w_mins_7d} total minutes)** over the past 7 days.
- **Current BMI**: {f"{bmi.bmi:.1f} ({bmi.category}) at {bmi.weight_kg} kg" if bmi else "Baseline ~70kg recorded"}.

### 💡 Specific Recommendations
1. **Enforce a Strict 300–400 kcal Deficit**: If weight loss has plateaued, tighten intake tracking—hidden cooking oils and liquid calories often offset margins.
2. **Elevate Baseline NEAT to 10,000 Steps**: Ambulation accounts for up to 15% of total daily energy expenditure, vastly outlasting isolated gym workouts.
3. **Prioritize Protein Intake (1.8g–2.2g/kg)**: High protein protects lean muscle mass in a deficit and induces a superior thermic effect of food (TEF).

### ⚡ Action Steps
1. Log all meals and snacks before eating to verify they fit inside the **{target_cals:.0f} kcal** budget today.
2. Add a brisk 20-minute post-meal walk today to bridge your steps from **{steps_today:,}** toward 10,000.
3. Schedule at least 3 structured resistance training sessions this week to prevent metabolic slowdown.

### ⚠️ Key Precautions
- Avoid extreme crash deficits (>700 kcal) which suppress thyroid output (T3) and degrade metabolic rate.
- Daily scale weight can fluctuate 1–2 kg due to sodium and glycogen water retention; rely on weekly trendlines."""

        # -------------------------------------------------------------
        # Scenario B: Hydration & Water Intake
        # -------------------------------------------------------------
        elif any(w in msg_lower for w in ["water", "hydrat", "drink", "fluid", "thirst"]):
            sources = ["water", "workouts", "insights"]
            deficit_liters = max(0.0, 3.0 - water_today)
            response = f"""### 📊 Telemetry Analysis: Cellular Hydration Status
Reviewing your fluid telemetry:
- **Today's Consumption**: Logged **{water_today:.2f} L** out of the **3.00 L** clinical target (**{deficit_liters:.2f} L remaining**).
- **7-Day Rolling Average**: **{water_avg:.2f} L/day**.
- **Exercise Exertion**: You logged **{data['today_workout_mins']} workout minutes** today, which induces acute electrolyte and water transpiration.

### 💡 Specific Recommendations
1. **Front-Load Hydration Upon Waking**: Drink 500 mL immediately after waking to counter nocturnal respiratory dehydration.
2. **Per-Workout Fluid Replacement**: Ingest 250 mL of water with sodium/potassium electrolytes for every 30 minutes of vigorous training.
3. **Glycogen Osmosis**: Every gram of muscle glycogen requires ~3 grams of cellular water for optimal muscular torque output.

### ⚡ Action Steps
1. Drink two large glasses (~500 mL) within the next hour to bridge your current level of **{water_today:.2f} L**.
2. Keep a 1-liter container at your workstation as a visual consumption anchor.
3. Track each intake via the dashboard quick-log (`+ Water`) button.

### ⚠️ Key Precautions
- Mild dehydration of just 2% of body weight reduces maximal anaerobic strength by up to 10% and elevates perceived exertion."""

        # -------------------------------------------------------------
        # Scenario C: Workouts, Strength & Muscle Gain
        # -------------------------------------------------------------
        elif any(w in msg_lower for w in ["workout", "muscle", "strength", "train", "gym", "hypertrophy", "plan"]):
            sources = ["workouts", "workout_plan", "video"]
            plan_name = data["active_workout"].title if data["active_workout"] else "Standard Periodization"
            video_note = (
                f"- **Video Form Check**: Your recent {video.exercise_name} score was **{video.form_score}/100** with **{video.injury_risk_level.upper()}** risk profile."
                if video
                else "- **Form Quality**: Remember to run a video form check on compound lifts via the Video Analyzer."
            )

            response = f"""### 📊 Telemetry Analysis: Training Stimulus & Mechanical Load
Evaluating your muscular stimulation metrics:
- **Recent Volume**: **{w_count_7d} workouts ({w_mins_7d} minutes total)** across the past week.
- **Active Program**: **{plan_name}**.
{video_note}

### 💡 Specific Recommendations
1. **Mechanical Tension Over Volume**: Ensure primary compound sets are taken to 1–2 Repetitions in Reserve (RIR) to recruit high-threshold motor units.
2. **Progressive Overload Tracking**: Increase either load by 1.25–2.5 kg or reps by 1–2 every session on key lifts.
3. **Inter-Set Rest Intervals**: Rest 2.5–3.5 minutes on multi-joint lifts (Squat, Deadlift, Press) to enable complete ATP-CP resynthesis.

### ⚡ Action Steps
1. Review the daily routine in your active workout plan before your next session.
2. Log precise sets and reps in your workout tracker to ensure overload progression.
3. Use the **Multimodal Video Analyzer** on your heaviest set to verify bar path and joint symmetry.

### ⚠️ Key Precautions
- Adding excessive volume when under-slept or under-fueled increases systemic inflammation without additional myofibrillar synthesis."""

        # -------------------------------------------------------------
        # Scenario D: BMI Increasing / Body Composition
        # -------------------------------------------------------------
        elif any(w in msg_lower for w in ["bmi", "increasing", "gain", "mass", "bulk"]):
            sources = ["bmi", "calories", "workouts"]
            response = f"""### 📊 Telemetry Analysis: BMI Trajectory & Tissue Adaptation
- **Current BMI Reading**: {f"{bmi.bmi:.1f} ({bmi.category}) at {bmi.weight_kg} kg" if bmi else "Pending initial weigh-in"}.
- **Caloric Environment**: Consuming **{cal_avg:.0f} kcal/day** on average against target **{target_cals:.0f} kcal**.
- **Resistance Training**: **{w_count_7d} sessions** logged over 7 days.

### 💡 Specific Recommendations
1. **Distinguish Hypertrophy from Adiposity**: If BMI is increasing while strength is rising and waist circumference is static, the gain is primarily functional lean mass and glycogen storage.
2. **Calibrate Caloric Surplus**: For lean bulking, a modest surplus of only 200–250 kcal/day is optimal to minimize unwanted adipose accretion.
3. **Cardiovascular Conditioning**: Maintain at least 8,000–10,000 daily steps even during a mass phase to preserve insulin sensitivity.

### ⚡ Action Steps
1. Measure waist circumference at the umbilicus weekly alongside scale measurements.
2. Cap daily intake at **{target_cals + 250:.0f} kcal** to prevent rapid spillover into fat stores.
3. Continue progressive overload on your core resistance routine.

### ⚠️ Key Precautions
- BMI does not isolate skeletal muscle from adipose tissue. Athletes with high muscularity frequently score as 'Overweight' on raw BMI scales."""

        # -------------------------------------------------------------
        # Scenario E: Holistic Comprehensive Review / Default
        # -------------------------------------------------------------
        else:
            sources = ["bmi", "calories", "workouts", "water", "steps"]
            response = f"""### 📊 Telemetry Analysis: Holistic Biological Status
Here is your current fitness system overview:
- **Body Mass**: {f"BMI {bmi.bmi:.1f} ({bmi.category}), {bmi.weight_kg} kg" if bmi else "No recent weigh-in"}.
- **Nutrition**: Today's calories at **{cal_today:.0f} kcal** (7d avg: **{cal_avg:.0f} kcal** vs **{target_cals:.0f} target**).
- **Hydration**: **{water_today:.2f} L** logged today (7d avg: **{water_avg:.2f} L**).
- **Daily Movement**: **{steps_today:,} steps** today (7d avg: **{steps_avg:,} steps**).
- **Resistance Training**: **{w_count_7d} workouts** logged in the past week (**{w_mins_7d} min**).

### 💡 Specific Recommendations
1. **Tighten Consistency Across All 4 Pillars**: Nutrition, hydration, progressive resistance, and daily ambulation compound exponentially.
2. **Prioritize Your Lagging Pillar**: {"Hydration is below the 3.0L threshold." if water_today < 2.5 else "Keep up your strong hydration cadence."}
3. **Sleep & Recovery**: Aim for 7.5–8.5 hours of uninterrupted sleep to maximize growth hormone release and central nervous system recovery.

### ⚡ Action Steps
1. Complete remaining hydration to reach your **3.00 L** daily milestone.
2. Hit your target step count by taking a short walk this evening.
3. Prepare tomorrow's meals in alignment with your active nutrition plan.

### ⚠️ Key Precautions
- Consistency on 85% of days beats sporadic 100% efforts. Focus on sustainable, repeatable daily systems."""

        return response.strip(), sources

    # -------------------------------------------------------------------------
    # 5. Core Chat Handler
    # -------------------------------------------------------------------------
    @classmethod
    def process_chat_message(
        cls, db: Session, user: User, message: str
    ) -> CoachChatResponse:
        """
        Processes a chat request:
        1. Gathers full user telemetry
        2. Builds context
        3. Attempts Gemini call (gemini-2.5-flash)
        4. Seamlessly falls back to sports science reasoning engine if needed
        5. Persists turn to database
        6. Returns structured response
        """
        # 1. Collect telemetry
        telemetry = cls.collect_user_data(db, user)

        # 2. Build context
        context = cls.build_ai_context(telemetry)

        # 3. Detect telemetry sources
        sources: List[str] = ["user_profile"]
        if telemetry.get("latest_bmi"):
            sources.append("bmi")
        if telemetry.get("today_calories") or telemetry.get("avg_7d_calories"):
            sources.append("calories")
        if telemetry.get("workout_count_7d") > 0:
            sources.append("workouts")
        if telemetry.get("today_water") > 0:
            sources.append("water")
        if telemetry.get("today_steps") > 0:
            sources.append("steps")
        if telemetry.get("active_diet"):
            sources.append("diet_plan")
        if telemetry.get("active_workout"):
            sources.append("workout_plan")
        if telemetry.get("latest_video"):
            sources.append("video_biomechanics")
        if telemetry.get("recent_insights"):
            sources.append("health_insights")

        # 4. Generate prompt & attempt Gemini
        prompt = cls.generate_coach_prompt(message, context)
        gemini_result = cls.call_gemini_coach(prompt)

        if gemini_result is not None:
            response_text, tokens_used = gemini_result
        else:
            # Intelligent fallback reasoning
            response_text, specific_sources = cls.fallback_reasoning_engine(message, telemetry)
            tokens_used = len(response_text.split()) + len(prompt.split())
            if specific_sources:
                sources = list(set(sources + specific_sources))

        # 5. Save conversation
        conversation = CoachConversation(
            user_id=user.id,
            message=message,
            response=response_text,
            sources=",".join(sources),
            tokens_used=tokens_used,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        return CoachChatResponse(
            id=conversation.id,
            message=conversation.message,
            response=conversation.response,
            sources=[s.strip() for s in conversation.sources.split(",") if s.strip()],
            tokens_used=conversation.tokens_used,
            created_at=conversation.created_at,
        )

    # -------------------------------------------------------------------------
    # 6. Conversation History Management
    # -------------------------------------------------------------------------
    @classmethod
    def get_conversation_history(
        cls, db: Session, user: User, limit: int = 30, offset: int = 0
    ) -> ConversationHistoryResponse:
        """Fetch past conversation turns for the user."""
        query = db.query(CoachConversation).filter(CoachConversation.user_id == user.id)
        total = query.count()

        records = (
            query.order_by(CoachConversation.created_at.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        items = [
            CoachConversationItem(
                id=r.id,
                user_id=r.user_id,
                message=r.message,
                response=r.response,
                sources=[s.strip() for s in r.sources.split(",") if s.strip()],
                tokens_used=r.tokens_used,
                created_at=r.created_at,
            )
            for r in records
        ]

        return ConversationHistoryResponse(conversations=items, total=total)

    @classmethod
    def clear_conversation_history(cls, db: Session, user: User) -> int:
        """Clear all conversation history for the user."""
        count = (
            db.query(CoachConversation)
            .filter(CoachConversation.user_id == user.id)
            .delete(synchronize_session=False)
        )
        db.commit()
        return count

    # -------------------------------------------------------------------------
    # 7. Sidebar Telemetry
    # -------------------------------------------------------------------------
    @classmethod
    def get_sidebar_stats(cls, db: Session, user: User) -> CoachSidebarStats:
        """Compute quick metrics for the coach interface sidebar."""
        telemetry = cls.collect_user_data(db, user)
        bmi = telemetry.get("latest_bmi")
        diet = telemetry.get("active_diet")
        w_plan = telemetry.get("active_workout")

        # Determine streak based on recent workouts/steps
        streak = min(7, telemetry.get("workout_count_7d", 0) + (1 if telemetry.get("today_steps", 0) > 6000 else 0))

        return CoachSidebarStats(
            bmi=bmi.bmi if bmi else None,
            bmi_category=bmi.category if bmi else None,
            weight_kg=bmi.weight_kg if bmi else None,
            calories_today=telemetry.get("today_calories", 0.0),
            calorie_target=diet.target_calories if diet else 2400.0,
            water_liters_today=telemetry.get("today_water", 0.0),
            water_target=3.0,
            steps_today=telemetry.get("today_steps", 0),
            step_target=10000,
            workout_minutes_today=telemetry.get("today_workout_mins", 0),
            current_streak=max(1, streak),
            active_diet_plan=diet.title if diet else None,
            active_workout_plan=w_plan.title if w_plan else None,
        )
