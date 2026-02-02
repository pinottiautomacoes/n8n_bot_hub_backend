from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.models.bot import Bot
from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceResponse
from app.api.api_v1.endpoints.auth import get_current_user

router = APIRouter()

@router.get("/bots/{bot_id}/services", response_model=List[ServiceResponse])
def read_services(
    *,
    db: Session = Depends(get_db),
    bot_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve services for a specific bot.
    """
    bot = db.query(Bot).filter(Bot.id == bot_id, Bot.user_id == current_user.id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
        
    services = db.query(Service).filter(Service.bot_id == bot_id).all()
    return services

@router.post("/bots/{bot_id}/services", response_model=ServiceResponse)
def create_service(
    *,
    db: Session = Depends(get_db),
    bot_id: str,
    service_in: ServiceCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new service for a bot.
    """
    bot = db.query(Bot).filter(Bot.id == bot_id, Bot.user_id == current_user.id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
        
    service = Service(
        **service_in.model_dump(),
        bot_id=bot_id
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return service

@router.put("/services/{service_id}", response_model=ServiceResponse)
def update_service(
    *,
    db: Session = Depends(get_db),
    service_id: str,
    service_in: ServiceCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a service.
    """
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
        
    # Verify ownership through bot
    bot = db.query(Bot).filter(Bot.id == service.bot_id, Bot.user_id == current_user.id).first()
    if not bot:
        raise HTTPException(status_code=403, detail="Not authorized to update this service")
    
    update_data = service_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(service, field, value)
    
    db.add(service)
    db.commit()
    db.refresh(service)
    return service

@router.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    *,
    db: Session = Depends(get_db),
    service_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a service.
    """
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
        
    # Verify ownership through bot
    bot = db.query(Bot).filter(Bot.id == service.bot_id, Bot.user_id == current_user.id).first()
    if not bot:
        raise HTTPException(status_code=403, detail="Not authorized to delete this service")
    
    db.delete(service)
    db.commit()
    return None
