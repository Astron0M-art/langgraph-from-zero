# 练习

复制相邻 `snapshot/graph.py` 到临时目录，新增一个 `quality_check` 节点：

- `collect` 达到数量后先进入 `quality_check`。
- `quality_check` 根据 `quality_ok` 路由到 `review` 或返回 `collect`。
- 为通过与退回两条路径各写一个断言。
- 再写一个永远退回的案例，证明 `max_steps` 能阻断循环。

不要直接修改冻结快照；练习结果应能独立运行。
