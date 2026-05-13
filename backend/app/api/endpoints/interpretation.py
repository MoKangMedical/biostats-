"""
AI interpretation endpoints
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.endpoints.users import get_current_user
from app.models.user import User
from app.services.interpretation import InterpretationService

router = APIRouter()


# Request/Response models
class SurvivalInterpretationRequest(BaseModel):
    median_survival: Optional[float] = Field(None, description="Median survival time")
    events: int = Field(..., description="Number of events")
    censored: int = Field(..., description="Number of censored observations")
    log_rank_p: Optional[float] = Field(None, description="Log-rank test p-value")


class SampleSizeInterpretationRequest(BaseModel):
    n_per_group: int = Field(..., description="Sample size per group")
    total_n: int = Field(..., description="Total sample size")
    power: float = Field(..., description="Statistical power")
    alpha: float = Field(..., description="Significance level")
    effect_size: float = Field(..., description="Effect size")


class MetaAnalysisInterpretationRequest(BaseModel):
    pooled_effect: float = Field(..., description="Pooled effect size")
    ci_lower: float = Field(..., description="Lower confidence bound")
    ci_upper: float = Field(..., description="Upper confidence bound")
    heterogeneity: Dict[str, float] = Field(..., description="Heterogeneity statistics")
    n_studies: int = Field(..., description="Number of studies")


class HypothesisTestInterpretationRequest(BaseModel):
    test_name: str = Field(..., description="Name of the test")
    test_statistic: float = Field(..., description="Test statistic")
    p_value: float = Field(..., description="P-value")
    effect_size: Optional[float] = Field(None, description="Effect size")
    significant: bool = Field(..., description="Whether result is significant")


class BayesianInterpretationRequest(BaseModel):
    posterior_mean: float = Field(..., description="Posterior mean")
    posterior_sd: float = Field(..., description="Posterior standard deviation")
    credible_lower: float = Field(..., description="Lower credible bound")
    credible_upper: float = Field(..., description="Upper credible bound")
    prior_mean: float = Field(..., description="Prior mean")
    prior_sd: float = Field(..., description="Prior standard deviation")


class InterpretationResponse(BaseModel):
    interpretation: str


# Endpoints
@router.post("/survival", response_model=InterpretationResponse)
async def interpret_survival(
    request: SurvivalInterpretationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate plain-language interpretation of survival analysis results
    """
    try:
        interpretation = InterpretationService.interpret_survival_analysis(
            median_survival=request.median_survival,
            events=request.events,
            censored=request.censored,
            log_rank_p=request.log_rank_p
        )
        return InterpretationResponse(interpretation=interpretation)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Interpretation error: {str(e)}"
        )


@router.post("/sample-size", response_model=InterpretationResponse)
async def interpret_sample_size(
    request: SampleSizeInterpretationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate plain-language interpretation of sample size calculation
    """
    try:
        interpretation = InterpretationService.interpret_sample_size(
            n_per_group=request.n_per_group,
            total_n=request.total_n,
            power=request.power,
            alpha=request.alpha,
            effect_size=request.effect_size
        )
        return InterpretationResponse(interpretation=interpretation)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Interpretation error: {str(e)}"
        )


@router.post("/meta-analysis", response_model=InterpretationResponse)
async def interpret_meta_analysis(
    request: MetaAnalysisInterpretationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate plain-language interpretation of meta-analysis results
    """
    try:
        interpretation = InterpretationService.interpret_meta_analysis(
            pooled_effect=request.pooled_effect,
            ci_lower=request.ci_lower,
            ci_upper=request.ci_upper,
            heterogeneity=request.heterogeneity,
            n_studies=request.n_studies
        )
        return InterpretationResponse(interpretation=interpretation)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Interpretation error: {str(e)}"
        )


@router.post("/hypothesis-test", response_model=InterpretationResponse)
async def interpret_hypothesis_test(
    request: HypothesisTestInterpretationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate plain-language interpretation of hypothesis test results
    """
    try:
        interpretation = InterpretationService.interpret_hypothesis_test(
            test_name=request.test_name,
            test_statistic=request.test_statistic,
            p_value=request.p_value,
            effect_size=request.effect_size,
            significant=request.significant
        )
        return InterpretationResponse(interpretation=interpretation)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Interpretation error: {str(e)}"
        )


@router.post("/bayesian", response_model=InterpretationResponse)
async def interpret_bayesian(
    request: BayesianInterpretationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate plain-language interpretation of Bayesian analysis results
    """
    try:
        interpretation = InterpretationService.interpret_bayesian(
            posterior_mean=request.posterior_mean,
            posterior_sd=request.posterior_sd,
            credible_lower=request.credible_lower,
            credible_upper=request.credible_upper,
            prior_mean=request.prior_mean,
            prior_sd=request.prior_sd
        )
        return InterpretationResponse(interpretation=interpretation)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Interpretation error: {str(e)}"
        )
