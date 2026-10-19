# 知答 · 本地 RAG 知识库助手

用 Vue 3、Vite、FastAPI、Python、SQLite，以及 LangChain 和 LangGraph，做成可本地运行的多知识库问答应用。前端由 Vue 3 渲染，使用 JavaScript/JSX 编写界面；后端是 Python。无需额外数据库服务。

## 功能

- 每个知识库独立保存 PDF、DOCX、TXT、Markdown、CSV 文档。
- 一个项目可以组合多个知识库；默认“嵌入式项目”已经关联 STM32F103、机械臂和 MQTT 三个知识库。
- 每个项目可以创建多段独立对话；历史消息保存在 SQLite，对话可以单独调整检索范围。
- LangChain 负责加载文档、递归切块、Ollama 向量化、Chroma 持久化和相似度检索；LangGraph `StateGraph` 负责“检索 → 回答”流程。
- 回答支持流式显示和来源片段；低于相关度阈值的片段会被过滤，没有足够相关资料时会明确提示。
- 多轮追问会先改写成独立检索问题；回答流异常中断会显示错误并保留已收到的内容。
- 新对话默认每轮自动检索项目关联的全部知识库；单段对话也能改成自定义范围。
- 可拖入或选择多个文件，确认目标知识库后逐份上传、分片和建索引，失败项可以单独重试。
- 可打开文档查看完整分片并删除指定片段；删除后新问题不再检索该片段，原文件和已有历史回答保留。
- 游客可查看和检索已有资料、选择 RAG 范围及管理自己的对话；新增知识库、上传或删除资料与分片仅管理员可用。
- 管理员登录配置保存在两个后端的 `.env`；Agent 与 RAG 使用相同账号、密码哈希和签名密钥时共享登录状态。
- 上传文件、SQLite 数据和 Chroma 索引保存在 RAG 后端的 `backend/storage/`。部署到服务器后，这些资料由服务器存储和检索。
- Agent 控制台可按项目或手动选择知识库，通过本机只读接口 `/api/integrations/agent/retrieve` 获取相关片段；该接口只检索，不生成回答或修改资料。
- 电商分析平台会把商品描述和买家评价同步到独立知识库“电商商品与评价”；电商语义检索和 Agent 问答共用这份索引。同步接口仅接受本机请求，并校验 `ECOM_RAG_SYNC_TOKEN`。
- RAG 回答直接使用 Agent 当前浏览器中启用的模型；在 Agent 模型设置保存后，从 RAG 左下角连接模型。模型配置和 API Key 保存在用户浏览器的 `localStorage`，浏览器直接请求模型服务，RAG/Agent 后端不接收或保存 API Key。

### PDF 分片和图片说明

- 有些 CAD/打印机导出的 PDF 没有正确写入字体的 Unicode 映射。`backend/app/rag/pipeline.py` 会在这种情况下尝试把错误解码的 GBK/GB18030 文本修复后再分片；已经导入过的旧文件需要重新导入，或在后端重新索引，旧分片不会自动改变。
- PDF 会逐页检查文字量；遇到文字层很少的页面会尝试 RapidOCR，把扫描页的文字转成可检索文本。已导入的旧文档需要重新导入，才会使用新的逐页提取逻辑。
- 当前向量库保存的是“文字分片”和来源页码。PDF 里的原始图片、矢量电路图和页面排版不会直接出现在分片窗口里，也不会自动变成图片向量；因此图纸上的空间关系、纯图片文字仍需要单独的页面预览或多模态检索功能。
- DOCX 当前使用文字提取器，嵌入的截图不会进入文本分片；图片很多但文字很少的 DOCX 可能只有一个文本分片。Ollama 向量接口偶发返回 502/503 时，导入器会自动重试三次。

## 启动

环境需要 Python 3.10+、Node.js/npm 和 Ollama。Windows 启动器使用 `D:\Python\python.exe` 创建项目内虚拟环境。不会往全局 Python 安装项目依赖。

1. 第一次使用时在 PowerShell 下载模型：

   ```powershell
   ollama pull qwen3.5:9b
   ollama pull bge-m3
   ```

   启动器检测到 `D:\Ollama\ollama.exe` 时会自动启动 Ollama；如果你的 Ollama 安装在其他位置，请先手动运行 `ollama serve`。

   如果已经有其他聊天模型，在 `backend/.env` 设置 `OLLAMA_CHAT_MODEL`。建库和提问要使用同一个 embedding 模型。

2. 双击 `启动知识库.bat`。首次启动会自动创建 `.venv` 并安装 Python、npm 依赖，随后打开浏览器。

3. 如果需要手动启动，分别在两个终端运行：

   ```powershell
   cd "D:\one project\rag-assistant\backend"
   .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

   ```powershell
   cd "D:\one project\rag-assistant\frontend"
   npm run dev
   ```

网页：<http://127.0.0.1:4173>　API 文档：<http://127.0.0.1:8000/docs>

游客默认进入只读管理模式。管理员账号由 Agent 和 RAG 后端 `.env` 中的 `YUGAN_ADMIN_USERNAME`、`YUGAN_ADMIN_PASSWORD_HASH`、`YUGAN_AUTH_SIGNING_SECRET` 配置；两端取值应一致。上线时将 `RAG_WEB_ORIGINS` 改为实际前端 Origin，并通过同一站点或反向代理提供前后端。

## 开始使用

1. 选择左侧“嵌入式项目”。
2. 管理员可把 PDF、DOCX、TXT、Markdown 或 CSV 拖到网页，或者点“添加资料”，再选择目标知识库并开始导入。游客没有资料管理权限。
3. 游客可读取已有知识库并开始对话；回答时，浏览器使用从 Agent 连接的当前模型。API Key 只发往模型服务。资料导入及向量检索由 RAG 后端运行，需要后端能够访问 Ollama 的 embedding 模型 `bge-m3`。
4. 游客只能查看文件和分片；管理员可上传文件、删除文件或指定分片。删除后该资料不再参与新问题；历史回答仍保留原记录。
5. 点顶部“自动检索”可让这段对话跟随项目，也可勾选知识库设置仅对当前对话生效的范围。创建其他项目时，在项目设置里组合对应知识库；不同项目和不同对话各自保存历史。

## 配置和文件位置

复制配置模板：

```powershell
Copy-Item "D:\one project\rag-assistant\backend\.env.example" "D:\one project\rag-assistant\backend\.env"
```

- `OLLAMA_BASE_URL`：默认 `http://127.0.0.1:11434`
- `OLLAMA_CHAT_MODEL`：默认 `qwen3.5:9b`
- `OLLAMA_EMBED_MODEL`：默认 `bge-m3`
- `RAG_TOP_K`：每个知识库的候选片段数，默认 4
- `RAG_MIN_RELEVANCE`：最低相关度，默认 0.25；这是初始值，应运行下面的评测再按资料调整
- `ECOM_RAG_SYNC_TOKEN`：电商后端与本机 RAG 共享的同步密钥，必须与电商 `.env` 中的 `RAG_SYNC_TOKEN` 一致
- `MAX_UPLOAD_MB`：单文件最大大小，默认 30 MB
- `backend/storage/assistant.sqlite3`：项目、知识库、对话、消息记录
- `backend/storage/uploads/`：导入的原始文档
- `backend/storage/vectors/`：Chroma 向量集合

删除文件时会同时删掉对应的向量片段；单独删除分片不会删除原始文件。更换 embedding 模型后，需要清掉并重新导入旧索引。API Key 不进入上述数据库或上传目录。

## 检索评测

先确保 Ollama 与 `bge-m3` 正常运行，再在项目根目录执行：

```powershell
cd "D:\one project\rag-assistant"
.\backend\.venv\Scripts\python.exe .\eval\run_retrieval.py
```

`eval/retrieval_cases.json` 中的 4 条资料定位题来自人工抽查记录，另有 2 条应拒绝的库外问题。脚本输出每题是否找到了指定文件或正确拒绝、检索分数、耗时和分类通过率；模型服务出错时不计算通过率。扩充测试集时，请先人工核对预期文件，再添加新的题目。

## 主要代码

- `backend/app/main.py`：FastAPI 接口、上传、持久对话、SSE 流式返回
- `backend/app/database.py`：SQLite 表和默认项目/知识库
- `backend/app/rag/pipeline.py`：文档加载、切块、Chroma 入库和多库检索
- `backend/app/rag/graph.py`：LangGraph 检索与回答节点
- `frontend/src/App.vue.jsx`：Vue 3 界面与项目、对话、文件交互
- `frontend/src/vue-state.js`：Vue 响应式状态与生命周期适配
- `frontend/src/api.js`：FastAPI 请求封装
- `frontend/src/styles.css`：页面样式

## 课程技术对应

课程 PDF 第 60–83 页介绍 PDF/Word/CSV/TXT 加载器、文本切块、Chroma、Top‑K 检索和来源；本项目沿用这些概念。前端按当前要求改为 Vue 3，仍使用 Vite/npm 与 FastAPI 联调。旧课件代码和新版 LangChain 接口有差异，所以本项目直接使用 `StateGraph`、`ChatOllama`、`OllamaEmbeddings` 等当前 API。

- [LangChain Python 文档](https://docs.langchain.com/oss/python/langchain/overview)
- [LangGraph Python 文档](https://docs.langchain.com/oss/python/langgraph/overview)
- [Ollama 聊天模型和向量模型](https://docs.langchain.com/oss/python/integrations/chat/ollama)
- [Chroma 持久化](https://docs.trychroma.com/docs/run-chroma/clients)
- [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/)
