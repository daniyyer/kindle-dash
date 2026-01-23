import { schedules } from "@trigger.dev/sdk/v3";

// Kindle Dashboard 刷新任务
// 每 30 分钟调用一次 Render 服务生成新的仪表盘图片
export const refreshDashboard = schedules.task({
    id: "refresh-kindle-dashboard",
    // 每 30 分钟运行一次
    cron: {
        pattern: "*/30 * * * *",
        timezone: "Asia/Shanghai",
    },
    // 使用最小规格的机器以节省费用
    machine: {
        preset: "micro",
    },
    run: async (payload) => {
        const dashboardUrl = process.env.DASHBOARD_URL || "https://kindle-dash-server.onrender.com/dashboard";

        console.log(`[${payload.timestamp.toISOString()}] Refreshing dashboard from: ${dashboardUrl}`);

        const startTime = Date.now();

        try {
            const response = await fetch(dashboardUrl, {
                method: "GET",
                headers: {
                    "User-Agent": "KindleDash-Trigger/1.0",
                },
            });

            const duration = Date.now() - startTime;

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            // 验证返回的是图片
            const contentType = response.headers.get("content-type");
            if (!contentType?.includes("image/png")) {
                throw new Error(`Unexpected content type: ${contentType}`);
            }

            const contentLength = response.headers.get("content-length");

            console.log(`✅ Dashboard refreshed successfully`);
            console.log(`   - Duration: ${duration}ms`);
            console.log(`   - Image size: ${contentLength} bytes`);
            console.log(`   - Next run: ${payload.upcoming[0]?.toISOString()}`);

            return {
                status: "success",
                duration,
                imageSize: contentLength ? parseInt(contentLength) : null,
                timestamp: payload.timestamp.toISOString(),
            };
        } catch (error) {
            const duration = Date.now() - startTime;
            console.error(`❌ Failed to refresh dashboard after ${duration}ms:`, error);

            // 抛出错误让 Trigger.dev 记录失败
            throw error;
        }
    },
});
