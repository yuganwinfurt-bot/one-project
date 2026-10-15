# 参与开发

1. 使用 Python 3.11+ 和独立虚拟环境安装 `.[dev]`。
2. 新功能放在 `src/yugan_agent/`；原上游代码在 `cai-agent/`，修改它时运行对应测试。
3. 新工具说明输入、输出、副作用和失败行为；敏感工具默认禁用。
4. 运行 `pytest -q tests`、`ruff check src/yugan_agent tests examples` 和 `ruff format --check src/yugan_agent tests examples`。
5. 不提交 `.env`、API Key、SQLite 数据库、日志或设备真实数据。
6. PR 描述中写明用户可见行为、测试结果以及是否调用真实模型或硬件。
