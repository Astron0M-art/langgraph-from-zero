# 02：条件路由与循环

## 本版目标

让图在节点更新状态后，根据最新状态选择“继续收集”或“进入审查”，并把终止条件变成可观察、可测试的控制流。

本版加入两个最小抽象：

1. `add_conditional_edges()` 注册路由函数与可选的标签映射。
2. `Step.next_node` 记录本步实际选择的下一跳，包括显式 `END`。

## 从上一版的局限开始

v0.1 的普通边只能预先写死。研究任务若不知道要收集几份证据，只能把判断塞进节点并伪造状态，或者在图外另写循环；两种方式都会让控制流脱离轨迹。本版让路由成为图的一等边界。

## 运行

从仓库根目录执行：

```bash
python lessons/02-conditional-routing/snapshot/graph.py
python -m unittest discover -s lessons/02-conditional-routing/tests -v
```

预期轨迹见 [`traces/happy-path.txt`](traces/happy-path.txt)。它完全离线，不调用模型或网络。

## 验收

- `collect` 恰好运行两次，路由先回到 `collect`，再转到 `review`。
- 路由读取节点更新合并后的状态，而不是旧状态。
- 未登记的路由标签显式失败。
- 永不结束的条件环在 `max_steps` 处显式失败。
- 初始输入不被修改，重复运行得到相同轨迹。

## 本版边界

- 一个节点只能选择一条普通边或一组条件边，不能同时拥有两者。
- 路由结果只有一个，不支持并行 fan-out 或 `Send`。
- 状态仍是浅复制字典，没有 schema、Reducer 或冲突合并。
- 没有 checkpoint；超过步数后只能从初始输入重跑。

下一版将处理“多个更新如何累积”的问题，引入类型化 State 与 Reducer。
