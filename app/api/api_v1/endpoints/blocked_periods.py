from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from app.api.deps import get_db
from app.models.blocked_period import BlockedPeriod as BlockedPeriodModel
from app.models.bot import Bot as BotModel
from app.schemas.blocked_period import (
    BlockedPeriod,
    BlockedPeriodCreate,
    BlockedPeriodUpdate,
)

router = APIRouter()


@router.post("/bots/{bot_id}/blocked-periods", response_model=BlockedPeriod, status_code=201)
def create_blocked_period(
    bot_id: UUID,
    blocked_period: BlockedPeriodCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new blocked period for a bot.
    
    This prevents appointments from being scheduled during the specified time range.
    """
    # Verify bot exists
    bot = db.query(BotModel).filter(BotModel.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Create blocked period
    db_blocked_period = BlockedPeriodModel(
        bot_id=bot_id,
        **blocked_period.model_dump()
    )
    db.add(db_blocked_period)
    db.commit()
    db.refresh(db_blocked_period)
    
    return db_blocked_period


@router.get("/bots/{bot_id}/blocked-periods", response_model=List[BlockedPeriod])
def list_blocked_periods(
    bot_id: UUID,
    start_date: Optional[datetime] = Query(None, description="Filter periods starting after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter periods ending before this date"),
    active_only: bool = Query(False, description="Only show periods that haven't ended yet"),
    db: Session = Depends(get_db)
):
    """
    List all blocked periods for a bot.
    
    Supports filtering by date range and active status.
    """
    # Verify bot exists
    bot = db.query(BotModel).filter(BotModel.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Build query
    query = db.query(BlockedPeriodModel).filter(BlockedPeriodModel.bot_id == bot_id)
    
    if start_date:
        query = query.filter(BlockedPeriodModel.start_datetime >= start_date)
    
    if end_date:
        query = query.filter(BlockedPeriodModel.end_datetime <= end_date)
    
    if active_only:
        query = query.filter(BlockedPeriodModel.end_datetime >= datetime.utcnow())
    
    # Order by start date
    query = query.order_by(BlockedPeriodModel.start_datetime)
    
    return query.all()


@router.get("/blocked-periods/{blocked_period_id}", response_model=BlockedPeriod)
def get_blocked_period(
    blocked_period_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific blocked period by ID.
    """
    blocked_period = db.query(BlockedPeriodModel).filter(
        BlockedPeriodModel.id == blocked_period_id
    ).first()
    
    if not blocked_period:
        raise HTTPException(status_code=404, detail="Blocked period not found")
    
    return blocked_period


@router.put("/blocked-periods/{blocked_period_id}", response_model=BlockedPeriod)
def update_blocked_period(
    blocked_period_id: UUID,
    blocked_period_update: BlockedPeriodUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a blocked period.
    """
    db_blocked_period = db.query(BlockedPeriodModel).filter(
        BlockedPeriodModel.id == blocked_period_id
    ).first()
    
    if not db_blocked_period:
        raise HTTPException(status_code=404, detail="Blocked period not found")
    
    # Update fields
    update_data = blocked_period_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_blocked_period, field, value)
    
    db.commit()
    db.refresh(db_blocked_period)
    
    return db_blocked_period


@router.delete("/blocked-periods/{blocked_period_id}", status_code=204)
def delete_blocked_period(
    blocked_period_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a blocked period.
    """
    db_blocked_period = db.query(BlockedPeriodModel).filter(
        BlockedPeriodModel.id == blocked_period_id
    ).first()
    
    if not db_blocked_period:
        raise HTTPException(status_code=404, detail="Blocked period not found")
    
    db.delete(db_blocked_period)
    db.commit()
    
    return None
