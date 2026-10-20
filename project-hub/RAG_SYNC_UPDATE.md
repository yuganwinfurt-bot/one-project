# RAG 同步和项目菜单更新

## 原因

服务器 2026-10-20 16:47:37 的 Nginx 日志显示 `/ecommerce/api/semantic/sync` 等待上游响应超时。Ollama 后续仍在向量化，单批 `/api/embed` 耗时约 57 秒。浏览器里的聊天 API 不负责这一步。

Agent 和 RAG 的菜单保留了电商上线前的判断，公网环境会禁用电商链接。

## 本次修改

- 电商同步提交后台任务，RAG 保存进度和结果，页面使用短请求读取进度。离开页面不会取消同步。
- 正在运行的任务会被复用，避免重复点击同时建立多份索引。RAG 重启后，上次未完成的任务标记为中断，可重新同步。
- 每批默认处理 16 个分片，可通过 RAG 的 `RAG_EMBED_BATCH_SIZE` 调整。任务仍依赖服务器向量模型，CPU 上首次同步可能需要数分钟。
- 两个项目菜单在公网跳转 `/ecommerce/`，本机继续使用 5173 端口。

## 更新服务器

1. 在本机 GitHub Desktop 提交并推送本次全部源码修改，提交说明可用 `修复 RAG 同步超时和项目导航`。仅提交到本机还不够，需要再点“推送 origin”。
2. 本机更新包为 `D:\one project\release-output\rag-sync-navigation-update.tar.gz`。它包含电商和 RAG 的构建页面，Git 不跟踪这两个 dist 目录。重新打包可在 PowerShell 执行：

   ```powershell
   & 'D:\one project\project-hub\deploy\prepare-rag-sync-update.ps1'
   ```

3. 用 OrcaTerm 上传这个新包到服务器 `/home/ubuntu/`，然后执行：

   ```bash
   cd /home/ubuntu/one-project &&
   git pull --ff-only origin main &&
   tar -xzf /home/ubuntu/rag-sync-navigation-update.tar.gz -C /home/ubuntu/one-project &&
   sudo systemctl restart rag-assistant ecommerce-api yugan-agent
   ```

   命令之间的 `&&` 表示前一步成功才继续；拉取出现冲突时停在该步骤，贴出错误后处理。

4. 等服务启动后，在电商、RAG 和 Agent 页面分别按 `Ctrl+F5`。点击一次“同步后台数据到 RAG”，页面会显示分片进度。服务启动情况可查看：

   ```bash
   systemctl is-active rag-assistant ecommerce-api yugan-agent
   ```

这次不需要重新导入 MySQL、上传旧数据包或修改 Nginx。RAG 启动时会自动创建同步任务表。部署保持现有单进程 RAG 服务；任务队列和锁由该进程管理。
