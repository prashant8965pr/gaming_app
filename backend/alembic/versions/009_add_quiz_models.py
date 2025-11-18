"""add quiz models

Revision ID: 009
Revises: 008
Create Date: 2025-11-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade():
    # Create quiz_categories table
    op.create_table(
        'quiz_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon_url', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True),
        sa.Column('difficulty_multiplier', sa.Float(), server_default='1.0', nullable=True),
        sa.Column('total_questions', sa.Integer(), server_default='0', nullable=True),
        sa.Column('total_plays', sa.Integer(), server_default='0', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_quiz_categories_code', 'quiz_categories', ['code'])
    op.create_index('idx_quiz_categories_is_active', 'quiz_categories', ['is_active'])
    op.create_index(op.f('ix_quiz_categories_code'), 'quiz_categories', ['code'], unique=True)

    # Create quiz_questions table
    op.create_table(
        'quiz_questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('question_type', sa.String(length=20), server_default='multiple_choice', nullable=True),
        sa.Column('difficulty', sa.String(length=20), server_default='medium', nullable=False),
        sa.Column('correct_answer', sa.String(length=500), nullable=False),
        sa.Column('incorrect_answers', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('hint', sa.String(length=500), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('audio_url', sa.String(length=500), nullable=True),
        sa.Column('time_limit_seconds', sa.Integer(), server_default='15', nullable=True),
        sa.Column('base_points', sa.Integer(), server_default='100', nullable=True),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('question_metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True),
        sa.Column('is_verified', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('times_asked', sa.Integer(), server_default='0', nullable=True),
        sa.Column('times_correct', sa.Integer(), server_default='0', nullable=True),
        sa.Column('times_incorrect', sa.Integer(), server_default='0', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['quiz_categories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_quiz_questions_category_id', 'quiz_questions', ['category_id'])
    op.create_index('idx_quiz_questions_difficulty', 'quiz_questions', ['difficulty'])
    op.create_index('idx_quiz_questions_is_active', 'quiz_questions', ['is_active'])

    # Create quiz_game_sessions table
    op.create_table(
        'quiz_game_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('game_session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('num_questions', sa.Integer(), server_default='10', nullable=True),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('difficulty', sa.String(length=20), nullable=True),
        sa.Column('current_question_index', sa.Integer(), server_default='0', nullable=True),
        sa.Column('questions_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('question_started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('question_deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['game_session_id'], ['game_sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['quiz_categories.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('game_session_id')
    )
    op.create_index('idx_quiz_sessions_game_session_id', 'quiz_game_sessions', ['game_session_id'])
    op.create_index('idx_quiz_sessions_category_id', 'quiz_game_sessions', ['category_id'])

    # Create quiz_answers table
    op.create_table(
        'quiz_answers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quiz_session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('participant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_index', sa.Integer(), nullable=False),
        sa.Column('player_answer', sa.String(length=500), nullable=True),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('time_taken_ms', sa.Integer(), nullable=False),
        sa.Column('answered_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('points_earned', sa.Integer(), server_default='0', nullable=True),
        sa.Column('time_bonus', sa.Integer(), server_default='0', nullable=True),
        sa.Column('streak_bonus', sa.Integer(), server_default='0', nullable=True),
        sa.Column('total_points', sa.Integer(), server_default='0', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['quiz_session_id'], ['quiz_game_sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['participant_id'], ['game_participants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['quiz_questions.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_quiz_answers_session_id', 'quiz_answers', ['quiz_session_id'])
    op.create_index('idx_quiz_answers_participant_id', 'quiz_answers', ['participant_id'])
    op.create_index('idx_quiz_answers_question_id', 'quiz_answers', ['question_id'])

    # Create quiz_leaderboard table
    op.create_table(
        'quiz_leaderboard',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('leaderboard_type', sa.String(length=20), server_default='all_time', nullable=False),
        sa.Column('total_games', sa.Integer(), server_default='0', nullable=True),
        sa.Column('total_questions', sa.Integer(), server_default='0', nullable=True),
        sa.Column('correct_answers', sa.Integer(), server_default='0', nullable=True),
        sa.Column('total_points', sa.Integer(), server_default='0', nullable=True),
        sa.Column('highest_score', sa.Integer(), server_default='0', nullable=True),
        sa.Column('current_streak', sa.Integer(), server_default='0', nullable=True),
        sa.Column('best_streak', sa.Integer(), server_default='0', nullable=True),
        sa.Column('rank', sa.Integer(), nullable=True),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['quiz_categories.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_quiz_leaderboard_user_id', 'quiz_leaderboard', ['user_id'])
    op.create_index('idx_quiz_leaderboard_category_id', 'quiz_leaderboard', ['category_id'])
    op.create_index('idx_quiz_leaderboard_type', 'quiz_leaderboard', ['leaderboard_type'])
    op.create_index('idx_quiz_leaderboard_rank', 'quiz_leaderboard', ['rank'])
    op.create_index('idx_quiz_leaderboard_total_points', 'quiz_leaderboard', ['total_points'])


def downgrade():
    # Drop tables in reverse order
    op.drop_table('quiz_leaderboard')
    op.drop_table('quiz_answers')
    op.drop_table('quiz_game_sessions')
    op.drop_table('quiz_questions')
    op.drop_table('quiz_categories')
