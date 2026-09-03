# 参考思路

```python
def merge_citations(current: list[str], update: list[str]) -> list[str]:
    return list(dict.fromkeys([*current, *update]))


class ResearchState(TypedDict):
    citations: Annotated[list[str], merge_citations]
```

至少测试空更新、批内重复、跨批重复和输入不变。这个实现对列表拼接顺序敏感，但在调用者提供固定 update 顺序时结果确定；v0.6 才会定义并行任务的确定性提交顺序。
