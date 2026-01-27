from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User as UserModel
from app.models.conversation import Conversation as ConversationModel
from app.models.message import Message as MessageModel
from app.models.instance import Instance as InstanceModel
from app.schemas.conversation import Conversation
from app.schemas.message import Message


router = APIRouter()


@router.get("", response_model=List[Conversation])
async def list_conversations(
    instance_id: Optional[UUID] = Query(None),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all conversations for the current user.
    Optionally filter by instance_id.
    """
    query = db.query(ConversationModel).join(InstanceModel).filter(
        InstanceModel.user_id == current_user.id
    )
    
    if instance_id:
        query = query.filter(ConversationModel.instance_id == instance_id)
    
    conversations = query.all()
    return conversations


@router.get("/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific conversation by ID.
    """
    conversation = db.query(ConversationModel).join(InstanceModel).filter(
        ConversationModel.id == conversation_id,
        InstanceModel.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return conversation


@router.get("/{conversation_id}/messages", response_model=List[Message])
async def get_conversation_messages(
    conversation_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all messages for a conversation.
    """
    # Verify conversation ownership
    conversation = db.query(ConversationModel).join(InstanceModel).filter(
        ConversationModel.id == conversation_id,
        InstanceModel.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    messages = db.query(MessageModel).filter(
        MessageModel.conversation_id == conversation_id
    ).order_by(MessageModel.created_at.asc()).all()
    
    return messages
