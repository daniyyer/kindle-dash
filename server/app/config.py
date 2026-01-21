import os
from dotenv import load_dotenv

load_dotenv()

# QWeather API configuration
QWEATHER_API_HOST = os.getenv("QWEATHER_API_HOST", "devapi.qweather.com")
QWEATHER_BASE_URL = f"https://{QWEATHER_API_HOST}/v7"

# QWeather JWT authentication (recommended)
QWEATHER_PROJECT_ID = os.getenv("QWEATHER_PROJECT_ID", "")
QWEATHER_KEY_ID = os.getenv("QWEATHER_KEY_ID", "")
QWEATHER_PRIVATE_KEY = os.getenv("QWEATHER_PRIVATE_KEY", "")

# Location (longitude,latitude or city ID)
LOCATION = "121.1462,31.4622"  # Default location (Taicang)
LOCATION_NAME = "太仓"

# 新闻 RSS 配置
NEWS_RSS_DOMESTIC = "https://www.chinanews.com.cn/rss/importnews.xml"
NEWS_RSS_INTERNATIONAL = {
    "国际": "https://news.google.com/rss/search?q=site:reuters.com+world",
    "财经": "https://news.google.com/rss/search?q=site:reuters.com+markets",
    "科技": "https://news.google.com/rss/search?q=site:reuters.com+technology"
}

# 新闻条数
NEWS_COUNT_DOMESTIC = 5
NEWS_COUNT_PER_CATEGORY = 2  # 每个国际分类获取2条

# 截图尺寸 (Kindle 4/5 NT)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
