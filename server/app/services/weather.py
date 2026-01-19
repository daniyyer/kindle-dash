"""
QWeather API Service

Features:
- Real-time weather (temperature, conditions, feels-like, wind)
- Air quality (AQI index, category)
- Minutely precipitation forecast (next 2 hours)
- Daily forecast (next 3 days)
"""

import time
import httpx
import jwt
from typing import Optional
from dataclasses import dataclass
from app.config import (
    QWEATHER_BASE_URL,
    QWEATHER_PROJECT_ID,
    QWEATHER_KEY_ID,
    QWEATHER_PRIVATE_KEY,
    LOCATION
)


def generate_jwt_token() -> str:
    """
    Generate a JWT token for QWeather API authentication.
    Uses EdDSA (Ed25519) algorithm as required by QWeather.
    """
    now = int(time.time())
    
    # Prepare private key (handle newlines in env var)
    private_key = QWEATHER_PRIVATE_KEY.replace("\\n", "\n")
    
    payload = {
        "sub": QWEATHER_PROJECT_ID,
        "iat": now - 30,  # 30 seconds in the past to handle clock skew
        "exp": now + 900   # Valid for 15 minutes
    }
    
    headers = {
        "kid": QWEATHER_KEY_ID
    }
    
    token = jwt.encode(
        payload,
        private_key,
        algorithm="EdDSA",
        headers=headers
    )
    return token


def get_auth_headers() -> dict:
    """Get authorization headers for API requests."""
    token = generate_jwt_token()
    return {"Authorization": f"Bearer {token}"}


@dataclass
class CurrentWeather:
    """实时天气数据"""
    temp: str           # 温度 (°C)
    feels_like: str     # 体感温度 (°C)
    text: str           # 天气状况文字 (晴/多云/雨...)
    icon: str           # 天气图标代码
    wind_dir: str       # 风向 (东北风)
    wind_scale: str     # 风力等级 (3级)


@dataclass
class AirQuality:
    """空气质量数据"""
    aqi: str            # AQI 指数
    category: str       # 空气质量类别 (优/良/轻度污染...)


@dataclass
class MinutelyRain:
    """分钟级降水预报"""
    summary: str        # 预报摘要 (未来2小时无降水 / 10分钟后开始下雨...)


@dataclass
class DailyForecast:
    """逐日天气预报"""
    date: str           # 日期 (01-20)
    text_day: str       # 白天天气
    icon_day: str       # 白天图标
    temp_min: str       # 最低温度
    temp_max: str       # 最高温度


@dataclass
class WeatherData:
    """完整天气数据"""
    current: CurrentWeather
    air: Optional[AirQuality]
    minutely: Optional[MinutelyRain]
    daily: list[DailyForecast]


async def fetch_current_weather(location: str = LOCATION) -> CurrentWeather:
    """Fetch current weather"""
    url = f"{QWEATHER_BASE_URL}/weather/now"
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            resp = await client.get(
                url,
                headers=get_auth_headers(),
                params={"location": location},
                timeout=10.0
            )
            data = resp.json()
            
            if data.get("code") == "200":
                now = data["now"]
                return CurrentWeather(
                    temp=now["temp"],
                    feels_like=now["feelsLike"],
                    text=now["text"],
                    icon=now["icon"],
                    wind_dir=now["windDir"],
                    wind_scale=now["windScale"]
                )
            else:
                raise Exception(f"Weather API error: {data.get('code')} - {data.get('error', {}).get('detail', 'Unknown')}")
        except Exception as e:
            raise Exception(f"Failed to fetch weather: {e}")


async def fetch_air_quality(location: str = LOCATION) -> Optional[AirQuality]:
    """获取空气质量"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{QWEATHER_BASE_URL}/air/now",
            headers=get_auth_headers(),
            params={"location": location}
        )
        data = resp.json()
        
        if data.get("code") != "200":
            return None
        
        now = data.get("now", {})
        return AirQuality(
            aqi=now.get("aqi", "N/A"),
            category=now.get("category", "未知")
        )


async def fetch_minutely_rain(location: str = LOCATION) -> Optional[MinutelyRain]:
    """获取分钟级降水预报"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{QWEATHER_BASE_URL}/minutely/5m",
            headers=get_auth_headers(),
            params={"location": location}
        )
        data = resp.json()
        
        if data.get("code") != "200":
            return None
        
        summary = data.get("summary", "未来2小时天气情况未知")
        return MinutelyRain(summary=summary)


async def fetch_daily_forecast(location: str = LOCATION, days: int = 3) -> list[DailyForecast]:
    """获取逐日天气预报"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{QWEATHER_BASE_URL}/weather/{days}d",
            headers=get_auth_headers(),
            params={"location": location}
        )
        data = resp.json()
        
        if data.get("code") != "200":
            return []
        
        forecasts = []
        for day in data.get("daily", []):
            forecasts.append(DailyForecast(
                date=day["fxDate"][5:],  # 只取月-日
                text_day=day["textDay"],
                icon_day=day["iconDay"],
                temp_min=day["tempMin"],
                temp_max=day["tempMax"]
            ))
        return forecasts


async def get_weather_data(location: str = LOCATION) -> WeatherData:
    """获取所有天气数据"""
    current = await fetch_current_weather(location)
    air = await fetch_air_quality(location)
    minutely = await fetch_minutely_rain(location)
    daily = await fetch_daily_forecast(location)
    
    return WeatherData(
        current=current,
        air=air,
        minutely=minutely,
        daily=daily
    )
