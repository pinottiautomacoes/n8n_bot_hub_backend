from fastapi import APIRouter
from app.api.api_v1.endpoints import (
    auth,
    instances,
    bots,
    business_hours,
    appointments,
    blocked_periods,
    availability,
    webhooks
)

api_router = APIRouter()

# Auth routes
api_router.include_router(auth.router, tags=["auth"])

# Instance routes
api_router.include_router(instances.router, prefix="/instances", tags=["instances"])

# Bot routes
api_router.include_router(bots.router, prefix="/bots", tags=["bots"])

# Business hours routes
api_router.include_router(business_hours.router, tags=["business-hours"])

# Blocked periods routes
api_router.include_router(blocked_periods.router, tags=["blocked-periods"])

# Availability routes
api_router.include_router(availability.router, tags=["availability"])

# Appointment routes
api_router.include_router(appointments.router, tags=["appointments"])

# Webhook routes (no auth required)
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])


