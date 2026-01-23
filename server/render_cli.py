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
from app.services.r2_storage import upload_dashboard_image, is_r2_configured
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

    # 4. 始终保存到本地 ./static/dashboard.png
    output_dir = Path("./static")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "dashboard.png"
    try:
        with open(output_path, "wb") as f:
            f.write(png_bytes)
        print(f"Saved local copy to {output_path}")
    except Exception as e:
        print(f"Failed to save local copy: {str(e)}")

    # 5. 上传到 Cloudflare R2 (如果配置了)
    if is_r2_configured():
        print("Uploading to Cloudflare R2...")
        if upload_dashboard_image(png_bytes):
            print("Successfully uploaded dashboard.png to R2!")
        else:
            print("Failed to upload to R2.")
    else:
        print("R2 credentials not set, skipping upload.")

if __name__ == "__main__":
    asyncio.run(main())

