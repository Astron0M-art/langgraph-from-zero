# 实验：谁拥有状态合并规则

## 正常任务

运行冻结快照，观察两次 `collect` 都只返回一个单元素列表，但 Step state 中的 `evidence` 依次为一个、两个元素。这证明累积来自 Reducer，不是节点读取旧列表后自行修改。

再运行课程测试，确认同一 Reducer 也能把两个 update batch 值合并为 `['a', 'b']`。

## 边界任务

把初始 `evidence` 删除。当前实现会报告 `reducer key 'evidence' must be initialized` 或缺少必填字段，而不是猜测空列表。这暴露了本版没有通用 Reducer identity 推导的边界。

## 故障注入一：普通字段多写

对 `evidence_needed` 调用：

```python
graph.merge_updates(
    {"evidence_needed": 2, "evidence": []},
    [{"evidence_needed": 3}, {"evidence_needed": 4}],
)
```

必须得到明确冲突错误。注意：这里只构造“一个未来 superstep 收到两个 update”的合并输入，并没有声称节点已并行运行。

## 故障注入二：Reducer 破坏类型

临时把 Reducer 改成返回字符串。合并必须在结果边界失败，不能把错误类型写进权威状态。

> 以上均为教学故障注入，不是生产事故或真实用户数据。

## 代码练习

完成 [`exercises/README.md`](exercises/README.md) 的去重 citation Reducer，并对照
[`solution/README.md`](solution/README.md) 检查。不要修改冻结快照。

## 理解检验

1. 为什么两个节点写出相同普通值仍应视为冲突？
2. Reducer 为什么不应该负责选择下一节点？
3. `merge_updates()` 为什么不能证明系统已有并发能力？
4. Step 同时保留原始 update 和合并后 state 有什么价值？

参考答案：写入所有权仍然不明确；状态合并与调度应分责；该接口只验证一个有序批次的纯合并；两者共同建立“节点贡献了什么、运行器最终接受了什么”的证据链。
