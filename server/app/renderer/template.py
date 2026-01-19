"""
HTML 模板渲染器

使用 Jinja2 将天气和新闻数据渲染成 HTML
"""

from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from app.services.weather import WeatherData
from app.services.news import NewsData


# 天气图标代码 -> Emoji 映射
WEATHER_EMOJI_MAP = {
    "100": "☀️",   # 晴
    "101": "⛅",   # 多云
    "102": "⛅",   # 少云
    "103": "⛅",   # 晴间多云
    "104": "☁️",   # 阴
    "150": "🌙",   # 晴(夜)
    "151": "🌙",   # 多云(夜)
    "300": "🌧️",  # 阵雨
    "301": "🌧️",  # 强阵雨
    "302": "⛈️",   # 雷阵雨
    "303": "⛈️",   # 强雷阵雨
    "304": "⛈️",   # 雷阵雨伴有冰雹
    "305": "🌧️",  # 小雨
    "306": "🌧️",  # 中雨
    "307": "🌧️",  # 大雨
    "308": "🌧️",  # 极端降雨
    "309": "🌧️",  # 毛毛雨
    "310": "🌧️",  # 暴雨
    "311": "🌧️",  # 大暴雨
    "312": "🌧️",  # 特大暴雨
    "313": "🌧️",  # 冻雨
    "314": "🌧️",  # 小到中雨
    "315": "🌧️",  # 中到大雨
    "316": "🌧️",  # 大到暴雨
    "317": "🌧️",  # 暴雨到大暴雨
    "318": "🌧️",  # 大暴雨到特大暴雨
    "399": "🌧️",  # 雨
    "400": "❄️",   # 小雪
    "401": "❄️",   # 中雪
    "402": "❄️",   # 大雪
    "403": "❄️",   # 暴雪
    "404": "🌨️",  # 雨夹雪
    "405": "🌨️",  # 雨雪天气
    "406": "🌨️",  # 阵雨夹雪
    "407": "🌨️",  # 阵雪
    "408": "❄️",   # 小到中雪
    "409": "❄️",   # 中到大雪
    "410": "❄️",   # 大到暴雪
    "499": "❄️",   # 雪
    "500": "🌫️",  # 薄雾
    "501": "🌫️",  # 雾
    "502": "🌫️",  # 霾
    "503": "🌫️",  # 扬沙
    "504": "🌫️",  # 浮尘
    "507": "🌫️",  # 沙尘暴
    "508": "🌫️",  # 强沙尘暴
    "509": "🌫️",  # 浓雾
    "510": "🌫️",  # 强浓雾
    "511": "🌫️",  # 中度霾
    "512": "🌫️",  # 重度霾
    "513": "🌫️",  # 严重霾
    "514": "🌫️",  # 大雾
    "515": "🌫️",  # 特强浓雾
    "900": "🔥",   # 热
    "901": "🥶",   # 冷
    "999": "❓",   # 未知
}


def get_weather_emoji(icon_code: str) -> str:
    """获取天气 emoji"""
    return WEATHER_EMOJI_MAP.get(icon_code, "🌡️")


def get_weekday_name(date: datetime) -> str:
    """获取星期几"""
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return weekdays[date.weekday()]


def render_dashboard_html(weather: WeatherData, news: NewsData) -> str:
    """渲染仪表盘 HTML"""
    template_dir = Path(__file__).parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("dashboard.html")
    
    now = datetime.now()
    
    # 格式化日期
    date_str = f"{now.year}年{now.month}月{now.day}日 {get_weekday_name(now)}"
    update_time = now.strftime("%H:%M")
    
    # 获取天气 emoji
    weather_emoji = get_weather_emoji(weather.current.icon)
    
    return template.render(
        date_str=date_str,
        update_time=update_time,
        weather=weather,
        weather_emoji=weather_emoji,
        news=news
    )
