"""
Seed Quiz Categories
Create initial quiz categories
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import settings
from models.quiz import QuizCategory


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
    {
        "code": "mythology",
        "name": "Mythology",
        "description": "Ancient myths, legends, and folklore",
        "difficulty_multiplier": 1.1,
    },
    {
        "code": "art",
        "name": "Art",
        "description": "Paintings, sculptures, and artistic movements",
        "difficulty_multiplier": 1.0,
    },
]


def main():
    """Main seed function"""
    print("=" * 60)
    print("QUIZ CATEGORIES SEEDER")
    print("=" * 60)
    print()

    # Create database connection (sync)
    # Convert async URL to sync
    db_url = settings.DATABASE_URL.replace("+asyncpg", "")

    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        created_count = 0
        existing_count = 0

        for cat_data in CATEGORIES:
            # Check if exists
            existing = db.query(QuizCategory).filter(
                QuizCategory.code == cat_data["code"]
            ).first()

            if existing:
                print(f"✓ Category '{cat_data['name']}' already exists")
                existing_count += 1
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
                print(f"+ Created category '{cat_data['name']}'")
                created_count += 1

        db.commit()

        print()
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Created: {created_count}")
        print(f"Already existed: {existing_count}")
        print(f"Total: {created_count + existing_count}")
        print()
        print("✅ Seeding complete!")

    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
