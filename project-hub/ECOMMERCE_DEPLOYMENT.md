# 电商平台首次上线（现有腾讯云服务器）

已确认的布局：服务器代码仓库 `/home/ubuntu/one-project`，首页服务目录 `/opt/project-hub`；
Nginx 网站配置 `/etc/nginx/sites-enabled/default`；域名 `https://www.yuganwinfurt.top`。
现有 `/agent/`、`/rag/` 保留，电商新增 `/ecommerce/`。

## 1. Windows：提交并推送源码

电商源码在 `D:\one project\customer-service-system\customer-service-system`。
外层目录已经位于 one-project 工作区中；未跟踪目录需要 `git add` 和提交，不需要 Git merge。
`ai-scaffold` 是同目录下的原始脚手架，不是服务器启动的电商程序。

本次新增代码已加入暂存区。GitHub Desktop 填摘要“上线电商分析平台及更新项目入口”，
提交全部本次改动，然后点击“推送 origin”。真实 `.env`、依赖、数据库和普通上传图片不随 Git 上传。

## 2. Windows：构建上线页面并导出业务数据库

**本次页面资源包和数据库已经生成，可直接上传下面的两个文件，不用重新执行构建和导出。**
下面的命令用于以后代码或数据变更后重新准备上线包：

在 PowerShell 执行：

```powershell
Set-Location 'D:\one project'
powershell.exe -NoProfile -ExecutionPolicy Bypass -File '.\project-hub\deploy\prepare-ecommerce-release.ps1'
& '.\customer-service-system\customer-service-system\backend\.venv\Scripts\python.exe' '.\project-hub\deploy\export-ecommerce-database.py'
```

第一个命令构建首页、RAG 和 `/ecommerce/` 电商前端，打包图片；不会启动或部署服务。
缺少某个前端的依赖时，在提示目录执行 `npm.cmd ci` 再重试。电脑的 Node 版本须符合各项目 `package.json`。
第二个命令自动读取本机电商 `.env`，使用 mysqldump 导出实际正在用的数据库，不显示密码。
导出目标已存在会停止，避免覆盖之前的导出文件。

将这两个文件通过 OrcaTerm 文件面板上传至服务器 `/home/ubuntu/`：

- `D:\one project\release-output\ecommerce-site-assets.tar.gz`
- `D:\one project\release-output\ecommerce-data.sql`

SQL 包含账号密码哈希、订单和地址等应用数据，只私下传到服务器，不提交 Git。
图片已经包含在资源包中。不要上传 Windows `.venv`、`node_modules`，也不要运行 seed 清库脚本。
Git 中旧的 `sql/ecommerce.sql` 是初始化示例，不能代替本次真实数据库导出。

## 3. Ubuntu：拉取源码、解压页面和图片

```bash
cd /home/ubuntu/one-project
git pull --ff-only origin main
```

**仅在拉取成功后继续。** 若提示本地改动、无法快进或会覆盖文件，停止并贴出报错，不使用 reset --hard、clean 或强制覆盖。
现有那几份 `.bak-*` / `.before-*` 文件可以留着，不需要删除。

```bash
cd /home/ubuntu/one-project
tar -xzf /home/ubuntu/ecommerce-site-assets.tar.gz -C /home/ubuntu/one-project
sudo apt-get update
sudo apt-get install -y mysql-server python3-venv
sudo systemctl enable --now mysql
cd customer-service-system/customer-service-system/backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

页面在电脑上已构建，服务器不需要额外安装 Node。
Python 若报不能创建 venv，先确认 `python3` 对应的版本以及该版本的 venv 包；不要删除既有 Agent/RAG 的虚拟环境。

## 4. Ubuntu：首次建库和生成配置

```bash
cd /home/ubuntu/one-project
customer-service-system/customer-service-system/backend/.venv/bin/python project-hub/deploy/init-ecommerce-server.py
```

脚本新建独立 `ecommerce_demo` 数据库并导入上传的 SQL，创建 `ecom_app` 数据库账号和随机密码，
生成电商 `backend/.env`，并与 RAG 的同步密钥保持一致。
它发现已有电商 `.env`、同名数据库或同名数据库账号时会停止；这是首次安装脚本，不用于更新时重复导入。
现有 Agent/RAG 的管理员配置和知识库资料不被替换。

```bash
sudo install -m 644 project-hub/deploy/ecommerce-api.service /etc/systemd/system/ecommerce-api.service
sudo systemctl daemon-reload
sudo systemctl enable --now ecommerce-api
```

电商后端只监听 `127.0.0.1:8001`，并保持单进程。模型请求和待确认任务暂存在进程内，不能简单增加 workers。

## 5. Ubuntu：给现有 HTTPS 网站增加路由

```bash
sudo install -d /etc/nginx/snippets
sudo install -m 644 /home/ubuntu/one-project/project-hub/deploy/ecommerce.nginx.conf /etc/nginx/snippets/ecommerce.conf
sudo nano /etc/nginx/sites-enabled/default
```

在现有 `server_name www.yuganwinfurt.top;` 且有 `listen 443 ...` 的 **server 大括号内**，
加下面一行。不要加到 80 端口重定向的 server 中，也不要覆盖整个站点：

```nginx
include /etc/nginx/snippets/ecommerce.conf;
```

配置将 `/ecommerce/api/` 转到 8001，`/ecommerce/` 提供前端并支持刷新深层页面，
`/uploads/` 提供已有商品图与头像；聊天代理关闭缓冲并允许较长连接。
依据 [Nginx 路径映射文档](https://nginx.org/en/docs/http/ngx_http_core_module.html#try_files)
和[反向代理文档](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_pass)。

按 Ctrl+O、Enter 保存，Ctrl+X 退出，然后：

```bash
sudo nginx -t && sudo systemctl reload nginx
```

只有配置检查成功才会重载。无需在腾讯云放通 8000/8001/8020/8030/3306/11434 公网端口。

## 6. Ubuntu：更新实际运行的首页与关联服务

首页运行的是 `/opt/project-hub` 的版本，仅拉取仓库不会更新这里。

```bash
sudo cp -a /home/ubuntu/one-project/project-hub/dist/. /opt/project-hub/dist/
sudo install -o projecthub -g projecthub -m 644 /home/ubuntu/one-project/project-hub/hub_api.py /opt/project-hub/hub_api.py
sudo chown -R projecthub:projecthub /opt/project-hub/dist
```

RAG 与 Agent 本次有配套源码修改。使用各自现有 Python 更新本次配套包：

```bash
/home/ubuntu/one-project/rag-assistant/backend/.venv/bin/python -m pip install -r /home/ubuntu/one-project/rag-assistant/backend/requirements.txt
/home/ubuntu/one-project/yugan-agent/.venv/bin/python -m pip install --no-deps -e /home/ubuntu/one-project/yugan-agent
sudo systemctl restart yugan-agent rag-assistant project-hub ecommerce-api
```

先等当前问答结束再重启。当前进程中的待确认任务和进行中的模型请求会随重启失效。
首页按 Ctrl+F5 更新，应出现 3 个入口；电商地址为：

`https://www.yuganwinfurt.top/ecommerce/`

## 7. 问答与 RAG

- 进入 `/agent/`，在模型设置选择可用模型；公网访客浏览器中的 `127.0.0.1` 是访客自己的电脑，不是你的电脑。
- 这台服务器约 4 GB 内存，问答可优先使用云端 API；不要沿用本机 `qwen3.5:9b` 并假设服务器也能运行。
- RAG 的向量检索仍需要服务器可用的 embedding 服务。查看 `ollama list`；现有 RAG 使用 `bge-m3` 时，缺少模型再执行 `ollama pull bge-m3`。
- 电商的“语义检索”页面点击“同步后台数据到 RAG”，会在服务器 RAG 建立/更新“电商分析平台”知识库。
- 本次没有把本机整套 RAG storage 覆盖到服务器；服务器原有知识库保留，电商知识库从已迁移的业务库重建。
- 普通数据分析对话使用 Agent 网页选中的模型；“一键巡检”和部分后台功能仍使用电商 `.env` 的 `LLM_*`，要使用时再填写服务器端模型配置。

## 8. 更新演示账号、订单页与项目首页

先在电脑的 GitHub Desktop 提交并推送本次源码改动。
将 `D:\one project\release-output\portfolio-demo-update.tar.gz` 上传到 `/home/ubuntu/`，然后执行：

```bash
bash <<'BASH'
set -e
cd /home/ubuntu/one-project
git pull --ff-only origin main
tar -xzf /home/ubuntu/portfolio-demo-update.tar.gz -C /home/ubuntu/one-project
sudo cp -a project-hub/dist/. /opt/project-hub/dist/
sudo chown -R projecthub:projecthub /opt/project-hub/dist
sudo systemctl restart project-hub ecommerce-api
sudo systemctl status ecommerce-api --no-pager -l
BASH
```

发现拉取冲突会立即停止，保留服务器上的修改，不强制覆盖。
后端启动时自动新建展示凭据表并补齐字段，无需重新导入 SQL 或清理数据。页面按 Ctrl+F5 更新。
运营账号按创建顺序选择最早两个启用账号；删除或停用后补位，新建、改名、改密后同步。
客户注册账号不参与排序；用户登录页展示专用买家 `demo_customer` / `demo123456`，同名已有账号存在时使用后缀。
已有未知口令的后台账号需成功登录一次或重新设密，系统才能保存正确展示口令。

订单页按视口高度调整每页条数、按可用宽度分配列宽，长字段换行，保留日期和物流各段内容。
三个项目介绍分别采用经营看板、任务控制台、资料引用的视觉样式；首页数量标识改为 `SELECTED WORKS / 03`。
该更新包只有首页与电商前端构建产物，后端源码通过上述 Git 拉取更新。

## 出错时贴这些输出

```bash
systemctl status ecommerce-api --no-pager -l
journalctl -u ecommerce-api -n 60 --no-pager
```

不要贴出 `.env` 的完整内容、密码或模型密钥。
