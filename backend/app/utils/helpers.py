"""Helper utility functions."""

from __future__ import annotations


def calculate_bmi(height_cm: float, weight_kg: float) -> float:
    """
    Calculate BMI (Body Mass Index).

    Formula: BMI = weight_kg / (height_m ^ 2)

    Args:
        height_cm: Height in centimeters.
        weight_kg: Weight in kilograms.

    Returns:
        Calculated BMI value (rounded to 2 decimal places).
    """
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2)


def get_bmi_category(bmi: float) -> str:
    """
    Get BMI category based on BMI value.

    Categories:
        - Underweight: BMI < 18.5
        - Normal:      18.5 <= BMI < 25
        - Overweight:  25 <= BMI < 30
        - Obese:       BMI >= 30

    Args:
        bmi: The BMI value.

    Returns:
        BMI category as string.
    """
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


def get_bmi_recommendation(bmi: float) -> str:
    """
    Get health recommendation based on BMI.

    Args:
        bmi: The BMI value.

    Returns:
        Health recommendation string.
    """
    category = get_bmi_category(bmi)

    recommendations = {
        "Underweight": "Consider consulting a healthcare professional for personalized nutrition advice.",
        "Normal": "Maintain your healthy weight through balanced diet and regular exercise.",
        "Overweight": "Consider increasing physical activity and reviewing your diet for better health.",
        "Obese": "Consult a healthcare professional for a personalized weight management plan.",
    }

    return recommendations.get(category, "Unknown category")


def format_response(success: bool, message: str, data: dict | None = None) -> dict:
    """
    Format API response in standardized format.

    Args:
        success: Whether the operation was successful.
        message: Response message.
        data: Optional data payload.

    Returns:
        Formatted response dictionary.
    """
    return {
        "success": success,
        "message": message,
        "data": data or {},
    }
