from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List
from uuid import UUID
from datetime import datetime, timedelta
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User as UserModel
from app.models.appointment import Appointment as AppointmentModel
from app.models.bot import Bot as BotModel
from app.models.business_hour import BusinessHour as BusinessHourModel
from app.models.instance import Instance as InstanceModel
from app.schemas.appointment import Appointment, AppointmentCreate, AppointmentUpdate


router = APIRouter()


@router.get("/bots/{bot_id}/appointments", response_model=List[Appointment])
async def list_appointments(
    bot_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all appointments for a bot.
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
    
    appointments = db.query(AppointmentModel).filter(
        AppointmentModel.bot_id == bot_id
    ).order_by(AppointmentModel.start_time.asc()).all()
    
    return appointments


@router.post("/bots/{bot_id}/appointments", response_model=Appointment, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    bot_id: UUID,
    appointment_data: AppointmentCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new appointment.
    Validates business hours, blocked periods, and checks for conflicts.
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
    
    # Calculate end time based on service duration
    start_time = appointment_data.start_time
    end_time = start_time + timedelta(minutes=bot.service_duration_minutes)
    
    # Use availability service to check if slot is available
    # This checks business hours, blocked periods, and existing appointments
    from app.services.availability_service import check_time_slot_available
    
    is_available, reason = check_time_slot_available(
        db=db,
        bot_id=bot_id,
        start_time=start_time,
        end_time=end_time
    )
    
    if not is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=reason
        )
    
    # Create appointment
    appointment = AppointmentModel(
        bot_id=bot_id,
        contact_id=appointment_data.contact_id,
        start_time=start_time,
        end_time=end_time,
        status="active"
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    
    return appointment


@router.patch("/appointments/{appointment_id}", response_model=Appointment)
async def update_appointment(
    appointment_id: UUID,
    appointment_data: AppointmentUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an appointment (mainly for cancellation).
    """
    # Verify ownership
    appointment = db.query(AppointmentModel).join(BotModel).join(InstanceModel).filter(
        AppointmentModel.id == appointment_id,
        InstanceModel.user_id == current_user.id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Update fields
    update_data = appointment_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(appointment, field, value)
    
    db.commit()
    db.refresh(appointment)
    return appointment


@router.delete("/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_appointment(
    appointment_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel an appointment (marks as cancelled, doesn't delete).
    """
    # Verify ownership
    appointment = db.query(AppointmentModel).join(BotModel).join(InstanceModel).filter(
        AppointmentModel.id == appointment_id,
        InstanceModel.user_id == current_user.id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    appointment.status = "cancelled"
    db.commit()
    return None
