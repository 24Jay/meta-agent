# Research Agent Capability Matrix

This sanitized example shows how to describe a professional agent with explicit capability, evidence, and risk boundaries.

| Capability | Status | Evidence Level | Risk Level | Human Review |
| --- | --- | --- | --- | --- |
| Summarize public references | supported | cited | read_only | optional |
| Compare technical approaches | supported | cited | read_only | optional |
| Produce recommendations | supported | reasoned | review_required | recommended |
| Update long-term memory | proposed | reviewed_feedback | review_required | required |
| Contact external systems | unsupported | none | blocked | required before implementation |

## Notes

- The agent may summarize and compare public or sanitized material.
- Recommendations must separate evidence from interpretation.
- Feedback can propose memory candidates, but memory is not committed without human review.
- Any action involving private data, external publication, or production systems is out of scope for this example.
