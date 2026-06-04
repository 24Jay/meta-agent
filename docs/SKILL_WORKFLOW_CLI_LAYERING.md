# Skill / Workflow / CLI Layering

Conclusion: Skill selects the expert mode, workflow defines the SOP, and CLI/tools execute concrete steps.

## One-line Distinction

- Skill: when to use this expert capability.
- Workflow: what steps should be followed.
- CLI/Tools: how each step is executed.

## Responsibilities

| Layer | Responsible For | Not Responsible For |
|---|---|---|
| Skill | role, triggers, boundaries, startup context | executing every step |
| Workflow | steps, status, failure policy, approvals | low-level data processing |
| CLI/Tools | stable execution and structured output | final domain judgment |
| Knowledge | stable facts and domain rules | temporary task state |
| Memory | long-term preferences and decisions | raw conversation logs |

## Anti-patterns

- A giant prompt that tries to do everything.
- One-off scripts for repeated tasks.
- Hidden evidence levels.
- Missing risk boundaries.
- Auto-applying feedback without review.
