# 作品集首页

Vue 3 首页展示本仓库的电商、客服、Agent 和 RAG 入口。[线上首页](https://www.yuganwinfurt.top/) · [项目总览](../README.md)

页面入口和说明定义在 [src/projects.js](src/projects.js)。[hub_api.py](hub_api.py) 提供健康检查、静态页回退和身份代理。首页后端通过 `PROJECT_HUB_AGENT_API_URL` 转发身份状态、登录和退出。

从仓库根目录按[首页启动步骤](../docs/LOCAL_DEVELOPMENT.md#作品集首页)运行。前端开发时运行 `npm run dev`，Vite 将 `/api` 转发到 `127.0.0.1:8030`。`npm run build:shared-ui` 会生成供 RAG 与 Agent 页面复用的知识说明组件，并写入两个应用的静态目录。

上线资料在[部署核对单](DEPLOYMENT.md)、[电商部署记录](ECOMMERCE_DEPLOYMENT.md)和 [deploy/](deploy/) 中。部署记录里的电商嵌套路径属于旧布局，实际源码路径及容器差异见[审查报告](../docs/CODE_QUALITY_REPORT.md)。
