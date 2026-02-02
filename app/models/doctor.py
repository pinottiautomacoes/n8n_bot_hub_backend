from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class Doctor(Base):
    __tablename__ = "doctors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bot_id = Column(UUID(as_uuid=True), ForeignKey("bots.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    specialties = Column(Text, nullable=True)
    crm = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    bot = relationship("Bot", back_populates="doctors")
    appointments = relationship("Appointment", back_populates="doctor", cascade="all, delete-orphan")
    business_hours = relationship("BusinessHour", back_populates="doctor", cascade="all, delete-orphan")
    blocked_periods = relationship("BlockedPeriod", back_populates="doctor", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Doctor {self.name}>"
