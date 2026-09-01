# LangGraph Source Map

固定上游：LangGraph `1.2.11`，commit
`644815f9e5bc52ad8f7a5227a456227e9c3e639b`。

| 概念 | 上游位置 | 本版处理 |
|---|---|---|
| 图构建器 | `libs/langgraph/langgraph/graph/state.py` 的 `StateGraph` | 保留 add node/edge/compile 三步 |
| 编译结果 | 同文件的 `CompiledStateGraph` | 简化为只支持普通单出边 |
| 执行入口 | `libs/langgraph/langgraph/pregel/main.py` 的 Pregel 接口 | 只保留同步 `invoke`/`stream` |
| 运行循环 | `libs/langgraph/langgraph/pregel/_loop.py` 的 `PregelLoop` | 用顺序循环代替 superstep runtime |
| 结束哨兵 | `langgraph.constants` 与图 API | 使用课程自己的 `START`/`END` 字符串 |

## 上游事实

- LangGraph 使用图构建与编译分离的公共形态。
- 编译图最终由 Pregel 风格运行时驱动，而不是简单遍历节点列表。
- 正式实现包含 channel、checkpoint、interrupt、stream、retry 等本版没有的语义。

## 教学简化

- 不兼容 LangGraph API，不导入任何 LangGraph 包。
- 不实现 Pregel superstep、conditional edge、schema 或异步执行。
- 编译检查只覆盖进入本版运行循环所需的最小不变量。

## 我们的设计

- 节点始终收到状态副本，输入 mapping 不被修改。
- `Step` 同时暴露局部 update 和合并后的 state，便于教学断言。
- 即使图结构合法，也用 `max_steps` 守住运行时活性边界。

这些设计不能用来推断 LangGraph 的完整并发、持久化或恢复语义。
