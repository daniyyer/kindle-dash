"""
Kindle Dashboard Server

FastAPI 主入口，提供仪表盘图片生成服务
"""

import logging
import os
from pathlib import Path

from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.services.weather import get_weather_data

logger = logging.getLogger(__name__)
from app.services.news import get_news_data
from app.renderer.template import render_dashboard_html
from app.renderer.screenshot import html_to_grayscale_png
from app.config import LOCATION

app = FastAPI(
    title="Kindle Dashboard Server",
    description="为 Kindle 设备生成天气和新闻仪表盘图片",
    version="1.0.0"
)

# 确保静态目录存在
STATIC_DIR = Path(__file__).parent.parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok"}


@app.get("/dashboard.png")
async def get_dashboard_image():
    """
    生成仪表盘 PNG 图片
    
    返回 800x600 灰度 PNG 图片，适用于 Kindle eips 显示
    """
    try:
        # 1. 获取天气数据
        weather = await get_weather_data(LOCATION)
        
        # 2. 获取新闻数据
        news = get_news_data()
        
        # 3. 渲染 HTML
        html_content = render_dashboard_html(weather, news)
        
        # 4. 生成灰度 PNG 截图
        png_bytes = await html_to_grayscale_png(html_content)
        
        # 5. 保存到静态目录供调试
        try:
            with open(STATIC_DIR / "dashboard.png", "wb") as f:
                f.write(png_bytes)
        except Exception as e:
            logger.error(f"Failed to save static dashboard image: {e}")
            
        return Response(
            content=png_bytes,
            media_type="image/png",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/preview")
async def preview_dashboard():
    """
    预览仪表盘 HTML（调试用）
    
    返回渲染后的 HTML 页面，可在浏览器中查看
    """
    try:
        weather = await get_weather_data(LOCATION)
        news = get_news_data()
        html_content = render_dashboard_html(weather, news)
        
        return Response(
            content=html_content,
            media_type="text/html"
        )
    except Exception as e:
        logger.exception("Preview endpoint error")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )



