"""
Live Stream API Endpoints
Handles live streaming creation, viewer management, and interactions
"""
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from config.database import get_db
from middleware.auth import get_current_user
from models.user import User
from services.live_stream_service import LiveStreamService


router = APIRouter()


# Pydantic Schemas
class CreateStreamRequest(BaseModel):
    title: str
    description: Optional[str] = None
    game_id: Optional[str] = None
    scheduled_start_time: Optional[datetime] = None
    is_public: bool = True
    allow_chat: bool = True
    is_monetized: bool = False
    entry_fee: int = 0  # in rupees
    tags: List[str] = []


class SendChatMessageRequest(BaseModel):
    message: str
    message_type: str = "text"


class DonationRequest(BaseModel):
    amount: float  # in rupees
    message: Optional[str] = None
    is_anonymous: bool = False


# ============================================================================
# Stream Management Endpoints
# ============================================================================

@router.post("/create")
async def create_stream(
    request: CreateStreamRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new live stream"""
    try:
        # Convert rupees to paise
        entry_fee_paise = int(request.entry_fee * 100)

        stream = LiveStreamService.create_stream(
            db=db,
            streamer_id=str(current_user.id),
            title=request.title,
            description=request.description,
            game_id=request.game_id,
            scheduled_start_time=request.scheduled_start_time,
            is_public=request.is_public,
            allow_chat=request.allow_chat,
            is_monetized=request.is_monetized,
            entry_fee=entry_fee_paise,
            tags=request.tags
        )

        stream_dict = stream.to_dict()

        # Add streaming information (only for the streamer)
        stream_dict['stream_key'] = stream.stream_key
        stream_dict['stream_url'] = stream.stream_url

        return {
            "success": True,
            "stream": stream_dict,
            "message": "Stream created successfully. Use the stream key to start broadcasting."
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{stream_id}/start")
async def start_stream(
    stream_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a scheduled stream (streamer only)"""
    try:
        stream = LiveStreamService.start_stream(
            db=db,
            stream_id=stream_id,
            streamer_id=str(current_user.id)
        )

        return {
            "success": True,
            "stream": stream.to_dict(),
            "message": "Stream started successfully. You are now live!"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{stream_id}/end")
async def end_stream(
    stream_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """End a live stream (streamer only)"""
    try:
        stream = LiveStreamService.end_stream(
            db=db,
            stream_id=stream_id,
            streamer_id=str(current_user.id)
        )

        return {
            "success": True,
            "stream": stream.to_dict(),
            "statistics": {
                "duration_seconds": stream.duration_seconds,
                "total_views": stream.total_views,
                "peak_viewers": stream.peak_viewers,
                "likes": stream.like_count,
                "revenue": stream.revenue_generated / 100 if stream.is_monetized else 0
            },
            "message": f"Stream ended. Duration: {stream.duration_seconds // 60} minutes"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/live")
async def get_live_streams(
    game_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get list of currently live streams"""
    streams = LiveStreamService.get_live_streams(
        db=db,
        game_id=game_id,
        status='live',
        skip=skip,
        limit=limit
    )

    return {
        "streams": streams,
        "total_count": len(streams)
    }


@router.get("/upcoming")
async def get_upcoming_streams(
    game_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get list of scheduled/upcoming streams"""
    streams = LiveStreamService.get_live_streams(
        db=db,
        game_id=game_id,
        status='scheduled',
        skip=skip,
        limit=limit
    )

    return {
        "streams": streams,
        "total_count": len(streams)
    }


@router.get("/{stream_id}")
async def get_stream_details(
    stream_id: str,
    db: Session = Depends(get_db)
):
    """Get details of a specific stream"""
    from sqlalchemy import and_
    from models.live_stream import LiveStream

    stream = db.query(LiveStream).filter(LiveStream.id == stream_id).first()

    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream not found"
        )

    # Get streamer info
    streamer = db.query(User).filter(User.id == stream.streamer_id).first()

    stream_dict = stream.to_dict()
    if streamer:
        stream_dict['streamer'] = {
            'id': str(streamer.id),
            'username': streamer.username,
            'display_name': streamer.display_name,
            'avatar': streamer.avatar
        }

    return stream_dict


# ============================================================================
# Viewer Endpoints
# ============================================================================

@router.post("/{stream_id}/join")
async def join_stream(
    stream_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join a live stream as a viewer"""
    try:
        result = LiveStreamService.join_stream(
            db=db,
            stream_id=stream_id,
            user_id=str(current_user.id)
        )

        return {
            "success": True,
            **result,
            "message": "Successfully joined the stream"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{stream_id}/leave")
async def leave_stream(
    stream_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Leave a live stream"""
    result = LiveStreamService.leave_stream(
        db=db,
        stream_id=stream_id,
        user_id=str(current_user.id)
    )

    return {
        **result,
        "message": f"Left stream. Watch duration: {result['watch_duration']} seconds"
    }


@router.post("/{stream_id}/like")
async def like_stream(
    stream_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Like a live stream"""
    try:
        result = LiveStreamService.like_stream(
            db=db,
            stream_id=stream_id,
            user_id=str(current_user.id)
        )

        return {
            **result,
            "message": "Stream liked!"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================================================
# Chat Endpoints
# ============================================================================

@router.post("/{stream_id}/chat")
async def send_chat_message(
    stream_id: str,
    request: SendChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a chat message in a live stream"""
    try:
        chat_message = LiveStreamService.send_chat_message(
            db=db,
            stream_id=stream_id,
            user_id=str(current_user.id),
            message=request.message,
            message_type=request.message_type
        )

        message_dict = chat_message.to_dict()
        message_dict['user'] = {
            'id': str(current_user.id),
            'username': current_user.username,
            'display_name': current_user.display_name,
            'avatar': current_user.avatar
        }

        return {
            "success": True,
            "message": message_dict
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{stream_id}/chat")
async def get_chat_messages(
    stream_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get chat messages for a stream"""
    from sqlalchemy import and_, desc
    from models.live_stream import StreamChat

    messages = db.query(StreamChat, User).join(
        User, StreamChat.user_id == User.id
    ).filter(
        and_(
            StreamChat.stream_id == stream_id,
            StreamChat.is_deleted == False
        )
    ).order_by(desc(StreamChat.sent_at)).offset(skip).limit(limit).all()

    # Reverse to show oldest first
    messages = list(reversed(messages))

    result = []
    for chat, user in messages:
        message_dict = chat.to_dict()
        message_dict['user'] = {
            'id': str(user.id),
            'username': user.username,
            'display_name': user.display_name,
            'avatar': user.avatar
        }
        result.append(message_dict)

    return {
        "messages": result,
        "total_count": len(result)
    }


# ============================================================================
# Donation Endpoints
# ============================================================================

@router.post("/{stream_id}/donate")
async def donate_to_streamer(
    stream_id: str,
    request: DonationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send donation/tip to streamer"""
    try:
        # Convert rupees to paise
        amount_paise = int(request.amount * 100)

        if amount_paise < 1000:  # Minimum ₹10
            raise ValueError("Minimum donation amount is ₹10")

        donation = LiveStreamService.donate_to_streamer(
            db=db,
            stream_id=stream_id,
            donor_id=str(current_user.id),
            amount=amount_paise,
            message=request.message,
            is_anonymous=request.is_anonymous
        )

        return {
            "success": True,
            "donation_id": str(donation.id),
            "amount": request.amount,
            "highlighted": donation.was_highlighted,
            "message": f"Thank you for your donation of ₹{request.amount}!"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================================================
# WebSocket Endpoint for Real-time Updates
# ============================================================================

@router.websocket("/{stream_id}/ws")
async def stream_websocket(
    websocket: WebSocket,
    stream_id: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time stream updates (chat, viewer count, etc.)"""
    await websocket.accept()

    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_json()

            # Handle different message types
            message_type = data.get("type")

            if message_type == "chat":
                # Broadcast chat message
                await websocket.send_json({
                    "type": "chat",
                    "message": data.get("message"),
                    "user": data.get("user")
                })

            elif message_type == "viewer_count":
                # Send viewer count update
                from models.live_stream import LiveStream
                stream = db.query(LiveStream).filter(LiveStream.id == stream_id).first()
                if stream:
                    await websocket.send_json({
                        "type": "viewer_count",
                        "count": stream.viewer_count
                    })

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for stream {stream_id}")
