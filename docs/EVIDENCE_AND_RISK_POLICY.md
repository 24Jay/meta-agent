# Evidence and Risk Policy

Evidence and risk are different.

- `evidence_level` describes the support behind a conclusion.
- `risk_level` describes the impact of an action.

## Evidence Levels

| Level | Meaning | Appropriate Claims |
|---|---|---|
| `knowledge_only` | Based only on docs or knowledge | principles, possible directions |
| `conversation_summary` | Based on summarized conversation | what was discussed or decided |
| `single_observation` | One observation or case | case-level diagnosis |
| `batch_observation` | Multiple observations | patterns and hypotheses |
| `offline_replay` | Offline replay/evaluator | offline metric changes |
| `single_seed_eval` | One experimental seed | limited experimental result |
| `multi_seed_eval` | Multiple seeds | mean/variance within scope |
| `gray_experiment` | Limited online experiment | scoped online effect |
| `production_monitoring` | Long-term monitoring | production trend |

## Risk Levels

| Level | Meaning | Requirement |
|---|---|---|
| `read_only` | Analysis only | can run automatically |
| `review_required` | Suggestion or proposed change | human review before applying |
| `approval_required` | External or production impact | explicit approval required |
| `blocked` | Missing data, permission, or safety | explain blocker |

## Rule

Do not claim stable improvement, root cause, or production readiness without sufficient evidence. Do not execute high-risk actions without approval.
