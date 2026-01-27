"""
Availability service - Helper functions for checking appointment availability
"""
from datetime import datetime, timedelta
from typing import List, Tuple
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.bot import Bot
from app.models.business_hour import BusinessHour
from app.models.appointment import Appointment
from app.models.blocked_period import BlockedPeriod


def check_time_slot_available(
    db: Session,
    bot_id: UUID,
    start_time: datetime,
    end_time: datetime,
    exclude_appointment_id: UUID = None
) -> Tuple[bool, str]:
    """
    Check if a time slot is available for booking.
    
    Args:
        db: Database session
        bot_id: Bot ID
        start_time: Start time of the slot
        end_time: End time of the slot
        exclude_appointment_id: Optional appointment ID to exclude (for updates)
    
    Returns:
        Tuple of (is_available: bool, reason: str)
    """
    # Get bot
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        return False, "Bot not found"
    
    # Check if time is in blocked period
    blocked_period = db.query(BlockedPeriod).filter(
        BlockedPeriod.bot_id == bot_id,
        BlockedPeriod.start_datetime <= start_time,
        BlockedPeriod.end_datetime >= end_time
    ).first()
    
    if blocked_period:
        reason = f"Time slot is blocked"
        if blocked_period.reason:
            reason += f": {blocked_period.reason}"
        return False, reason
    
    # Check if overlaps with any blocked period
    overlapping_blocked = db.query(BlockedPeriod).filter(
        BlockedPeriod.bot_id == bot_id,
        BlockedPeriod.start_datetime < end_time,
        BlockedPeriod.end_datetime > start_time
    ).first()
    
    if overlapping_blocked:
        reason = f"Time slot overlaps with blocked period"
        if overlapping_blocked.reason:
            reason += f": {overlapping_blocked.reason}"
        return False, reason
    
    # Check business hours
    weekday = start_time.weekday()
    business_hour = db.query(BusinessHour).filter(
        BusinessHour.bot_id == bot_id,
        BusinessHour.weekday == weekday
    ).first()
    
    if not business_hour:
        return False, f"No business hours configured for {start_time.strftime('%A')}"
    
    # Convert datetime to time for comparison
    start_time_only = start_time.time()
    end_time_only = end_time.time()
    
    if start_time_only < business_hour.start_time or end_time_only > business_hour.end_time:
        return False, f"Time slot outside business hours ({business_hour.start_time} - {business_hour.end_time})"
    
    # Check for overlapping appointments
    query = db.query(Appointment).filter(
        Appointment.bot_id == bot_id,
        Appointment.status == "active",
        Appointment.start_time < end_time,
        Appointment.end_time > start_time
    )
    
    if exclude_appointment_id:
        query = query.filter(Appointment.id != exclude_appointment_id)
    
    overlapping_appointment = query.first()
    
    if overlapping_appointment:
        return False, "Time slot conflicts with existing appointment"
    
    return True, "Time slot is available"


def get_available_slots(
    db: Session,
    bot_id: UUID,
    date: datetime,
    duration_minutes: int = None
) -> List[Tuple[datetime, datetime]]:
    """
    Get all available time slots for a given day.
    
    Args:
        db: Database session
        bot_id: Bot ID
        date: Date to check (time will be ignored)
        duration_minutes: Duration of appointment in minutes (defaults to bot's service_duration_minutes)
    
    Returns:
        List of tuples (start_time, end_time) for available slots
    """
    # Get bot
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        return []
    
    if duration_minutes is None:
        duration_minutes = bot.service_duration_minutes
    
    # Get business hours for this day
    weekday = date.weekday()
    business_hour = db.query(BusinessHour).filter(
        BusinessHour.bot_id == bot_id,
        BusinessHour.weekday == weekday
    ).first()
    
    if not business_hour:
        return []
    
    # Create datetime objects for business hours
    start_datetime = datetime.combine(date.date(), business_hour.start_time)
    end_datetime = datetime.combine(date.date(), business_hour.end_time)
    
    # Generate all possible slots
    available_slots = []
    current_time = start_datetime
    slot_duration = timedelta(minutes=duration_minutes)
    
    while current_time + slot_duration <= end_datetime:
        slot_end = current_time + slot_duration
        
        # Check if this slot is available
        is_available, _ = check_time_slot_available(
            db=db,
            bot_id=bot_id,
            start_time=current_time,
            end_time=slot_end
        )
        
        if is_available:
            available_slots.append((current_time, slot_end))
        
        # Move to next slot (using same duration as increment)
        current_time += slot_duration
    
    return available_slots
