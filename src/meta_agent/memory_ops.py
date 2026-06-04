import json
import re
from pathlib import Path


DESTINATION_TO_CANDIDATE_TYPE = {
    "memory": "feedback",
    "knowledge": "feedback",
    "workflow": "feedback",
    "roadmap": "project",
    "code": "not_memory",
    "ignore": "not_memory",
}


def load_feedback_event(path, feedback_id=None):
    path = Path(path).resolve()
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    events = data if isinstance(data, list) else [data]
    if feedback_id is None:
        if len(events) != 1:
            raise ValueError("feedback_id is required when the file contains multiple feedback events")
        return events[0]
    for event in events:
        if event.get("feedback_id") == feedback_id:
            return event
    raise ValueError(f"feedback event not found: {feedback_id}")


def feedback_to_memory_candidate(event):
    suggested_destination = event.get("suggested_destination", "memory")
    candidate_type = DESTINATION_TO_CANDIDATE_TYPE.get(suggested_destination, "feedback")
    feedback_id = event.get("feedback_id", "feedback")
    target_agent = event.get("agent_id")

    if candidate_type == "not_memory":
        content = event.get("correction") or event.get("encouragement") or event.get("reason") or "No durable memory proposed."
        how_to_apply = "Do not commit this as memory unless a human reviewer changes the candidate type."
    else:
        content = event.get("correction") or event.get("encouragement") or event.get("reason")
        how_to_apply = "Apply only after human review. Keep the lesson specific to the target agent and artifact."

    return {
        "candidate_id": f"memcand_from_{feedback_id}",
        "source_ref": feedback_id,
        "candidate_type": candidate_type,
        "target_agent": target_agent,
        "content": content,
        "why": event.get("reason", "Generated from a structured feedback event."),
        "how_to_apply": how_to_apply,
        "confidence": "medium" if event.get("rating") is None else "high",
        "risk_level": event.get("risk_level", "review_required"),
        "status": "proposed",
    }


def load_memory_candidate(path):
    path = Path(path).resolve()
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, list):
        if len(data) != 1:
            raise ValueError("candidate file must contain exactly one candidate object")
        return data[0]
    return data


def review_memory_candidate(candidate, decision, reviewer, reason):
    if decision not in {"accept", "reject"}:
        raise ValueError("decision must be 'accept' or 'reject'")
    if not reviewer:
        raise ValueError("reviewer is required")
    if not reason:
        raise ValueError("review reason is required")

    reviewed = dict(candidate)
    reviewed["status"] = "reviewed" if decision == "accept" else "rejected"
    reviewed["review"] = {
        "decision": decision,
        "reviewer": reviewer,
        "reason": reason,
    }
    if decision == "accept":
        reviewed["how_to_apply"] = reviewed.get("how_to_apply") or "Apply according to the reviewed candidate content."
    return reviewed


def write_candidate(candidate, output_path):
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(candidate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


def slugify(value):
    value = str(value or "memory-candidate").strip().lower()
    value = re.sub(r"[^a-z0-9_-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "memory-candidate"


def ensure_committable(candidate):
    if candidate.get("status") != "reviewed":
        raise ValueError("only reviewed memory candidates can be committed")
    review = candidate.get("review") or {}
    if review.get("decision") != "accept":
        raise ValueError("only accepted memory candidates can be committed")
    if candidate.get("candidate_type") == "not_memory":
        raise ValueError("not_memory candidates cannot be committed as memory")


def candidate_to_markdown(candidate):
    ensure_committable(candidate)
    name = slugify(candidate.get("candidate_id"))
    description = str(candidate.get("content", "")).replace("\n", " ")[:120]
    metadata_type = candidate.get("candidate_type", "feedback")
    target_agent = candidate.get("target_agent")
    review = candidate.get("review") or {}

    lines = [
        "---",
        f"name: {name}",
        f"description: {description}",
        "metadata:",
        f"  type: {metadata_type}",
    ]
    if target_agent:
        lines.append(f"  target_agent: {target_agent}")
    if candidate.get("source_ref"):
        lines.append(f"  source_ref: {candidate['source_ref']}")
    lines.extend([
        f"  review_decision: {review.get('decision')}",
        f"  reviewer: {review.get('reviewer')}",
        "---",
        "",
        str(candidate.get("content", "")),
        "",
        f"**Why:** {candidate.get('why', '')}",
        "",
        f"**How to apply:** {candidate.get('how_to_apply', '')}",
        "",
        f"**Review reason:** {review.get('reason', '')}",
    ])
    return "\n".join(lines) + "\n"


def commit_candidate_to_markdown(candidate, output_dir):
    ensure_committable(candidate)
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{slugify(candidate.get('candidate_id'))}.md"
    output_path.write_text(candidate_to_markdown(candidate), encoding="utf-8")
    return output_path
