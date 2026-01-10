from typing import Optional, Literal
from pydantic import BaseModel, Field


# Pydantic Models
class UserRegister(BaseModel):
    email: str
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=250)


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    username: str
    is_verified: bool


class ChatResponse(BaseModel):
    session_id: str
    response: str
    history: list


class EmailVerificationRequest(BaseModel):
    token: str


class ChatIn(BaseModel):
    message: str
    session_id: str | None = None


class HealthOut(BaseModel):
    status: str
    uptime_seconds: float | None = None


class Extracted(BaseModel):
    location: str
    when: str
    units: Optional[Literal["C", "F"]] = "C"


class FollowUp(BaseModel):
    next_step: str | None = None