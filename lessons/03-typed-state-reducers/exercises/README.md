# 练习

复制相邻冻结快照到临时目录，为研究状态增加 `citations` 字段和 Reducer：

- update 类型为 `list[str]`，state value 也是 `list[str]`。
- 保留首次出现顺序并去重。
- 两个 update batch 分别包含 `['A', 'B']` 与 `['B', 'C']`，结果必须是 `['A', 'B', 'C']`。
- 初始 state 不得被修改。
- 再构造一个 Reducer 返回错误类型的失败断言。

写下该 Reducer 是否满足结合律；未来并行提交顺序变化时，这个性质为什么重要？
