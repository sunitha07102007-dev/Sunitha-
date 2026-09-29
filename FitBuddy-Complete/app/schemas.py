from typing import Literal
from pydantic import BaseModel, Field, field_validator

Goal = Literal["weight loss", "muscle gain", "general wellness", "flexibility", "endurance"]
Intensity = Literal["low", "medium", "high"]

class UserInput(BaseModel):
    user_id: str = Field(min_length=2, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    name: str = Field(min_length=2, max_length=100)
    age: int = Field(default=13, ge=13, le=100)
    weight: float = Field(default=20, ge=20, le=300)
    goal: Goal
    intensity: Intensity

    @field_validator("name")
    @classmethod
    def clean_name(cls, value):
        return " ".join(value.strip().split())

class FeedbackRequest(BaseModel):
    user_id: str = Field(min_length=2, max_length=64)
    feedback: str = Field(min_length=3, max_length=1000)
