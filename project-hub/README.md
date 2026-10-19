# 个人练习 · 电商分析 × Agent × RAG 项目实验室

Vue 3 首页展示电商数据分析、Agent 和 RAG 项目。在本机打开 <http://127.0.0.1:8030/> 后，电商分析入口进入 <http://127.0.0.1:5173/>，Agent 和 RAG 入口分别进入 <http://127.0.0.1:8020/> 和 <http://127.0.0.1:4173/>。页头显示当前游客/管理员身份，并提供管理员登录；身份请求由首页后端转发到本机 Agent，浏览器不直接访问 Agent API。公网首页不提供指向访客本机 `127.0.0.1` 的操作链接，也不公开 Agent 的管理接口。

## 增加新项目

编辑 [`src/projects.js`](src/projects.js)，在 `projects` 数组末尾加一个对象。主页的项目数量、介绍卡片和右侧入口都会自动更新。例如：

```js
{
  id: 'new-project',               // 不要和已有 id 重复
  name: '新项目',
  shortName: '新项目',
  mark: 'N',                        // 卡片上的单字标识
  category: '项目类型',
  description: '一句话介绍项目功能。',
  introLabel: 'NEW PROJECT 使用介绍',
  introTitle: '一句话，',
  introAccent: '说明价值。',
  intro: '在介绍大图中说明这个项目怎样使用。',
  tags: ['功能一', '功能二'],
  features: [
    { name: '功能一', detail: '具体说明用途。' },
    { name: '功能二', detail: '具体说明用途。' },
  ],
  note: '使用限制或需要留意的条件。',
  caption: '主要能力 · 使用场景',
  tone: 'paper',                    // navy、mint 或 paper；不填也会自动轮换
  localUrl: 'http://127.0.0.1:8040/',
  publicUrl: '',                   // 项目安全上线后再填写真正的公网地址
  action: '打开新项目',
},
```

保存后在 `D:\one project\project-hub` 执行 `npm run build`，刷新首页即可看到新卡片。`localUrl` 只在本机预览时生成链接；`publicUrl` 留空时公网只展示介绍，不会把访客导向其自己的电脑。首页不要加入姓名、手机号、邮箱等个人信息；Agent 管理后台也不要直接填写为 `publicUrl`。

## 一次启动本机后端和主页

直接双击项目总目录的 [启动本地项目.bat](../启动本地项目.bat)。这个双击入口只负责调用同目录的 [start_local_projects.py](../start_local_projects.py)；实际启动逻辑仍由 Python 实现。也可在 PowerShell 中运行：

```powershell
& 'D:\one project\yugan-agent\.venv\Scripts\python.exe' 'D:\one project\start_local_projects.py'
```

脚本依次检查 Ollama、RAG 后端 `127.0.0.1:8000`、RAG 页面 `127.0.0.1:4173`、yugan-agent 控制台 `127.0.0.1:8020`、电商分析后端 `127.0.0.1:8001`、电商分析前端 `127.0.0.1:5173` 和主页网关 `127.0.0.1:8030`；已经运行的服务会跳过。电商源码会先在 `D:\one project\customer-service-system` 下查找（含其子目录），找不到时使用桌面上的源码目录。浏览器会打开 <http://127.0.0.1:8030/>。日志保存在 `data/local-launcher/`，不会提交到仓库。

停止由这个脚本启动的进程：

```powershell
& 'D:\one project\yugan-agent\.venv\Scripts\python.exe' 'D:\one project\start_local_projects.py' stop
```

只检查文件是否齐全，不启动服务：把末尾的 `stop` 改为 `check`。此脚本用于**本机预览**，不会部署到云服务器，也不会把 8020 管理控制台公开到互联网。

## 本地看首页

在 PowerShell 中运行：

```powershell
cd 'D:\one project\project-hub'
npm run build
& 'D:\one project\yugan-agent\.venv\Scripts\python.exe' -m uvicorn hub_api:app --host 127.0.0.1 --port 8030
```

打开 <http://127.0.0.1:8030/>。开发前端时运行 `npm run dev`，访问 Vite 输出的网址；Vite 会把 `/api` 代理到 8030 端口。

首次安装首页前端依赖：在 `project-hub` 目录运行 `npm install`。若双击启动时提示缺少 RAG 的 `vite.js`，在 `D:\one project\rag-assistant\frontend` 目录再运行一次 `npm install`。本机因为 npm 镜像 DNS 暂不可用，当前首页 `node_modules` 使用已有 Vue 项目的依赖复制来完成构建；部署到服务器时重新执行 `npm install`。

## Linux 部署包

电商平台接入现有服务器的步骤见 [电商平台上线操作单](ECOMMERCE_DEPLOYMENT.md)，包含源码提交、页面和图片打包、MySQL 迁移及 `/ecommerce/` 路由配置。

本地已生成 `project-hub-release.zip`，包含构建后的 Vue 项目页、静态页面网关及 [Nginx](deploy/nginx.example.conf)、[systemd](deploy/project-hub.service.example) 模板。公开部署前，在项目首页服务环境中设置 `PROJECT_HUB_AGENT_API_URL=http://127.0.0.1:8020`，并在服务器本机启动 Agent；首页只代理身份状态、登录和退出，其他 Agent/RAG API 仍不对公网开放。Agent 与 RAG 的管理员签名配置必须一致。当前 4 GB 云服务器已运行 Hermes Agent，先用 [只读检查脚本](deploy/inspect-server.sh)核对已有站点和端口，再人工核对证书路径，避免覆盖原应用。部署细节见 [上线核对单](DEPLOYMENT.md)。

## 上线与备案

请按 [上线核对单](DEPLOYMENT.md)检查域名、HTTPS、备案、访问控制和实际服务内容。公安备案号及跳转 ID **取得后**，在构建前分别设置 `VITE_PSB_RECORD_NUMBER` 和 `VITE_PSB_RECORD_ID`，再执行 `npm run build`；缺少其中任一项时页面不会显示公安备案号。收到公安备案平台提供的页脚展示代码与图标后，还需核对并按要求使用。ICP备案号已经按提交的 PDF 写在首页页脚。
