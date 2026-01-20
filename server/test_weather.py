import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("QWEATHER_API_KEY")
LOCATION = os.getenv("LOCATION", "116.41,39.92")

async def test():
    print(f"Testing with Key: {API_KEY[:4]}***, Location: {LOCATION}")
    
    urls = [
        f"https://devapi.qweather.com/v7/weather/now",
        f"https://api.qweather.com/v7/weather/now"
    ]
    
    async with httpx.AsyncClient() as client:
        for url in urls:
            print(f"\nRequesting: {url}")
            try:
                resp = await client.get(url, params={"key": API_KEY, "location": LOCATION})
                print(f"Status: {resp.status_code}")
                print(f"Raw Body: {resp.text}")
                data = resp.json()
                print(f"Json Code: {data.get('code')}")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
