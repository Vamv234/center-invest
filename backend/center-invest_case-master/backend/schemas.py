"""Pydantic schemas for request/response validation"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ============ User Schemas ============

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str = Field(..., max_length=128, min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    access_token: Optional[str] = None
    token_type: Optional[str] = "bearer"
    
    class Config:
        from_attributes = True


# ============ Scenario Schemas ============

class AttackChoice(BaseModel):
    id: int
    text: str
    is_safe: bool
    consequence: str


class AttackStep(BaseModel):
    id: int
    title: str
    description: str
    image_url: Optional[str] = None
    choices: List[AttackChoice]


class AttackScenarioResponse(BaseModel):
    id: int
    title: str
    description: str
    context: str
    attack_type: str
    difficulty: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AttackScenarioDetailResponse(BaseModel):
    id: int
    title: str
    description: str
    context: str
    attack_type: str
    difficulty: str
    attack_steps: List[dict]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Progress Schemas ============

class StartScenarioRequest(BaseModel):
    scenario_id: int


class UserProgressResponse(BaseModel):
    id: int
    user_id: int
    scenario_id: int
    status: str
    security_level: int
    correct_choices: int
    total_choices: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ChoiceSubmission(BaseModel):
    step_id: int
    choice_id: int
    is_final: bool = False


class ChoiceResultResponse(BaseModel):
    is_correct: bool
    explanation: str
    security_level: int
    total_choices: int
    correct_choices: int
    accuracy: float


class UserStatsResponse(BaseModel):
    total_scenarios_completed: int
    total_scenarios_attempted: int
    average_security_level: float
    total_correct_choices: int
    total_choices: int
    accuracy: float
    certificates_earned: int
    rank: str


# ============ Certificate Schemas ============

class CertificateResponse(BaseModel):
    id: int
    user_id: int
    scenario_id: int
    achievement: str
    qr_code: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
