# 电商数据同步提速

## 本次调整

原实现只在整份 CSV 完全相同时跳过计算；任何一条数据变化都会重新计算整份快照。截图中的 795 条记录对应 934 个分片，包括 510 条历史运行步骤。

新版保留全部原有资料范围、脱敏规则和 bge-m3，改为按分片正文摘要复用向量：

- 优先从上次已登记的电商快照读取已有向量，升级后的第一次增量同步也可复用它们。
- 新增、修改的正文才调用向量模型。删除的记录通过提交新快照、删除旧快照的索引反映。
- 每批计算完成后缓存向量；后续批次失败时，重试仍可复用已经计算的批次。
- 缓存按模型名称和 Ollama 模型 digest 隔离。旧快照只支持自动迁移本项目原有 bge-m3 的 1024 维向量；模型改变时不会混用缓存。
- 新快照索引写好并登记后再清理旧快照，其他知识库和手动导入的不同文件保留。
- 页面显示新增、更新、删除、未变化的记录数，以及复用分片和新计算向量数。

这里优化的是重复同步。没有现成向量的首次全量导入仍需计算全部分片；若历史快照的分片被删除或原文变化，相应部分也需要重新计算。不承诺固定耗时或提速倍数。

记录的 `update_time` 仍作为业务资料保留；它变化时只影响相应记录。导出摘要里的 `snapshot_at` 没有写入快照正文，不会使所有分片失效。

## 本机打包

```powershell
& 'D:\one project\project-hub\deploy\prepare-rag-incremental-update.ps1'
```

输出：`D:\one project\release-output\rag-incremental-sync-update.tar.gz`。

## 更新服务器

1. 在 GitHub Desktop 提交本次全部源码修改，并推送 origin。可用提交说明：`电商 RAG 增量同步与向量缓存`。
2. 上传这个新包到服务器 `/home/ubuntu/one-project/`。
3. 执行：

   ```bash
   cd /home/ubuntu/one-project &&
   git pull --ff-only origin main &&
   python3 project-hub/deploy/apply-rag-incremental-update.py /home/ubuntu/one-project/rag-incremental-sync-update.tar.gz &&
   sudo systemctl restart rag-assistant ecommerce-api
   ```

   校验脚本会在解压页面前比较源码摘要。若未推送、未拉到源码或包和源码不是同一版，会停止并指出文件。Git 拉取发生冲突时也会停止，先处理报错。

4. 服务启动后，电商页按 `Ctrl+F5`，点击一次同步。完成后查看“复用”和“新计算”的数量。没有数据变化时，新计算应为 0；有新增运行、消息、订单等记录时，对应的新内容仍需计算。

RAG 启动时自动创建缓存表、增加进度和模型标记字段，使用现有 Python 依赖。数据库和 .env 不在页面包内。
