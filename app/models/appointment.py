from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=True, index=True)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id", ondelete="CASCADE"), nullable=True, index=True)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String, default="active", nullable=False)  # active | cancelled
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")
    contact = relationship("Contact", back_populates="appointments")
    
    def __repr__(self):
        return f"<Appointment {self.title}>"
