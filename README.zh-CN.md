# meta-agent

[English](README.md) | 简体中文

meta-agent 帮助团队设计专业 AI Agent，使其可审查、具备证据边界、风险受控，并能通过人工反馈持续改进。

大多数 Agent 框架关注编排和执行：Agent 如何调用工具、如何协作、如何完成任务。meta-agent 关注的是专业 Agent 周围的工程治理层：Agent 如何被定义、审查、治理、评估和持续改进。

它不绑定特定模型提供商或运行时。Claude、本地模型、CLI Agent、workflow engine 或自定义 runtime 都可以作为下游实现。

## 为什么需要 meta-agent

专业 Agent 不应该只是带有隐藏假设的长 prompt，而应该是可审计的系统：

```text
Agent Definition
+ Capability Matrix
+ Knowledge
+ Memory
+ Workflows
+ Tools / Connectors
+ Evidence Policy
+ Risk Policy
+ Human Feedback
+ Review / Approval
+ Run Records
```

meta-agent 提供 schemas、templates、workflows、examples 和验证工具，帮助团队构建这套系统。

## 核心理念

- 专业 Agent 不只是 prompt。
- 能力边界应该显式、可审查。
- Workflow 应该描述可复用 SOP，而不是临时行为。
- Evidence level 用于防止过度断言。
- Risk level 用于定义人工 review 和 approval 边界。
- Feedback event 需要经过审查，才能转化为 memory、knowledge、workflow change 或 roadmap item。
- MemoryOps 应该把原始日志和经过整理的长期记忆分开。
- 运行时自动化应该建立在清晰设计和治理边界之后。

## 与编排框架的区别

meta-agent 不试图替代 LangChain、CrewAI、AutoGen 等编排优先框架。那些项目帮助执行 Agent 系统；meta-agent 帮助在执行之前和执行周围设计、审查和治理专业 Agent。

| 维度 | 编排优先框架 | meta-agent |
| --- | --- | --- |
| 主要关注 | 运行 Agent 任务 | 设计、审查和改进专业 Agent |
| 核心资产 | Chains、tools、agents、graphs | Agent specs、capability matrices、workflows、policies、feedback、memory candidates |
| 治理 | 通常由项目自行实现 | Evidence/risk policy 是一等概念 |
| Memory | 常见为运行时 memory | 带人工审查的 MemoryOps |
| 适用场景 | 构建执行流程 | 让 Agent 可审计、可审查、更安全地运行 |

meta-agent 也可以为 Claude Code skills、slash commands 或自定义 Agent 配置提供结构化的设计和 review 层。

## 仓库结构

```text
meta-agent/
├── docs/          方法论和设计文档
├── schemas/       Agent、workflow、run、feedback、approval 的 JSON schemas
├── workflows/     可复用 workflow specs
├── templates/     Agent 和 workflow 模板
├── examples/      脱敏示例 Agent 和数据
├── packages/      未来 core/cli/server/web packages
└── scripts/       验证和脱敏辅助脚本
```

## 快速开始

克隆仓库，查看方法论资产，并验证项目内容：

```bash
git clone https://github.com/24Jay/meta-agent.git
cd meta-agent
PYTHONPATH=src python3 -m meta_agent validate .
PYTHONPATH=src python3 -m meta_agent inspect-project . --format json
PYTHONPATH=src python3 -m meta_agent readiness .
PYTHONPATH=src python3 -m meta_agent report-project . --output /tmp/meta-agent-report.md
PYTHONPATH=src python3 -m meta_agent run-workflow examples/agents/research-agent/workflows/research-summary.json --format json
PYTHONPATH=src python3 -m meta_agent review examples/agents/research-agent
PYTHONPATH=src python3 -m meta_agent score examples/agents/research-agent --format json
PYTHONPATH=src python3 -m meta_agent propose-memory-candidate examples/data/feedback_events.example.json
PYTHONPATH=src python3 -m meta_agent review-memory-candidate examples/data/memory_candidates.example.json --decision accept --reviewer reviewer-example --reason "Specific and durable behavior." --output /tmp/reviewed-candidate.json
PYTHONPATH=src python3 -m meta_agent commit-memory-candidate /tmp/reviewed-candidate.json --output-dir /tmp/meta-agent-memory
PYTHONPATH=src python3 -m meta_agent init example-agent --output-dir /tmp
```

兼容脚本仍然可用：

```bash
python3 scripts/validate_project.py
```

建议先阅读端到端示例：

- `examples/README.md` 展示一个 `research-agent` 如何从设计、review、run record、feedback event 走到 memory candidate。

然后阅读核心文档：

- `docs/PROJECT_DESCRIPTION_ZH.md`：中文项目说明。
- `docs/PROJECT_DESCRIPTION_EN.md`：英文项目说明。
- `docs/PROFESSIONAL_AGENT_DESIGN.md`：核心设计模型。
- `docs/EVIDENCE_AND_RISK_POLICY.md`：证据和风险边界。
- `docs/AGENT_MEMORY_OPS_SPEC.md`：MemoryOps 和反馈处理。
- `docs/AGENT_EVALUATION_RUBRIC.md`：Agent 成熟度评估。
- `docs/CLI.md`：当前 CLI 能力。
- `docs/WORKFLOW_AUTHORING.md`：如何编写能通过语义校验的 workflow specs。

## 当前状态

当前仓库是早期开源种子版本。当前里程碑包括文档、schemas、workflow specs、templates、脱敏 examples 和最小项目验证器。

后续计划见 `ROADMAP.md`。

## 这个项目不是什么

- 不是模型 provider wrapper。
- 不绑定某个 LLM provider。
- 不是领域专业知识的替代品。
- 不是黑盒 autonomous agent runner。
- 不是绕过人工审批的工具。
- 不是存放密钥、客户数据、原始聊天记录或私有运行日志的地方。

## Provider 策略

框架应该保持 provider-agnostic。Claude 可以是一等 provider，但方法论和 schemas 应该适用于任意 LLM、CLI Agent、workflow runtime 或本地模型。

## License

Apache-2.0。详见 `LICENSE`。
