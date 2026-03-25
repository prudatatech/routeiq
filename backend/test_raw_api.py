import requests
import json

url = "https://vqjmdzvjknhhdwpswvvh.supabase.co"
service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZxam1denZqa25oaGR3cHN3dnZoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDQzNzU1NywiZXhwIjoyMDkwMDEzNTU3fQ.W-MsOnGxBNIMeaYd1Dh9eTl8y3tuRy4Z6nojueof7q8"
anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZxam1denZqa25oaGR3cHN3dnZoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ0Mzc1NTcsImV4cCI6MjA5MDAxMzU1N30.j8rC5a8U3E4a-15ekL5lqomfl4ghE9QXvHg9JApXpbE"

print(f"Testing direct connection to: {url}")

def test_key(name, key):
    print(f"\nTesting {name} key...")
    try:
        r = requests.get(
            f"{url}/rest/v1/",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}"
            }
        )
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

test_key("Anon", anon_key)
test_key("Service Role", service_key)

# Test Auth health
print("\nTesting Auth Health...")
r = requests.get(f"{url}/auth/v1/health")
print(f"Status: {r.status_code}")
print(f"Response: {r.text}")
