"""
Game Logic Utilities
Helper functions for game management, prize distribution, and XP calculation
"""
from typing import Dict, Any, List, Tuple
import random
import string
from datetime import datetime, timedelta


class GameManager:
    """Manager for game session operations"""

    # XP rewards based on game result
    XP_FOR_WIN = 100
    XP_FOR_SECOND = 60
    XP_FOR_THIRD = 40
    XP_FOR_PARTICIPATION = 20

    # Platform fee
    DEFAULT_PLATFORM_FEE_PERCENTAGE = 5.0  # 5%

    @staticmethod
    def generate_session_code(length: int = 8) -> str:
        """Generate unique session code for game room"""
        characters = string.ascii_uppercase + string.digits
        # Exclude similar looking characters
        characters = characters.replace('O', '').replace('0', '').replace('I', '').replace('1', '')
        return ''.join(random.choice(characters) for _ in range(length))

    @staticmethod
    def calculate_prize_distribution(
        total_prize_pool: int,
        num_players: int,
        prize_distribution_config: Dict[str, Any]
    ) -> Dict[int, int]:
        """
        Calculate prize amounts for each rank
        Returns: {rank: prize_amount_in_paise}
        """
        prizes = {}

        # Default distribution if not configured
        if not prize_distribution_config:
            if num_players == 2:
                prize_distribution_config = {"1st": 100}
            elif num_players == 3:
                prize_distribution_config = {"1st": 70, "2nd": 30}
            else:
                prize_distribution_config = {"1st": 50, "2nd": 30, "3rd": 20}

        # Calculate prizes based on percentages
        for position, percentage in prize_distribution_config.items():
            rank = int(position.replace("st", "").replace("nd", "").replace("rd", "").replace("th", ""))

            if rank <= num_players:
                prize_amount = int(total_prize_pool * (percentage / 100))
                prizes[rank] = prize_amount

        return prizes

    @staticmethod
    def calculate_platform_fee(
        total_entry_fees: int,
        platform_fee_percentage: float = None
    ) -> int:
        """Calculate platform commission"""
        if platform_fee_percentage is None:
            platform_fee_percentage = GameManager.DEFAULT_PLATFORM_FEE_PERCENTAGE

        return int(total_entry_fees * (platform_fee_percentage / 100))

    @staticmethod
    def calculate_prize_pool(
        total_entry_fees: int,
        platform_fee_percentage: float = None
    ) -> Tuple[int, int]:
        """
        Calculate prize pool after platform fee
        Returns: (prize_pool, platform_fee)
        """
        platform_fee = GameManager.calculate_platform_fee(total_entry_fees, platform_fee_percentage)
        prize_pool = total_entry_fees - platform_fee
        return prize_pool, platform_fee

    @staticmethod
    def calculate_xp_reward(rank: int, total_players: int, game_duration_minutes: int = 10) -> int:
        """
        Calculate XP reward based on rank and game
        """
        base_xp = 0

        if rank == 1:
            base_xp = GameManager.XP_FOR_WIN
        elif rank == 2:
            base_xp = GameManager.XP_FOR_SECOND
        elif rank == 3:
            base_xp = GameManager.XP_FOR_THIRD
        else:
            base_xp = GameManager.XP_FOR_PARTICIPATION

        # Bonus XP for longer games
        duration_multiplier = 1.0
        if game_duration_minutes > 20:
            duration_multiplier = 1.5
        elif game_duration_minutes > 10:
            duration_multiplier = 1.2

        # Bonus XP for more players
        player_multiplier = 1.0 + (total_players - 2) * 0.1  # +10% per additional player over 2

        total_xp = int(base_xp * duration_multiplier * player_multiplier)
        return total_xp

    @staticmethod
    def check_achievement_unlock(
        user_stats: Dict[str, Any],
        game_result: Dict[str, Any]
    ) -> List[str]:
        """
        Check if any achievements should be unlocked
        Returns: List of achievement codes
        """
        achievements_unlocked = []

        # First Win achievement
        if game_result.get("rank") == 1 and user_stats.get("total_wins", 0) == 1:
            achievements_unlocked.append("FIRST_GAME_WIN")

        # Win Streak achievements
        current_streak = user_stats.get("current_win_streak", 0)
        if current_streak == 3:
            achievements_unlocked.append("WIN_STREAK_3")
        elif current_streak == 5:
            achievements_unlocked.append("WIN_STREAK_5")
        elif current_streak == 10:
            achievements_unlocked.append("WIN_STREAK_10")

        # Total Games achievements
        total_games = user_stats.get("total_games_played", 0)
        if total_games == 10:
            achievements_unlocked.append("GAMES_PLAYED_10")
        elif total_games == 50:
            achievements_unlocked.append("GAMES_PLAYED_50")
        elif total_games == 100:
            achievements_unlocked.append("GAMES_PLAYED_100")

        # Total Wins achievements
        total_wins = user_stats.get("total_wins", 0)
        if total_wins == 10:
            achievements_unlocked.append("WINS_10")
        elif total_wins == 50:
            achievements_unlocked.append("WINS_50")
        elif total_wins == 100:
            achievements_unlocked.append("WINS_100")

        # Winnings achievements
        total_winnings = user_stats.get("total_winnings", 0)
        if total_winnings >= 100000:  # Rs.1000
            achievements_unlocked.append("WINNINGS_1K")
        elif total_winnings >= 1000000:  # Rs.10000
            achievements_unlocked.append("WINNINGS_10K")

        return achievements_unlocked

    @staticmethod
    def calculate_turn_deadline(base_seconds: int = 30) -> datetime:
        """Calculate deadline for next turn"""
        return datetime.utcnow() + timedelta(seconds=base_seconds)

    @staticmethod
    def is_turn_expired(deadline: datetime) -> bool:
        """Check if turn has expired"""
        if not deadline:
            return False
        return datetime.utcnow() > deadline

    @staticmethod
    def assign_player_colors(num_players: int) -> List[str]:
        """Assign colors to players"""
        colors = ["red", "blue", "green", "yellow", "purple", "orange", "pink", "brown"]
        return colors[:num_players]

    @staticmethod
    def validate_entry_fee(
        entry_fee: int,
        min_fee: int,
        max_fee: int = None
    ) -> Tuple[bool, str]:
        """Validate entry fee for a game"""
        if entry_fee < min_fee:
            return False, f"Minimum entry fee is Rs.{min_fee / 100}"

        if max_fee and entry_fee > max_fee:
            return False, f"Maximum entry fee is Rs.{max_fee / 100}"

        return True, "Valid entry fee"


class GameStateManager:
    """Manager for game state operations"""

    @staticmethod
    def initialize_game_state(game_type: str, num_players: int, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Initialize game state based on game type
        This is a basic template - specific game logic would be implemented per game
        """
        if config is None:
            config = {}

        base_state = {
            "game_type": game_type,
            "num_players": num_players,
            "current_turn": 0,
            "current_player_position": 1,
            "started_at": datetime.utcnow().isoformat(),
            "status": "in_progress"
        }

        # Game-specific initialization
        if game_type == "ludo":
            base_state.update({
                "board": GameStateManager._initialize_ludo_board(num_players),
                "dice_value": None,
                "last_roll": None
            })
        elif game_type == "rummy":
            base_state.update({
                "deck": [],
                "discard_pile": [],
                "player_hands": {},
                "current_phase": "draw"
            })
        elif game_type == "quiz":
            base_state.update({
                "questions": [],
                "current_question_index": 0,
                "player_scores": {},
                "time_remaining": config.get("time_per_question", 30)
            })

        return base_state

    @staticmethod
    def _initialize_ludo_board(num_players: int) -> Dict[str, Any]:
        """Initialize Ludo board state"""
        colors = GameManager.assign_player_colors(num_players)

        board = {
            "pieces": {},
            "safe_spots": [1, 9, 14, 22, 27, 35, 40, 48],  # Example safe spots
            "home_positions": {}
        }

        for i, color in enumerate(colors):
            board["pieces"][color] = [
                {"id": f"{color}_1", "position": -1, "in_home": True},
                {"id": f"{color}_2", "position": -1, "in_home": True},
                {"id": f"{color}_3", "position": -1, "in_home": True},
                {"id": f"{color}_4", "position": -1, "in_home": True}
            ]
            board["home_positions"][color] = i * 13  # Starting position

        return board

    @staticmethod
    def validate_move(
        game_state: Dict[str, Any],
        move_data: Dict[str, Any],
        player_position: int
    ) -> Tuple[bool, str]:
        """
        Validate if a move is legal
        Basic validation - game-specific validation would be more detailed
        """
        # Check if it's the player's turn
        if game_state.get("current_player_position") != player_position:
            return False, "Not your turn"

        # Game-specific validation would go here
        game_type = game_state.get("game_type")

        if game_type == "ludo":
            return GameStateManager._validate_ludo_move(game_state, move_data)

        # Default: allow the move
        return True, "Valid move"

    @staticmethod
    def _validate_ludo_move(game_state: Dict[str, Any], move_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate Ludo-specific move"""
        move_type = move_data.get("type")

        if move_type == "roll_dice":
            return True, "Can roll dice"

        elif move_type == "move_piece":
            dice_value = game_state.get("dice_value")
            if not dice_value:
                return False, "Must roll dice first"

            piece_id = move_data.get("piece_id")
            if not piece_id:
                return False, "Must specify piece to move"

            # Additional validation would check:
            # - Can the piece move with this dice value?
            # - Is the destination valid?
            # - Are there any pieces blocking?

            return True, "Valid move"

        return False, "Invalid move type"

    @staticmethod
    def apply_move(
        game_state: Dict[str, Any],
        move_data: Dict[str, Any],
        player_position: int
    ) -> Dict[str, Any]:
        """
        Apply a move to game state and return new state
        """
        new_state = game_state.copy()
        game_type = new_state.get("game_type")

        if game_type == "ludo":
            new_state = GameStateManager._apply_ludo_move(new_state, move_data, player_position)

        # Advance turn
        num_players = new_state.get("num_players", 2)
        new_state["current_player_position"] = (player_position % num_players) + 1
        new_state["current_turn"] += 1

        return new_state

    @staticmethod
    def _apply_ludo_move(
        game_state: Dict[str, Any],
        move_data: Dict[str, Any],
        player_position: int
    ) -> Dict[str, Any]:
        """Apply Ludo move to game state"""
        move_type = move_data.get("type")

        if move_type == "roll_dice":
            # Simulate dice roll
            dice_value = move_data.get("dice_value", random.randint(1, 6))
            game_state["dice_value"] = dice_value
            game_state["last_roll"] = datetime.utcnow().isoformat()

        elif move_type == "move_piece":
            # Move piece on board
            piece_id = move_data.get("piece_id")
            dice_value = game_state.get("dice_value")

            # Update piece position in board
            # This is simplified - full implementation would handle:
            # - Moving pieces out of home
            # - Capturing opponent pieces
            # - Reaching finish
            # - Safe spots

            game_state["dice_value"] = None  # Clear dice after move

        return game_state

    @staticmethod
    def check_game_over(game_state: Dict[str, Any], player_scores: Dict[int, int] = None) -> Tuple[bool, Optional[int]]:
        """
        Check if game is over and determine winner
        Returns: (is_over, winner_position)
        """
        game_type = game_state.get("game_type")

        # Time-based games
        max_turns = game_state.get("max_turns")
        if max_turns and game_state.get("current_turn", 0) >= max_turns:
            # Determine winner by score
            if player_scores:
                winner = max(player_scores.items(), key=lambda x: x[1])[0]
                return True, winner
            return True, None

        # Game-specific win conditions
        if game_type == "ludo":
            return GameStateManager._check_ludo_win(game_state)

        return False, None

    @staticmethod
    def _check_ludo_win(game_state: Dict[str, Any]) -> Tuple[bool, Optional[int]]:
        """Check if someone won Ludo"""
        board = game_state.get("board", {})
        pieces = board.get("pieces", {})

        # Check if any player has all pieces in finish
        for color, player_pieces in pieces.items():
            finished_pieces = sum(1 for piece in player_pieces if piece.get("finished", False))
            if finished_pieces == 4:
                # Find player position by color
                # This is simplified - would need color-to-position mapping
                return True, 1

        return False, None


# Singleton instances
game_manager = GameManager()
game_state_manager = GameStateManager()
