"""
Pydantic schemas for API request/response validation
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int
    subscription_tier: str
    analyses_this_month: int
    monthly_limit: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Auth schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


# Analysis schemas
class AnalysisBase(BaseModel):
    analysis_type: str
    parameters: Dict[str, Any]


class AnalysisCreate(AnalysisBase):
    upload_id: Optional[int] = None


class AnalysisResponse(AnalysisBase):
    id: int
    user_id: int
    status: str
    results: Optional[Dict[str, Any]] = None
    interpretation: Optional[str] = None
    execution_time: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Survival analysis schemas
class SurvivalAnalysisRequest(BaseModel):
    time: List[float] = Field(..., description="Time to event")
    event: List[int] = Field(..., description="Event indicator (1=event, 0=censored)")
    group: Optional[List[str]] = None
    method: str = Field(default="kaplan_meier", description="Method: kaplan_meier, cox, fine_gray")


class SampleSizeRequest(BaseModel):
    design: str = Field(..., description="Trial design: superiority, non_inferiority, equivalence")
    endpoint: str = Field(..., description="Endpoint type: continuous, binary, survival")
    alpha: float = Field(default=0.05, description="Significance level")
    power: float = Field(default=0.80, description="Statistical power")
    params: Dict[str, Any] = Field(..., description="Design-specific parameters")


# Upload schemas
class UploadResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    rows: int
    columns: int
    column_names: List[str]
    uploaded_at: datetime

    class Config:
        from_attributes = True


# Pagination
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    pages: int
