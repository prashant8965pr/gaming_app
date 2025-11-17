"""
Chat API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict

from config.database import get_db
from middleware.auth import get_current_user
from models.user import User
from services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])


# Schemas
class SendMessageRequest(BaseModel):
    receiver_id: str
    content: str
    message_type: str = "text"
    metadata: Optional[Dict] = None


class EditMessageRequest(BaseModel):
    content: str


class TypingIndicatorRequest(BaseModel):
    conversation_id: str


@router.get("/conversations")
async def get_conversations(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's conversations"""
    try:
        conversations = ChatService.get_user_conversations(
            db,
            str(current_user.id),
            skip,
            limit
        )
        return {
            "success": True,
            "data": {
                "conversations": conversations,
                "total": len(conversations)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation details"""
    try:
        # Verify access
        from models.chat import Conversation
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        user_id = str(current_user.id)
        if user_id not in [str(conversation.user1_id), str(conversation.user2_id)]:
            raise HTTPException(status_code=403, detail="Access denied")

        return {
            "success": True,
            "data": {"conversation": conversation.to_dict(current_user_id=user_id)}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send")
async def send_message(
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message"""
    try:
        # Get or create conversation
        conversation = ChatService.get_or_create_conversation(
            db,
            str(current_user.id),
            request.receiver_id
        )

        # Send message
        message = ChatService.send_message(
            db,
            str(conversation.id),
            str(current_user.id),
            request.content,
            request.message_type,
            request.metadata
        )

        return {
            "success": True,
            "data": {"message": message.to_dict()}
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/messages/{conversation_id}")
async def get_messages(
    conversation_id: str,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages in a conversation"""
    try:
        messages = ChatService.get_messages(
            db,
            conversation_id,
            str(current_user.id),
            skip,
            limit
        )

        return {
            "success": True,
            "data": {
                "messages": [m.to_dict() for m in messages],
                "total": len(messages)
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages/{conversation_id}/mark-read")
async def mark_messages_read(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all messages in conversation as read"""
    try:
        count = ChatService.mark_messages_as_read(
            db,
            conversation_id,
            str(current_user.id)
        )

        return {
            "success": True,
            "data": {"marked_read": count}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/messages/{conversation_id}/unread-count")
async def get_unread_count(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get unread message count"""
    try:
        count = ChatService.get_unread_count(
            db,
            conversation_id,
            str(current_user.id)
        )

        return {
            "success": True,
            "data": {"unread_count": count}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/messages/{message_id}")
async def edit_message(
    message_id: str,
    request: EditMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Edit a message"""
    try:
        message = ChatService.edit_message(
            db,
            message_id,
            str(current_user.id),
            request.content
        )

        return {
            "success": True,
            "data": {"message": message.to_dict()}
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a message"""
    try:
        message = ChatService.delete_message(
            db,
            message_id,
            str(current_user.id)
        )

        return {
            "success": True,
            "data": {"message": message.to_dict()}
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/typing")
async def set_typing_indicator(
    request: TypingIndicatorRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set typing indicator"""
    try:
        indicator = ChatService.set_typing_indicator(
            db,
            request.conversation_id,
            str(current_user.id)
        )

        return {
            "success": True,
            "data": {"indicator": indicator.to_dict()}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/typing/{conversation_id}")
async def get_typing_users(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get users currently typing"""
    try:
        typing_users = ChatService.get_typing_users(
            db,
            conversation_id,
            str(current_user.id)
        )

        return {
            "success": True,
            "data": {"typing_users": typing_users}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_messages(
    query: str = Query(..., min_length=1),
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search messages"""
    try:
        results = ChatService.search_messages(
            db,
            str(current_user.id),
            query,
            limit
        )

        return {
            "success": True,
            "data": {
                "results": results,
                "total": len(results)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
