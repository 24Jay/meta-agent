# Open Source Design

Conclusion: meta-agent should be methodology-first. The Agent Ops Panel is a reference implementation that demonstrates the methodology in practice.

## Project Boundary

Open-source core:

- Professional agent design methodology.
- Skill / Workflow / Tool / Knowledge / Memory layering.
- Evidence and risk policies.
- Agent evaluation rubric.
- MemoryOps and feedback loops.
- Agent Ops data model.
- Schemas, templates, and workflow specs.
- Sanitized examples.

Private downstream projects should keep their domain logic, internal data, private connectors, and real run logs outside the open-source repository.

## Architecture

```text
Methodology
  ↓
Schemas / Templates / Workflows
  ↓
Agent Runtime Interfaces
  ↓
Connectors / Providers
  ↓
Agent Ops Panel reference implementation
```

## Provider Strategy

The framework must be provider-agnostic. Claude can be the first supported provider, but the framework should not assume a specific model runtime.

Recommended abstraction:

```text
Agent Definition → Agent Runtime → Provider Adapter → Model / CLI / Workflow Engine
```

## Reference Implementation

Agent Ops Panel should remain a supplement:

- It visualizes agents, workflows, runs, feedback, approvals, and memory candidates.
- It should not become the primary identity of the project.
- It should not execute high-risk actions without explicit human approval.

## Sanitization Rules

Before publishing, remove or replace:

- Internal paths and hostnames.
- Private docs and wiki links.
- Device IDs, run IDs, session IDs, customer data, and raw logs.
- Business-specific model or algorithm details.
- Private memory and feedback events.
