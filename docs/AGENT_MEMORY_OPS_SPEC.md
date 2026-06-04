# Agent MemoryOps

Do not store raw conversations directly as long-term memory. Use a pipeline.

```text
Raw conversation / run log
  → summary
  → memory / knowledge / task / feedback candidates
  → human review
  → commit to memory / knowledge / roadmap / workflow / task / feedback
```

## Memory vs Knowledge

- Memory: long-term preferences, decisions, project constraints, feedback rules.
- Knowledge: stable domain knowledge, reference material, methods, schemas.
- Raw logs: archive and audit source, not memory.
- Candidates: proposed items pending review.

## Memory Candidate Types

- `user`
- `feedback`
- `project`
- `reference`
- `not_memory`

## Safety Rules

- Do not store secrets.
- Do not store raw customer data.
- Do not turn temporary task state into long-term memory.
- Deduplicate before committing.
- Review before writing memory.
