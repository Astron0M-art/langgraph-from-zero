# Contributing

本项目中文优先，同时接受中文或英文 Issue、Discussion 和 Pull Request。公共 API、代码标识符和
协议字段使用英文；中文课程是教学事实源。参见[语言策略](docs/language-policy.md)。

## 欢迎的贡献

- 修正代码、测试、架构图或讲义中的错误
- 增加可复现的边界案例和故障注入
- 改善固定 LangGraph 上游的源码符号映射
- 补充 checkpoint、并发、幂等和跨平台验证
- 提升不依赖真实模型与网络的离线评测

## 开发流程

1. 从 `main` 创建短生命周期分支。
2. 一个变更解决一个明确问题，不跨越 Roadmap 多个版本。
3. 同步更新实现、冻结快照、讲义、测试、README 状态和 Changelog。
4. 运行完整质量检查。
5. Pull Request 写清上一版限制、新抽象、源码依据和验证证据。

```bash
python -m pip install -e '.[dev]'
ruff format --check .
ruff check .
mypy src
pytest
python -m unittest discover -s lessons/01-minimal-state-graph/tests -v
python -m build
```

## Commit messages

使用 Conventional Commits，例如：

```text
feat(routing): add conditional edges
fix(checkpoint): reject partial snapshots
test(runtime): inject parallel node failure
docs(source-map): pin pregel loop symbols
```

改变课程结论时必须说明原结论、上游证据、受影响版本和是否需要迁移 trace 或 fixture。
