"""
Water intake request and response schemas.
Pydantic v2 syntax.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class WaterCreate(BaseModel):
    """Payload for POST /water.

    Accepts either glasses or liters; at least one must be provided.
    If only glasses is given, liters is derived (1 glass ≈ 0.25 L).
    If only liters is given, glasses is derived.
    """

    glasses: int = Field(default=0, ge=0, description="Number of glasses consumed")
    liters: float = Field(default=0.0, ge=0, description="Volume in litres")

    @model_validator(mode="after")
    def at_least_one_and_derive(self) -> "WaterCreate":
        if self.glasses == 0 and self.liters == 0.0:
            raise ValueError("Provide at least glasses or liters (or both)")
        # Derive whichever is missing
        if self.glasses == 0 and self.liters > 0:
            self.glasses = max(1, round(self.liters / 0.25))
        elif self.liters == 0.0 and self.glasses > 0:
            self.liters = round(self.glasses * 0.25, 3)
        return self

    model_config = {
        "json_schema_extra": {
            "example": {"glasses": 2, "liters": 0.5}
        }
    }


class WaterResponse(BaseModel):
    """Water record returned in responses."""

    id: int
    user_id: int
    glasses: int
    liters: float
    created_at: datetime

    model_config = {"from_attributes": True}
