from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User as UserModel
from app.models.bot import Bot as BotModel
from app.models.instance import Instance as InstanceModel
from app.schemas.bot import Bot, BotCreate, BotUpdate


router = APIRouter()


@router.get("/", response_model=List[Bot])
async def get_bots(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all bots owned by the current user.
    """
    bots = db.query(BotModel).join(InstanceModel).filter(
        InstanceModel.user_id == current_user.id
    ).all()
    return bots


@router.post("/", response_model=Bot, status_code=status.HTTP_201_CREATED)
async def create_bot(
    bot_data: BotCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new bot.
    """
    # Verify the instance exists and belongs to the current user
    instance = db.query(InstanceModel).filter(
        InstanceModel.id == bot_data.instance_id,
        InstanceModel.user_id == current_user.id
    ).first()
    
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instance not found or does not belong to user"
        )
    
    # Check if a bot already exists for this instance (1 bot per instance rule)
    existing_bot = db.query(BotModel).filter(
        BotModel.instance_id == bot_data.instance_id
    ).first()
    
    if existing_bot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A bot already exists for this instance"
        )
    
    bot = BotModel(**bot_data.model_dump())
    db.add(bot)
    db.commit()
    db.refresh(bot)
    return bot

@router.get("/{bot_id}", response_model=Bot)
async def get_bot(
    bot_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific bot by ID.
    Validates ownership through instance.
    """
    bot = db.query(BotModel).join(InstanceModel).filter(
        BotModel.id == bot_id,
        InstanceModel.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot not found"
        )
    
    return bot


@router.patch("/{bot_id}", response_model=Bot)
async def update_bot(
    bot_id: UUID,
    bot_data: BotUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a bot's configuration.
    """
    bot = db.query(BotModel).join(InstanceModel).filter(
        BotModel.id == bot_id,
        InstanceModel.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot not found"
        )
    
    # Update fields
    update_data = bot_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bot, field, value)
    
    db.commit()
    db.refresh(bot)
    return bot


@router.delete("/{bot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bot(
    bot_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a bot.
    Validates ownership through instance.
    """
    bot = db.query(BotModel).join(InstanceModel).filter(
        BotModel.id == bot_id,
        InstanceModel.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot not found"
        )
    
    db.delete(bot)
    db.commit()
    return None
