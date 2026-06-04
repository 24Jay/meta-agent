from pathlib import Path

from .inspector import inspect_project
from .reviewer import add_check, review_agent, summarize_score
from .validator import validate_project

PUBLIC_DOCS = ["README.md", "LICENSE", "SECURITY.md", "CONTRIBUTING.md", "ROADMAP.md"]
DEFAULT_AGENT_PATH = Path("examples/agents/research-agent")


def _score_percent(score, max_score):
    if not max_score:
        return 0
    return round((score / max_score) * 100)


def _add_path_check(checks, name, root, paths, detail, weight=1):
    missing = [path for path in paths if not (root / path).exists()]
    if missing:
        add_check(checks, name, False, f"Missing: {', '.join(str(path) for path in missing)}.", weight=weight)
    else:
        add_check(checks, name, True, detail, weight=weight)


def _has_files(path, pattern):
    return path.exists() and any(path.rglob(pattern))


def _collect_status_count(inspection, section, field_name, status):
    return inspection.get(section, {}).get(field_name, {}).get(status, 0)


def build_readiness_report(root, agent_path=None, fail_under=None, strict=False):
    root = Path(root).resolve()
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Project path does not exist or is not a directory: {root}")

    checks = []
    blockers = []
    warnings = []
    next_steps = []

    validation = validate_project(root)
    if validation.ok:
        add_check(checks, "project_validation", True, "Project validation passed.", weight=3)
    else:
        detail = f"Project validation failed with {len(validation.errors)} error(s)."
        add_check(checks, "project_validation", False, detail, weight=3)
        blockers.extend(validation.errors)
        next_steps.append("Fix validation errors before publishing, tagging, or operating the project.")

    inspection = inspect_project(root)
    inspection_warnings = inspection.get("warnings", [])
    if inspection_warnings:
        detail = f"Project inspection found {len(inspection_warnings)} warning(s)."
        add_check(checks, "project_inspection", not strict, detail, weight=2)
        warnings.extend(inspection_warnings)
        if strict:
            blockers.extend(inspection_warnings)
        next_steps.append("Resolve inspection warnings or explain why they are acceptable for this release.")
    else:
        add_check(checks, "project_inspection", True, "Project references are internally consistent.", weight=2)

    _add_path_check(
        checks,
        "required_public_docs",
        root,
        [Path(path) for path in PUBLIC_DOCS],
        "Public README, license, security, contribution, and roadmap files are present.",
        weight=2,
    )
    if not checks[-1]["passed"]:
        warnings.append(checks[-1]["detail"])
        next_steps.append("Add the missing public documentation files.")

    _add_path_check(
        checks,
        "ci_workflow",
        root,
        [Path(".github/workflows/ci.yml")],
        "CI workflow is present.",
        weight=1,
    )
    if not checks[-1]["passed"]:
        warnings.append(checks[-1]["detail"])
        next_steps.append("Add a CI workflow that runs validation and tests.")

    if _has_files(root / "tests", "test_*.py"):
        add_check(checks, "tests_present", True, "Python test files are present.", weight=1)
    else:
        add_check(checks, "tests_present", False, "No Python test files found under tests/.", weight=1)
        warnings.append("No Python test files found under tests/.")
        next_steps.append("Add tests for CLI and validation behavior.")

    example_paths = [root / "examples" / "agents", root / "examples" / "data"]
    if all(path.exists() and any(path.iterdir()) for path in example_paths):
        add_check(checks, "examples_present", True, "Example agents and data are present.", weight=1)
    else:
        add_check(checks, "examples_present", False, "Examples are missing agent or data assets.", weight=1)
        warnings.append("Examples are missing agent or data assets.")
        next_steps.append("Add sanitized examples that demonstrate the methodology end to end.")

    selected_agent_path = Path(agent_path) if agent_path else root / DEFAULT_AGENT_PATH
    if not selected_agent_path.is_absolute():
        selected_agent_path = root / selected_agent_path
    agent_review = None
    if selected_agent_path.exists():
        agent_review = review_agent(selected_agent_path)
        add_check(
            checks,
            "agent_review",
            agent_review.get("passed", False),
            f"Agent review score: {agent_review.get('score')}/{agent_review.get('max_score')} for {agent_review.get('agent_id', selected_agent_path.name)}.",
            weight=2,
        )
        if agent_review.get("gaps"):
            warnings.extend(agent_review["gaps"])
            next_steps.extend(agent_review.get("next_steps", []))
    else:
        add_check(checks, "agent_review", False, f"Agent path not found: {selected_agent_path}.", weight=2)
        warnings.append(f"Agent path not found: {selected_agent_path}.")
        next_steps.append("Provide --agent with a valid agent workspace or add the example research-agent.")

    proposed_feedback = _collect_status_count(inspection, "feedback_events", "status", "proposed")
    proposed_memory = _collect_status_count(inspection, "memory_candidates", "status", "proposed")
    if proposed_feedback or proposed_memory:
        detail = f"Found proposed feedback_events={proposed_feedback}, memory_candidates={proposed_memory}."
        add_check(checks, "feedback_memory_state", True, detail, weight=1)
        warnings.append(detail)
        next_steps.append("Review proposed feedback and memory candidates before turning them into durable project state.")
    else:
        add_check(checks, "feedback_memory_state", True, "No proposed feedback or memory candidates require review.", weight=1)

    score, max_score, passed, ratio = summarize_score(checks)
    score_percent = _score_percent(score, max_score)
    threshold_failed = fail_under is not None and score_percent < fail_under

    if threshold_failed:
        warnings.append(f"Readiness score {score_percent} is below fail-under threshold {fail_under}.")
        next_steps.append("Improve readiness checks or lower --fail-under for this context.")

    if blockers:
        status = "blocked"
    elif not passed or threshold_failed:
        status = "needs-work"
    else:
        status = "ready"

    if not next_steps and status == "ready":
        next_steps.append("Keep validation and readiness checks in CI before publishing changes.")

    return {
        "root": str(root),
        "status": status,
        "score": score_percent,
        "raw_score": score,
        "max_score": max_score,
        "score_ratio": ratio,
        "passed": status == "ready",
        "strict": strict,
        "fail_under": fail_under,
        "checks": checks,
        "blockers": blockers,
        "warnings": warnings,
        "next_steps": list(dict.fromkeys(next_steps)),
        "validation": {
            "ok": validation.ok,
            "errors": validation.errors,
            "json_count": validation.json_count,
        },
        "inspection": inspection,
        "agent_review": agent_review,
    }


def format_readiness_text(report):
    lines = [
        "# meta-agent Readiness Report",
        "",
        f"root: {report['root']}",
        f"status: {report['status']}",
        f"score: {report['score']}/100",
        f"raw_score: {report['raw_score']}/{report['max_score']}",
        f"strict: {str(report['strict']).lower()}",
    ]
    if report.get("fail_under") is not None:
        lines.append(f"fail_under: {report['fail_under']}")

    lines.extend(["", "checks:"])
    for check in report["checks"]:
        status = "PASS" if check.get("passed") else "FAIL"
        lines.append(f"- {status} {check.get('name')}: {check.get('detail')}")

    lines.extend(["", "blockers:"])
    if report["blockers"]:
        lines.extend(f"- {blocker}" for blocker in report["blockers"])
    else:
        lines.append("- none")

    lines.extend(["", "warnings:"])
    if report["warnings"]:
        lines.extend(f"- {warning}" for warning in report["warnings"])
    else:
        lines.append("- none")

    lines.extend(["", "next_steps:"])
    if report["next_steps"]:
        lines.extend(f"- {step}" for step in report["next_steps"])
    else:
        lines.append("- none")

    return "\n".join(lines) + "\n"
