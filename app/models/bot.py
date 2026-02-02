from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class Bot(Base):
    __tablename__ = "bots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Basic Info
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Instance Info
    instance_name = Column(String, nullable=True)
    
    # Settings
    personality = Column(Text, nullable=True)
    company_info = Column(Text, nullable=True)
    
    # Status
    enabled = Column(Boolean, default=True, nullable=False)
    timezone = Column(String, default="America/Sao_Paulo", nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="bots")
    
    def __repr__(self):
        return f"<Bot {self.name}>"
