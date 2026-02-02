from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.models.contact import Contact
from app.schemas.contact import Contact as ContactSchema, ContactCreate, ContactUpdate, ContactResponse
from app.api.api_v1.endpoints.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[ContactResponse])
def read_contacts(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve contacts for the current user.
    """
    query = db.query(Contact).filter(Contact.user_id == current_user.id)
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=ContactResponse)
def create_contact(
    *,
    db: Session = Depends(get_db),
    contact_in: ContactCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a contact for the current user.
    """
    # Check if contact already exists for this user? Optional, but good practice.
    # contact = Contact(
    #     **contact_in.model_dump(),
    #     user_id=current_user.id
    # )
    
    contact = Contact(
        **contact_in.model_dump(),
        user_id=current_user.id
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

@router.get("/{contact_id}", response_model=ContactResponse)
def read_contact(
    *,
    db: Session = Depends(get_db),
    contact_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get contact by ID.
    """
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.patch("/{contact_id}", response_model=ContactResponse)
def update_contact(
    *,
    db: Session = Depends(get_db),
    contact_id: str,
    contact_in: ContactUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a contact.
    """
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
        
    update_data = contact_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)
        
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

@router.delete("/{contact_id}", response_model=ContactResponse)
def delete_contact(
    *,
    db: Session = Depends(get_db),
    contact_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a contact.
    """
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
        
    db.delete(contact)
    db.commit()
    return contact
