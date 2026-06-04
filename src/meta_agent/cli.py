import argparse
import json
import sys
from pathlib import Path

from .inspector import format_inspection_text, inspect_project
from .memory_ops import commit_candidate_to_markdown, feedback_to_memory_candidate, load_feedback_event, load_memory_candidate, review_memory_candidate, write_candidate
from .readiness import build_readiness_report, format_readiness_text
from .reporter import build_project_report, format_project_report_markdown
from .reviewer import format_review_markdown, review_agent
from .runner import create_run_record, format_run_record_text
from .scaffolder import create_agent
from .validator import validate_project


def command_init(args):
    try:
        agent_dir = create_agent(args.agent_id, args.output_dir, role=args.role, force=args.force)
    except FileExistsError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    print(f"Created agent workspace: {agent_dir}")
    print(f"Next: meta-agent review {agent_dir}")
    return 0


def command_validate(args):
    result = validate_project(args.path)
    output = "\n".join(result.lines())
    stream = sys.stdout if result.ok else sys.stderr
    print(output, file=stream)
    return 0 if result.ok else 1


def iter_workflow_files(root):
    for directory in ["workflows", "examples"]:
        path = root / directory
        if path.exists():
            yield from sorted(path.rglob("*.json"))


def command_report_project(args):
    report = build_project_report(args.path)
    if args.format == "json":
        output = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    else:
        output = format_project_report_markdown(report)

    if args.output:
        output_path = Path(args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding="utf-8")
        print(f"Wrote project report: {output_path}", file=sys.stderr)

    print(output, end="")
    return 0 if report["validation"]["ok"] and not report["inspection"].get("warnings") else 2


def command_inspect_project(args):
    summary = inspect_project(args.path)
    if args.format == "json":
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(format_inspection_text(summary), end="")
    return 0 if not summary.get("warnings") else 2


def command_readiness(args):
    try:
        report = build_readiness_report(args.path, agent_path=args.agent, fail_under=args.fail_under, strict=args.strict)
    except Exception as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(format_readiness_text(report), end="")
    return 0 if report.get("passed") else 2


def command_list_workflows(args):
    root = Path(args.path).resolve()
    workflows = []
    for path in iter_workflow_files(root):
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except Exception:
            continue
        if "steps" not in data or "name" not in data:
            continue
        workflows.append({
            "path": str(path.relative_to(root)),
            "name": data.get("name"),
            "version": data.get("version"),
            "risk_level": data.get("risk_level"),
            "description": data.get("description"),
        })

    if args.format == "json":
        print(json.dumps(workflows, indent=2, ensure_ascii=False))
    else:
        for workflow in workflows:
            print(f"{workflow['path']} | {workflow['name']} | {workflow.get('risk_level')} | {workflow.get('description')}")
    return 0


def parse_input_json(value):
    if not value:
        return {}
    path = Path(value)
    if path.exists():
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    return json.loads(value)


def command_explain_workflow(args):
    path = Path(args.workflow_path).resolve()
    with path.open("r", encoding="utf-8") as handle:
        workflow = json.load(handle)

    if args.format == "json":
        print(json.dumps(workflow, indent=2, ensure_ascii=False))
        return 0

    print(f"# Workflow: {workflow.get('name', path.stem)}")
    print()
    print(f"- Path: `{path}`")
    print(f"- Version: `{workflow.get('version', 'unknown')}`")
    print(f"- Risk level: `{workflow.get('risk_level', 'unknown')}`")
    print(f"- Description: {workflow.get('description', '')}")
    print()
    print("## Steps")
    print()
    for index, step in enumerate(workflow.get("steps", []), start=1):
        print(f"{index}. `{step.get('name', 'unnamed')}` — {step.get('description', '')}")
    evidence_policy = workflow.get("evidence_policy")
    if evidence_policy:
        print()
        print("## Evidence Policy")
        print()
        print(json.dumps(evidence_policy, indent=2, ensure_ascii=False))
    return 0


def command_run_workflow(args):
    try:
        inputs = parse_input_json(args.input_json)
    except Exception as exc:
        print(f"FAIL invalid input JSON: {exc}", file=sys.stderr)
        return 1
    record = create_run_record(args.workflow_path, inputs=inputs, output_path=args.output_path)
    if args.format == "json":
        print(json.dumps(record, indent=2, ensure_ascii=False))
    else:
        print(format_run_record_text(record), end="")
    return 0


def command_review(args):
    review = review_agent(args.agent_path)
    if args.format == "json":
        print(json.dumps(review, indent=2, ensure_ascii=False))
    else:
        print(format_review_markdown(review), end="")
    return 0 if not review.get("gaps") else 2


def command_propose_memory_candidate(args):
    try:
        event = load_feedback_event(args.feedback_path, feedback_id=args.feedback_id)
        candidate = feedback_to_memory_candidate(event)
    except Exception as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1

    if args.output:
        output_path = write_candidate(candidate, args.output)
        print(f"Wrote memory candidate: {output_path}", file=sys.stderr)

    print(json.dumps(candidate, indent=2, ensure_ascii=False))
    return 0


def command_review_memory_candidate(args):
    try:
        candidate = load_memory_candidate(args.candidate_path)
        reviewed = review_memory_candidate(candidate, args.decision, args.reviewer, args.reason)
    except Exception as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1

    if args.output:
        output_path = write_candidate(reviewed, args.output)
        print(f"Wrote reviewed memory candidate: {output_path}", file=sys.stderr)

    print(json.dumps(reviewed, indent=2, ensure_ascii=False))
    return 0 if reviewed.get("status") == "reviewed" else 2


def command_commit_memory_candidate(args):
    try:
        candidate = load_memory_candidate(args.candidate_path)
        output_path = commit_candidate_to_markdown(candidate, args.output_dir)
    except Exception as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    print(f"Committed memory candidate: {output_path}")
    return 0


def command_score(args):
    review = review_agent(args.agent_path)
    if args.format == "json":
        payload = {
            "agent_id": review.get("agent_id"),
            "agent_path": review.get("agent_path"),
            "maturity_level": review.get("maturity_level"),
            "risk_level": review.get("risk_level"),
            "score": review.get("score"),
            "max_score": review.get("max_score"),
            "score_ratio": review.get("score_ratio"),
            "passed": review.get("passed"),
            "checks": review.get("checks", []),
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"agent_id: {review.get('agent_id', 'unknown')}")
        print(f"maturity_level: {review.get('maturity_level')}")
        print(f"risk_level: {review.get('risk_level')}")
        print(f"score: {review.get('score')}/{review.get('max_score')}")
        print(f"passed: {str(review.get('passed', False)).lower()}")
        print("checks:")
        for check in review.get("checks", []):
            status = "PASS" if check.get("passed") else "FAIL"
            print(f"- {status} {check.get('name')}: {check.get('detail')}")
    return 0 if review.get("passed") else 2


def build_parser():
    parser = argparse.ArgumentParser(prog="meta-agent", description="Professional agent design and governance toolkit.")
    parser.add_argument("--version", action="version", version="meta-agent 0.1.0a0")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Create a new agent workspace scaffold.")
    init.add_argument("agent_id", help="Agent identifier, for example research-agent.")
    init.add_argument("--output-dir", default=".", help="Directory where the agent workspace should be created.")
    init.add_argument("--role", default=None, help="Agent role description.")
    init.add_argument("--force", action="store_true", help="Allow writing into an existing non-empty agent directory.")
    init.set_defaults(func=command_init)

    validate = subparsers.add_parser("validate", help="Validate a meta-agent project.")
    validate.add_argument("path", nargs="?", default=".", help="Project root to validate.")
    validate.set_defaults(func=command_validate)

    inspect = subparsers.add_parser("inspect-project", help="Inspect project data summaries.")
    inspect.add_argument("path", nargs="?", default=".", help="Project root to inspect.")
    inspect.add_argument("--format", choices=["text", "json"], default="text")
    inspect.set_defaults(func=command_inspect_project)

    readiness = subparsers.add_parser("readiness", help="Check whether a meta-agent project is ready to publish or operate.")
    readiness.add_argument("path", nargs="?", default=".", help="Project root to check.")
    readiness.add_argument("--agent", default=None, help="Optional agent workspace to review as part of readiness.")
    readiness.add_argument("--format", choices=["text", "json"], default="text")
    readiness.add_argument("--fail-under", type=int, default=None, help="Fail when readiness score is below this 0-100 threshold.")
    readiness.add_argument("--strict", action="store_true", help="Treat inspection warnings as blockers.")
    readiness.set_defaults(func=command_readiness)

    report = subparsers.add_parser("report-project", help="Generate a project report from validation and inspection data.")
    report.add_argument("path", nargs="?", default=".", help="Project root to report.")
    report.add_argument("--format", choices=["markdown", "json"], default="markdown")
    report.add_argument("--output", default=None, help="Optional output file path.")
    report.set_defaults(func=command_report_project)

    list_workflows = subparsers.add_parser("list-workflows", help="List workflow specs in a project.")
    list_workflows.add_argument("path", nargs="?", default=".", help="Project root to inspect.")
    list_workflows.add_argument("--format", choices=["text", "json"], default="text")
    list_workflows.set_defaults(func=command_list_workflows)

    explain = subparsers.add_parser("explain-workflow", help="Explain a workflow spec.")
    explain.add_argument("workflow_path", help="Workflow JSON file to explain.")
    explain.add_argument("--format", choices=["markdown", "json"], default="markdown")
    explain.set_defaults(func=command_explain_workflow)

    run_workflow = subparsers.add_parser("run-workflow", help="Create a dry-run record for a workflow spec.")
    run_workflow.add_argument("workflow_path", help="Workflow JSON file to dry-run.")
    run_workflow.add_argument("--input-json", default=None, help="Inline JSON object or path to a JSON file.")
    run_workflow.add_argument("--output-path", default=None, help="Optional output path to include in the run record.")
    run_workflow.add_argument("--format", choices=["text", "json"], default="text")
    run_workflow.set_defaults(func=command_run_workflow)

    review = subparsers.add_parser("review", help="Review an agent workspace.")
    review.add_argument("agent_path", help="Path to an agent workspace containing agent.yaml.")
    review.add_argument("--format", choices=["markdown", "json"], default="markdown")
    review.set_defaults(func=command_review)

    score = subparsers.add_parser("score", help="Score an agent workspace review.")
    score.add_argument("agent_path", help="Path to an agent workspace containing agent.yaml.")
    score.add_argument("--format", choices=["text", "json"], default="text")
    score.set_defaults(func=command_score)

    propose = subparsers.add_parser("propose-memory-candidate", help="Create a proposed memory candidate from feedback.")
    propose.add_argument("feedback_path", help="Feedback event JSON file or JSON array file.")
    propose.add_argument("--feedback-id", default=None, help="Feedback ID to select when the file contains multiple events.")
    propose.add_argument("--output", default=None, help="Optional path to write the candidate JSON.")
    propose.set_defaults(func=command_propose_memory_candidate)

    review_memory = subparsers.add_parser("review-memory-candidate", help="Review a proposed memory candidate.")
    review_memory.add_argument("candidate_path", help="Memory candidate JSON file.")
    review_memory.add_argument("--decision", choices=["accept", "reject"], required=True, help="Review decision.")
    review_memory.add_argument("--reviewer", required=True, help="Reviewer identifier.")
    review_memory.add_argument("--reason", required=True, help="Review reason.")
    review_memory.add_argument("--output", default=None, help="Optional path to write the reviewed candidate JSON.")
    review_memory.set_defaults(func=command_review_memory_candidate)

    commit_memory = subparsers.add_parser("commit-memory-candidate", help="Commit an accepted reviewed candidate to local markdown.")
    commit_memory.add_argument("candidate_path", help="Reviewed memory candidate JSON file.")
    commit_memory.add_argument("--output-dir", required=True, help="Directory where the markdown memory file should be written.")
    commit_memory.set_defaults(func=command_commit_memory_candidate)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
