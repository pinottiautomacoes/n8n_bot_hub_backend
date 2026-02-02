from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.models.bot import Bot
from app.models.doctor import Doctor
from app.models.blocked_period import BlockedPeriod
from app.schemas.blocked_period import BlockedPeriodCreate, BlockedPeriodUpdate, BlockedPeriod as BlockedPeriodSchema
from app.api.api_v1.endpoints.auth import get_current_user

router = APIRouter()

@router.get("/doctors/{doctor_id}/blocked-periods", response_model=List[BlockedPeriodSchema])
def read_blocked_periods(
    *,
    db: Session = Depends(get_db),
    doctor_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get blocked periods for a specific doctor.
    """
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id, Doctor.user_id, current_user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    return db.query(BlockedPeriod).filter(BlockedPeriod.doctor_id == doctor_id).all()

@router.post("/doctors/{doctor_id}/blocked-periods", response_model=BlockedPeriodSchema)
def create_blocked_period(
    *,
    db: Session = Depends(get_db),
    doctor_id: str,
    period_in: BlockedPeriodCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a blocked period for a doctor.
    """
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id, Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
        
    blocked_period = BlockedPeriod(
        **period_in.model_dump(exclude={"doctor_id"}), # doctor_id from path overrides or should match
        doctor_id=doctor_id
    )
    db.add(blocked_period)
    db.commit()
    db.refresh(blocked_period)
    return blocked_period

@router.patch("/blocked-periods/{id}", response_model=BlockedPeriodSchema)
def update_blocked_period(
    *,
    db: Session = Depends(get_db),
    id: str,
    period_in: BlockedPeriodUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a blocked period.
    """
    period = db.query(BlockedPeriod).filter(BlockedPeriod.id == id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Blocked period not found")
        
    # Verify ownership
    doctor = db.query(Doctor).filter(Doctor.id == period.doctor_id, Doctor.user_id == current_user.id).first()
    if not doctor:
         raise HTTPException(status_code=404, detail="Doctor not found for this period")
        
    update_data = period_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(period, field, value)
        
    db.add(period)
    db.commit()
    db.refresh(period)
    return period

@router.delete("/blocked-periods/{id}", response_model=BlockedPeriodSchema)
def delete_blocked_period(
    *,
    db: Session = Depends(get_db),
    id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a blocked period.
    """
    period = db.query(BlockedPeriod).filter(BlockedPeriod.id == id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Blocked period not found")
        
    # Verify ownership
    doctor = db.query(Doctor).filter(Doctor.id == period.doctor_id, Doctor.user_id == current_user.id).first()
    if not doctor:
         raise HTTPException(status_code=404, detail="Doctor not found for this period")
        
    db.delete(period)
    db.commit()
    return period
