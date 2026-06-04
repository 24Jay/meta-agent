# Professional Agent Design

A professional agent is not a longer prompt. It is an engineering system with role boundaries, stable knowledge, memory, workflows, tools, evidence policies, risk policies, and delivery practices.

## Layers

```text
Memory      Long-term preferences, decisions, constraints
Knowledge   Stable domain knowledge and reference material
Skill       Entry point and usage boundaries
Workflow    Repeatable SOP with steps and status
Tools       Stable execution and data access
Reports     Human-readable delivery artifacts
Ops         Feedback, review, monitoring, approvals
```

## Maturity Model

| Level | Name | Description |
|---|---|---|
| L0 | prompt-only | Goal exists only in conversation or prompt |
| L1 | knowledge-agent | Has knowledge and guidance documents |
| L2 | tool-agent | Has stable tools or CLI/API |
| L3 | workflow-agent | Has auditable workflows and run records |
| L4 | delivery-agent | Can produce reliable reports and reviews |
| L5 | monitored-agent | Supports read-only monitoring and periodic summaries |
| L6 | semi-autonomous-agent | Can advance work under explicit human approval |

## Design Checklist

- What is the agent's role?
- What should it never do?
- What knowledge does it need?
- What memory should affect future behavior?
- What workflows should be repeatable?
- What tools/connectors should be stable?
- What evidence level is required for each type of claim?
- What risk level requires human review or approval?
