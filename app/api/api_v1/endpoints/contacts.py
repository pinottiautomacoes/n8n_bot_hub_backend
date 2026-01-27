from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User as UserModel
from app.models.contact import Contact as ContactModel
from app.models.instance import Instance as InstanceModel
from app.schemas.contact import Contact


router = APIRouter()


@router.get("", response_model=List[Contact])
async def list_contacts(
    instance_id: Optional[UUID] = Query(None),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all contacts for the current user.
    Optionally filter by instance_id.
    """
    query = db.query(ContactModel).join(InstanceModel).filter(
        InstanceModel.user_id == current_user.id
    )
    
    if instance_id:
        query = query.filter(ContactModel.instance_id == instance_id)
    
    contacts = query.all()
    return contacts


@router.get("/{contact_id}", response_model=Contact)
async def get_contact(
    contact_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific contact by ID.
    """
    contact = db.query(ContactModel).join(InstanceModel).filter(
        ContactModel.id == contact_id,
        InstanceModel.user_id == current_user.id
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    return contact
