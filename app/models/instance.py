from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class Instance(Base):
    __tablename__ = "instances"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    channel = Column(String, nullable=False)  # whatsapp, instagram, messenger, etc
    external_instance_id = Column(String, nullable=True)  # Evolution API instance ID
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="instances")
    bot = relationship("Bot", back_populates="instance", uselist=False, cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="instance", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="instance", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Instance {self.name} ({self.channel})>"
