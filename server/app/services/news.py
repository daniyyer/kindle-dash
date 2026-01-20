"""
News RSS Service

Fetch domestic and international news titles from RSS feeds
"""

import httpx
import feedparser
from io import BytesIO
from dataclasses import dataclass
from app.config import (
    NEWS_RSS_DOMESTIC,
    NEWS_RSS_INTERNATIONAL,
    NEWS_COUNT_DOMESTIC,
    NEWS_COUNT_INTERNATIONAL
)


@dataclass
class NewsItem:
    """新闻条目"""
    title: str          # 新闻标题
    link: str           # 链接 (可选展示)


@dataclass
class NewsData:
    """新闻数据"""
    domestic: list[NewsItem]      # 国内新闻
    international: list[NewsItem] # 国际新闻


def truncate_title(title: str, max_length: int = 28) -> str:
    """截断标题，适应 Kindle 显示"""
    if len(title) <= max_length:
        return title
    return title[:max_length - 1] + "…"


def fetch_rss_news(url: str, count: int) -> list[NewsItem]:
    """Fetch news from RSS feed with timeout"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        # Use httpx with timeout to fetch RSS content
        with httpx.Client(timeout=10.0, follow_redirects=True, headers=headers) as client:
            resp = client.get(url)
            feed = feedparser.parse(BytesIO(resp.content))
        
        news_list = []
        
        for entry in feed.entries[:count]:
            title = entry.get("title", "").strip()
            link = entry.get("link", "")
            
            if title:
                news_list.append(NewsItem(
                    title=truncate_title(title),
                    link=link
                ))
        
        return news_list
    except Exception as e:
        print(f"Error fetching RSS from {url}: {e}")
        return []


def get_news_data() -> NewsData:
    """获取所有新闻数据"""
    domestic = fetch_rss_news(NEWS_RSS_DOMESTIC, NEWS_COUNT_DOMESTIC)
    international = fetch_rss_news(NEWS_RSS_INTERNATIONAL, NEWS_COUNT_INTERNATIONAL)
    
    # 如果获取失败，提供默认内容
    if not domestic:
        domestic = [NewsItem(title="暂无国内新闻", link="")]
    if not international:
        international = [NewsItem(title="暂无国际新闻", link="")]
    
    return NewsData(domestic=domestic, international=international)
