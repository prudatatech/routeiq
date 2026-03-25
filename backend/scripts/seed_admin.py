import asyncio
import os
import sys
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Add the parent directory to sys.path so we can import 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.security import hash_password
from app.models.models import User, Base

async def seed_admin():
    print("🚀 Starting Admin Seeding...")
    
    # Check if DATABASE_URL is still using the placeholder
    db_url = settings.DATABASE_URL
    if "[YOUR_PASSWORD]" in db_url:
        print("⚠️  Error: Your DATABASE_URL in .env still contains '[YOUR_PASSWORD]'.")
        print("Please replace it with your actual Supabase database password first.")
        return

    engine = create_async_engine(db_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check if admin already exists
        email = "admin@routeiq.com"
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if user:
            print(f"ℹ️  User {email} already exists. Updating password...")
            user.hashed_password = hash_password("Admin@123")
            user.role = "superadmin"
            user.is_active = True
        else:
            print(f"✨ Creating new admin user: {email}")
            user = User(
                email=email,
                full_name="System Administrator",
                hashed_password=hash_password("Admin@123"),
                role="superadmin",
                is_active=True
            )
            session.add(user)

        try:
            await session.commit()
            print("✅ Admin user seeded successfully!")
            print(f"📧 Login: {email}")
            print("🔑 Password: Admin@123")
        except Exception as e:
            print(f"❌ Error during seeding: {e}")
            await session.rollback()
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_admin())
