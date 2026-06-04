import json
from pathlib import Path


RISK_ORDER = ["read_only", "review_required", "approval_required", "blocked"]


def parse_simple_yaml(path):
    values = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"\'')
    return values


def load_json_files(path):
    items = []
    if not path.exists():
        return items
    for file_path in sorted(path.rglob("*.json")):
        try:
            with file_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            items.append((file_path, data))
        except Exception as exc:
            items.append((file_path, {"_load_error": str(exc)}))
    return items


def risk_index(risk_level):
    try:
        return RISK_ORDER.index(risk_level)
    except ValueError:
        return len(RISK_ORDER)


def add_check(checks, name, passed, detail, weight=1):
    checks.append({
        "name": name,
        "passed": bool(passed),
        "detail": detail,
        "weight": weight,
        "score": weight if passed else 0,
    })


def summarize_score(checks):
    score = sum(check["score"] for check in checks)
    max_score = sum(check["weight"] for check in checks)
    passed = score == max_score
    ratio = score / max_score if max_score else 0
    return score, max_score, passed, ratio


def review_agent(agent_path):
    agent_path = Path(agent_path).resolve()
    strengths = []
    gaps = []
    warnings = []
    next_steps = []
    checks = []

    agent_file = agent_path / "agent.yaml"
    capability_file = agent_path / "CAPABILITY_MATRIX.md"
    workflow_dir = agent_path / "workflows"

    if not agent_file.exists():
        add_check(checks, "agent_definition", False, "Missing agent.yaml.", weight=2)
        score, max_score, passed, ratio = summarize_score(checks)
        return {
            "agent_path": str(agent_path),
            "maturity_level": "L0",
            "risk_level": "blocked",
            "score": score,
            "max_score": max_score,
            "score_ratio": ratio,
            "passed": passed,
            "checks": checks,
            "strengths": [],
            "gaps": ["Missing agent.yaml."],
            "warnings": [],
            "next_steps": ["Create an agent definition from templates/AGENT.template.yaml."],
        }

    agent = parse_simple_yaml(agent_file)
    agent_id = agent.get("id") or agent.get("agent_id") or agent_path.name
    maturity_level = agent.get("maturity_level", "unknown")
    default_risk_level = agent.get("default_risk_level", "blocked")

    required_agent_fields = ["id", "name", "role", "maturity_level", "default_risk_level"]
    missing_agent_fields = [field for field in required_agent_fields if not agent.get(field)]
    if missing_agent_fields:
        detail = f"agent.yaml is missing fields: {', '.join(missing_agent_fields)}."
        gaps.append(detail)
        add_check(checks, "agent_definition", False, detail, weight=2)
    else:
        detail = "Agent definition includes identity, role, maturity, and default risk level."
        strengths.append(detail)
        add_check(checks, "agent_definition", True, detail, weight=2)

    if capability_file.exists():
        capability_text = capability_file.read_text(encoding="utf-8", errors="ignore")
        if "Evidence Level" in capability_text and "Risk Level" in capability_text:
            detail = "Capability matrix includes evidence and risk boundaries."
            strengths.append(detail)
            add_check(checks, "capability_matrix", True, detail, weight=2)
        else:
            detail = "Capability matrix exists but does not clearly include evidence and risk columns."
            gaps.append(detail)
            add_check(checks, "capability_matrix", False, detail, weight=2)
    else:
        detail = "Missing CAPABILITY_MATRIX.md."
        gaps.append(detail)
        add_check(checks, "capability_matrix", False, detail, weight=2)
        next_steps.append("Add a capability matrix with supported/proposed/unsupported capabilities.")

    workflow_files = load_json_files(workflow_dir)
    if workflow_files:
        detail = f"Found {len(workflow_files)} workflow spec(s)."
        strengths.append(detail)
        add_check(checks, "workflow_presence", True, detail, weight=2)
    else:
        detail = "No workflow specs found under workflows/."
        gaps.append(detail)
        add_check(checks, "workflow_presence", False, detail, weight=2)
        next_steps.append("Add at least one read-only workflow spec.")

    workflow_quality_errors = []
    max_workflow_risk = default_risk_level
    for workflow_path, workflow in workflow_files:
        relative_name = workflow_path.relative_to(agent_path)
        if "_load_error" in workflow:
            detail = f"Workflow {relative_name} failed to load: {workflow['_load_error']}."
            gaps.append(detail)
            workflow_quality_errors.append(detail)
            continue
        for field in ["name", "version", "description", "risk_level", "steps"]:
            if field not in workflow:
                detail = f"Workflow {relative_name} is missing required field: {field}."
                gaps.append(detail)
                workflow_quality_errors.append(detail)
        steps = workflow.get("steps", [])
        if not steps:
            detail = f"Workflow {relative_name} has no steps."
            gaps.append(detail)
            workflow_quality_errors.append(detail)
        if not workflow.get("evidence_policy"):
            detail = f"Workflow {relative_name} has no evidence_policy."
            gaps.append(detail)
            workflow_quality_errors.append(detail)
        workflow_risk = workflow.get("risk_level", "blocked")
        if risk_index(workflow_risk) > risk_index(max_workflow_risk):
            max_workflow_risk = workflow_risk

    if workflow_files:
        if workflow_quality_errors:
            add_check(checks, "workflow_quality", False, f"Found {len(workflow_quality_errors)} workflow quality issue(s).", weight=2)
        else:
            add_check(checks, "workflow_quality", True, "Workflow specs include required fields, steps, and evidence policy.", weight=2)

    if risk_index(max_workflow_risk) > risk_index(default_risk_level):
        warnings.append("At least one workflow has a higher risk level than the agent default.")
        add_check(checks, "risk_alignment", False, "At least one workflow has a higher risk level than the agent default.", weight=1)
    else:
        add_check(checks, "risk_alignment", True, "Workflow risk levels do not exceed the agent default risk boundary.", weight=1)

    if not gaps:
        next_steps.append("Run the workflow manually and record a run entry before adding automation.")
    if workflow_files and capability_file.exists():
        next_steps.append("Collect human feedback and convert durable lessons into reviewed memory candidates.")

    if gaps:
        computed_maturity = "L1" if strengths else "L0"
    elif workflow_files and capability_file.exists():
        computed_maturity = maturity_level if maturity_level != "unknown" else "L2"
    else:
        computed_maturity = "L1"

    score, max_score, passed, ratio = summarize_score(checks)

    return {
        "agent_id": agent_id,
        "agent_path": str(agent_path),
        "maturity_level": computed_maturity,
        "declared_maturity_level": maturity_level,
        "risk_level": max_workflow_risk,
        "score": score,
        "max_score": max_score,
        "score_ratio": ratio,
        "passed": passed,
        "checks": checks,
        "strengths": strengths,
        "gaps": gaps,
        "warnings": warnings,
        "next_steps": next_steps,
    }


def format_review_markdown(review):
    lines = [
        f"# Agent Review: {review.get('agent_id', 'unknown')}",
        "",
        f"- Agent path: `{review['agent_path']}`",
        f"- Maturity level: `{review['maturity_level']}`",
        f"- Risk level: `{review['risk_level']}`",
        f"- Score: `{review.get('score', 0)}/{review.get('max_score', 0)}`",
        f"- Passed: `{str(review.get('passed', False)).lower()}`",
    ]
    if review.get("declared_maturity_level"):
        lines.append(f"- Declared maturity level: `{review['declared_maturity_level']}`")

    for title, key in [("Strengths", "strengths"), ("Gaps", "gaps"), ("Warnings", "warnings"), ("Next Steps", "next_steps")]:
        lines.extend(["", f"## {title}", ""])
        values = review.get(key) or []
        if values:
            lines.extend(f"- {value}" for value in values)
        else:
            lines.append("- None.")

    return "\n".join(lines) + "\n"
