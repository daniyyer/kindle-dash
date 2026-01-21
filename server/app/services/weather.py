"""
QWeather API Service

Features:
- Real-time weather (temperature, conditions, feels-like, wind)
- Air quality (AQI index, category)
- Minutely precipitation forecast (next 2 hours)
- Daily forecast (next 3 days)
"""

import time
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass

import httpx
import jwt

from app.config import (
    QWEATHER_BASE_URL,
    QWEATHER_PROJECT_ID,
    QWEATHER_KEY_ID,
    QWEATHER_PRIVATE_KEY,
    LOCATION,
    LOCATION_NAME
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
    obs_time: str       # 观测时间 (16:35)


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
    location_name: str    # 地理位置名称 (例如: 太仓, 北京)
    current: CurrentWeather
    air: Optional[AirQuality]
    minutely: Optional[MinutelyRain]
    daily: list[DailyForecast]


async def fetch_current_weather(location: str = LOCATION) -> CurrentWeather:
    """Fetch current grid weather (格点天气)"""
    # 使用格点天气 API 路径
    url = f"{QWEATHER_BASE_URL}/grid-weather/now"

    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            resp = await client.get(
                url,
                headers=get_auth_headers(),
                params={"location": location},
                timeout=10.0
            )
            data = resp.json()
            # 如果格点天气返回 403 或 404，则回退到普通实时天气
            if data.get("code") in ["403", "404"]:
                url = f"{QWEATHER_BASE_URL}/weather/now"
                resp = await client.get(
                    url,
                    headers=get_auth_headers(),
                    params={"location": location},
                    timeout=10.0
                )
                data = resp.json()

            if data.get("code") == "200":
                now = data["now"]

                # 提取时间并转为北京时间 (处理 2024-01-20T02:00+00:00 格式)
                obs_time_raw = now.get("obsTime", "")
                obs_time = "未知"
                if obs_time_raw:
                    try:
                        # 解析 ISO 格式时间 (例如 2026-01-20T02:00+00:00)
                        # 虽然 Python 3.7+ fromisoformat 支持，但处理末尾的 +00:00 兼容性更好
                        dt_utc = datetime.fromisoformat(obs_time_raw.replace('Z', '+00:00'))
                        # 转为北京时间 (+8h)
                        dt_beijing = dt_utc + timedelta(hours=8)
                        obs_time = dt_beijing.strftime("%H:%M")
                    except (ValueError, TypeError, IndexError):
                        # 处理时间解析失败的多种可能
                        obs_time = obs_time_raw[11:16] if len(obs_time_raw) >= 16 else "未知"

                return CurrentWeather(
                    temp=now["temp"],
                    feels_like=now["feelsLike"],
                    text=now["text"],
                    icon=now["icon"],
                    wind_dir=now["windDir"],
                    wind_scale=now["windScale"],
                    obs_time=obs_time
                )
            else:
                return CurrentWeather(
                    temp="N/A", feels_like="N/A", text="Error", icon="999",
                    wind_dir="", wind_scale="", obs_time="N/A"
                )
        except (httpx.HTTPError, KeyError, ValueError, TypeError):
            return CurrentWeather(
                temp="N/A", feels_like="N/A", text="Error", icon="999",
                wind_dir="", wind_scale="", obs_time="N/A"
            )


async def fetch_air_quality(location: str = LOCATION) -> Optional[AirQuality]:
    """获取高精度空气质量 (使用 /airquality/v1/current 接口)"""
    # 提取经纬度并处理格式: latitude/longitude (保留2位小数)
    try:
        lon, lat = location.split(',')
        lat = f"{float(lat):.2f}"
        lon = f"{float(lon):.2f}"
    except (ValueError, AttributeError, IndexError):
        # 如果不是坐标格式，回退到老接口尝试
        return await _fetch_air_quality_v7(location)

    async with httpx.AsyncClient() as client:
        # 注意: 此接口路径不含 /v7
        api_host = QWEATHER_BASE_URL.split('/v7', maxsplit=1)[0]
        url = f"{api_host}/airquality/v1/current/{lat}/{lon}"

        resp = await client.get(url, headers=get_auth_headers())
        data = resp.json()

        if resp.status_code != 200:
            return None

        # 寻找中国标准 (cn-mee)
        indexes = data.get("indexes", [])
        cn_index = next((i for i in indexes if i.get("code") == "cn-mee"), None)

        if not cn_index:
            # 如果没找到，取第一个
            cn_index = indexes[0] if indexes else {}

        return AirQuality(
            aqi=str(cn_index.get("aqi", "N/A")),
            category=cn_index.get("category", "")
        )


async def _fetch_air_quality_v7(location: str) -> Optional[AirQuality]:
    """老版本 v7 接口，作为回退或兼容逻辑"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{QWEATHER_BASE_URL}/air/now",
                headers=get_auth_headers(),
                params={"location": location},
                timeout=5.0
            )
            data = resp.json()
            if data.get("code") == "200":
                now = data.get("now", {})
                return AirQuality(aqi=now.get("aqi", "N/A"), category=now.get("category", ""))
    except (httpx.HTTPError, ValueError, KeyError):
        return None
    return None


async def fetch_minutely_rain(location: str = LOCATION) -> Optional[MinutelyRain]:
    """获取分钟级降水预报"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{QWEATHER_BASE_URL}/minutely/5m",
                headers=get_auth_headers(),
                params={"location": location},
                timeout=5.0
            )
            data = resp.json()

            if data.get("code") != "200":
                return None

            summary = data.get("summary", "未来2小时天气情况未知")
            return MinutelyRain(summary=summary)
    except (httpx.HTTPError, ValueError, KeyError):
        return None


async def fetch_daily_forecast(location: str = LOCATION, days: int = 3) -> list[DailyForecast]:
    """获取逐日天气预报"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{QWEATHER_BASE_URL}/weather/{days}d",
                headers=get_auth_headers(),
                params={"location": location},
                timeout=5.0
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
    except (httpx.HTTPError, ValueError, KeyError):
        return []


async def get_weather_data(location: str = LOCATION) -> WeatherData:
    """获取所有天气数据"""
    current = await fetch_current_weather(location)
    air = await fetch_air_quality(location)
    minutely = await fetch_minutely_rain(location)
    daily = await fetch_daily_forecast(location)

    # 获取地理位置名称，优先使用配置中的名称
    return WeatherData(
        location_name=LOCATION_NAME,
        current=current,
        air=air,
        minutely=minutely,
        daily=daily
    )
