# meta-agent

meta-agent helps teams design professional AI agents that are reviewable, evidence-aware, risk-bounded, and continuously improved through human feedback.

Most agent frameworks focus on orchestration: how agents call tools, talk to each other, or execute tasks. meta-agent focuses on the engineering layer around professional agents: how they are specified, reviewed, governed, evaluated, and improved over time.

It is methodology-first and provider-agnostic. Claude, local models, CLI agents, workflow engines, or custom runtimes can all be downstream implementations.

## Why meta-agent

Professional agents should not be long prompts with hidden assumptions. They should be auditable systems:

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

meta-agent provides schemas, templates, workflows, examples, and validation utilities for building that system.

## Core Ideas

- A professional agent is not just a prompt.
- Capabilities should be explicit and reviewable.
- Workflows define repeatable SOPs rather than ad-hoc behavior.
- Evidence levels prevent overclaiming.
- Risk levels define human review and approval boundaries.
- Feedback events are reviewed before becoming memory, knowledge, workflow changes, or roadmap items.
- MemoryOps should keep raw logs separate from curated long-term memory.
- Runtime automation should come after clear design and governance boundaries.

## How meta-agent is different

meta-agent is not trying to replace orchestration-first frameworks such as LangChain, CrewAI, or AutoGen. Those projects help execute agent systems. meta-agent helps design and govern professional agents before and around execution.

| Area | Orchestration-first frameworks | meta-agent |
| --- | --- | --- |
| Primary focus | Running agent tasks | Designing, reviewing, and improving professional agents |
| Core assets | Chains, tools, agents, graphs | Agent specs, capability matrices, workflows, policies, feedback, memory candidates |
| Governance | Usually project-specific | Evidence/risk policy as a first-class concept |
| Memory | Often runtime memory | Curated MemoryOps with human review |
| Best use | Building execution flows | Making agents auditable, reviewable, and safer to operate |

meta-agent can also complement Claude Code skills, slash commands, or custom agent configs by providing a structured design and review layer around them.

## Repository Structure

```text
meta-agent/
├── docs/          Methodology and design references
├── schemas/       JSON schemas for agents, workflows, runs, feedback, approvals
├── workflows/     Reusable workflow specs
├── templates/     Agent and workflow templates
├── examples/      Sanitized example agents and data
├── packages/      Future core/cli/server/web packages
└── scripts/       Validation and redaction helpers
```

## Quickstart

Clone the repository, inspect the methodology assets, and validate the project assets:

```bash
git clone https://github.com/<owner>/meta-agent.git
cd meta-agent
PYTHONPATH=src python3 -m meta_agent validate .
PYTHONPATH=src python3 -m meta_agent inspect-project . --format json
PYTHONPATH=src python3 -m meta_agent report-project . --output /tmp/meta-agent-report.md
PYTHONPATH=src python3 -m meta_agent run-workflow examples/agents/research-agent/workflows/research-summary.json --format json
PYTHONPATH=src python3 -m meta_agent review examples/agents/research-agent
PYTHONPATH=src python3 -m meta_agent score examples/agents/research-agent --format json
PYTHONPATH=src python3 -m meta_agent propose-memory-candidate examples/data/feedback_events.example.json
PYTHONPATH=src python3 -m meta_agent review-memory-candidate examples/data/memory_candidates.example.json --decision accept --reviewer reviewer-example --reason "Specific and durable behavior." --output /tmp/reviewed-candidate.json
PYTHONPATH=src python3 -m meta_agent commit-memory-candidate /tmp/reviewed-candidate.json --output-dir /tmp/meta-agent-memory
PYTHONPATH=src python3 -m meta_agent init example-agent --output-dir /tmp
```

The compatibility script still works:

```bash
python3 scripts/validate_project.py
```

Start with the end-to-end walkthrough:

- `examples/README.md` shows how an example `research-agent` moves from design to review, run record, feedback event, and memory candidate.

Then read the project overview and core methodology docs:

- `docs/PROJECT_DESCRIPTION_EN.md` for the English project description.
- `docs/PROJECT_DESCRIPTION_ZH.md` for the Chinese project description.
- `docs/PROFESSIONAL_AGENT_DESIGN.md` for the core design model.
- `docs/EVIDENCE_AND_RISK_POLICY.md` for review and approval boundaries.
- `docs/AGENT_MEMORY_OPS_SPEC.md` for memory and feedback handling.
- `docs/AGENT_EVALUATION_RUBRIC.md` for evaluating agent maturity.
- `docs/CLI.md` for the current read-only command-line interface.
- `docs/WORKFLOW_AUTHORING.md` for writing workflow specs that pass semantic validation.

## Current Status

This repository is an early open-source seed. The current milestone is documentation, schemas, workflow specs, templates, sanitized examples, and a minimal project validator.

See `ROADMAP.md` for the planned path from methodology seed to CLI, reference operations layer, and runtime interfaces.

## What This Project Is Not

- Not a model provider wrapper.
- Not tied to one LLM provider.
- Not a replacement for domain expertise.
- Not a black-box autonomous agent runner.
- Not a tool for bypassing human approval.
- Not a storage location for secrets, customer data, raw chat logs, or private run logs.

## Provider Strategy

The framework should be provider-agnostic. Claude can be a first-class provider, but the methodology and schemas should work with any LLM, CLI agent, workflow runtime, or local model.

## License

Apache-2.0. See `LICENSE`.
