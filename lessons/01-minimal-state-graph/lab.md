# 实验：看见状态与控制流

## 正常任务

运行冻结快照，确认 `normalize` 先清理问题，`plan` 后读取清理后的状态。

## 边界任务

把问题改为空字符串。观察图仍然完成，这说明“图能终止”不代表“领域输入有效”；输入 schema 将在后续版本出现。

## 故障注入

把 `plan -> END` 改成 `plan -> normalize`，并把 `max_steps` 设置为 3。验收结果必须是显式
`GraphError`，不能静默挂起。

## 代码练习

在 `exercises/` 中实现 `word_count` 节点，并把它插入 `normalize` 与 `plan` 之间。要求：

- 不修改输入 mapping。
- Step 顺序为 `normalize`、`word_count`、`plan`。
- 最终状态新增 `word_count`。

## 理解检验

1. 为什么节点应该返回局部更新而不是完整状态？
2. 为什么 `compile()` 通过后仍需要 `max_steps`？
3. 本版谁决定下一步？

参考答案：局部更新为未来 reducer 和并发合并留下边界；静态合法的环仍可能无法终止；本版由静态边映射决定下一步。
