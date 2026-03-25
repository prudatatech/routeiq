import os

env_path = os.path.join(os.path.dirname(__file__), ".env")
with open(env_path, "rb") as f:
    content = f.read()
    print(f"Raw .env content (bytes):")
    print(content)

# Test env loading
from dotenv import load_dotenv
load_dotenv(env_path)
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
print(f"\nLoaded URL: '{url}'")
print(f"Loaded Key (first 10): '{key[:10]}...'")
print(f"Loaded Key (last 10): '...{key[-10:]}'")
