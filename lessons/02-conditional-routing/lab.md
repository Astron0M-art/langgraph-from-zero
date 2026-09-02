# 实验：让终止条件进入图

## 正常任务

运行冻结快照。确认轨迹顺序为 `collect -> collect -> review`，三个 `next` 依次为 `collect`、`review`、`__end__`。

然后把 `evidence_needed` 改为 1，确认只执行一次 `collect` 就进入 `review`。这证明路由读取的是合并后的更新。

## 边界任务

把 `evidence_needed` 改为 0。当前实现仍会先执行一次 `collect` 再审查，说明图运行时只负责控制流，
不会替你定义“证据数必须为正”的领域约束。记录这一结果，不要在路由里静默修正输入；类型化 State 与输入校验属于后续课程。

## 故障注入一：未知路由

把 `route_after_collect()` 的最后一个返回值改成 `"publish"`，但不要把它加入 `path_map`。运行必须抛出包含 `unknown route 'publish'` 的 `GraphError`，而不是忽略错误或猜测节点。

## 故障注入二：条件永远继续

让路由永远返回 `"continue"`，并以 `max_steps=3` 运行。验收结果必须是 `graph exceeded max_steps=3`，进程不能挂起。

> 以上是明确构造的教学故障，不代表真实生产事故或线上数据。

## 代码练习

完成 [`exercises/README.md`](exercises/README.md) 的 `quality_check` 分支，并对照
[`solution/README.md`](solution/README.md) 检查控制流。练习代码应放在临时副本中，不修改冻结快照。

## 理解检验

1. 为什么 `max_steps` 不能替代领域终止条件？
2. 路由为何不直接修改 state？
3. `path_map` 相比直接返回节点名提供了什么解耦？

参考答案：步数预算只能阻断失控执行；读写分离让更新归属可追踪；领域标签不会因节点重命名而改变。
