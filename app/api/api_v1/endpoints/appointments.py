from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.core.database import get_db
from app.models.user import User
from app.models.bot import Bot
from app.models.contact import Contact
from app.models.appointment import Appointment
from app.models.blocked_period import BlockedPeriod
from app.models.business_hour import BusinessHour
from app.models.doctor import Doctor
from app.models.service import Service
from app.schemas.appointment import Appointment as AppointmentSchema, AppointmentCreate, AppointmentUpdate, AppointmentResponse, AvailableSlotsResponse, AvailableTimeSlot
from zoneinfo import ZoneInfo
from app.api.api_v1.endpoints.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[AppointmentResponse])
def read_appointments(
    *,
    db: Session = Depends(get_db),
    doctor_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve appointments for the current user.
    """
    query = db.query(Appointment).filter(Appointment.user_id == current_user.id)
    
    if doctor_id:
        query = query.filter(Appointment.doctor_id == doctor_id)

    if start_date:
        query = query.filter(Appointment.start_time >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        # Inclusive end date
        query = query.filter(Appointment.end_time <= datetime.combine(end_date, datetime.max.time()))
        
    return query.offset(skip).limit(limit).all()

@router.get("/available-slots", response_model=AvailableSlotsResponse)
def get_available_slots(
    *,
    db: Session = Depends(get_db),
    instance_name: str = Query(..., alias="instanceName"),
    date_param: date = Query(..., alias="date"),
    doctor_id: str = Query(..., alias="doctorId"),
    service_id: str = Query(..., alias="serviceId")
):
    """
    Get available time slots for a specific doctor and service on a date.
    """
    # 1. Find Bot
    bot = db.query(Bot).filter(Bot.instance_name == instance_name).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot instance not found")

    if not bot.enabled:
        raise HTTPException(status_code=400, detail="Bot is disabled")
        
    # 2. Find Doctor & Service
    # Ensure they belong to the bot
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id, Doctor.bot_id == bot.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found for this bot")
        
    service = db.query(Service).filter(Service.id == service_id, Service.bot_id == bot.id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found for this bot")

    # 3. Setup Timezone
    try:
        tz = ZoneInfo(bot.timezone)
    except Exception:
        tz = ZoneInfo("America/Sao_Paulo")  # Fallback

    # 4. Determine Business Hours for the Doctor
    weekday = (date_param.weekday() + 1) % 7
    
    business_hour = db.query(BusinessHour).filter(
        BusinessHour.doctor_id == doctor.id,
        BusinessHour.weekday == weekday,
        BusinessHour.is_available == True
    ).first()

    if not business_hour:
        # Doctor Closed on this day
        return AvailableSlotsResponse(available_slots=[])

    # Convert Business Hours to UTC for the specific date
    bh_start_naive = datetime.combine(date_param, business_hour.start_time)
    bh_end_naive = datetime.combine(date_param, business_hour.end_time)

    # Localize to bot's timezone
    bh_start_local = bh_start_naive.replace(tzinfo=tz)
    bh_end_local = bh_end_naive.replace(tzinfo=tz)

    # Convert to UTC for DB querying
    open_start_utc = bh_start_local.astimezone(ZoneInfo("UTC"))
    open_end_utc = bh_end_local.astimezone(ZoneInfo("UTC"))

    if open_end_utc <= open_start_utc:
         # Handle wrap around if needed
         pass

    # 5. Fetch Busy Intervals
    # Appointments for this Doctor
    # Only active appointments count as busy
    appointments = db.query(Appointment).filter(
        Appointment.doctor_id == doctor.id,
        Appointment.status == "active",
        Appointment.start_time < open_end_utc.replace(tzinfo=None), 
        Appointment.end_time > open_start_utc.replace(tzinfo=None)
    ).all()

    # Blocked Periods
    # Filtered by Doctor
    blocked_periods = db.query(BlockedPeriod).filter(
        BlockedPeriod.doctor_id == doctor.id,
        BlockedPeriod.start_time < open_end_utc.replace(tzinfo=None),
        BlockedPeriod.end_time > open_start_utc.replace(tzinfo=None)
    ).all()

    # 6. Process Availability
    busy_intervals = []
    
    def to_aware_utc(dt):
        if dt.tzinfo is None:
            return dt.replace(tzinfo=ZoneInfo("UTC"))
        return dt.astimezone(ZoneInfo("UTC"))

    for appt in appointments:
        start = to_aware_utc(appt.start_time)
        end = to_aware_utc(appt.end_time)
        busy_intervals.append((start, end))
        
    for bp in blocked_periods:
        start = to_aware_utc(bp.start_time)
        end = to_aware_utc(bp.end_time)
        busy_intervals.append((start, end))
        
    # Sort by start time
    busy_intervals.sort(key=lambda x: x[0])

    available_slots = []
    
    # 7. Generate fixed slots based on Service Duration
    duration = timedelta(minutes=service.duration)
    current_slot_start = open_start_utc
    
    sp_tz = ZoneInfo("America/Sao_Paulo")

    def utc_to_sp(dt: datetime) -> datetime:
        return dt.astimezone(sp_tz)

    while current_slot_start + duration <= open_end_utc:
        current_slot_end = current_slot_start + duration
        is_conflicted = False
        
        for busy_start, busy_end in busy_intervals:
            if busy_start < current_slot_end and busy_end > current_slot_start:
                is_conflicted = True
                break
        
        if not is_conflicted:
            available_slots.append(AvailableTimeSlot(start=utc_to_sp(current_slot_start), end=utc_to_sp(current_slot_end)))
            
        current_slot_start += duration

    return AvailableSlotsResponse(available_slots=available_slots)

@router.get("/by-contact", response_model=List[AppointmentResponse])
def get_appointments_by_contact(
    *,
    db: Session = Depends(get_db),
    instance_name: str = Query(..., alias="instanceName"),
    contact_phone: str = Query(..., alias="contactNumber"),
):
    """
    Get all upcoming appointments for a contact by phone number.
    Filters by the Bot's User to find the correct Contact.
    """
    # 1. Find Bot
    bot = db.query(Bot).filter(Bot.instance_name == instance_name).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot instance not found")

    # 2. Find Contact via User
    # Contact is now linked to User (bot.user_id)
    contact = db.query(Contact).filter(
        Contact.phone == contact_phone,
        Contact.user_id == bot.user_id
    ).first()
    
    if not contact:
        return []

    # 3. Find Upcoming Appointments
    # We might want to filter only appointments related to this bot? 
    # Since Appointment -> Doctor -> Bot, we can join.
    current_time_utc = datetime.utcnow()
    
    appointments = db.query(Appointment).join(Doctor).filter(
        Appointment.contact_id == contact.id,
        Doctor.bot_id == bot.id, # Encapsulate to this bot
        Appointment.status == "active",
        Appointment.start_time >= current_time_utc
    ).order_by(Appointment.start_time.asc()).all()
    
    return appointments

@router.post("/", response_model=AppointmentResponse)
def create_appointment(
    *,
    db: Session = Depends(get_db),
    appointment_in: AppointmentCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create new appointment.
    """
    # Verify contact belongs to current user
    contact = db.query(Contact).filter(Contact.id == appointment_in.contact_id, Contact.user_id == current_user.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    # Verify Doctor
    # Doctor must belong to a bot owned by current_user.
    if not appointment_in.doctor_id:
         raise HTTPException(status_code=400, detail="Doctor ID is required")
         
    doctor = db.query(Doctor).filter(Doctor.id == appointment_in.doctor_id, Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found or authorization failed")

    # Verify Service
    if not appointment_in.service_id:
         raise HTTPException(status_code=400, detail="Service ID is required")
         
    service = db.query(Service).filter(Service.id == appointment_in.service_id, Service.user_id == current_user.id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found or authorization failed")

    # Optional: Verify Doctor and Service belong to same Bot?
    if doctor.bot_id != service.bot_id:
        raise HTTPException(status_code=400, detail="Doctor and Service must belong to the same Bot")

    appointment = Appointment(
        **appointment_in.model_dump(),
        user_id=current_user.id
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
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id, Appointment.user_id == current_user.id).first()
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
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id, Appointment.user_id == current_user.id).first()
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
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id, Appointment.user_id == current_user.id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
        
    appointment.status = "cancelled"
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment
