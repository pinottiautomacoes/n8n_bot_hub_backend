from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    phone = Column(String, nullable=False)  # Renamed from external_contact_id
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="contacts")
    appointments = relationship("Appointment", back_populates="contact", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Contact {self.name or self.phone}>"
