# 架构说明

```text
input mapping
    │ copy
    ▼
CompiledGraph.stream
    │ select edge
    ▼
node(old state) ──returns──> partial update
    │ merge into copied state
    ▼
Step(index, node, update, state)
    │
    └── next static edge ──> END or next node
```

## 五个责任点

- **请求入口**：`CompiledGraph.invoke()` 或 `stream()`。
- **权威状态**：运行器内部的 `state` 字典；节点只得到副本。
- **下一步决策者**：编译后的静态 `edges` 映射，不是节点或模型。
- **副作用位置**：本版设计要求节点为纯函数；运行时不执行外部副作用。
- **完成证据**：执行到 `END`，并返回最终状态或完整 Step 轨迹。

## 错误与恢复

- 非法图在 `compile()` 中失败，不进入执行。
- 环路超过 `max_steps` 时抛出 `GraphError`。
- 本版没有 checkpoint，失败后只能从初始状态重新运行。
