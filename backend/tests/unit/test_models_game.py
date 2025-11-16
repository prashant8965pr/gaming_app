"""
Unit tests for Game models
"""
import pytest
from datetime import datetime
import uuid

from models.game import Game, GameSession, GameParticipant, GameMove, GameResult


@pytest.mark.unit
@pytest.mark.games
class TestGameModel:
    """Test Game model"""

    async def test_create_game(self, db_session):
        """Test creating a new game"""
        game = Game(
            id=uuid.uuid4(),
            code="test_game",
            name="Test Game",
            category="board",
            min_players=2,
            max_players=4,
            default_entry_fee=10000,
            prize_distribution={"1st": 70, "2nd": 30},
            is_active=True,
            is_skill_based=True
        )

        db_session.add(game)
        await db_session.commit()
        await db_session.refresh(game)

        assert game.id is not None
        assert game.code == "test_game"
        assert game.is_active == True
        assert game.prize_distribution["1st"] == 70

    async def test_game_code_unique(self, db_session, test_game):
        """Test game code uniqueness"""
        duplicate_game = Game(
            id=uuid.uuid4(),
            code=test_game.code,  # Same code
            name="Duplicate Game",
            category="board",
            default_entry_fee=10000
        )

        db_session.add(duplicate_game)

        with pytest.raises(Exception):  # Should raise integrity error
            await db_session.commit()


@pytest.mark.unit
@pytest.mark.games
class TestGameSession:
    """Test GameSession model"""

    async def test_create_game_session(self, db_session, test_game):
        """Test creating a game session"""
        session = GameSession(
            id=uuid.uuid4(),
            game_id=test_game.id,
            session_code="ABCD1234",
            session_type="public",
            entry_fee=10000,
            max_players=4,
            status="waiting"
        )

        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        assert session.id is not None
        assert session.session_code == "ABCD1234"
        assert session.status == "waiting"
        assert session.current_players == 0

    async def test_session_code_unique(self, db_session, test_game_session):
        """Test session code uniqueness"""
        duplicate_session = GameSession(
            id=uuid.uuid4(),
            game_id=test_game_session.game_id,
            session_code=test_game_session.session_code,  # Same code
            session_type="public",
            entry_fee=10000,
            max_players=4
        )

        db_session.add(duplicate_session)

        with pytest.raises(Exception):  # Should raise integrity error
            await db_session.commit()

    async def test_game_state_json(self, db_session, test_game_session, sample_game_state):
        """Test game state JSON storage"""
        test_game_session.game_state = sample_game_state
        await db_session.commit()
        await db_session.refresh(test_game_session)

        assert test_game_session.game_state["game_type"] == "ludo"
        assert test_game_session.game_state["num_players"] == 4


@pytest.mark.unit
@pytest.mark.games
class TestGameParticipant:
    """Test GameParticipant model"""

    async def test_create_participant(self, db_session, test_game_session, test_user):
        """Test creating a game participant"""
        participant = GameParticipant(
            id=uuid.uuid4(),
            session_id=test_game_session.id,
            user_id=test_user.id,
            player_position=1,
            player_color="red",
            player_name=test_user.display_name,
            entry_fee_paid=10000,
            status="joined"
        )

        db_session.add(participant)
        await db_session.commit()
        await db_session.refresh(participant)

        assert participant.id is not None
        assert participant.player_position == 1
        assert participant.status == "joined"

    async def test_participant_unique_constraint(self, db_session, test_game_session, test_user):
        """Test user can't join same session twice"""
        participant1 = GameParticipant(
            id=uuid.uuid4(),
            session_id=test_game_session.id,
            user_id=test_user.id,
            player_position=1,
            player_name="Test",
            entry_fee_paid=10000
        )

        db_session.add(participant1)
        await db_session.commit()

        # Try to join again
        participant2 = GameParticipant(
            id=uuid.uuid4(),
            session_id=test_game_session.id,
            user_id=test_user.id,  # Same user, same session
            player_position=2,
            player_name="Test",
            entry_fee_paid=10000
        )

        db_session.add(participant2)

        with pytest.raises(Exception):  # Should raise integrity error
            await db_session.commit()


@pytest.mark.unit
@pytest.mark.games
class TestGameMove:
    """Test GameMove model"""

    async def test_create_move(self, db_session, test_game_session, test_user):
        """Test creating a game move"""
        # Create participant first
        participant = GameParticipant(
            id=uuid.uuid4(),
            session_id=test_game_session.id,
            user_id=test_user.id,
            player_position=1,
            player_name="Test",
            entry_fee_paid=10000
        )
        db_session.add(participant)
        await db_session.commit()

        # Create move
        move = GameMove(
            id=uuid.uuid4(),
            session_id=test_game_session.id,
            participant_id=participant.id,
            user_id=test_user.id,
            move_number=1,
            turn_number=1,
            move_type="roll_dice",
            move_data={"dice_value": 6},
            is_valid=True
        )

        db_session.add(move)
        await db_session.commit()
        await db_session.refresh(move)

        assert move.id is not None
        assert move.move_type == "roll_dice"
        assert move.move_data["dice_value"] == 6


@pytest.mark.unit
@pytest.mark.games
class TestGameResult:
    """Test GameResult model"""

    async def test_create_game_result(self, db_session, test_game, test_game_session, test_user):
        """Test creating game result"""
        result = GameResult(
            id=uuid.uuid4(),
            session_id=test_game_session.id,
            game_id=test_game.id,
            winner_id=test_user.id,
            winner_name=test_user.display_name,
            winning_prize=7000,
            final_rankings=[
                {"user_id": str(test_user.id), "rank": 1, "score": 100, "prize": 7000}
            ],
            total_players=1,
            total_prize_pool=10000,
            platform_fee_collected=500,
            game_started_at=datetime.utcnow(),
            game_ended_at=datetime.utcnow()
        )

        db_session.add(result)
        await db_session.commit()
        await db_session.refresh(result)

        assert result.id is not None
        assert result.winner_id == test_user.id
        assert len(result.final_rankings) == 1
        assert result.final_rankings[0]["rank"] == 1
