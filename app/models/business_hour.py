from sqlalchemy import Column, Integer, Time, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class BusinessHour(Base):
    __tablename__ = "business_hours"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bot_id = Column(UUID(as_uuid=True), ForeignKey("bots.id", ondelete="CASCADE"), nullable=False, index=True)
    weekday = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    # Relationships
    bot = relationship("Bot", back_populates="business_hours")
    
    def __repr__(self):
        return f"<BusinessHour {self.weekday} {self.start_time}-{self.end_time}>"
