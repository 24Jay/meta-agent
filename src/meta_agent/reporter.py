from pathlib import Path

from .inspector import inspect_project
from .validator import validate_project


def build_project_report(root):
    root = Path(root).resolve()
    validation = validate_project(root)
    inspection = inspect_project(root)
    next_steps = []

    if validation.ok:
        next_steps.append("Keep project validation in CI before publishing changes.")
    else:
        next_steps.append("Fix validation errors before publishing or tagging a release.")

    if inspection["memory_candidates"].get("status", {}).get("proposed"):
        next_steps.append("Review proposed memory candidates before committing durable memory.")

    if inspection["feedback_events"].get("status", {}).get("proposed"):
        next_steps.append("Process proposed feedback events into reviewed candidates or reject them.")

    if not inspection["warnings"] and validation.ok:
        next_steps.append("Project is ready for a seed repository review.")

    return {
        "root": str(root),
        "validation": {
            "ok": validation.ok,
            "errors": validation.errors,
            "json_count": validation.json_count,
        },
        "inspection": inspection,
        "next_steps": next_steps,
    }


def format_project_report_markdown(report):
    validation = report["validation"]
    inspection = report["inspection"]
    lines = [
        "# meta-agent Project Report",
        "",
        f"- Root: `{report['root']}`",
        f"- Validation: `{'passed' if validation['ok'] else 'failed'}`",
        f"- JSON files validated: `{validation['json_count']}`",
        "",
        "## Counts",
        "",
    ]

    for key, value in inspection["counts"].items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Validation Errors", ""])
    if validation["errors"]:
        lines.extend(f"- {error}" for error in validation["errors"])
    else:
        lines.append("- None.")

    lines.extend(["", "## Warnings", ""])
    if inspection["warnings"]:
        lines.extend(f"- {warning}" for warning in inspection["warnings"])
    else:
        lines.append("- None.")

    for section in ["agents", "workflows", "runs", "feedback_events", "memory_candidates"]:
        lines.extend(["", f"## {section}", ""])
        for field_name, counts in inspection[section].items():
            rendered = ", ".join(f"{key}={value}" for key, value in counts.items()) or "none"
            lines.append(f"- {field_name}: {rendered}")

    lines.extend(["", "## Next Steps", ""])
    if report["next_steps"]:
        lines.extend(f"- {step}" for step in report["next_steps"])
    else:
        lines.append("- None.")

    return "\n".join(lines) + "\n"
