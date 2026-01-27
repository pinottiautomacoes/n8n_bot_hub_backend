from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from uuid import UUID

from app.api.deps import get_db
from app.services.availability_service import get_available_slots

router = APIRouter()


@router.get("/bots/{bot_id}/available-slots")
def get_bot_available_slots(
    bot_id: UUID,
    date: datetime = Query(..., description="Date to check for available slots"),
    duration_minutes: int = Query(None, description="Duration in minutes (defaults to bot's service duration)"),
    db: Session = Depends(get_db)
):
    """
    Get all available time slots for a bot on a specific date.
    
    This endpoint considers:
    - Business hours
    - Existing appointments
    - Blocked periods
    
    Returns a list of available time slots.
    """
    slots = get_available_slots(
        db=db,
        bot_id=bot_id,
        date=date,
        duration_minutes=duration_minutes
    )
    
    return {
        "bot_id": str(bot_id),
        "date": date.date().isoformat(),
        "available_slots": [
            {
                "start_time": start.isoformat(),
                "end_time": end.isoformat()
            }
            for start, end in slots
        ],
        "total_slots": len(slots)
    }
