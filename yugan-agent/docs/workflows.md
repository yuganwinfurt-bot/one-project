# JSON 工作流

```powershell
.\.venv\Scripts\python.exe -m yugan_agent workflow demo
.\.venv\Scripts\python.exe -m yugan_agent workflow demo --graph
```

内置定义位于 `src/yugan_agent/data/greenhouse.json`。最小示例：

```json
{
  "name": "温度判断", "start": "check", "max_steps": 5,
  "initial_state": {"temperature": 31},
  "nodes": [
    {"id": "check", "kind": "condition", "left": {"$ref": "temperature"}, "op": "gt", "right": 30, "then": "hot", "otherwise": "normal"},
    {"id": "hot", "kind": "set", "values": {"message": "建议检查通风"}, "next": null},
    {"id": "normal", "kind": "set", "values": {"message": "继续观察"}, "next": null}
  ]
}
```

节点类型：`tool`、`set`、`condition`、`agent`。`{"$ref":"key.nested"}` 读取状态；`{"$add":[左,右]}` 加两个数。条件比较支持 `eq/ne/gt/ge/lt/le/contains`。工作流 JSON 不执行 Python 代码。

循环通过节点跳转实现，`max_steps` 限制最多执行次数。结果包含最终状态、逐步轨迹与错误，状态为 `completed`、`limited` 或 `error`。
