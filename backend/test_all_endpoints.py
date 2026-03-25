import requests

service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZxam1denZqa25oaGR3cHN3dnZoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDQzNzU1NywiZXhwIjoyMDkwMDEzNTU3fQ.W-MsOnGxBNIMeaYd1Dh9eTl8y3tuRy4Z6nojueof7q8"
anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZxam1denZqa25oaGR3cHN3dnZoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ0Mzc1NTcsImV4cCI6MjA5MDAxMzU1N30.j8rC5a8U3E4a-15ekL5lqomfl4ghE9QXvHg9JApXpbE"

urls = [
    "https://routeiq.prudata-tech.workers.dev",
    "https://vqjmdzvjknhhdwpswvvh.supabase.co"
]

def test(url, name, key):
    print(f"\n[Testing {url}] with {name} key")
    try:
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}"
        }
        r = requests.get(f"{url}/auth/v1/health", headers=headers)
        print(f"Health Status: {r.status_code}")
        
        r2 = requests.get(f"{url}/rest/v1/", headers=headers)
        print(f"Rest Status: {r2.status_code}")
        if r2.status_code != 200:
            print(f"Rest Body: {r2.text[:100]}")
            
    except Exception as e:
        print(f"Error: {e}")

for url in urls:
    test(url, "Anon", anon_key)
    test(url, "Service Role", service_key)
