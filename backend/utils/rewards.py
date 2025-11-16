"""
Rewards Calculation Utilities
Helper functions for calculating rewards, achievements, levels, etc.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
import math


class RewardCalculator:
    """Calculator for various reward types"""

    # Daily bonus amounts for 7-day cycle (in rupees)
    DAILY_BONUS_AMOUNTS = [10, 15, 20, 25, 30, 40, 50]

    # Referral rewards (in rupees)
    REFERRER_REWARD_BASE = 100  # Base reward for referrer
    REFERRED_REWARD_BASE = 50   # Base reward for referred user
    REFERRER_DEPOSIT_BONUS_PERCENT = 10  # 10% of first deposit

    # Level progression
    BASE_XP_PER_LEVEL = 100
    XP_MULTIPLIER = 1.5

    # Achievement points to XP conversion
    ACHIEVEMENT_POINTS_TO_XP = 10

    @staticmethod
    def calculate_daily_bonus(current_streak: int, last_claim_date: datetime = None) -> Tuple[bool, int, int]:
        """
        Calculate daily bonus
        Returns: (can_claim, bonus_amount_paise, next_day_number)
        """
        today = datetime.utcnow().date()

        # Check if can claim today
        can_claim = True
        if last_claim_date:
            last_claim = last_claim_date.date()

            # Already claimed today
            if last_claim == today:
                can_claim = False

            # Streak broken (missed yesterday)
            elif last_claim < today - timedelta(days=1):
                current_streak = 0

        # Calculate next day in cycle (1-7)
        next_day = (current_streak % 7) + 1

        # Get bonus amount
        bonus_amount = RewardCalculator.DAILY_BONUS_AMOUNTS[next_day - 1]
        bonus_amount_paise = int(bonus_amount * 100)

        return can_claim, bonus_amount_paise, next_day

    @staticmethod
    def get_daily_bonus_calendar(current_streak: int) -> List[Dict[str, Any]]:
        """
        Get 7-day bonus calendar
        Returns list of day bonuses with status
        """
        calendar = []
        current_day = (current_streak % 7) + 1

        for day in range(1, 8):
            calendar.append({
                "day": day,
                "amount": RewardCalculator.DAILY_BONUS_AMOUNTS[day - 1],
                "is_current": day == current_day,
                "is_completed": day < current_day or (current_streak >= 7 and day <= current_day),
                "is_locked": day > current_day
            })

        return calendar

    @staticmethod
    def calculate_referral_reward(first_deposit_amount: int = 0) -> Tuple[int, int]:
        """
        Calculate referral rewards for both referrer and referred user
        Returns: (referrer_reward_paise, referred_reward_paise)
        """
        # Base rewards
        referrer_reward = RewardCalculator.REFERRER_REWARD_BASE * 100  # Convert to paise
        referred_reward = RewardCalculator.REFERRED_REWARD_BASE * 100

        # Add bonus for referrer based on referred user's first deposit
        if first_deposit_amount > 0:
            deposit_bonus = int(first_deposit_amount * RewardCalculator.REFERRER_DEPOSIT_BONUS_PERCENT / 100)
            # Cap at 500 rupees
            deposit_bonus = min(deposit_bonus, 50000)
            referrer_reward += deposit_bonus

        return referrer_reward, referred_reward

    @staticmethod
    def calculate_xp_for_level(level: int) -> int:
        """
        Calculate total XP required to reach a specific level
        """
        if level <= 1:
            return 0

        total_xp = 0
        for lvl in range(1, level):
            total_xp += RewardCalculator.calculate_xp_for_next_level(lvl)

        return total_xp

    @staticmethod
    def calculate_xp_for_next_level(current_level: int) -> int:
        """
        Calculate XP required to reach next level from current level
        """
        return int(RewardCalculator.BASE_XP_PER_LEVEL * (RewardCalculator.XP_MULTIPLIER ** (current_level - 1)))

    @staticmethod
    def calculate_level_from_xp(total_xp: int) -> Tuple[int, int, int, float]:
        """
        Calculate level and progress from total XP
        Returns: (level, xp_at_current_level, xp_for_next_level, progress_percentage)
        """
        level = 1
        xp_accumulated = 0

        while True:
            xp_for_next = RewardCalculator.calculate_xp_for_next_level(level)

            if xp_accumulated + xp_for_next > total_xp:
                # Found the current level
                xp_at_current_level = total_xp - xp_accumulated
                progress_percentage = (xp_at_current_level / xp_for_next) * 100
                return level, xp_at_current_level, xp_for_next, progress_percentage

            xp_accumulated += xp_for_next
            level += 1

            # Safety limit
            if level > 100:
                break

        return level, 0, 0, 0.0

    @staticmethod
    def get_level_perks(level: int) -> List[str]:
        """
        Get unlocked perks for a specific level
        """
        perks = []

        if level >= 5:
            perks.append("higher_withdrawal_limit")
        if level >= 10:
            perks.append("priority_support")
        if level >= 15:
            perks.append("exclusive_tournaments")
        if level >= 20:
            perks.append("vip_badge")
        if level >= 25:
            perks.append("reduced_fees")
        if level >= 30:
            perks.append("early_access")
        if level >= 40:
            perks.append("custom_avatar")
        if level >= 50:
            perks.append("legendary_status")

        return perks

    @staticmethod
    def check_achievement_criteria(criteria: Dict[str, Any], user_stats: Dict[str, Any]) -> Tuple[bool, int, int]:
        """
        Check if achievement criteria is met
        Returns: (is_complete, current_progress, target)
        """
        if not criteria:
            return False, 0, 100

        criteria_type = criteria.get("type")
        target = criteria.get("count", 100)

        if criteria_type == "win_streak":
            current = user_stats.get("current_streak", 0)
            return current >= target, current, target

        elif criteria_type == "total_games":
            current = user_stats.get("total_games_played", 0)
            return current >= target, current, target

        elif criteria_type == "total_wins":
            current = user_stats.get("total_games_won", 0)
            return current >= target, current, target

        elif criteria_type == "referrals":
            current = user_stats.get("total_referrals", 0)
            return current >= target, current, target

        elif criteria_type == "total_winnings":
            # Target in rupees, current in paise
            current = user_stats.get("total_winnings", 0) / 100
            return current >= target, int(current), target

        elif criteria_type == "win_rate":
            # Target is percentage
            games_played = user_stats.get("total_games_played", 0)
            if games_played == 0:
                return False, 0, target
            games_won = user_stats.get("total_games_won", 0)
            win_rate = (games_won / games_played) * 100
            return win_rate >= target, int(win_rate), target

        elif criteria_type == "level":
            current = user_stats.get("current_level", 1)
            return current >= target, current, target

        return False, 0, target

    @staticmethod
    def calculate_promo_discount(
        promo_type: str,
        discount_type: str,
        discount_value: float,
        order_amount: float,
        max_discount: float = None,
        min_deposit: float = None
    ) -> Tuple[bool, float, str]:
        """
        Calculate promo code discount
        Returns: (is_valid, discount_amount, message)
        """
        # Check minimum deposit
        if min_deposit and order_amount < min_deposit:
            return False, 0.0, f"Minimum deposit of Rs.{min_deposit} required"

        discount_amount = 0.0

        if discount_type == "percentage":
            discount_amount = (order_amount * discount_value) / 100

            # Apply max discount cap
            if max_discount:
                discount_amount = min(discount_amount, max_discount)

        elif discount_type == "fixed":
            discount_amount = discount_value

            # Cannot exceed order amount
            if discount_amount > order_amount:
                discount_amount = order_amount

        elif discount_type == "free":
            discount_amount = order_amount

        return True, discount_amount, f"Discount of Rs.{discount_amount:.2f} applied"


class LeaderboardCalculator:
    """Calculator for leaderboard rankings"""

    @staticmethod
    def calculate_rank_change(old_rank: int, new_rank: int) -> int:
        """
        Calculate rank change (positive for improvement, negative for drop)
        """
        if old_rank is None or old_rank == 0:
            return 0

        # Lower rank number is better (1 is top)
        return old_rank - new_rank

    @staticmethod
    def get_period_dates(board_type: str) -> Tuple[datetime, datetime]:
        """
        Get start and end dates for leaderboard period
        """
        now = datetime.utcnow()

        if board_type == "daily":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)

        elif board_type == "weekly":
            # Week starts on Monday
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=7)

        elif board_type == "monthly":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            # Next month
            if now.month == 12:
                end = start.replace(year=now.year + 1, month=1)
            else:
                end = start.replace(month=now.month + 1)

        else:  # all_time
            start = datetime(2024, 1, 1)  # Platform launch date
            end = now + timedelta(days=365)

        return start, end

    @staticmethod
    def calculate_leaderboard_rewards(rank: int, board_type: str) -> int:
        """
        Calculate reward for leaderboard rank (in paise)
        """
        if board_type == "daily":
            rewards = {
                1: 50000,   # �500
                2: 30000,   # �300
                3: 20000,   # �200
                4: 10000,   # �100
                5: 10000,
            }
        elif board_type == "weekly":
            rewards = {
                1: 500000,  # �5000
                2: 300000,  # �3000
                3: 200000,  # �2000
                4: 100000,  # �1000
                5: 100000,
                6: 50000,
                7: 50000,
                8: 50000,
                9: 50000,
                10: 50000,
            }
        elif board_type == "monthly":
            rewards = {
                1: 5000000,  # �50,000
                2: 3000000,  # �30,000
                3: 2000000,  # �20,000
                4: 1000000,  # �10,000
                5: 1000000,
                6: 500000,
                7: 500000,
                8: 500000,
                9: 500000,
                10: 500000,
            }
        else:  # all_time
            rewards = {
                1: 10000000,  # �1,00,000
                2: 5000000,   # �50,000
                3: 3000000,   # �30,000
            }

        return rewards.get(rank, 0)


# Singleton instances
reward_calculator = RewardCalculator()
leaderboard_calculator = LeaderboardCalculator()
