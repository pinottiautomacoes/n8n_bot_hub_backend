from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.models.bot import Bot
from app.models.doctor import Doctor
from app.models.business_hour import BusinessHour
from app.schemas.business_hour import BusinessHour as BusinessHourSchema, BusinessHourCreate, BusinessHourUpdate, BusinessHourResponse
from app.api.api_v1.endpoints.auth import get_current_user

router = APIRouter()

@router.get("/doctors/{doctor_id}/business-hours", response_model=List[BusinessHourResponse])
def read_business_hours(
    *,
    db: Session = Depends(get_db),
    doctor_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get business hours for a specific doctor.
    """
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id, Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
        
        
    return db.query(BusinessHour).filter(BusinessHour.doctor_id == doctor_id).all()

@router.post("/doctors/{doctor_id}/business-hours", response_model=BusinessHourResponse)
def create_business_hour(
    *,
    db: Session = Depends(get_db),
    doctor_id: str,
    hour_in: BusinessHourCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a business hour entry for a doctor.
    """
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id, Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
        
    business_hour = BusinessHour(
        **hour_in.model_dump(),
        doctor_id=doctor_id
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
        
    # Verify ownership via doctor -> bot
    doctor = db.query(Doctor).filter(Doctor.id == hour.doctor_id, Doctor.user_id == current_user.id).first()
    if not doctor:
         raise HTTPException(status_code=404, detail="Doctor not found for this business hour")
        
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
        
    # Verify ownership
    doctor = db.query(Doctor).filter(Doctor.id == hour.doctor_id, Doctor.user_id == current_user.id).first()
    if not doctor:
         raise HTTPException(status_code=404, detail="Doctor not found for this business hour")
        
    db.delete(hour)
    db.commit()
    return hour
