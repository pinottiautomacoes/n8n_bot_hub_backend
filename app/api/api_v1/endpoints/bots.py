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

def _call_evolution_api(method: str, endpoint: str, json: Any = None):
    url = f"{settings.EVOLUTION_API_URL}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "apikey": settings.EVOLUTION_API_KEY
    }
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=json)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
            
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # Log error here if logging is set up
        print(f"Error calling Evolution API: {e}")
        if hasattr(e, 'response') and e.response is not None:
             print(f"Evolution API Response: {e.response.text}")
             if e.response.status_code == 404:
                  return None # Or handle specific 404 cases
        raise HTTPException(status_code=502, detail=f"Error communicating with Evolution API: {str(e)}")

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
    
    if not bot.instance_name:
         bot.instance_name = f"bot-{bot.id}"
         
    # Call Evolution API to create instance
    payload = {
        "instanceName": bot.instance_name,
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS",
         # We can make webhook URL configurable later or derive it from settings
        "webhook": {
          "url": settings.N8N_WEBHOOK_URL, 
          "byEvents": False,
          "base64": True,
          "events": ["MESSAGES_UPSERT"]
        }
    }
    
    try:
        _call_evolution_api("POST", "/instance/create", json=payload)
    except HTTPException as e:
         # If instance already exists, we might want to just return the bot or check status
         # For now, let's assume if it fails it might be because it exists or connection error
         if "403" in str(e) or "422" in str(e): # Adjust based on Evolution API error for 'already exists'
              pass
         else:
              raise e

    db.add(bot)
    db.commit()
    db.refresh(bot)
    return bot

@router.get("/{bot_id}/instance/status")
def get_instance_status(
    *,
    db: Session = Depends(get_db),
    bot_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get the connection status of the bot's instance.
    """
    bot = db.query(Bot).filter(Bot.id == bot_id, Bot.user_id == current_user.id).first()
    if not bot or not bot.instance_name:
        raise HTTPException(status_code=404, detail="Bot or instance not found")

    result = _call_evolution_api("GET", f"/instance/connectionState/bot-{bot.instance_name}")
    return result

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
        
    if not bot.instance_name:
         # Optionally try to create it or just return error
         raise HTTPException(status_code=400, detail="Instance not created yet")
    
    # Evolution API /instance/connect/{instance} returns the QR code (often base64 inside JSON)
    result = _call_evolution_api("GET", f"/instance/connect/bot-{bot.instance_name}")
    return result

@router.post("/{bot_id}/instance/restart")
def restart_instance(
    *,
    db: Session = Depends(get_db),
    bot_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Restart the bot's instance.
    """
    bot = db.query(Bot).filter(Bot.id == bot_id, Bot.user_id == current_user.id).first()
    if not bot or not bot.instance_name:
         raise HTTPException(status_code=404, detail="Bot or instance not found")
         
    result = _call_evolution_api("POST", f"/instance/restart/bot-{bot.instance_name}")
    return result

@router.delete("/{bot_id}/instance")
def delete_instance(
    *,
    db: Session = Depends(get_db),
    bot_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete the bot's instance from Evolution API.
    """
    bot = db.query(Bot).filter(Bot.id == bot_id, Bot.user_id == current_user.id).first()
    if not bot or not bot.instance_name:
         raise HTTPException(status_code=404, detail="Bot or instance not found")
         
    _call_evolution_api("DELETE", f"/instance/delete/bot-{bot.instance_name}")
    
    bot.instance_name = None
    db.add(bot)
    db.commit()
    return {"message": "Instance deleted"}
