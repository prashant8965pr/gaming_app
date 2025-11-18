"""
Quiz Question Bank Management
Utilities for loading, filtering, and managing quiz questions
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import random
import httpx


class QuizQuestionManager:
    """Manager for quiz question operations"""

    # Open Trivia Database API
    OPENTDB_API_URL = "https://opentdb.com/api.php"

    # Category mapping: our codes to OpenTDB category IDs
    OPENTDB_CATEGORIES = {
        "general": 9,  # General Knowledge
        "books": 10,  # Entertainment: Books
        "film": 11,  # Entertainment: Film
        "music": 12,  # Entertainment: Music
        "tv": 14,  # Entertainment: Television
        "video_games": 15,  # Entertainment: Video Games
        "board_games": 16,  # Entertainment: Board Games
        "science_nature": 17,  # Science & Nature
        "computers": 18,  # Science: Computers
        "mathematics": 19,  # Science: Mathematics
        "mythology": 20,  # Mythology
        "sports": 21,  # Sports
        "geography": 22,  # Geography
        "history": 23,  # History
        "politics": 24,  # Politics
        "art": 25,  # Art
        "celebrities": 26,  # Celebrities
        "animals": 27,  # Animals
        "vehicles": 28,  # Vehicles
        "comics": 29,  # Entertainment: Comics
        "gadgets": 30,  # Science: Gadgets
        "anime": 31,  # Entertainment: Japanese Anime & Manga
        "cartoons": 32,  # Entertainment: Cartoon & Animations
    }

    # Difficulty mapping
    DIFFICULTY_POINTS = {
        "easy": 100,
        "medium": 200,
        "hard": 300,
    }

    DIFFICULTY_TIME = {
        "easy": 15,  # seconds
        "medium": 20,
        "hard": 30,
    }

    @staticmethod
    async def fetch_from_opentdb(
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        num_questions: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Fetch questions from Open Trivia Database API

        Args:
            category: Category code (general, science, etc.)
            difficulty: easy, medium, hard
            num_questions: Number of questions to fetch (max 50)

        Returns:
            List of question dictionaries
        """
        params = {
            "amount": min(num_questions, 50),
            "type": "multiple",  # Multiple choice
        }

        if category and category in QuizQuestionManager.OPENTDB_CATEGORIES:
            params["category"] = QuizQuestionManager.OPENTDB_CATEGORIES[category]

        if difficulty:
            params["difficulty"] = difficulty.lower()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    QuizQuestionManager.OPENTDB_API_URL,
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()

                if data.get("response_code") == 0:
                    return data.get("results", [])
                else:
                    return []

        except Exception as e:
            print(f"Error fetching from OpenTDB: {e}")
            return []

    @staticmethod
    def parse_opentdb_question(raw_question: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse OpenTDB question format to our format

        Args:
            raw_question: Raw question from OpenTDB API

        Returns:
            Formatted question dictionary
        """
        difficulty = raw_question.get("difficulty", "medium")

        return {
            "question_text": raw_question["question"],
            "question_type": "multiple_choice",
            "difficulty": difficulty,
            "correct_answer": raw_question["correct_answer"],
            "incorrect_answers": raw_question["incorrect_answers"],
            "time_limit_seconds": QuizQuestionManager.DIFFICULTY_TIME[difficulty],
            "base_points": QuizQuestionManager.DIFFICULTY_POINTS[difficulty],
            "source": "opentdb",
            "question_metadata": {
                "opentdb_category": raw_question.get("category"),
                "opentdb_type": raw_question.get("type"),
            },
        }

    @staticmethod
    def get_random_questions(
        db: Session,
        category_id: Optional[str] = None,
        difficulty: Optional[str] = None,
        num_questions: int = 10,
        exclude_ids: List[str] = None
    ) -> List[Any]:
        """
        Get random questions from database

        Args:
            db: Database session
            category_id: Filter by category (optional)
            difficulty: Filter by difficulty (optional)
            num_questions: Number of questions to return
            exclude_ids: List of question IDs to exclude

        Returns:
            List of QuizQuestion objects
        """
        from models.quiz import QuizQuestion

        query = db.query(QuizQuestion).filter(QuizQuestion.is_active == True)

        # Apply filters
        if category_id:
            query = query.filter(QuizQuestion.category_id == category_id)

        if difficulty:
            query = query.filter(QuizQuestion.difficulty == difficulty)

        if exclude_ids:
            query = query.filter(~QuizQuestion.id.in_(exclude_ids))

        # Get all matching questions
        questions = query.all()

        # Randomly select requested number
        if len(questions) <= num_questions:
            return questions
        else:
            return random.sample(questions, num_questions)

    @staticmethod
    def calculate_score(
        base_points: int,
        time_limit_seconds: int,
        time_taken_ms: int,
        current_streak: int = 0
    ) -> Dict[str, int]:
        """
        Calculate score for a question answer

        Args:
            base_points: Base points for the question
            time_limit_seconds: Time limit for the question
            time_taken_ms: Time taken to answer in milliseconds
            current_streak: Current correct answer streak

        Returns:
            Dictionary with points breakdown
        """
        time_taken_seconds = time_taken_ms / 1000
        time_limit_ms = time_limit_seconds * 1000

        # Base points
        points_earned = base_points

        # Time bonus: faster answers get more points
        # Up to 50% bonus for very fast answers
        if time_taken_ms < time_limit_ms:
            time_remaining = time_limit_ms - time_taken_ms
            time_bonus_percentage = (time_remaining / time_limit_ms) * 0.5
            time_bonus = int(base_points * time_bonus_percentage)
        else:
            time_bonus = 0

        # Streak bonus: 10% per streak, max 100%
        streak_multiplier = min(current_streak * 0.1, 1.0)
        streak_bonus = int(base_points * streak_multiplier)

        # Total
        total_points = points_earned + time_bonus + streak_bonus

        return {
            "points_earned": points_earned,
            "time_bonus": time_bonus,
            "streak_bonus": streak_bonus,
            "total_points": total_points,
        }

    @staticmethod
    def get_shuffled_options(
        correct_answer: str,
        incorrect_answers: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Shuffle answer options and return with labels

        Args:
            correct_answer: The correct answer
            incorrect_answers: List of incorrect answers

        Returns:
            List of options with labels (A, B, C, D)
        """
        all_answers = [correct_answer] + incorrect_answers
        random.shuffle(all_answers)

        labels = ["A", "B", "C", "D"]
        return [
            {"label": labels[i], "text": answer}
            for i, answer in enumerate(all_answers[:4])
        ]

    @staticmethod
    def validate_answer(
        player_answer: str,
        correct_answer: str,
        question_type: str = "multiple_choice"
    ) -> bool:
        """
        Validate if player's answer is correct

        Args:
            player_answer: Player's answer
            correct_answer: Correct answer
            question_type: Type of question

        Returns:
            True if correct, False otherwise
        """
        if question_type == "multiple_choice":
            # Case-insensitive exact match
            return player_answer.strip().lower() == correct_answer.strip().lower()
        elif question_type == "true_false":
            # Boolean comparison
            return player_answer.strip().lower() == correct_answer.strip().lower()
        elif question_type == "text":
            # Fuzzy match (allow minor variations)
            player = player_answer.strip().lower()
            correct = correct_answer.strip().lower()

            # Exact match
            if player == correct:
                return True

            # Remove punctuation and check
            import string
            player_clean = player.translate(str.maketrans('', '', string.punctuation))
            correct_clean = correct.translate(str.maketrans('', '', string.punctuation))

            return player_clean == correct_clean

        return False

    @staticmethod
    def update_question_stats(
        db: Session,
        question_id: str,
        is_correct: bool
    ):
        """
        Update question statistics

        Args:
            db: Database session
            question_id: Question ID
            is_correct: Whether answer was correct
        """
        from models.quiz import QuizQuestion

        question = db.query(QuizQuestion).filter(QuizQuestion.id == question_id).first()
        if question:
            question.times_asked += 1
            if is_correct:
                question.times_correct += 1
            else:
                question.times_incorrect += 1
            db.commit()

    @staticmethod
    def update_leaderboard(
        db: Session,
        user_id: str,
        category_id: Optional[str],
        points: int,
        questions_answered: int,
        correct_count: int,
        streak: int
    ):
        """
        Update user's leaderboard entry

        Args:
            db: Database session
            user_id: User ID
            category_id: Category ID (None for overall)
            points: Points earned
            questions_answered: Number of questions answered
            correct_count: Number of correct answers
            streak: Current streak
        """
        from models.quiz import QuizLeaderboard

        # Get or create leaderboard entry
        leaderboard = db.query(QuizLeaderboard).filter(
            and_(
                QuizLeaderboard.user_id == user_id,
                QuizLeaderboard.category_id == category_id,
                QuizLeaderboard.leaderboard_type == "all_time"
            )
        ).first()

        if not leaderboard:
            leaderboard = QuizLeaderboard(
                user_id=user_id,
                category_id=category_id,
                leaderboard_type="all_time"
            )
            db.add(leaderboard)

        # Update stats
        leaderboard.total_games += 1
        leaderboard.total_questions += questions_answered
        leaderboard.correct_answers += correct_count
        leaderboard.total_points += points

        if points > leaderboard.highest_score:
            leaderboard.highest_score = points

        if streak > leaderboard.best_streak:
            leaderboard.best_streak = streak

        leaderboard.current_streak = streak

        db.commit()

    @staticmethod
    def get_leaderboard(
        db: Session,
        category_id: Optional[str] = None,
        leaderboard_type: str = "all_time",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get leaderboard rankings

        Args:
            db: Database session
            category_id: Category filter (None for overall)
            leaderboard_type: daily, weekly, monthly, all_time
            limit: Number of entries to return

        Returns:
            List of leaderboard entries with user info
        """
        from models.quiz import QuizLeaderboard
        from models.user import User

        query = db.query(QuizLeaderboard, User).join(
            User, QuizLeaderboard.user_id == User.id
        ).filter(
            QuizLeaderboard.leaderboard_type == leaderboard_type
        )

        if category_id:
            query = query.filter(QuizLeaderboard.category_id == category_id)
        else:
            query = query.filter(QuizLeaderboard.category_id.is_(None))

        # Order by total points descending
        query = query.order_by(QuizLeaderboard.total_points.desc())

        # Limit results
        results = query.limit(limit).all()

        # Format response
        leaderboard_data = []
        for rank, (leaderboard, user) in enumerate(results, 1):
            entry = leaderboard.to_dict()
            entry["rank"] = rank
            entry["user_name"] = user.display_name
            entry["user_avatar"] = getattr(user, 'avatar_url', None)
            leaderboard_data.append(entry)

        return leaderboard_data


# Create singleton instance
quiz_question_manager = QuizQuestionManager()
