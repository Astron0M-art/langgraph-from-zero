# 教学契约

每个正式版本必须形成“问题—实现—实验—证据—边界”的闭环。

## 课程目录

```text
lessons/NN-topic/
├── README.md
├── architecture.md
├── langgraph-source-map.md
├── lab.md
├── exercises/
├── solution/
├── snapshot/
├── tests/
└── traces/
```

## 必需内容

- `README.md`：本版目标、上一版局限、运行命令、预期输出、不解决的问题。
- `architecture.md`：入口、权威状态、调度者、副作用、完成证据、失败和恢复路径。
- `langgraph-source-map.md`：固定上游文件、符号、测试；分清上游事实、教学简化和我们的设计。
- `lab.md`：正常任务、边界任务、故障注入、代码练习、理解检验和答案。
- `snapshot/`：无需未来课程代码即可运行的冻结实现。
- `tests/`：默认离线，验证外部行为而不是 Agent 自报完成。
- `traces/`：经过测试或脚本产生的确定性示例，不手写伪造运行证据。

## 发布门禁

- 快照可在干净环境运行。
- 格式、静态检查、类型检查、测试、构建全部通过。
- 讲义中的命令已经实际执行。
- Source Map 指向锁定上游，链接可解析。
- 中文 README、英文 README、版本号和 Changelog 一致。
- 安全扫描不包含密钥、个人数据、本地路径依赖或真实 Session。
- 版本拥有明确的限制；不把实验性能力称为生产就绪。
