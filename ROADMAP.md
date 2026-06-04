# Roadmap

meta-agent is methodology-first. The roadmap prioritizes clear agent design, reviewability, evidence/risk boundaries, and human feedback loops before heavy runtime automation.

## v0.0.x — Open-source seed

Goal: make the project understandable, safe to publish, and useful as a reference package.

- Stabilize the repository identity around `meta-agent`.
- Keep the core provider-agnostic.
- Maintain sanitized docs, schemas, workflows, templates, and examples.
- Provide a minimal validation script for JSON-based assets.
- Document what belongs in open source and what must stay in private downstream projects.
- Add a clear quickstart and contribution path.

Exit criteria:

- New readers can understand the project in under five minutes.
- All JSON schemas, workflows, templates, and examples pass local validation.
- Security and sanitization guidance is visible from the repository root.

## v0.1 — Usable methodology toolkit

Goal: let users apply meta-agent to design and review a professional agent without writing custom code.

Planned capabilities:

- End-to-end example: define an agent, review its design, run a workflow checklist, record feedback, and produce a memory candidate.
- Stronger README quickstart.
- Validation command or script for repository assets.
- Agent design review checklist.
- Workflow authoring guide.
- Capability matrix guide.
- Evidence/risk policy examples.
- MemoryOps example with human review before persistence.

Current progress:

- `meta-agent init` creates a minimal agent workspace scaffold.
- `meta-agent validate` exists as a read-only project validator.
- `meta-agent inspect-project` summarizes agents, workflows, runs, feedback events, and memory candidates for CI or dashboard use.
- `meta-agent report-project` generates Markdown/JSON project reports from validation and inspection data.
- `meta-agent list-workflows` lists workflow specs.
- `meta-agent explain-workflow` explains a workflow spec.
- `meta-agent run-workflow` creates dry-run run records for workflow specs without external side effects.
- `meta-agent review` performs a lightweight design review for an agent workspace.
- `meta-agent score` emits structured scoring output for CI or dashboards.
- `meta-agent propose-memory-candidate` creates proposed memory candidates from feedback events without committing memory.
- `meta-agent review-memory-candidate` records accept/reject review decisions without committing memory.
- `meta-agent commit-memory-candidate` writes accepted reviewed candidates to local markdown and refuses proposed/rejected/not_memory candidates.
- `tests/test_cli.py` covers the basic CLI paths.
- `.github/workflows/ci.yml` runs compile, unit tests, project validation, and CLI validation.
- Schema conformity validation checks example agents, workflows, runs, feedback events, and memory candidates against repository schemas.
- Workflow semantic validation checks required fields, risk levels, steps, input/output metadata, and evidence policy.
- Markdown local link validation catches missing or project-external relative links.
- `docs/WORKFLOW_AUTHORING.md` documents workflow authoring rules and common validation failures.

Possible CLI shape:

```bash
meta-agent validate .
meta-agent review examples/agents/research-agent
meta-agent explain-workflow workflows/agent-design-review.json
```

Exit criteria:

- A user can clone the repository and follow one complete example.
- Existing examples are validated by a repeatable command.
- The project is clearly differentiated from orchestration-first agent frameworks.

## v0.2 — Reference operations layer

Goal: demonstrate how professional agents can be managed, reviewed, and improved over time.

Planned capabilities:

- Agent Ops Panel reference implementation or lightweight demo.
- Run records, feedback events, approvals, knowledge sources, and memory candidates displayed together.
- Example feedback review flow.
- Example approval policy flow for high-risk actions.
- Import/export format for local JSON stores.

Exit criteria:

- Users can see how methodology artifacts become an operational loop.
- The panel remains a reference implementation, not the core identity of the project.
- High-risk actions remain gated by explicit human approval.

## v0.3 — Runtime interfaces and adapters

Goal: define clean interfaces for running agent workflows across providers and local tools.

Planned capabilities:

- Minimal runtime interface for loading agent definitions and workflow specs.
- Provider adapter interface for LLMs, CLI agents, or local workflow engines.
- Connector interface for tools and external systems.
- Run output schema enforcement.
- Evidence/risk checks during workflow execution.

Exit criteria:

- The framework can support multiple providers without assuming one model vendor.
- Runtime behavior remains auditable and reviewable.
- Human-in-the-loop boundaries are enforceable, not just documented.

## Later directions

Potential future work:

- Package publishing through npm or PyPI.
- Markdown and link validation.
- Schema-based documentation generation.
- Agent maturity scoring.
- Workflow marketplace or template gallery.
- Integration guides for existing agent frameworks.
- Evaluation datasets for agent design quality.

## Non-goals

meta-agent should not become:

- A model-provider wrapper.
- A black-box autonomous agent runner.
- A tool for bypassing human approval.
- A storage location for private run logs, customer data, secrets, or internal system details.
- A domain-specific project that leaks private downstream business logic.
