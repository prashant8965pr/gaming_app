"""
Chat service for messaging functionality
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta
from typing import List, Optional, Dict

from models.chat import Conversation, Message, MessageReadReceipt, TypingIndicator
from models.user import User


class ChatService:
    """Service for chat management"""

    @staticmethod
    def get_or_create_conversation(db: Session, user1_id: str, user2_id: str) -> Conversation:
        """Get or create direct conversation between two users"""
        # Check both orderings
        conversation = db.query(Conversation).filter(
            or_(
                and_(
                    Conversation.user1_id == user1_id,
                    Conversation.user2_id == user2_id
                ),
                and_(
                    Conversation.user1_id == user2_id,
                    Conversation.user2_id == user1_id
                )
            ),
            Conversation.conversation_type == 'direct'
        ).first()

        if not conversation:
            conversation = Conversation(
                conversation_type='direct',
                user1_id=user1_id,
                user2_id=user2_id
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        return conversation

    @staticmethod
    def get_user_conversations(db: Session, user_id: str, skip: int = 0, limit: int = 20) -> List[Dict]:
        """Get all conversations for a user"""
        conversations = db.query(Conversation).filter(
            or_(
                Conversation.user1_id == user_id,
                Conversation.user2_id == user_id
            )
        ).order_by(desc(Conversation.last_message_at)).offset(skip).limit(limit).all()

        result = []
        for conv in conversations:
            # Get other user info
            other_user_id = conv.user2_id if conv.user1_id == user_id else conv.user1_id
            other_user = db.query(User).filter(User.id == other_user_id).first()

            # Get unread count
            unread_count = ChatService.get_unread_count(db, conv.id, user_id)

            # Get last message
            last_message = db.query(Message).filter(
                Message.conversation_id == conv.id
            ).order_by(desc(Message.sent_at)).first()

            conv_dict = conv.to_dict(current_user_id=user_id)
            conv_dict['other_user'] = {
                'id': str(other_user.id),
                'username': other_user.username,
                'avatar': other_user.avatar,
            } if other_user else None
            conv_dict['unread_count'] = unread_count
            conv_dict['last_message'] = last_message.to_dict() if last_message else None

            result.append(conv_dict)

        return result

    @staticmethod
    def send_message(
        db: Session,
        conversation_id: str,
        sender_id: str,
        content: str,
        message_type: str = 'text',
        metadata: Dict = None
    ) -> Message:
        """Send a message in a conversation"""
        # Verify sender is part of conversation
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise ValueError("Conversation not found")

        if sender_id not in [str(conversation.user1_id), str(conversation.user2_id)]:
            raise ValueError("User not part of conversation")

        # Create message
        message = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            message_type=message_type,
            content=content,
            metadata=metadata
        )

        db.add(message)

        # Update conversation last message
        conversation.last_message_id = message.id
        conversation.last_message_at = message.sent_at
        conversation.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(message)

        return message

    @staticmethod
    def get_messages(
        db: Session,
        conversation_id: str,
        user_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Message]:
        """Get messages in a conversation"""
        # Verify user is part of conversation
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise ValueError("Conversation not found")

        if user_id not in [str(conversation.user1_id), str(conversation.user2_id)]:
            raise ValueError("User not part of conversation")

        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.is_deleted == False
        ).order_by(desc(Message.sent_at)).offset(skip).limit(limit).all()

        # Reverse to show oldest first
        return list(reversed(messages))

    @staticmethod
    def mark_messages_as_read(db: Session, conversation_id: str, user_id: str) -> int:
        """Mark all messages in a conversation as read"""
        # Get all unread messages
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.sender_id != user_id
        ).all()

        count = 0
        for message in messages:
            # Check if already read
            existing = db.query(MessageReadReceipt).filter(
                and_(
                    MessageReadReceipt.message_id == message.id,
                    MessageReadReceipt.user_id == user_id
                )
            ).first()

            if not existing:
                receipt = MessageReadReceipt(
                    message_id=message.id,
                    user_id=user_id
                )
                db.add(receipt)
                count += 1

        db.commit()
        return count

    @staticmethod
    def get_unread_count(db: Session, conversation_id: str, user_id: str) -> int:
        """Get count of unread messages in a conversation"""
        # Get messages from other user
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.sender_id != user_id
        ).all()

        unread_count = 0
        for message in messages:
            # Check if read
            receipt = db.query(MessageReadReceipt).filter(
                and_(
                    MessageReadReceipt.message_id == message.id,
                    MessageReadReceipt.user_id == user_id
                )
            ).first()

            if not receipt:
                unread_count += 1

        return unread_count

    @staticmethod
    def edit_message(db: Session, message_id: str, user_id: str, new_content: str) -> Message:
        """Edit a message"""
        message = db.query(Message).filter(Message.id == message_id).first()

        if not message:
            raise ValueError("Message not found")

        if str(message.sender_id) != user_id:
            raise ValueError("Can only edit your own messages")

        message.content = new_content
        message.is_edited = True
        message.edited_at = datetime.utcnow()

        db.commit()
        db.refresh(message)

        return message

    @staticmethod
    def delete_message(db: Session, message_id: str, user_id: str) -> Message:
        """Delete a message (soft delete)"""
        message = db.query(Message).filter(Message.id == message_id).first()

        if not message:
            raise ValueError("Message not found")

        if str(message.sender_id) != user_id:
            raise ValueError("Can only delete your own messages")

        message.is_deleted = True
        message.content = "[Message deleted]"

        db.commit()
        db.refresh(message)

        return message

    @staticmethod
    def set_typing_indicator(db: Session, conversation_id: str, user_id: str) -> TypingIndicator:
        """Set typing indicator for user in conversation"""
        # Remove old indicator
        db.query(TypingIndicator).filter(
            and_(
                TypingIndicator.conversation_id == conversation_id,
                TypingIndicator.user_id == user_id
            )
        ).delete()

        # Create new indicator
        indicator = TypingIndicator(
            conversation_id=conversation_id,
            user_id=user_id,
            expires_at=datetime.utcnow() + timedelta(seconds=5)
        )

        db.add(indicator)
        db.commit()
        db.refresh(indicator)

        return indicator

    @staticmethod
    def get_typing_users(db: Session, conversation_id: str, exclude_user_id: str) -> List[Dict]:
        """Get users currently typing in a conversation"""
        now = datetime.utcnow()

        indicators = db.query(TypingIndicator).filter(
            and_(
                TypingIndicator.conversation_id == conversation_id,
                TypingIndicator.user_id != exclude_user_id,
                TypingIndicator.expires_at > now
            )
        ).all()

        result = []
        for indicator in indicators:
            user = db.query(User).filter(User.id == indicator.user_id).first()
            if user:
                result.append({
                    'user_id': str(user.id),
                    'username': user.username,
                })

        return result

    @staticmethod
    def search_messages(
        db: Session,
        user_id: str,
        query: str,
        limit: int = 20
    ) -> List[Dict]:
        """Search messages across all user's conversations"""
        # Get user's conversations
        conversations = db.query(Conversation).filter(
            or_(
                Conversation.user1_id == user_id,
                Conversation.user2_id == user_id
            )
        ).all()

        conversation_ids = [str(conv.id) for conv in conversations]

        # Search messages
        messages = db.query(Message).filter(
            Message.conversation_id.in_(conversation_ids),
            Message.content.ilike(f'%{query}%'),
            Message.is_deleted == False
        ).order_by(desc(Message.sent_at)).limit(limit).all()

        result = []
        for message in messages:
            message_dict = message.to_dict()

            # Get conversation info
            conversation = db.query(Conversation).filter(
                Conversation.id == message.conversation_id
            ).first()

            if conversation:
                other_user_id = conversation.user2_id if conversation.user1_id == user_id else conversation.user1_id
                other_user = db.query(User).filter(User.id == other_user_id).first()

                message_dict['conversation'] = {
                    'id': str(conversation.id),
                    'other_user': {
                        'id': str(other_user.id),
                        'username': other_user.username,
                    } if other_user else None
                }

            result.append(message_dict)

        return result
