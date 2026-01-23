# Kindle Dashboard - Trigger.dev 定时任务

本目录是定时刷新 Kindle Dashboard 的 Trigger.dev 项目。

## 设置步骤

1. 安装依赖:
   ```bash
   npm install
   ```

2. 配置环境变量:
   创建 `.env` 文件并添加 `TRIGGER_SECRET_KEY`

3. 开发模式:
   ```bash
   npx trigger.dev@latest dev
   ```

4. 部署:
   ```bash
   npx trigger.dev@latest deploy
   ```
