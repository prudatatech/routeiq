import os
from dotenv import load_dotenv
from supabase import create_client

def create_admin_user():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(env_path)
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in .env")
        return

    supabase = create_client(url, key)
    
    email = "admin@routeiq.com"
    password = "RouteIQ_Admin_2026!"
    
    print(f"Attempting to create user: {email}")
    
    try:
        # Create user via Auth Admin API (bypasses email confirmation)
        res = supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {"full_name": "System Administrator"}
        })
        print(f"✅ Success! User created with ID: {res.user.id}")
        print(f"\nLogin Credentials:")
        print(f"Email: {email}")
        print(f"Password: {password}")
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        if "already registered" in str(e).lower():
            print("Note: This user already exists in your Supabase Auth.")

if __name__ == "__main__":
    create_admin_user()
