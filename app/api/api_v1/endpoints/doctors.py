from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.models.bot import Bot
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorResponse
from app.api.api_v1.endpoints.auth import get_current_user

router = APIRouter()

@router.get("/bots/{bot_id}/doctors", response_model=List[DoctorResponse])
def read_doctors(
    *,
    db: Session = Depends(get_db),
    bot_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve doctors for a specific bot.
    """
    bot = db.query(Bot).filter(Bot.id == bot_id, Bot.user_id == current_user.id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
        
    doctors = db.query(Doctor).filter(Doctor.bot_id == bot_id).all()
    return doctors

@router.post("/bots/{bot_id}/doctors", response_model=DoctorResponse)
def create_doctor(
    *,
    db: Session = Depends(get_db),
    bot_id: str,
    doctor_in: DoctorCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new doctor for a bot.
    """
    bot = db.query(Bot).filter(Bot.id == bot_id, Bot.user_id == current_user.id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
        
    doctor = Doctor(
        **doctor_in.model_dump(),
        bot_id=bot_id
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor

@router.put("/doctors/{doctor_id}", response_model=DoctorResponse)
def update_doctor(
    *,
    db: Session = Depends(get_db),
    doctor_id: str,
    doctor_in: DoctorCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a doctor.
    """
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
        
    # Verify ownership through bot
    bot = db.query(Bot).filter(Bot.id == doctor.bot_id, Bot.user_id == current_user.id).first()
    if not bot:
        raise HTTPException(status_code=403, detail="Not authorized to update this doctor")
    
    update_data = doctor_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(doctor, field, value)
    
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor

@router.delete("/doctors/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor(
    *,
    db: Session = Depends(get_db),
    doctor_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a doctor.
    """
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
        
    # Verify ownership through bot
    bot = db.query(Bot).filter(Bot.id == doctor.bot_id, Bot.user_id == current_user.id).first()
    if not bot:
        raise HTTPException(status_code=403, detail="Not authorized to delete this doctor")
    
    db.delete(doctor)
    db.commit()
    return None
