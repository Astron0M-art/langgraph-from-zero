# Security Policy

## Supported versions

在 `v1.0.0` 前，仅最新教学版本接受安全修复。冻结快照中的问题通过说明和回归测试标注，避免静默
改写历史。`v1.0.0` 的支持窗口将在发布时根据实际维护能力声明。

## Reporting

请优先使用 GitHub Private Vulnerability Reporting。不要在公开 Issue 中粘贴：

- API Key、Token、Cookie 或 OAuth 信息
- 未脱敏的 checkpoint、trace、提示词或研究数据
- 可直接利用的破坏性 payload
- 包含个人信息的路径、日志或真实会话

报告应包含受影响版本、最小复现、影响范围和可能的缓解方式。

## Educational boundary

本项目是教学运行时，不是安全沙箱。未来加入的 URL 策略、审批、超时、幂等和权限边界只能降低
风险，不能替代容器、虚拟机、网络隔离、秘密管理或成熟生产平台。
