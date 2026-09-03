# LangGraph Source Map

固定上游：LangGraph `1.2.11`，commit
`644815f9e5bc52ad8f7a5227a456227e9c3e639b`。本版没有移动基线；所有路径与行号仅对该 commit 有效。

| 概念 | 固定上游位置 | 本版处理 |
|---|---|---|
| State schema 与 Reducer 契约 | `libs/langgraph/langgraph/graph/state.py:131-215` 的 `StateGraph` 文档 | 保留 `State -> Partial<State>` 与二元 Reducer 形态 |
| Schema 注册 | `state.py:216-271` 的 `StateGraph.__init__`、`state.py:343-370` 的 `_add_schema` | 只解析一个 TypedDict 风格 state schema |
| 字段到 Channel | `state.py:1815-1869` 的 `_get_channels`、`_get_channel` | 简化为课程 `_StateSpec` 字段表 |
| Annotated Reducer 识别 | `state.py:1904-1924` 的 `_is_field_binop` | 读取最后一个 callable 元数据并检查二元签名 |
| 普通字段语义 | `libs/langgraph/langgraph/channels/last_value.py:20-67` 的 `LastValue.update` | 同批多个值直接冲突 |
| Reducer 聚合 | `libs/langgraph/langgraph/channels/binop.py:65-145` 的 `BinaryOperatorAggregate` | 按调用者提供的 update 顺序折叠 |
| Channel 单元测试 | `libs/langgraph/tests/test_channels.py:34-43`、`:95-104` | 对照单值冲突与二元累积 |
| 图级冲突测试 | `libs/langgraph/tests/test_pregel.py:117-137`、`:775-800` | 用离线 update batch 复现多写冲突，不实现并发 |
| Reducer 路由状态 | `libs/langgraph/tests/test_state.py:275-308` | 路由读取 Reducer 合并后的值 |

## 上游事实

- 固定上游 `StateGraph` 要求 state schema；节点契约是读取 State、返回 Partial State。
- 字段可以通过 `Annotated` 声明二元 Reducer；解析逻辑要求 callable 接受两个位置参数。
- 未配置 Reducer 的 `LastValue` channel 每个 step 最多接收一个值；多个值触发 `InvalidUpdateError`。
- `BinaryOperatorAggregate` 会把一组值依次交给二元 operator。

## 教学简化

- 没有独立 Channel 对象、Pregel loop、superstep、并行任务或 `Overwrite`。
- 只解析一个 state schema，不区分 input、output、private state、context 或 managed value。
- 当前包为兼容前两版调用仍允许省略 schema；v0.3 冻结快照和本课示例都要求显式 schema。
- Reducer key 要求由初始状态提供 current value，不自动构造各种类型的 identity。
- 类型校验只支持课程所需的 Python 常用类型，不实现完整 typing 运行时。

## 我们的设计

- 为了在引入并行之前先测试合并契约，增加 `CompiledGraph.merge_updates()` 教学接口；它不是 LangGraph API。
- 对初始状态、节点更新和 Reducer 结果做运行时 key/type 检查；不能据此推断上游会做同样校验。
- 普通字段冲突错误直接指出 key、值数量和缺少 Reducer。
- Step 保留原始局部 update，同时展示 Reducer 合并后的 state。

本课只复刻状态更新的最小因果链，不能用于推断 LangGraph 完整 Channel、并发与持久化语义。
