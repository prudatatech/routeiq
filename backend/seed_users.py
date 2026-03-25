import asyncio
import uuid
import bcrypt
from app.core.database import get_db

def hash_password(password: str) -> str:
    pw_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw_bytes, salt).decode("utf-8")

async def seed_users():
    print("--- SEEDING USERS VIA SUPABASE CLIENT ---")
    db = get_db()
    
    users_to_seed = [
        {
            "id": str(uuid.uuid4()),
            "email": "admin@routeiq.io",
            "full_name": "Fleet Admin",
            "password": "Admin1234!",
            "role": "admin"
        },
        {
            "id": str(uuid.uuid4()),
            "email": "driver@routeiq.io",
            "full_name": "John Driver",
            "password": "Driver1234!",
            "role": "driver"
        }
    ]
    
    for u_data in users_to_seed:
        # Check if exists
        res = db.table("users").select("id").eq("email", u_data["email"]).execute()
        if not res.data:
            print(f"Creating user: {u_data['email']}")
            hashed = hash_password(u_data["password"])
            new_user = {
                "id": u_data["id"],
                "email": u_data["email"],
                "full_name": u_data["full_name"],
                "hashed_password": hashed,
                "role": u_data["role"],
                "is_active": True
            }
            db.table("users").insert(new_user).execute()
        else:
            print(f"User already exists: {u_data['email']}")
            
    print("--- SEED COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(seed_users())
