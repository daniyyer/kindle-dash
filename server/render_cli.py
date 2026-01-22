import asyncio
import os
import sys
from pathlib import Path

# 确保导入路径正确
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.weather import get_weather_data
from app.services.news import get_news_data
from app.renderer.template import render_dashboard_html
from app.renderer.screenshot import html_to_grayscale_png
from app.config import LOCATION

async def main():
    print(f"Starting dashboard render for {LOCATION}...")
    
    # 1. 获取数据
    weather = await get_weather_data(LOCATION)
    news = get_news_data()
    
    # 2. 渲染 HTML
    html_content = render_dashboard_html(weather, news)
    
    # 3. 生成灰度 PNG
    png_bytes = await html_to_grayscale_png(html_content)
    
    # 4. 保存到输出目录
    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / "dashboard.png"
    with open(output_path, "wb") as f:
        f.write(png_bytes)
        
    print(f"Successfully rendered dashboard to {output_path}")

if __name__ == "__main__":
    asyncio.run(main())
