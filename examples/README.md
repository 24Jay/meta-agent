# End-to-End Example

This walkthrough shows how meta-agent assets fit together for a sanitized `research-agent`.

The goal is not to run an autonomous agent. The goal is to make the agent design reviewable before runtime automation is added.

## 1. Define the agent

Start with the agent definition:

- `examples/agents/research-agent/agent.yaml`
- `examples/data/agents.example.json`

The example agent is read-only by default and is limited to public or sanitized research tasks.

## 2. Declare capabilities and boundaries

Review the capability matrix:

- `examples/agents/research-agent/CAPABILITY_MATRIX.md`

The matrix makes supported, proposed, unsupported, evidence, risk, and human-review boundaries explicit.

Key design rule:

```text
Recommendations are allowed, but they should separate evidence from interpretation.
Memory updates are proposed, not automatically committed.
```

## 3. Attach a workflow

The example workflow index is:

- `examples/data/workflows.example.json`

It points to a read-only `research-summary` workflow. The reusable workflow design pattern is represented in:

- `workflows/agent-design-review.json`
- `workflows/agent-feedback-loop.json`
- `workflows/memory-candidate-extraction.json`
- `workflows/memory-review-and-commit.json`

## 4. Produce a run record

A sample run record is stored in:

- `examples/data/runs.example.json`

It records:

- `agent_id`
- `workflow_id`
- `status`
- `risk_level`
- `evidence_level`
- `input`
- `output_path`
- `warnings`
- `next_steps`

The example output is:

- `examples/reports/research-summary.md`

## 5. Collect human feedback

A reviewer praises the report for separating evidence from recommendations:

- `examples/data/feedback_events.example.json`

The feedback event is still only `proposed`. It does not directly update memory or knowledge.

## 6. Extract a memory candidate

The feedback becomes a proposed memory candidate:

- `examples/data/memory_candidates.example.json`

You can generate the same shape from the feedback event:

```bash
PYTHONPATH=src python3 -m meta_agent propose-memory-candidate examples/data/feedback_events.example.json
```

The candidate says future research reports should keep separate `Evidence` and `Recommendations` sections.

## 7. Require review before persistence

The memory candidate remains `proposed` until a human review workflow accepts or rejects it.

Relevant workflow:

- `workflows/memory-review-and-commit.json`

You can record a review decision without committing memory:

```bash
PYTHONPATH=src python3 -m meta_agent review-memory-candidate examples/data/memory_candidates.example.json \
  --decision accept \
  --reviewer reviewer-example \
  --reason "Specific and durable behavior." \
  --output /tmp/reviewed-candidate.json

PYTHONPATH=src python3 -m meta_agent commit-memory-candidate /tmp/reviewed-candidate.json \
  --output-dir /tmp/meta-agent-memory
```

The commit command writes local markdown only after review. It refuses `proposed`, `rejected`, or `not_memory` candidates.

This is the core MemoryOps pattern:

```text
raw output / feedback
  → summarized evidence
  → proposed candidate
  → human review
  → memory / knowledge / workflow / roadmap update
```

## 8. Validate and review the example assets

Run:

```bash
PYTHONPATH=src python3 -m meta_agent validate .
PYTHONPATH=src python3 -m meta_agent list-workflows .
PYTHONPATH=src python3 -m meta_agent review examples/agents/research-agent
```

The validator checks JSON syntax, required files, example references, and a small set of sensitive-content patterns. The review command checks the example agent definition, capability matrix, workflow specs, and evidence/risk boundaries.

## What this example demonstrates

- Agent design is explicit.
- Capabilities are reviewable.
- Risk and evidence are tracked.
- Feedback is captured as a structured event.
- Memory changes require review.
- Runtime automation can be added later without losing governance boundaries.
