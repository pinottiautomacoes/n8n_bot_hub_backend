from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User as UserModel
from app.models.bot import Bot as BotModel
from app.models.business_hour import BusinessHour as BusinessHourModel
from app.models.instance import Instance as InstanceModel
from app.schemas.business_hour import BusinessHour, BusinessHourCreate


router = APIRouter()


@router.post("/bots/{bot_id}/business-hours", response_model=BusinessHour, status_code=status.HTTP_201_CREATED)
async def create_business_hour(
    bot_id: UUID,
    business_hour_data: BusinessHourCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a business hour for a bot.
    """
    # Verify bot ownership
    bot = db.query(BotModel).join(InstanceModel).filter(
        BotModel.id == bot_id,
        InstanceModel.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot not found"
        )
    
    # Create business hour
    business_hour = BusinessHourModel(
        bot_id=bot_id,
        weekday=business_hour_data.weekday,
        start_time=business_hour_data.start_time,
        end_time=business_hour_data.end_time
    )
    db.add(business_hour)
    db.commit()
    db.refresh(business_hour)
    
    return business_hour


@router.get("/bots/{bot_id}/business-hours", response_model=List[BusinessHour])
async def list_business_hours(
    bot_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all business hours for a bot.
    """
    # Verify bot ownership
    bot = db.query(BotModel).join(InstanceModel).filter(
        BotModel.id == bot_id,
        InstanceModel.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot not found"
        )
    
    business_hours = db.query(BusinessHourModel).filter(
        BusinessHourModel.bot_id == bot_id
    ).all()
    
    return business_hours


@router.delete("/business-hours/{business_hour_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_business_hour(
    business_hour_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a business hour.
    """
    # Verify ownership through bot and instance
    business_hour = db.query(BusinessHourModel).join(BotModel).join(InstanceModel).filter(
        BusinessHourModel.id == business_hour_id,
        InstanceModel.user_id == current_user.id
    ).first()
    
    if not business_hour:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business hour not found"
        )
    
    db.delete(business_hour)
    db.commit()
    return None
