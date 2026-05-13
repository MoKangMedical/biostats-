"""
Visualization endpoints
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.endpoints.users import get_current_user
from app.models.user import User
from app.services.visualization import VisualizationService

router = APIRouter()


# Request/Response models
class SurvivalCurveRequest(BaseModel):
    times: List[float] = Field(..., description="Time points")
    survival_prob: List[float] = Field(..., description="Survival probabilities")
    confidence_lower: Optional[List[float]] = Field(None, description="Lower confidence bound")
    confidence_upper: Optional[List[float]] = Field(None, description="Upper confidence bound")
    title: str = Field(default="Kaplan-Meier Survival Curve", description="Plot title")


class ForestPlotRequest(BaseModel):
    effects: List[float] = Field(..., description="Effect sizes")
    ci_lower: List[float] = Field(..., description="Lower confidence bounds")
    ci_upper: List[float] = Field(..., description="Upper confidence bounds")
    labels: List[str] = Field(..., description="Study labels")
    weights: Optional[List[float]] = Field(None, description="Study weights")
    pooled_effect: Optional[float] = Field(None, description="Pooled effect size")
    pooled_ci_lower: Optional[float] = Field(None, description="Pooled lower CI")
    pooled_ci_upper: Optional[float] = Field(None, description="Pooled upper CI")
    title: str = Field(default="Forest Plot", description="Plot title")


class FunnelPlotRequest(BaseModel):
    effects: List[float] = Field(..., description="Effect sizes")
    se: List[float] = Field(..., description="Standard errors")
    title: str = Field(default="Funnel Plot", description="Plot title")


class HistogramRequest(BaseModel):
    data: List[float] = Field(..., description="Data values")
    title: str = Field(default="Histogram", description="Plot title")
    xlabel: str = Field(default="Value", description="X-axis label")
    ylabel: str = Field(default="Frequency", description="Y-axis label")
    bins: int = Field(default=20, description="Number of bins")


class BoxplotRequest(BaseModel):
    groups: List[List[float]] = Field(..., description="Data groups")
    labels: List[str] = Field(..., description="Group labels")
    title: str = Field(default="Box Plot", description="Plot title")
    ylabel: str = Field(default="Value", description="Y-axis label")


class ScatterPlotRequest(BaseModel):
    x: List[float] = Field(..., description="X values")
    y: List[float] = Field(..., description="Y values")
    title: str = Field(default="Scatter Plot", description="Plot title")
    xlabel: str = Field(default="X", description="X-axis label")
    ylabel: str = Field(default="Y", description="Y-axis label")
    show_regression: bool = Field(default=True, description="Show regression line")


class VisualizationResponse(BaseModel):
    image_base64: str
    format: str = "png"


# Endpoints
@router.post("/survival-curve", response_model=VisualizationResponse)
async def create_survival_curve(
    request: SurvivalCurveRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate survival curve visualization
    
    Create a Kaplan-Meier survival curve plot with optional confidence intervals.
    """
    try:
        image_base64 = VisualizationService.survival_curve(
            times=request.times,
            survival_prob=request.survival_prob,
            confidence_lower=request.confidence_lower,
            confidence_upper=request.confidence_upper,
            title=request.title
        )
        return VisualizationResponse(image_base64=image_base64)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Visualization error: {str(e)}"
        )


@router.post("/forest-plot", response_model=VisualizationResponse)
async def create_forest_plot(
    request: ForestPlotRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate forest plot visualization
    
    Create a forest plot for meta-analysis results.
    """
    try:
        if len(request.effects) != len(request.ci_lower) or len(request.effects) != len(request.ci_upper):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Effects, CI lower, and CI upper must have the same length"
            )
        
        image_base64 = VisualizationService.forest_plot(
            effects=request.effects,
            ci_lower=request.ci_lower,
            ci_upper=request.ci_upper,
            labels=request.labels,
            weights=request.weights,
            pooled_effect=request.pooled_effect,
            pooled_ci_lower=request.pooled_ci_lower,
            pooled_ci_upper=request.pooled_ci_upper,
            title=request.title
        )
        return VisualizationResponse(image_base64=image_base64)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Visualization error: {str(e)}"
        )


@router.post("/funnel-plot", response_model=VisualizationResponse)
async def create_funnel_plot(
    request: FunnelPlotRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate funnel plot visualization
    
    Create a funnel plot for publication bias assessment.
    """
    try:
        image_base64 = VisualizationService.funnel_plot(
            effects=request.effects,
            se=request.se,
            title=request.title
        )
        return VisualizationResponse(image_base64=image_base64)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Visualization error: {str(e)}"
        )


@router.post("/histogram", response_model=VisualizationResponse)
async def create_histogram(
    request: HistogramRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate histogram visualization
    
    Create a histogram of the data distribution.
    """
    try:
        image_base64 = VisualizationService.histogram(
            data=request.data,
            title=request.title,
            xlabel=request.xlabel,
            ylabel=request.ylabel,
            bins=request.bins
        )
        return VisualizationResponse(image_base64=image_base64)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Visualization error: {str(e)}"
        )


@router.post("/boxplot", response_model=VisualizationResponse)
async def create_boxplot(
    request: BoxplotRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate box plot visualization
    
    Create a box plot comparing multiple groups.
    """
    try:
        image_base64 = VisualizationService.boxplot(
            groups=request.groups,
            labels=request.labels,
            title=request.title,
            ylabel=request.ylabel
        )
        return VisualizationResponse(image_base64=image_base64)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Visualization error: {str(e)}"
        )


@router.post("/scatter-plot", response_model=VisualizationResponse)
async def create_scatter_plot(
    request: ScatterPlotRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate scatter plot visualization
    
    Create a scatter plot with optional regression line.
    """
    try:
        image_base64 = VisualizationService.scatter_plot(
            x=request.x,
            y=request.y,
            title=request.title,
            xlabel=request.xlabel,
            ylabel=request.ylabel,
            show_regression=request.show_regression
        )
        return VisualizationResponse(image_base64=image_base64)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Visualization error: {str(e)}"
        )
