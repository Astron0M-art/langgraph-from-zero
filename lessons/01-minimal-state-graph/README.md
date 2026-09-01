# 01：最小状态图

## 本版目标

构建一个不依赖模型、不依赖 LangGraph 的最小状态图，观察 Agent 编排最基础的四个事实：

1. 节点读取旧状态并返回局部更新。
2. 边决定下一个节点。
3. 编译阶段先拒绝明显非法结构。
4. 运行时用步数预算阻止无法终止的图。

## 为什么不从 LLM 开始

模型输出会引入随机性、费用和供应商差异，掩盖“状态由谁修改、下一步由谁决定”。本版全部节点是纯函数，
先建立可以逐步断言的运行时语义。

## 运行

从仓库根目录执行：

```bash
python lessons/01-minimal-state-graph/snapshot/graph.py
python -m unittest discover -s lessons/01-minimal-state-graph/tests -v
```

预期轨迹见 [`traces/happy-path.txt`](traces/happy-path.txt)。

## 本版边界

- 每个节点只能有一条普通出边。
- 状态只是浅复制字典，没有 schema 或 reducer。
- 没有并发、checkpoint、interrupt、重试或 LLM。
- `stream()` 当前返回完整 Step 列表，不是异步增量流。

下一版将用一个可复现失败说明：静态边无法根据研究结果选择“继续检索”还是“进入审查”。
