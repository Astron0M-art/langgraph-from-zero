# LangGraph from Zero

[简体中文](README.md) | [English](README_EN.md)

面向具备 Python 基础、希望通过小型可运行实现理解图运行时语义的中文优先课程。项目从约
100 行确定性状态图出发，逐步研究可恢复 Agent 工作流。

> 本项目以 [LangGraph](https://github.com/langchain-ai/langgraph) 源码为研究锚点，但不是
> LangChain 官方项目，也不是 LangGraph 的 Python 移植版或 API 兼容实现。

## 当前能做什么

当前版本：[`v0.3.0` 类型化 State 与 Reducer](lessons/03-typed-state-reducers/README.md)。它用
`TypedDict` 定义字段契约，用 `Annotated` Reducer 累积更新，并让显式初始状态或节点更新中的未知
字段、错误类型和无 Reducer 的批内多写失败；不依赖 LangChain、LangGraph 或真实模型。

当前运行器按顺序执行节点，支持静态边、条件路由和有序 update batch 的合并实验。运行演示会看到
四个确定性步骤：规范化问题、两次收集离线证据、进入审查；每步显示局部更新、合并后状态和下一跳。

## 尚未做到什么

当前没有 Channel、Pregel superstep、并行调度、Checkpoint、持久化、崩溃恢复或 Interrupt，也没有
内建的模型、网络与外部副作用 adapter。`merge_updates()` 只是验证 Reducer 与普通字段冲突语义的教学
接口，不代表已有并发执行。用户提供的 Python 节点、路由和 Reducer 仍是可信回调；运行器只浅拷贝
state，不会阻止它们修改嵌套对象或自行执行副作用。以上路线能力不是 `v0.3.0` 的现状。

## 5 分钟运行

要求 Python 3.11 或更高版本。

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m langgraph_from_zero
pytest
```

## 后续学习路径

```text
约 100 行状态图
→ 条件路由与循环
→ 类型化 State 与 Reducer
→ 编译期图校验
→ Channel 与 Pregel Superstep
→ 并行调度与确定性提交
→ Checkpoint 与崩溃恢复
→ Interrupt 与人工审批
→ 幂等重试、超时和取消
→ 事件流、轨迹与回放
→ Subgraph 与状态适配
→ 短期状态与长期 Memory
→ FakeModel 与最小 Agent 桥接
→ 多角色编排与评测
→ 可恢复 Deep Research Agent
```

完整版本计划见 [ROADMAP.md](ROADMAP.md)。每个正式版本必须满足
[教学契约](docs/teaching-contract.md)和[生产成长门禁](docs/production-readiness.md)。

## 与 Pi Agent from Zero 的边界

本项目不会再次把 read/write/edit、Shell、TUI、MCP 或 Skills 当作课程主线。

- `pi-agent-from-zero` 研究单体 Coding Agent 如何感知和作用于本地环境。
- `langgraph-from-zero` 的路线图研究长运行 Agent 如何组织状态、并发、恢复、人工介入和验证。
- 工具调用只在后期作为图运行时的一个适配边界出现。

## 教学原则

- 每版冻结快照可独立运行，不依赖未来版本。
- 先暴露上一版的真实局限，再引入最小新抽象。
- 中文讲义是教学事实源；公共 API 和代码标识符使用英文。
- 每个源码结论指向固定上游 commit、文件、符号或测试。
- 默认使用 FakeModel、fixture 和确定性时钟，不要求 API Key。
- 故障注入明确标为实验，不冒充生产事故。
- “可生产”是一组可验证门禁，不是一句宣传语。

## 仓库结构

```text
langgraph-from-zero/
├── lessons/                    # 每版独立课程与冻结快照
├── src/langgraph_from_zero/    # 当前最新实现
├── tests/                      # 当前版本自动化测试
├── docs/                       # 教学、上游、生产与自动化规范
├── ROADMAP.md
└── CHANGELOG.md
```

## 开源协作

- [贡献指南](CONTRIBUTING.md)
- [行为准则](CODE_OF_CONDUCT.md)
- [安全策略](SECURITY.md)
- [上游基线](docs/upstream-baseline.md)
- [自动维护策略](docs/automation-policy.md)

## 作者与维护者

- [Astron_ma](https://github.com/Astron0M-art)（GitHub：`Astron0M-art`）

## License

[MIT](LICENSE)。上游项目及第三方项目保留其各自许可证与署名。
