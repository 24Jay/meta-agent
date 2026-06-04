import json
from collections import Counter
from pathlib import Path


DATA_FILES = {
    "agents": "examples/data/agents.example.json",
    "workflows": "examples/data/workflows.example.json",
    "runs": "examples/data/runs.example.json",
    "feedback_events": "examples/data/feedback_events.example.json",
    "memory_candidates": "examples/data/memory_candidates.example.json",
}


def load_json_array(root, relative_path):
    path = root / relative_path
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data if isinstance(data, list) else [data]


def count_by(items, field_name):
    return dict(sorted(Counter(item.get(field_name, "unknown") for item in items).items()))


def inspect_project(root):
    root = Path(root).resolve()
    agents = load_json_array(root, DATA_FILES["agents"])
    workflows = load_json_array(root, DATA_FILES["workflows"])
    runs = load_json_array(root, DATA_FILES["runs"])
    feedback_events = load_json_array(root, DATA_FILES["feedback_events"])
    memory_candidates = load_json_array(root, DATA_FILES["memory_candidates"])

    agent_ids = {agent.get("agent_id") for agent in agents}
    workflow_ids = {workflow.get("workflow_id") for workflow in workflows}
    referenced_agents = {workflow.get("agent_id") for workflow in workflows} | {run.get("agent_id") for run in runs} | {event.get("agent_id") for event in feedback_events}
    referenced_workflows = {run.get("workflow_id") for run in runs if run.get("workflow_id")}

    warnings = []
    missing_agents = sorted(value for value in referenced_agents if value and value not in agent_ids)
    missing_workflows = sorted(value for value in referenced_workflows if value and value not in workflow_ids)
    if missing_agents:
        warnings.append(f"Unknown referenced agents: {', '.join(missing_agents)}")
    if missing_workflows:
        warnings.append(f"Unknown referenced workflows: {', '.join(missing_workflows)}")

    return {
        "root": str(root),
        "counts": {
            "agents": len(agents),
            "workflows": len(workflows),
            "runs": len(runs),
            "feedback_events": len(feedback_events),
            "memory_candidates": len(memory_candidates),
        },
        "agents": {
            "status": count_by(agents, "status"),
            "maturity_level": count_by(agents, "maturity_level"),
            "default_risk_level": count_by(agents, "default_risk_level"),
        },
        "workflows": {
            "risk_level": count_by(workflows, "risk_level"),
            "status": count_by(workflows, "status"),
        },
        "runs": {
            "status": count_by(runs, "status"),
            "risk_level": count_by(runs, "risk_level"),
            "evidence_level": count_by(runs, "evidence_level"),
        },
        "feedback_events": {
            "status": count_by(feedback_events, "status"),
            "risk_level": count_by(feedback_events, "risk_level"),
            "suggested_destination": count_by(feedback_events, "suggested_destination"),
        },
        "memory_candidates": {
            "status": count_by(memory_candidates, "status"),
            "risk_level": count_by(memory_candidates, "risk_level"),
            "candidate_type": count_by(memory_candidates, "candidate_type"),
        },
        "warnings": warnings,
    }


def format_inspection_text(summary):
    lines = [
        f"root: {summary['root']}",
        "counts:",
    ]
    for key, value in summary["counts"].items():
        lines.append(f"- {key}: {value}")

    for section in ["agents", "workflows", "runs", "feedback_events", "memory_candidates"]:
        lines.append(f"{section}:")
        for field_name, counts in summary[section].items():
            rendered = ", ".join(f"{key}={value}" for key, value in counts.items()) or "none"
            lines.append(f"- {field_name}: {rendered}")

    if summary["warnings"]:
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in summary["warnings"])
    else:
        lines.append("warnings: none")

    return "\n".join(lines) + "\n"
