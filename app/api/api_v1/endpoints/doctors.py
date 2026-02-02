from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorResponse
from app.api.api_v1.endpoints.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[DoctorResponse])
def read_doctors(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve doctors for the current user.
    """
    query = db.query(Doctor).filter(Doctor.user_id == current_user.id)
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=DoctorResponse)
def create_doctor(
    *,
    db: Session = Depends(get_db),
    doctor_in: DoctorCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new doctor for the current user.
    """
    doctor = Doctor(
        **doctor_in.model_dump(),
        user_id=current_user.id
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor

@router.put("/{doctor_id}", response_model=DoctorResponse)
def update_doctor(
    *,
    db: Session = Depends(get_db),
    doctor_id: str,
    doctor_in: DoctorCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a doctor.
    """
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
        
    update_data = doctor_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(doctor, field, value)
    
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor

@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor(
    *,
    db: Session = Depends(get_db),
    doctor_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a doctor.
    """
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
        
    db.delete(doctor)
    db.commit()
    return None
