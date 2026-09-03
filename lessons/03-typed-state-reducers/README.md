# 03：类型化 State 与 Reducer

## 本版目标

把“状态里允许出现什么、更新如何合并”从节点的默契提升为可验证契约：

1. 用 `TypedDict` 声明字段、必填项与值类型。
2. 用 `Annotated[ValueType, reducer]` 声明可累积字段。
3. 普通字段收到同批多个值时显式报告冲突。
4. 用 `CompiledGraph.merge_updates()` 在并行调度出现前，单独验证批量更新语义。

## 从上一版的局限开始

v0.2 对所有更新都执行 `dict.update()`。第二次 `collect` 返回新的 `evidence` 时会覆盖第一次结果；若两个未来并行节点同时写同一个 key，后写者还会静默获胜。图虽然能路由和终止，却无法解释“状态为什么变成这个值”。

## 运行

从仓库根目录执行：

```bash
python lessons/03-typed-state-reducers/snapshot/graph.py
python -m unittest discover -s lessons/03-typed-state-reducers/tests -v
```

预期 `evidence` 从空列表依次累积 `source-1`、`source-2`，然后进入审查。实际输出与
[`traces/happy-path.txt`](traces/happy-path.txt) 逐字节比对，全程不调用网络或模型。

## 验收

- Reducer 对顺序节点更新和显式 update batch 使用同一合并规则。
- 普通字段在同一 update batch 中收到两个值时失败，不静默覆盖。
- 未知字段、缺少必填字段和错误值类型在状态边界失败。
- 节点仍只返回局部更新，路由读取的是 reducer 合并后的状态。
- 冻结快照可独立运行，v0.1 与 v0.2 快照不被修改。

## 本版边界

- `merge_updates()` 只是隔离合并语义的教学接口，不代表节点已经并行执行。
- update batch 的顺序由调用者明确给出；尚未定义并行任务的确定性提交顺序。
- Reducer key 必须在初始状态中初始化，本版不推导通用 identity。
- 状态只做浅复制；Reducer 必须返回新值，不得原地修改 current 或 update 中的嵌套对象。
- 运行时类型检查只覆盖课程支持的常用 Python 类型，不替代静态类型检查或数据验证库。
- 仍无 Channel、Pregel superstep、checkpoint、异步执行或外部副作用。

下一版将把更多结构错误前移到编译期，加入可达性、死端与保留节点检查。
