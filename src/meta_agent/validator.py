import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .schema_validator import validate_schema

JSON_TARGET_DIRS = ["schemas", "workflows", "templates", "examples"]
REQUIRED_FILES = [
    "README.md",
    "ROADMAP.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "docs/PROFESSIONAL_AGENT_DESIGN.md",
    "docs/EVIDENCE_AND_RISK_POLICY.md",
    "docs/AGENT_MEMORY_OPS_SPEC.md",
    "docs/AGENT_EVALUATION_RUBRIC.md",
    "docs/WORKFLOW_AUTHORING.md",
    "examples/README.md",
    "examples/agents/research-agent/agent.yaml",
    "examples/agents/research-agent/CAPABILITY_MATRIX.md",
    "examples/data/agents.example.json",
    "examples/data/workflows.example.json",
    "examples/data/runs.example.json",
    "examples/data/feedback_events.example.json",
    "examples/data/memory_candidates.example.json",
]
FORBIDDEN_PATTERN_SOURCES = [
    "professional" + "-agent-kit",
    r"/home/[A-Za-z0-9._-]+",
    r"/Users/[A-Za-z0-9._-]+",
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(?:corp|internal|local)",
    r"https?://[^\s)\"]*(?:corp|internal|intranet|private)[^\s)\"]*",
    r"(?:api[_-]?key|secret|password|credential|private[_-]?key)\s*[:=]",
]
FORBIDDEN_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in FORBIDDEN_PATTERN_SOURCES]
TEXT_EXTENSIONS = {".md", ".json", ".yaml", ".yml", ".py", ".sh", ".txt", ".toml"}
RISK_LEVELS = {"read_only", "review_required", "approval_required", "blocked"}
MARKDOWN_LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
SENSITIVE_ALLOWLIST = {
    "LICENSE",
    "scripts/validate_project.py",
    "src/meta_agent/validator.py",
}


@dataclass
class ValidationResult:
    root: Path
    json_count: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self):
        return not self.errors

    def lines(self):
        if self.errors:
            return [f"FAIL {error}" for error in self.errors] + [f"Validation failed with {len(self.errors)} error(s)."]
        return [
            f"OK JSON syntax: {self.json_count} files",
            "OK required files",
            "OK example references",
            "OK schema conformity",
            "OK workflow semantics",
            "OK markdown local links",
            "OK sensitive pattern scan",
            "Project validation passed.",
        ]


def iter_json_files(root):
    for directory in JSON_TARGET_DIRS:
        path = root / directory
        if path.exists():
            yield from sorted(path.rglob("*.json"))


def iter_text_files(root):
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix in TEXT_EXTENSIONS:
            yield path


def iter_markdown_files(root):
    for path in sorted(root.rglob("*.md")):
        if path.is_file():
            yield path


def load_json(root, relative_path):
    with (root / relative_path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def check_json_syntax(root, errors):
    files = list(iter_json_files(root))
    for path in files:
        try:
            with path.open("r", encoding="utf-8") as handle:
                json.load(handle)
        except Exception as exc:
            errors.append(f"Invalid JSON: {path.relative_to(root)}: {exc}")
    return len(files)


def check_required_files(root, errors):
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            errors.append(f"Missing required file: {relative_path}")


def check_example_references(root, errors):
    required_example_files = [
        "examples/data/agents.example.json",
        "examples/data/workflows.example.json",
        "examples/data/runs.example.json",
        "examples/data/feedback_events.example.json",
        "examples/data/memory_candidates.example.json",
    ]
    if any(not (root / path).exists() for path in required_example_files):
        return

    agents = load_json(root, "examples/data/agents.example.json")
    workflows = load_json(root, "examples/data/workflows.example.json")
    runs = load_json(root, "examples/data/runs.example.json")
    feedback = load_json(root, "examples/data/feedback_events.example.json")
    candidates = load_json(root, "examples/data/memory_candidates.example.json")

    agent_ids = {agent["agent_id"] for agent in agents}
    workflow_ids = {workflow["workflow_id"] for workflow in workflows}
    run_ids = {run["run_id"] for run in runs}
    feedback_ids = {event["feedback_id"] for event in feedback}

    for agent in agents:
        for field_name in ["workspace_path", "workflow_specs_path"]:
            value = agent.get(field_name)
            if value and not (root / value).exists():
                errors.append(f"Agent {agent['agent_id']} references missing {field_name}: {value}")

    for workflow in workflows:
        if workflow["agent_id"] not in agent_ids:
            errors.append(f"Workflow {workflow['workflow_id']} references unknown agent_id: {workflow['agent_id']}")

    for run in runs:
        if run["agent_id"] not in agent_ids:
            errors.append(f"Run {run['run_id']} references unknown agent_id: {run['agent_id']}")
        if run.get("workflow_id") and run["workflow_id"] not in workflow_ids:
            errors.append(f"Run {run['run_id']} references unknown workflow_id: {run['workflow_id']}")
        output_path = run.get("output_path")
        if output_path and not (root / output_path).exists():
            errors.append(f"Run {run['run_id']} references missing output_path: {output_path}")

    for event in feedback:
        if event["agent_id"] not in agent_ids:
            errors.append(f"Feedback {event['feedback_id']} references unknown agent_id: {event['agent_id']}")
        target_ref = event.get("target_ref")
        if target_ref and not (root / target_ref).exists():
            errors.append(f"Feedback {event['feedback_id']} references missing target_ref: {target_ref}")

    for candidate in candidates:
        source_ref = candidate.get("source_ref")
        if candidate.get("target_agent") and candidate["target_agent"] not in agent_ids:
            errors.append(f"Memory candidate {candidate['candidate_id']} references unknown target_agent: {candidate['target_agent']}")
        if source_ref and source_ref not in run_ids and source_ref not in feedback_ids and not (root / source_ref).exists():
            errors.append(f"Memory candidate {candidate['candidate_id']} references unknown source_ref: {source_ref}")


def check_schema_conformity(root, errors):
    schema_specs = [
        ("schemas/agent.schema.json", "examples/data/agents.example.json", True),
        ("schemas/workflow.schema.json", "workflows", False),
        ("schemas/workflow.schema.json", "examples/agents", False),
        ("schemas/run.schema.json", "examples/data/runs.example.json", True),
        ("schemas/feedback-event.schema.json", "examples/data/feedback_events.example.json", True),
        ("schemas/memory-candidate.schema.json", "examples/data/memory_candidates.example.json", True),
    ]

    for schema_path, target_path, target_is_array in schema_specs:
        schema_file = root / schema_path
        target = root / target_path
        if not schema_file.exists() or not target.exists():
            continue
        schema = load_json(root, schema_path)
        if target.is_dir():
            files = [path for path in sorted(target.rglob("*.json")) if not path.name.endswith(".schema.json")]
            for file_path in files:
                data = json.loads(file_path.read_text(encoding="utf-8"))
                if is_workflow_json(file_path, data):
                    for error in validate_schema(data, schema):
                        errors.append(f"Schema {schema_path} failed for {file_path.relative_to(root)}: {error}")
        else:
            data = load_json(root, target_path)
            items = data if target_is_array else [data]
            for index, item in enumerate(items):
                item_path = f"{target_path}[{index}]" if target_is_array else target_path
                for error in validate_schema(item, schema):
                    errors.append(f"Schema {schema_path} failed for {item_path}: {error}")


def is_workflow_json(path, data):
    if not isinstance(data, dict):
        return False
    if path.name.endswith(".schema.json"):
        return False
    return "steps" in data or {"name", "version", "risk_level"}.issubset(data.keys())


def check_named_items(workflow_path, workflow, field_name, errors):
    items = workflow.get(field_name, [])
    if items is None:
        return
    if not isinstance(items, list):
        errors.append(f"Workflow {workflow_path} field {field_name} must be a list.")
        return
    seen = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"Workflow {workflow_path} {field_name}[{index}] must be an object.")
            continue
        name = item.get("name")
        if not name:
            errors.append(f"Workflow {workflow_path} {field_name}[{index}] is missing name.")
        elif name in seen:
            errors.append(f"Workflow {workflow_path} has duplicate {field_name} name: {name}")
        else:
            seen.add(name)
        if field_name in {"inputs", "outputs"} and not item.get("type"):
            errors.append(f"Workflow {workflow_path} {field_name}[{index}] is missing type.")
        if not item.get("description"):
            errors.append(f"Workflow {workflow_path} {field_name}[{index}] is missing description.")


def check_workflow_semantics(root, errors):
    for path in iter_json_files(root):
        try:
            with path.open("r", encoding="utf-8") as handle:
                workflow = json.load(handle)
        except Exception:
            continue
        if not is_workflow_json(path, workflow):
            continue

        relative = str(path.relative_to(root))
        for field_name in ["name", "version", "description", "risk_level", "steps"]:
            if field_name not in workflow:
                errors.append(f"Workflow {relative} is missing required field: {field_name}")

        risk_level = workflow.get("risk_level")
        if risk_level and risk_level not in RISK_LEVELS:
            errors.append(f"Workflow {relative} has invalid risk_level: {risk_level}")

        steps = workflow.get("steps")
        if not isinstance(steps, list) or not steps:
            errors.append(f"Workflow {relative} must define at least one step.")
        else:
            seen_steps = set()
            for index, step in enumerate(steps):
                if not isinstance(step, dict):
                    errors.append(f"Workflow {relative} steps[{index}] must be an object.")
                    continue
                step_name = step.get("name")
                if not step_name:
                    errors.append(f"Workflow {relative} steps[{index}] is missing name.")
                elif step_name in seen_steps:
                    errors.append(f"Workflow {relative} has duplicate step name: {step_name}")
                else:
                    seen_steps.add(step_name)
                if not step.get("description"):
                    errors.append(f"Workflow {relative} steps[{index}] is missing description.")
                if step.get("on_failure") not in {None, "block", "continue_with_warning", "await_human", "skip"}:
                    errors.append(f"Workflow {relative} step {step_name or index} has invalid on_failure: {step.get('on_failure')}")

        check_named_items(relative, workflow, "inputs", errors)
        check_named_items(relative, workflow, "outputs", errors)

        evidence_policy = workflow.get("evidence_policy")
        if not isinstance(evidence_policy, dict):
            errors.append(f"Workflow {relative} must define evidence_policy object.")
            continue
        must_include = evidence_policy.get("must_include")
        if not isinstance(must_include, list) or not must_include:
            errors.append(f"Workflow {relative} evidence_policy.must_include must be a non-empty list.")
        forbid_claims = evidence_policy.get("forbid_claims_when_insufficient")
        if forbid_claims is not None and not isinstance(forbid_claims, list):
            errors.append(f"Workflow {relative} evidence_policy.forbid_claims_when_insufficient must be a list when present.")


def should_ignore_markdown_link(target):
    target = target.strip()
    if not target or target.startswith("#"):
        return True
    lowered = target.lower()
    return lowered.startswith(("http://", "https://", "mailto:", "tel:"))


def normalize_markdown_link_target(target):
    target = target.strip().split("#", 1)[0]
    if " " in target:
        target = target.split(" ", 1)[0]
    return target


def check_markdown_links(root, errors):
    for path in iter_markdown_files(root):
        content = path.read_text(encoding="utf-8", errors="ignore")
        for match in MARKDOWN_LINK_PATTERN.finditer(content):
            raw_target = match.group(1)
            if should_ignore_markdown_link(raw_target):
                continue
            target = normalize_markdown_link_target(raw_target)
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                errors.append(f"Markdown link in {path.relative_to(root)} points outside project: {raw_target}")
                continue
            if not resolved.exists():
                errors.append(f"Markdown link in {path.relative_to(root)} points to missing file: {raw_target}")


def check_sensitive_patterns(root, errors):
    for path in iter_text_files(root):
        relative = str(path.relative_to(root))
        if relative in SENSITIVE_ALLOWLIST:
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(content):
                errors.append(f"Forbidden pattern {pattern.pattern!r} found in {relative}")


def validate_project(root):
    root = Path(root).resolve()
    result = ValidationResult(root=root)
    result.json_count = check_json_syntax(root, result.errors)
    check_required_files(root, result.errors)
    check_example_references(root, result.errors)
    check_schema_conformity(root, result.errors)
    check_workflow_semantics(root, result.errors)
    check_markdown_links(root, result.errors)
    check_sensitive_patterns(root, result.errors)
    return result
