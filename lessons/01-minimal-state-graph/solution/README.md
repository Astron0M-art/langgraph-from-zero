# 参考思路

```python
def word_count(state):
    return {"word_count": len(str(state["question"]).split())}
```

将边调整为 `normalize -> word_count -> plan`。测试既要断言最终值，也要断言 Step 顺序；否则无法证明节点确实插入了控制流。
