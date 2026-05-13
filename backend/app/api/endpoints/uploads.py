"""
File upload endpoints
"""

import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import pandas as pd

from app.core.database import get_db
from app.core.config import settings
from app.api.endpoints.users import get_current_user
from app.models.user import User
from app.models.analysis import Upload
from app.schemas.schemas import UploadResponse

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a data file for analysis"""
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE // (1024*1024)}MB"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Parse file to get metadata
    try:
        if file_ext == ".csv":
            df = pd.read_csv(file_path)
        elif file_ext in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path)
        elif file_ext == ".json":
            df = pd.read_json(file_path)
        else:
            df = None
        
        if df is not None:
            rows = len(df)
            columns = len(df.columns)
            column_names = df.columns.tolist()
            column_types = {col: str(dtype) for col, dtype in df.dtypes.items()}
        else:
            rows = 0
            columns = 0
            column_names = []
            column_types = {}
    except Exception as e:
        # Clean up file on parse error
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error parsing file: {str(e)}"
        )
    
    # Create upload record
    upload = Upload(
        user_id=current_user.id,
        filename=unique_filename,
        original_filename=file.filename,
        file_size=len(contents),
        file_type=file_ext,
        rows=rows,
        columns=columns,
        column_names=column_names,
        column_types=column_types,
    )
    db.add(upload)
    db.commit()
    db.refresh(upload)
    
    return UploadResponse.from_orm(upload)


@router.get("/", response_model=List[UploadResponse])
async def list_uploads(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's uploaded files"""
    uploads = db.query(Upload).filter(
        Upload.user_id == current_user.id
    ).order_by(Upload.uploaded_at.desc()).offset(offset).limit(limit).all()
    
    return [UploadResponse.from_orm(u) for u in uploads]


@router.get("/{upload_id}", response_model=UploadResponse)
async def get_upload(
    upload_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get upload details"""
    upload = db.query(Upload).filter(
        Upload.id == upload_id,
        Upload.user_id == current_user.id
    ).first()
    
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found"
        )
    
    return UploadResponse.from_orm(upload)


@router.delete("/{upload_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_upload(
    upload_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete uploaded file"""
    upload = db.query(Upload).filter(
        Upload.id == upload_id,
        Upload.user_id == current_user.id
    ).first()
    
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found"
        )
    
    # Delete file from disk
    file_path = os.path.join(UPLOAD_DIR, upload.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Delete record
    db.delete(upload)
    db.commit()
    return None
