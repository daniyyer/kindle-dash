import os
from dotenv import load_dotenv

load_dotenv()

# QWeather API configuration
QWEATHER_API_KEY = os.getenv("QWEATHER_API_KEY", "")  # Legacy, kept for compatibility
QWEATHER_API_HOST = os.getenv("QWEATHER_API_HOST", "devapi.qweather.com")
QWEATHER_BASE_URL = f"https://{QWEATHER_API_HOST}/v7"

# QWeather JWT authentication (recommended)
QWEATHER_PROJECT_ID = os.getenv("QWEATHER_PROJECT_ID", "")
QWEATHER_KEY_ID = os.getenv("QWEATHER_KEY_ID", "")
QWEATHER_PRIVATE_KEY = os.getenv("QWEATHER_PRIVATE_KEY", "")

# Location (longitude,latitude or city ID)
LOCATION = os.getenv("LOCATION", "116.41,39.92")  # Default: Beijing

# 新闻 RSS 配置
NEWS_RSS_DOMESTIC = os.getenv(
    "NEWS_RSS_DOMESTIC",
    "https://rsshub.app/thepaper/newsDetail/25"  # 澎湃新闻-时事
)
NEWS_RSS_INTERNATIONAL = os.getenv(
    "NEWS_RSS_INTERNATIONAL",
    "https://rsshub.app/bbc/world"  # BBC 国际新闻
)

# 新闻条数
NEWS_COUNT_DOMESTIC = int(os.getenv("NEWS_COUNT_DOMESTIC", "4"))
NEWS_COUNT_INTERNATIONAL = int(os.getenv("NEWS_COUNT_INTERNATIONAL", "4"))

# 截图尺寸 (Kindle 4/5 NT)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
