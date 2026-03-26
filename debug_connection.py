import os
import httpx
from dotenv import load_dotenv
from supabase import create_client

def debug():
    # Load .env
    load_dotenv('./backend/.env')
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    anon = os.getenv('SUPABASE_ANON_KEY')
    
    print(f"--- Environment ---")
    print(f"SUPABASE_URL: {url}")
    print(f"Keys Loaded: {'Yes' if key and anon else 'No'}")
    
    print(f"\n--- Network Checks ---")
    
    # 1. Direct Supabase Domain (Expected to fail if Jio blocks it)
    direct_url = "https://vqjmdzvjknhhdwpswvvh.supabase.co"
    try:
        httpx.get(f"{direct_url}/rest/v1/", timeout=5)
        print(f"[SUCCESS] Direct connection to {direct_url} works!")
    except Exception as e:
        print(f"[BLOCKED] Direct connection to {direct_url} failed (Expected on Jio).")

    # 2. Proxy Check
    if not url:
        print("[ERROR] SUPABASE_URL is missing in .env")
        return

    try:
        res = httpx.get(f"{url}/rest/v1/", headers={"apikey": anon}, timeout=10)
        print(f"[SUCCESS] Proxy {url} is reachable. Status: {res.status_code}")
    except Exception as e:
        print(f"[FAILED] Proxy {url} is unreachable: {str(e)}")

    print(f"\n--- Supabase Client Test ---")
    try:
        supabase = create_client(url, key)
        # Try a simple select
        res = supabase.table("users").select("id", count="exact").limit(1).execute()
        print(f"[SUCCESS] Database query successful! User count: {res.count}")
    except Exception as e:
        print(f"[FAILED] Supabase Client check failed: {str(e)}")
        if "Invalid API key" in str(e):
            print(">>> ALERT: Your SERVICE_ROLE_KEY is still being rejected by Supabase!")

if __name__ == "__main__":
    debug()
