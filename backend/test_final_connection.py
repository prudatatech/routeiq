import requests
import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print(f"Target URL: {url}")
print(f"Key Prefix: {key[:20]}...")

# Test 1: Direct hitting the rest endpoint
print("\nTest 1: Direct POSTGREST")
try:
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    r = requests.get(f"{url}/rest/v1/", headers=headers)
    print(f"Status: {r.status_code}")
    print(f"Body: {r.text}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Auth Endpoints
print("\nTest 2: AUTH ADMIN USERS")
try:
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}"
    }
    r = requests.get(f"{url}/auth/v1/admin/users", headers=headers)
    print(f"Status: {r.status_code}")
    print(f"Body: {r.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
