# meta-agent 项目说明

## 一句话介绍

meta-agent 是一个方法论优先的专业 AI Agent 工具包，用于设计、审查、验证和持续改进具备证据边界、风险边界、记忆治理和人工反馈闭环的专业 Agent。

## 项目定位

大多数 Agent 框架更关注编排和执行：Agent 如何调用工具、如何协作、如何完成任务。meta-agent 关注的是专业 Agent 外围的工程治理层：Agent 如何被定义、审查、验证、评估、运营和持续改进。

它的目标是帮助团队把 Agent 从“长 prompt + 临时脚本”升级为可审查、可验证、可追踪、可治理的专业系统。

## 要解决的问题

专业 AI Agent 正在被用于研究、数据分析、工程辅助、运营支持和垂直领域决策。但很多 Agent 项目仍然存在以下问题：

- 能力边界藏在 prompt 里，难以审查。
- 风险边界不清楚，不知道哪些动作需要人工确认。
- 证据和建议混在一起，容易过度断言。
- 用户反馈没有转化为可追踪的长期改进。
- memory 写入过于随意，容易被原始日志或临时信息污染。
- workflow 在自动化前缺少可 review 的规范。
- 项目发布或共享前缺少轻量级质量检查。

## 解决方案

meta-agent 提供一套轻量、模型无关、运行时无关的专业 Agent 工程结构：

- Agent definition
- Capability matrix
- Workflow spec
- Evidence policy
- Risk policy
- Run record
- Feedback event
- Memory candidate
- Human review checkpoint
- Project validation
- 只读 CLI 工具
- 项目报告和发布前检查

项目坚持方法论优先，不绑定特定模型提供商，也不要求使用某个 Agent 编排框架。

## meta-agent 是什么

meta-agent 是：

- 专业 Agent 设计工具包。
- Agent 项目的验证和审查层。
- 一组 schemas、templates、workflows、examples。
- 一个可运行 CLI，用于初始化、验证、审查、评分、dry-run 和生成报告。
- 一套 MemoryOps 流程，用于把反馈转化为经过审查的 memory candidate。

## meta-agent 不是什么

meta-agent 不是：

- 模型 provider wrapper。
- LangChain、CrewAI、AutoGen 等编排框架的替代品。
- 黑盒 autonomous agent runner。
- 绕过人工审批的工具。
- 存放密钥、私有日志、客户数据或生产数据的地方。

## 核心概念

### Agent Definition

描述 Agent 的身份、角色、成熟度、默认风险等级、workflow 和 connector。

### Capability Matrix

用表格明确 Agent 支持什么、计划支持什么、不支持什么，以及对应的证据等级、风险等级和人工 review 要求。

### Workflow Spec

用 JSON 描述可重复执行的 SOP，包括风险等级、输入、输出、步骤、失败策略和证据要求。

### Evidence Policy

用于防止过度断言。例如要求报告必须包含 evidence、known limitations 和 next steps。

### Risk Policy

用于区分 read-only、review-required、approval-required 和 blocked 动作。

### MemoryOps

meta-agent 的 memory 不是自动写入，而是经过候选和审查流程：

```text
feedback event
  -> proposed memory candidate
  -> human review
  -> accepted/rejected candidate
  -> optional local markdown commit
```

meta-agent 不会自动提交长期 memory。

## 当前 CLI 能力

```bash
meta-agent init <agent-id>
meta-agent validate [path]
meta-agent inspect-project [path]
meta-agent report-project [path]
meta-agent list-workflows [path]
meta-agent explain-workflow <workflow.json>
meta-agent run-workflow <workflow.json>
meta-agent review <agent-path>
meta-agent score <agent-path>
meta-agent propose-memory-candidate <feedback.json>
meta-agent review-memory-candidate <candidate.json>
meta-agent commit-memory-candidate <candidate.json>
```

## 当前验证能力

`meta-agent validate` 当前检查：

- JSON 语法
- 必备项目文件
- 示例数据引用关系
- schema conformity
- workflow semantics
- Markdown 本地链接
- 敏感信息模式

## 示例流程

仓库中包含一个脱敏的 `research-agent` 示例：

```text
agent definition
  -> capability matrix
  -> workflow spec
  -> dry-run record
  -> research report
  -> feedback event
  -> memory candidate
  -> human review
  -> local markdown memory commit
```

## 当前状态

当前状态：**v0.1 alpha seed**。

项目已经具备 CLI、测试、CI、示例、schemas、workflow specs、验证器和文档，适合作为 GitHub 初始开源种子仓库发布。但它还不是完整 runtime SDK，也还没有 provider adapter 和 Agent Ops Panel reference implementation。

## Roadmap

近期重点：

- 继续强化验证和审查工具。
- 完善 examples 和文档。
- 增加发布前 readiness checks。
- 准备 GitHub seed 发布材料。

后续方向：

- runtime interfaces
- provider adapters
- Agent Ops Panel reference implementation
- 包发布
- Agent maturity scoring 增强
- workflow template gallery

## 目标用户

meta-agent 适合：

- AI Agent 工程师
- LLM 应用开发者
- 内部 Agent 平台团队
- 需要 human-in-the-loop 治理的团队
- 设计领域专家 Agent 的研究者
- 希望 Agent workflow 可审计、可验证、可持续改进的维护者

## GitHub 仓库简介建议

Methodology-first toolkit for professional AI agent design, validation, review, MemoryOps, and human-in-the-loop governance.

## GitHub topics 建议

```text
ai-agent
llm
agent-framework
agent-evaluation
human-in-the-loop
memory
workflow
governance
ai-safety
cli
```
