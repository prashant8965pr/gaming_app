"""
Admin User Seed Script
Creates a default admin user for the gaming platform
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from config.database import get_async_session, async_engine
from models.user import User
from core.security import hash_password
import uuid


async def create_admin_user(db: AsyncSession):
    """Create default admin user"""

    # Check if admin already exists
    result = await db.execute(
        select(User).where(User.username == "admin")
    )
    existing_admin = result.scalar_one_or_none()

    if existing_admin:
        print("✅ Admin user already exists")
        print(f"   Username: {existing_admin.username}")
        print(f"   Email: {existing_admin.email}")
        print(f"   Role: {existing_admin.role}")
        return existing_admin

    # Create admin user
    admin_password = "Admin@123"  # Change this in production!
    admin_user = User(
        id=uuid.uuid4(),
        username="admin",
        email="admin@gamingplatform.com",
        phone="+919999999999",
        password_hash=hash_password(admin_password),
        display_name="Platform Administrator",
        role="superadmin",
        status="active",
        kyc_status="verified",
        is_email_verified=True,
        is_phone_verified=True,
        referral_code="ADMIN001"
    )

    db.add(admin_user)
    await db.commit()
    await db.refresh(admin_user)

    print("✅ Admin user created successfully!")
    print(f"   Username: {admin_user.username}")
    print(f"   Email: {admin_user.email}")
    print(f"   Phone: {admin_user.phone}")
    print(f"   Password: {admin_password}")
    print(f"   Role: {admin_user.role}")
    print(f"   ID: {admin_user.id}")
    print("\n⚠️  IMPORTANT: Change the default password immediately!")

    return admin_user


async def create_demo_users(db: AsyncSession):
    """Create demo users for testing"""

    demo_users_data = [
        {
            "username": "player1",
            "email": "player1@example.com",
            "phone": "+919876543210",
            "display_name": "Demo Player 1",
            "role": "user",
            "password": "Player1@123"
        },
        {
            "username": "player2",
            "email": "player2@example.com",
            "phone": "+919876543211",
            "display_name": "Demo Player 2",
            "role": "user",
            "password": "Player2@123"
        },
        {
            "username": "player3",
            "email": "player3@example.com",
            "phone": "+919876543212",
            "display_name": "Demo Player 3",
            "role": "user",
            "password": "Player3@123"
        }
    ]

    created_count = 0

    for user_data in demo_users_data:
        # Check if user already exists
        result = await db.execute(
            select(User).where(User.username == user_data["username"])
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            continue

        # Create demo user
        demo_user = User(
            id=uuid.uuid4(),
            username=user_data["username"],
            email=user_data["email"],
            phone=user_data["phone"],
            password_hash=hash_password(user_data["password"]),
            display_name=user_data["display_name"],
            role=user_data["role"],
            status="active",
            kyc_status="pending",
            is_email_verified=True,
            is_phone_verified=True,
            referral_code=f"DEMO{user_data['username'][-1:].upper()}001"
        )

        db.add(demo_user)
        created_count += 1

    if created_count > 0:
        await db.commit()
        print(f"\n✅ Created {created_count} demo users")
        print("   Demo credentials:")
        for user_data in demo_users_data:
            print(f"   - {user_data['username']} / {user_data['password']}")
    else:
        print("\n✅ Demo users already exist")


async def main():
    """Main seed function"""
    print("=" * 60)
    print("Gaming Platform - Admin User Seed Script")
    print("=" * 60)
    print()

    try:
        # Get database session
        async for session in get_async_session():
            # Create admin user
            await create_admin_user(session)

            # Create demo users
            await create_demo_users(session)

            print()
            print("=" * 60)
            print("✅ Seeding completed successfully!")
            print("=" * 60)
            break

    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
