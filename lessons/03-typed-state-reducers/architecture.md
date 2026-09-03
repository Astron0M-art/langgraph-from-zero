# 架构说明

```text
TypedDict + Annotated reducer
          │ inspect once
          ▼
      StateSpec
          │
initial ──┼── validate keys / required fields / values
          │
updates ──┴── group by key
                    │
          ┌─────────┴──────────┐
          ▼                    ▼
   one plain value      one or more reducer values
      overwrite         fold(current, update...)
          │                    │
          └─────────┬──────────┘
                    ▼
             validate result
                    ▼
        authoritative copied state
```

## 责任边界

- **请求入口**：`invoke()`、`stream()`；`merge_updates()` 只用于隔离验证合并规则。
- **权威状态**：运行器内部复制的 `state`，不修改调用者输入。
- **更新契约**：`StateSpec` 解析 schema，决定字段是否合法、是否必填以及是否拥有 reducer。
- **调度者**：仍是 `CompiledGraph` 的顺序循环和条件边；Reducer 不决定下一步。
- **副作用**：本版继续排除，节点和 Reducer 都必须是确定性纯函数；Reducer 返回新值，不原地修改输入。
- **完成证据**：Step 中的合并后状态、显式 `END`、fixture trace 和冲突断言。

## 单更新与批量更新共用语义

正常节点执行产生一个 update，运行器调用 `merge(state, [update])`。教学接口把多个 update 作为一个有序 batch 传给同一函数。这样可以在实现 superstep 之前先回答：哪些 key 可以聚合，哪些多写必须失败。

## 错误与恢复

- 未知 key、缺少必填 key、普通 key 多写、错误结果类型：抛出 `GraphError`。
- Reducer 抛出的异常会保留为 cause，并在状态 key 边界包装为 `GraphError`。
- 合并采用 copy-on-write；失败时调用者传入的 state 不变。
- 本版仍无 checkpoint，修复 schema、Reducer 或 update 后只能从初始状态重跑。

## 关键不变量

- 普通 key 在一个 batch 中最多收到一个值。
- Reducer 签名必须是 `(current, update) -> value`。
- Reducer 输出必须符合字段声明的 state value type。
- 路由看到的是 Reducer 已经合并完成的状态。
