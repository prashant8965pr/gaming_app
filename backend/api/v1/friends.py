"""
Friends API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from pydantic import BaseModel

from config.database import get_db
from middleware.auth import get_current_user
from models.user import User
from models.friends import Friendship, FriendRequest

router = APIRouter(prefix="/friends", tags=["Friends"])


class SendFriendRequest(BaseModel):
    receiver_id: str
    message: str = None


@router.get("")
async def get_friends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get friends list"""
    friendships = db.query(Friendship).filter(
        and_(
            Friendship.user_id == current_user.id,
            Friendship.status == 'accepted'
        )
    ).all()
    
    return {
        "success": True,
        "data": {
            "friends": [f.to_dict() for f in friendships],
            "total": len(friendships)
        }
    }


@router.post("/request")
async def send_friend_request(
    request_data: SendFriendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send friend request"""
    # Check if already friends
    existing_friendship = db.query(Friendship).filter(
        or_(
            and_(
                Friendship.user_id == current_user.id,
                Friendship.friend_id == request_data.receiver_id
            ),
            and_(
                Friendship.user_id == request_data.receiver_id,
                Friendship.friend_id == current_user.id
            )
        )
    ).first()
    
    if existing_friendship:
        raise HTTPException(status_code=400, detail="Already friends")
    
    # Check for existing request
    existing_request = db.query(FriendRequest).filter(
        and_(
            FriendRequest.sender_id == current_user.id,
            FriendRequest.receiver_id == request_data.receiver_id,
            FriendRequest.status == 'pending'
        )
    ).first()
    
    if existing_request:
        raise HTTPException(status_code=400, detail="Friend request already sent")
    
    # Create request
    friend_request = FriendRequest(
        sender_id=current_user.id,
        receiver_id=request_data.receiver_id,
        message=request_data.message
    )
    
    db.add(friend_request)
    db.commit()
    db.refresh(friend_request)
    
    return {
        "success": True,
        "data": {"request": friend_request.to_dict()}
    }


@router.get("/requests")
async def get_friend_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get pending friend requests"""
    requests = db.query(FriendRequest).filter(
        and_(
            FriendRequest.receiver_id == current_user.id,
            FriendRequest.status == 'pending'
        )
    ).all()
    
    return {
        "success": True,
        "data": {
            "requests": [r.to_dict() for r in requests],
            "total": len(requests)
        }
    }


@router.post("/requests/{request_id}/accept")
async def accept_friend_request(
    request_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Accept friend request"""
    friend_request = db.query(FriendRequest).filter(
        and_(
            FriendRequest.id == request_id,
            FriendRequest.receiver_id == current_user.id,
            FriendRequest.status == 'pending'
        )
    ).first()
    
    if not friend_request:
        raise HTTPException(status_code=404, detail="Friend request not found")
    
    # Update request
    friend_request.status = 'accepted'
    friend_request.responded_at = datetime.utcnow()
    
    # Create friendship (bidirectional)
    friendship1 = Friendship(
        user_id=friend_request.sender_id,
        friend_id=friend_request.receiver_id,
        status='accepted'
    )
    friendship2 = Friendship(
        user_id=friend_request.receiver_id,
        friend_id=friend_request.sender_id,
        status='accepted'
    )
    
    db.add(friendship1)
    db.add(friendship2)
    db.commit()
    
    return {
        "success": True,
        "message": "Friend request accepted"
    }
