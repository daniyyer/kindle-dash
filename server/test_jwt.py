"""Debug script to test QWeather JWT authentication"""
import asyncio
import time
import os
import jwt
import httpx
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("QWEATHER_PROJECT_ID")
KEY_ID = os.getenv("QWEATHER_KEY_ID")
PRIVATE_KEY = os.getenv("QWEATHER_PRIVATE_KEY", "").replace("\\n", "\n")
LOCATION = os.getenv("LOCATION", "116.41,39.92")
API_HOST = os.getenv("QWEATHER_API_HOST", "devapi.qweather.com")

print(f"Project ID: {PROJECT_ID}")
print(f"Key ID: {KEY_ID}")
print(f"Private Key (first 50 chars): {PRIVATE_KEY[:50]}...")
print(f"Location: {LOCATION}")
print(f"API Host: {API_HOST}")
print()

def generate_jwt():
    now = int(time.time())
    payload = {
        "sub": PROJECT_ID,
        "iat": now - 30,
        "exp": now + 900
    }
    headers = {"kid": KEY_ID}
    
    token = jwt.encode(payload, PRIVATE_KEY, algorithm="EdDSA", headers=headers)
    return token

async def test_api():
    token = generate_jwt()
    print(f"Generated JWT: {token[:50]}...")
    print()
    
    url = f"https://{API_HOST}/v7/weather/now"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"location": LOCATION}
    
    print(f"Request URL: {url}")
    print(f"Request params: {params}")
    print()
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, params=params, timeout=10.0)
        print(f"Response status: {resp.status_code}")
        print(f"Response headers: {dict(resp.headers)}")
        print(f"Response body: {resp.text}")

if __name__ == "__main__":
    asyncio.run(test_api())
