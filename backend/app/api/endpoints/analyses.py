"""
Analysis endpoints
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.endpoints.users import get_current_user
from app.models.user import User
from app.models.analysis import Analysis, AnalysisStatus
from app.schemas.schemas import AnalysisCreate, AnalysisResponse

router = APIRouter()


@router.post("/", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    analysis_data: AnalysisCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new analysis"""
    # Check usage limits
    if not current_user.can_analyze():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Monthly analysis limit reached. Please upgrade your plan."
        )
    
    # Create analysis record
    analysis = Analysis(
        user_id=current_user.id,
        upload_id=analysis_data.upload_id,
        analysis_type=analysis_data.analysis_type,
        parameters=analysis_data.parameters,
        status=AnalysisStatus.PENDING,
    )
    db.add(analysis)
    
    # Update usage counter
    current_user.analyses_this_month += 1
    
    db.commit()
    db.refresh(analysis)
    
    # TODO: Trigger async analysis execution
    # For now, mark as completed immediately
    analysis.status = AnalysisStatus.COMPLETED
    analysis.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(analysis)
    
    return AnalysisResponse.from_orm(analysis)


@router.get("/", response_model=List[AnalysisResponse])
async def list_analyses(
    analysis_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's analyses"""
    query = db.query(Analysis).filter(Analysis.user_id == current_user.id)
    
    if analysis_type:
        query = query.filter(Analysis.analysis_type == analysis_type)
    if status:
        query = query.filter(Analysis.status == status)
    
    analyses = query.order_by(Analysis.created_at.desc()).offset(offset).limit(limit).all()
    return [AnalysisResponse.from_orm(a) for a in analyses]


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analysis by ID"""
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id
    ).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    return AnalysisResponse.from_orm(analysis)


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete analysis"""
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id
    ).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    db.delete(analysis)
    db.commit()
    return None
