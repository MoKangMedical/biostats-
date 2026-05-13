"""
Analysis and Upload database models
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class AnalysisType(str, enum.Enum):
    SURVIVAL = "survival"
    SAMPLE_SIZE = "sample_size"
    BAYESIAN = "bayesian"
    META_ANALYSIS = "meta_analysis"
    HYPOTHESIS_TEST = "hypothesis_test"
    REGRESSION = "regression"


class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=True)
    
    # Analysis details
    analysis_type = Column(String(50), nullable=False)
    parameters = Column(JSON)  # Store analysis parameters
    status = Column(String(20), default=AnalysisStatus.PENDING)
    
    # Results
    results = Column(JSON)  # Store analysis results
    interpretation = Column(Text)  # AI-generated interpretation
    
    # Metadata
    execution_time = Column(Float)  # Seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="analyses")
    upload = relationship("Upload", back_populates="analyses")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "analysis_type": self.analysis_type,
            "parameters": self.parameters,
            "status": self.status,
            "results": self.results,
            "interpretation": self.interpretation,
            "execution_time": self.execution_time,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # File details
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer)  # bytes
    file_type = Column(String(50))
    
    # Data metadata
    rows = Column(Integer)
    columns = Column(Integer)
    column_names = Column(JSON)  # List of column names
    column_types = Column(JSON)  # Dict of column types
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="uploads")
    analyses = relationship("Analysis", back_populates="upload")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "rows": self.rows,
            "columns": self.columns,
            "column_names": self.column_names,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
        }
