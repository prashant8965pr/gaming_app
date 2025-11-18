"""
Quiz Game Service
Business logic for quiz game functionality
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
import uuid

from models.quiz import (
    QuizCategory, QuizQuestion, QuizGameSession,
    QuizAnswer, QuizLeaderboard
)
from models.game import GameSession, GameParticipant
from utils.quiz_questions import quiz_question_manager


class QuizService:
    """Service for quiz game operations"""

    @staticmethod
    def create_quiz_session(
        db: Session,
        game_session_id: str,
        num_questions: int = 10,
        category_id: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> QuizGameSession:
        """
        Create a quiz game session with selected questions

        Args:
            db: Database session
            game_session_id: Parent game session ID
            num_questions: Number of questions (default 10)
            category_id: Category filter (optional)
            difficulty: Difficulty filter (optional)

        Returns:
            QuizGameSession object
        """
        # Get random questions
        questions = quiz_question_manager.get_random_questions(
            db,
            category_id=category_id,
            difficulty=difficulty,
            num_questions=num_questions
        )

        if len(questions) < num_questions:
            raise ValueError(f"Not enough questions available. Found {len(questions)}, need {num_questions}")

        # Prepare questions data (store question IDs and metadata)
        questions_data = {
            "questions": [
                {
                    "question_id": str(q.id),
                    "index": i,
                    "difficulty": q.difficulty,
                    "base_points": q.base_points,
                    "time_limit": q.time_limit_seconds
                }
                for i, q in enumerate(questions)
            ],
            "total_questions": num_questions,
        }

        # Create quiz session
        quiz_session = QuizGameSession(
            game_session_id=game_session_id,
            num_questions=num_questions,
            category_id=category_id,
            difficulty=difficulty,
            current_question_index=0,
            questions_data=questions_data
        )

        db.add(quiz_session)
        db.commit()
        db.refresh(quiz_session)

        return quiz_session

    @staticmethod
    def get_current_question(
        db: Session,
        quiz_session_id: str
    ) -> Dict[str, Any]:
        """
        Get the current question for the quiz

        Args:
            db: Database session
            quiz_session_id: Quiz session ID

        Returns:
            Question data with shuffled options
        """
        quiz_session = db.query(QuizGameSession).filter(
            QuizGameSession.id == quiz_session_id
        ).first()

        if not quiz_session:
            raise ValueError("Quiz session not found")

        # Check if quiz is finished
        if quiz_session.current_question_index >= quiz_session.num_questions:
            raise ValueError("Quiz already completed")

        # Get current question ID
        questions_list = quiz_session.questions_data["questions"]
        current_q_data = questions_list[quiz_session.current_question_index]
        question_id = current_q_data["question_id"]

        # Fetch question from database
        question = db.query(QuizQuestion).filter(
            QuizQuestion.id == question_id
        ).first()

        if not question:
            raise ValueError("Question not found")

        # Get shuffled options
        options = quiz_question_manager.get_shuffled_options(
            question.correct_answer,
            question.incorrect_answers
        )

        # Set question start time and deadline
        now = datetime.utcnow()
        deadline = now + timedelta(seconds=question.time_limit_seconds)

        quiz_session.question_started_at = now
        quiz_session.question_deadline = deadline
        db.commit()

        # Return question data (without correct answer)
        return {
            "question_id": str(question.id),
            "question_index": quiz_session.current_question_index,
            "question_text": question.question_text,
            "options": options,
            "time_limit_seconds": question.time_limit_seconds,
            "base_points": question.base_points,
            "difficulty": question.difficulty,
            "hint": question.hint,
            "image_url": question.image_url,
            "started_at": now.isoformat(),
            "deadline": deadline.isoformat(),
        }

    @staticmethod
    def submit_answer(
        db: Session,
        quiz_session_id: str,
        participant_id: str,
        question_id: str,
        player_answer: str
    ) -> Dict[str, Any]:
        """
        Submit an answer to a question

        Args:
            db: Database session
            quiz_session_id: Quiz session ID
            participant_id: Game participant ID
            question_id: Question ID
            player_answer: Player's answer

        Returns:
            Answer result with score breakdown
        """
        quiz_session = db.query(QuizGameSession).filter(
            QuizGameSession.id == quiz_session_id
        ).first()

        if not quiz_session:
            raise ValueError("Quiz session not found")

        # Get question
        question = db.query(QuizQuestion).filter(
            QuizQuestion.id == question_id
        ).first()

        if not question:
            raise ValueError("Question not found")

        # Calculate time taken
        now = datetime.utcnow()
        time_taken_ms = int((now - quiz_session.question_started_at).total_seconds() * 1000)

        # Check if answer is correct
        is_correct = quiz_question_manager.validate_answer(
            player_answer,
            question.correct_answer,
            question.question_type
        )

        # Get participant's current streak
        current_streak = QuizService._get_participant_streak(
            db, quiz_session_id, participant_id
        )

        # Calculate score if correct
        if is_correct:
            score_data = quiz_question_manager.calculate_score(
                question.base_points,
                question.time_limit_seconds,
                time_taken_ms,
                current_streak
            )
            current_streak += 1
        else:
            score_data = {
                "points_earned": 0,
                "time_bonus": 0,
                "streak_bonus": 0,
                "total_points": 0,
            }
            current_streak = 0

        # Create answer record
        answer = QuizAnswer(
            quiz_session_id=quiz_session_id,
            participant_id=participant_id,
            question_id=question_id,
            question_index=quiz_session.current_question_index,
            player_answer=player_answer,
            is_correct=is_correct,
            time_taken_ms=time_taken_ms,
            **score_data
        )

        db.add(answer)

        # Update question statistics
        quiz_question_manager.update_question_stats(db, question_id, is_correct)

        # Update participant score in game_participants table
        participant = db.query(GameParticipant).filter(
            GameParticipant.id == participant_id
        ).first()

        if participant:
            participant.final_score = (participant.final_score or 0) + score_data["total_points"]

        db.commit()
        db.refresh(answer)

        # Return result
        return {
            **answer.to_dict(),
            "correct_answer": question.correct_answer,
            "explanation": question.explanation,
            "current_streak": current_streak,
        }

    @staticmethod
    def handle_timeout(
        db: Session,
        quiz_session_id: str,
        participant_id: str,
        question_id: str
    ) -> Dict[str, Any]:
        """
        Handle question timeout (no answer submitted)

        Args:
            db: Database session
            quiz_session_id: Quiz session ID
            participant_id: Participant ID
            question_id: Question ID

        Returns:
            Timeout result
        """
        quiz_session = db.query(QuizGameSession).filter(
            QuizGameSession.id == quiz_session_id
        ).first()

        question = db.query(QuizQuestion).filter(
            QuizQuestion.id == question_id
        ).first()

        # Calculate time taken (full time limit)
        time_limit_ms = question.time_limit_seconds * 1000

        # Create answer record (incorrect, no answer)
        answer = QuizAnswer(
            quiz_session_id=quiz_session_id,
            participant_id=participant_id,
            question_id=question_id,
            question_index=quiz_session.current_question_index,
            player_answer=None,  # No answer
            is_correct=False,
            time_taken_ms=time_limit_ms,
            points_earned=0,
            time_bonus=0,
            streak_bonus=0,
            total_points=0
        )

        db.add(answer)

        # Update question stats
        quiz_question_manager.update_question_stats(db, question_id, False)

        db.commit()
        db.refresh(answer)

        return {
            **answer.to_dict(),
            "correct_answer": question.correct_answer,
            "explanation": question.explanation,
            "timeout": True,
        }

    @staticmethod
    def next_question(
        db: Session,
        quiz_session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Move to next question

        Args:
            db: Database session
            quiz_session_id: Quiz session ID

        Returns:
            Next question data or None if quiz complete
        """
        quiz_session = db.query(QuizGameSession).filter(
            QuizGameSession.id == quiz_session_id
        ).first()

        if not quiz_session:
            raise ValueError("Quiz session not found")

        # Increment question index
        quiz_session.current_question_index += 1
        db.commit()

        # Check if quiz is complete
        if quiz_session.current_question_index >= quiz_session.num_questions:
            return None

        # Get next question
        return QuizService.get_current_question(db, quiz_session_id)

    @staticmethod
    def get_quiz_results(
        db: Session,
        quiz_session_id: str
    ) -> Dict[str, Any]:
        """
        Get final quiz results for all participants

        Args:
            db: Database session
            quiz_session_id: Quiz session ID

        Returns:
            Complete quiz results with rankings
        """
        quiz_session = db.query(QuizGameSession).filter(
            QuizGameSession.id == quiz_session_id
        ).first()

        if not quiz_session:
            raise ValueError("Quiz session not found")

        # Get all participants
        participants = db.query(GameParticipant).filter(
            GameParticipant.session_id == quiz_session.game_session_id
        ).order_by(GameParticipant.final_score.desc()).all()

        # Get all answers for this quiz
        answers = db.query(QuizAnswer).filter(
            QuizAnswer.quiz_session_id == quiz_session_id
        ).all()

        # Build participant results
        participant_results = []
        for rank, participant in enumerate(participants, 1):
            # Get participant's answers
            participant_answers = [
                a for a in answers if str(a.participant_id) == str(participant.id)
            ]

            correct_count = sum(1 for a in participant_answers if a.is_correct)
            total_time_ms = sum(a.time_taken_ms for a in participant_answers)

            # Calculate streak
            max_streak = QuizService._calculate_max_streak(participant_answers)

            participant_results.append({
                "participant_id": str(participant.id),
                "user_id": str(participant.user_id),
                "player_name": participant.player_name,
                "rank": rank,
                "total_score": participant.final_score or 0,
                "correct_answers": correct_count,
                "total_questions": quiz_session.num_questions,
                "accuracy_rate": (correct_count / quiz_session.num_questions * 100) if quiz_session.num_questions > 0 else 0,
                "total_time_ms": total_time_ms,
                "max_streak": max_streak,
            })

        return {
            "quiz_session_id": str(quiz_session.id),
            "game_session_id": str(quiz_session.game_session_id),
            "num_questions": quiz_session.num_questions,
            "category_id": str(quiz_session.category_id) if quiz_session.category_id else None,
            "difficulty": quiz_session.difficulty,
            "participants": participant_results,
        }

    @staticmethod
    def finalize_quiz(
        db: Session,
        quiz_session_id: str
    ) -> Dict[str, Any]:
        """
        Finalize quiz and update leaderboards

        Args:
            db: Database session
            quiz_session_id: Quiz session ID

        Returns:
            Final results
        """
        results = QuizService.get_quiz_results(db, quiz_session_id)
        quiz_session = db.query(QuizGameSession).filter(
            QuizGameSession.id == quiz_session_id
        ).first()

        # Update leaderboards for all participants
        for participant_data in results["participants"]:
            quiz_question_manager.update_leaderboard(
                db,
                user_id=participant_data["user_id"],
                category_id=quiz_session.category_id,
                points=participant_data["total_score"],
                questions_answered=participant_data["total_questions"],
                correct_count=participant_data["correct_answers"],
                streak=participant_data["max_streak"]
            )

        return results

    @staticmethod
    def _get_participant_streak(
        db: Session,
        quiz_session_id: str,
        participant_id: str
    ) -> int:
        """Get participant's current answer streak"""
        answers = db.query(QuizAnswer).filter(
            and_(
                QuizAnswer.quiz_session_id == quiz_session_id,
                QuizAnswer.participant_id == participant_id
            )
        ).order_by(QuizAnswer.question_index.desc()).all()

        # Count consecutive correct answers from most recent
        streak = 0
        for answer in answers:
            if answer.is_correct:
                streak += 1
            else:
                break

        return streak

    @staticmethod
    def _calculate_max_streak(answers: List[QuizAnswer]) -> int:
        """Calculate maximum consecutive correct answers"""
        if not answers:
            return 0

        # Sort by question index
        sorted_answers = sorted(answers, key=lambda a: a.question_index)

        max_streak = 0
        current_streak = 0

        for answer in sorted_answers:
            if answer.is_correct:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0

        return max_streak

    @staticmethod
    def get_categories(db: Session) -> List[Dict[str, Any]]:
        """Get all active quiz categories"""
        categories = db.query(QuizCategory).filter(
            QuizCategory.is_active == True
        ).all()

        return [
            {
                "id": str(c.id),
                "code": c.code,
                "name": c.name,
                "description": c.description,
                "icon_url": c.icon_url,
                "total_questions": c.total_questions,
            }
            for c in categories
        ]

    @staticmethod
    def get_leaderboard(
        db: Session,
        category_id: Optional[str] = None,
        leaderboard_type: str = "all_time",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get quiz leaderboard"""
        return quiz_question_manager.get_leaderboard(
            db,
            category_id=category_id,
            leaderboard_type=leaderboard_type,
            limit=limit
        )


# Create singleton instance
quiz_service = QuizService()
