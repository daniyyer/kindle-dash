import { defineConfig } from "@trigger.dev/sdk/v3";

export default defineConfig({
    project: "proj_gocjbqexkdxxzqlcsvpi",
    runtime: "node",
    logLevel: "log",
    maxDuration: 300, // 增加到 300 秒以应对 Render 免费档的冷启动时间
    dirs: ["./src/trigger"],
});
