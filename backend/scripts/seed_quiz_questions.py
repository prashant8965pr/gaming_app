"""
Seed Quiz Questions
Populate the quiz question bank with questions from Open Trivia DB
"""
import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from config.database import async_session_maker
from models.quiz import QuizCategory, QuizQuestion
from utils.quiz_questions import QuizQuestionManager
import uuid


# Category definitions
CATEGORIES = [
    {
        "code": "general",
        "name": "General Knowledge",
        "description": "Test your knowledge across various topics",
        "difficulty_multiplier": 1.0,
    },
    {
        "code": "science_nature",
        "name": "Science & Nature",
        "description": "Questions about science and the natural world",
        "difficulty_multiplier": 1.2,
    },
    {
        "code": "history",
        "name": "History",
        "description": "Historical events, figures, and periods",
        "difficulty_multiplier": 1.1,
    },
    {
        "code": "geography",
        "name": "Geography",
        "description": "Countries, capitals, landmarks, and more",
        "difficulty_multiplier": 1.0,
    },
    {
        "code": "sports",
        "name": "Sports",
        "description": "All about sports, athletes, and competitions",
        "difficulty_multiplier": 1.0,
    },
    {
        "code": "film",
        "name": "Movies & Film",
        "description": "Cinema, movies, actors, and directors",
        "difficulty_multiplier": 0.9,
    },
    {
        "code": "music",
        "name": "Music",
        "description": "Artists, songs, albums, and music theory",
        "difficulty_multiplier": 0.9,
    },
    {
        "code": "computers",
        "name": "Technology & Computers",
        "description": "Technology, computing, and digital world",
        "difficulty_multiplier": 1.2,
    },
]


async def seed_categories(db: Session) -> dict:
    """Seed quiz categories"""
    print("Seeding quiz categories...")

    category_map = {}

    for cat_data in CATEGORIES:
        # Check if exists
        existing = db.query(QuizCategory).filter(
            QuizCategory.code == cat_data["code"]
        ).first()

        if existing:
            print(f"  ✓ Category '{cat_data['name']}' already exists")
            category_map[cat_data["code"]] = existing
        else:
            category = QuizCategory(
                code=cat_data["code"],
                name=cat_data["name"],
                description=cat_data["description"],
                difficulty_multiplier=cat_data["difficulty_multiplier"],
                is_active=True,
                total_questions=0,
            )
            db.add(category)
            db.commit()
            db.refresh(category)
            category_map[cat_data["code"]] = category
            print(f"  ✓ Created category '{cat_data['name']}'")

    print(f"✅ Seeded {len(category_map)} categories\n")
    return category_map


async def seed_questions_for_category(
    db: Session,
    category: QuizCategory,
    category_code: str,
    num_questions: int = 150
):
    """Seed questions for a specific category"""
    print(f"Seeding questions for '{category.name}'...")

    # Check existing count
    existing_count = db.query(QuizQuestion).filter(
        QuizQuestion.category_id == category.id
    ).count()

    if existing_count >= num_questions:
        print(f"  ✓ Already has {existing_count} questions, skipping")
        return

    needed = num_questions - existing_count
    print(f"  Need {needed} more questions...")

    # Fetch questions from OpenTDB for each difficulty
    difficulties = ["easy", "medium", "hard"]
    questions_per_difficulty = needed // 3

    total_added = 0

    for difficulty in difficulties:
        print(f"  Fetching {questions_per_difficulty} {difficulty} questions...")

        try:
            raw_questions = await QuizQuestionManager.fetch_from_opentdb(
                category=category_code,
                difficulty=difficulty,
                num_questions=questions_per_difficulty
            )

            if not raw_questions:
                print(f"    ⚠️  No questions returned from API")
                continue

            # Parse and save questions
            for raw_q in raw_questions:
                parsed = QuizQuestionManager.parse_opentdb_question(raw_q)

                question = QuizQuestion(
                    category_id=category.id,
                    **parsed,
                    is_active=True,
                    is_verified=True,  # Auto-verify API questions
                )

                db.add(question)
                total_added += 1

            db.commit()
            print(f"    ✓ Added {len(raw_questions)} {difficulty} questions")

        except Exception as e:
            print(f"    ✗ Error fetching {difficulty} questions: {e}")
            continue

        # Small delay to respect API rate limits
        await asyncio.sleep(1)

    # Update category question count
    category.total_questions = db.query(QuizQuestion).filter(
        QuizQuestion.category_id == category.id
    ).count()
    db.commit()

    print(f"  ✅ Added {total_added} questions, total now: {category.total_questions}\n")


async def main():
    """Main seed function"""
    print("=" * 60)
    print("QUIZ QUESTIONS SEEDER")
    print("=" * 60)
    print()

    async with async_session_maker() as db:
        try:
            # Seed categories
            category_map = await seed_categories(db)

            # Seed questions for each category
            for code, category in category_map.items():
                await seed_questions_for_category(db, category, code, num_questions=150)

            # Print summary
            print("=" * 60)
            print("SUMMARY")
            print("=" * 60)

            total_questions = db.query(QuizQuestion).count()
            total_categories = db.query(QuizCategory).count()

            print(f"Total Categories: {total_categories}")
            print(f"Total Questions: {total_questions}")
            print()

            # Per category breakdown
            for category in category_map.values():
                count = db.query(QuizQuestion).filter(
                    QuizQuestion.category_id == category.id
                ).count()
                print(f"  {category.name}: {count} questions")

            print()
            print("✅ Seeding complete!")

        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    # Run async main
    asyncio.run(main())
