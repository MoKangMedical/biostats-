"""
Statistical analysis endpoints
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.endpoints.users import get_current_user
from app.models.user import User
from app.services.statistics import SurvivalService, SampleSizeService

router = APIRouter()


# Request/Response models
class KaplanMeierRequest(BaseModel):
    time: List[float] = Field(..., description="Time to event")
    event: List[int] = Field(..., description="Event indicator (1=event, 0=censored)")
    confidence_level: float = Field(default=0.95, description="Confidence level")


class KaplanMeierResponse(BaseModel):
    times: List[float]
    survival_prob: List[float]
    confidence_lower: List[float]
    confidence_upper: List[float]
    median_survival: Optional[float]
    events: int
    censored: int


class LogRankRequest(BaseModel):
    time1: List[float] = Field(..., description="Time for group 1")
    event1: List[int] = Field(..., description="Event indicator for group 1")
    time2: List[float] = Field(..., description="Time for group 2")
    event2: List[int] = Field(..., description="Event indicator for group 2")


class LogRankResponse(BaseModel):
    chi2: float
    p_value: float
    significant: bool
    observed_group1: int
    expected_group1: float
    observed_group2: int


class SampleSizeMeansRequest(BaseModel):
    mean1: float = Field(..., description="Mean of group 1")
    mean2: float = Field(..., description="Mean of group 2")
    sd: float = Field(..., description="Standard deviation")
    alpha: float = Field(default=0.05, description="Significance level")
    power: float = Field(default=0.80, description="Statistical power")
    ratio: float = Field(default=1.0, description="Allocation ratio")


class SampleSizeProportionsRequest(BaseModel):
    p1: float = Field(..., description="Proportion in group 1")
    p2: float = Field(..., description="Proportion in group 2")
    alpha: float = Field(default=0.05, description="Significance level")
    power: float = Field(default=0.80, description="Statistical power")
    ratio: float = Field(default=1.0, description="Allocation ratio")


class SampleSizeSurvivalRequest(BaseModel):
    hazard_ratio: float = Field(..., description="Hazard ratio")
    alpha: float = Field(default=0.05, description="Significance level")
    power: float = Field(default=0.80, description="Statistical power")
    prob_event: float = Field(default=0.5, description="Probability of event")
    ratio: float = Field(default=1.0, description="Allocation ratio")


class SampleSizeResponse(BaseModel):
    n_per_group: int
    total_n: int
    power: float
    alpha: float
    effect_size: float


# Endpoints
@router.post("/survival/kaplan-meier", response_model=KaplanMeierResponse)
async def kaplan_meier_analysis(
    request: KaplanMeierRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Perform Kaplan-Meier survival analysis
    
    Calculate survival curve, confidence intervals, and median survival time.
    """
    try:
        result = SurvivalService.kaplan_meier(
            time=request.time,
            event=request.event,
            confidence_level=request.confidence_level
        )
        return KaplanMeierResponse(
            times=result.times,
            survival_prob=result.survival_prob,
            confidence_lower=result.confidence_lower,
            confidence_upper=result.confidence_upper,
            median_survival=result.median_survival,
            events=result.events,
            censored=result.censored
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Analysis error: {str(e)}"
        )


@router.post("/survival/log-rank", response_model=LogRankResponse)
async def log_rank_test(
    request: LogRankRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Perform log-rank test for comparing two survival curves
    
    Tests the null hypothesis that there is no difference between survival curves.
    """
    try:
        result = SurvivalService.log_rank_test(
            time1=request.time1,
            event1=request.event1,
            time2=request.time2,
            event2=request.event2
        )
        return LogRankResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Analysis error: {str(e)}"
        )


@router.post("/sample-size/means", response_model=SampleSizeResponse)
async def sample_size_means(
    request: SampleSizeMeansRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Calculate sample size for comparing two means
    
    Uses the formula for two-sample t-test sample size calculation.
    """
    try:
        result = SampleSizeService.two_means(
            mean1=request.mean1,
            mean2=request.mean2,
            sd=request.sd,
            alpha=request.alpha,
            power=request.power,
            ratio=request.ratio
        )
        return SampleSizeResponse(
            n_per_group=result.n_per_group,
            total_n=result.total_n,
            power=result.power,
            alpha=result.alpha,
            effect_size=result.effect_size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Calculation error: {str(e)}"
        )


@router.post("/sample-size/proportions", response_model=SampleSizeResponse)
async def sample_size_proportions(
    request: SampleSizeProportionsRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Calculate sample size for comparing two proportions
    
    Uses the formula for two-proportion z-test sample size calculation.
    """
    try:
        result = SampleSizeService.two_proportions(
            p1=request.p1,
            p2=request.p2,
            alpha=request.alpha,
            power=request.power,
            ratio=request.ratio
        )
        return SampleSizeResponse(
            n_per_group=result.n_per_group,
            total_n=result.total_n,
            power=result.power,
            alpha=result.alpha,
            effect_size=result.effect_size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Calculation error: {str(e)}"
        )


@router.post("/sample-size/survival", response_model=SampleSizeResponse)
async def sample_size_survival(
    request: SampleSizeSurvivalRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Calculate sample size for survival endpoint
    
    Uses Schoenfeld formula for proportional hazards.
    """
    try:
        result = SampleSizeService.survival(
            hazard_ratio=request.hazard_ratio,
            alpha=request.alpha,
            power=request.power,
            prob_event=request.prob_event,
            ratio=request.ratio
        )
        return SampleSizeResponse(
            n_per_group=result.n_per_group,
            total_n=result.total_n,
            power=result.power,
            alpha=result.alpha,
            effect_size=result.effect_size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Calculation error: {str(e)}"
        )
