"""
User database model
"""

from datetime import datetime
from sqlalchemy import Boolean, Column, String, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    
    # Subscription
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)
    subscription_expires = Column(DateTime, nullable=True)
    
    # Usage tracking
    analyses_this_month = Column(Integer, default=0)
    monthly_limit = Column(Integer, default=10)  # Free tier: 10 analyses/month
    
    # Status
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analyses = relationship("Analysis", back_populates="user")
    uploads = relationship("Upload", back_populates="user")

    def can_analyze(self) -> bool:
        """Check if user can perform more analyses"""
        if self.subscription_tier == SubscriptionTier.ENTERPRISE:
            return True
        if self.subscription_tier == SubscriptionTier.PRO:
            return True
        return self.analyses_this_month < self.monthly_limit
