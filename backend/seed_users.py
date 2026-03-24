import asyncio
import uuid
import bcrypt
from datetime import datetime, timezone
from sqlalchemy import text, select
from app.core.database import AsyncSessionLocal, engine
from app.models.models import User

async def seed_users():
    print("--- SEEDING USERS ---")
    async with AsyncSessionLocal() as session:
        users_to_seed = [
            {
                "email": "superadmin@routeiq.io",
                "full_name": "Platform Superadmin",
                "password": "SuperAdmin1234!",
                "role": "superadmin"
            },
            {
                "email": "admin@routeiq.io",
                "full_name": "Fleet Admin",
                "password": "Admin1234!",
                "role": "admin"
            },
            {
                "email": "manager@routeiq.io",
                "full_name": "Fleet Manager",
                "password": "Manager1234!",
                "role": "manager"
            },
            {
                "email": "driver@routeiq.io",
                "full_name": "John Driver",
                "password": "Driver1234!",
                "role": "driver"
            }
        ]
        
        for u_data in users_to_seed:
            result = await session.execute(select(User).where(User.email == u_data["email"]))
            user = result.scalar_one_or_none()
            if not user:
                print(f"Creating user: {u_data['email']} ({u_data['role']})")
                hashed = bcrypt.hashpw(u_data["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                user = User(
                    email=u_data["email"],
                    full_name=u_data["full_name"],
                    hashed_password=hashed,
                    role=u_data["role"],
                    is_active=True
                )
                session.add(user)
            else:
                print(f"User already exists: {u_data['email']}")
        
        await session.commit()
    print("--- USER SEED COMPLETE ---")

async def main():
    await seed_users()
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
