# CLI

meta-agent includes an early read-only CLI for validating project assets and reviewing example agents.

The CLI is intentionally lightweight. It does not execute autonomous agent tasks or call model providers.

## Run without installation

From the repository root:

```bash
PYTHONPATH=src python3 -m meta_agent --version
PYTHONPATH=src python3 -m meta_agent init example-agent --output-dir /tmp
PYTHONPATH=src python3 -m meta_agent validate .
PYTHONPATH=src python3 -m meta_agent inspect-project .
PYTHONPATH=src python3 -m meta_agent report-project . --output /tmp/meta-agent-report.md
PYTHONPATH=src python3 -m meta_agent list-workflows .
PYTHONPATH=src python3 -m meta_agent explain-workflow workflows/agent-design-review.json
PYTHONPATH=src python3 -m meta_agent run-workflow examples/agents/research-agent/workflows/research-summary.json --format json
PYTHONPATH=src python3 -m meta_agent review examples/agents/research-agent
PYTHONPATH=src python3 -m meta_agent score examples/agents/research-agent --format json
PYTHONPATH=src python3 -m meta_agent propose-memory-candidate examples/data/feedback_events.example.json
```

## Install locally

For local development:

```bash
python3 -m pip install -e .
meta-agent --version
meta-agent validate .
```

## Commands

### `meta-agent init <agent-id>`

Creates a new agent workspace scaffold.

Example:

```bash
meta-agent init research-agent --output-dir examples/agents
meta-agent review examples/agents/research-agent
```

Generated files:

- `agent.yaml`
- `CAPABILITY_MATRIX.md`
- `workflows/read-only-review.json`

The command refuses to overwrite a non-empty target directory unless `--force` is provided.

### `meta-agent validate [path]`

Validates a meta-agent project.

Current checks:

- JSON syntax under `schemas/`, `workflows/`, `templates/`, and `examples/`.
- Required project files.
- Example references between agents, workflows, runs, feedback events, and memory candidates.
- Schema conformity for example agents, workflows, runs, feedback events, and memory candidates using the repository schemas.
- Workflow semantic checks for required fields, valid risk levels, non-empty steps, unique step names, input/output metadata, and evidence policy.
- Markdown local link checks for missing or project-external relative links.
- Basic sensitive-content and old-name patterns.

### `meta-agent inspect-project [path]`

Summarizes project data for agents, workflows, runs, feedback events, and memory candidates.

This command is read-only and is intended for CI summaries or future Agent Ops Panel integrations.

Example:

```bash
meta-agent inspect-project .
meta-agent inspect-project . --format json
```

### `meta-agent report-project [path]`

Generates a project report by combining validation results and project inspection data.

This command is useful for CI artifacts, release readiness checks, or future dashboard summaries.

Example:

```bash
meta-agent report-project .
meta-agent report-project . --format json
meta-agent report-project . --output /tmp/meta-agent-report.md
```

### `meta-agent list-workflows [path]`

Lists workflow specs found under `workflows/` and `examples/`.

Use JSON output for automation:

```bash
meta-agent list-workflows . --format json
```

### `meta-agent explain-workflow <workflow.json>`

Prints a readable explanation of a workflow spec, including steps and evidence policy.

Use JSON output to inspect the raw workflow:

```bash
meta-agent explain-workflow workflows/agent-design-review.json --format json
```

### `meta-agent run-workflow <workflow.json>`

Creates a dry-run run record for a workflow spec.

This command does not execute external actions or model calls. It loads the workflow, records the planned steps, and emits a run-like object for review, CI, or future runtime integration.

Example:

```bash
meta-agent run-workflow examples/agents/research-agent/workflows/research-summary.json \
  --input-json '{"topic":"professional agent design"}' \
  --format json
```

The JSON output includes:

- `run_id`
- `agent_id`
- `workflow_id`
- `status`
- `risk_level`
- `evidence_level`
- `input`
- `warnings`
- `next_steps`
- `dry_run.steps`

### `meta-agent review <agent-path>`

Reviews an agent workspace containing `agent.yaml`.

The current review checks:

- Agent identity, role, maturity, and default risk level.
- Capability matrix presence and evidence/risk columns.
- Workflow specs under `workflows/`.
- Basic workflow fields, steps, and evidence policy.
- Risk alignment between the agent default and workflow specs.
- Maturity, risk, score, strengths, gaps, warnings, and next steps.

Example:

```bash
meta-agent review examples/agents/research-agent
```

### `meta-agent score <agent-path>`

Scores the same review checks and emits a compact result suitable for CI or dashboards.

Example:

```bash
meta-agent score examples/agents/research-agent
meta-agent score examples/agents/research-agent --format json
```

Current score checks:

- `agent_definition` weight 2
- `capability_matrix` weight 2
- `workflow_presence` weight 2
- `workflow_quality` weight 2
- `risk_alignment` weight 1

### `meta-agent propose-memory-candidate <feedback.json>`

Creates a proposed memory candidate from a structured feedback event.

This command does not commit memory. It emits a `status: proposed` candidate that should go through human review before persistence.

Example:

```bash
meta-agent propose-memory-candidate examples/data/feedback_events.example.json
meta-agent propose-memory-candidate examples/data/feedback_events.example.json \
  --feedback-id fb_example_001 \
  --output examples/data/generated-memory-candidate.json
```

### `meta-agent review-memory-candidate <candidate.json>`

Reviews a proposed memory candidate and returns either `status: reviewed` or `status: rejected`.

This command still does not commit memory. It records a review decision so a later persistence layer can decide what to apply.

Example:

```bash
meta-agent review-memory-candidate examples/data/memory_candidates.example.json \
  --decision accept \
  --reviewer reviewer-example \
  --reason "Specific and durable behavior."
```

### `meta-agent commit-memory-candidate <candidate.json>`

Commits an accepted reviewed candidate to a local markdown memory file.

This command refuses candidates that are still `proposed`, `rejected`, or marked as `not_memory`.

Example:

```bash
meta-agent review-memory-candidate examples/data/memory_candidates.example.json \
  --decision accept \
  --reviewer reviewer-example \
  --reason "Specific and durable behavior." \
  --output /tmp/reviewed-candidate.json

meta-agent commit-memory-candidate /tmp/reviewed-candidate.json \
  --output-dir /tmp/meta-agent-memory
```

## Current limitations

- The CLI supports a practical JSON Schema subset, not the full JSON Schema specification.
- `run-workflow` creates dry-run records; it does not execute workflow steps or external actions.
- The CLI only parses simple top-level `agent.yaml` fields.
- The review and score commands are design review helpers, not runtime evaluators.
