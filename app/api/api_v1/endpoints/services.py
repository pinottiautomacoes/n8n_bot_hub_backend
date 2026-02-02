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

@router.get("/", response_model=List[ServiceResponse])
def read_services(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve services for a specific user.
    """
    services = db.query(Service).filter(Service.user_id == current_user.id).all()
    return services

@router.post("/", response_model=ServiceResponse)
def create_service(
    *,
    db: Session = Depends(get_db),
    service_in: ServiceCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new service for a user.
    """
        
    service = Service(
        **service_in.model_dump(),
        user_id=current_user.id
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return service

@router.put("/{service_id}", response_model=ServiceResponse)
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
        
    # Verify ownership through user_id
    if service.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this service")
    
    update_data = service_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(service, field, value)
    
    db.add(service)
    db.commit()
    db.refresh(service)
    return service

@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
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
        
    # Verify ownership through user_id
    if service.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this service")
    
    db.delete(service)
    db.commit()
    return None
