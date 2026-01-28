from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.models.bot import Bot
from app.models.business_hour import BusinessHour
from app.schemas.business_hour import BusinessHour as BusinessHourSchema, BusinessHourCreate, BusinessHourUpdate, BusinessHourResponse
from app.api.api_v1.endpoints.auth import get_current_user

router = APIRouter()

@router.get("/bots/{bot_id}/business-hours", response_model=List[BusinessHourResponse])
def read_business_hours(
    *,
    db: Session = Depends(get_db),
    bot_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get business hours for a specific bot.
    """
    bot = db.query(Bot).filter(Bot.id == bot_id, Bot.user_id == current_user.id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
        
    return db.query(BusinessHour).filter(BusinessHour.bot_id == bot_id).all()

@router.post("/bots/{bot_id}/business-hours", response_model=BusinessHourResponse)
def create_business_hour(
    *,
    db: Session = Depends(get_db),
    bot_id: str,
    hour_in: BusinessHourCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a business hour entry for a bot.
    """
    bot = db.query(Bot).filter(Bot.id == bot_id, Bot.user_id == current_user.id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
        
    business_hour = BusinessHour(
        **hour_in.model_dump(),
        bot_id=bot_id
    )
    db.add(business_hour)
    db.commit()
    db.refresh(business_hour)
    return business_hour

@router.patch("/business-hours/{id}", response_model=BusinessHourResponse)
def update_business_hour(
    *,
    db: Session = Depends(get_db),
    id: str,
    hour_in: BusinessHourUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a business hour entry.
    """
    hour = db.query(BusinessHour).filter(BusinessHour.id == id).first()
    if not hour:
        raise HTTPException(status_code=404, detail="Business hour not found")
        
    # Verify ownership via bot
    bot = db.query(Bot).filter(Bot.id == hour.bot_id, Bot.user_id == current_user.id).first()
    if not bot:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    update_data = hour_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(hour, field, value)
        
    db.add(hour)
    db.commit()
    db.refresh(hour)
    return hour

@router.delete("/business-hours/{id}", response_model=BusinessHourResponse)
def delete_business_hour(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a business hour entry.
    """
    hour = db.query(BusinessHour).filter(BusinessHour.id == id).first()
    if not hour:
        raise HTTPException(status_code=404, detail="Business hour not found")
        
    # Verify ownership via bot
    bot = db.query(Bot).filter(Bot.id == hour.bot_id, Bot.user_id == current_user.id).first()
    if not bot:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db.delete(hour)
    db.commit()
    return hour
