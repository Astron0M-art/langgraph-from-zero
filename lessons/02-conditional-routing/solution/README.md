# 参考思路

```python
graph.add_node("quality_check", lambda state: {})
graph.add_conditional_edges(
    "quality_check",
    lambda state: "accept" if state["quality_ok"] else "retry",
    {"accept": "review", "retry": "collect"},
)
```

同时把 `collect` 的 `review` 映射目标改为 `quality_check`。测试至少断言节点顺序、`next` 选择和最终状态；只断言最终状态无法证明退回路径真的发生过。
