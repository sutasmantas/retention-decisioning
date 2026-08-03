from typing import Literal

from pydantic import BaseModel, Field


class ScoreRequest(BaseModel):
    account_name: str = Field(min_length=2, max_length=100)
    segment: Literal["Enterprise", "Business", "Growth"] = "Business"
    mrr: float = Field(gt=0, le=500_000)
    seat_change_pct: float = Field(ge=-100, le=100)
    weekly_active_ratio: float = Field(ge=0, le=1)
    priority_tickets: int = Field(ge=0, le=50)
    days_to_renewal: int = Field(ge=0, le=730)
    feature_adoption: float = Field(ge=0, le=1)
    tenure_months: int = Field(ge=1, le=240)
    nps: float = Field(ge=-100, le=100)
    resolution_hours: float = Field(ge=0, le=720)


class PolicyRequest(BaseModel):
    threshold: float = Field(ge=0.45, le=0.80)
    capacity: int = Field(default=50, ge=1, le=500)
