"""Validation utilities for input validation."""

import re
from typing import Tuple


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password strength.
    
    Requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
    
    Args:
        password: The password to validate.
        
    Returns:
        Tuple of (is_valid, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"


def validate_email_format(email: str) -> bool:
    """
    Validate email format using regex.
    
    Args:
        email: The email to validate.
        
    Returns:
        True if email format is valid, False otherwise.
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_bmi_inputs(height_cm: float, weight_kg: float) -> Tuple[bool, str]:
    """
    Validate BMI calculation inputs.
    
    Args:
        height_cm: Height in centimeters.
        weight_kg: Weight in kilograms.
        
    Returns:
        Tuple of (is_valid, message)
    """
    if height_cm <= 0:
        return False, "Height must be positive"
    
    if weight_kg <= 0:
        return False, "Weight must be positive"
    
    if height_cm < 50:
        return False, "Height seems too low (minimum 50cm)"
    
    if height_cm > 250:
        return False, "Height seems too high (maximum 250cm)"
    
    if weight_kg < 20:
        return False, "Weight seems too low (minimum 20kg)"
    
    if weight_kg > 500:
        return False, "Weight seems too high (maximum 500kg)"
    
    return True, "Valid BMI inputs"
