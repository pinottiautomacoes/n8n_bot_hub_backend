from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class Bot(Base):
    __tablename__ = "bots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instance_id = Column(UUID(as_uuid=True), ForeignKey("instances.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)
    personality = Column(Text, nullable=True)
    company_info = Column(Text, nullable=True)
    target_audience = Column(Text, nullable=True)
    service_duration_minutes = Column(Integer, default=30, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    instance = relationship("Instance", back_populates="bot")
    business_hours = relationship("BusinessHour", back_populates="bot", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="bot", cascade="all, delete-orphan")
    blocked_periods = relationship("BlockedPeriod", back_populates="bot", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Bot {self.name}>"
