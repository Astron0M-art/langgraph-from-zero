# Upstream baseline

## 主研究锚点

- Project: [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)
- Release: [`1.2.11`](https://github.com/langchain-ai/langgraph/releases/tag/1.2.11)
- Commit: `644815f9e5bc52ad8f7a5227a456227e9c3e639b`
- License: MIT

上游只读。课程不要求读者本地检出 LangGraph；Source Map 必须引用公开仓库的 commit、路径、符号和测试。

## 证据分类

每条重要架构结论使用以下标签之一：

- **上游事实**：可以从固定 commit 的源码、测试或官方文档直接验证。
- **教学简化**：为暴露核心机制而有意删除的生产复杂度。
- **我们的设计**：课程自己选择的 API、错误模型、测试方式或目录组织。

## 升级规则

课程发布后不静默追随上游。升级必须单独提交 baseline diff，列出符号移动、行为改变、测试影响和
课程是否需要迁移；已经发布的冻结快照保持不变。
