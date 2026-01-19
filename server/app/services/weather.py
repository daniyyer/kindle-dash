"""
和风天气 API 服务

提供以下功能:
- 实时天气（温度、天气状况、体感温度、风力风向）
- 空气质量（AQI指数、等级）
- 分钟级降水预报（未来2小时）
- 逐日天气预报（未来3天）
"""

import httpx
from typing import Optional
from dataclasses import dataclass
from app.config import QWEATHER_API_KEY, QWEATHER_BASE_URL, LOCATION


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
    """获取实时天气"""
    urls = [
        f"https://devapi.qweather.com/v7/weather/now",
        f"https://api.qweather.com/v7/weather/now"
    ]
    
    last_error = None
    async with httpx.AsyncClient(follow_redirects=True) as client:
        for url in urls:
            try:
                resp = await client.get(
                    url,
                    params={"key": QWEATHER_API_KEY, "location": location},
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
                elif data.get("code") in ["401", "403"]:
                    last_error = f"API Key error or Invalid Host ({data.get('code')})"
                    continue # 尝试下一个域名
                else:
                    raise Exception(f"Weather API error: {data.get('code')}")
            except Exception as e:
                last_error = str(e)
                continue
                
    raise Exception(f"Failed to fetch weather: {last_error}")


async def fetch_air_quality(location: str = LOCATION) -> Optional[AirQuality]:
    """获取空气质量"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{QWEATHER_BASE_URL}/air/now",
            params={"key": QWEATHER_API_KEY, "location": location}
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
            params={"key": QWEATHER_API_KEY, "location": location}
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
            params={"key": QWEATHER_API_KEY, "location": location}
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
