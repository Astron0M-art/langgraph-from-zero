# LangGraph Source Map

固定上游：LangGraph `1.2.11`，commit
`644815f9e5bc52ad8f7a5227a456227e9c3e639b`。所有路径和行号仅对该 commit 有效。

| 概念 | 固定上游位置 | 本版处理 |
|---|---|---|
| 条件边公共入口 | `libs/langgraph/langgraph/graph/state.py:982` 的 `StateGraph.add_conditional_edges` | 保留 source、path 与可选 path_map |
| 路由规格 | `libs/langgraph/langgraph/graph/_branch.py:83` 的 `BranchSpec` | 简化为私有 `_ConditionalEdge` |
| 路由构建 | `_branch.py:89` 的 `BranchSpec.from_path` | 不做 Runnable 包装或类型提示推导 |
| 路由执行 | `_branch.py:122` 的 `BranchSpec.run` | 只实现同步、单结果路由 |
| 结果映射与校验 | `_branch.py:192` 的 `BranchSpec._finish` | 映射标签，拒绝非法目标，允许 `END` |
| Agent 工具循环示例 | `libs/langgraph/tests/test_large_cases.py:498-591` | 改成离线“收集—审查”循环 |
| 条件环与递归限制 | `libs/langgraph/tests/test_pregel.py:588-626` | 用 `max_steps` 做最小活性门禁 |
| 路由读取合并状态 | `libs/langgraph/tests/test_state.py:275-308` | 用测试固定“更新后再路由” |

## 上游事实

- `StateGraph.add_conditional_edges()` 接受源节点、路由 callable/Runnable，以及可选的目标映射。
- 路由可以用 `END` 表示终止；固定上游的 branch 完成逻辑还支持目标列表与 `Send`。
- 固定上游测试覆盖条件循环、递归限制，以及条件边读取更新后状态的行为。

## 教学简化

- 不导入 LangGraph，也不追求 API 兼容。
- 不支持异步路由、多个目的地、`Send`、Runnable、类型提示推导或可视化推断。
- 只允许节点拥有普通单出边或条件单出边之一。

## 我们的设计

- `path_map` 的键是领域标签，值是节点名或课程 `END`。
- `Step.next_node` 让每次选择进入确定性轨迹。
- 无映射时允许直接返回节点名，但运行器仍验证目标。
- 未知标签和无穷条件环都有专门的离线故障实验。

这些课程设计不能用于推断 LangGraph 完整 Pregel、并发或持久化语义。
