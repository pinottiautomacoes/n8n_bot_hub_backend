from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.conversation import Conversation as ConversationModel
from app.models.message import Message as MessageModel
from app.schemas.webhook import N8nIncoming, N8nOutgoing


router = APIRouter()


@router.post("/incoming")
async def n8n_incoming(
    payload: N8nIncoming,
    db: Session = Depends(get_db)
):
    """
    Receive incoming messages from n8n for processing.
    This endpoint is called by n8n when it needs to process a message.
    
    Note: The actual message has already been persisted by the webhook endpoint.
    This is mainly for n8n to acknowledge receipt and potentially trigger workflows.
    """
    return {
        "status": "received",
        "conversation_id": payload.conversation_id,
        "message": payload.message
    }


@router.post("/outgoing")
async def n8n_outgoing(
    payload: N8nOutgoing,
    db: Session = Depends(get_db)
):
    """
    Receive outgoing messages from n8n (bot responses).
    Persists the bot's response in the database.
    """
    try:
        # Verify conversation exists
        conversation = db.query(ConversationModel).filter(
            ConversationModel.id == payload.conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Create message from bot
        message = MessageModel(
            conversation_id=conversation.id,
            sender="bot",
            message_type=payload.message_type,
            content=payload.message,
            external_message_id=payload.external_message_id
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        
        return {
            "status": "ok",
            "message_id": str(message.id)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing outgoing message: {str(e)}"
        )
