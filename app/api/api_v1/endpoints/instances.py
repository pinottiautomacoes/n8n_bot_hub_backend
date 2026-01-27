from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User as UserModel
from app.models.instance import Instance as InstanceModel
from app.models.bot import Bot as BotModel
from app.schemas.instance import Instance, InstanceCreate, InstanceUpdate
from app.schemas.bot import Bot, BotCreate


router = APIRouter()


@router.post("", response_model=Instance, status_code=status.HTTP_201_CREATED)
async def create_instance(
    instance_data: InstanceCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new instance for the current user.
    Automatically creates a bot for the instance.
    """
    # Create instance
    instance = InstanceModel(
        user_id=current_user.id,
        **instance_data.model_dump()
    )
    db.add(instance)
    db.commit()
    db.refresh(instance)
    
    # Automatically create bot for instance (1 bot per instance rule)
    bot = BotModel(
        instance_id=instance.id,
        name=f"{instance.name} Bot"
    )
    db.add(bot)
    db.commit()
    
    return instance


@router.get("", response_model=List[Instance])
async def list_instances(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all instances for the current user.
    """
    instances = db.query(InstanceModel).filter(
        InstanceModel.user_id == current_user.id
    ).all()
    return instances


@router.get("/{instance_id}", response_model=Instance)
async def get_instance(
    instance_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific instance by ID.
    """
    instance = db.query(InstanceModel).filter(
        InstanceModel.id == instance_id,
        InstanceModel.user_id == current_user.id
    ).first()
    
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instance not found"
        )
    
    return instance


@router.patch("/{instance_id}", response_model=Instance)
async def update_instance(
    instance_id: UUID,
    instance_data: InstanceUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an instance.
    """
    instance = db.query(InstanceModel).filter(
        InstanceModel.id == instance_id,
        InstanceModel.user_id == current_user.id
    ).first()
    
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instance not found"
        )
    
    # Update fields
    update_data = instance_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(instance, field, value)
    
    db.commit()
    db.refresh(instance)
    return instance


@router.delete("/{instance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_instance(
    instance_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an instance.
    """
    instance = db.query(InstanceModel).filter(
        InstanceModel.id == instance_id,
        InstanceModel.user_id == current_user.id
    ).first()
    
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instance not found"
        )
    
    db.delete(instance)
    db.commit()
    return None
