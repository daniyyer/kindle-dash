# Kindle Dashboard Server

部署在 Render 上的服务器端程序，为 Kindle 4/5 NT 设备提供天气和新闻仪表盘图片。

## 功能

- 获取实时天气、空气质量、风力、未来2小时降水预报
- 获取国内外新闻标题
- 生成 800×600 灰度 PNG 图片供 Kindle 显示

## 快速开始

### 环境变量

```bash
export QWEATHER_API_KEY="your_api_key"
export LOCATION="116.41,39.92"  # 北京坐标
```

### 本地运行

```bash
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload
```

### 测试

```bash
curl http://localhost:8000/dashboard.png -o test.png
```

## API 端点

| 端点 | 说明 |
|------|------|
| `GET /dashboard.png` | 返回仪表盘 PNG 图片 |
| `GET /health` | 健康检查 |

## 部署到 Render

1. Fork 此仓库
2. 在 Render 创建 Web Service
3. 连接仓库，选择 Docker 运行时
4. 设置环境变量 `QWEATHER_API_KEY` 和 `LOCATION`
