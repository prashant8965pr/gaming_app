"""
Push Notification Service
Handles sending push notifications via Firebase Cloud Messaging (FCM)
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import httpx
import json

from models.notification import (
    DeviceToken, PushNotification, NotificationPreference, NotificationTemplate
)
from models.user import User
from config.settings import settings


class PushNotificationService:
    """Service for managing push notifications"""

    FCM_API_URL = "https://fcm.googleapis.com/fcm/send"

    @staticmethod
    def register_device(
        db: Session,
        user_id: str,
        device_token: str,
        device_type: str,
        device_name: str = None,
        device_model: str = None,
        app_version: str = None,
        os_version: str = None
    ) -> DeviceToken:
        """Register a device for push notifications"""
        # Check if token already exists
        existing = db.query(DeviceToken).filter(
            DeviceToken.device_token == device_token
        ).first()

        if existing:
            # Update existing token
            existing.user_id = user_id
            existing.device_type = device_type
            existing.device_name = device_name
            existing.device_model = device_model
            existing.app_version = app_version
            existing.os_version = os_version
            existing.is_active = True
            existing.last_used_at = datetime.utcnow()

            db.commit()
            db.refresh(existing)
            return existing

        # Create new device token
        device = DeviceToken(
            user_id=user_id,
            device_token=device_token,
            device_type=device_type,
            device_name=device_name,
            device_model=device_model,
            app_version=app_version,
            os_version=os_version
        )

        db.add(device)
        db.commit()
        db.refresh(device)

        return device

    @staticmethod
    def unregister_device(db: Session, device_token: str) -> bool:
        """Unregister a device"""
        device = db.query(DeviceToken).filter(
            DeviceToken.device_token == device_token
        ).first()

        if device:
            device.is_active = False
            db.commit()
            return True

        return False

    @staticmethod
    def get_user_devices(db: Session, user_id: str, active_only: bool = True) -> List[DeviceToken]:
        """Get all devices for a user"""
        query = db.query(DeviceToken).filter(DeviceToken.user_id == user_id)

        if active_only:
            query = query.filter(DeviceToken.is_active == True, DeviceToken.enabled == True)

        return query.all()

    @staticmethod
    def get_or_create_preferences(db: Session, user_id: str) -> NotificationPreference:
        """Get or create notification preferences for user"""
        prefs = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id
        ).first()

        if not prefs:
            prefs = NotificationPreference(user_id=user_id)
            db.add(prefs)
            db.commit()
            db.refresh(prefs)

        return prefs

    @staticmethod
    def update_preferences(
        db: Session,
        user_id: str,
        preferences: Dict
    ) -> NotificationPreference:
        """Update notification preferences"""
        prefs = PushNotificationService.get_or_create_preferences(db, user_id)

        # Update preferences
        for key, value in preferences.items():
            if hasattr(prefs, key):
                setattr(prefs, key, value)

        db.commit()
        db.refresh(prefs)

        return prefs

    @staticmethod
    def should_send_notification(
        db: Session,
        user_id: str,
        category: str
    ) -> bool:
        """Check if notification should be sent based on user preferences"""
        prefs = PushNotificationService.get_or_create_preferences(db, user_id)

        # Check if push notifications are enabled
        if not prefs.push_enabled:
            return False

        # Check category preferences
        category_map = {
            'social': prefs.social_notifications,
            'gaming': prefs.gaming_notifications,
            'financial': prefs.financial_notifications,
            'promotional': prefs.promotional_notifications,
            'system': prefs.system_notifications
        }

        if category in category_map and not category_map[category]:
            return False

        # Check quiet hours
        if prefs.quiet_hours_enabled and prefs.quiet_hours_start and prefs.quiet_hours_end:
            now_time = datetime.utcnow().time()
            start_time = datetime.strptime(prefs.quiet_hours_start, "%H:%M").time()
            end_time = datetime.strptime(prefs.quiet_hours_end, "%H:%M").time()

            if start_time <= end_time:
                # Same day range (e.g., 08:00 - 22:00)
                if start_time <= now_time <= end_time:
                    return False
            else:
                # Overnight range (e.g., 22:00 - 08:00)
                if now_time >= start_time or now_time <= end_time:
                    return False

        return True

    @staticmethod
    async def send_fcm_notification(
        device_tokens: List[str],
        title: str,
        body: str,
        data: Dict = None,
        icon: str = None,
        image: str = None,
        priority: str = "normal"
    ) -> Dict:
        """Send notification via Firebase Cloud Messaging"""
        if not device_tokens:
            return {"success": False, "error": "No device tokens provided"}

        # FCM server key from environment
        fcm_server_key = getattr(settings, 'FCM_SERVER_KEY', None)

        if not fcm_server_key:
            return {"success": False, "error": "FCM server key not configured"}

        # Build FCM payload
        notification_payload = {
            "title": title,
            "body": body
        }

        if icon:
            notification_payload["icon"] = icon

        if image:
            notification_payload["image"] = image

        # Set priority
        priority_map = {
            "low": "normal",
            "normal": "high",
            "high": "high",
            "urgent": "high"
        }
        fcm_priority = priority_map.get(priority, "high")

        # Send to multiple devices
        headers = {
            "Authorization": f"key={fcm_server_key}",
            "Content-Type": "application/json"
        }

        results = []

        async with httpx.AsyncClient() as client:
            for token in device_tokens:
                payload = {
                    "to": token,
                    "priority": fcm_priority,
                    "notification": notification_payload,
                    "data": data or {}
                }

                try:
                    response = await client.post(
                        PushNotificationService.FCM_API_URL,
                        headers=headers,
                        json=payload,
                        timeout=10.0
                    )

                    if response.status_code == 200:
                        result = response.json()
                        results.append({
                            "token": token,
                            "success": result.get("success", 0) > 0,
                            "message_id": result.get("results", [{}])[0].get("message_id")
                        })
                    else:
                        results.append({
                            "token": token,
                            "success": False,
                            "error": f"HTTP {response.status_code}"
                        })

                except Exception as e:
                    results.append({
                        "token": token,
                        "success": False,
                        "error": str(e)
                    })

        success_count = sum(1 for r in results if r.get("success"))

        return {
            "success": success_count > 0,
            "total": len(device_tokens),
            "success_count": success_count,
            "failed_count": len(device_tokens) - success_count,
            "results": results
        }

    @staticmethod
    async def send_notification(
        db: Session,
        user_id: str,
        notification_type: str,
        title: str,
        body: str,
        category: str = "general",
        action_url: str = None,
        action_data: Dict = None,
        icon: str = None,
        image: str = None,
        priority: str = "normal",
        scheduled_for: datetime = None
    ) -> PushNotification:
        """Send push notification to a user"""
        # Check if user should receive notification
        if not PushNotificationService.should_send_notification(db, user_id, category):
            # Create notification record but don't send
            notification = PushNotification(
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                body=body,
                category=category,
                action_url=action_url,
                action_data=action_data,
                icon=icon,
                image=image,
                priority=priority,
                status='skipped'
            )
            db.add(notification)
            db.commit()
            return notification

        # Create notification record
        notification = PushNotification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            body=body,
            category=category,
            action_url=action_url,
            action_data=action_data,
            icon=icon,
            image=image,
            priority=priority,
            scheduled_for=scheduled_for,
            status='pending'
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        # If scheduled for future, return
        if scheduled_for and scheduled_for > datetime.utcnow():
            return notification

        # Get user's active devices
        devices = PushNotificationService.get_user_devices(db, user_id, active_only=True)

        if not devices:
            notification.status = 'failed'
            notification.error_message = "No active devices found"
            notification.failed_at = datetime.utcnow()
            db.commit()
            return notification

        # Extract device tokens
        device_tokens = [device.device_token for device in devices]

        # Prepare data payload
        data_payload = action_data or {}
        if action_url:
            data_payload['action_url'] = action_url

        # Send via FCM
        result = await PushNotificationService.send_fcm_notification(
            device_tokens=device_tokens,
            title=title,
            body=body,
            data=data_payload,
            icon=icon,
            image=image,
            priority=priority
        )

        # Update notification status
        if result.get("success"):
            notification.status = 'sent'
            notification.sent_at = datetime.utcnow()

            # Store FCM message ID if available
            if result.get("results"):
                first_success = next(
                    (r for r in result["results"] if r.get("success")),
                    None
                )
                if first_success and first_success.get("message_id"):
                    notification.fcm_message_id = first_success["message_id"]
        else:
            notification.status = 'failed'
            notification.failed_at = datetime.utcnow()
            notification.error_message = result.get("error", "Unknown error")

        db.commit()
        db.refresh(notification)

        return notification

    @staticmethod
    async def send_notification_from_template(
        db: Session,
        user_id: str,
        template_code: str,
        variables: Dict = None,
        action_url: str = None,
        scheduled_for: datetime = None
    ) -> PushNotification:
        """Send notification using a template"""
        # Get template
        template = db.query(NotificationTemplate).filter(
            and_(
                NotificationTemplate.template_code == template_code,
                NotificationTemplate.is_active == True
            )
        ).first()

        if not template:
            raise ValueError(f"Template not found: {template_code}")

        # Replace variables in template
        title = template.title_template
        body = template.body_template

        if variables:
            for key, value in variables.items():
                title = title.replace(f"{{{key}}}", str(value))
                body = body.replace(f"{{{key}}}", str(value))

        # Send notification
        return await PushNotificationService.send_notification(
            db=db,
            user_id=user_id,
            notification_type=template.notification_type,
            title=title,
            body=body,
            category=template.category,
            action_url=action_url or template.default_action_url,
            icon=template.icon_url,
            image=template.image_url,
            priority=template.default_priority,
            scheduled_for=scheduled_for
        )

    @staticmethod
    def get_user_notifications(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
        unread_only: bool = False
    ) -> List[PushNotification]:
        """Get notifications for a user"""
        query = db.query(PushNotification).filter(
            PushNotification.user_id == user_id
        )

        if unread_only:
            query = query.filter(PushNotification.clicked_at == None)

        query = query.order_by(desc(PushNotification.created_at))
        query = query.offset(skip).limit(limit)

        return query.all()

    @staticmethod
    def mark_notification_clicked(
        db: Session,
        notification_id: str,
        user_id: str
    ) -> PushNotification:
        """Mark notification as clicked/read"""
        notification = db.query(PushNotification).filter(
            and_(
                PushNotification.id == notification_id,
                PushNotification.user_id == user_id
            )
        ).first()

        if notification and not notification.clicked_at:
            notification.clicked_at = datetime.utcnow()
            notification.status = 'clicked'
            db.commit()
            db.refresh(notification)

        return notification

    @staticmethod
    def get_unread_count(db: Session, user_id: str) -> int:
        """Get count of unread notifications"""
        return db.query(PushNotification).filter(
            and_(
                PushNotification.user_id == user_id,
                PushNotification.clicked_at == None,
                PushNotification.status.in_(['sent', 'delivered'])
            )
        ).count()
