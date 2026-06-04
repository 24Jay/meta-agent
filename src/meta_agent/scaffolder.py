import json
import re
from pathlib import Path


def slugify(value):
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9_-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "example-agent"


def titleize(agent_id):
    return " ".join(part.capitalize() for part in re.split(r"[-_]+", agent_id) if part) or "Example Agent"


def create_agent(agent_id, output_dir, role=None, force=False):
    agent_id = slugify(agent_id)
    output_dir = Path(output_dir).resolve()
    agent_dir = output_dir / agent_id

    if agent_dir.exists() and any(agent_dir.iterdir()) and not force:
        raise FileExistsError(f"Refusing to overwrite non-empty directory: {agent_dir}")

    workflows_dir = agent_dir / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)

    name = titleize(agent_id)
    role = role or "A professional agent with explicit capability, evidence, and risk boundaries."

    (agent_dir / "agent.yaml").write_text(
        "\n".join([
            f"id: {agent_id}",
            f"name: {name}",
            f"role: {role}",
            "maturity_level: L1",
            "default_provider: mock",
            "default_risk_level: read_only",
            "knowledge_index: ./knowledge/README.md",
            "workflow_dir: ./workflows",
            "",
        ]),
        encoding="utf-8",
    )

    (agent_dir / "CAPABILITY_MATRIX.md").write_text(
        f"# {name} Capability Matrix\n\n"
        "| Capability | Status | Evidence Level | Risk Level | Human Review |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| Describe the agent role | supported | documented | read_only | optional |\n"
        "| Run read-only workflow checklist | proposed | checklist | read_only | optional |\n"
        "| Update memory or knowledge | proposed | reviewed_feedback | review_required | required |\n"
        "| Execute external side effects | unsupported | none | blocked | required before implementation |\n\n"
        "## Notes\n\n"
        "- Start with read-only workflows.\n"
        "- Keep evidence and recommendations separate.\n"
        "- Do not commit memory or knowledge changes without review.\n",
        encoding="utf-8",
    )

    workflow = {
        "name": "read-only-review",
        "version": "0.1.0",
        "description": "Review the agent workspace without external side effects.",
        "risk_level": "read_only",
        "owner_skill": agent_id,
        "inputs": [
            {"name": "agent_path", "type": "path", "required": True, "description": "Path to the agent workspace."}
        ],
        "outputs": [
            {"name": "review_report", "type": "markdown", "description": "Review report with strengths, gaps, and next steps."}
        ],
        "steps": [
            {"name": "inspect_agent_definition", "description": "Inspect agent.yaml.", "on_failure": "block"},
            {"name": "inspect_capabilities", "description": "Inspect capability matrix.", "on_failure": "continue_with_warning"},
            {"name": "inspect_workflows", "description": "Inspect workflow specs.", "on_failure": "continue_with_warning"},
            {"name": "emit_review", "description": "Emit a read-only review report.", "on_failure": "block"},
        ],
        "evidence_policy": {
            "must_include": ["agent_path", "strengths", "gaps", "risk_level", "next_steps"],
            "forbid_claims_when_insufficient": ["claim_production_ready_without_run_records"],
        },
    }
    (workflows_dir / "read-only-review.json").write_text(
        json.dumps(workflow, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return agent_dir
