import json
from datetime import datetime, timezone
from pathlib import Path


def load_workflow(workflow_path):
    workflow_path = Path(workflow_path).resolve()
    with workflow_path.open("r", encoding="utf-8") as handle:
        workflow = json.load(handle)
    return workflow_path, workflow


def workflow_id_from_path(workflow_path, workflow):
    parent = workflow_path.parent.parent.name if workflow_path.parent.name == "workflows" else None
    name = workflow.get("name") or workflow_path.stem
    return f"{parent}:{name}" if parent else name


def infer_agent_id(workflow_path, workflow):
    if workflow.get("owner_skill"):
        return workflow["owner_skill"]
    if workflow_path.parent.name == "workflows":
        return workflow_path.parent.parent.name
    return "meta-agent"


def create_run_record(workflow_path, inputs=None, output_path=None):
    workflow_path, workflow = load_workflow(workflow_path)
    inputs = inputs or {}
    warnings = []
    next_steps = []

    steps = workflow.get("steps", [])
    if not steps:
        warnings.append("Workflow has no steps; dry-run cannot confirm execution sequence.")
    else:
        next_steps.append("Review the dry-run step plan before implementing executable runtime behavior.")

    if workflow.get("risk_level") != "read_only":
        next_steps.append("Require human review before executing or persisting effects from this workflow.")

    run_id = "run_" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return {
        "run_id": run_id,
        "task_id": None,
        "agent_id": infer_agent_id(workflow_path, workflow),
        "workflow_id": workflow_id_from_path(workflow_path, workflow),
        "status": "success",
        "risk_level": workflow.get("risk_level", "blocked"),
        "evidence_level": "dry_run",
        "input": inputs,
        "output_path": output_path,
        "warnings": warnings,
        "next_steps": next_steps,
        "dry_run": {
            "workflow_path": str(workflow_path),
            "workflow_name": workflow.get("name"),
            "step_count": len(steps),
            "steps": [
                {
                    "name": step.get("name"),
                    "description": step.get("description"),
                    "on_failure": step.get("on_failure"),
                }
                for step in steps
            ],
        },
    }


def format_run_record_text(record):
    lines = [
        f"run_id: {record['run_id']}",
        f"agent_id: {record['agent_id']}",
        f"workflow_id: {record['workflow_id']}",
        f"status: {record['status']}",
        f"risk_level: {record['risk_level']}",
        f"evidence_level: {record['evidence_level']}",
        "steps:",
    ]
    for index, step in enumerate(record["dry_run"]["steps"], start=1):
        lines.append(f"{index}. {step.get('name')} — {step.get('description')}")
    if record.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in record["warnings"])
    if record.get("next_steps"):
        lines.append("next_steps:")
        lines.extend(f"- {step}" for step in record["next_steps"])
    return "\n".join(lines) + "\n"
