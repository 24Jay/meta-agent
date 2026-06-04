# meta-agent Project Description

## One-line Summary

meta-agent is a methodology-first toolkit for designing, reviewing, validating, and improving professional AI agents with explicit evidence, risk, memory, and human-feedback boundaries.

## Elevator Pitch

Most agent frameworks focus on orchestration: how agents call tools, coordinate tasks, or execute workflows. meta-agent focuses on the engineering layer around professional agents: how they are specified, reviewed, governed, evaluated, and improved over time.

It helps teams turn agents from long prompts and one-off scripts into reviewable systems with clear capabilities, risk levels, evidence policies, run records, feedback loops, and curated MemoryOps.

## Problem

Professional AI agents are increasingly used for research, data analysis, engineering support, operations, and domain-specific decision support. However, many agent projects still suffer from common problems:

- Agent capabilities are hidden inside prompts.
- Risk boundaries are unclear.
- Evidence and recommendations are mixed together.
- Feedback is not converted into durable improvements.
- Memory is written too casually or polluted by raw logs.
- Workflows are hard to review before they become automation.
- Teams lack lightweight validation and readiness checks before sharing or publishing agent projects.

## Solution

meta-agent provides a lightweight, provider-agnostic structure for professional agent development:

- Agent definitions
- Capability matrices
- Workflow specs
- Evidence and risk policies
- Run records
- Feedback events
- Memory candidates
- Human review checkpoints
- Project validation
- Read-only CLI tools
- Release/readiness reports

The project is intentionally methodology-first. It does not require a specific model provider, agent runtime, or orchestration framework.

## What meta-agent Is

meta-agent is:

- A professional agent design toolkit.
- A validation and review layer for agent projects.
- A set of schemas, templates, workflows, and examples.
- A CLI for initializing, validating, reviewing, scoring, dry-running, and reporting agent projects.
- A MemoryOps workflow for turning feedback into reviewed memory candidates.

## What meta-agent Is Not

meta-agent is not:

- A model provider wrapper.
- A replacement for LangChain, CrewAI, AutoGen, or other orchestration frameworks.
- A black-box autonomous agent runner.
- A tool for bypassing human approval.
- A storage location for secrets, private logs, customer data, or production data.

## Core Concepts

### Agent Definition

A structured description of the agent identity, role, maturity level, default risk level, workflows, and connectors.

### Capability Matrix

A reviewable table describing what the agent supports, what is proposed, what is unsupported, and what evidence/risk boundaries apply.

### Workflow Spec

A JSON SOP for repeated agent work. Workflows include risk level, inputs, outputs, steps, failure behavior, and evidence policy.

### Evidence Policy

Rules that prevent overclaiming. For example, a workflow can require evidence, known limitations, and next steps before emitting a report.

### Risk Policy

A boundary system for distinguishing read-only work, review-required work, approval-required work, and blocked work.

### MemoryOps

A curated memory workflow:

```text
feedback event
  -> proposed memory candidate
  -> human review
  -> accepted/rejected candidate
  -> optional local markdown commit
```

meta-agent never commits memory automatically.

## Current CLI Capabilities

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

## Validation Coverage

`meta-agent validate` currently checks:

- JSON syntax
- Required project files
- Example references
- Schema conformity
- Workflow semantics
- Markdown local links
- Sensitive pattern scan

## Example Flow

The repository includes a sanitized `research-agent` example:

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

## Project Status

Current status: **v0.1 alpha seed**.

The project is ready to be pushed as an initial GitHub seed repository. It has CLI commands, tests, CI, examples, schemas, workflow specs, validation, and documentation. It is not yet a full runtime SDK or provider adapter framework.

## Roadmap

Near-term focus:

- Strengthen validation and review tooling.
- Improve examples and documentation.
- Add more project readiness checks.
- Prepare release artifacts and GitHub seed publishing.

Later directions:

- Runtime interfaces
- Provider adapters
- Agent Ops Panel reference implementation
- Package publishing
- Agent maturity scoring improvements
- Workflow template gallery

## Target Users

meta-agent is useful for:

- AI agent engineers
- LLM application developers
- platform teams building internal agents
- teams that need human-in-the-loop governance
- researchers designing domain-specific AI agents
- maintainers who want auditable agent workflows

## Suggested GitHub Repository Description

Methodology-first toolkit for professional AI agent design, validation, review, MemoryOps, and human-in-the-loop governance.

## Suggested Topics

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
