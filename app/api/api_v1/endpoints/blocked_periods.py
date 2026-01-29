from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.models.bot import Bot
from app.models.blocked_period import BlockedPeriod
from app.schemas.blocked_period import BlockedPeriod as BlockedPeriodSchema, BlockedPeriodCreate, BlockedPeriodUpdate
from app.api.api_v1.endpoints.auth import get_current_user
from uuid import UUID

router = APIRouter()

@router.get("/", response_model=List[BlockedPeriodSchema])
def read_blocked_periods(
    db: Session = Depends(get_db),
    bot_id: UUID = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve blocked periods.
    """
    query = db.query(BlockedPeriod).join(Bot).filter(Bot.user_id == current_user.id)
    if bot_id:
        query = query.filter(BlockedPeriod.bot_id == bot_id)
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=BlockedPeriodSchema)
def create_blocked_period(
    *,
    db: Session = Depends(get_db),
    blocked_period_in: BlockedPeriodCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create new blocked period.
    """
    # Verify bot belongs to user
    bot = db.query(Bot).filter(Bot.id == blocked_period_in.bot_id, Bot.user_id == current_user.id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    blocked_period = BlockedPeriod(**blocked_period_in.model_dump())
    db.add(blocked_period)
    db.commit()
    db.refresh(blocked_period)
    return blocked_period

@router.get("/{blocked_period_id}", response_model=BlockedPeriodSchema)
def read_blocked_period(
    *,
    db: Session = Depends(get_db),
    blocked_period_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get blocked period by ID.
    """
    blocked_period = db.query(BlockedPeriod).join(Bot).filter(
        BlockedPeriod.id == blocked_period_id,
        Bot.user_id == current_user.id
    ).first()
    
    if not blocked_period:
        raise HTTPException(status_code=404, detail="Blocked period not found")
    return blocked_period

@router.patch("/{blocked_period_id}", response_model=BlockedPeriodSchema)
def update_blocked_period(
    *,
    db: Session = Depends(get_db),
    blocked_period_id: str,
    blocked_period_in: BlockedPeriodUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a blocked period.
    """
    blocked_period = db.query(BlockedPeriod).join(Bot).filter(
        BlockedPeriod.id == blocked_period_id,
        Bot.user_id == current_user.id
    ).first()
    
    if not blocked_period:
        raise HTTPException(status_code=404, detail="Blocked period not found")
    
    update_data = blocked_period_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(blocked_period, field, value)
    
    db.add(blocked_period)
    db.commit()
    db.refresh(blocked_period)
    return blocked_period

@router.delete("/{blocked_period_id}", response_model=BlockedPeriodSchema)
def delete_blocked_period(
    *,
    db: Session = Depends(get_db),
    blocked_period_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a blocked period.
    """
    blocked_period = db.query(BlockedPeriod).join(Bot).filter(
        BlockedPeriod.id == blocked_period_id,
        Bot.user_id == current_user.id
    ).first()
    
    if not blocked_period:
        raise HTTPException(status_code=404, detail="Blocked period not found")
    
    db.delete(blocked_period)
    db.commit()
    return blocked_period
