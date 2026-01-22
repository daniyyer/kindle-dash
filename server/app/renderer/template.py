"""
HTML 模板渲染器

使用 Jinja2 将天气和新闻数据渲染成 HTML
"""

from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from jinja2 import Environment, FileSystemLoader
from app.services.weather import WeatherData
from app.services.news import NewsData

# 中国时区
CHINA_TZ = ZoneInfo("Asia/Shanghai")


def get_weekday_name(date: datetime) -> str:
    """获取星期几"""
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return weekdays[date.weekday()]


def render_dashboard_html(weather: WeatherData, news: NewsData) -> str:
    """渲染仪表盘 HTML"""
    template_dir = Path(__file__).parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("dashboard.html")
    
    now = datetime.now(CHINA_TZ)
    
    # 格式化日期
    date_str = f"{now.year}年{now.month}月{now.day}日 {get_weekday_name(now)}"
    update_time = now.strftime("%H:%M")
    
    return template.render(
        date_str=date_str,
        update_time=update_time,
        weather=weather,
        news=news
    )
