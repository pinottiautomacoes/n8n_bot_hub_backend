from fastapi import APIRouter
from app.api.api_v1.endpoints import (
    auth,
    bots,
    business_hours,
    appointments,
    contacts,
    blocked_periods,
    doctors,
    services
)

api_router = APIRouter()

# Auth routes
api_router.include_router(auth.router, tags=["auth"])

# Bot routes
api_router.include_router(bots.router, prefix="/bots", tags=["bots"])

# Business hours routes
api_router.include_router(business_hours.router, tags=["business-hours"])

# Appointment routes
api_router.include_router(appointments.router, prefix="/appointments", tags=["appointments"])

# Contact routes
api_router.include_router(contacts.router, prefix="/contacts", tags=["contacts"])

# Blocked Periods routes
api_router.include_router(blocked_periods.router, tags=["blocked-periods"])

# Doctor routes
api_router.include_router(doctors.router, prefix="/doctors", tags=["doctors"])

# Service routes
api_router.include_router(services.router, prefix="/services", tags=["services"])
