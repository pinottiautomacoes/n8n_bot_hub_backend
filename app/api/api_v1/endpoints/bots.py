from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any
import requests
from app.core.database import get_db
from app.models.user import User
from app.models.bot import Bot
from app.schemas.bot import Bot as BotSchema, BotCreate, BotUpdate, BotResponse
from app.api.api_v1.endpoints.auth import get_current_user
from app.core.config import settings

router = APIRouter()

@router.get("/", response_model=List[BotResponse])
def read_bots(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve bots.
    """
    bots = db.query(Bot).filter(Bot.user_id == current_user.id).offset(skip).limit(limit).all()
    return bots

@router.post("/", response_model=BotResponse)
def create_bot(
    *,
    db: Session = Depends(get_db),
    bot_in: BotCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create new bot.
    """
    bot = Bot(
        **bot_in.model_dump(),
        user_id=current_user.id
    )
    db.add(bot)
    db.commit()
    db.refresh(bot)
    return bot

@router.get("/{bot_id}", response_model=BotResponse)
def read_bot(
    *,
    db: Session = Depends(get_db),
    bot_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get bot by ID.
    """
    bot = db.query(Bot).filter(Bot.id == bot_id, Bot.user_id == current_user.id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    return bot

@router.patch("/{bot_id}", response_model=BotResponse)
def update_bot(
    *,
    db: Session = Depends(get_db),
    bot_id: str,
    bot_in: BotUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a bot.
    """
    bot = db.query(Bot).filter(Bot.id == bot_id, Bot.user_id == current_user.id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    update_data = bot_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bot, field, value)
    
    db.add(bot)
    db.commit()
    db.refresh(bot)
    return bot

@router.delete("/{bot_id}", response_model=BotResponse)
def delete_bot(
    *,
    db: Session = Depends(get_db),
    bot_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a bot.
    """
    bot = db.query(Bot).filter(Bot.id == bot_id, Bot.user_id == current_user.id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Hard delete for now, or use soft delete (enabled=False) if preferred
    db.delete(bot)
    db.commit()
    return bot

# Instance Management Endpoints

@router.post("/{bot_id}/instance", response_model=BotResponse)
def create_instance(
    *,
    db: Session = Depends(get_db),
    bot_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Create an instance on the Evolution API matching this bot.
    """
    bot = db.query(Bot).filter(Bot.id == bot_id, Bot.user_id == current_user.id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Logic to call Evolution API would go here
    # For now, we simulate success or expect 'instance_name' to be set
    if not bot.instance_name:
         bot.instance_name = f"bot-{bot.id}"
    
    # TODO: Call Evolution API to create instance
    # requests.post(f"{settings.EVOLUTION_URL}/instance/create", ...)

    db.add(bot)
    db.commit()
    return bot

@router.get("/{bot_id}/qrcode")
def get_qrcode(
    *,
    db: Session = Depends(get_db),
    bot_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get QR code for the bot's instance.
    """
    bot = db.query(Bot).filter(Bot.id == bot_id, Bot.user_id == current_user.id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # TODO: Proxy to Evolution API
    # return requests.get(f"{settings.EVOLUTION_URL}/instance/qrcode/{bot.instance_name}").json()
    
    return {"message": "QR Code logic pending implementation"}
