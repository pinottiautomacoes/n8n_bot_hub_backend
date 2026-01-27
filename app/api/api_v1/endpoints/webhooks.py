from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
import httpx
from app.core.database import get_db
from app.core.config import settings
from app.models.instance import Instance as InstanceModel
from app.models.contact import Contact as ContactModel
from app.models.conversation import Conversation as ConversationModel
from app.models.message import Message as MessageModel
from app.schemas.webhook import WebhookMessage, N8nIncoming, N8nOutgoing


router = APIRouter()


async def send_to_n8n(payload: dict):
    """
    Send payload to n8n webhook.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.N8N_WEBHOOK_URL}/webhook/incoming",
                json=payload,
                timeout=10.0
            )
            response.raise_for_status()
        except Exception as e:
            print(f"Error sending to n8n: {e}")


def normalize_whatsapp_payload(payload: dict) -> WebhookMessage:
    """
    Normalize WhatsApp webhook payload.
    Adjust this based on Evolution API webhook format.
    """
    # This is a simplified example - adjust based on actual Evolution API format
    return WebhookMessage(
        channel="whatsapp",
        instance_id=payload.get("instance"),
        contact_id=payload.get("key", {}).get("remoteJid"),
        message=payload.get("message", {}).get("conversation", ""),
        message_type="text",
        external_message_id=payload.get("key", {}).get("id"),
        from_me=payload.get("key", {}).get("fromMe", False)
    )


@router.post("/whatsapp")
async def whatsapp_webhook(
    payload: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Receive WhatsApp messages from Evolution API.
    """
    try:
        # Normalize payload
        normalized = normalize_whatsapp_payload(payload)
        
        # Get or create instance
        instance = db.query(InstanceModel).filter(
            InstanceModel.external_instance_id == normalized.instance_id
        ).first()
        
        if not instance:
            return {"status": "ignored", "reason": "instance not found"}
        
        # Get or create contact
        contact = db.query(ContactModel).filter(
            ContactModel.instance_id == instance.id,
            ContactModel.external_contact_id == normalized.contact_id
        ).first()
        
        if not contact:
            contact = ContactModel(
                instance_id=instance.id,
                external_contact_id=normalized.contact_id
            )
            db.add(contact)
            db.commit()
            db.refresh(contact)
        
        # Get or create conversation
        conversation = db.query(ConversationModel).filter(
            ConversationModel.instance_id == instance.id,
            ConversationModel.contact_id == contact.id
        ).first()
        
        if not conversation:
            conversation = ConversationModel(
                instance_id=instance.id,
                contact_id=contact.id,
                status="bot"
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        # Create message
        message = MessageModel(
            conversation_id=conversation.id,
            sender="user" if not normalized.from_me else "human",
            message_type=normalized.message_type,
            content=normalized.message,
            external_message_id=normalized.external_message_id
        )
        db.add(message)
        db.commit()
        
        # If message is from the owner (from_me), update conversation status to human
        if normalized.from_me:
            conversation.status = "human"
            conversation.last_human_message_at = message.created_at
            db.commit()
            return {"status": "ok", "action": "handoff_to_human"}
        
        # If conversation is in human mode, don't send to n8n
        if conversation.status == "human":
            return {"status": "ok", "action": "human_handling"}
        
        # Send to n8n for bot processing
        n8n_payload = N8nIncoming(
            channel=normalized.channel,
            instance_id=str(instance.id),
            contact_id=str(contact.id),
            conversation_id=str(conversation.id),
            message=normalized.message,
            message_type=normalized.message_type,
            external_message_id=normalized.external_message_id
        )
        
        background_tasks.add_task(send_to_n8n, n8n_payload.model_dump())
        
        return {"status": "ok", "action": "sent_to_bot"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )


@router.post("/instagram")
async def instagram_webhook(payload: dict, db: Session = Depends(get_db)):
    """
    Receive Instagram messages.
    TODO: Implement Instagram-specific normalization.
    """
    return {"status": "not_implemented"}


@router.post("/messenger")
async def messenger_webhook(payload: dict, db: Session = Depends(get_db)):
    """
    Receive Messenger messages.
    TODO: Implement Messenger-specific normalization.
    """
    return {"status": "not_implemented"}


@router.post("/tiktok")
async def tiktok_webhook(payload: dict, db: Session = Depends(get_db)):
    """
    Receive TikTok messages.
    TODO: Implement TikTok-specific normalization.
    """
    return {"status": "not_implemented"}
