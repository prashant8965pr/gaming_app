"""
Live Streaming Service
Handles live stream creation, management, and viewer interactions
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import secrets
import hashlib

from models.live_stream import LiveStream, StreamViewer, StreamChat, StreamDonation
from models.user import User
from models.wallet import Wallet, WalletTransaction


class LiveStreamService:
    """Service for live streaming management"""

    @staticmethod
    def generate_stream_key(user_id: str) -> str:
        """Generate unique stream key for broadcaster"""
        random_part = secrets.token_urlsafe(16)
        user_hash = hashlib.sha256(str(user_id).encode()).hexdigest()[:8]
        timestamp = int(datetime.utcnow().timestamp())
        return f"stream_{user_hash}_{timestamp}_{random_part}"

    @staticmethod
    def create_stream(
        db: Session,
        streamer_id: str,
        title: str,
        description: str = None,
        game_id: str = None,
        scheduled_start_time: datetime = None,
        is_public: bool = True,
        allow_chat: bool = True,
        is_monetized: bool = False,
        entry_fee: int = 0,
        tags: List[str] = None
    ) -> LiveStream:
        """Create a new live stream"""
        stream_key = LiveStreamService.generate_stream_key(streamer_id)

        # Generate URLs (in production, these would be from streaming service like AWS IVS, Agora, etc.)
        stream_url = f"rtmp://stream.yourgame.com/live/{stream_key}"
        playback_url = f"https://stream.yourgame.com/live/{stream_key}/index.m3u8"

        stream = LiveStream(
            streamer_id=streamer_id,
            game_id=game_id,
            title=title,
            description=description,
            stream_key=stream_key,
            stream_url=stream_url,
            playback_url=playback_url,
            scheduled_start_time=scheduled_start_time or datetime.utcnow(),
            is_public=is_public,
            allow_chat=allow_chat,
            is_monetized=is_monetized,
            entry_fee=entry_fee,
            tags=tags or [],
            status='scheduled'
        )

        db.add(stream)
        db.commit()
        db.refresh(stream)

        return stream

    @staticmethod
    def start_stream(db: Session, stream_id: str, streamer_id: str) -> LiveStream:
        """Start a scheduled stream"""
        stream = db.query(LiveStream).filter(
            and_(
                LiveStream.id == stream_id,
                LiveStream.streamer_id == streamer_id
            )
        ).first()

        if not stream:
            raise ValueError("Stream not found")

        if stream.status not in ['scheduled']:
            raise ValueError(f"Cannot start stream in status: {stream.status}")

        stream.status = 'live'
        stream.actual_start_time = datetime.utcnow()

        db.commit()
        db.refresh(stream)

        return stream

    @staticmethod
    def end_stream(db: Session, stream_id: str, streamer_id: str) -> LiveStream:
        """End a live stream"""
        stream = db.query(LiveStream).filter(
            and_(
                LiveStream.id == stream_id,
                LiveStream.streamer_id == streamer_id
            )
        ).first()

        if not stream:
            raise ValueError("Stream not found")

        if stream.status != 'live':
            raise ValueError("Stream is not live")

        stream.status = 'ended'
        stream.end_time = datetime.utcnow()

        # Calculate duration
        if stream.actual_start_time:
            duration = (stream.end_time - stream.actual_start_time).total_seconds()
            stream.duration_seconds = int(duration)

        # Update all active viewers
        active_viewers = db.query(StreamViewer).filter(
            and_(
                StreamViewer.stream_id == stream_id,
                StreamViewer.left_at == None
            )
        ).all()

        for viewer in active_viewers:
            viewer.left_at = datetime.utcnow()
            if viewer.joined_at:
                watch_duration = (viewer.left_at - viewer.joined_at).total_seconds()
                viewer.watch_duration_seconds = int(watch_duration)

        db.commit()
        db.refresh(stream)

        return stream

    @staticmethod
    def join_stream(db: Session, stream_id: str, user_id: str) -> Dict:
        """User joins a live stream"""
        stream = db.query(LiveStream).filter(LiveStream.id == stream_id).first()

        if not stream:
            raise ValueError("Stream not found")

        if stream.status != 'live':
            raise ValueError("Stream is not live")

        # Check if monetized
        if stream.is_monetized and stream.entry_fee > 0:
            # Check if already paid or joined
            existing_viewer = db.query(StreamViewer).filter(
                and_(
                    StreamViewer.stream_id == stream_id,
                    StreamViewer.user_id == user_id
                )
            ).first()

            if not existing_viewer or not existing_viewer.paid_entry_fee:
                # Deduct entry fee
                wallet = db.query(Wallet).filter(
                    and_(
                        Wallet.user_id == user_id,
                        Wallet.wallet_type == 'cash'
                    )
                ).first()

                if not wallet or wallet.balance < stream.entry_fee:
                    raise ValueError("Insufficient balance to join monetized stream")

                wallet.balance -= stream.entry_fee

                # Create transaction
                transaction = WalletTransaction(
                    user_id=user_id,
                    wallet_id=wallet.id,
                    amount=stream.entry_fee,
                    transaction_type='debit',
                    category='stream_entry',
                    description=f"Entry fee for stream: {stream.title}",
                    status='completed'
                )
                db.add(transaction)

                # Add to stream revenue
                stream.revenue_generated += stream.entry_fee

                # Create or update viewer record
                if existing_viewer:
                    existing_viewer.paid_entry_fee = True
                    existing_viewer.payment_amount = stream.entry_fee
                    existing_viewer.payment_transaction_id = transaction.id
                    existing_viewer.joined_at = datetime.utcnow()
                    viewer = existing_viewer
                else:
                    viewer = StreamViewer(
                        stream_id=stream_id,
                        user_id=user_id,
                        paid_entry_fee=True,
                        payment_amount=stream.entry_fee,
                        payment_transaction_id=transaction.id
                    )
                    db.add(viewer)
        else:
            # Free stream - check if already viewing
            viewer = db.query(StreamViewer).filter(
                and_(
                    StreamViewer.stream_id == stream_id,
                    StreamViewer.user_id == user_id
                )
            ).first()

            if not viewer:
                viewer = StreamViewer(
                    stream_id=stream_id,
                    user_id=user_id
                )
                db.add(viewer)
            else:
                # Rejoining
                viewer.joined_at = datetime.utcnow()
                viewer.left_at = None

        # Update viewer count
        current_viewers = db.query(StreamViewer).filter(
            and_(
                StreamViewer.stream_id == stream_id,
                StreamViewer.left_at == None
            )
        ).count()

        stream.viewer_count = current_viewers
        stream.total_views += 1

        if current_viewers > stream.peak_viewers:
            stream.peak_viewers = current_viewers

        db.commit()
        db.refresh(stream)

        return {
            "stream": stream.to_dict(),
            "playback_url": stream.playback_url,
            "allow_chat": stream.allow_chat
        }

    @staticmethod
    def leave_stream(db: Session, stream_id: str, user_id: str) -> Dict:
        """User leaves a live stream"""
        viewer = db.query(StreamViewer).filter(
            and_(
                StreamViewer.stream_id == stream_id,
                StreamViewer.user_id == user_id
            )
        ).first()

        if viewer:
            viewer.left_at = datetime.utcnow()

            # Calculate watch duration
            if viewer.joined_at:
                watch_duration = (viewer.left_at - viewer.joined_at).total_seconds()
                viewer.watch_duration_seconds += int(watch_duration)

            # Update stream viewer count
            stream = db.query(LiveStream).filter(LiveStream.id == stream_id).first()
            if stream:
                current_viewers = db.query(StreamViewer).filter(
                    and_(
                        StreamViewer.stream_id == stream_id,
                        StreamViewer.left_at == None
                    )
                ).count()
                stream.viewer_count = current_viewers

            db.commit()

        return {"success": True, "watch_duration": viewer.watch_duration_seconds if viewer else 0}

    @staticmethod
    def send_chat_message(
        db: Session,
        stream_id: str,
        user_id: str,
        message: str,
        message_type: str = 'text'
    ) -> StreamChat:
        """Send chat message in live stream"""
        stream = db.query(LiveStream).filter(LiveStream.id == stream_id).first()

        if not stream:
            raise ValueError("Stream not found")

        if not stream.allow_chat:
            raise ValueError("Chat is disabled for this stream")

        # Verify user is viewing the stream
        viewer = db.query(StreamViewer).filter(
            and_(
                StreamViewer.stream_id == stream_id,
                StreamViewer.user_id == user_id,
                StreamViewer.left_at == None
            )
        ).first()

        if not viewer:
            raise ValueError("Must be viewing the stream to chat")

        # Create chat message
        chat_message = StreamChat(
            stream_id=stream_id,
            user_id=user_id,
            message=message,
            message_type=message_type
        )

        db.add(chat_message)

        # Update viewer message count
        viewer.messages_sent += 1

        db.commit()
        db.refresh(chat_message)

        return chat_message

    @staticmethod
    def get_live_streams(
        db: Session,
        game_id: str = None,
        status: str = 'live',
        skip: int = 0,
        limit: int = 20
    ) -> List[Dict]:
        """Get list of live streams"""
        query = db.query(LiveStream, User).join(
            User, LiveStream.streamer_id == User.id
        )

        if status:
            query = query.filter(LiveStream.status == status)

        if game_id:
            query = query.filter(LiveStream.game_id == game_id)

        query = query.filter(LiveStream.is_public == True)
        query = query.order_by(desc(LiveStream.viewer_count))
        query = query.offset(skip).limit(limit)

        streams = query.all()

        result = []
        for stream, streamer in streams:
            stream_dict = stream.to_dict()
            stream_dict['streamer'] = {
                'id': str(streamer.id),
                'username': streamer.username,
                'display_name': streamer.display_name,
                'avatar': streamer.avatar
            }
            result.append(stream_dict)

        return result

    @staticmethod
    def like_stream(db: Session, stream_id: str, user_id: str) -> Dict:
        """Like a stream"""
        viewer = db.query(StreamViewer).filter(
            and_(
                StreamViewer.stream_id == stream_id,
                StreamViewer.user_id == user_id
            )
        ).first()

        if not viewer:
            raise ValueError("Must be viewing the stream to like")

        if not viewer.liked:
            viewer.liked = True

            stream = db.query(LiveStream).filter(LiveStream.id == stream_id).first()
            if stream:
                stream.like_count += 1

            db.commit()

        return {"success": True, "liked": True}

    @staticmethod
    def donate_to_streamer(
        db: Session,
        stream_id: str,
        donor_id: str,
        amount: int,
        message: str = None,
        is_anonymous: bool = False
    ) -> StreamDonation:
        """Donate to streamer during live stream"""
        stream = db.query(LiveStream).filter(LiveStream.id == stream_id).first()

        if not stream:
            raise ValueError("Stream not found")

        # Deduct from donor wallet
        wallet = db.query(Wallet).filter(
            and_(
                Wallet.user_id == donor_id,
                Wallet.wallet_type == 'cash'
            )
        ).first()

        if not wallet or wallet.balance < amount:
            raise ValueError("Insufficient balance")

        wallet.balance -= amount

        # Create transaction
        transaction = WalletTransaction(
            user_id=donor_id,
            wallet_id=wallet.id,
            amount=amount,
            transaction_type='debit',
            category='donation',
            description=f"Donation to stream: {stream.title}",
            status='completed'
        )
        db.add(transaction)

        # Credit to streamer (80% - 20% platform fee)
        streamer_share = int(amount * 0.80)
        streamer_wallet = db.query(Wallet).filter(
            and_(
                Wallet.user_id == stream.streamer_id,
                Wallet.wallet_type == 'winnings'
            )
        ).first()

        if streamer_wallet:
            streamer_wallet.balance += streamer_share

            streamer_transaction = WalletTransaction(
                user_id=stream.streamer_id,
                wallet_id=streamer_wallet.id,
                amount=streamer_share,
                transaction_type='credit',
                category='donation_received',
                description=f"Donation from viewer",
                status='completed'
            )
            db.add(streamer_transaction)

        # Create donation record
        donation = StreamDonation(
            stream_id=stream_id,
            donor_id=donor_id,
            streamer_id=stream.streamer_id,
            amount=amount,
            message=message,
            is_anonymous=is_anonymous,
            transaction_id=transaction.id,
            status='completed',
            was_highlighted=(amount >= 10000)  # Highlight donations of ₹100 or more
        )

        db.add(donation)

        # Update stream revenue
        stream.revenue_generated += amount

        db.commit()
        db.refresh(donation)

        return donation
