# Workflow Authoring Guide

Workflows describe repeatable SOPs for professional agents. They should be reviewable before they become executable automation.

A workflow is a JSON document with explicit purpose, risk, steps, inputs, outputs, and evidence policy.

## Minimal workflow

```json
{
  "name": "research-summary",
  "version": "0.1.0",
  "description": "Summarize public or sanitized references with evidence separated from recommendations.",
  "risk_level": "read_only",
  "owner_skill": "research-agent",
  "inputs": [
    { "name": "topic", "type": "string", "required": true, "description": "Research topic." }
  ],
  "outputs": [
    { "name": "summary_report", "type": "markdown", "description": "Summary report." }
  ],
  "steps": [
    { "name": "confirm_source_boundary", "description": "Confirm source boundary.", "on_failure": "block" },
    { "name": "emit_summary", "description": "Write the summary.", "on_failure": "block" }
  ],
  "evidence_policy": {
    "must_include": ["topic", "evidence", "recommendations", "known_limitations"],
    "forbid_claims_when_insufficient": ["claim_exhaustive_coverage"]
  }
}
```

## Required fields

The project validator requires:

- `name`
- `version`
- `description`
- `risk_level`
- `steps`
- `evidence_policy`

## Risk levels

Allowed values:

- `read_only`: inspection, analysis, local validation, or documentation-only output.
- `review_required`: output may influence future behavior and should be reviewed before persistence.
- `approval_required`: action may affect external systems, production state, users, infrastructure, or publication.
- `blocked`: action is intentionally unsupported.

Start new workflows as `read_only` unless they clearly require review or approval.

## Steps

Each step should include:

- `name`: stable identifier.
- `description`: what the step checks or produces.
- `on_failure`: optional failure behavior.

Allowed `on_failure` values:

- `block`
- `continue_with_warning`
- `await_human`
- `skip`

Step names must be unique within one workflow.

## Inputs and outputs

Inputs and outputs are optional, but when present each item should include:

- `name`
- `type`
- `description`

Names should be stable because future runtime and review tools may refer to them.

## Evidence policy

Every workflow should include an `evidence_policy` object.

Recommended fields:

- `must_include`: evidence fields that output reports must include.
- `forbid_claims_when_insufficient`: claims the agent must not make without stronger evidence.

Examples:

```json
{
  "must_include": ["agent_path", "strengths", "gaps", "risk_level", "next_steps"],
  "forbid_claims_when_insufficient": ["claim_production_ready_without_run_records"]
}
```

## Common validation failures

- Missing `evidence_policy`.
- Empty `steps`.
- Invalid `risk_level`.
- Duplicate step names.
- Input or output item missing `name`, `type`, or `description`.
- Invalid `on_failure` value.

Run:

```bash
PYTHONPATH=src python3 -m meta_agent validate .
```

## Design guidance

Prefer small read-only workflows first. Add review-required and approval-required workflows only after the evidence and human approval boundary is clear.
