from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.core.database import get_db
from app.models.user import User
from app.models.bot import Bot
from app.models.contact import Contact
from app.models.appointment import Appointment
from app.schemas.appointment import Appointment as AppointmentSchema, AppointmentCreate, AppointmentUpdate, AppointmentResponse
from app.api.api_v1.endpoints.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[AppointmentResponse])
def read_appointments(
    *,
    db: Session = Depends(get_db),
    bot_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve appointments.
    """
    query = db.query(Appointment)
    
    if bot_id:
        # Verify bot ownership
        bot = db.query(Bot).filter(Bot.id == bot_id, Bot.user_id == current_user.id).first()
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")
        query = query.filter(Appointment.bot_id == bot_id)
    else:
        # Return all appointments for all user's bots
        query = query.join(Bot).filter(Bot.user_id == current_user.id)
        
    if start_date:
        query = query.filter(Appointment.start_time >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        # Inclusive end date
        query = query.filter(Appointment.end_time <= datetime.combine(end_date, datetime.max.time()))
        
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=AppointmentResponse)
def create_appointment(
    *,
    db: Session = Depends(get_db),
    appointment_in: AppointmentCreate,
    bot_id: str, # From query or inferred from contact? Better explicit.
    current_user: User = Depends(get_current_user)
):
    """
    Create new appointment.
    """
    # Verify bot exists and owned by user
    bot = db.query(Bot).filter(Bot.id == bot_id, Bot.user_id == current_user.id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
        
    # Verify contact belongs to bot
    contact = db.query(Contact).filter(Contact.id == appointment_in.contact_id, Contact.bot_id == bot_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found for this bot")

    appointment = Appointment(
        **appointment_in.model_dump(),
        bot_id=bot_id
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment

@router.get("/{appointment_id}", response_model=AppointmentResponse)
def read_appointment(
    *,
    db: Session = Depends(get_db),
    appointment_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get appointment by ID.
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).join(Bot).filter(Bot.user_id == current_user.id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@router.patch("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    *,
    db: Session = Depends(get_db),
    appointment_id: str,
    appointment_in: AppointmentUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update an appointment.
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).join(Bot).filter(Bot.user_id == current_user.id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
        
    update_data = appointment_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(appointment, field, value)
        
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment

@router.delete("/{appointment_id}", response_model=AppointmentResponse)
def delete_appointment(
    *,
    db: Session = Depends(get_db),
    appointment_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Soft delete an appointment (set status to cancelled).
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).join(Bot).filter(Bot.user_id == current_user.id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
        
    appointment.status = "cancelled"
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment
