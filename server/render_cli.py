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
    
    # 4. 上传到 Cloudflare R2
    # 如果配置了 R2 相关的环境变量，则执行上传
    r2_account_id = os.getenv("R2_ACCOUNT_ID")
    r2_access_key = os.getenv("R2_ACCESS_KEY_ID")
    r2_secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
    r2_bucket_name = os.getenv("R2_BUCKET_NAME", "file")
    
    if all([r2_account_id, r2_access_key, r2_secret_key]):
        import boto3
        from botocore.exceptions import NoCredentialsError

        print(f"Uploading to Cloudflare R2 bucket: {r2_bucket_name}...")
        try:
            s3 = boto3.client(
                's3',
                endpoint_url=f'https://{r2_account_id}.r2.cloudflarestorage.com',
                aws_access_key_id=r2_access_key,
                aws_secret_access_key=r2_secret_key,
            )

            # Upload buffer directly to R2
            # Key "dashboard.png" represents the file name in the bucket
            s3.put_object(
                Bucket=r2_bucket_name,
                Key='dashboard.png',
                Body=png_bytes,
                ContentType='image/png',
                CacheControl='max-age=60' # Tell Cloudflare/Browser to cache for 1 minute
            )
            print("Successfully uploaded dashboard.png to R2!")
        except NoCredentialsError:
            print("Credentials not available for R2 upload.")
        except Exception as e:
            print(f"Failed to upload to R2: {str(e)}")
            # Fallback to local file for debugging if upload fails
            output_dir = Path("./static")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / "dashboard.png"
            with open(output_path, "wb") as f:
                f.write(png_bytes)
            print(f"Saved local fallback to {output_path}")
    else:
        # Fallback for local dev or if env vars missing
        output_dir = Path("./static")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "dashboard.png"
        with open(output_path, "wb") as f:
            f.write(png_bytes)
        print(f"R2 credentials missing. Saved locally to {output_path}")

if __name__ == "__main__":
    asyncio.run(main())
