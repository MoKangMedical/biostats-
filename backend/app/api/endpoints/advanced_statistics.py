"""
Advanced statistical analysis endpoints
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.endpoints.users import get_current_user
from app.models.user import User
from app.services.advanced_statistics import (
    MetaAnalysisService,
    BayesianService,
    HypothesisTestService
)

router = APIRouter()


# Request/Response models
class MetaAnalysisRequest(BaseModel):
    effects: List[float] = Field(..., description="Effect sizes from each study")
    se: List[float] = Field(..., description="Standard errors from each study")
    method: str = Field(default="fixed", description="Method: fixed or random")


class MetaAnalysisResponse(BaseModel):
    pooled_effect: float
    pooled_se: float
    ci_lower: float
    ci_upper: float
    heterogeneity: Dict[str, float]
    studies: List[Dict[str, Any]]


class BayesianBinomialRequest(BaseModel):
    successes: int = Field(..., description="Number of successes")
    trials: int = Field(..., description="Number of trials")
    prior_alpha: float = Field(default=1.0, description="Prior alpha parameter")
    prior_beta: float = Field(default=1.0, description="Prior beta parameter")


class BayesianNormalRequest(BaseModel):
    data_mean: float = Field(..., description="Sample mean")
    data_sd: float = Field(..., description="Sample standard deviation")
    n: int = Field(..., description="Sample size")
    prior_mean: float = Field(default=0.0, description="Prior mean")
    prior_sd: float = Field(default=1.0, description="Prior standard deviation")


class BayesianResponse(BaseModel):
    posterior_mean: float
    posterior_sd: float
    credible_lower: float
    credible_upper: float
    prior_mean: float
    prior_sd: float


class TTestRequest(BaseModel):
    group1: List[float] = Field(..., description="First group data")
    group2: List[float] = Field(..., description="Second group data")
    alternative: str = Field(default="two-sided", description="Alternative hypothesis")


class ChiSquareRequest(BaseModel):
    observed: List[List[int]] = Field(..., description="Observed frequency table")


class MannWhitneyRequest(BaseModel):
    group1: List[float] = Field(..., description="First group data")
    group2: List[float] = Field(..., description="Second group data")
    alternative: str = Field(default="two-sided", description="Alternative hypothesis")


class HypothesisTestResponse(BaseModel):
    test_statistic: float
    p_value: float
    significant: bool
    effect_size: Optional[float]
    confidence_interval: Optional[Dict[str, float]]


# Endpoints
@router.post("/meta-analysis", response_model=MetaAnalysisResponse)
async def meta_analysis(
    request: MetaAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Perform meta-analysis
    
    Combine results from multiple studies using fixed or random effects model.
    """
    try:
        if len(request.effects) != len(request.se):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Effects and standard errors must have the same length"
            )
        
        if len(request.effects) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least 2 studies required for meta-analysis"
            )
        
        if request.method == "fixed":
            result = MetaAnalysisService.fixed_effects(
                effects=request.effects,
                se=request.se
            )
        elif request.method == "random":
            result = MetaAnalysisService.random_effects(
                effects=request.effects,
                se=request.se
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Method must be 'fixed' or 'random'"
            )
        
        return MetaAnalysisResponse(
            pooled_effect=result.pooled_effect,
            pooled_se=result.pooled_se,
            ci_lower=result.ci_lower,
            ci_upper=result.ci_upper,
            heterogeneity=result.heterogeneity,
            studies=result.studies
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Analysis error: {str(e)}"
        )


@router.post("/bayesian/binomial", response_model=BayesianResponse)
async def bayesian_binomial(
    request: BayesianBinomialRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Beta-Binomial conjugate analysis
    
    Update prior beliefs about a proportion using observed data.
    """
    try:
        result = BayesianService.beta_binomial(
            successes=request.successes,
            trials=request.trials,
            prior_alpha=request.prior_alpha,
            prior_beta=request.prior_beta
        )
        return BayesianResponse(
            posterior_mean=result.posterior_mean,
            posterior_sd=result.posterior_sd,
            credible_lower=result.credible_lower,
            credible_upper=result.credible_upper,
            prior_mean=result.prior_mean,
            prior_sd=result.prior_sd
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Analysis error: {str(e)}"
        )


@router.post("/bayesian/normal", response_model=BayesianResponse)
async def bayesian_normal(
    request: BayesianNormalRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Normal-Normal conjugate analysis
    
    Update prior beliefs about a mean using observed data.
    """
    try:
        result = BayesianService.normal_normal(
            data_mean=request.data_mean,
            data_sd=request.data_sd,
            n=request.n,
            prior_mean=request.prior_mean,
            prior_sd=request.prior_sd
        )
        return BayesianResponse(
            posterior_mean=result.posterior_mean,
            posterior_sd=result.posterior_sd,
            credible_lower=result.credible_lower,
            credible_upper=result.credible_upper,
            prior_mean=result.prior_mean,
            prior_sd=result.prior_sd
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Analysis error: {str(e)}"
        )


@router.post("/hypothesis/t-test", response_model=HypothesisTestResponse)
async def t_test(
    request: TTestRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Two-sample t-test
    
    Compare means between two independent groups.
    """
    try:
        result = HypothesisTestService.t_test_two_samples(
            group1=request.group1,
            group2=request.group2,
            alternative=request.alternative
        )
        return HypothesisTestResponse(
            test_statistic=result.test_statistic,
            p_value=result.p_value,
            significant=result.significant,
            effect_size=result.effect_size,
            confidence_interval=result.confidence_interval
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Analysis error: {str(e)}"
        )


@router.post("/hypothesis/chi-square", response_model=HypothesisTestResponse)
async def chi_square_test(
    request: ChiSquareRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Chi-square test of independence
    
    Test association between two categorical variables.
    """
    try:
        result = HypothesisTestService.chi_square_test(
            observed=request.observed
        )
        return HypothesisTestResponse(
            test_statistic=result.test_statistic,
            p_value=result.p_value,
            significant=result.significant,
            effect_size=result.effect_size,
            confidence_interval=result.confidence_interval
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Analysis error: {str(e)}"
        )


@router.post("/hypothesis/mann-whitney", response_model=HypothesisTestResponse)
async def mann_whitney_test(
    request: MannWhitneyRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Mann-Whitney U test (non-parametric)
    
    Compare distributions between two independent groups.
    """
    try:
        result = HypothesisTestService.mann_whitney_test(
            group1=request.group1,
            group2=request.group2,
            alternative=request.alternative
        )
        return HypothesisTestResponse(
            test_statistic=result.test_statistic,
            p_value=result.p_value,
            significant=result.significant,
            effect_size=result.effect_size,
            confidence_interval=result.confidence_interval
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Analysis error: {str(e)}"
        )
