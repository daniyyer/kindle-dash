import os
from dotenv import load_dotenv

load_dotenv()

# 和风天气 API 配置
QWEATHER_API_KEY = os.getenv("QWEATHER_API_KEY", "")
QWEATHER_BASE_URL = "https://devapi.qweather.com/v7"

# 位置配置 (经度,纬度 或 城市ID)
LOCATION = os.getenv("LOCATION", "116.41,39.92")  # 默认北京

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
