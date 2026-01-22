"""
Playwright 截图服务

将 HTML 渲染成灰度 PNG 图片（无透明通道），适用于 Kindle eips 显示
"""

import asyncio
from io import BytesIO
from PIL import Image
from playwright.async_api import async_playwright
from app.config import SCREEN_WIDTH, SCREEN_HEIGHT


async def html_to_grayscale_png(html_content: str) -> bytes:
    """
    将 HTML 内容转换为灰度 PNG 图片
    
    Args:
        html_content: HTML 字符串
        
    Returns:
        PNG 图片的字节数据（8位灰度，无透明通道）
    """
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": SCREEN_WIDTH, "height": SCREEN_HEIGHT}
        )
        
        # 设置 HTML 内容
        await page.set_content(html_content, wait_until="networkidle")
        
        # 等待字体加载
        await page.wait_for_timeout(500)
        
        # 截图
        screenshot_bytes = await page.screenshot(
            type="png",
            full_page=False
        )
        
        await browser.close()
    
    # 将截图转换为灰度图
    img = Image.open(BytesIO(screenshot_bytes))
    
    # 转换为灰度模式 (L = 8-bit grayscale)
    grayscale_img = img.convert("L")
    
    # 增强对比度 (让黑更黑，白更白，减少中间灰色)
    from PIL import ImageEnhance
    enhancer = ImageEnhance.Contrast(grayscale_img)
    grayscale_img = enhancer.enhance(1.2)  # 提升 20% 对比度
    
    # 将 256 级灰度压缩至 16 级 (4-bit), 匹配 Kindle 硬件
    # 映射公式：(x // 16) * 17 确保 0->0, 255->255，且只有 16 个阶梯
    grayscale_img = grayscale_img.point(lambda x: (x // 16) * 17)
    
    # 保存到字节流
    output = BytesIO()
    grayscale_img.save(output, format="PNG", optimize=True)
    output.seek(0)
    
    return output.getvalue()


def sync_html_to_grayscale_png(html_content: str) -> bytes:
    """同步版本的 HTML 转灰度 PNG"""
    return asyncio.run(html_to_grayscale_png(html_content))
