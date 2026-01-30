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
from app.schemas.appointment import Appointment as AppointmentSchema, AppointmentCreate, AppointmentUpdate, AppointmentResponse, AvailableSlotsResponse, AvailableTimeSlot
from zoneinfo import ZoneInfo
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

@router.get("/available-slots", response_model=AvailableSlotsResponse)
def get_available_slots(
    *,
    db: Session = Depends(get_db),
    instance_name: str = Query(..., alias="instanceName"),
    date_param: date = Query(..., alias="date"),
):
    """
    Get available time slots for a specific bot instance and date.
    Checks business hours, blocked periods, and existing appointments.
    """
    # 1. Find Bot
    bot = db.query(Bot).filter(Bot.instance_name == instance_name).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot instance not found")

    if not bot.enabled:
        raise HTTPException(status_code=400, detail="Bot is disabled")

    # 2. Setup Timezone
    try:
        tz = ZoneInfo(bot.timezone)
    except Exception:
        tz = ZoneInfo("America/Sao_Paulo")  # Fallback

    # 3. Determine Business Hours for the day
    # n8n/User request: 0=Sunday, 1=Monday, ... 6=Saturday
    # Python date.weekday(): 0=Monday, ... 6=Sunday
    # Mapping: (python_weekday + 1) % 7 => 0=Sunday, 1=Monday
    weekday = (date_param.weekday() + 1) % 7
    
    business_hour = db.query(BusinessHour).filter(
        BusinessHour.bot_id == bot.id,
        BusinessHour.weekday == weekday,
        BusinessHour.is_available == True
    ).first()

    if not business_hour:
        # Closed on this day
        return AvailableSlotsResponse(available_slots=[])

    # Convert Business Hours to UTC for the specific date
    # Note: business_hour.start_time is a time object (naive)
    
    # Create naive datetime from date + time
    bh_start_naive = datetime.combine(date_param, business_hour.start_time)
    bh_end_naive = datetime.combine(date_param, business_hour.end_time)

    # Localize to bot's timezone
    bh_start_local = bh_start_naive.replace(tzinfo=tz)
    bh_end_local = bh_end_naive.replace(tzinfo=tz)

    # Convert to UTC for DB querying
    open_start_utc = bh_start_local.astimezone(ZoneInfo("UTC"))
    open_end_utc = bh_end_local.astimezone(ZoneInfo("UTC"))

    # If end time is before start time (e.g. crossing midnight), handle it? 
    # Current logic assumes same-day business hours logic for simplicity.
    if open_end_utc <= open_start_utc:
         # If it wrapped around, we might need to handle it. 
         # Assuming simple 9-5 for now.
         pass

    # 4. Fetch Busy Intervals (Appointments & Blocked Periods)
    # Filter for anything overlapping the open window
    
    # Appointments
    appointments = db.query(Appointment).filter(
        Appointment.bot_id == bot.id,
        Appointment.status == "active",
        Appointment.start_time < open_end_utc.replace(tzinfo=None), # DB is usually naive UTC
        Appointment.end_time > open_start_utc.replace(tzinfo=None)
    ).all()

    # Blocked Periods
    blocked_periods = db.query(BlockedPeriod).filter(
        BlockedPeriod.bot_id == bot.id,
        BlockedPeriod.start_time < open_end_utc.replace(tzinfo=None),
        BlockedPeriod.end_time > open_start_utc.replace(tzinfo=None)
    ).all()

    # 5. Process Availability
    busy_intervals = []
    
    # Helper to standardize to aware UTC
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
    
    # 6. Generate fixed slots
    duration = timedelta(minutes=bot.appointment_duration)
    current_slot_start = open_start_utc
    
    sp_tz = ZoneInfo("America/Sao_Paulo")

    def utc_to_sp(dt: datetime) -> datetime:
        return dt.astimezone(sp_tz)

    while current_slot_start + duration <= open_end_utc:
        current_slot_end = current_slot_start + duration
        is_conflicted = False
        
        for busy_start, busy_end in busy_intervals:
            # Check for overlap:
            # (StartA < EndB) and (EndA > StartB)
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
    """
    # 1. Find Bot
    bot = db.query(Bot).filter(Bot.instance_name == instance_name).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot instance not found")

    # 2. Find Contact
    contact = db.query(Contact).filter(
        Contact.phone == contact_phone,
        Contact.bot_id == bot.id
    ).first()
    
    if not contact:
        # If contact doesn't exist, they can't have appointments
        return []

    # 3. Find Upcoming Appointments
    # Ensure they are active and in the future
    current_time_utc = datetime.utcnow()
    
    appointments = db.query(Appointment).filter(
        Appointment.contact_id == contact.id,
        Appointment.bot_id == bot.id,
        Appointment.status == "active",
        Appointment.start_time >= current_time_utc
    ).order_by(Appointment.start_time.asc()).all()
    
    return appointments

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
