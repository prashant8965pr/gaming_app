"""
Push Notifications API Endpoints
Handles device registration, notification preferences, and notification history
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime

from config.database import get_db
from middleware.auth import get_current_user
from models.user import User
from services.push_notification_service import PushNotificationService


router = APIRouter()


# Pydantic Schemas
class RegisterDeviceRequest(BaseModel):
    device_token: str
    device_type: str  # ios, android, web
    device_name: Optional[str] = None
    device_model: Optional[str] = None
    app_version: Optional[str] = None
    os_version: Optional[str] = None


class UpdatePreferencesRequest(BaseModel):
    push_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    social_notifications: Optional[bool] = None
    gaming_notifications: Optional[bool] = None
    financial_notifications: Optional[bool] = None
    promotional_notifications: Optional[bool] = None
    system_notifications: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None  # "22:00"
    quiet_hours_end: Optional[str] = None  # "08:00"
    sound_enabled: Optional[bool] = None
    vibration_enabled: Optional[bool] = None


class SendTestNotificationRequest(BaseModel):
    title: str
    body: str
    icon: Optional[str] = None
    image: Optional[str] = None


# ============================================================================
# Device Management Endpoints
# ============================================================================

@router.post("/devices/register")
async def register_device(
    request: RegisterDeviceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register a device for push notifications"""
    try:
        device = PushNotificationService.register_device(
            db=db,
            user_id=str(current_user.id),
            device_token=request.device_token,
            device_type=request.device_type,
            device_name=request.device_name,
            device_model=request.device_model,
            app_version=request.app_version,
            os_version=request.os_version
        )

        return {
            "success": True,
            "device_id": str(device.id),
            "message": "Device registered successfully for push notifications"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/devices/unregister")
async def unregister_device(
    device_token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unregister a device from push notifications"""
    success = PushNotificationService.unregister_device(db, device_token)

    if success:
        return {
            "success": True,
            "message": "Device unregistered successfully"
        }
    else:
        return {
            "success": False,
            "message": "Device not found"
        }


@router.get("/devices/list")
async def list_devices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of registered devices"""
    devices = PushNotificationService.get_user_devices(
        db, str(current_user.id), active_only=False
    )

    device_list = []
    for device in devices:
        device_list.append({
            "id": str(device.id),
            "device_type": device.device_type,
            "device_name": device.device_name,
            "device_model": device.device_model,
            "app_version": device.app_version,
            "os_version": device.os_version,
            "is_active": device.is_active,
            "enabled": device.enabled,
            "last_used_at": device.last_used_at.isoformat() if device.last_used_at else None,
            "created_at": device.created_at.isoformat() if device.created_at else None
        })

    return {
        "devices": device_list,
        "total_count": len(device_list)
    }


# ============================================================================
# Preferences Endpoints
# ============================================================================

@router.get("/preferences")
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notification preferences"""
    prefs = PushNotificationService.get_or_create_preferences(db, str(current_user.id))

    return {
        "push_enabled": prefs.push_enabled,
        "email_enabled": prefs.email_enabled,
        "sms_enabled": prefs.sms_enabled,
        "social_notifications": prefs.social_notifications,
        "gaming_notifications": prefs.gaming_notifications,
        "financial_notifications": prefs.financial_notifications,
        "promotional_notifications": prefs.promotional_notifications,
        "system_notifications": prefs.system_notifications,
        "quiet_hours_enabled": prefs.quiet_hours_enabled,
        "quiet_hours_start": prefs.quiet_hours_start,
        "quiet_hours_end": prefs.quiet_hours_end,
        "sound_enabled": prefs.sound_enabled,
        "vibration_enabled": prefs.vibration_enabled
    }


@router.put("/preferences")
async def update_preferences(
    request: UpdatePreferencesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update notification preferences"""
    # Convert request to dict and filter out None values
    preferences = {k: v for k, v in request.dict().items() if v is not None}

    prefs = PushNotificationService.update_preferences(
        db, str(current_user.id), preferences
    )

    return {
        "success": True,
        "message": "Notification preferences updated successfully",
        "preferences": {
            "push_enabled": prefs.push_enabled,
            "email_enabled": prefs.email_enabled,
            "sms_enabled": prefs.sms_enabled,
            "social_notifications": prefs.social_notifications,
            "gaming_notifications": prefs.gaming_notifications,
            "financial_notifications": prefs.financial_notifications,
            "promotional_notifications": prefs.promotional_notifications,
            "system_notifications": prefs.system_notifications,
            "quiet_hours_enabled": prefs.quiet_hours_enabled,
            "quiet_hours_start": prefs.quiet_hours_start,
            "quiet_hours_end": prefs.quiet_hours_end,
            "sound_enabled": prefs.sound_enabled,
            "vibration_enabled": prefs.vibration_enabled
        }
    }


# ============================================================================
# Notification History Endpoints
# ============================================================================

@router.get("/history")
async def get_notification_history(
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notification history"""
    notifications = PushNotificationService.get_user_notifications(
        db, str(current_user.id), skip, limit, unread_only
    )

    notification_list = [notif.to_dict() for notif in notifications]

    # Get unread count
    unread_count = PushNotificationService.get_unread_count(db, str(current_user.id))

    return {
        "notifications": notification_list,
        "total_count": len(notification_list),
        "unread_count": unread_count
    }


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications"""
    count = PushNotificationService.get_unread_count(db, str(current_user.id))

    return {
        "unread_count": count
    }


@router.post("/{notification_id}/mark-read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark notification as read/clicked"""
    notification = PushNotificationService.mark_notification_clicked(
        db, notification_id, str(current_user.id)
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    return {
        "success": True,
        "message": "Notification marked as read"
    }


@router.post("/mark-all-read")
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    from models.notification import PushNotification
    from sqlalchemy import and_

    # Update all unread notifications
    db.query(PushNotification).filter(
        and_(
            PushNotification.user_id == current_user.id,
            PushNotification.clicked_at == None
        )
    ).update({
        "clicked_at": datetime.utcnow(),
        "status": "clicked"
    })

    db.commit()

    return {
        "success": True,
        "message": "All notifications marked as read"
    }


# ============================================================================
# Test Notification Endpoint
# ============================================================================

@router.post("/send-test")
async def send_test_notification(
    request: SendTestNotificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a test notification to the current user"""
    notification = await PushNotificationService.send_notification(
        db=db,
        user_id=str(current_user.id),
        notification_type="test",
        title=request.title,
        body=request.body,
        category="system",
        icon=request.icon,
        image=request.image,
        priority="normal"
    )

    return {
        "success": notification.status in ['sent', 'delivered'],
        "notification_id": str(notification.id),
        "status": notification.status,
        "message": "Test notification sent successfully" if notification.status == 'sent' else f"Notification status: {notification.status}"
    }


# ============================================================================
# Helper Endpoints for Common Notifications
# ============================================================================

@router.post("/send/friend-request")
async def send_friend_request_notification(
    friend_username: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send friend request notification (example helper)"""
    # Find friend
    friend = db.query(User).filter(User.username == friend_username).first()

    if not friend:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Send notification
    notification = await PushNotificationService.send_notification(
        db=db,
        user_id=str(friend.id),
        notification_type="friend_request",
        title="New Friend Request",
        body=f"{current_user.display_name or current_user.username} sent you a friend request",
        category="social",
        action_url="/friends/requests",
        priority="normal"
    )

    return {
        "success": True,
        "message": "Friend request notification sent"
    }
