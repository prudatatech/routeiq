import os
import httpx
from dotenv import load_dotenv
from supabase import create_client

def debug():
    # Load .env
    load_dotenv('./backend/.env')
    url = os.getenv('SUPABASE_URL') # Proxy
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    anon = os.getenv('SUPABASE_ANON_KEY')
    
    # The direct URL
    direct_url = "https://vqjmdzvjknhhdwpswvvh.supabase.co"

    print(f"--- Supabase Credential Debug ---")
    print(f"Project Reference: vqjmdzvjknhhdwpswvvh")
    
    print(f"\n[1/3] Testing DIRECT URL with Service Role Key...")
    try:
        # We use curl-like headers to be sure
        headers = {"apikey": key, "Authorization": f"Bearer {key}"}
        res = httpx.get(f"{direct_url}/rest/v1/users?select=id&limit=1", headers=headers, timeout=10)
        if res.status_code == 200:
            print(f"[SUCCESS] Direct URL accepted the Service Role Key!")
        else:
            print(f"[FAILED] Direct URL rejected the Key. Status: {res.status_code}")
            print(f"Response: {res.text}")
    except Exception as e:
        print(f"[ERROR] Direct connection error: {str(e)}")

    print(f"\n[2/3] Testing PROXY URL with Service Role Key...")
    try:
        headers = {"apikey": key, "Authorization": f"Bearer {key}"}
        res = httpx.get(f"{url}/rest/v1/users?select=id&limit=1", headers=headers, timeout=10)
        if res.status_code == 200:
            print(f"[SUCCESS] Proxy URL accepted the Service Role Key!")
        else:
            print(f"[FAILED] Proxy URL rejected the Key. Status: {res.status_code}")
            print(f"Response: {res.text}")
    except Exception as e:
        print(f"[ERROR] Proxy connection error: {str(e)}")

    print(f"\n[3/3] Testing Supabase Python Client (Final Verification)")
    try:
        supabase = create_client(url, key)
        res = supabase.table("users").select("id", count="exact").limit(1).execute()
        print(f"[SUCCESS] Client works! User count: {res.count}")
    except Exception as e:
        print(f"[FAILED] Client check failed: {str(e)}")

if __name__ == "__main__":
    debug()
