"""
Game Catalog Seed Script
Seeds the initial game catalog with all available games
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from config.database import get_async_session
from models.game import Game
import uuid


# Game catalog data
GAMES_DATA = [
    {
        "code": "quiz",
        "name": "Quiz Master",
        "description": "Test your knowledge across various categories! Answer questions correctly and faster than your opponents to win.",
        "category": "quiz",
        "min_players": 1,
        "max_players": 10,
        "avg_duration_minutes": 5,
        "difficulty_level": "easy",
        "min_entry_fee": 0,
        "max_entry_fee": 100000,  # Rs.1000
        "default_entry_fee": 5000,  # Rs.50
        "prize_distribution": {
            "1st": 60,
            "2nd": 25,
            "3rd": 10,
            "4th": 5
        },
        "rules": {
            "total_questions": 10,
            "time_per_question": 15,
            "points_correct": 10,
            "points_wrong": 0,
            "bonus_speed": True,
            "categories": ["general", "sports", "entertainment", "science", "history"]
        },
        "game_config": {
            "question_types": ["multiple_choice"],
            "difficulty_progression": True,
            "allow_lifelines": False,
            "real_time_multiplayer": True
        },
        "is_active": True,
        "is_featured": True,
        "is_skill_based": True,
        "display_order": 1
    },
    {
        "code": "ludo",
        "name": "Ludo Classic",
        "description": "Classic board game of strategy and luck! Roll the dice, move your pieces, and race to the finish.",
        "category": "board",
        "min_players": 2,
        "max_players": 4,
        "avg_duration_minutes": 15,
        "difficulty_level": "medium",
        "min_entry_fee": 1000,  # Rs.10
        "max_entry_fee": 500000,  # Rs.5000
        "default_entry_fee": 10000,  # Rs.100
        "prize_distribution": {
            "1st": 70,
            "2nd": 20,
            "3rd": 10
        },
        "rules": {
            "board_size": 52,
            "pieces_per_player": 4,
            "home_stretch": 6,
            "safe_spots": [1, 9, 14, 22, 27, 35, 40, 48],
            "must_roll_six_to_start": True,
            "extra_turn_on_six": True,
            "capture_sends_home": True,
            "exact_roll_to_finish": False
        },
        "game_config": {
            "dice_type": "standard_6",
            "auto_move_single_piece": True,
            "turn_timeout_seconds": 30,
            "colors": ["red", "blue", "green", "yellow"]
        },
        "is_active": False,  # Coming soon
        "is_featured": True,
        "is_skill_based": True,
        "display_order": 2
    },
    {
        "code": "rummy",
        "name": "Indian Rummy",
        "description": "Form valid sets and sequences in this classic card game! Declare before your opponents to win.",
        "category": "card",
        "min_players": 2,
        "max_players": 6,
        "avg_duration_minutes": 10,
        "difficulty_level": "hard",
        "min_entry_fee": 2000,  # Rs.20
        "max_entry_fee": 1000000,  # Rs.10000
        "default_entry_fee": 20000,  # Rs.200
        "prize_distribution": {
            "1st": 80,
            "2nd": 15,
            "3rd": 5
        },
        "rules": {
            "cards_per_player": 13,
            "decks": 2,
            "jokers": True,
            "min_sequences_required": 2,
            "pure_sequence_mandatory": True,
            "max_points_to_lose": 80,
            "drop_penalty": {"first_drop": 20, "middle_drop": 40, "full_count": 80}
        },
        "game_config": {
            "variant": "points_rummy",
            "point_value": 100,  # Re.1 = 1 point in entry fee
            "declare_timeout": 60,
            "show_timeout": 45
        },
        "is_active": False,  # Coming soon
        "is_featured": False,
        "is_skill_based": True,
        "display_order": 3
    },
    {
        "code": "poker",
        "name": "Texas Hold'em Poker",
        "description": "The ultimate game of skill and strategy! Form the best 5-card hand and outplay your opponents.",
        "category": "card",
        "min_players": 2,
        "max_players": 9,
        "avg_duration_minutes": 20,
        "difficulty_level": "hard",
        "min_entry_fee": 10000,  # Rs.100
        "max_entry_fee": 5000000,  # Rs.50000
        "default_entry_fee": 50000,  # Rs.500
        "prize_distribution": {
            "1st": 50,
            "2nd": 30,
            "3rd": 15,
            "4th": 5
        },
        "rules": {
            "variant": "texas_holdem",
            "hole_cards": 2,
            "community_cards": 5,
            "betting_rounds": 4,
            "small_blind": 50,  # 5% of entry
            "big_blind": 100,  # 10% of entry
            "hand_rankings": [
                "high_card", "pair", "two_pair", "three_of_a_kind",
                "straight", "flush", "full_house", "four_of_a_kind",
                "straight_flush", "royal_flush"
            ]
        },
        "game_config": {
            "table_type": "tournament",
            "blind_increase_minutes": 5,
            "starting_chips": 1000,
            "action_timeout": 30
        },
        "is_active": False,  # Coming soon
        "is_featured": False,
        "is_skill_based": True,
        "display_order": 4
    },
    {
        "code": "carrom",
        "name": "Carrom Board",
        "description": "Pocket all your pieces before your opponent! Master angles and power in this classic strike game.",
        "category": "board",
        "min_players": 2,
        "max_players": 4,
        "avg_duration_minutes": 12,
        "difficulty_level": "medium",
        "min_entry_fee": 1000,  # Rs.10
        "max_entry_fee": 500000,  # Rs.5000
        "default_entry_fee": 10000,  # Rs.100
        "prize_distribution": {
            "1st": 75,
            "2nd": 25
        },
        "rules": {
            "pieces_per_player": 9,
            "queen_points": 3,
            "cover_queen_required": True,
            "foul_penalty": 1,
            "max_consecutive_fouls": 3,
            "points_to_win": 29,
            "time_per_turn": 30
        },
        "game_config": {
            "game_mode": "singles",
            "board_size": "standard",
            "physics_enabled": True,
            "aim_assist": False
        },
        "is_active": False,  # Coming soon
        "is_featured": False,
        "is_skill_based": True,
        "display_order": 5
    },
    {
        "code": "pool",
        "name": "8-Ball Pool",
        "description": "Sink all your balls and then the 8-ball to win! Practice your aim and shot power.",
        "category": "board",
        "min_players": 2,
        "max_players": 2,
        "avg_duration_minutes": 10,
        "difficulty_level": "medium",
        "min_entry_fee": 1000,  # Rs.10
        "max_entry_fee": 500000,  # Rs.5000
        "default_entry_fee": 10000,  # Rs.100
        "prize_distribution": {
            "1st": 90,
            "2nd": 10
        },
        "rules": {
            "variant": "8_ball",
            "total_balls": 16,
            "solids": [1, 2, 3, 4, 5, 6, 7],
            "stripes": [9, 10, 11, 12, 13, 14, 15],
            "must_call_shot": True,
            "break_rules": {
                "must_hit_minimum_balls": 4,
                "sink_on_break": "continue"
            },
            "foul_types": ["scratch", "wrong_ball", "no_rail", "double_hit"]
        },
        "game_config": {
            "table_size": "standard",
            "physics_enabled": True,
            "shot_timer": 45,
            "aim_guide": "medium"
        },
        "is_active": False,  # Coming soon
        "is_featured": False,
        "is_skill_based": True,
        "display_order": 6
    }
]


async def seed_game(db: AsyncSession, game_data: dict) -> Game:
    """Seed a single game"""

    # Check if game already exists
    result = await db.execute(
        select(Game).where(Game.code == game_data["code"])
    )
    existing_game = result.scalar_one_or_none()

    if existing_game:
        print(f"   ⏭️  {game_data['name']} already exists (ID: {existing_game.id})")
        return existing_game

    # Create new game
    game = Game(
        id=uuid.uuid4(),
        **game_data
    )

    db.add(game)
    await db.commit()
    await db.refresh(game)

    status = "✅ ACTIVE" if game.is_active else "🔜 COMING SOON"
    featured = "⭐" if game.is_featured else ""
    print(f"   ✅ {game.name} {featured} - {status}")
    print(f"      ID: {game.id}")
    print(f"      Category: {game.category.upper()}")
    print(f"      Players: {game.min_players}-{game.max_players}")
    print(f"      Entry: ₹{game.min_entry_fee/100:.0f} - ₹{game.max_entry_fee/100:.0f if game.max_entry_fee else 'No Limit'}")

    return game


async def main():
    """Main seed function"""
    print("=" * 70)
    print("Gaming Platform - Game Catalog Seed Script")
    print("=" * 70)
    print()

    try:
        # Get database session
        async for session in get_async_session():
            print(f"📦 Seeding {len(GAMES_DATA)} games...")
            print()

            created_count = 0
            active_count = 0

            for game_data in GAMES_DATA:
                game = await seed_game(session, game_data)
                if game.code == game_data["code"]:  # Newly created
                    created_count += 1
                if game.is_active:
                    active_count += 1
                print()

            print("=" * 70)
            print("✅ Game Catalog Seeding Complete!")
            print("=" * 70)
            print(f"Total Games: {len(GAMES_DATA)}")
            print(f"Active Games: {active_count}")
            print(f"Coming Soon: {len(GAMES_DATA) - active_count}")
            print()
            print("📝 Active Games:")
            for game_data in GAMES_DATA:
                if game_data["is_active"]:
                    print(f"   ✅ {game_data['name']}")
            print()
            print("🔜 Coming Soon:")
            for game_data in GAMES_DATA:
                if not game_data["is_active"]:
                    print(f"   ⏳ {game_data['name']}")
            print()
            print("=" * 70)

            break

    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(main())
