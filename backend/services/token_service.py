"""
Token system service for practice games and rewards
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from models.token import TokenWallet, TokenTransaction


class TokenService:
    """Service for token management"""
    
    @staticmethod
    def get_or_create_wallet(db: Session, user_id: str) -> TokenWallet:
        """Get or create token wallet for user"""
        wallet = db.query(TokenWallet).filter(TokenWallet.user_id == user_id).first()
        
        if not wallet:
            wallet = TokenWallet(user_id=user_id, balance=100)  # Welcome bonus
            db.add(wallet)
            db.commit()
            db.refresh(wallet)
        
        return wallet
    
    @staticmethod
    def claim_daily_bonus(db: Session, user_id: str) -> dict:
        """Claim daily login bonus"""
        wallet = TokenService.get_or_create_wallet(db, user_id)
        
        now = datetime.utcnow()
        
        # Check if already claimed today
        if wallet.last_daily_claim and wallet.last_daily_claim.date() == now.date():
            raise ValueError("Daily bonus already claimed today")
        
        # Calculate streak
        if wallet.last_daily_claim:
            days_diff = (now.date() - wallet.last_daily_claim.date()).days
            if days_diff == 1:
                wallet.daily_claim_streak += 1
            else:
                wallet.daily_claim_streak = 1
        else:
            wallet.daily_claim_streak = 1
        
        # Calculate bonus amount (increases with streak)
        base_bonus = 100
        streak_bonus = min(wallet.daily_claim_streak * 10, 100)  # Max 100 extra
        total_bonus = base_bonus + streak_bonus
        
        # Add tokens
        wallet.balance += total_bonus
        wallet.total_earned += total_bonus
        wallet.last_daily_claim = now
        
        # Create transaction
        transaction = TokenTransaction(
            user_id=user_id,
            wallet_id=wallet.id,
            amount=total_bonus,
            transaction_type='earn',
            source='daily_login',
            description=f"Daily login bonus (Day {wallet.daily_claim_streak})",
            balance_after=wallet.balance
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(wallet)
        
        return {
            "tokens_earned": total_bonus,
            "current_streak": wallet.daily_claim_streak,
            "new_balance": wallet.balance
        }
    
    @staticmethod
    def earn_from_ad(db: Session, user_id: str) -> dict:
        """Earn tokens from watching ad"""
        wallet = TokenService.get_or_create_wallet(db, user_id)
        
        now = datetime.utcnow()
        
        # Reset counter if new day
        if wallet.ads_reset_date and wallet.ads_reset_date.date() < now.date():
            wallet.ads_watched_today = 0
            wallet.ads_reset_date = now
        elif not wallet.ads_reset_date:
            wallet.ads_reset_date = now
        
        # Check limit
        if wallet.ads_watched_today >= 5:
            raise ValueError("Daily ad watch limit reached (5/day)")
        
        # Award tokens
        ad_reward = 50
        wallet.balance += ad_reward
        wallet.total_earned += ad_reward
        wallet.ads_watched_today += 1
        wallet.last_ad_watch = now
        
        # Create transaction
        transaction = TokenTransaction(
            user_id=user_id,
            wallet_id=wallet.id,
            amount=ad_reward,
            transaction_type='earn',
            source='ad_watch',
            description=f"Watched ad ({wallet.ads_watched_today}/5)",
            balance_after=wallet.balance
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(wallet)
        
        return {
            "tokens_earned": ad_reward,
            "ads_watched_today": wallet.ads_watched_today,
            "ads_remaining": 5 - wallet.ads_watched_today,
            "new_balance": wallet.balance
        }
    
    @staticmethod
    def spend_tokens(db: Session, user_id: str, amount: int, source: str, description: str) -> TokenWallet:
        """Spend tokens"""
        wallet = TokenService.get_or_create_wallet(db, user_id)
        
        if wallet.balance < amount:
            raise ValueError("Insufficient token balance")
        
        wallet.balance -= amount
        wallet.total_spent += amount
        
        transaction = TokenTransaction(
            user_id=user_id,
            wallet_id=wallet.id,
            amount=-amount,
            transaction_type='spend',
            source=source,
            description=description,
            balance_after=wallet.balance
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(wallet)
        
        return wallet
