# 架构说明

```text
node(state copy) ──> partial update ──> merge into authoritative state
                                             │
                                             ▼
                                      route(merged state)
                                             │ label
                               optional path_map lookup
                                             │ target
                          ┌──────────────────┴───────────────┐
                          ▼                                  ▼
                    next graph node                    explicit END
```

## 责任边界

- **请求入口**是冻结快照的 `CompiledGraph.run()`；当前包对应 `invoke()` 和 `stream()`。
- **权威状态**是运行器内部浅复制的 `state`；节点与路由都只收到副本。
- **节点**只计算局部状态更新，不偷偷决定调度。
- **路由函数**只读取合并后的状态并返回字符串标签或节点名。
- **路径映射**把稳定的领域标签（如 `continue`）翻译成图节点名。
- **运行器是调度者**，负责校验目标、记录下一跳，并执行下一步或结束。
- **步数预算**是循环的活性保险，不是业务终止条件。
- **副作用**在本版仍被排除；所有示例节点和路由都是确定性内存函数。
- **完成证据**是实际选择 `END`、返回最终状态，并产生与 fixture 完全一致的轨迹。

## 为什么先合并再路由

`collect` 把 `evidence_collected` 从 1 更新为 2 时，路由必须看到 2 才能进入审查。若路由读取旧状态，就会多执行一次节点，产生 off-by-one。测试把这一执行顺序固定为课程契约。

## 错误面

- `path_map` 指向不存在节点：编译期失败。
- 路由返回未登记标签：决策边界失败，不执行猜测出来的节点。
- 直接路由返回不存在节点或 `START`：运行期失败。
- 条件始终继续：达到 `max_steps` 后失败。

本版没有 checkpoint，因此错误后的恢复策略仍是修复输入或图定义后从头重跑。
